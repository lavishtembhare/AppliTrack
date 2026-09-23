import os
import sqlite3
from datetime import datetime
import pandas as pd

DEFAULT_EXPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")

class DatabaseManager:
    """Handles SQLite storage for job applications, conduits, emails, and system settings."""
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

            # Conduits / Portals Table
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

            # System Settings Table
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

            # Default Settings
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('export_dir', ?)", (DEFAULT_EXPORT_PATH,))
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('default_portal', 'LinkedIn')")
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('default_email', 'primary.work@gmail.com')")
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('sort_order', 'DESC')")

            conn.commit()

    # --- System Settings ---
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

    def get_all_applications(self, sort_order=None):
        """Fetches applications ordered according to user preference (ASC or DESC)."""
        if sort_order is None:
            sort_order = self.get_setting("sort_order", "DESC").upper()
        
        direction = "ASC" if sort_order in ["ASC", "ASCENDING", "OLDEST FIRST"] else "DESC"
        query = f"SELECT * FROM applications ORDER BY date_applied {direction}, id {direction}"
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_applications_for_export(self):
        """Always fetches applications sorted by id ascending (1, 2, 3...) for Excel export."""
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM applications ORDER BY id ASC", conn)

    # --- Spreadsheet Ingestion Engine ---
    def import_applications_from_dataframe(self, imported_df: pd.DataFrame) -> int:
        col_map = {}
        for col in imported_df.columns:
            clean = str(col).strip().lower().replace("_", " ").replace("-", " ")
            if any(k in clean for k in ["company", "organization", "employer"]):
                col_map["company"] = col
            elif any(k in clean for k in ["role", "position", "job title", "title"]):
                col_map["role"] = col
            elif any(k in clean for k in ["date", "applied on", "timestamp"]):
                col_map["date"] = col
            elif any(k in clean for k in ["status", "stage", "pipeline status"]):
                col_map["status"] = col
            elif any(k in clean for k in ["portal", "applied through", "channel", "source"]):
                col_map["portal"] = col
            elif any(k in clean for k in ["email", "applicant email", "applied email", "account"]):
                col_map["email"] = col
            elif any(k in clean for k in ["notes", "url", "link", "remark", "description"]):
                col_map["notes"] = col

        if "company" not in col_map or "role" not in col_map:
            raise ValueError("Spreadsheet must contain at least 'Company' and 'Role' columns.")

        imported_count = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for _, row in imported_df.iterrows():
                comp = str(row[col_map["company"]]).strip() if pd.notna(row[col_map["company"]]) else ""
                role = str(row[col_map["role"]]).strip() if pd.notna(row[col_map["role"]]) else ""

                if not comp or not role or comp.lower() == "nan" or role.lower() == "nan":
                    continue

                date_val = datetime.now().strftime("%Y-%m-%d")
                if "date" in col_map and pd.notna(row[col_map["date"]]):
                    try:
                        parsed_dt = pd.to_datetime(row[col_map["date"]])
                        date_val = parsed_dt.strftime("%Y-%m-%d")
                    except Exception:
                        date_val = str(row[col_map["date"]]).strip()

                raw_st = str(row[col_map["status"]]).strip() if "status" in col_map and pd.notna(row[col_map["status"]]) else "Applied"
                valid_statuses = ["Applied", "Interview", "Offer", "Rejected"]
                matched_status = "Applied"
                for vs in valid_statuses:
                    if vs.lower() in raw_st.lower():
                        matched_status = vs
                        break

                portal_val = str(row[col_map["portal"]]).strip() if "portal" in col_map and pd.notna(row[col_map["portal"]]) else "LinkedIn"
                if portal_val.lower() == "nan" or not portal_val:
                    portal_val = "LinkedIn"

                email_val = str(row[col_map["email"]]).strip() if "email" in col_map and pd.notna(row[col_map["email"]]) else ""
                if email_val.lower() == "nan":
                    email_val = ""

                notes_val = str(row[col_map["notes"]]).strip() if "notes" in col_map and pd.notna(row[col_map["notes"]]) else ""
                if notes_val.lower() == "nan":
                    notes_val = ""

                cursor.execute(
                    """INSERT INTO applications 
                       (company, role, date_applied, status, portal, applied_email, notes) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (comp, role, date_val, matched_status, portal_val, email_val, notes_val)
                )

                if portal_val and portal_val != "nan":
                    cursor.execute("INSERT OR IGNORE INTO portals (name) VALUES (?)", (portal_val,))
                if email_val and "@" in email_val and "." in email_val:
                    cursor.execute("INSERT OR IGNORE INTO emails (email) VALUES (?)", (email_val,))

                imported_count += 1

            conn.commit()

        return imported_count