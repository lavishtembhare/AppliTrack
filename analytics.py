import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=12, fg_color="#1f2937")

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=15, pady=(10, 2))

        ctk.CTkLabel(
            top_bar, text="Applications by Status",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f3f4f6"
        ).pack(side="left")

        self.highlight_lbl = ctk.CTkLabel(
            top_bar, text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        )
        self.highlight_lbl.pack(side="right")

        # Matplotlib Figure embedded into CustomTkinter
        self.fig, self.ax = plt.subplots(figsize=(4.5, 2.8), dpi=100)
        self.fig.patch.set_facecolor('#1f2937')
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.08)

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(2, 10))

    def render_charts(self, df: pd.DataFrame):
        self.ax.clear()
        self.ax.set_facecolor('#1f2937')

        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            self.ax.text(0.5, 0.5, "No applications logged yet", ha='center', va='center', color='#9ca3af', fontsize=11)
            self.ax.axis('off')
            self.canvas_widget.draw()
            return

        status_counts = df["status"].value_counts()
        total_apps = len(df)
        self.highlight_lbl.configure(text=f"Total: {total_apps} active trackings")

        palette = {
            "Applied": "#38bdf8",
            "Interview": "#fbbf24",
            "Offer": "#34d399",
            "Rejected": "#f87171"
        }
        slice_colors = [palette.get(status, "#9ca3af") for status in status_counts.index]

        # Donut Chart
        wedges, texts, autotexts = self.ax.pie(
            status_counts.values,
            labels=status_counts.index,
            autopct='%1.0f%%',
            startangle=140,
            colors=slice_colors,
            wedgeprops=dict(width=0.48, edgecolor='#1f2937', linewidth=2),
            textprops=dict(color="#d1d5db", fontsize=8.5, weight="bold"),
            pctdistance=0.74
        )

        for at in autotexts:
            at.set_color("#ffffff")
            at.set_weight("bold")
            at.set_fontsize(8)

        # Center Text with Total Count
        self.ax.text(
            0, 0, f"{total_apps}\nTotal",
            ha='center', va='center',
            color='#f3f4f6', fontsize=12, weight='bold'
        )
        self.ax.set_aspect('equal')
        self.canvas_widget.draw()