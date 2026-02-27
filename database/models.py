from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ==========================================
# 1️⃣ USER ENTITY
# ==========================================

@dataclass
class User:
    user_id: Optional[int]
    name: str
    age: int
    occupation: str = ""
    preferences_json: str = "{}"


# ==========================================
# 2️⃣ SESSION ENTITY
# ==========================================

@dataclass
class Session:
    session_id: Optional[int]
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    total_screen_time_minutes: int = 0
    total_break_time_minutes: int = 0
    bad_posture_count: int = 0


# ==========================================
# 3️⃣ POSTURE EVENT ENTITY
# ==========================================

@dataclass
class PostureEvent:
    event_id: Optional[int]
    session_id: int
    timestamp: datetime
    posture_class: str
    back_angle: float
    neck_angle: float
    shoulder_alignment: float
    is_alert_triggered: bool = False


# ==========================================
# 4️⃣ BREAK EVENT ENTITY
# ==========================================

@dataclass
class BreakEvent:
    break_id: Optional[int]
    session_id: int
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    break_type: str = "Short Break"


# ==========================================
# 5️⃣ BURNOUT ASSESSMENT ENTITY
# ==========================================

@dataclass
class BurnoutAssessment:
    assessment_id: Optional[int]
    user_id: int
    interval_start: datetime
    interval_end: datetime
    burnout_probability: float
    avg_screen_time_per_day: float
    avg_bad_posture_per_hour: float
    avg_breaks_per_hour: float


# ==========================================
# 6️⃣ ALERT ENTITY
# ==========================================

@dataclass
class Alert:
    alert_id: Optional[int]
    user_id: int
    alert_time: datetime
    alert_type: str
    message: str
    session_id: Optional[int] = None
    assessment_id: Optional[int] = None
    resolved: bool = False
