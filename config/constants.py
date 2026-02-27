"""
DeskGuardian - Global System Constants
---------------------------------------
Central configuration file for thresholds, limits, timings, and enums.
All system modules import values from here.

Modifying values here updates system-wide behavior.
"""

# ===============================
# 🎥 WEBCAM & FRAME SETTINGS
# ===============================

FPS = 15  # Frames per second (SRS: 10–30 FPS requirement)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480


# ===============================
# 🧍 POSTURE CLASSIFICATION
# ===============================

# Angle thresholds (degrees)
GOOD_POSTURE_MAX_BACK_ANGLE = 10
GOOD_POSTURE_MAX_NECK_ANGLE = 10

SLIGHT_BAD_POSTURE_MAX_BACK_ANGLE = 20
SLIGHT_BAD_POSTURE_MAX_NECK_ANGLE = 20

BAD_POSTURE_MAX_BACK_ANGLE = 35
BAD_POSTURE_MAX_NECK_ANGLE = 35

# Posture class labels (Domain constraint - enum values)
POSTURE_CLASSES = [
    "Good",
    "Slightly Bad",
    "Bad",
    "Very Bad"
]

# Alert trigger threshold
POSTURE_ALERT_THRESHOLD_SECONDS = 5  # Continuous bad posture duration


# ===============================
# ⏳ SCREEN TIME & BREAK DETECTION
# ===============================

# Continuous screen usage alert threshold
CONTINUOUS_SCREEN_TIME_LIMIT_MINUTES = 45

# Break detection threshold (SRS FR-3: 2 minutes)
BREAK_THRESHOLD_SECONDS = 120

# Idle detection
IDLE_FACE_NOT_DETECTED_SECONDS = 10


# ===============================
# 🔥 BURNOUT PREDICTION
# ===============================

# Burnout risk classification thresholds
LOW_RISK_THRESHOLD = 0.4
HIGH_RISK_THRESHOLD = 0.7

# Burnout evaluation interval (in minutes)
BURNOUT_EVALUATION_INTERVAL_MINUTES = 30

# Domain constraint (SRS)
BURNOUT_PROBABILITY_MIN = 0.0
BURNOUT_PROBABILITY_MAX = 1.0


# ===============================
# 🔔 ALERT TYPES (Enum Constraint)
# ===============================

ALERT_TYPES = [
    "POSTURE_ALERT",
    "SCREEN_TIME_ALERT",
    "BREAK_REMINDER",
    "BURNOUT_HIGH_RISK"
]


# ===============================
# 🗄 DATABASE CONFIG
# ===============================

DATABASE_NAME = "data/deskguardian.db"


# ===============================
# 🖥 DASHBOARD CONFIG
# ===============================

DASHBOARD_REFRESH_INTERVAL_MS = 3000


# ===============================
# 🧠 SYSTEM STATES (State Diagram)
# ===============================

SYSTEM_STATES = [
    "IDLE",
    "INITIALIZING",
    "MONITORING",
    "WEBCAM_ERROR",
    "GOOD_POSTURE",
    "BAD_POSTURE",
    "IDLE_DETECTED",
    "BREAK_DETECTED",
    "BURNOUT_CHECK",
    "LOW_RISK",
    "HIGH_RISK",
    "STOPPED"
]
