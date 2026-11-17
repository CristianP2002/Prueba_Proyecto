import os, sqlite3
from datetime import datetime

def connect(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db(path):
    db = connect(path)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS vehicles (
      id INTEGER PRIMARY KEY AUTOINCREMENT, plate TEXT UNIQUE NOT NULL,
      vehicle_type TEXT NOT NULL, brand TEXT, color TEXT, owner TEXT,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS spaces (
      id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL,
      vehicle_type TEXT NOT NULL, occupied INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS parking_sessions (
      id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id INTEGER NOT NULL,
      space_id INTEGER NOT NULL, entry_time TEXT NOT NULL, exit_time TEXT,
      status TEXT DEFAULT 'ACTIVE', FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
      FOREIGN KEY(space_id) REFERENCES spaces(id)
    );
    CREATE TABLE IF NOT EXISTS coupons (
      id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL,
      discount INTEGER NOT NULL, active INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS payments (
      id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
      amount REAL NOT NULL, discount REAL DEFAULT 0, method TEXT NOT NULL,
      paid_at TEXT NOT NULL, coupon_code TEXT,
      FOREIGN KEY(session_id) REFERENCES parking_sessions(id)
    );
    """)
    count = db.execute("SELECT COUNT(*) FROM spaces").fetchone()[0]
    if count == 0:
        for prefix, kind, amount in [("A", "Carro", 12), ("M", "Moto", 8), ("B", "Bicicleta", 4)]:
            db.executemany("INSERT INTO spaces(code, vehicle_type) VALUES (?,?)",
                           [(f"{prefix}{i:02d}", kind) for i in range(1, amount+1)])
    db.commit()
    db.close()
