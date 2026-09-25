import os
import sqlite3
from datetime import datetime
import pandas as pd

DEFAULT_EXPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")

class DatabaseManager:
    """High-performance SQLite engine with persistent connection, WAL mode, indexing, in-memory caching, and batch ingestion."""
    def __init__(self, db_path="applitrack.db"):
        self.db_path = db_path
        self._cached_df = None
        
        # Single persistent connection to eliminate per-query disk handshake overhead
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._configure_connection()
        self.init_db()

    def _configure_connection(self):
        """Enables high-throughput SQLite PRAGMAs."""
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.execute("PRAGMA cache_size = -64000;")  # 64MB RAM cache
        self.conn.execute("PRAGMA temp_store = MEMORY;")

    def get_connection(self):
        return self.conn

    def _invalidate_cache(self):
        """Invalidates the in-memory DataFrame cache when data mutations occur."""
        self._cached_df = None

    def init_db(self):
        with self.conn:
            cursor = self.conn.cursor()
            
            # 1. Applications Table
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

            # Fast Search & Sort Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_apps_date_id ON applications(date_applied, id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_apps_status ON applications(status);")

            # 2. Conduits / Portals Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # 3. Emails Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL
                )
            """)

            # 4. System Settings Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # Auto-purge legacy dummy entries
            cursor.execute("DELETE FROM emails WHERE email IN ('primary.work@gmail.com', 'career.applicant@outlook.com')")
            cursor.execute("UPDATE settings SET value = '' WHERE key = 'default_email' AND value = 'primary.work@gmail.com'")

            # Default Settings
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('export_dir', ?)", (DEFAULT_EXPORT_PATH,))
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('default_portal', '')")
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('default_email', '')")
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('sort_order', 'DESC')")

    # --- System Settings ---
    def get_setting(self, key, default=""):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        if key == "sort_order":
            self._invalidate_cache()

    # --- Portal Management ---
    def get_portals(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM portals ORDER BY name ASC")
        rows = cursor.fetchall()
        return [r[0] for r in rows] if rows else []

    def add_portal(self, name):
        name = name.strip()
        if not name:
            return
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO portals (name) VALUES (?)", (name,))

    def delete_portal(self, name):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM portals WHERE name = ?", (name.strip(),))

    # --- Email Management ---
    def get_emails(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT email FROM emails ORDER BY email ASC")
        rows = cursor.fetchall()
        return [r[0] for r in rows] if rows else []

    def add_email(self, email_str):
        email_str = email_str.strip()
        if not email_str:
            return
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO emails (email) VALUES (?)", (email_str,))

    def delete_email(self, email_str):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM emails WHERE email = ?", (email_str.strip(),))

    # --- Applications CRUD ---
    def add_application(self, company, role, date_applied, status, portal="", applied_email="", notes=""):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO applications 
                   (company, role, date_applied, status, portal, applied_email, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (company.strip(), role.strip(), date_applied.strip(), status, portal.strip(), applied_email.strip(), notes.strip())
            )
        self._invalidate_cache()

    def update_status(self, app_id, new_status):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
        self._invalidate_cache()

    def delete_application(self, app_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        self._invalidate_cache()

    def clear_all(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM applications")
        self._invalidate_cache()

    def get_all_applications(self, sort_order=None):
        """Fetches from in-memory cache if available; loads from indexed SQLite on cache miss."""
        if sort_order is None:
            sort_order = self.get_setting("sort_order", "DESC").upper()
        
        ascending = sort_order in ["ASC", "ASCENDING", "OLDEST FIRST"]

        if self._cached_df is None:
            self._cached_df = pd.read_sql_query("SELECT * FROM applications", self.conn)

        if self._cached_df.empty:
            return self._cached_df.copy()

        # Instant in-memory sort (< 1ms)
        sorted_df = self._cached_df.sort_values(
            by=["date_applied", "id"],
            ascending=[ascending, ascending]
        )
        return sorted_df.copy()

    def get_applications_for_export(self):
        return pd.read_sql_query("SELECT * FROM applications ORDER BY id ASC", self.conn)

    # --- High-Speed Vectorized Batch Ingestion ---
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

        # Bulk filter invalid rows
        valid_df = imported_df[
            imported_df[col_map["company"]].notna() & 
            imported_df[col_map["role"]].notna()
        ].copy()

        if valid_df.empty:
            return 0

        # Vectorized string sanitization
        valid_df["comp_clean"] = valid_df[col_map["company"]].astype(str).str.strip()
        valid_df["role_clean"] = valid_df[col_map["role"]].astype(str).str.strip()
        valid_df = valid_df[(valid_df["comp_clean"] != "") & (valid_df["comp_clean"].str.lower() != "nan")]
        valid_df = valid_df[(valid_df["role_clean"] != "") & (valid_df["role_clean"].str.lower() != "nan")]

        if valid_df.empty:
            return 0

        # Vectorized date handling
        default_today = datetime.now().strftime("%Y-%m-%d")
        if "date" in col_map:
            parsed_dates = pd.to_datetime(valid_df[col_map["date"]], errors="coerce").dt.strftime("%Y-%m-%d")
            valid_df["date_clean"] = parsed_dates.fillna(default_today)
        else:
            valid_df["date_clean"] = default_today

        # Status normalization
        def clean_status(val):
            s = str(val).strip().capitalize() if pd.notna(val) else "Applied"
            for target in ["Interview", "Offer", "Rejected", "Applied"]:
                if target.lower() in s.lower():
                    return target
            return "Applied"

        if "status" in col_map:
            valid_df["status_clean"] = valid_df[col_map["status"]].apply(clean_status)
        else:
            valid_df["status_clean"] = "Applied"

        # Conduits, Emails & Notes
        valid_df["portal_clean"] = valid_df[col_map["portal"]].fillna("").astype(str).str.strip() if "portal" in col_map else ""
        valid_df["portal_clean"] = valid_df["portal_clean"].replace({"nan": "", "None": ""})

        valid_df["email_clean"] = valid_df[col_map["email"]].fillna("").astype(str).str.strip() if "email" in col_map else ""
        valid_df["email_clean"] = valid_df["email_clean"].replace({"nan": "", "None": ""})

        valid_df["notes_clean"] = valid_df[col_map["notes"]].fillna("").astype(str).str.strip() if "notes" in col_map else ""
        valid_df["notes_clean"] = valid_df["notes_clean"].replace({"nan": "", "None": ""})

        # Batch tuples
        records_to_insert = list(zip(
            valid_df["comp_clean"],
            valid_df["role_clean"],
            valid_df["date_clean"],
            valid_df["status_clean"],
            valid_df["portal_clean"],
            valid_df["email_clean"],
            valid_df["notes_clean"]
        ))

        unique_portals = [(p,) for p in set(valid_df["portal_clean"]) if p]
        unique_emails = [(e,) for e in set(valid_df["email_clean"]) if "@" in e and "." in e]

        # Single atomic batch transaction
        with self.conn:
            cursor = self.conn.cursor()
            cursor.executemany(
                """INSERT INTO applications 
                   (company, role, date_applied, status, portal, applied_email, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                records_to_insert
            )
            if unique_portals:
                cursor.executemany("INSERT OR IGNORE INTO portals (name) VALUES (?)", unique_portals)
            if unique_emails:
                cursor.executemany("INSERT OR IGNORE INTO emails (email) VALUES (?)", unique_emails)

        self._invalidate_cache()
        return len(records_to_insert)

    def close(self):
        """Closes the persistent SQLite connection cleanly."""
        try:
            self.conn.close()
        except Exception:
            pass