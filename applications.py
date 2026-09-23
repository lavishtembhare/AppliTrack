import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

STATUS_COLORS = {
    "Applied": "#38bdf8",
    "Interview": "#fbbf24",
    "Offer": "#34d399",
    "Rejected": "#f87171"
}

class ApplicationHistoryView(ctk.CTkFrame):
    def __init__(self, parent, on_delete_callback, on_status_change_callback, on_clear_all_callback):
        super().__init__(parent, corner_radius=12, fg_color="#1f2937")
        self.on_delete_callback = on_delete_callback
        self.on_status_change_callback = on_status_change_callback
        self.on_clear_all_callback = on_clear_all_callback
        self.current_filter = "All"
        self.raw_df = None
        self.row_cards = []

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header Bar
        header_bar = ctk.CTkFrame(self, fg_color="transparent")
        header_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 4))
        header_bar.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header_bar, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box, text="Tracked Applications",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f3f4f6"
        ).pack(side="left")

        self.count_badge = ctk.CTkLabel(
            title_box, text="(0)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af"
        )
        self.count_badge.pack(side="left", padx=8)

        ctk.CTkButton(
            header_bar, text="🗑️ Clear All", width=86, height=26,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#991b1b", hover_color="#dc2626",
            command=self._handle_clear_all
        ).pack(side="right")

        # Status Tabs Filter
        self.filter_toggle = ctk.CTkSegmentedButton(
            self,
            values=["All", "Applied", "Interview", "Offer", "Rejected"],
            selected_color="#6366f1",
            command=self.apply_filter
        )
        self.filter_toggle.set("All")
        self.filter_toggle.grid(row=1, column=0, sticky="w", padx=15, pady=(4, 8))

        # Scrollable Area
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll_area.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))

    def apply_filter(self, val):
        self.current_filter = val
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
            self.count_badge.configure(text="(0)")
            lbl = ctk.CTkLabel(self.scroll_area, text="No applications logged yet.", text_color="#6b7280")
            lbl.pack(pady=30)
            self.row_cards.append(lbl)
            return

        df = self.raw_df
        if self.current_filter != "All":
            df = df[df["status"] == self.current_filter]

        self.count_badge.configure(text=f"({len(df)})")

        if df.empty:
            lbl = ctk.CTkLabel(self.scroll_area, text=f"No applications marked as '{self.current_filter}'.", text_color="#6b7280")
            lbl.pack(pady=20)
            self.row_cards.append(lbl)
            return

        for idx, row in df.reset_index(drop=True).iterrows():
            is_newest = (idx == 0 and highlight_new)
            status_val = row["status"]
            status_color = STATUS_COLORS.get(status_val, "#9ca3af")

            row_card = ctk.CTkFrame(
                self.scroll_area,
                fg_color="#182234" if is_newest else "#111827",
                border_width=2 if is_newest else 0,
                border_color="#6366f1",
                corner_radius=8
            )
            row_card.pack(fill="x", pady=4, padx=5)
            self.row_cards.append(row_card)

            # Left Details
            left_col = ctk.CTkFrame(row_card, fg_color="transparent")
            left_col.pack(side="left", padx=12, pady=8)

            company_title = f"{row['company']}  •  {row['role']}"
            if is_newest:
                company_title = f"✨ New  •  {company_title}"

            ctk.CTkLabel(
                left_col, text=company_title,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#f3f4f6"
            ).pack(anchor="w")

            notes_snippet = f"  •  📝 {row['notes']}" if row['notes'] else ""
            ctk.CTkLabel(
                left_col,
                text=f"📅 Applied: {row['date_applied']}{notes_snippet}",
                font=ctk.CTkFont(size=11),
                text_color="#9ca3af"
            ).pack(anchor="w")

            # Right Controls
            right_col = ctk.CTkFrame(row_card, fg_color="transparent")
            right_col.pack(side="right", padx=12, pady=8)

            # Status Selector
            status_menu = ctk.CTkOptionMenu(
                right_col,
                values=["Applied", "Interview", "Offer", "Rejected"],
                width=110,
                height=26,
                fg_color=status_color,
                text_color="#111827",
                font=ctk.CTkFont(weight="bold", size=11),
                command=lambda new_val, aid=row["id"]: self.on_status_change_callback(aid, new_val)
            )
            status_menu.set(status_val)
            status_menu.pack(side="left", padx=(0, 8))

            # Delete
            ctk.CTkButton(
                right_col, text="✕", width=26, height=26,
                fg_color="#374151", hover_color="#ef4444",
                command=lambda aid=row["id"]: self.on_delete_callback(aid)
            ).pack(side="left")