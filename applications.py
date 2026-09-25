import re
from difflib import SequenceMatcher
import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

STATUS_THEMES = {
    "Applied": {"bg": "#07202c", "text": "#00f0ff", "border": "#0e4e63"},
    "Interview": {"bg": "#2b1b04", "text": "#fbbf24", "border": "#633c09"},
    "Offer": {"bg": "#022915", "text": "#00f5a0", "border": "#055c32"},
    "Rejected": {"bg": "#26060e", "text": "#fb7185", "border": "#5c1023"},
}

PAGE_SIZE = 25


def fuzzy_search_and_rank(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Intelligent cross-field search algorithm:
    1. Multi-token omnibar matching across Company, Role, Conduit, Email, Notes, Date.
    2. Fuzzy typo-tolerance using Levenshtein-style ratio matching.
    3. Weighted relevance scoring (Exact > Prefix > Substring > Fuzzy).
    """
    clean_query = query.strip().lower()
    if not clean_query or df.empty:
        return df

    tokens = clean_query.split()
    scored_results = []

    for idx, row in df.iterrows():
        comp = str(row.get("company", "")).lower()
        role = str(row.get("role", "")).lower()
        portal = str(row.get("portal", "")).lower()
        email = str(row.get("applied_email", "")).lower()
        notes = str(row.get("notes", "")).lower()
        date_str = str(row.get("date_applied", "")).lower()

        combined_text = f"{comp} {role} {portal} {email} {notes} {date_str}"
        words_in_row = re.findall(r"\w+", combined_text)

        score = 0
        all_tokens_matched = True

        for token in tokens:
            token_matched = False

            # 1. Exact field match (Highest priority)
            if token == comp or token == role:
                score += 80
                token_matched = True
            # 2. Prefix match (Company / Role starts with token)
            elif comp.startswith(token) or role.startswith(token):
                score += 50
                token_matched = True
            # 3. Substring match anywhere in the record
            elif token in combined_text:
                score += 30
                token_matched = True
            else:
                # 4. Fuzzy match against individual words (Typo tolerance)
                token_len = len(token)
                if token_len >= 3:
                    for word in words_in_row:
                        # Quick length delta filter before expensive SequenceMatcher
                        if abs(len(word) - token_len) <= 2:
                            ratio = SequenceMatcher(None, token, word).ratio()
                            if ratio >= 0.75:
                                score += int(ratio * 20)
                                token_matched = True
                                break

            if not token_matched:
                all_tokens_matched = False
                break

        if all_tokens_matched and score > 0:
            # Bonus points if the entire phrase appears verbatim
            if clean_query in combined_text:
                score += 40
            scored_results.append((idx, score))

    if not scored_results:
        return df.iloc[0:0]

    # Rank rows by highest match score first
    scored_results.sort(key=lambda item: item[1], reverse=True)
    sorted_indices = [item[0] for item in scored_results]

    return df.loc[sorted_indices]


class ApplicationHistoryView(ctk.CTkFrame):
    def __init__(self, parent, on_delete_callback, on_status_change_callback, on_clear_all_callback):
        super().__init__(parent, fg_color="transparent")
        self.on_delete_callback = on_delete_callback
        self.on_status_change_callback = on_status_change_callback
        self.on_clear_all_callback = on_clear_all_callback

        self.current_filter = "All"
        self.search_term = ""
        self.sort_by = "Date Applied"
        self.sort_direction = "Newest First"
        self.raw_df = None
        self.visible_limit = PAGE_SIZE
        self._debounce_timer = None

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Control Deck
        control_deck = ctk.CTkFrame(
            self, fg_color="#11131e", corner_radius=14,
            border_width=1, border_color="#1e2235"
        )
        control_deck.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 12))
        control_deck.grid_columnconfigure(1, weight=1)

        header_left = ctk.CTkFrame(control_deck, fg_color="transparent")
        header_left.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="w")

        ctk.CTkLabel(
            header_left, text="📂 Pipeline Repository",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f8fafc"
        ).pack(side="left")

        self.count_badge = ctk.CTkLabel(
            header_left, text="[00 Tracks]",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#00f0ff"
        )
        self.count_badge.pack(side="left", padx=10)

        ctk.CTkButton(
            control_deck, text="🗑️ Purge All", width=110, height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#380b15", hover_color="#540f1f", text_color="#f43f5e",
            border_width=1, border_color="#540f1f",
            command=self._handle_clear_all
        ).grid(row=0, column=2, padx=20, pady=(16, 12), sticky="e")

        # Search Bar + Sort Dropdowns
        filter_bar = ctk.CTkFrame(control_deck, fg_color="transparent")
        filter_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 16))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Smart search (e.g. 'Google Senior', 'Stripe Remote', 'Indeed')...",
            height=38,
            fg_color="#0a0b12",
            border_color="#1e2235",
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_keyrelease)

        ctk.CTkLabel(filter_bar, text="Sort by:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8").grid(row=0, column=1, padx=(0, 6))
        self.sort_field_menu = ctk.CTkOptionMenu(
            filter_bar,
            values=["Date Applied", "Company", "Role", "Status"],
            width=130, height=36,
            fg_color="#0a0b12", button_color="#1e2235",
            command=self._on_sort_field_changed
        )
        self.sort_field_menu.set("Date Applied")
        self.sort_field_menu.grid(row=0, column=2, padx=(0, 8))

        self.sort_dir_menu = ctk.CTkOptionMenu(
            filter_bar,
            values=["Newest First", "Oldest First"],
            width=135, height=36,
            fg_color="#0a0b12", button_color="#1e2235",
            command=self._on_sort_dir_changed
        )
        self.sort_dir_menu.set("Newest First")
        self.sort_dir_menu.grid(row=0, column=3)

        # Status Tabs
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 10))

        self.filter_buttons = {}
        for cat in ["All", "Applied", "Interview", "Offer", "Rejected"]:
            btn = ctk.CTkButton(
                self.filter_frame,
                text=cat,
                height=30,
                font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                fg_color="#6366f1" if cat == "All" else "#11131e",
                hover_color="#4f46e5",
                text_color="#ffffff" if cat == "All" else "#94a3b8",
                border_width=1,
                border_color="#6366f1" if cat == "All" else "#1e2235",
                corner_radius=8,
                command=lambda c=cat: self.apply_filter(c)
            )
            btn.pack(side="left", padx=(0, 8))
            self.filter_buttons[cat] = btn

        # Scroll Area
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll_area.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 15))

    def _on_search_keyrelease(self, event):
        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(140, self._apply_search)

    def _apply_search(self):
        self.search_term = self.search_entry.get().strip().lower()
        self.visible_limit = PAGE_SIZE
        self.render_rows()

    def _on_sort_field_changed(self, field_val):
        self.sort_by = field_val
        if field_val in ["Company", "Role", "Status"]:
            self.sort_dir_menu.configure(values=["A to Z", "Z to A"])
            self.sort_dir_menu.set("A to Z")
            self.sort_direction = "A to Z"
        else:
            self.sort_dir_menu.configure(values=["Newest First", "Oldest First"])
            self.sort_dir_menu.set("Newest First")
            self.sort_direction = "Newest First"
        self.visible_limit = PAGE_SIZE
        self.render_rows()

    def _on_sort_dir_changed(self, dir_val):
        self.sort_direction = dir_val
        self.visible_limit = PAGE_SIZE
        self.render_rows()

    def apply_filter(self, selected_filter):
        self.current_filter = selected_filter
        for cat, btn in self.filter_buttons.items():
            is_active = (cat == selected_filter)
            btn.configure(
                fg_color="#6366f1" if is_active else "#11131e",
                text_color="#ffffff" if is_active else "#94a3b8",
                border_color="#6366f1" if is_active else "#1e2235"
            )
        self.visible_limit = PAGE_SIZE
        self.render_rows()

    def _handle_clear_all(self):
        if self.raw_df is None or self.raw_df.empty:
            messagebox.showinfo("Purge", "No applications in repository.")
            return

        confirm = messagebox.askyesno(
            "System Purge",
            "⚠️ Purge all opportunity records? This will delete local SQLite entries permanently."
        )
        if confirm:
            self.on_clear_all_callback()

    def render_list(self, df: pd.DataFrame):
        self.raw_df = df
        self.visible_limit = PAGE_SIZE
        self.render_rows()

    def load_more(self):
        self.visible_limit += PAGE_SIZE
        self.render_rows()

    def render_rows(self):
        for widget in self.scroll_area.winfo_children():
            widget.destroy()

        if self.raw_df is None or self.raw_df.empty:
            self.count_badge.configure(text="[00 Tracks]")
            lbl = ctk.CTkLabel(self.scroll_area, text="No application records found.", font=ctk.CTkFont(size=13), text_color="#475569")
            lbl.pack(pady=40)
            return

        total_cnt = len(self.raw_df)
        self.count_badge.configure(text=f"[{total_cnt:02d} Tracks]")

        for cat, btn in self.filter_buttons.items():
            cnt = total_cnt if cat == "All" else len(self.raw_df[self.raw_df["status"] == cat])
            btn.configure(text=f"{cat} [{cnt:02d}]")

        df = self.raw_df.copy()

        # Step 1: Category Filter
        if self.current_filter != "All":
            df = df[df["status"] == self.current_filter]

        # Step 2: Intelligent Multi-Token & Fuzzy Search
        if self.search_term:
            df = fuzzy_search_and_rank(df, self.search_term)
        else:
            # Step 3: Standard Field Sorting (When not searching)
            ascending = self.sort_direction in ["Oldest First", "A to Z"]
            col_target = {
                "Date Applied": "date_applied",
                "Company": "company",
                "Role": "role",
                "Status": "status"
            }.get(self.sort_by, "date_applied")
            df = df.sort_values(by=[col_target, "id"], ascending=[ascending, ascending])

        if df.empty:
            lbl = ctk.CTkLabel(
                self.scroll_area,
                text="No matching records found. (Try typing partial names or keywords)",
                font=ctk.CTkFont(size=13),
                text_color="#475569"
            )
            lbl.pack(pady=35)
            return

        matched_total = len(df)
        visible_df = df.iloc[:self.visible_limit]

        for _, row in visible_df.iterrows():
            status_val = row["status"]
            theme = STATUS_THEMES.get(status_val, {"bg": "#11131e", "text": "#94a3b8", "border": "#1e2235"})

            row_card = ctk.CTkFrame(
                self.scroll_area,
                fg_color="#0d0f18",
                border_width=1,
                border_color="#1c2032",
                corner_radius=10
            )
            row_card.pack(fill="x", pady=4, padx=5)

            left_col = ctk.CTkFrame(row_card, fg_color="transparent")
            left_col.pack(side="left", padx=16, pady=12)

            initial = row['company'][:2].upper() if row['company'] else "AP"
            avatar = ctk.CTkLabel(
                left_col, text=initial, width=42, height=42,
                corner_radius=8, fg_color="#141724",
                font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                text_color="#00f0ff"
            )
            avatar.pack(side="left", padx=(0, 14))

            info_box = ctk.CTkFrame(left_col, fg_color="transparent")
            info_box.pack(side="left")

            ctk.CTkLabel(
                info_box, text=f"{row['company']}  —  {row['role']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#f8fafc"
            ).pack(anchor="w")

            portal_val = row.get("portal", "")
            portal_str = portal_val if portal_val else "Direct"
            email_val = row.get("applied_email", "")

            meta_parts = [f"📅 {row['date_applied']}", f"🌐 {portal_str}"]
            if email_val:
                meta_parts.append(f"✉️ {email_val}")
            if row.get("notes"):
                meta_parts.append(f"📝 {row['notes']}")

            ctk.CTkLabel(
                info_box,
                text="   •   ".join(meta_parts),
                font=ctk.CTkFont(size=11),
                text_color="#64748b"
            ).pack(anchor="w")

            right_col = ctk.CTkFrame(row_card, fg_color="transparent")
            right_col.pack(side="right", padx=14, pady=12)

            status_menu = ctk.CTkOptionMenu(
                right_col,
                values=["Applied", "Interview", "Offer", "Rejected"],
                width=120, height=30,
                fg_color=theme["bg"],
                text_color=theme["text"],
                font=ctk.CTkFont(family="Consolas", weight="bold", size=11),
                command=lambda new_val, aid=row["id"]: self.on_status_change_callback(aid, new_val)
            )
            status_menu.set(status_val)
            status_menu.pack(side="left", padx=(0, 10))

            del_btn = ctk.CTkButton(
                right_col, text="✕", width=30, height=30,
                fg_color="#181c2b", hover_color="#ef4444",
                text_color="#94a3b8",
                font=ctk.CTkFont(weight="bold"),
                command=lambda aid=row["id"]: self.on_delete_callback(aid)
            )
            del_btn.pack(side="left")

        # Load More Button
        if matched_total > self.visible_limit:
            remaining = matched_total - self.visible_limit
            load_btn = ctk.CTkButton(
                self.scroll_area,
                text=f"⬇️ Load More Records ({remaining} remaining)",
                height=34,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#141724", hover_color="#1e2235", text_color="#38bdf8",
                border_width=1, border_color="#1e2235",
                command=self.load_more
            )
            load_btn.pack(fill="x", pady=12, padx=20)