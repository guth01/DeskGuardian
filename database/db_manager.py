import sqlite3
import os
from datetime import datetime
from config.constants import DATABASE_NAME


class DBManager:
    """
    DeskGuardian Database Manager
    --------------------------------
    Handles:
    - Database initialization
    - CRUD operations
    - Safe transactions
    """

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()
        self._initialize_database()

    # ======================================
    # DATABASE INITIALIZATION
    # ======================================

    def _initialize_database(self):
        # the schema file contains emoji and other Unicode characters, so
        # open it explicitly with utf-8 encoding to avoid "charmap" codec
        # errors on Windows.
        with open("database/schema.sql", "r", encoding="utf-8") as f:
            schema = f.read()
        self.cursor.executescript(schema)
        self.conn.commit()

    # utility to convert Python values to something SQLite accepts.
    def _to_sql(self, value):
        if isinstance(value, datetime):
            # store datetimes as ISO strings (space between date/time matches
            # sqlite's default format)
            return value.isoformat(sep=" ")
        return value

    # ======================================
    # USER OPERATIONS
    # ======================================

    def create_user(self, name, password_hash, age, occupation="", preferences_json="{}"):
        self.cursor.execute("""
            INSERT INTO User (name, password_hash, age, occupation, preferences_json)
            VALUES (?, ?, ?, ?, ?)
        """, (name, password_hash, age, occupation, preferences_json))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_user_by_name(self, name):
        """Return the full user row for the given username, or None."""
        self.cursor.execute(
            "SELECT user_id, name, password_hash, age, occupation FROM User WHERE name = ?",
            (name,),
        )
        return self.cursor.fetchone()

    # ======================================
    # SESSION OPERATIONS
    # ======================================

    def start_session(self, user_id):
        start_time = datetime.now()
        self.cursor.execute("""
            INSERT INTO Session (user_id, start_time)
            VALUES (?, ?)
        """, (user_id, self._to_sql(start_time)))
        self.conn.commit()
        return self.cursor.lastrowid

    def end_session(self, session_id):
        end_time = datetime.now()
        self.cursor.execute("""
            UPDATE Session
            SET end_time = ?
            WHERE session_id = ?
        """, (self._to_sql(end_time), session_id))
        self.conn.commit()

    def update_session_metrics(self, session_id, total_screen_time_minutes, bad_posture_count):
        """Persist accumulated screen time and posture counts to the Session row."""
        self.cursor.execute("""
            UPDATE Session
            SET total_screen_time_minutes = ?,
                bad_posture_count = ?
            WHERE session_id = ?
        """, (total_screen_time_minutes, bad_posture_count, session_id))
        self.conn.commit()

    # ======================================
    # POSTURE EVENT
    # ======================================

    def log_posture_event(self, session_id, posture_class,
                          back_angle, neck_angle,
                          shoulder_alignment,
                          is_alert_triggered=False):

        timestamp = datetime.now()

        # normalize enum values to their string representation
        if hasattr(posture_class, "value"):
            posture_class = posture_class.value

        self.cursor.execute("""
            INSERT INTO PostureEvent
            (session_id, timestamp, posture_class,
             back_angle, neck_angle, shoulder_alignment,
             is_alert_triggered)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            self._to_sql(timestamp),
            posture_class,
            back_angle,
            neck_angle,
            shoulder_alignment,
            int(is_alert_triggered)
        ))
        self.conn.commit()

    # ======================================
    # BREAK EVENT
    # ======================================

    def log_break(self, session_id, start_time, end_time,
                  duration_minutes, break_type="Short Break"):

        self.cursor.execute("""
            INSERT INTO BreakEvent
            (session_id, start_time, end_time,
             duration_minutes, break_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            self._to_sql(start_time),
            self._to_sql(end_time),
            duration_minutes,
            break_type
        ))
        self.conn.commit()

    # ======================================
    # BURNOUT ASSESSMENT
    # ======================================

    def log_burnout_assessment(self, user_id,
                               interval_start,
                               interval_end,
                               burnout_probability,
                               avg_screen_time_per_day,
                               avg_bad_posture_per_hour,
                               avg_breaks_per_hour):

        self.cursor.execute("""
            INSERT INTO BurnoutAssessment
            (user_id, interval_start, interval_end,
             burnout_probability,
             avg_screen_time_per_day,
             avg_bad_posture_per_hour,
             avg_breaks_per_hour)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            self._to_sql(interval_start),
            self._to_sql(interval_end),
            burnout_probability,
            avg_screen_time_per_day,
            avg_bad_posture_per_hour,
            avg_breaks_per_hour
        ))
        self.conn.commit()

        return self.cursor.lastrowid

    # ======================================
    # ALERTS
    # ======================================

    def log_alert(self, user_id, session_id,
                  assessment_id, alert_type, message):

        alert_time = datetime.now()

        self.cursor.execute("""
            INSERT INTO Alert
            (user_id, session_id, assessment_id,
             alert_time, alert_type, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            session_id,
            assessment_id,
            self._to_sql(alert_time),
            alert_type,
            message
        ))
        self.conn.commit()

    # ======================================
    # FETCH METHODS (Dashboard Use)
    # ======================================

    def fetch_user_sessions(self, user_id):
        self.cursor.execute("""
            SELECT * FROM Session
            WHERE user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def fetch_posture_events(self, session_id):
        self.cursor.execute("""
            SELECT * FROM PostureEvent
            WHERE session_id = ?
        """, (session_id,))
        return self.cursor.fetchall()

    def fetch_burnout_history(self, user_id):
        self.cursor.execute("""
            SELECT * FROM BurnoutAssessment
            WHERE user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    # ======================================
    # CLOSE CONNECTION
    # ======================================

    def close(self):
        self.conn.close()
