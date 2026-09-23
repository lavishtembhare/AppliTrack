import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

STATUS_THEMES = {
    "Applied": {"bg": "#082f49", "text": "#38bdf8", "border": "#0284c7"},
    "Interview": {"bg": "#451a03", "text": "#fbbf24", "border": "#d97706"},
    "Offer": {"bg": "#064e3b", "text": "#34d399", "border": "#059669"},
    "Rejected": {"bg": "#4c0519", "text": "#f87171", "border": "#e11d48"},
}

class ApplicationHistoryView(ctk.CTkFrame):
    def __init__(self, parent, on_delete_callback, on_status_change_callback, on_clear_all_callback):
        super().__init__(parent, corner_radius=12, fg_color="#1e293b", border_width=1, border_color="#334155")
        self.on_delete_callback = on_delete_callback
        self.on_status_change_callback = on_status_change_callback
        self.on_clear_all_callback = on_clear_all_callback
        self.current_filter = "All"
        self.search_term = ""
        self.raw_df = None
        self.row_cards = []

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Top Header Bar
        header_bar = ctk.CTkFrame(self, fg_color="transparent")
        header_bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        header_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_bar, text="📁 Tracked Opportunities",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc"
        ).grid(row=0, column=0, sticky="w")

        # Instant Live Search Bar
        self.search_entry = ctk.CTkEntry(
            header_bar,
            placeholder_text="🔍 Search company, role, portal, or email...",
            height=30,
            fg_color="#0f172a",
            border_color="#334155"
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(20, 15))
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        ctk.CTkButton(
            header_bar, text="Clear All", width=76, height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#7f1d1d", hover_color="#991b1b",
            command=self._handle_clear_all
        ).grid(row=0, column=2, sticky="e")

        # 2. Filter Tabs
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        self.filter_buttons = {}
        for cat in ["All", "Applied", "Interview", "Offer", "Rejected"]:
            btn = ctk.CTkButton(
                self.filter_frame,
                text=cat,
                height=26,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#6366f1" if cat == "All" else "#0f172a",
                hover_color="#4f46e5",
                command=lambda c=cat: self.apply_filter(c)
            )
            btn.pack(side="left", padx=(0, 6))
            self.filter_buttons[cat] = btn

        # 3. Scrollable Cards Container
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll_area.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))

    def _on_search_changed(self, event):
        self.search_term = self.search_entry.get().strip().lower()
        self.render_rows()

    def apply_filter(self, selected_filter):
        self.current_filter = selected_filter
        for cat, btn in self.filter_buttons.items():
            btn.configure(fg_color="#6366f1" if cat == selected_filter else "#0f172a")
        self.render_rows()

    def _handle_clear_all(self):
        if not self.row_cards:
            messagebox.showinfo("Clear All", "There are no applications to clear.")
            return

        confirm = messagebox.askyesno(
            "Confirm Reset",
            "⚠️ Are you sure you want to permanently clear all job records? This cannot be undone."
        )
        if confirm:
            self.on_clear_all_callback()

    def render_list(self, df: pd.DataFrame, highlight_new=False):
        self.raw_df = df
        self.render_rows(highlight_new=highlight_new)

    def render_rows(self, highlight_new=False):
        for card in self.row_cards:
            try:
                card.destroy()
            except Exception:
                pass
        self.row_cards.clear()

        if self.raw_df is None or self.raw_df.empty:
            lbl = ctk.CTkLabel(self.scroll_area, text="No applications logged yet.", text_color="#64748b")
            lbl.pack(pady=30)
            self.row_cards.append(lbl)
            return

        # Update dynamic badges on buttons
        for cat, btn in self.filter_buttons.items():
            if cat == "All":
                cnt = len(self.raw_df)
            else:
                cnt = len(self.raw_df[self.raw_df["status"] == cat])
            btn.configure(text=f"{cat} ({cnt})")

        # Apply filtering & search
        df = self.raw_df.copy()
        if self.current_filter != "All":
            df = df[df["status"] == self.current_filter]

        if self.search_term:
            df = df[
                df["company"].astype(str).str.lower().str.contains(self.search_term, na=False) |
                df["role"].astype(str).str.lower().str.contains(self.search_term, na=False) |
                df["portal"].astype(str).str.lower().str.contains(self.search_term, na=False) |
                df["applied_email"].astype(str).str.lower().str.contains(self.search_term, na=False) |
                df["notes"].astype(str).str.lower().str.contains(self.search_term, na=False)
            ]

        if df.empty:
            lbl = ctk.CTkLabel(self.scroll_area, text="No applications match your filter.", text_color="#64748b")
            lbl.pack(pady=25)
            self.row_cards.append(lbl)
            return

        for idx, row in df.reset_index(drop=True).iterrows():
            is_newest = (idx == 0 and highlight_new)
            status_val = row["status"]
            theme = STATUS_THEMES.get(status_val, {"bg": "#1e293b", "text": "#94a3b8", "border": "#475569"})

            row_card = ctk.CTkFrame(
                self.scroll_area,
                fg_color="#0f172a" if not is_newest else "#1e1b4b",
                border_width=1,
                border_color="#4338ca" if is_newest else "#334155",
                corner_radius=10
            )
            row_card.pack(fill="x", pady=4, padx=5)
            self.row_cards.append(row_card)

            # Left: Company Avatar + Information
            left_col = ctk.CTkFrame(row_card, fg_color="transparent")
            left_col.pack(side="left", padx=12, pady=10)

            initial = row['company'][:1].upper() if row['company'] else "J"
            avatar = ctk.CTkLabel(
                left_col, text=initial, width=38, height=38,
                corner_radius=8, fg_color="#334155",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#f8fafc"
            )
            avatar.pack(side="left", padx=(0, 12))

            info_box = ctk.CTkFrame(left_col, fg_color="transparent")
            info_box.pack(side="left")

            title_text = f"{row['company']}  —  {row['role']}"
            if is_newest:
                title_text = f"✨ Added Just Now  •  {title_text}"

            ctk.CTkLabel(
                info_box, text=title_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#f8fafc"
            ).pack(anchor="w")

            # Metadata line: Date, Portal, Email, Notes
            portal_val = row.get("portal", "Career Portal")
            email_val = row.get("applied_email", "")

            meta_parts = [f"📅 {row['date_applied']}", f"🌐 {portal_val}"]
            if email_val:
                meta_parts.append(f"✉️ {email_val}")
            if row.get("notes"):
                meta_parts.append(f"📝 {row['notes']}")

            ctk.CTkLabel(
                info_box,
                text="  •  ".join(meta_parts),
                font=ctk.CTkFont(size=11),
                text_color="#94a3b8"
            ).pack(anchor="w")

            # Right: Status Selector + Delete Button
            right_col = ctk.CTkFrame(row_card, fg_color="transparent")
            right_col.pack(side="right", padx=12, pady=10)

            status_menu = ctk.CTkOptionMenu(
                right_col,
                values=["Applied", "Interview", "Offer", "Rejected"],
                width=110,
                height=28,
                fg_color=theme["bg"],
                text_color=theme["text"],
                font=ctk.CTkFont(weight="bold", size=11),
                command=lambda new_val, aid=row["id"]: self.on_status_change_callback(aid, new_val)
            )
            status_menu.set(status_val)
            status_menu.pack(side="left", padx=(0, 10))

            del_btn = ctk.CTkButton(
                right_col, text="✕", width=28, height=28,
                fg_color="#334155", hover_color="#ef4444",
                text_color="#cbd5e1",
                font=ctk.CTkFont(weight="bold"),
                command=lambda aid=row["id"]: self.on_delete_callback(aid)
            )
            del_btn.pack(side="left")