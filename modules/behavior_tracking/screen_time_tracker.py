from datetime import datetime


class ScreenTimeTracker:
    """
    Tracks:
    - Continuous screen time
    - Total session screen time
    - Bad posture occurrences
    """

    def __init__(self):
        self.session_start_time = None
        self.total_screen_time_seconds = 0
        self.bad_posture_count = 0
        self.last_update_time = None

    # ======================================
    # START SESSION
    # ======================================

    def start_session(self):
        self.session_start_time = datetime.now()
        self.last_update_time = datetime.now()
        self.total_screen_time_seconds = 0
        self.bad_posture_count = 0

    # ======================================
    # UPDATE SCREEN TIME (Call Every Loop)
    # ======================================

    def update_screen_time(self):
        if self.last_update_time:
            now = datetime.now()
            elapsed = (now - self.last_update_time).total_seconds()
            self.total_screen_time_seconds += elapsed
            self.last_update_time = now

    # ======================================
    # INCREMENT BAD POSTURE COUNT
    # ======================================

    def increment_bad_posture(self):
        self.bad_posture_count += 1

    # ======================================
    # GETTERS
    # ======================================

    def get_total_screen_time_minutes(self):
        return self.total_screen_time_seconds / 60

    def get_bad_posture_count(self):
        return self.bad_posture_count

    def get_session_duration_minutes(self):
        if self.session_start_time:
            elapsed = (datetime.now() - self.session_start_time).total_seconds()
            return elapsed / 60
        return 0
