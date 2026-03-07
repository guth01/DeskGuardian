from datetime import datetime
import time as _time
from utils.enums import AlertType
from database.db_manager import DBManager
from utils.logger import Logger
from modules.gui.notification_popup import show_popup


class NotificationEngine:
    """
    Handles:
    - Desktop popup notifications (custom Qt widget)
    - Logging alerts to database
    """

    def __init__(self, user_id, tray_icon=None):
        self.user_id = user_id
        self.db = DBManager()
        self._tray_icon = tray_icon          # kept for future use
        # Cooldown tracking to avoid notification spam
        self._last_notification_time = {}
        self._cooldown_seconds = 30

    # ======================================
    # SEND DESKTOP NOTIFICATION
    # ======================================

    def _show_desktop_notification(self, title, message, duration=8):
        """
        Show a popup notification in the bottom-right corner of the screen.
        Uses a cooldown per title to prevent notification spam.
        """
        now = _time.time()
        last = self._last_notification_time.get(title, 0)
        if now - last < self._cooldown_seconds:
            return  # skip - too soon since last notification of this type

        self._last_notification_time[title] = now

        try:
            show_popup(title, message, duration_ms=duration * 1000)
            Logger.info(f"Desktop notification shown: {title}")
        except Exception as e:
            Logger.warning(f"Failed to show desktop notification: {e}")

    # ======================================
    # POSTURE ALERT
    # ======================================

    def send_posture_alert(self, session_id, duration_seconds):
        """Send alert for bad posture maintained for a period of time."""
        message = f"Bad posture detected for {duration_seconds} seconds. Please sit upright."

        Logger.info(f"[ALERT] POSTURE: {message}")

        self._show_desktop_notification(
            title="Bad Posture Alert",
            message=message,
            duration=8
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type=AlertType.POSTURE_ALERT.value,
            message=message
        )

    # ======================================
    # SCREEN TIME ALERT
    # ======================================

    def send_screen_time_alert(self, session_id, screen_time_minutes):
        message = f"You have been working for {screen_time_minutes} minutes. Consider taking a break."

        Logger.info(f"[ALERT] SCREEN TIME: {message}")

        self._show_desktop_notification(
            title="Screen Time Alert",
            message=message,
            duration=8
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type=AlertType.SCREEN_TIME_ALERT.value,
            message=message
        )

    # ======================================
    # BREAK REMINDER
    # ======================================

    def send_break_reminder(self, session_id):
        message = "Time for a break! Stretch, walk, and relax your eyes."

        Logger.info(f"[ALERT] BREAK REMINDER: {message}")

        self._show_desktop_notification(
            title="Break Reminder",
            message=message,
            duration=8
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type=AlertType.BREAK_REMINDER.value,
            message=message
        )

    # ======================================
    # BURNOUT HIGH RISK ALERT
    # ======================================

    def send_burnout_alert(self, session_id, assessment_id, burnout_probability):
        message = f"High burnout risk detected (Probability: {burnout_probability:.1%}). Please take immediate rest."

        Logger.warning(f"[ALERT] BURNOUT HIGH RISK: {message}")

        self._show_desktop_notification(
            title="Burnout Risk Alert",
            message=message,
            duration=10
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=assessment_id,
            alert_type=AlertType.BURNOUT_HIGH_RISK.value,
            message=message
        )

    # ======================================
    # NO USER DETECTED ALERT
    # ======================================

    def send_no_user_detected_alert(self, session_id, idle_seconds):
        message = f"No user detected for {idle_seconds} seconds."

        Logger.warning(f"[ALERT] NO USER DETECTED: {message}")

        self._show_desktop_notification(
            title="No User Detected",
            message=message,
            duration=5
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type="NO_USER_DETECTED",
            message=message
        )

    # ======================================
    # USER RE-DETECTED NOTIFICATION
    # ======================================

    def send_user_detected_notification(self, session_id):
        message = "User detected. Resuming monitoring..."

        Logger.info(f"[INFO] USER DETECTED: {message}")

        self._show_desktop_notification(
            title="Monitoring Resumed",
            message=message,
            duration=3
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type="USER_DETECTED",
            message=message
        )

