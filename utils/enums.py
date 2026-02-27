from enum import Enum


# ==========================================
# 🧍 POSTURE CLASS ENUM
# ==========================================

class PostureClass(Enum):
    GOOD = "Good"
    SLIGHTLY_BAD = "Slightly Bad"
    BAD = "Bad"
    VERY_BAD = "Very Bad"


# ==========================================
# 🔔 ALERT TYPE ENUM
# ==========================================

class AlertType(Enum):
    POSTURE_ALERT = "POSTURE_ALERT"
    SCREEN_TIME_ALERT = "SCREEN_TIME_ALERT"
    BREAK_REMINDER = "BREAK_REMINDER"
    BURNOUT_HIGH_RISK = "BURNOUT_HIGH_RISK"


# ==========================================
# 🧠 SYSTEM STATE ENUM
# ==========================================

class SystemState(Enum):
    IDLE = "IDLE"
    INITIALIZING = "INITIALIZING"
    MONITORING = "MONITORING"
    WEBCAM_ERROR = "WEBCAM_ERROR"
    GOOD_POSTURE = "GOOD_POSTURE"
    BAD_POSTURE = "BAD_POSTURE"
    IDLE_DETECTED = "IDLE_DETECTED"
    BREAK_DETECTED = "BREAK_DETECTED"
    BURNOUT_CHECK = "BURNOUT_CHECK"
    LOW_RISK = "LOW_RISK"
    HIGH_RISK = "HIGH_RISK"
    STOPPED = "STOPPED"
