import os
from datetime import datetime
import customtkinter as ctk
import pandas as pd
from tkinter import filedialog, messagebox
from database import DEFAULT_EXPORT_PATH

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
            title_box, text="// SYSTEM PARAMETERS & STORAGE",
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box, text="Configure pipeline sorting, default conduits, credential endpoints, and automated exports.",
            font=ctk.CTkFont(size=12),
            text_color="#64748b"
        ).pack(anchor="w")

        # ----------------- TOP CARD: DATA SORTING PREFERENCE -----------------
        sort_card = ctk.CTkFrame(self, fg_color="#11131e", corner_radius=14, border_width=1, border_color="#1e2235")
        sort_card.pack(fill="x", padx=40, pady=(0, 20))

        sort_top = ctk.CTkFrame(sort_card, fg_color="transparent")
        sort_top.pack(fill="x", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            sort_top, text="⚡ PIPELINE DISPLAY ORDER", 
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), 
            text_color="#00f0ff"
        ).pack(side="left")

        current_sort = self.db.get_setting("sort_order", "DESC")
        sort_display_val = "Newest First" if current_sort == "DESC" else "Oldest First"

        self.sort_order_menu = ctk.CTkSegmentedButton(
            sort_card,
            values=["Newest First", "Oldest First"],
            selected_color="#6366f1",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            command=self.save_sort_order
        )
        self.sort_order_menu.set(sort_display_val)
        self.sort_order_menu.pack(fill="x", padx=20, pady=(4, 16))

        # ----------------- TWO COLUMN: PORTALS & EMAILS -----------------
        cards_grid = ctk.CTkFrame(self, fg_color="transparent")
        cards_grid.pack(fill="x", padx=40, pady=(0, 20))
        cards_grid.grid_columnconfigure((0, 1), weight=1)

        # Left Card: Portals
        portal_card = ctk.CTkFrame(cards_grid, fg_color="#11131e", corner_radius=14, border_width=1, border_color="#1e2235")
        portal_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(portal_card, text="🌐 APPLICATION CONDUITS", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#00f0ff").pack(anchor="w", padx=20, pady=(20, 2))
        ctk.CTkLabel(portal_card, text="Registered job boards and sourcing channels.", font=ctk.CTkFont(size=11), text_color="#64748b").pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(portal_card, text="Default Conduit on New Entry:", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=20, pady=(0, 2))
        self.default_portal_menu = ctk.CTkOptionMenu(
            portal_card, height=32,
            fg_color="#0a0b12", button_color="#1e2235",
            command=self.save_default_portal
        )
        self.default_portal_menu.pack(fill="x", padx=20, pady=(0, 12))

        p_input_box = ctk.CTkFrame(portal_card, fg_color="transparent")
        p_input_box.pack(fill="x", padx=20, pady=(0, 12))

        self.new_portal_entry = ctk.CTkEntry(p_input_box, placeholder_text="Conduit name...", fg_color="#0a0b12", border_color="#1e2235")
        self.new_portal_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(p_input_box, text="+ Add", width=65, font=ctk.CTkFont(family="Consolas", weight="bold"), fg_color="#6366f1", hover_color="#4f46e5", command=self.add_portal_action).pack(side="right")

        self.portal_scroll = ctk.CTkScrollableFrame(portal_card, height=180, fg_color="#0a0b12", corner_radius=8)
        self.portal_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Right Card: Emails
        email_card = ctk.CTkFrame(cards_grid, fg_color="#11131e", corner_radius=14, border_width=1, border_color="#1e2235")
        email_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(email_card, text="✉️ CREDENTIAL ADDRESSES", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#a855f7").pack(anchor="w", padx=20, pady=(20, 2))
        ctk.CTkLabel(email_card, text="Registered candidate communication profiles.", font=ctk.CTkFont(size=11), text_color="#64748b").pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(email_card, text="Default Email on New Entry:", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=20, pady=(0, 2))
        self.default_email_menu = ctk.CTkOptionMenu(
            email_card, height=32,
            fg_color="#0a0d16", button_color="#1e2235",
            command=self.save_default_email
        )
        self.default_email_menu.pack(fill="x", padx=20, pady=(0, 12))

        e_input_box = ctk.CTkFrame(email_card, fg_color="transparent")
        e_input_box.pack(fill="x", padx=20, pady=(0, 12))

        self.new_email_entry = ctk.CTkEntry(e_input_box, placeholder_text="applicant@domain.com", fg_color="#0a0d16", border_color="#1e2235")
        self.new_email_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(e_input_box, text="+ Add", width=65, font=ctk.CTkFont(family="Consolas", weight="bold"), fg_color="#6366f1", hover_color="#4f46e5", command=self.add_email_action).pack(side="right")

        self.email_scroll = ctk.CTkScrollableFrame(email_card, height=180, fg_color="#0a0d16", corner_radius=8)
        self.email_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ----------------- BOTTOM CARD: PREDECIDED EXPORT & INGESTION -----------------
        data_card = ctk.CTkFrame(self, fg_color="#11131e", corner_radius=14, border_width=1, border_color="#1e2235")
        data_card.pack(fill="x", padx=40, pady=(0, 30))

        ctk.CTkLabel(data_card, text="💾 PREDECIDED EXPORT PATH & DATA PIPELINE", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#00f5a0").pack(anchor="w", padx=20, pady=(20, 2))
        ctk.CTkLabel(data_card, text="Excel exports save sequentially (1, 2, 3...) directly to your predecided path without popups.", font=ctk.CTkFont(size=11), text_color="#64748b").pack(anchor="w", padx=20, pady=(0, 12))

        path_box = ctk.CTkFrame(data_card, fg_color="transparent")
        path_box.pack(fill="x", padx=20, pady=(0, 16))

        current_dir = self.db.get_setting("export_dir", DEFAULT_EXPORT_PATH)
        self.path_entry = ctk.CTkEntry(
            path_box, height=36,
            fg_color="#0a0d16", border_color="#1e2235",
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.path_entry.insert(0, current_dir)
        self.path_entry.configure(state="readonly")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            path_box, text="Change Folder", width=120, height=36,
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            fg_color="#1e2235", hover_color="#2b3149", text_color="#f8fafc",
            command=self.choose_export_directory
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            path_box, text="Open Folder", width=105, height=36,
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            fg_color="#1e2235", hover_color="#2b3149", text_color="#f8fafc",
            command=self.open_export_directory
        ).pack(side="left")

        # Action Buttons
        action_box = ctk.CTkFrame(data_card, fg_color="transparent")
        action_box.pack(fill="x", padx=20, pady=(0, 20))

        self.export_btn = ctk.CTkButton(
            action_box, text="⚡ Instant Export to Excel (.xlsx)",
            fg_color="#0e2a22", hover_color="#144236", text_color="#00f5a0",
            border_width=1, border_color="#184e3f",
            height=38, font=ctk.CTkFont(family="Consolas", weight="bold"),
            command=self.export_records
        )
        self.export_btn.pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            action_box, text="📥 Ingest / Import Excel (.xlsx / .csv)",
            fg_color="#181c2b", hover_color="#22273d", text_color="#38bdf8",
            border_width=1, border_color="#22273d",
            height=38, font=ctk.CTkFont(family="Consolas", weight="bold"),
            command=self.import_excel_file
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            action_box, text="⚠️ Wipe Entire Database",
            fg_color="#380b15", hover_color="#540f1f", text_color="#f43f5e",
            border_width=1, border_color="#540f1f",
            height=38, font=ctk.CTkFont(family="Consolas", weight="bold"),
            command=self.clear_all_data
        ).pack(side="left")

        self.refresh_portals_list()
        self.refresh_emails_list()

    def save_sort_order(self, selection):
        order_key = "DESC" if "Descending" in selection else "ASC"
        self.db.set_setting("sort_order", order_key)
        self.on_change_callback()

    def save_default_portal(self, selected_portal):
        self.db.set_setting("default_portal", selected_portal)
        self.on_change_callback()

    def save_default_email(self, selected_email):
        self.db.set_setting("default_email", selected_email)
        self.on_change_callback()

    def choose_export_directory(self):
        current = self.path_entry.get()
        new_dir = filedialog.askdirectory(initialdir=current, title="Select Predecided AppliTrack Export Directory")
        if new_dir:
            self.db.set_setting("export_dir", new_dir)
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, new_dir)
            self.path_entry.configure(state="readonly")
            messagebox.showinfo("Export Path Updated", f"Predecided export path saved:\n\n{new_dir}")

    def open_export_directory(self):
        target_dir = self.path_entry.get().strip()
        os.makedirs(target_dir, exist_ok=True)
        try:
            os.startfile(target_dir)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory:\n{str(e)}")

    def export_records(self):
        # Fetch records sorted by ID ascending
        df = self.db.get_applications_for_export()
        if df.empty:
            messagebox.showinfo("Export", "No application records available to export.")
            return

        export_dir = self.path_entry.get().strip()
        os.makedirs(export_dir, exist_ok=True)

        filename = f"AppliTrack_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        full_filepath = os.path.join(export_dir, filename)

        try:
            # Generate sequential ID (1, 2, 3, 4, 5...)
            export_df = df.copy()
            export_df["#"] = list(range(1, len(export_df) + 1))

            # Reorder columns with '#' first
            column_order = ["#", "company", "role", "date_applied", "status", "portal", "applied_email", "notes"]
            export_df = export_df[column_order]

            # Rename to clean executive headers
            export_df = export_df.rename(columns={
                "#": "ID",
                "company": "Company",
                "role": "Role",
                "date_applied": "Date Applied",
                "status": "Pipeline Status",
                "portal": "Applied Through",
                "applied_email": "Applicant Email",
                "notes": "Notes / URL"
            })

            export_df.to_excel(full_filepath, index=False, engine="openpyxl")

            self.export_btn.configure(text="✔ EXPORTED!", fg_color="#00f5a0", text_color="#000000")
            self.after(1500, lambda: self.export_btn.configure(text="⚡ Instant Export to Excel (.xlsx)", fg_color="#0e2a22", text_color="#00f5a0"))

            confirm = messagebox.askyesno(
                "Export Complete",
                f"Successfully exported {len(export_df)} records in sequential order (1, 2, 3...):\n\n{filename}\n\nLocation:\n{export_dir}\n\nOpen export directory now?"
            )
            if confirm:
                os.startfile(export_dir)

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate Excel file:\n{str(e)}")

    def import_excel_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Job Applications Spreadsheet (Excel or CSV)",
            filetypes=[
                ("Spreadsheet Files", "*.xlsx *.xls *.csv"),
                ("Excel Files", "*.xlsx *.xls"),
                ("CSV Files", "*.csv")
            ]
        )
        if not file_path:
            return

        try:
            df = pd.read_csv(file_path) if file_path.lower().endswith(".csv") else pd.read_excel(file_path)

            if df.empty:
                messagebox.showwarning("Empty File", "The selected file contains no data rows.")
                return

            imported_count = self.db.import_applications_from_dataframe(df)
            messagebox.showinfo(
                "Ingestion Complete",
                f"Successfully imported {imported_count} applications into AppliTrack!\n\nNew portals and emails were also auto-registered.\nSource: {os.path.basename(file_path)}"
            )
            self.refresh_portals_list()
            self.refresh_emails_list()
            self.on_change_callback()

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import file:\n{str(e)}")

    def refresh_portals_list(self):
        for w in self.portal_widgets:
            try: w.destroy()
            except Exception: pass
        self.portal_widgets.clear()

        portals = self.db.get_portals()
        saved_default = self.db.get_setting("default_portal", "LinkedIn")

        self.default_portal_menu.configure(values=portals if portals else ["Other"])
        if saved_default in portals:
            self.default_portal_menu.set(saved_default)
        elif portals:
            self.default_portal_menu.set(portals[0])
            self.db.set_setting("default_portal", portals[0])

        for p in portals:
            row = ctk.CTkFrame(self.portal_scroll, fg_color="#11131e", corner_radius=6)
            row.pack(fill="x", pady=2, padx=4)
            self.portal_widgets.append(row)

            is_def = (p == saved_default)
            display_text = f"🌐 {p} (Default)" if is_def else f"🌐 {p}"
            text_color = "#00f0ff" if is_def else "#f8fafc"

            ctk.CTkLabel(row, text=display_text, font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color=text_color).pack(side="left", padx=10, pady=6)
            ctk.CTkButton(
                row, text="✕", width=24, height=24, fg_color="#1e2235", hover_color="#ef4444",
                command=lambda name=p: self.delete_portal_action(name)
            ).pack(side="right", padx=6, pady=4)

    def add_portal_action(self):
        name = self.new_portal_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Conduit name cannot be empty.")
            return
        self.db.add_portal(name)
        self.new_portal_entry.delete(0, "end")
        self.refresh_portals_list()
        self.on_change_callback()

    def delete_portal_action(self, name):
        if len(self.db.get_portals()) <= 1:
            messagebox.showwarning("Notice", "At least one conduit must remain registered.")
            return
        if messagebox.askyesno("Confirm", f"Remove '{name}'?"):
            self.db.delete_portal(name)
            self.refresh_portals_list()
            self.on_change_callback()

    def refresh_emails_list(self):
        for w in self.email_widgets:
            try: w.destroy()
            except Exception: pass
        self.email_widgets.clear()

        emails = self.db.get_emails()
        saved_default = self.db.get_setting("default_email", "")

        self.default_email_menu.configure(values=emails if emails else ["None"])
        if saved_default in emails:
            self.default_email_menu.set(saved_default)
        elif emails:
            self.default_email_menu.set(emails[0])
            self.db.set_setting("default_email", emails[0])
        else:
            self.default_email_menu.set("None")

        for e in emails:
            row = ctk.CTkFrame(self.email_scroll, fg_color="#11131e", corner_radius=6)
            row.pack(fill="x", pady=2, padx=4)
            self.email_widgets.append(row)

            is_def = (e == saved_default)
            display_text = f"✉️ {e} (Default)" if is_def else f"✉️ {e}"
            text_color = "#a855f7" if is_def else "#f8fafc"

            ctk.CTkLabel(row, text=display_text, font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color=text_color).pack(side="left", padx=10, pady=6)
            ctk.CTkButton(
                row, text="✕", width=24, height=24, fg_color="#1e2235", hover_color="#ef4444",
                command=lambda email=e: self.delete_email_action(email)
            ).pack(side="right", padx=6, pady=4)

    def add_email_action(self):
        email_str = self.new_email_entry.get().strip()
        if not email_str or "@" not in email_str or "." not in email_str:
            messagebox.showwarning("Warning", "Valid email address format required.")
            return
        self.db.add_email(email_str)
        self.new_email_entry.delete(0, "end")
        self.refresh_emails_list()
        self.on_change_callback()

    def delete_email_action(self, email_str):
        if messagebox.askyesno("Confirm", f"Remove '{email_str}'?"):
            self.db.delete_email(email_str)
            self.refresh_emails_list()
            self.on_change_callback()

    def clear_all_data(self):
        if messagebox.askyesno("Confirm Wipe", "⚠️ Wipe all applications from SQLite database?"):
            self.db.clear_all()
            messagebox.showinfo("Wiped", "All pipeline records wiped.")
            self.on_change_callback()