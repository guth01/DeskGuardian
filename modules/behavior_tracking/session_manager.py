from datetime import datetime

from config.constants import BREAK_THRESHOLD_SECONDS
from database.db_manager import DBManager
from modules.behavior_tracking.break_detector import BreakDetector
from modules.behavior_tracking.screen_time_tracker import ScreenTimeTracker


class SessionManager:
    """
    Tracks a single user session by combining:

    * screen time measurements
    * break detection (via face visibility)
    * posture/event logging to the database

    The controller uses the public methods defined below and inspects the
    ``screen_tracker`` attribute for metrics.  Internally the class delegates
    timings to ``ScreenTimeTracker`` and ``BreakDetector``.
    """

    def __init__(self, user_id):
        # associated user in the database
        self.user_id = user_id

        # helper components
        self.db = DBManager()
        self.break_detector = BreakDetector()
        self.screen_tracker = ScreenTimeTracker()

        self.session_id = None
        self._latest_break_start = None

    # ======================================
    # SESSION LIFECYCLE
    # ======================================

    def start_session(self):
        """Create a new session row and reset trackers."""
        self.session_id = self.db.start_session(self.user_id)
        self.screen_tracker.start_session()

    def end_session(self):
        """Mark the session row as finished."""
        if self.session_id:
            self.db.end_session(self.session_id)

    # ======================================
    # MAIN UPDATE (called each loop)
    # ======================================

    def update(self, posture_class, alert_triggered, face_detected):
        """Process a single monitoring iteration.

        Returns any break event dictionary produced by the internal
        ``BreakDetector`` (``BREAK_STARTED`` or ``BREAK_ENDED``) so the caller
        can react (e.g. send a notification).
        """
        # maintain rolling screen time and posture metrics
        self.screen_tracker.update_screen_time()

        # increment bad posture count for classes that are not good
        if posture_class and posture_class != "Good":
            self.screen_tracker.increment_bad_posture()

        # log every posture classification to the database so the dashboard has
        # full history. ``back_angle`` etc. are intentionally left ``None``; the
        # posture detector could be extended later to supply them.
        if posture_class is not None and self.session_id is not None:
            self.db.log_posture_event(
                self.session_id,
                posture_class,
                back_angle=None,
                neck_angle=None,
                shoulder_alignment=None,
                is_alert_triggered=alert_triggered,
            )

        # feed face visibility to break detector
        break_event = self.break_detector.update_face_status(face_detected)
        if break_event and self.session_id is not None:
            if break_event["event"] == "BREAK_STARTED":
                self._latest_break_start = break_event["start_time"]
            elif break_event["event"] == "BREAK_ENDED" and self._latest_break_start:
                self.db.log_break(
                    self.session_id,
                    self._latest_break_start,
                    datetime.now(),
                    break_event["duration_minutes"],
                )
                self._latest_break_start = None

        return break_event
