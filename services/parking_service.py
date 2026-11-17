import math, sqlite3
from datetime import datetime
from models.database import connect
from models.entities import Vehicle, Coupon

class ParkingService:
    """Reglas de negocio del parqueadero; la interfaz no consulta SQL directamente."""
    def __init__(self, db_path, hourly_rate=3000):
        self.db_path, self.hourly_rate = db_path, hourly_rate

    def _db(self): return connect(self.db_path)

    def register_vehicle(self, plate, vehicle_type, brand="", color="", owner=""):
        plate = plate.strip().upper().replace(" ", "")
        if len(plate) < 5: raise ValueError("La placa debe tener al menos 5 caracteres.")
        if vehicle_type not in ("Carro", "Moto", "Bicicleta"): raise ValueError("Tipo de vehículo inválido.")
        db = self._db()
        try:
            db.execute("INSERT INTO vehicles(plate,vehicle_type,brand,color,owner,created_at) VALUES(?,?,?,?,?,?)",
                       (plate, vehicle_type, brand.strip(), color.strip(), owner.strip(), datetime.now().isoformat(timespec="seconds")))
            db.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Esta placa ya está registrada.")
        finally: db.close()

    def list_vehicles(self):
        db=self._db(); rows=db.execute("SELECT * FROM vehicles ORDER BY id DESC").fetchall(); db.close()
        return rows

    def available_vehicles(self):
        db=self._db()
        rows=db.execute("""SELECT v.* FROM vehicles v WHERE NOT EXISTS
          (SELECT 1 FROM parking_sessions s WHERE s.vehicle_id=v.id AND s.status='ACTIVE')
          ORDER BY v.plate""").fetchall()
        db.close(); return rows

    def check_in(self, plate):
        db=self._db(); vehicle=db.execute("SELECT * FROM vehicles WHERE plate=?", (plate.strip().upper(),)).fetchone()
        if not vehicle: db.close(); raise ValueError("No existe un vehículo con esa placa. Regístralo primero.")
        active=db.execute("SELECT id FROM parking_sessions WHERE vehicle_id=? AND status='ACTIVE'", (vehicle["id"],)).fetchone()
        if active: db.close(); raise ValueError("Este vehículo ya se encuentra dentro del parqueadero.")
        space=db.execute("SELECT * FROM spaces WHERE vehicle_type=? AND occupied=0 ORDER BY code LIMIT 1",
                         (vehicle["vehicle_type"],)).fetchone()
        if not space: db.close(); raise ValueError("No hay espacios disponibles para este tipo de vehículo.")
        cur=db.execute("INSERT INTO parking_sessions(vehicle_id,space_id,entry_time) VALUES(?,?,?)",
                       (vehicle["id"],space["id"],datetime.now().isoformat(timespec="seconds")))
        db.execute("UPDATE spaces SET occupied=1 WHERE id=?", (space["id"],))
        db.commit(); result={"session_id":cur.lastrowid,"space_code":space["code"]}; db.close()
        return result

    def active_sessions(self):
        db=self._db()
        rows=db.execute("""SELECT s.id,s.entry_time,v.plate,v.vehicle_type,sp.code AS space_code
          FROM parking_sessions s JOIN vehicles v ON v.id=s.vehicle_id JOIN spaces sp ON sp.id=s.space_id
          WHERE s.status='ACTIVE' ORDER BY s.entry_time""").fetchall()
        db.close(); return rows

    def prepare_checkout(self, session_id):
        db=self._db()
        row=db.execute("""SELECT s.*,v.plate,v.vehicle_type,sp.code AS space_code
          FROM parking_sessions s JOIN vehicles v ON v.id=s.vehicle_id JOIN spaces sp ON sp.id=s.space_id
          WHERE s.id=? AND s.status='ACTIVE'""",(session_id,)).fetchone()
        db.close()
        if not row: raise ValueError("La sesión no existe o ya fue cerrada.")
        start=datetime.fromisoformat(row["entry_time"]); minutes=max(1,math.ceil((datetime.now()-start).total_seconds()/60))
        hours=max(1,math.ceil(minutes/60)); amount=hours*self.hourly_rate
        return dict(row) | {"minutes":minutes,"hours":hours,"amount":amount}

    def complete_checkout(self, session_id, method, coupon_code=""):
        if method not in ("Efectivo","Tarjeta","QR"): raise ValueError("Método de pago inválido.")
        session=self.prepare_checkout(session_id); discount=0; coupon_code=coupon_code.strip().upper()
        db=self._db()
        if coupon_code:
            coupon=db.execute("SELECT * FROM coupons WHERE code=? AND active=1",(coupon_code,)).fetchone()
            if not coupon: db.close(); raise ValueError("Cupón inválido o inactivo.")
            discount=session["amount"]*coupon["discount"]/100
        final=max(0,session["amount"]-discount)
        db.execute("INSERT INTO payments(session_id,amount,discount,method,paid_at,coupon_code) VALUES(?,?,?,?,?,?)",
                   (session_id,final,discount,method,datetime.now().isoformat(timespec="seconds"),coupon_code or None))
        db.execute("UPDATE parking_sessions SET status='CLOSED',exit_time=? WHERE id=?",
                   (datetime.now().isoformat(timespec="seconds"),session_id))
        db.execute("UPDATE spaces SET occupied=0 WHERE id=?",(session["space_id"],))
        db.commit(); db.close()

    def create_coupon(self, code, discount):
        code=code.strip().upper()
        if not code or not 1 <= discount <= 80: raise ValueError("Usa un código y un descuento entre 1% y 80%.")
        db=self._db()
        try: db.execute("INSERT INTO coupons(code,discount) VALUES(?,?)",(code,discount)); db.commit()
        except sqlite3.IntegrityError: raise ValueError("Ese cupón ya existe.")
        finally: db.close()

    def list_coupons(self):
        db=self._db(); rows=db.execute("SELECT * FROM coupons ORDER BY id DESC").fetchall(); db.close(); return rows

    def payment_history(self):
        db=self._db()
        rows=db.execute("""SELECT p.*,v.plate,s.entry_time FROM payments p
          JOIN parking_sessions s ON s.id=p.session_id JOIN vehicles v ON v.id=s.vehicle_id
          ORDER BY p.id DESC LIMIT 100""").fetchall()
        db.close(); return rows

    def dashboard_stats(self):
        db=self._db()
        active=db.execute("SELECT COUNT(*) FROM parking_sessions WHERE status='ACTIVE'").fetchone()[0]
        total=db.execute("SELECT COUNT(*) FROM spaces").fetchone()[0]
        today=datetime.now().date().isoformat()
        income=db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE substr(paid_at,1,10)=?",(today,)).fetchone()[0]
        count=db.execute("SELECT COUNT(*) FROM payments WHERE substr(paid_at,1,10)=?",(today,)).fetchone()[0]
        vehicles=db.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
        db.close()
        return {"occupied":active,"available":total-active,"total":total,"income":income,"payments":count,"vehicles":vehicles}

    def space_status(self):
        db=self._db(); rows=db.execute("SELECT * FROM spaces ORDER BY code").fetchall(); db.close(); return rows

    def recent_activity(self):
        db=self._db()
        rows=db.execute("""SELECT v.plate,s.entry_time,s.exit_time,s.status,sp.code
          FROM parking_sessions s JOIN vehicles v ON v.id=s.vehicle_id JOIN spaces sp ON sp.id=s.space_id
          ORDER BY s.id DESC LIMIT 8""").fetchall()
        db.close(); return rows

    def analytics_snapshot(self):
        db=self._db()
        data={
          "ocupacion_actual": db.execute("SELECT COUNT(*) FROM parking_sessions WHERE status='ACTIVE'").fetchone()[0],
          "vehiculos_registrados": db.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0],
          "ingresos_totales": db.execute("SELECT COALESCE(SUM(amount),0) FROM payments").fetchone()[0],
          "pagos_por_metodo": [dict(r) for r in db.execute("SELECT method,COUNT(*) AS cantidad,SUM(amount) AS total FROM payments GROUP BY method")],
          "vehiculos_por_tipo": [dict(r) for r in db.execute("SELECT vehicle_type,COUNT(*) AS cantidad FROM vehicles GROUP BY vehicle_type")],
          "ultimos_pagos": [dict(r) for r in db.execute("SELECT amount,method,paid_at FROM payments ORDER BY id DESC LIMIT 10")]
        }
        db.close(); return data
