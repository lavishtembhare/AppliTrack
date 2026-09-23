from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

class EntryView(ctk.CTkScrollableFrame):
    def __init__(self, parent, db, on_application_saved):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_application_saved = on_application_saved

        # Header Title
        title_box = ctk.CTkFrame(self, fg_color="transparent")
        title_box.pack(fill="x", padx=40, pady=(30, 20))

        ctk.CTkLabel(
            title_box, text="📝 Log New Job Application",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box, text="Fill out the details below to add a new opportunity to your pipeline tracker.",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        ).pack(anchor="w")

        # Main Centered Card Container
        self.form_card = ctk.CTkFrame(
            self, fg_color="#1e293b", corner_radius=14, 
            border_width=1, border_color="#334155"
        )
        self.form_card.pack(fill="x", padx=40, pady=(0, 30))
        self.form_card.grid_columnconfigure((0, 1), weight=1)

        # Field 1: Company
        ctk.CTkLabel(self.form_card, text="Company Name *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1").grid(row=0, column=0, padx=25, pady=(25, 4), sticky="w")
        self.company_entry = ctk.CTkEntry(self.form_card, placeholder_text="e.g. Google, Stripe, Notion", height=38, fg_color="#0f172a", border_color="#334155")
        self.company_entry.grid(row=1, column=0, padx=25, pady=(0, 16), sticky="ew")

        # Field 2: Role
        ctk.CTkLabel(self.form_card, text="Role / Position *", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1").grid(row=0, column=1, padx=25, pady=(25, 4), sticky="w")
        self.role_entry = ctk.CTkEntry(self.form_card, placeholder_text="e.g. Senior Data Analyst", height=38, fg_color="#0f172a", border_color="#334155")
        self.role_entry.grid(row=1, column=1, padx=25, pady=(0, 16), sticky="ew")

        # Field 3: Portal
        ctk.CTkLabel(self.form_card, text="Applied Through (Portal)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1").grid(row=2, column=0, padx=25, pady=(0, 4), sticky="w")
        self.portal_menu = ctk.CTkOptionMenu(self.form_card, height=38, fg_color="#0f172a", button_color="#334155")
        self.portal_menu.grid(row=3, column=0, padx=25, pady=(0, 16), sticky="ew")

        # Field 4: Email Applied Through
        ctk.CTkLabel(self.form_card, text="Email Account Used", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1").grid(row=2, column=1, padx=25, pady=(0, 4), sticky="w")
        self.email_menu = ctk.CTkOptionMenu(self.form_card, height=38, fg_color="#0f172a", button_color="#334155")
        self.email_menu.grid(row=3, column=1, padx=25, pady=(0, 16), sticky="ew")

        # Field 5: Date Applied
        date_header = ctk.CTkFrame(self.form_card, fg_color="transparent")
        date_header.grid(row=4, column=0, padx=25, pady=(0, 4), sticky="ew")
        ctk.CTkLabel(date_header, text="Date Applied", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1").pack(side="left")
        ctk.CTkButton(date_header, text="Set Today", width=65, height=20, font=ctk.CTkFont(size=10), fg_color="#334155", hover_color="#475569", command=self.set_today).pack(side="right")

        self.date_entry = ctk.CTkEntry(self.form_card, height=38, fg_color="#0f172a", border_color="#334155")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=5, column=0, padx=25, pady=(0, 16), sticky="ew")

        # Field 6: Status
        ctk.CTkLabel(self.form_card, text="Current Pipeline Stage", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1").grid(row=4, column=1, padx=25, pady=(0, 4), sticky="w")
        self.status_menu = ctk.CTkOptionMenu(
            self.form_card, values=["Applied", "Interview", "Offer", "Rejected"],
            height=38, fg_color="#0f172a", button_color="#334155"
        )
        self.status_menu.set("Applied")
        self.status_menu.grid(row=5, column=1, padx=25, pady=(0, 16), sticky="ew")

        # Field 7: Notes & Job Description (Spans both columns)
        ctk.CTkLabel(self.form_card, text="Notes, Links, or Referral Details", font=ctk.CTkFont(size=12, weight="bold"), text_color="#cbd5e1").grid(row=6, column=0, columnspan=2, padx=25, pady=(0, 4), sticky="w")
        self.notes_entry = ctk.CTkEntry(self.form_card, placeholder_text="e.g. Job post URL, recruiter contact, referral name, salary range", height=38, fg_color="#0f172a", border_color="#334155")
        self.notes_entry.grid(row=7, column=0, columnspan=2, padx=25, pady=(0, 25), sticky="ew")

        # Action Buttons Row
        btn_box = ctk.CTkFrame(self.form_card, fg_color="transparent")
        btn_box.grid(row=8, column=0, columnspan=2, padx=25, pady=(0, 25), sticky="e")

        ctk.CTkButton(
            btn_box, text="Clear Form", width=100, height=40,
            fg_color="#334155", hover_color="#475569",
            command=self.clear_inputs
        ).pack(side="left", padx=(0, 12))

        self.submit_btn = ctk.CTkButton(
            btn_box, text="➕ Save to Pipeline", width=180, height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#6366f1", hover_color="#4f46e5",
            command=self.save_application
        )
        self.submit_btn.pack(side="left")

        self.refresh_dropdowns()

    def set_today(self):
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def clear_inputs(self):
        self.company_entry.delete(0, "end")
        self.role_entry.delete(0, "end")
        self.notes_entry.delete(0, "end")
        self.status_menu.set("Applied")
        self.set_today()

    def refresh_dropdowns(self):
        portals = self.db.get_portals()
        self.portal_menu.configure(values=portals if portals else ["Other"])
        if "LinkedIn" in portals:
            self.portal_menu.set("LinkedIn")
        elif portals:
            self.portal_menu.set(portals[0])

        emails = self.db.get_emails()
        self.email_menu.configure(values=emails if emails else ["None"])
        if emails:
            self.email_menu.set(emails[0])
        else:
            self.email_menu.set("None")

    def save_application(self):
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
            messagebox.showerror("Validation Error", "Please fill in both Company Name and Role.")
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

        self.clear_inputs()
        self.submit_btn.configure(text="✔ Added Successfully!", fg_color="#10b981")
        self.after(1000, lambda: self.submit_btn.configure(text="➕ Save to Pipeline", fg_color="#6366f1"))

        self.on_application_saved()