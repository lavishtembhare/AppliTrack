import os
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
            title_box, text="// SYSTEM PARAMETERS & STORAGE",
            font=ctk.CTkFont(family="Consolas", size=22, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box, text="Configure target conduits, credential endpoints, and predetermined automated exports.",
            font=ctk.CTkFont(size=12),
            text_color="#64748b"
        ).pack(anchor="w")

        cards_grid = ctk.CTkFrame(self, fg_color="transparent")
        cards_grid.pack(fill="x", padx=40, pady=(0, 20))
        cards_grid.grid_columnconfigure((0, 1), weight=1)

        # ----------------- LEFT: PORTAL MANAGER -----------------
        portal_card = ctk.CTkFrame(cards_grid, fg_color="#11131e", corner_radius=14, border_width=1, border_color="#1e2235")
        portal_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(portal_card, text="🌐 APPLICATION CONDUITS", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#00f0ff").pack(anchor="w", padx=20, pady=(20, 2))
        ctk.CTkLabel(portal_card, text="Registered job boards and sourcing platforms.", font=ctk.CTkFont(size=11), text_color="#64748b").pack(anchor="w", padx=20, pady=(0, 12))

        p_input_box = ctk.CTkFrame(portal_card, fg_color="transparent")
        p_input_box.pack(fill="x", padx=20, pady=(0, 12))

        self.new_portal_entry = ctk.CTkEntry(p_input_box, placeholder_text="Conduit name...", fg_color="#0a0b12", border_color="#1e2235")
        self.new_portal_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(p_input_box, text="+ Add", width=65, font=ctk.CTkFont(family="Consolas", weight="bold"), fg_color="#6366f1", hover_color="#4f46e5", command=self.add_portal_action).pack(side="right")

        self.portal_scroll = ctk.CTkScrollableFrame(portal_card, height=200, fg_color="#0a0b12", corner_radius=8)
        self.portal_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ----------------- RIGHT: EMAIL MANAGER -----------------
        email_card = ctk.CTkFrame(cards_grid, fg_color="#11131e", corner_radius=14, border_width=1, border_color="#1e2235")
        email_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(email_card, text="✉️ CREDENTIAL ADDRESSES", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#a855f7").pack(anchor="w", padx=20, pady=(20, 2))
        ctk.CTkLabel(email_card, text="Registered communication email profiles.", font=ctk.CTkFont(size=11), text_color="#64748b").pack(anchor="w", padx=20, pady=(0, 12))

        e_input_box = ctk.CTkFrame(email_card, fg_color="transparent")
        e_input_box.pack(fill="x", padx=20, pady=(0, 12))

        self.new_email_entry = ctk.CTkEntry(e_input_box, placeholder_text="applicant@domain.com", fg_color="#0a0b12", border_color="#1e2235")
        self.new_email_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(e_input_box, text="+ Add", width=65, font=ctk.CTkFont(family="Consolas", weight="bold"), fg_color="#6366f1", hover_color="#4f46e5", command=self.add_email_action).pack(side="right")

        self.email_scroll = ctk.CTkScrollableFrame(email_card, height=200, fg_color="#0a0b12", corner_radius=8)
        self.email_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ----------------- BOTTOM: PREDECIDED EXPORT & ARCHIVE -----------------
        data_card = ctk.CTkFrame(self, fg_color="#11131e", corner_radius=14, border_width=1, border_color="#1e2235")
        data_card.pack(fill="x", padx=40, pady=(0, 30))

        ctk.CTkLabel(data_card, text="💾 PREDECIDED EXPORT PATH & ARCHIVE", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#00f5a0").pack(anchor="w", padx=20, pady=(20, 2))
        ctk.CTkLabel(data_card, text="Automated destination where Excel spreadsheets are saved immediately without popups.", font=ctk.CTkFont(size=11), text_color="#64748b").pack(anchor="w", padx=20, pady=(0, 12))

        # Predecided Path Row
        path_box = ctk.CTkFrame(data_card, fg_color="transparent")
        path_box.pack(fill="x", padx=20, pady=(0, 16))

        default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
        current_dir = self.db.get_setting("export_dir", default_dir)

        self.path_entry = ctk.CTkEntry(
            path_box, height=36,
            fg_color="#0a0b12", border_color="#1e2235",
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.path_entry.insert(0, current_dir)
        self.path_entry.configure(state="readonly")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            path_box, text="Change Folder", width=110, height=36,
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            fg_color="#1e2235", hover_color="#2b3149", text_color="#f8fafc",
            command=self.choose_export_directory
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            path_box, text="Open Folder", width=100, height=36,
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
        self.export_btn.pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            action_box, text="⚠️ Wipe Entire Database",
            fg_color="#380b15", hover_color="#540f1f", text_color="#f43f5e",
            border_width=1, border_color="#540f1f",
            height=38, font=ctk.CTkFont(family="Consolas", weight="bold"),
            command=self.clear_all_data
        ).pack(side="left")

        self.refresh_portals_list()
        self.refresh_emails_list()

    def choose_export_directory(self):
        current = self.path_entry.get()
        new_dir = filedialog.askdirectory(initialdir=current, title="Select Predecided Export Directory")
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
        df = self.db.get_all_applications()
        if df.empty:
            messagebox.showinfo("Export", "No application records available to export.")
            return

        export_dir = self.path_entry.get().strip()
        os.makedirs(export_dir, exist_ok=True)

        filename = f"AppliTrack_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        full_filepath = os.path.join(export_dir, filename)

        try:
            # Clean columns for display
            export_df = df.rename(columns={
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
                f"Successfully generated Excel record:\n\n{filename}\n\nLocation:\n{export_dir}\n\nWould you like to open the export folder now?"
            )
            if confirm:
                os.startfile(export_dir)

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save Excel file:\n{str(e)}")

    def refresh_portals_list(self):
        for w in self.portal_widgets:
            try: w.destroy()
            except Exception: pass
        self.portal_widgets.clear()

        for p in self.db.get_portals():
            row = ctk.CTkFrame(self.portal_scroll, fg_color="#11131e", corner_radius=6)
            row.pack(fill="x", pady=2, padx=4)
            self.portal_widgets.append(row)

            ctk.CTkLabel(row, text=f"🌐 {p}", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#f8fafc").pack(side="left", padx=10, pady=6)
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

        for e in self.db.get_emails():
            row = ctk.CTkFrame(self.email_scroll, fg_color="#11131e", corner_radius=6)
            row.pack(fill="x", pady=2, padx=4)
            self.email_widgets.append(row)

            ctk.CTkLabel(row, text=f"✉️ {e}", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#f8fafc").pack(side="left", padx=10, pady=6)
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