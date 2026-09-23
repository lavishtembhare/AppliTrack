from datetime import datetime
import customtkinter as ctk
import pandas as pd
from tkinter import filedialog, messagebox
from dialogs import ManagePortalsDialog, ManageEmailsDialog

class SidebarView(ctk.CTkFrame):
    def __init__(self, parent, db, on_add_callback):
        super().__init__(parent, width=300, corner_radius=0, fg_color="#0b0f19")
        self.db = db
        self.on_add_callback = on_add_callback

        self.grid_rowconfigure(16, weight=1)

        # Header Title & Subtitle
        header_box = ctk.CTkFrame(self, fg_color="transparent")
        header_box.grid(row=0, column=0, padx=20, pady=(20, 14), sticky="w")

        ctk.CTkLabel(
            header_box, text="💼 AppliTrack",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#38bdf8"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_box, text="Job Search & Pipeline Engine",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        ).pack(anchor="w")

        # Company Field
        ctk.CTkLabel(self, text="Target Company:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1").grid(row=1, column=0, padx=20, pady=(0, 2), sticky="w")
        self.company_entry = ctk.CTkEntry(self, placeholder_text="e.g. Google, Figma, Stripe", fg_color="#1e293b", border_color="#334155")
        self.company_entry.grid(row=2, column=0, padx=20, pady=(0, 8), sticky="ew")

        # Role Field
        ctk.CTkLabel(self, text="Role / Position:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1").grid(row=3, column=0, padx=20, pady=(0, 2), sticky="w")
        self.role_entry = ctk.CTkEntry(self, placeholder_text="e.g. Data Analyst", fg_color="#1e293b", border_color="#334155")
        self.role_entry.grid(row=4, column=0, padx=20, pady=(0, 8), sticky="ew")

        # Applied Through (Portal) Row with Manage Button
        portal_header = ctk.CTkFrame(self, fg_color="transparent")
        portal_header.grid(row=5, column=0, padx=20, pady=(0, 2), sticky="ew")
        
        ctk.CTkLabel(portal_header, text="Applied Through (Portal):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1").pack(side="left")
        ctk.CTkButton(
            portal_header, text="⚙️ Manage", width=62, height=18, 
            font=ctk.CTkFont(size=10), fg_color="#334155", hover_color="#475569", 
            command=self.open_manage_portals
        ).pack(side="right")

        portals_list = self.db.get_portals()
        self.portal_menu = ctk.CTkOptionMenu(
            self, values=portals_list if portals_list else ["Other"],
            fg_color="#1e293b", button_color="#334155"
        )
        if "LinkedIn" in portals_list:
            self.portal_menu.set("LinkedIn")
        elif portals_list:
            self.portal_menu.set(portals_list[0])
        self.portal_menu.grid(row=6, column=0, padx=20, pady=(0, 8), sticky="ew")

        # Email Applied Through Dropdown with Manage Button
        email_header = ctk.CTkFrame(self, fg_color="transparent")
        email_header.grid(row=7, column=0, padx=20, pady=(0, 2), sticky="ew")

        ctk.CTkLabel(email_header, text="Email Applied Through:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1").pack(side="left")
        ctk.CTkButton(
            email_header, text="⚙️ Manage", width=62, height=18,
            font=ctk.CTkFont(size=10), fg_color="#334155", hover_color="#475569",
            command=self.open_manage_emails
        ).pack(side="right")

        emails_list = self.db.get_emails()
        self.email_menu = ctk.CTkOptionMenu(
            self, values=emails_list if emails_list else ["None"],
            fg_color="#1e293b", button_color="#334155"
        )
        if emails_list:
            self.email_menu.set(emails_list[0])
        else:
            self.email_menu.set("None")
        self.email_menu.grid(row=8, column=0, padx=20, pady=(0, 8), sticky="ew")

        # Date Row
        date_header = ctk.CTkFrame(self, fg_color="transparent")
        date_header.grid(row=9, column=0, padx=20, pady=(0, 2), sticky="ew")
        ctk.CTkLabel(date_header, text="Date Applied:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1").pack(side="left")
        ctk.CTkButton(date_header, text="Today", width=46, height=18, font=ctk.CTkFont(size=10), fg_color="#334155", hover_color="#475569", command=self.set_today).pack(side="right")

        self.date_entry = ctk.CTkEntry(self, fg_color="#1e293b", border_color="#334155")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=10, column=0, padx=20, pady=(0, 8), sticky="ew")

        # Initial Status Dropdown
        ctk.CTkLabel(self, text="Current Pipeline Stage:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1").grid(row=11, column=0, padx=20, pady=(0, 2), sticky="w")
        self.status_menu = ctk.CTkOptionMenu(
            self, values=["Applied", "Interview", "Offer", "Rejected"],
            fg_color="#1e293b", button_color="#334155"
        )
        self.status_menu.set("Applied")
        self.status_menu.grid(row=12, column=0, padx=20, pady=(0, 8), sticky="ew")

        # Notes
        ctk.CTkLabel(self, text="Notes / URL:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1").grid(row=13, column=0, padx=20, pady=(0, 2), sticky="w")
        self.notes_entry = ctk.CTkEntry(self, placeholder_text="e.g. Referral, Take-home round", fg_color="#1e293b", border_color="#334155")
        self.notes_entry.grid(row=14, column=0, padx=20, pady=(0, 14), sticky="ew")

        # Add Button
        self.add_btn = ctk.CTkButton(
            self, text="➕ Add to Pipeline",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#6366f1", hover_color="#4f46e5",
            height=34, command=self.submit
        )
        self.add_btn.grid(row=15, column=0, padx=20, pady=(0, 8), sticky="ew")

        # Export Button
        self.export_btn = ctk.CTkButton(
            self, text="📤 Export Applications",
            fg_color="#10b981", hover_color="#059669",
            height=30, command=self.export_records
        )
        self.export_btn.grid(row=16, column=0, padx=20, pady=(0, 8), sticky="ew")

    def set_today(self):
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def open_manage_portals(self):
        ManagePortalsDialog(self, self.db, on_portals_changed=self.refresh_portals)

    def refresh_portals(self, new_portal=None):
        portals = self.db.get_portals()
        self.portal_menu.configure(values=portals if portals else ["Other"])
        if new_portal and new_portal in portals:
            self.portal_menu.set(new_portal)
        elif self.portal_menu.get() not in portals and portals:
            self.portal_menu.set(portals[0])

    def open_manage_emails(self):
        ManageEmailsDialog(self, self.db, on_emails_changed=self.refresh_emails)

    def refresh_emails(self, new_email=None):
        emails = self.db.get_emails()
        self.email_menu.configure(values=emails if emails else ["None"])
        if new_email and new_email in emails:
            self.email_menu.set(new_email)
        elif self.email_menu.get() not in emails and emails:
            self.email_menu.set(emails[0])
        elif not emails:
            self.email_menu.set("None")

    def submit(self):
        comp = self.company_entry.get().strip()
        role = self.role_entry.get().strip()
        dt = self.date_entry.get().strip()
        portal = self.portal_menu.get().strip()
        
        email = self.email_menu.get().strip()
        if email == "None":
            email = ""

        st = self.status_menu.get()
        notes = self.notes_entry.get().strip()

        if not comp or not role:
            messagebox.showerror("Validation Error", "Please provide both Company Name and Role.")
            return

        try:
            datetime.strptime(dt, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must follow YYYY-MM-DD format.")
            return

        self.db.add_application(
            company=comp, role=role, date_applied=dt,
            status=st, portal=portal, applied_email=email, notes=notes
        )

        self.company_entry.delete(0, "end")
        self.role_entry.delete(0, "end")
        self.notes_entry.delete(0, "end")
        self.add_btn.configure(text="✔ Logged!", fg_color="#10b981")
        self.after(900, lambda: self.add_btn.configure(text="➕ Add to Pipeline", fg_color="#6366f1"))

        self.on_add_callback(highlight_new=True)

    def export_records(self):
        df = self.db.get_all_applications()
        if df.empty:
            messagebox.showinfo("Export", "No application data to export.")
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