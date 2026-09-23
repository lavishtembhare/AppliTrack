import os
import ctypes
import customtkinter as ctk
from tkinter import messagebox

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

class JobTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AppliTrack — Career OS & Executive Pipeline Engine")
        self.geometry("1240x800")
        self.minsize(1080, 720)

        # Icon Setup
        icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # Void Obsidian Root
        self.configure(fg_color="#08090e")
        self.db = DatabaseManager()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Left Titanium Navigation Sidebar
        self.sidebar = SidebarView(self, on_navigate=self.show_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Main Content Host Area
        self.main_container = ctk.CTkFrame(self, fg_color="#0c0d15", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # VIEW 1: DASHBOARD
        self.dashboard_view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.dashboard_view.grid_columnconfigure(0, weight=1)
        self.dashboard_view.grid_rowconfigure(2, weight=1)

        dash_padding = ctk.CTkFrame(self.dashboard_view, fg_color="transparent")
        dash_padding.pack(fill="both", expand=True, padx=20, pady=20)
        dash_padding.grid_columnconfigure(0, weight=1)
        dash_padding.grid_rowconfigure(2, weight=1)

        self.metrics_view = MetricCardsView(dash_padding)
        self.metrics_view.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.analytics_view = AnalyticsView(dash_padding)
        self.analytics_view.grid(row=1, column=0, sticky="nsew", pady=(0, 12))

        self.history_view = ApplicationHistoryView(
            dash_padding,
            on_delete_callback=self.delete_record,
            on_status_change_callback=self.change_status,
            on_clear_all_callback=self.clear_all_records
        )
        self.history_view.grid(row=2, column=0, sticky="nsew")

        # VIEW 2: FULL SCREEN DATA ENTRY
        self.entry_view = EntryView(
            self.main_container, self.db,
            on_application_saved=lambda: self.refresh_all(highlight_new=True)
        )

        # VIEW 3: SETTINGS
        self.settings_view = SettingsView(
            self.main_container, self.db,
            on_change_callback=self.on_settings_updated
        )

        self.views = {
            "dashboard": self.dashboard_view,
            "add_entry": self.entry_view,
            "settings": self.settings_view
        }

        self.show_view("dashboard")
        self.refresh_all()

    def show_view(self, view_key):
        for k, view in self.views.items():
            if k == view_key:
                view.grid(row=0, column=0, sticky="nsew")
            else:
                view.grid_forget()

        if view_key == "add_entry":
            self.entry_view.refresh_dropdowns()

    def on_settings_updated(self):
        self.entry_view.refresh_dropdowns()
        self.refresh_all()

    def delete_record(self, app_id):
        if messagebox.askyesno("Purge Record", "Purge this application from local storage?"):
            self.db.delete_application(app_id)
            self.refresh_all(highlight_new=False)

    def change_status(self, app_id, new_status):
        self.db.update_status(app_id, new_status)
        self.refresh_all(highlight_new=False)

    def clear_all_records(self):
        self.db.clear_all()
        self.refresh_all(highlight_new=False)

    def refresh_all(self, highlight_new=False):
        df = self.db.get_all_applications()
        self.metrics_view.update_metrics(df)
        self.analytics_view.render_charts(df)
        self.history_view.render_list(df, highlight_new=highlight_new)

    def on_close(self):
        try:
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