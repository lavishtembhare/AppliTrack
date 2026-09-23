import customtkinter as ctk
import pandas as pd

class MetricCardsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.apps_card = self.make_card("Total Applications", "0", 0, text_color="#38bdf8")
        self.interview_card = self.make_card("Interviews", "0", 1, text_color="#fbbf24")
        self.offers_card = self.make_card("Offers", "0", 2, text_color="#34d399")
        self.conversion_card = self.make_card("Conversion Rate", "0.0%", 3, text_color="#c084fc")

    def make_card(self, title, val, col, text_color="white"):
        frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1f2937")
        frame.grid(row=0, column=col, sticky="ew", padx=6, pady=2)

        lbl_title = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=12), text_color="#9ca3af")
        lbl_title.pack(anchor="w", padx=16, pady=(12, 2))

        lbl_val = ctk.CTkLabel(frame, text=val, font=ctk.CTkFont(size=22, weight="bold"), text_color=text_color)
        lbl_val.pack(anchor="w", padx=16, pady=(0, 12))
        return lbl_val

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
        conversion_rate = (offers / total * 100) if total > 0 else 0.0

        self.apps_card.configure(text=str(total))
        self.interview_card.configure(text=str(interviews))
        self.offers_card.configure(text=str(offers))
        self.conversion_card.configure(text=f"{conversion_rate:.1f}%")