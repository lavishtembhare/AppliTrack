import sqlite3
from datetime import datetime
import pandas as pd

class DatabaseManager:
    """Handles SQLite storage for job applications and settings."""
    def __init__(self, db_path="job_tracker.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT NOT NULL,
                    role TEXT NOT NULL,
                    date_applied TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Applied',
                    notes TEXT
                )
            """)

            # Pre-populate sample entries if empty
            cursor.execute("SELECT COUNT(*) FROM applications")
            if cursor.fetchone()[0] == 0:
                sample_data = [
                    ("Google", "Data Analyst", "2026-08-12", "Interview", "Round 2 scheduled"),
                    ("Notion", "Data Scientist", "2026-08-05", "Applied", "Referral via LinkedIn"),
                    ("Airbnb", "Analyst", "2026-07-28", "Rejected", "Resume screened out"),
                    ("Spotify", "BI Analyst", "2026-07-20", "Interview", "Take-home test done"),
                    ("Amazon", "Data Analyst", "2026-07-15", "Applied", "Online assessment completed"),
                    ("Microsoft", "Data Engineer", "2026-07-10", "Offer", "Offer package received"),
                ]
                cursor.executemany(
                    "INSERT INTO applications (company, role, date_applied, status, notes) VALUES (?, ?, ?, ?, ?)",
                    sample_data
                )
            conn.commit()

    def add_application(self, company, role, date_applied, status, notes=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO applications (company, role, date_applied, status, notes) VALUES (?, ?, ?, ?, ?)",
                (company.strip(), role.strip(), date_applied.strip(), status, notes.strip())
            )
            conn.commit()

    def update_status(self, app_id, new_status):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
            conn.commit()

    def delete_application(self, app_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
            conn.commit()

    def clear_all(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM applications")
            conn.commit()

    def get_all_applications(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM applications ORDER BY date_applied DESC, id DESC", conn)