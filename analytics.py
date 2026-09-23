import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=12, fg_color="#11131e", border_width=1, border_color="#1e2235")

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=18, pady=(12, 2))

        ctk.CTkLabel(
            top_bar, text="⚡ PIPELINE TELEMETRY & CONVERSION ANALYTICS",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#00f0ff"
        ).pack(side="left")

        self.highlight_lbl = ctk.CTkLabel(
            top_bar, text="",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#a855f7"
        )
        self.highlight_lbl.pack(side="right")

        # Two-chart canvas
        self.fig, (self.ax_donut, self.ax_bar) = plt.subplots(1, 2, figsize=(8.0, 2.7), dpi=100)
        self.fig.patch.set_facecolor('#11131e')
        self.fig.subplots_adjust(left=0.06, right=0.96, top=0.88, bottom=0.15, wspace=0.35)

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(2, 10))

    def render_charts(self, df: pd.DataFrame):
        self.ax_donut.clear()
        self.ax_bar.clear()
        self.ax_donut.set_facecolor('#11131e')
        self.ax_bar.set_facecolor('#11131e')

        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            self.ax_donut.text(0.5, 0.5, "// AWAITING APPLICATION TELEMETRY", ha='center', va='center', color='#475569', fontfamily="monospace", fontsize=9)
            self.ax_bar.text(0.5, 0.5, "// STAGE FLOW ACTIVE ON ENTRY", ha='center', va='center', color='#334155', fontfamily="monospace", fontsize=9)
            self.ax_donut.axis('off')
            self.ax_bar.axis('off')
            self.canvas_widget.draw()
            return

        palette = {
            "Applied": "#00f0ff",     # Cyber Cyan
            "Interview": "#f59e0b",   # Solar Gold
            "Offer": "#00f5a0",       # Neon Mint
            "Rejected": "#f43f5e"     # Velvet Crimson
        }

        total_apps = len(df)
        status_counts = df["status"].value_counts()
        self.highlight_lbl.configure(text=f"[ LIVE NODES: {total_apps:02d} ]")

        # 1. Left Chart: Donut
        slice_colors = [palette.get(status, "#64748b") for status in status_counts.index]
        wedges, texts, autotexts = self.ax_donut.pie(
            status_counts.values,
            labels=status_counts.index,
            autopct='%1.0f%%',
            startangle=140,
            colors=slice_colors,
            wedgeprops=dict(width=0.44, edgecolor='#11131e', linewidth=2.5),
            textprops=dict(color="#cbd5e1", fontsize=8, weight="bold", fontfamily="sans-serif"),
            pctdistance=0.75
        )

        for at in autotexts:
            at.set_color("#000000")
            at.set_weight("bold")
            at.set_fontsize(7.5)

        self.ax_donut.text(0, 0, f"{total_apps}\nTRACKS", ha='center', va='center', color='#f8fafc', fontsize=10, weight='bold', fontfamily="sans-serif")
        self.ax_donut.set_title("STATUS VOLUME SHARE", color="#64748b", fontsize=9, weight="bold", fontfamily="monospace", pad=6)
        self.ax_donut.set_aspect('equal')

        # 2. Right Chart: Horizontal Funnel Bars
        all_statuses = ["Applied", "Interview", "Offer", "Rejected"]
        bar_vals = [int(status_counts.get(s, 0)) for s in all_statuses]
        bar_colors = [palette[s] for s in all_statuses]

        y_positions = list(range(len(all_statuses)))
        bars = self.ax_bar.barh(y_positions, bar_vals, color=bar_colors, height=0.48)

        self.ax_bar.set_yticks(y_positions)
        self.ax_bar.set_yticklabels(all_statuses, color="#cbd5e1", fontsize=8.5, weight="bold", fontfamily="sans-serif")
        self.ax_bar.set_title("CONVERSION FUNNEL (COUNT)", color="#64748b", fontsize=9, weight="bold", fontfamily="monospace", pad=6)
        self.ax_bar.tick_params(colors="#475569", labelsize=8)

        max_val = max(bar_vals) if bar_vals and max(bar_vals) > 0 else 1
        self.ax_bar.set_xlim(0, max_val * 1.35)

        self.ax_bar.spines['top'].set_visible(False)
        self.ax_bar.spines['right'].set_visible(False)
        self.ax_bar.spines['left'].set_color('#1e2235')
        self.ax_bar.spines['bottom'].set_color('#1e2235')
        self.ax_bar.grid(axis="x", color="#1a1e2e", linestyle="--", alpha=0.6)

        for bar, val in zip(bars, bar_vals):
            w = bar.get_width()
            self.ax_bar.text(
                w + (max_val * 0.04),
                bar.get_y() + bar.get_height() / 2,
                str(val),
                ha='left', va='center', color='#f8fafc', fontsize=8.5, weight="bold", fontfamily="monospace"
            )

        self.canvas_widget.draw()