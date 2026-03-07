"""
Main monitoring window — displays the live camera feed with posture overlay
inside a PyQt5 widget and provides a button to open the Dashboard.
"""

import cv2
import time
import numpy as np
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont

from core.state_manager import StateManager
from core.background_timer import BackgroundTimer
from modules.posture_detection.pose_detector import PoseDetector
from modules.behavior_tracking.session_manager import SessionManager
from modules.burnout_prediction.burnout_model import BurnoutModel
from modules.notification.notification_engine import NotificationEngine
from utils.enums import SystemState, PostureClass
from utils.logger import Logger
from config.settings import (
    ENABLE_POSTURE_ALERTS,
    ENABLE_SCREEN_TIME_ALERTS,
    ENABLE_BURNOUT_ALERTS,
)
from config.constants import IDLE_FACE_NOT_DETECTED_SECONDS, CONTINUOUS_SCREEN_TIME_LIMIT_MINUTES


class MonitoringWindow(QMainWindow):
    """
    Real-time posture monitoring window with embedded camera feed.
    """

    closed = pyqtSignal()  # emitted when the user closes / logs out

    def __init__(self, user_id: int, username: str, tray_icon=None):
        super().__init__()
        self.user_id = user_id
        self.username = username

        # ---- Core components ----
        self.state_manager = StateManager()
        self.timer_bg = BackgroundTimer()
        self.pose_detector = PoseDetector()
        self.session_manager = SessionManager(user_id)
        self.burnout_model = BurnoutModel()
        self.notifier = NotificationEngine(user_id, tray_icon=tray_icon)

        self.last_user_detected_time = None
        self.no_user_alert_sent = False
        self._screen_time_alert_sent = False
        self._posture_alert_sent = False
        self._dashboard_window = None

        # ---- Build UI ----
        self.setWindowTitle(f"DeskGuardian — Monitoring ({username})")
        self.setMinimumSize(860, 580)
        self.setStyleSheet("background-color:#1e1e2e;")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)

        # Top bar: status + buttons
        top_bar = QHBoxLayout()

        self.status_label = QLabel("Initializing…")
        self.status_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.status_label.setStyleSheet("color:#aaa;")
        top_bar.addWidget(self.status_label)

        top_bar.addStretch()

        self.posture_label = QLabel("")
        self.posture_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.posture_label.setStyleSheet("color:#00ff88; padding:0 16px;")
        top_bar.addWidget(self.posture_label)

        dashboard_btn = QPushButton("📊 Dashboard")
        dashboard_btn.setCursor(Qt.PointingHandCursor)
        dashboard_btn.setStyleSheet(
            "QPushButton{background:#007bff;color:white;padding:8px 18px;"
            "border-radius:6px;font-size:13px;font-weight:bold;}"
            "QPushButton:hover{background:#0056b3;}"
        )
        dashboard_btn.clicked.connect(self._open_dashboard)
        top_bar.addWidget(dashboard_btn)

        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet(
            "QPushButton{background:#dc3545;color:white;padding:8px 14px;"
            "border-radius:6px;font-size:12px;font-weight:bold;}"
            "QPushButton:hover{background:#a71d2a;}"
        )
        logout_btn.clicked.connect(self._logout)
        top_bar.addWidget(logout_btn)

        root.addLayout(top_bar)

        # Camera feed
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet(
            "background:black; border-radius:8px;"
        )
        root.addWidget(self.camera_label, stretch=1)

        # Bottom metrics bar
        metrics_bar = QHBoxLayout()
        self.back_label = self._metric_widget("Back Angle", "—")
        self.neck_label = self._metric_widget("Neck Angle", "—")
        self.screen_time_label = self._metric_widget("Screen Time", "0 min")
        self.session_time_label = self._metric_widget("Session", "0 min")
        metrics_bar.addWidget(self.back_label)
        metrics_bar.addWidget(self.neck_label)
        metrics_bar.addWidget(self.screen_time_label)
        metrics_bar.addWidget(self.session_time_label)
        root.addLayout(metrics_bar)

        # ---- Start monitoring ----
        self._start_monitoring()

        # Frame timer (~15 FPS via QTimer so GUI stays responsive)
        self._frame_timer = QTimer(self)
        self._frame_timer.timeout.connect(self._process_frame)
        self._frame_timer.start(66)  # ~15 fps

    # ------------------------------------------------------------------
    # MONITORING LIFECYCLE
    # ------------------------------------------------------------------

    def _start_monitoring(self):
        self.state_manager.transition(SystemState.INITIALIZING)

        if not self.pose_detector.is_camera_available():
            self.state_manager.transition(SystemState.WEBCAM_ERROR)
            self.status_label.setText("Webcam not available!")
            self.status_label.setStyleSheet("color:red;")
            Logger.error("Webcam not available.")
            return

        self.session_manager.start_session()
        self.timer_bg.start_monitoring()
        self.last_user_detected_time = datetime.now()

        self.state_manager.transition(SystemState.MONITORING)
        self.status_label.setText("Monitoring Active")
        self.status_label.setStyleSheet("color:#00ff88;")
        Logger.info("Monitoring started.")

    # ------------------------------------------------------------------
    # PER-FRAME PROCESSING (runs on QTimer)
    # ------------------------------------------------------------------

    def _process_frame(self):
        if self.state_manager.get_state() != SystemState.MONITORING:
            return

        frame, posture_class, alert_triggered, back_angle, neck_angle = self.pose_detector.process_frame()
        if frame is None:
            return

        face_detected = posture_class is not None

        # --- no-user-detected logic ---
        if face_detected:
            self.last_user_detected_time = datetime.now()
            if self.no_user_alert_sent:
                self.no_user_alert_sent = False
                if ENABLE_POSTURE_ALERTS:
                    self.notifier.send_user_detected_notification(
                        self.session_manager.session_id
                    )
        else:
            if self.last_user_detected_time:
                elapsed = (datetime.now() - self.last_user_detected_time).total_seconds()
                if elapsed >= IDLE_FACE_NOT_DETECTED_SECONDS and not self.no_user_alert_sent:
                    self.no_user_alert_sent = True
                    if ENABLE_POSTURE_ALERTS:
                        self.notifier.send_no_user_detected_alert(
                            self.session_manager.session_id, int(elapsed)
                        )

        # --- session / behavior tracking ---
        break_event = self.session_manager.update(
            posture_class, alert_triggered, face_detected,
            back_angle=back_angle, neck_angle=neck_angle
        )

        # --- posture alert ---
        if alert_triggered and ENABLE_POSTURE_ALERTS and not self._posture_alert_sent:
            self._posture_alert_sent = True
            duration_seconds = 0
            if self.pose_detector.classifier.bad_posture_start_time:
                duration_seconds = time.time() - self.pose_detector.classifier.bad_posture_start_time
            Logger.warning(f"Bad posture alert! Duration: {duration_seconds:.0f}s")
            self.notifier.send_posture_alert(
                self.session_manager.session_id, int(duration_seconds)
            )
        elif not alert_triggered:
            # Reset so the next bad-posture stretch triggers a fresh alert
            self._posture_alert_sent = False

        # --- screen time alert ---
        st = self.session_manager.screen_tracker.get_total_screen_time_minutes()
        if st >= CONTINUOUS_SCREEN_TIME_LIMIT_MINUTES and not self._screen_time_alert_sent and ENABLE_SCREEN_TIME_ALERTS:
            self._screen_time_alert_sent = True
            Logger.warning(f"Screen time alert! {st:.1f} minutes")
            self.notifier.send_screen_time_alert(
                self.session_manager.session_id, int(st)
            )

        # --- burnout check ---
        if self.timer_bg.is_time_for_burnout_check():
            prob = self.burnout_model.predict_burnout(
                total_screen_time_minutes=self.session_manager.screen_tracker.get_total_screen_time_minutes(),
                bad_posture_count=self.session_manager.screen_tracker.get_bad_posture_count(),
                total_breaks=0,
                session_duration_minutes=self.session_manager.screen_tracker.get_session_duration_minutes(),
            )
            self.session_manager.db.log_burnout_assessment(
                user_id=self.user_id,
                interval_start=datetime.now(),
                interval_end=datetime.now(),
                burnout_probability=prob,
                avg_screen_time_per_day=self.session_manager.screen_tracker.get_total_screen_time_minutes(),
                avg_bad_posture_per_hour=self.session_manager.screen_tracker.get_bad_posture_count(),
                avg_breaks_per_hour=0,
            )
            if prob >= 0.7 and ENABLE_BURNOUT_ALERTS:
                self.notifier.send_burnout_alert(
                    self.session_manager.session_id, None, prob
                )

        # --- update UI widgets ---
        self._update_camera_feed(frame)
        self._update_metrics(posture_class, back_angle, neck_angle)

    # ------------------------------------------------------------------
    # UI UPDATES
    # ------------------------------------------------------------------

    def _update_camera_feed(self, frame):
        """Convert OpenCV BGR frame to QPixmap and display."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled = qt_img.scaled(
            self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.camera_label.setPixmap(QPixmap.fromImage(scaled))

    def _update_metrics(self, posture_class, back_angle, neck_angle):
        if posture_class:
            color = "#00ff88" if posture_class == PostureClass.GOOD else "#ff4444"
            self.posture_label.setText(f"Posture: {posture_class.value}")
            self.posture_label.setStyleSheet(f"color:{color}; padding:0 16px;")

        if back_angle is not None:
            self.back_label.findChild(QLabel, "val").setText(f"{back_angle:.1f}°")
        if neck_angle is not None:
            self.neck_label.findChild(QLabel, "val").setText(f"{neck_angle:.1f}°")

        st = self.session_manager.screen_tracker.get_total_screen_time_minutes()
        sd = self.session_manager.screen_tracker.get_session_duration_minutes()
        self.screen_time_label.findChild(QLabel, "val").setText(f"{st:.1f} min")
        self.session_time_label.findChild(QLabel, "val").setText(f"{sd:.1f} min")

    # ------------------------------------------------------------------
    # DASHBOARD
    # ------------------------------------------------------------------

    def _open_dashboard(self):
        # Import here to avoid circular import at module level
        from modules.dashboard.dashboard_ui import DashboardUI

        if self._dashboard_window is None or not self._dashboard_window.isVisible():
            self._dashboard_window = DashboardUI(self.user_id)
        self._dashboard_window.show()
        self._dashboard_window.raise_()
        self._dashboard_window.activateWindow()

    # ------------------------------------------------------------------
    # LOGOUT / CLOSE
    # ------------------------------------------------------------------

    def _logout(self):
        self._shutdown()
        self.closed.emit()
        self.close()

    def closeEvent(self, event):
        self._shutdown()
        self.closed.emit()
        super().closeEvent(event)

    def _shutdown(self):
        self._frame_timer.stop()
        self.session_manager.end_session()
        self.pose_detector.release()
        if self._dashboard_window:
            self._dashboard_window.close()
        Logger.info("Monitoring stopped.")

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _metric_widget(title_text, default_val):
        """Build a small metric box for the bottom bar."""
        frame = QFrame()
        frame.setStyleSheet(
            "background:#2a2a3d; border-radius:8px; padding:6px;"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 6, 12, 6)

        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 9))
        title.setStyleSheet("color:#888;")
        title.setAlignment(Qt.AlignCenter)

        val = QLabel(default_val)
        val.setObjectName("val")
        val.setFont(QFont("Segoe UI", 14, QFont.Bold))
        val.setStyleSheet("color:white;")
        val.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(val)
        return frame
