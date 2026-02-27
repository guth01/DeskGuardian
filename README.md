# 🧍 DeskGuardian - Posture & Burnout Detection System

A real-time AI-powered desktop application that monitors user posture, detects prolonged screen time, and predicts burnout risk using computer vision and machine learning.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Core Modules](#core-modules)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

DeskGuardian is a comprehensive workplace wellness application designed to:

1. **Monitor Posture in Real-Time** - Uses MediaPipe pose detection to track body position via webcam
2. **Track Screen Time** - Detects prolonged continuous work sessions and suggests breaks
3. **Detect Work Breaks** - Identifies when users step away from their desk
4. **Predict Burnout Risk** - Uses machine learning to assess burnout probability based on posture, screen time, and break patterns
5. **Send Smart Alerts** - Notifies users about poor posture, excessive screen time, and high burnout risk

The system logs all metrics to an SQLite database for analytics and dashboard visualization.

---

## ✨ Features

### Real-Time Posture Detection

- Continuous webcam monitoring using MediaPipe Pose
- Classifies posture into 4 categories: Good, Slightly Bad, Bad, Very Bad
- Intelligent angle calculations (back and neck deviation from vertical)
- Displays real-time posture metrics on screen

### Screen Time & Break Management

- Tracks continuous and cumulative screen time per session
- Automatically detects breaks when face is not visible for 120+ seconds
- Logs break duration and frequency to database
- Configurable screen time limits (default: 45 minutes)

### Burnout Prediction

- Machine learning model trained on posture, screen time, and break patterns
- Generates burnout probability score (0.0 - 1.0)
- Risk classification: Low Risk (<0.7) and High Risk (≥0.7)
- Periodic predictive evaluations (configurable interval)

### Comprehensive Logging

- Application-wide logging to console and file (`data/deskguardian.log`)
- All posture, break, and alert events logged to SQLite database
- Full session history with metrics and timestamps

### Customizable Alerts

- Configurable alert toggles (posture, screen time, burnout)
- Alert threshold management per alert type
- Database logging of all triggered alerts

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SystemController                          │
│         (Central orchestrator managing all modules)           │
└─────────────────────────────────────────────────────────────┘
          │              │               │              │
          ▼              ▼               ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │PoseDetect│   │SessionMgr│   │BurnoutMdl│   │Notifier  │
    │(Computer │   │(Behavior │   │(ML Model)│   │(Alerts)  │
    │ Vision)  │   │ Tracking)│   │          │   │          │
    └──────────┘   └──────────┘   └──────────┘   └──────────┘
          │              │               │              │
          └──────────────┴───────────────┴──────────────┘
                         │
                    ┌────▼────┐
                    │DBManager│
                    │(SQLite) │
                    └┬────────┘
                     │
           ┌─────────▼──────────┐
           │    Database File   │
           │(data/deskguardian) │
           └────────────────────┘
```

---

## 🛠 Tech Stack

| Component            | Technology                      |
| -------------------- | ------------------------------- |
| **Language**         | Python 3.10+                    |
| **Computer Vision**  | MediaPipe Pose (pose detection) |
| **ML Framework**     | scikit-learn (burnout model)    |
| **Database**         | SQLite3                         |
| **Image Processing** | OpenCV (cv2)                    |
| **UI Framework**     | PyQt5 (future dashboard)        |
| **Data Processing**  | NumPy, Pandas                   |
| **Visualization**    | Matplotlib                      |
| **Serialization**    | joblib (model persistence)      |

---

## 📁 Project Structure

```
DeskGuardian/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── config/
│   ├── constants.py                # System-wide thresholds and limits
│   └── settings.py                 # Configuration defaults (user, logging, alerts)
│
├── core/
│   ├── system_controller.py        # Central orchestrator (main loop)
│   ├── state_manager.py            # System state machine
│   └── background_timer.py         # Screen time and burnout check timers
│
├── database/
│   ├── db_manager.py               # SQLite operations (CRUD)
│   ├── models.py                   # Data models/schemas
│   └── schema.sql                  # Database schema definition
│
├── modules/
│   ├── behavior_tracking/
│   │   ├── session_manager.py      # Session lifecycle & integration layer
│   │   ├── screen_time_tracker.py  # Screen time metrics
│   │   └── break_detector.py       # Break event detection
│   │
│   ├── burnout_prediction/
│   │   ├── burnout_model.py        # ML model inference
│   │   └── feature_engineering.py  # Feature extraction for ML
│   │
│   ├── posture_detection/
│   │   ├── pose_detector.py        # Webcam & pose landmark extraction
│   │   ├── posture_classifier.py   # Angle-based posture classification
│   │   └── posture_metrics.py      # Angle computation (back, neck, shoulder)
│   │
│   ├── notification/
│   │   └── notification_engine.py  # Alert generation and logging
│   │
│   └── dashboard/
│       ├── dashboard_ui.py         # PyQt5 dashboard (future)
│       └── analytics_engine.py     # Data aggregation for dashboard
│
├── utils/
│   ├── enums.py                    # PostureClass, AlertType, SystemState
│   ├── helpers.py                  # Utility functions
│   └── logger.py                   # Centralized logging
│
├── data/                           # Runtime data directory
│   ├── deskguardian.db            # SQLite database
│   └── deskguardian.log           # Application log file
│
└── venv/                          # Python virtual environment
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.10 or higher**
- **Webcam** (required for pose detection)
- **20MB+ disk space** (for database and logs)
- **Windows, macOS, or Linux** (cross-platform compatible)

### Step 1: Clone Repository

```bash
git clone https://github.com/7vik2005/DeskGuardian.git
cd DeskGuardian
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Setup

```bash
# Run a quick syntax check
python -m py_compile **/*.py

# Check if database initializes correctly
python -c "from database.db_manager import DBManager; db = DBManager(); print('Database OK')"
```

### Step 5: Run Application

```bash
python main.py
```

You should see:

1. A log message: `Starting DeskGuardian Application...`
2. Webcam feed display: `DeskGuardian - Monitoring` window
3. Real-time posture classification and metrics
4. Status transitions in console

---

## ⚙️ Configuration

All configuration is centralized in `config/` directory:

### config/constants.py

Contains system-wide thresholds:

```python
# Posture angle thresholds (degrees deviation from vertical)
GOOD_POSTURE_MAX_BACK_ANGLE = 10
GOOD_POSTURE_MAX_NECK_ANGLE = 10
SLIGHT_BAD_POSTURE_MAX_BACK_ANGLE = 20
SLIGHT_BAD_POSTURE_MAX_NECK_ANGLE = 20
BAD_POSTURE_MAX_BACK_ANGLE = 35
BAD_POSTURE_MAX_NECK_ANGLE = 35

# Screen time & break thresholds
CONTINUOUS_SCREEN_TIME_LIMIT_MINUTES = 45      # Alert after 45min continuous
BREAK_THRESHOLD_SECONDS = 120                  # 2min break detection
POSTURE_ALERT_THRESHOLD_SECONDS = 5            # Alert after 5sec bad posture

# Burnout evaluation
BURNOUT_EVALUATION_INTERVAL_MINUTES = 30       # Check burnout every 30min
LOW_RISK_THRESHOLD = 0.4
HIGH_RISK_THRESHOLD = 0.7
```

### config/settings.py

Contains runtime defaults:

```python
# Default user profile (created on first run)
DEFAULT_USER_NAME = "DefaultUser"
DEFAULT_USER_AGE = 25
DEFAULT_USER_OCCUPATION = "Unknown"

# Logging
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"                            # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Alert toggles (disable to suppress specific alerts)
ENABLE_POSTURE_ALERTS = True
ENABLE_SCREEN_TIME_ALERTS = True
ENABLE_BURNOUT_ALERTS = True
```

**To customize**: Edit these files and restart the application.

---

## 📖 Usage

### Running the Application

```bash
python main.py
```

### What Happens on Startup

1. **User Check**: Creates default user or uses existing one
2. **Database Init**: Initializes SQLite database with schema
3. **Webcam Start**: Opens camera feed and begins pose detection
4. **Session Log**: Records a new session in database
5. **Monitoring**: Enters main loop, continuously:
   - Detects posture
   - Tracks screen time
   - Logs events to database
   - Sends alerts (console and database)

### On-Screen Information

```
┌────────────────────────────────────────────┐
│  DeskGuardian - Monitoring                  │
├────────────────────────────────────────────┤
│  [Webcam Feed with Pose Landmarks]         │
│                                             │
│  Posture: Good                              │
│  Back:178.5 Neck:91.2                      │
│                                             │
│  (Press 'q' to quit)                       │
└────────────────────────────────────────────┘
```

**Legend:**

- **Posture Line**: Current classification
- **Back Angle**: Spine deviation from vertical (0° = perfect)
- **Neck Angle**: Head deviation from upright (0° = perfect)

### Console Output

```
2026-02-27 19:00:00,100 | INFO | Starting DeskGuardian Application...
2026-02-27 19:00:00,150 | INFO | System Initializing...
[STATE] IDLE → INITIALIZING
[STATE] INITIALIZING → MONITORING
2026-02-27 19:00:00,200 | INFO | Monitoring Started.
2026-02-27 19:00:30,500 | INFO | Posture alert triggered.
[ALERT] POSTURE ALERT: Poor posture detected. Please sit upright.
```

### Exit Application

Press **`q`** in the monitoring window to gracefully shutdown.

---

## 🔌 Core Modules

### SystemController (`core/system_controller.py`)

**Purpose**: Central orchestrator and main event loop

**Key Methods:**

- `start()` - Initialize and begin monitoring
- `_monitor_loop()` - Main loop (processes frames, detects posture, triggers alerts)
- `shutdown()` - Graceful shutdown

**Integration**: Manages all submodules (pose detection, session tracking, notifications)

### PoseDetector (`modules/posture_detection/pose_detector.py`)

**Purpose**: Real-time pose detection and classification

**Key Methods:**

- `process_frame()` - Captures webcam frame, detects landmarks, classifies posture
- `is_camera_available()` - Checks webcam status

**Output**: `(frame, PostureClass, alert_triggered)`

### SessionManager (`modules/behavior_tracking/session_manager.py`)

**Purpose**: Tracks session lifecycle and integrates behavior metrics

**Key Methods:**

- `start_session()` - Create new session record in DB
- `update(posture_class, alert_triggered, face_detected)` - Process frame metrics
- `end_session()` - Close session and save final metrics

**Internally Uses**:

- `ScreenTimeTracker` - Measures continuous and session screen time
- `BreakDetector` - Detects break events (face not visible)

### BurnoutModel (`modules/burnout_prediction/burnout_model.py`)

**Purpose**: ML-based burnout risk assessment

**Key Methods:**

- `predict_burnout(total_screen_time_min, bad_posture_count, ...)` - Returns probability (0.0-1.0)

**Model**: Pre-trained scikit-learn classifier (loaded from `models/burnout_model.pkl`)

### NotificationEngine (`modules/notification/notification_engine.py`)

**Purpose**: Generate and log alerts

**Key Methods:**

- `send_posture_alert(session_id)` - Alert for bad posture
- `send_screen_time_alert(session_id)` - Alert for excessive screen time
- `send_burnout_alert(session_id, assessment_id)` - Alert for high burnout risk

**Output**: Console messages + Database logging

---

## 🗄 Database Schema

SQLite database with 6 core tables:

### User

Stores user profile information

```sql
CREATE TABLE User (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    occupation TEXT,
    preferences_json TEXT
);
```

### Session

Records work sessions with aggregated metrics

```sql
CREATE TABLE Session (
    session_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    start_time DATETIME,
    end_time DATETIME,
    total_screen_time_minutes INTEGER,
    total_break_time_minutes INTEGER,
    bad_posture_count INTEGER,
    FOREIGN KEY(user_id) REFERENCES User(user_id)
);
```

### PostureEvent

Logs every posture detection (high frequency)

```sql
CREATE TABLE PostureEvent (
    event_id INTEGER PRIMARY KEY,
    session_id INTEGER,
    timestamp DATETIME,
    posture_class TEXT,          -- 'Good', 'Slightly Bad', 'Bad', 'Very Bad'
    back_angle REAL,
    neck_angle REAL,
    is_alert_triggered BOOLEAN,
    FOREIGN KEY(session_id) REFERENCES Session(session_id)
);
```

### BreakEvent

Logs detected breaks (low frequency)

```sql
CREATE TABLE BreakEvent (
    break_id INTEGER PRIMARY KEY,
    session_id INTEGER,
    start_time DATETIME,
    end_time DATETIME,
    duration_minutes INTEGER,
    FOREIGN KEY(session_id) REFERENCES Session(session_id)
);
```

### BurnoutAssessment

Records burnout predictions at intervals

```sql
CREATE TABLE BurnoutAssessment (
    assessment_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    interval_start DATETIME,
    interval_end DATETIME,
    burnout_probability REAL,     -- 0.0 to 1.0
    avg_screen_time_per_day REAL,
    avg_bad_posture_per_hour REAL,
    FOREIGN KEY(user_id) REFERENCES User(user_id)
);
```

### Alert

Logs all alert events for audit trail

```sql
CREATE TABLE Alert (
    alert_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    alert_time DATETIME,
    alert_type TEXT,              -- 'POSTURE_ALERT', 'SCREEN_TIME_ALERT', etc.
    message TEXT,
    resolved BOOLEAN DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES User(user_id)
);
```

**Access Database:**

```bash
sqlite3 data/deskguardian.db
sqlite> SELECT * FROM Session;
sqlite> SELECT COUNT(*) FROM PostureEvent WHERE posture_class = 'Bad';
```

---

## 🐛 Troubleshooting

### Issue: "Webcam not available"

**Cause**: Camera not detected or already in use

**Solution:**

1. Check device manager for connected camera
2. Close other applications using the camera
3. Restart the application
4. Try USB camera if built-in doesn't work

### Issue: "Very Bad posture" constantly displayed despite sitting straight

**Cause**: Posture angle thresholds too strict or angle calculation incorrect

**Solution:**

1. Open the monitoring window and note the angle values (Back, Neck)
2. Adjust thresholds in `config/constants.py`:
   ```python
   GOOD_POSTURE_MAX_BACK_ANGLE = 15    # Increased from 10
   GOOD_POSTURE_MAX_NECK_ANGLE = 15
   ```
3. Restart application and test

### Issue: Alerts not appearing

**Cause**: Alerts may be disabled in config

**Solution:**
Check `config/settings.py`:

```python
ENABLE_POSTURE_ALERTS = True           # Ensure this is True
ENABLE_SCREEN_TIME_ALERTS = True
ENABLE_BURNOUT_ALERTS = True
```

### Issue: Database locked error

**Cause**: Multiple instances running or improper shutdown

**Solution:**

1. Close all running instances
2. Delete `data/deskguardian.db` to reset
3. Restart application

### Issue: "ImportError: cannot import name..."

**Cause**: Missing dependencies or incomplete installation

**Solution:**

```bash
pip install --upgrade -r requirements.txt
python -m py_compile **/*.py          # Check for syntax errors
```

---

## 📊 Data Analysis Examples

### View Today's Sessions

```python
from database.db_manager import DBManager
db = DBManager()

sessions = db.fetch_user_sessions(user_id=1)
for session in sessions:
    print(f"Session {session[0]}: {session[2]} to {session[3]}")
    print(f"  Screen Time: {session[4]} min | Bad Posture: {session[6]} times")
```

### Check Posture Distribution

```python
import sqlite3
conn = sqlite3.connect('data/deskguardian.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT posture_class, COUNT(*) as count
    FROM PostureEvent
    WHERE session_id = ?
    GROUP BY posture_class
""", (session_id,))

for posture, count in cursor.fetchall():
    print(f"{posture}: {count} detections")
```

### Export Session Report

```python
import pandas as pd

conn = sqlite3.connect('data/deskguardian.db')
df = pd.read_sql_query("""
    SELECT * FROM Session WHERE user_id = 1
""", conn)

df.to_csv('session_report.csv', index=False)
```

---

## 🤝 Contributing

### Code Style

- **PEP 8 compliance** for formatting
- **Type hints** where practical
- **Docstrings** for all classes and key methods
- **Comments** for non-obvious logic

### Adding Features

1. **Create a branch**: `git checkout -b feature/my-feature`
2. **Implement changes** with tests
3. **Update README** if user-facing
4. **Commit**: `git commit -m "feat: description"`
5. **Push**: `git push origin feature/my-feature`
6. **Create Pull Request**

### Reporting Bugs

Please include:

- Python version: `python --version`
- OS: Windows/macOS/Linux
- Steps to reproduce
- Error message and logs (`data/deskguardian.log`)

---

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

---

## 👥 Team

- **Satvik** - Lead Developer

---

## 📧 Support & Questions

For questions or issues, please:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs in `data/deskguardian.log`
3. Open an issue on GitHub

---

**Last Updated**: February 27, 2026
**Version**: 1.0.0
