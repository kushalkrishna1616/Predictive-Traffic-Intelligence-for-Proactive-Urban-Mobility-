"""
SQLite Historical Traffic Telemetry Logger & Trend Engine
Problem Statement: AI/ML-09 / AML-05 (Innohack Project)

Stores historical corridor telemetry (PCU density, speed, vehicle counts)
and generates 24-hour historical time-series curves for predictive AI models.
"""

import sqlite3
import os
import time
import random
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "traffic_history.db")

class TelemetryLogger:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        """Initializes SQLite tables for historical telemetry logs."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS corridor_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                corridor_id TEXT,
                corridor_name TEXT,
                pcu_load REAL,
                avg_speed_kmh REAL,
                congestion_pct REAL,
                total_vehicles INTEGER
            )
        ''')
        conn.commit()

        # Seed initial 24-hour historical data if table is empty
        cursor.execute("SELECT COUNT(*) FROM corridor_logs")
        count = cursor.fetchone()[0]
        if count == 0:
            self._seed_historical_data(cursor)
            conn.commit()

        conn.close()

    def _seed_historical_data(self, cursor):
        """Generates realistic 24-hour historical traffic curves for Bengaluru junctions."""
        now = int(time.time())
        corridors = ["Silk Board Junction", "Outer Ring Road (Bellandur)", "Tin Factory", "Hebbal Flyover", "MG Road"]
        
        # Seed 24 hourly data points going backwards
        for hour in range(24, 0, -1):
            ts = now - (hour * 3600)
            hour_of_day = (24 - hour) % 24

            # Peak rush hours: 8am-10am and 5pm-8pm
            is_peak = (8 <= hour_of_day <= 10) or (17 <= hour_of_day <= 20)
            base_pct = random.uniform(75.0, 95.0) if is_peak else random.uniform(25.0, 55.0)

            for c in corridors:
                speed = max(8.0, 45.0 * (1.0 - (base_pct / 120.0)))
                pcu = round(base_pct * 0.45, 1)
                vehicles = int(pcu * random.uniform(1.8, 2.4))

                cursor.execute('''
                    INSERT INTO corridor_logs (timestamp, corridor_id, corridor_name, pcu_load, avg_speed_kmh, congestion_pct, total_vehicles)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (ts, c.lower().replace(" ", "_"), c, pcu, round(speed, 1), round(base_pct, 1), vehicles))

    def log_telemetry(self, corridor_name: str, pcu_load: float, speed: float, congestion_pct: float, vehicles: int):
        """Logs a real-time telemetry snapshot."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO corridor_logs (timestamp, corridor_id, corridor_name, pcu_load, avg_speed_kmh, congestion_pct, total_vehicles)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (int(time.time()), corridor_name.lower().replace(" ", "_"), corridor_name, pcu_load, speed, congestion_pct, vehicles))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging telemetry: {e}")

    def get_24h_trends(self, corridor_name: str = "Silk Board Junction") -> Dict[str, Any]:
        """Returns 24-hour time-series trends for charting."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, congestion_pct, avg_speed_kmh, pcu_load 
            FROM corridor_logs 
            WHERE corridor_name LIKE ? 
            ORDER BY timestamp ASC LIMIT 24
        ''', (f"%{corridor_name}%",))
        rows = cursor.fetchall()
        conn.close()

        labels = []
        congestion_curve = []
        speed_curve = []
        pcu_curve = []

        for r in rows:
            t_str = time.strftime("%H:%M", time.localtime(r[0]))
            labels.append(t_str)
            congestion_curve.append(r[1])
            speed_curve.append(r[2])
            pcu_curve.append(r[3])

        return {
            "corridor": corridor_name,
            "data_points": len(rows),
            "timestamps": labels,
            "congestion_pct": congestion_curve,
            "avg_speed_kmh": speed_curve,
            "pcu_load": pcu_curve
        }
