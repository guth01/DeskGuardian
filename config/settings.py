"""
Global configuration settings for DeskGuardian.

This module contains application-wide defaults and feature toggles. It is
imported by most components but contains no operational logic; its purpose is
to centralize values that may need to be adjusted without modifying business
code.
"""

# ---------------------------------------------------------------------------
# 🧑‍💼 Default User Profile (used on first run)
# ---------------------------------------------------------------------------
DEFAULT_USER_NAME = "DefaultUser"
DEFAULT_USER_AGE = 25
DEFAULT_USER_OCCUPATION = "Unknown"

# ---------------------------------------------------------------------------
# 📝 Logging configuration
# ---------------------------------------------------------------------------
# Enable or disable all logging output. When disabled the Logger class becomes a
# no‑op. Changing this at runtime has no effect after the logger has been
# initialized.
ENABLE_LOGGING = True

# Standard Python log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# ---------------------------------------------------------------------------
# 🔔 Alert toggles
# ---------------------------------------------------------------------------
# These flags allow individual alert categories to be suppressed for testing or
# demonstration purposes without changing the underlying notification logic.
ENABLE_POSTURE_ALERTS = True
ENABLE_SCREEN_TIME_ALERTS = True
ENABLE_BURNOUT_ALERTS = True
