import customtkinter as ctk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=12, fg_color="#1e293b", border_width=1, border_color="#334155")

        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=15, pady=(10, 2))

        ctk.CTkLabel(
            top_bar, text="📊 Analytics & Status Distribution",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f8fafc"
        ).pack(side="left")

        self.highlight_lbl = ctk.CTkLabel(
            top_bar, text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        )
        self.highlight_lbl.pack(side="right")

        # Two-chart Canvas: Left (Donut) & Right (Funnel Bar)
        self.fig, (self.ax_donut, self.ax_bar) = plt.subplots(1, 2, figsize=(8.0, 2.7), dpi=100)
        self.fig.patch.set_facecolor('#1e293b')
        self.fig.subplots_adjust(left=0.06, right=0.96, top=0.88, bottom=0.15, wspace=0.35)

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(2, 8))

    def render_charts(self, df: pd.DataFrame):
        self.ax_donut.clear()
        self.ax_bar.clear()
        self.ax_donut.set_facecolor('#1e293b')
        self.ax_bar.set_facecolor('#1e293b')

        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            self.ax_donut.text(0.5, 0.5, "No data available", ha='center', va='center', color='#94a3b8', fontsize=10)
            self.ax_bar.text(0.5, 0.5, "Charts will activate on data", ha='center', va='center', color='#64748b', fontsize=10)
            self.ax_donut.axis('off')
            self.ax_bar.axis('off')
            self.canvas_widget.draw()
            return

        palette = {
            "Applied": "#38bdf8",
            "Interview": "#fbbf24",
            "Offer": "#34d399",
            "Rejected": "#f87171"
        }

        total_apps = len(df)
        status_counts = df["status"].value_counts()
        self.highlight_lbl.configure(text=f"Total: {total_apps} Active Records")

        # 1. Left Chart: Donut
        slice_colors = [palette.get(status, "#94a3b8") for status in status_counts.index]
        wedges, texts, autotexts = self.ax_donut.pie(
            status_counts.values,
            labels=status_counts.index,
            autopct='%1.0f%%',
            startangle=140,
            colors=slice_colors,
            wedgeprops=dict(width=0.45, edgecolor='#1e293b', linewidth=2),
            textprops=dict(color="#cbd5e1", fontsize=8, weight="bold"),
            pctdistance=0.75
        )

        for at in autotexts:
            at.set_color("#ffffff")
            at.set_weight("bold")
            at.set_fontsize(7.5)

        self.ax_donut.text(0, 0, f"{total_apps}\nJobs", ha='center', va='center', color='#f8fafc', fontsize=11, weight='bold')
        self.ax_donut.set_title("Share by Status", color="#94a3b8", fontsize=10, weight="bold", pad=4)
        self.ax_donut.set_aspect('equal')

        # 2. Right Chart: Horizontal Bar Funnel
        all_statuses = ["Applied", "Interview", "Offer", "Rejected"]
        bar_vals = [int(status_counts.get(s, 0)) for s in all_statuses]
        bar_colors = [palette[s] for s in all_statuses]

        y_positions = list(range(len(all_statuses)))
        bars = self.ax_bar.barh(y_positions, bar_vals, color=bar_colors, height=0.52)

        self.ax_bar.set_yticks(y_positions)
        self.ax_bar.set_yticklabels(all_statuses, color="#cbd5e1", fontsize=8.5, weight="bold")
        self.ax_bar.set_title("Hiring Funnel Count", color="#94a3b8", fontsize=10, weight="bold", pad=4)
        self.ax_bar.tick_params(colors="#64748b", labelsize=8)

        max_val = max(bar_vals) if bar_vals and max(bar_vals) > 0 else 1
        self.ax_bar.set_xlim(0, max_val * 1.35)

        self.ax_bar.spines['top'].set_visible(False)
        self.ax_bar.spines['right'].set_visible(False)
        self.ax_bar.spines['left'].set_color('#334155')
        self.ax_bar.spines['bottom'].set_color('#334155')
        self.ax_bar.grid(axis="x", color="#334155", linestyle="--", alpha=0.4)

        for bar, val in zip(bars, bar_vals):
            w = bar.get_width()
            self.ax_bar.text(
                w + (max_val * 0.04),
                bar.get_y() + bar.get_height() / 2,
                str(val),
                ha='left', va='center', color='#f8fafc', fontsize=8.5, weight="bold"
            )

        self.canvas_widget.draw()