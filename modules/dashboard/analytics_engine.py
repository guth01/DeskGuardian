from datetime import datetime
from utils.enums import AlertType
from database.db_manager import DBManager


class NotificationEngine:
    """
    Handles:
    - Alert display (console for now)
    - Logging alerts to database
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.db = DBManager()

    # ======================================
    # POSTURE ALERT
    # ======================================

    def send_posture_alert(self, session_id):
        message = "Poor posture detected. Please sit upright."

        print("[ALERT] POSTURE ALERT:", message)

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

    def send_screen_time_alert(self, session_id):
        message = "You have been working continuously. Consider taking a break."

        print("[ALERT] SCREEN TIME ALERT:", message)

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
        message = "Break time exceeded threshold. Please stretch and relax."

        print("[ALERT] BREAK REMINDER:", message)

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

    def send_burnout_alert(self, session_id, assessment_id):
        message = "High burnout risk detected. Immediate rest recommended."

        print("[ALERT] BURNOUT HIGH RISK:", message)

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=assessment_id,
            alert_type=AlertType.BURNOUT_HIGH_RISK.value,
            message=message
        )
