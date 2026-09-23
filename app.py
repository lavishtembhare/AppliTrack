import os
import sys
import ctypes
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt

from database import DatabaseManager
from metrics import MetricCardsView
from analytics import AnalyticsView
from applications import ApplicationHistoryView
from sidebar import SidebarView
from entry_view import EntryView
from settings_view import SettingsView

# --- High-DPI Crisp Font Rendering & Windows Taskbar App ID ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

try:
    myappid = 'applitrack.careeros.desktop.2.4'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def get_asset_path(filename: str) -> str:
    """Resolves resource paths for both standard execution and PyInstaller single-file builds."""
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)


class JobTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AppliTrack — Career OS & Executive Pipeline Engine")
        self.geometry("1240x800")
        self.minsize(1080, 720)

        # 1. PyInstaller Safe Icon Loader
        icon_path = get_asset_path("app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # 2. Void Obsidian Root Canvas
        self.configure(fg_color="#08090e")
        self.db = DatabaseManager()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 3. Left Titanium Navigation Sidebar
        self.sidebar = SidebarView(self, on_navigate=self.show_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 4. Main Content Host Area
        self.main_container = ctk.CTkFrame(self, fg_color="#0c0d15", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # ----------------- VIEW 1: DASHBOARD -----------------
        self.dashboard_view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.dashboard_view.grid_columnconfigure(0, weight=1)
        self.dashboard_view.grid_rowconfigure(2, weight=1)

        dash_padding = ctk.CTkFrame(self.dashboard_view, fg_color="transparent")
        dash_padding.pack(fill="both", expand=True, padx=20, pady=20)
        dash_padding.grid_columnconfigure(0, weight=1)
        dash_padding.grid_rowconfigure(2, weight=1)

        # Top Executive Telemetry Cards
        self.metrics_view = MetricCardsView(dash_padding)
        self.metrics_view.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # Analytics Visualizer (Donut & Funnel)
        self.analytics_view = AnalyticsView(dash_padding)
        self.analytics_view.grid(row=1, column=0, sticky="nsew", pady=(0, 12))

        # Applications Repository & Status Filter
        self.history_view = ApplicationHistoryView(
            dash_padding,
            on_delete_callback=self.delete_record,
            on_status_change_callback=self.change_status,
            on_clear_all_callback=self.clear_all_records
        )
        self.history_view.grid(row=2, column=0, sticky="nsew")

        # ----------------- VIEW 2: FULL-SCREEN DATA ENTRY -----------------
        self.entry_view = EntryView(
            self.main_container, self.db,
            on_application_saved=self.handle_application_saved
        )

        # ----------------- VIEW 3: SYSTEM CONFIG & SETTINGS -----------------
        self.settings_view = SettingsView(
            self.main_container, self.db,
            on_change_callback=self.on_settings_updated
        )

        self.views = {
            "dashboard": self.dashboard_view,
            "add_entry": self.entry_view,
            "settings": self.settings_view
        }

        # 5. Global Power-User Hotkeys
        self.bind("<Control-Key-1>", lambda e: self.navigate_hotkey("dashboard"))
        self.bind("<Control-Key-2>", lambda e: self.navigate_hotkey("add_entry"))
        self.bind("<Control-Key-3>", lambda e: self.navigate_hotkey("settings"))
        self.bind("<F5>", lambda e: self.refresh_all())
        self.bind("<Control-r>", lambda e: self.refresh_all())

        # Start on dashboard
        self.show_view("dashboard")
        self.refresh_all()

    def navigate_hotkey(self, view_key: str):
        """Keyboard shortcut routing that keeps sidebar indicator in sync."""
        self.sidebar.set_active(view_key)
        self.show_view(view_key)

    def show_view(self, view_key: str):
        for k, view in self.views.items():
            if k == view_key:
                view.grid(row=0, column=0, sticky="nsew")
            else:
                view.grid_forget()

        if view_key == "add_entry":
            self.entry_view.refresh_dropdowns()
        elif view_key == "dashboard":
            self.refresh_all()

    def handle_application_saved(self):
        """Smooth pipeline hand-off: refreshes records, highlights newest, and routes back to Dashboard."""
        self.refresh_all(highlight_new=True)
        self.sidebar.set_active("dashboard")
        self.show_view("dashboard")

    def on_settings_updated(self):
        self.entry_view.refresh_dropdowns()
        self.refresh_all()

    def delete_record(self, app_id: int):
        if messagebox.askyesno("Purge Record", "Purge this opportunity from encrypted local storage?"):
            self.db.delete_application(app_id)
            self.refresh_all(highlight_new=False)

    def change_status(self, app_id: int, new_status: str):
        self.db.update_status(app_id, new_status)
        self.refresh_all(highlight_new=False)

    def clear_all_records(self):
        self.db.clear_all()
        self.refresh_all(highlight_new=False)

    def refresh_all(self, highlight_new: bool = False):
        df = self.db.get_all_applications()
        self.metrics_view.update_metrics(df)
        self.analytics_view.render_charts(df)
        self.history_view.render_list(df, highlight_new=highlight_new)

    def on_close(self):
        """Clean shutdown avoiding zombie processes or matplotlib canvas leaks."""
        try:
            plt.close('all')
            self.withdraw()
            self.quit()
            self.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        app = JobTrackerApp()
        app.mainloop()
    except (KeyboardInterrupt, SystemExit):
        pass