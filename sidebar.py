import customtkinter as ctk

class SidebarView(ctk.CTkFrame):
    def __init__(self, parent, on_navigate):
        super().__init__(parent, width=230, corner_radius=0, fg_color="#08090e", border_width=0)
        self.on_navigate = on_navigate
        self.nav_buttons = {}

        self.grid_rowconfigure(6, weight=1)

        # Tech Brand Header
        header_box = ctk.CTkFrame(self, fg_color="transparent")
        header_box.grid(row=0, column=0, padx=20, pady=(24, 25), sticky="w")

        ctk.CTkLabel(
            header_box, text="⚡ APPLITRACK",
            font=ctk.CTkFont(family="Consolas", size=19, weight="bold"),
            text_color="#00f0ff"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_box, text="// CAREER OS • EXECUTIVE",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color="#64748b"
        ).pack(anchor="w")

        # 4 Primary Navigation Items
        nav_items = [
            ("dashboard", "⚡  Dashboard"),
            ("applications", "📑  Applications"),
            ("add_entry", "➕  Log Application"),
            ("settings", "⚙️  System Config")
        ]

        for idx, (key, label) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                height=42,
                font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                fg_color="transparent",
                hover_color="#131522",
                text_color="#94a3b8",
                corner_radius=8,
                command=lambda k=key: self.select_nav(k)
            )
            btn.grid(row=idx, column=0, padx=14, pady=4, sticky="ew")
            self.nav_buttons[key] = btn

        self.set_active("dashboard")

        # Footer Status Tag
        status_card = ctk.CTkFrame(self, fg_color="#0e111a", corner_radius=8, border_width=1, border_color="#1a1e2e")
        status_card.grid(row=7, column=0, padx=14, pady=16, sticky="ew")

        ctk.CTkLabel(
            status_card, text="● ENGINE ENCRYPTED",
            font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
            text_color="#00f5a0"
        ).pack(anchor="w", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            status_card, text="SQLite local database",
            font=ctk.CTkFont(size=9),
            text_color="#475569"
        ).pack(anchor="w", padx=10, pady=(0, 8))

    def select_nav(self, key):
        self.set_active(key)
        self.on_navigate(key)

    def set_active(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color="#141727",
                    text_color="#00f0ff",
                    hover_color="#191d33",
                    border_width=1,
                    border_color="#2b3152"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#94a3b8",
                    hover_color="#11131e",
                    border_width=0
                )