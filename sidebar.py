from datetime import datetime
import customtkinter as ctk
import pandas as pd
from tkinter import filedialog, messagebox

class SidebarView(ctk.CTkFrame):
    def __init__(self, parent, db, on_add_callback):
        super().__init__(parent, width=280, corner_radius=0, fg_color="#111827")
        self.db = db
        self.on_add_callback = on_add_callback

        self.grid_rowconfigure(14, weight=1)

        # Header Title
        ctk.CTkLabel(
            self, text="💼 Job Tracker",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#38bdf8"
        ).grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")

        # Company Field
        ctk.CTkLabel(self, text="Company Name:", font=ctk.CTkFont(size=11), text_color="#9ca3af").grid(row=1, column=0, padx=20, pady=(0, 2), sticky="w")
        self.company_entry = ctk.CTkEntry(self, placeholder_text="e.g. Google, Stripe")
        self.company_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Role Field
        ctk.CTkLabel(self, text="Role / Position:", font=ctk.CTkFont(size=11), text_color="#9ca3af").grid(row=3, column=0, padx=20, pady=(0, 2), sticky="w")
        self.role_entry = ctk.CTkEntry(self, placeholder_text="e.g. Data Analyst")
        self.role_entry.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Date Applied
        ctk.CTkLabel(self, text="Date Applied (YYYY-MM-DD):", font=ctk.CTkFont(size=11), text_color="#9ca3af").grid(row=5, column=0, padx=20, pady=(0, 2), sticky="w")
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Status Dropdown
        ctk.CTkLabel(self, text="Current Status:", font=ctk.CTkFont(size=11), text_color="#9ca3af").grid(row=7, column=0, padx=20, pady=(0, 2), sticky="w")
        self.status_menu = ctk.CTkOptionMenu(
            self,
            values=["Applied", "Interview", "Offer", "Rejected"],
            fg_color="#374151"
        )
        self.status_menu.set("Applied")
        self.status_menu.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Notes
        ctk.CTkLabel(self, text="Notes / Link:", font=ctk.CTkFont(size=11), text_color="#9ca3af").grid(row=9, column=0, padx=20, pady=(0, 2), sticky="w")
        self.notes_entry = ctk.CTkEntry(self, placeholder_text="e.g. Referral, Take-home")
        self.notes_entry.grid(row=10, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Add Button
        self.add_btn = ctk.CTkButton(
            self, text="➕ Add Application",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#6366f1", hover_color="#4f46e5",
            command=self.submit
        )
        self.add_btn.grid(row=11, column=0, padx=20, pady=(0, 12), sticky="ew")

        # Export Excel / CSV
        self.export_btn = ctk.CTkButton(
            self, text="📤 Export Applications",
            fg_color="#10b981", hover_color="#059669",
            command=self.export_records
        )
        self.export_btn.grid(row=12, column=0, padx=20, pady=(0, 6), sticky="ew")

    def submit(self):
        comp = self.company_entry.get().strip()
        role = self.role_entry.get().strip()
        dt = self.date_entry.get().strip()
        st = self.status_menu.get()
        notes = self.notes_entry.get().strip()

        if not comp or not role:
            messagebox.showerror("Validation Error", "Please provide both Company and Role.")
            return

        try:
            datetime.strptime(dt, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must follow YYYY-MM-DD format.")
            return

        self.db.add_application(comp, role, dt, st, notes)

        # Clean form & give visual feedback
        self.company_entry.delete(0, "end")
        self.role_entry.delete(0, "end")
        self.notes_entry.delete(0, "end")
        self.add_btn.configure(text="✔ Added!", fg_color="#10b981")
        self.after(900, lambda: self.add_btn.configure(text="➕ Add Application", fg_color="#6366f1"))

        self.on_add_callback(highlight_new=True)

    def export_records(self):
        df = self.db.get_all_applications()
        if df.empty:
            messagebox.showinfo("Export", "No application data to export.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv"), ("Excel Spreadsheet", "*.xlsx")],
            initialfile=f"Job_Applications_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if path:
            try:
                if path.endswith(".xlsx"):
                    df.to_excel(path, index=False)
                else:
                    df.to_csv(path, index=False)
                messagebox.showinfo("Success", f"Saved {len(df)} records successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))