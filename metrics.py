import customtkinter as ctk
import pandas as pd

class MetricCardsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.apps_card, self.apps_sub = self.make_card(
            icon="📊", tag="TOTAL APPLICATIONS", title="Pipeline Volume", val="00", sub="All-time targets logged",
            col=0, accent_color="#00f0ff"
        )
        self.interview_card, self.interview_sub = self.make_card(
            icon="⏳", tag="IN PROGRESS", title="Active Interviews", val="00", sub="Rounds underway",
            col=1, accent_color="#f59e0b"
        )
        self.offers_card, self.offers_sub = self.make_card(
            icon="🏆", tag="OFFERS SECURED", title="Offer Pipeline", val="00", sub="Conversion targets",
            col=2, accent_color="#00f5a0"
        )
        self.conversion_card, self.conversion_sub = self.make_card(
            icon="📈", tag="SUCCESS RATIO", title="Yield Rate", val="00.0%", sub="Offers ÷ Submissions",
            col=3, accent_color="#a855f7"
        )

    def make_card(self, icon, tag, title, val, sub, col, accent_color):
        frame = ctk.CTkFrame(
            self, corner_radius=12, fg_color="#11131e",
            border_width=1, border_color="#1e2235"
        )
        frame.grid(row=0, column=col, sticky="ew", padx=6, pady=2)

        top_row = ctk.CTkFrame(frame, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(12, 2))

        ctk.CTkLabel(
            top_row, text=f"{icon}  {tag}",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color=accent_color
        ).pack(side="left")

        ctk.CTkLabel(
            frame, text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=16, pady=(2, 0))

        lbl_val = ctk.CTkLabel(
            frame, text=val,
            font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
            text_color="#f8fafc"
        )
        lbl_val.pack(anchor="w", padx=16, pady=(2, 0))

        lbl_sub = ctk.CTkLabel(
            frame, text=sub,
            font=ctk.CTkFont(size=10),
            text_color="#64748b"
        )
        lbl_sub.pack(anchor="w", padx=16, pady=(0, 12))

        return lbl_val, lbl_sub

    def update_metrics(self, df: pd.DataFrame):
        if df is None or df.empty:
            self.apps_card.configure(text="00")
            self.interview_card.configure(text="00")
            self.offers_card.configure(text="00")
            self.conversion_card.configure(text="00.0%")
            return

        total = len(df)
        interviews = len(df[df["status"] == "Interview"])
        offers = len(df[df["status"] == "Offer"])
        rejected = len(df[df["status"] == "Rejected"])
        conversion_rate = (offers / total * 100) if total > 0 else 0.0

        self.apps_card.configure(text=f"{total:02d}")
        self.interview_card.configure(text=f"{interviews:02d}")
        self.interview_sub.configure(text=f"{(interviews/total)*100:.1f}% pipeline share" if total > 0 else "")
        self.offers_card.configure(text=f"{offers:02d}")
        self.conversion_card.configure(text=f"{conversion_rate:.1f}%")
        self.conversion_sub.configure(text=f"{rejected} rejections archived" if rejected > 0 else "Clean record • 0 rejected")