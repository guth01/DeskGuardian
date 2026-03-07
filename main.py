import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from modules.gui.login_page import LoginSignupPage
from modules.gui.monitoring_window import MonitoringWindow
from utils.logger import Logger


def _build_tray_icon(app):
    """Create a QSystemTrayIcon used for native Windows toast notifications."""
    # Try to use a custom icon; fall back to the app window icon
    icon_path = os.path.join(os.path.dirname(__file__), "data", "icon.png")
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
    else:
        icon = app.style().standardIcon(app.style().SP_ComputerIcon)

    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip("DeskGuardian")
    # Minimal context menu so the tray icon stays alive
    menu = QMenu()
    quit_action = QAction("Quit", app)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()
    return tray


class DeskGuardianApp:
    """
    Application controller.
    Shows Login → on success opens Monitoring window.
    Logout returns to Login.
    """

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.tray_icon = _build_tray_icon(self.app)
        self.login_page = None
        self.monitoring_window = None

    def run(self):
        Logger.info("Starting DeskGuardian Application...")
        self._show_login()
        sys.exit(self.app.exec_())

    # ------------------------------------------------------------------

    def _show_login(self):
        self.login_page = LoginSignupPage()
        self.login_page.login_success.connect(self._on_login_success)
        self.login_page.show()

    def _on_login_success(self, user_id: int, username: str):
        Logger.info(f"Login successful — user_id={user_id}, name={username}")
        if self.login_page:
            self.login_page.close()

        self.monitoring_window = MonitoringWindow(user_id, username, tray_icon=self.tray_icon)
        self.monitoring_window.closed.connect(self._on_monitoring_closed)
        self.monitoring_window.show()

    def _on_monitoring_closed(self):
        """User logged out or closed monitoring — return to login."""
        self.monitoring_window = None
        self._show_login()


if __name__ == "__main__":
    DeskGuardianApp().run()
