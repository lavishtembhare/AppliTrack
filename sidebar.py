import customtkinter as ctk

class SidebarView(ctk.CTkFrame):
    def __init__(self, parent, on_navigate):
        super().__init__(parent, width=220, corner_radius=0, fg_color="#0b0f19")
        self.on_navigate = on_navigate
        self.nav_buttons = {}

        self.grid_rowconfigure(5, weight=1)

        # App Brand Header
        header_box = ctk.CTkFrame(self, fg_color="transparent")
        header_box.grid(row=0, column=0, padx=20, pady=(24, 25), sticky="w")

        ctk.CTkLabel(
            header_box, text="💼 AppliTrack",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#38bdf8"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_box, text="Pipeline & Job Engine",
            font=ctk.CTkFont(size=10),
            text_color="#64748b"
        ).pack(anchor="w")

        # Navigation Buttons
        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("add_entry", "➕  Add Application"),
            ("settings", "⚙️  Settings")
        ]

        for idx, (key, label) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                hover_color="#1e293b",
                text_color="#94a3b8",
                corner_radius=8,
                command=lambda k=key: self.select_nav(k)
            )
            btn.grid(row=idx, column=0, padx=14, pady=4, sticky="ew")
            self.nav_buttons[key] = btn

        # Default Active Selection
        self.set_active("dashboard")

        # Footer Badge
        footer_lbl = ctk.CTkLabel(
            self, text="v2.0 • Local SQLite",
            font=ctk.CTkFont(size=10),
            text_color="#475569"
        )
        footer_lbl.grid(row=6, column=0, padx=20, pady=16, sticky="s")

    def select_nav(self, key):
        self.set_active(key)
        self.on_navigate(key)

    def set_active(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color="#6366f1", text_color="#ffffff", hover_color="#4f46e5")
            else:
                btn.configure(fg_color="transparent", text_color="#94a3b8", hover_color="#1e293b")