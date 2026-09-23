import customtkinter as ctk
from tkinter import messagebox

class ManagePortalsDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, on_portals_changed):
        super().__init__(parent)
        self.db = db
        self.on_portals_changed = on_portals_changed
        self.portal_row_widgets = []

        self.title("Manage Job Portals")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(fg_color="#0b0f19")
        self.grab_set()

        ctk.CTkLabel(
            self, text="🌐 Application Portals", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f8fafc"
        ).pack(pady=(18, 4))

        ctk.CTkLabel(
            self, text="Add custom portals or remove channels you don't use.",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        ).pack(pady=(0, 14))

        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=(0, 12))

        self.new_portal_entry = ctk.CTkEntry(
            add_frame, placeholder_text="e.g. Y Combinator, ZipRecruiter...",
            fg_color="#1e293b", border_color="#334155"
        )
        self.new_portal_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            add_frame, text="+ Add", width=70,
            fg_color="#6366f1", hover_color="#4f46e5",
            font=ctk.CTkFont(weight="bold"),
            command=self.add_portal_action
        ).pack(side="right")

        self.scroll_area = ctk.CTkScrollableFrame(
            self, height=270, fg_color="#1e293b", 
            border_width=1, border_color="#334155", corner_radius=10
        )
        self.scroll_area.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.load_portals_list()

    def load_portals_list(self):
        for w in self.portal_row_widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self.portal_row_widgets.clear()

        portals = self.db.get_portals()
        for portal in portals:
            row = ctk.CTkFrame(self.scroll_area, fg_color="#0f172a", corner_radius=6)
            row.pack(fill="x", pady=3, padx=4)
            self.portal_row_widgets.append(row)

            ctk.CTkLabel(
                row, text=f"🌐 {portal}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#f8fafc"
            ).pack(side="left", padx=12, pady=6)

            del_btn = ctk.CTkButton(
                row, text="🗑️", width=28, height=26,
                fg_color="#334155", hover_color="#ef4444",
                command=lambda p=portal: self.delete_portal_action(p)
            )
            del_btn.pack(side="right", padx=8, pady=4)

    def add_portal_action(self):
        name = self.new_portal_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Portal name cannot be empty.")
            return

        self.db.add_portal(name)
        self.new_portal_entry.delete(0, "end")
        self.load_portals_list()
        self.on_portals_changed(new_portal=name)

    def delete_portal_action(self, portal_name):
        portals = self.db.get_portals()
        if len(portals) <= 1:
            messagebox.showwarning("Cannot Delete", "At least one portal option is required.")
            return

        if messagebox.askyesno("Confirm Delete", f"Remove '{portal_name}' from your portals list?"):
            self.db.delete_portal(portal_name)
            self.load_portals_list()
            self.on_portals_changed()