from datetime import datetime
import customtkinter as ctk
import pandas as pd
from tkinter import filedialog, messagebox

class SettingsView(ctk.CTkScrollableFrame):
    def __init__(self, parent, db, on_change_callback):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_change_callback = on_change_callback
        self.portal_widgets = []
        self.email_widgets = []

        # Header Title
        title_box = ctk.CTkFrame(self, fg_color="transparent")
        title_box.pack(fill="x", padx=40, pady=(30, 20))

        ctk.CTkLabel(
            title_box, text="⚙️ Preferences & Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box, text="Manage application channels, applicant email addresses, and backup options.",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        ).pack(anchor="w")

        # Two-Column Container for Portals & Emails
        cards_grid = ctk.CTkFrame(self, fg_color="transparent")
        cards_grid.pack(fill="x", padx=40, pady=(0, 20))
        cards_grid.grid_columnconfigure((0, 1), weight=1)

        # ----------------- LEFT: PORTAL MANAGER -----------------
        portal_card = ctk.CTkFrame(cards_grid, fg_color="#1e293b", corner_radius=14, border_width=1, border_color="#334155")
        portal_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(portal_card, text="🌐 Application Portals", font=ctk.CTkFont(size=15, weight="bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(portal_card, text="Add or remove platforms you use to apply.", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", padx=20, pady=(0, 12))

        p_input_box = ctk.CTkFrame(portal_card, fg_color="transparent")
        p_input_box.pack(fill="x", padx=20, pady=(0, 12))

        self.new_portal_entry = ctk.CTkEntry(p_input_box, placeholder_text="New portal name...", fg_color="#0f172a", border_color="#334155")
        self.new_portal_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(p_input_box, text="+ Add", width=65, fg_color="#6366f1", hover_color="#4f46e5", command=self.add_portal_action).pack(side="right")

        self.portal_scroll = ctk.CTkScrollableFrame(portal_card, height=220, fg_color="#0f172a", corner_radius=8)
        self.portal_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ----------------- RIGHT: EMAIL MANAGER -----------------
        email_card = ctk.CTkFrame(cards_grid, fg_color="#1e293b", corner_radius=14, border_width=1, border_color="#334155")
        email_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(email_card, text="✉️ Saved Email Addresses", font=ctk.CTkFont(size=15, weight="bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(email_card, text="Keep track of different resume / work emails.", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", padx=20, pady=(0, 12))

        e_input_box = ctk.CTkFrame(email_card, fg_color="transparent")
        e_input_box.pack(fill="x", padx=20, pady=(0, 12))

        self.new_email_entry = ctk.CTkEntry(e_input_box, placeholder_text="e.g. applicant@gmail.com", fg_color="#0f172a", border_color="#334155")
        self.new_email_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(e_input_box, text="+ Add", width=65, fg_color="#6366f1", hover_color="#4f46e5", command=self.add_email_action).pack(side="right")

        self.email_scroll = ctk.CTkScrollableFrame(email_card, height=220, fg_color="#0f172a", corner_radius=8)
        self.email_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ----------------- BOTTOM: DATA BACKUP & ACTIONS -----------------
        data_card = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=14, border_width=1, border_color="#334155")
        data_card.pack(fill="x", padx=40, pady=(0, 30))

        ctk.CTkLabel(data_card, text="💾 Data Backup & Database Maintenance", font=ctk.CTkFont(size=15, weight="bold"), text_color="#f8fafc").pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(data_card, text="Export all your tracked opportunities or reset the database cleanly.", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", padx=20, pady=(0, 16))

        action_box = ctk.CTkFrame(data_card, fg_color="transparent")
        action_box.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
            action_box, text="📤 Export Applications to CSV / Excel",
            fg_color="#10b981", hover_color="#059669", height=38,
            font=ctk.CTkFont(weight="bold"),
            command=self.export_records
        ).pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            action_box, text="🗑️ Clear Entire Pipeline",
            fg_color="#7f1d1d", hover_color="#991b1b", height=38,
            font=ctk.CTkFont(weight="bold"),
            command=self.clear_all_data
        ).pack(side="left")

        self.refresh_portals_list()
        self.refresh_emails_list()

    def refresh_portals_list(self):
        for w in self.portal_widgets:
            try: w.destroy()
            except Exception: pass
        self.portal_widgets.clear()

        portals = self.db.get_portals()
        for p in portals:
            row = ctk.CTkFrame(self.portal_scroll, fg_color="#1e293b", corner_radius=6)
            row.pack(fill="x", pady=2, padx=4)
            self.portal_widgets.append(row)

            ctk.CTkLabel(row, text=f"🌐 {p}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#f8fafc").pack(side="left", padx=10, pady=6)
            ctk.CTkButton(
                row, text="✕", width=24, height=24, fg_color="#334155", hover_color="#ef4444",
                command=lambda name=p: self.delete_portal_action(name)
            ).pack(side="right", padx=6, pady=4)

    def add_portal_action(self):
        name = self.new_portal_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a portal name.")
            return
        self.db.add_portal(name)
        self.new_portal_entry.delete(0, "end")
        self.refresh_portals_list()
        self.on_change_callback()

    def delete_portal_action(self, name):
        if len(self.db.get_portals()) <= 1:
            messagebox.showwarning("Notice", "At least one portal option must remain.")
            return
        if messagebox.askyesno("Confirm Delete", f"Remove '{name}' from portals?"):
            self.db.delete_portal(name)
            self.refresh_portals_list()
            self.on_change_callback()

    def refresh_emails_list(self):
        for w in self.email_widgets:
            try: w.destroy()
            except Exception: pass
        self.email_widgets.clear()

        emails = self.db.get_emails()
        for e in emails:
            row = ctk.CTkFrame(self.email_scroll, fg_color="#1e293b", corner_radius=6)
            row.pack(fill="x", pady=2, padx=4)
            self.email_widgets.append(row)

            ctk.CTkLabel(row, text=f"✉️ {e}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#f8fafc").pack(side="left", padx=10, pady=6)
            ctk.CTkButton(
                row, text="✕", width=24, height=24, fg_color="#334155", hover_color="#ef4444",
                command=lambda email=e: self.delete_email_action(email)
            ).pack(side="right", padx=6, pady=4)

    def add_email_action(self):
        email_str = self.new_email_entry.get().strip()
        if not email_str or "@" not in email_str or "." not in email_str:
            messagebox.showwarning("Warning", "Please enter a valid email address.")
            return
        self.db.add_email(email_str)
        self.new_email_entry.delete(0, "end")
        self.refresh_emails_list()
        self.on_change_callback()

    def delete_email_action(self, email_str):
        if messagebox.askyesno("Confirm Delete", f"Remove '{email_str}' from saved emails?"):
            self.db.delete_email(email_str)
            self.refresh_emails_list()
            self.on_change_callback()

    def export_records(self):
        df = self.db.get_all_applications()
        if df.empty:
            messagebox.showinfo("Export", "No applications logged to export.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv"), ("Excel Spreadsheet", "*.xlsx")],
            initialfile=f"AppliTrack_Export_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if path:
            try:
                if path.endswith(".xlsx"):
                    df.to_excel(path, index=False)
                else:
                    df.to_csv(path, index=False)
                messagebox.showinfo("AppliTrack", f"Exported {len(df)} records successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def clear_all_data(self):
        if messagebox.askyesno("Confirm Full Reset", "⚠️ Are you sure you want to permanently delete ALL job applications?"):
            self.db.clear_all()
            messagebox.showinfo("Reset Complete", "All records have been cleared.")
            self.on_change_callback()