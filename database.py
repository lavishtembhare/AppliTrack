import os
import sqlite3
import pandas as pd

DEFAULT_EXPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")

class DatabaseManager:
    """Handles SQLite storage for job applications, portals, emails, and system settings."""
    def __init__(self, db_path="applitrack.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Applications Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT NOT NULL,
                    role TEXT NOT NULL,
                    date_applied TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Applied',
                    portal TEXT NOT NULL DEFAULT 'LinkedIn',
                    applied_email TEXT DEFAULT '',
                    notes TEXT
                )
            """)

            # Portals Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # Emails Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL
                )
            """)

            # System Settings Table (Stores predecided path, etc.)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Default Portals
            cursor.execute("SELECT COUNT(*) FROM portals")
            if cursor.fetchone()[0] == 0:
                defaults = ["LinkedIn", "Career Portal", "Indeed", "Glassdoor", "Wellfound", "Referral", "Cold Email", "Other"]
                for p in defaults:
                    cursor.execute("INSERT OR IGNORE INTO portals (name) VALUES (?)", (p,))

            # Default Emails
            cursor.execute("SELECT COUNT(*) FROM emails")
            if cursor.fetchone()[0] == 0:
                default_emails = ["primary.work@gmail.com", "career.applicant@outlook.com"]
                for em in default_emails:
                    cursor.execute("INSERT OR IGNORE INTO emails (email) VALUES (?)", (em,))

            # Default Predecided Export Directory
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('export_dir', ?)", (DEFAULT_EXPORT_PATH,))

            conn.commit()

    # --- System Settings (Predecided Path) ---
    def get_setting(self, key, default=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def set_setting(self, key, value):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()

    # --- Portal Management ---
    def get_portals(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM portals ORDER BY name ASC")
            rows = cursor.fetchall()
            return [r[0] for r in rows] if rows else ["Career Portal", "LinkedIn"]

    def add_portal(self, name):
        name = name.strip()
        if not name:
            return
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO portals (name) VALUES (?)", (name,))
            conn.commit()

    def delete_portal(self, name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM portals WHERE name = ?", (name.strip(),))
            conn.commit()

    # --- Email Management ---
    def get_emails(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM emails ORDER BY email ASC")
            rows = cursor.fetchall()
            return [r[0] for r in rows] if rows else []

    def add_email(self, email_str):
        email_str = email_str.strip()
        if not email_str:
            return
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO emails (email) VALUES (?)", (email_str,))
            conn.commit()

    def delete_email(self, email_str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM emails WHERE email = ?", (email_str.strip(),))
            conn.commit()

    # --- Applications CRUD ---
    def add_application(self, company, role, date_applied, status, portal="LinkedIn", applied_email="", notes=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO applications 
                   (company, role, date_applied, status, portal, applied_email, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (company.strip(), role.strip(), date_applied.strip(), status, portal.strip(), applied_email.strip(), notes.strip())
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