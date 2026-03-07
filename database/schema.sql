-- ==========================================
-- DeskGuardian Database Schema
-- SQLite Implementation
-- ==========================================

PRAGMA foreign_keys = ON;

-- ==========================================
-- 1️⃣ USER TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    age INTEGER NOT NULL CHECK(age > 0),
    occupation TEXT,
    preferences_json TEXT
);

-- ==========================================
-- 2️⃣ SESSION TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS Session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    total_screen_time_minutes INTEGER DEFAULT 0 CHECK(total_screen_time_minutes >= 0),
    total_break_time_minutes INTEGER DEFAULT 0 CHECK(total_break_time_minutes >= 0),
    bad_posture_count INTEGER DEFAULT 0 CHECK(bad_posture_count >= 0),

    FOREIGN KEY(user_id)
        REFERENCES User(user_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_session_user
ON Session(user_id);


-- ==========================================
-- 3️⃣ POSTURE EVENT TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS PostureEvent (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    posture_class TEXT NOT NULL CHECK(
        posture_class IN ('Good','Slightly Bad','Bad','Very Bad')
    ),
    back_angle REAL,
    neck_angle REAL,
    shoulder_alignment REAL,
    is_alert_triggered BOOLEAN DEFAULT 0,

    FOREIGN KEY(session_id)
        REFERENCES Session(session_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_posture_session
ON PostureEvent(session_id);


-- ==========================================
-- 4️⃣ BREAK EVENT TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS BreakEvent (
    break_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    duration_minutes REAL NOT NULL CHECK(duration_minutes > 0),
    break_type TEXT DEFAULT 'Short Break',

    FOREIGN KEY(session_id)
        REFERENCES Session(session_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_break_session
ON BreakEvent(session_id);


-- ==========================================
-- 5️⃣ BURNOUT ASSESSMENT TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS BurnoutAssessment (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interval_start DATETIME NOT NULL,
    interval_end DATETIME NOT NULL,
    burnout_probability REAL NOT NULL CHECK(
        burnout_probability >= 0.0 AND burnout_probability <= 1.0
    ),
    avg_screen_time_per_day REAL,
    avg_bad_posture_per_hour REAL,
    avg_breaks_per_hour REAL,

    FOREIGN KEY(user_id)
        REFERENCES User(user_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_burnout_user
ON BurnoutAssessment(user_id);


-- ==========================================
-- 6️⃣ ALERT TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS Alert (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id INTEGER,
    assessment_id INTEGER,
    alert_time DATETIME NOT NULL,
    alert_type TEXT NOT NULL CHECK(
        alert_type IN (
            'POSTURE_ALERT',
            'SCREEN_TIME_ALERT',
            'BREAK_REMINDER',
            'BURNOUT_HIGH_RISK',
            'NO_USER_DETECTED',
            'USER_DETECTED'
        )
    ),
    message TEXT NOT NULL,
    resolved BOOLEAN DEFAULT 0,

    FOREIGN KEY(user_id)
        REFERENCES User(user_id)
        ON DELETE CASCADE,

    FOREIGN KEY(session_id)
        REFERENCES Session(session_id)
        ON DELETE SET NULL,

    FOREIGN KEY(assessment_id)
        REFERENCES BurnoutAssessment(assessment_id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_alert_user
ON Alert(user_id);

CREATE INDEX IF NOT EXISTS idx_alert_time
ON Alert(alert_time);
