import cv2
from datetime import datetime

from core.state_manager import StateManager
from core.background_timer import BackgroundTimer
from modules.posture_detection.pose_detector import PoseDetector
from modules.behavior_tracking.session_manager import SessionManager
from modules.burnout_prediction.burnout_model import BurnoutModel
from modules.notification.notification_engine import NotificationEngine
from utils.enums import SystemState
from utils.logger import Logger
from config.settings import (
    ENABLE_POSTURE_ALERTS,
    ENABLE_SCREEN_TIME_ALERTS,
    ENABLE_BURNOUT_ALERTS
)


class SystemController:
    """
    Central orchestrator of DeskGuardian.
    Integrates all modules and manages runtime flow.
    """

    def __init__(self, user_id):
        self.user_id = user_id

        self.state_manager = StateManager()
        self.timer = BackgroundTimer()
        self.pose_detector = PoseDetector()
        self.session_manager = SessionManager(user_id)
        self.burnout_model = BurnoutModel()
        self.notifier = NotificationEngine(user_id)

    # ======================================
    # START SYSTEM
    # ======================================

    def start(self):
        try:
            Logger.info("System Initializing...")
            self.state_manager.transition(SystemState.INITIALIZING)

            if not self.pose_detector.is_camera_available():
                self.state_manager.transition(SystemState.WEBCAM_ERROR)
                Logger.error("Webcam not available.")
                return

            self.session_manager.start_session()
            self.timer.start_monitoring()

            self.state_manager.transition(SystemState.MONITORING)
            Logger.info("Monitoring Started.")

            self._monitor_loop()

        except Exception as e:
            Logger.error(f"System Error: {e}")

        finally:
            self.shutdown()

    # ======================================
    # MAIN MONITORING LOOP
    # ======================================

    def _monitor_loop(self):

        while self.state_manager.get_state() == SystemState.MONITORING:

            frame, posture_class, alert_triggered = \
                self.pose_detector.process_frame()

            if frame is None:
                Logger.warning("Frame capture failed.")
                break

            face_detected = posture_class is not None

            # Update behavior/session
            break_event = self.session_manager.update(
                posture_class,
                alert_triggered,
                face_detected
            )

            # POSTURE ALERT
            if alert_triggered and ENABLE_POSTURE_ALERTS:
                Logger.info("Posture alert triggered.")
                self.notifier.send_posture_alert(
                    self.session_manager.session_id
                )

            # SCREEN TIME ALERT
            if self.timer.is_screen_time_exceeded() and ENABLE_SCREEN_TIME_ALERTS:
                Logger.info("Screen time alert triggered.")
                self.notifier.send_screen_time_alert(
                    self.session_manager.session_id
                )

            # BURNOUT CHECK (Time-driven)
            if self.timer.is_time_for_burnout_check():

                self.state_manager.transition(SystemState.BURNOUT_CHECK)
                Logger.info("Running burnout evaluation...")

                probability = self.burnout_model.predict_burnout(
                    total_screen_time_minutes=
                        self.session_manager.screen_tracker.get_total_screen_time_minutes(),
                    bad_posture_count=
                        self.session_manager.screen_tracker.get_bad_posture_count(),
                    total_breaks=0,
                    session_duration_minutes=
                        self.session_manager.screen_tracker.get_session_duration_minutes()
                )

                Logger.info(f"Burnout Probability: {probability:.3f}")

                if probability > 0.7:
                    self.state_manager.transition(SystemState.HIGH_RISK)
                    if ENABLE_BURNOUT_ALERTS:
                        Logger.warning("High burnout risk detected.")
                        self.notifier.send_burnout_alert(
                            self.session_manager.session_id,
                            None
                        )
                else:
                    self.state_manager.transition(SystemState.LOW_RISK)

                self.state_manager.transition(SystemState.MONITORING)

            cv2.imshow("DeskGuardian - Monitoring", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                Logger.info("User requested shutdown.")
                self.state_manager.transition(SystemState.STOPPED)
                break

        self.session_manager.end_session()

    # ======================================
    # SHUTDOWN
    # ======================================

    def shutdown(self):
        self.pose_detector.release()
        Logger.info("System Shutdown Complete.")
