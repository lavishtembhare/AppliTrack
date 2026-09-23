import customtkinter as ctk
import pandas as pd

class MetricCardsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.apps_card, self.apps_sub = self.make_card("📋 Total Applied", "0", "All-time pipeline", 0, text_color="#38bdf8")
        self.interview_card, self.interview_sub = self.make_card("💬 In Interview", "0", "Active conversations", 1, text_color="#fbbf24")
        self.offers_card, self.offers_sub = self.make_card("🎉 Offers Received", "0", "Success count", 2, text_color="#34d399")
        self.conversion_card, self.conversion_sub = self.make_card("⚡ Conversion Rate", "0.0%", "Offers ÷ Applied", 3, text_color="#c084fc")

    def make_card(self, title, val, sub_text, col, text_color="white"):
        frame = ctk.CTkFrame(
            self, 
            corner_radius=12, 
            fg_color="#1e293b", 
            border_width=1, 
            border_color="#334155"
        )
        frame.grid(row=0, column=col, sticky="ew", padx=6, pady=2)

        lbl_title = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8")
        lbl_title.pack(anchor="w", padx=16, pady=(12, 2))

        lbl_val = ctk.CTkLabel(frame, text=val, font=ctk.CTkFont(size=24, weight="bold"), text_color=text_color)
        lbl_val.pack(anchor="w", padx=16, pady=(0, 2))

        lbl_sub = ctk.CTkLabel(frame, text=sub_text, font=ctk.CTkFont(size=10), text_color="#64748b")
        lbl_sub.pack(anchor="w", padx=16, pady=(0, 10))

        return lbl_val, lbl_sub

    def update_metrics(self, df: pd.DataFrame):
        if df is None or df.empty:
            self.apps_card.configure(text="0")
            self.interview_card.configure(text="0")
            self.offers_card.configure(text="0")
            self.conversion_card.configure(text="0.0%")
            return

        total = len(df)
        interviews = len(df[df["status"] == "Interview"])
        offers = len(df[df["status"] == "Offer"])
        rejected = len(df[df["status"] == "Rejected"])
        conversion_rate = (offers / total * 100) if total > 0 else 0.0

        self.apps_card.configure(text=str(total))
        self.interview_card.configure(text=str(interviews))
        self.interview_sub.configure(text=f"{round((interviews/total)*100, 1)}% of pipeline" if total > 0 else "")
        self.offers_card.configure(text=str(offers))
        self.conversion_card.configure(text=f"{conversion_rate:.1f}%")
        self.conversion_sub.configure(text=f"{rejected} rejected" if rejected > 0 else "No rejections yet")