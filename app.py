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

try:
    myappid = 'applitrack.careeros.desktop.2.4'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def get_asset_path(filename: str) -> str:
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, filename)

class JobTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AppliTrack — Career OS & Executive Pipeline Engine")
        self.geometry("1280x820")
        self.minsize(1080, 720)

        icon_path = get_asset_path("app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.configure(fg_color="#08090e")
        self.db = DatabaseManager()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Dirty flags for lazy loading (prevents background lag)
        self.dirty_views = {"dashboard": True, "applications": True}
        self.current_view_key = "dashboard"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Navigation Sidebar
        self.sidebar = SidebarView(self, on_navigate=self.show_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Main Container Host
        self.main_container = ctk.CTkFrame(self, fg_color="#0c0d15", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # VIEW 1: DASHBOARD
        self.dashboard_view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.dashboard_view.grid_columnconfigure(0, weight=1)

        dash_padding = ctk.CTkFrame(self.dashboard_view, fg_color="transparent")
        dash_padding.pack(fill="both", expand=True, padx=25, pady=25)
        dash_padding.grid_columnconfigure(0, weight=1)

        self.metrics_view = MetricCardsView(dash_padding)
        self.metrics_view.pack(fill="x", pady=(0, 16))

        self.analytics_view = AnalyticsView(dash_padding)
        self.analytics_view.pack(fill="both", expand=True)

        # VIEW 2: APPLICATIONS REPOSITORY
        self.applications_view = ApplicationHistoryView(
            self.main_container,
            on_delete_callback=self.delete_record,
            on_status_change_callback=self.change_status,
            on_clear_all_callback=self.clear_all_records
        )

        # VIEW 3: DATA ENTRY TAB
        self.entry_view = EntryView(
            self.main_container, self.db,
            on_application_saved=self.handle_application_saved
        )

        # VIEW 4: SETTINGS TAB
        self.settings_view = SettingsView(
            self.main_container, self.db,
            on_change_callback=self.on_settings_updated
        )

        self.views = {
            "dashboard": self.dashboard_view,
            "applications": self.applications_view,
            "add_entry": self.entry_view,
            "settings": self.settings_view
        }

        # Keyboard Navigation Shortcuts
        self.bind("<Control-Key-1>", lambda e: self.navigate_hotkey("dashboard"))
        self.bind("<Control-Key-2>", lambda e: self.navigate_hotkey("applications"))
        self.bind("<Control-Key-3>", lambda e: self.navigate_hotkey("add_entry"))
        self.bind("<Control-Key-4>", lambda e: self.navigate_hotkey("settings"))
        self.bind("<F5>", lambda e: self.force_refresh_current())

        self.show_view("dashboard")

    def navigate_hotkey(self, view_key: str):
        self.sidebar.set_active(view_key)
        self.show_view(view_key)

    def show_view(self, view_key: str):
        self.current_view_key = view_key
        for k, view in self.views.items():
            if k == view_key:
                view.grid(row=0, column=0, sticky="nsew")
            else:
                view.grid_forget()

        # Lazy Render: Only render the view that is now visible
        if view_key == "dashboard" and self.dirty_views["dashboard"]:
            df = self.db.get_all_applications()
            self.metrics_view.update_metrics(df)
            self.analytics_view.render_charts(df)
            self.dirty_views["dashboard"] = False

        elif view_key == "applications" and self.dirty_views["applications"]:
            df = self.db.get_all_applications()
            self.applications_view.render_list(df)
            self.dirty_views["applications"] = False

        elif view_key == "add_entry":
            self.entry_view.refresh_dropdowns()

    def handle_application_saved(self):
        """Called when a job is logged: marks caches dirty but stays on current form."""
        self.dirty_views["dashboard"] = True
        self.dirty_views["applications"] = True
        # Stays on entry form; no redirect

    def on_settings_updated(self):
        self.dirty_views["dashboard"] = True
        self.dirty_views["applications"] = True
        self.entry_view.refresh_dropdowns()

    def delete_record(self, app_id: int):
        if messagebox.askyesno("Purge Record", "Purge this opportunity from local storage?"):
            self.db.delete_application(app_id)
            self.dirty_views["dashboard"] = True
            df = self.db.get_all_applications()
            self.applications_view.render_list(df)
            self.dirty_views["applications"] = False

    def change_status(self, app_id: int, new_status: str):
        self.db.update_status(app_id, new_status)
        self.dirty_views["dashboard"] = True
        df = self.db.get_all_applications()
        self.applications_view.render_list(df)
        self.dirty_views["applications"] = False

    def clear_all_records(self):
        self.db.clear_all()
        self.dirty_views["dashboard"] = True
        df = self.db.get_all_applications()
        self.applications_view.render_list(df)
        self.dirty_views["applications"] = False

    def force_refresh_current(self):
        df = self.db.get_all_applications()
        if self.current_view_key == "dashboard":
            self.metrics_view.update_metrics(df)
            self.analytics_view.render_charts(df)
        elif self.current_view_key == "applications":
            self.applications_view.render_list(df)

    def on_close(self):
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