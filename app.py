from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from models.database import init_db
from services.parking_service import ParkingService
from services.ai_service import AIService

app = Flask(__name__)
app.config.from_object(Config)
init_db(app.config["DATABASE"])

parking = ParkingService(app.config["DATABASE"])
ai = AIService(app.config)

@app.context_processor
def inject_globals():
    return {"currency": lambda value: "${:,.0f}".format(value or 0).replace(",", ".")}

@app.route("/")
def dashboard():
    return render_template("dashboard.html", stats=parking.dashboard_stats(),
                           recent=parking.recent_activity(), spaces=parking.space_status())

@app.route("/vehicles", methods=["GET", "POST"])
def vehicles():
    if request.method == "POST":
        try:
            parking.register_vehicle(
                plate=request.form["plate"], vehicle_type=request.form["vehicle_type"],
                brand=request.form.get("brand", ""), color=request.form.get("color", ""),
                owner=request.form.get("owner", "")
            )
            flash("Vehículo registrado correctamente.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("vehicles"))
    return render_template("vehicles.html", vehicles=parking.list_vehicles())

@app.route("/entry", methods=["GET", "POST"])
def entry():
    if request.method == "POST":
        try:
            result = parking.check_in(request.form["plate"])
            flash(f"Ingreso registrado. Espacio {result['space_code']} asignado.", "success")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("entry"))
    return render_template("entry.html", vehicles=parking.available_vehicles(),
                           spaces=parking.space_status())

@app.route("/exit", methods=["GET", "POST"])
def exit_vehicle():
    if request.method == "POST":
        try:
            session = parking.prepare_checkout(request.form["session_id"])
            return render_template("checkout.html", session=session)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("exit_vehicle"))
    return render_template("exit.html", sessions=parking.active_sessions())

@app.route("/pay", methods=["POST"])
def pay():
    try:
        parking.complete_checkout(
            session_id=request.form["session_id"],
            method=request.form["method"],
            coupon_code=request.form.get("coupon_code", "")
        )
        flash("Pago simulado y salida registrada correctamente.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("dashboard"))

@app.route("/coupons", methods=["GET", "POST"])
def coupons():
    if request.method == "POST":
        try:
            parking.create_coupon(request.form["code"], int(request.form["discount"]))
            flash("Cupón creado.", "success")
        except (ValueError, KeyError) as exc:
            flash(str(exc) or "Datos no válidos.", "error")
        return redirect(url_for("coupons"))
    return render_template("coupons.html", coupons=parking.list_coupons())

@app.route("/history")
def history():
    return render_template("history.html", records=parking.payment_history())

@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    answer = None
    if request.method == "POST":
        snapshot = parking.analytics_snapshot()
        answer = ai.analyze(request.form.get("question", ""), snapshot)
    return render_template("assistant.html", answer=answer, available=ai.is_available())

@app.route("/api/summary")
def api_summary():
    return jsonify(parking.analytics_snapshot())

if __name__ == "__main__":
    app.run(debug=True)
