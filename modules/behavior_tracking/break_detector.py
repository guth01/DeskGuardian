from datetime import datetime
from config.constants import BREAK_THRESHOLD_SECONDS


class BreakDetector:
    """
    Detects and manages break events based on
    face visibility timing.
    """

    def __init__(self):
        self.last_face_detected_time = None
        self.break_start_time = None
        self.on_break = False

    # ======================================
    # UPDATE FACE VISIBILITY
    # ======================================

    def update_face_status(self, face_detected: bool):
        now = datetime.now()

        if face_detected:
            self.last_face_detected_time = now

            # If returning from break
            if self.on_break:
                return self._end_break()

        else:
            if self.last_face_detected_time:
                elapsed = (now - self.last_face_detected_time).total_seconds()

                if elapsed >= BREAK_THRESHOLD_SECONDS and not self.on_break:
                    return self._start_break()

        return None

    # ======================================
    # START BREAK
    # ======================================

    def _start_break(self):
        self.break_start_time = datetime.now()
        self.on_break = True
        return {
            "event": "BREAK_STARTED",
            "start_time": self.break_start_time
        }

    # ======================================
    # END BREAK
    # ======================================

    def _end_break(self):
        end_time = datetime.now()
        duration_seconds = (end_time - self.break_start_time).total_seconds()

        self.on_break = False
        self.break_start_time = None

        return {
            "event": "BREAK_ENDED",
            "start_time": end_time,
            "duration_minutes": duration_seconds / 60
        }
