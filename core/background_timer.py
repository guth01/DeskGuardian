import time
from datetime import datetime, timedelta
from config.constants import (
    BURNOUT_EVALUATION_INTERVAL_MINUTES,
    BREAK_THRESHOLD_SECONDS,
    CONTINUOUS_SCREEN_TIME_LIMIT_MINUTES
)


class BackgroundTimer:
    """
    Handles:
    - Burnout check interval
    - Screen-time accumulation
    - Idle & break timing
    """

    def __init__(self):
        self.monitoring_start_time = None
        self.last_burnout_check = None
        self.last_face_detected_time = None
        self.idle_start_time = None

        self.total_screen_time_seconds = 0
        self.total_break_time_seconds = 0

    # ======================================
    # MONITORING START
    # ======================================

    def start_monitoring(self):
        self.monitoring_start_time = datetime.now()
        self.last_burnout_check = datetime.now()
        self.last_face_detected_time = datetime.now()

    # ======================================
    # UPDATE SCREEN TIME
    # ======================================

    def update_screen_time(self):
        self.total_screen_time_seconds += 1

    def get_screen_time_minutes(self):
        return self.total_screen_time_seconds / 60

    # ======================================
    # FACE DETECTION UPDATE
    # ======================================

    def update_face_detected(self):
        self.last_face_detected_time = datetime.now()
        self.idle_start_time = None

    # ======================================
    # CHECK IDLE
    # ======================================

    def is_idle_detected(self):
        if self.last_face_detected_time is None:
            return False

        elapsed = (datetime.now() - self.last_face_detected_time).total_seconds()
        return elapsed > BREAK_THRESHOLD_SECONDS

    # ======================================
    # START BREAK
    # ======================================

    def start_break(self):
        self.idle_start_time = datetime.now()

    def end_break(self):
        if self.idle_start_time:
            duration = (datetime.now() - self.idle_start_time).total_seconds()
            self.total_break_time_seconds += duration
            self.idle_start_time = None
            return duration / 60
        return 0

    # ======================================
    # BURNOUT CHECK INTERVAL
    # ======================================

    def is_time_for_burnout_check(self):
        if self.last_burnout_check is None:
            return False

        now = datetime.now()
        elapsed_minutes = (now - self.last_burnout_check).total_seconds() / 60

        if elapsed_minutes >= BURNOUT_EVALUATION_INTERVAL_MINUTES:
            self.last_burnout_check = now
            return True
        return False

    # ======================================
    # SCREEN TIME ALERT CHECK
    # ======================================

    def is_screen_time_exceeded(self):
        return self.get_screen_time_minutes() >= CONTINUOUS_SCREEN_TIME_LIMIT_MINUTES
