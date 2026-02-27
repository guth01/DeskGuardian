from datetime import datetime


# ======================================
# SAFE DIVISION
# ======================================

def safe_divide(numerator, denominator):
    """
    Prevent division by zero.
    """
    if denominator == 0:
        return 0
    return numerator / denominator


# ======================================
# FORMAT DATETIME
# ======================================

def format_datetime(dt: datetime):
    """
    Formats datetime for UI display.
    """
    if not dt:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ======================================
# CLASSIFY BURNOUT RISK
# ======================================

def classify_burnout_risk(probability):
    """
    Converts probability to human-readable risk level.
    """

    if probability < 0.4:
        return "Low Risk"
    elif probability < 0.7:
        return "Moderate Risk"
    else:
        return "High Risk"


# ======================================
# PERCENT FORMAT
# ======================================

def format_percentage(value):
    """
    Converts 0–1 probability to percentage string.
    """
    return f"{value * 100:.2f}%"
