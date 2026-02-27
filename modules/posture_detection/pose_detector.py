import cv2
import mediapipe as mp
from config.constants import FPS, FRAME_WIDTH, FRAME_HEIGHT
from modules.posture_detection.posture_metrics import PostureMetrics
from modules.posture_detection.posture_classifier import PostureClassifier
from utils.enums import PostureClass


class PoseDetector:
    """
    Handles:
    - Webcam capture
    - MediaPipe pose detection
    - Metric computation
    - Posture classification
    """

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_draw = mp.solutions.drawing_utils

        self.classifier = PostureClassifier()
        self.metrics = PostureMetrics()

    # ======================================
    # CHECK CAMERA
    # ======================================

    def is_camera_available(self):
        return self.cap.isOpened()

    # ======================================
    # PROCESS FRAME
    # ======================================

    def process_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None, None, None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)

        posture_class = None
        alert_triggered = False

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Extract key landmarks
            left_shoulder = self._get_point(landmarks, self.mp_pose.PoseLandmark.LEFT_SHOULDER)
            right_shoulder = self._get_point(landmarks, self.mp_pose.PoseLandmark.RIGHT_SHOULDER)
            left_hip = self._get_point(landmarks, self.mp_pose.PoseLandmark.LEFT_HIP)
            left_ear = self._get_point(landmarks, self.mp_pose.PoseLandmark.LEFT_EAR)
            nose = self._get_point(landmarks, self.mp_pose.PoseLandmark.NOSE)

            # Compute metrics
            back_angle = self.metrics.compute_back_angle(left_hip, left_shoulder, left_ear)
            neck_angle = self.metrics.compute_neck_angle(left_shoulder, left_ear, nose)
            shoulder_alignment = self.metrics.compute_shoulder_alignment(
                left_shoulder, right_shoulder
            )

            # Classify posture
            posture_class, alert_triggered = self.classifier.classify(
                back_angle, neck_angle
            )

            # Draw landmarks
            self.mp_draw.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )

            # Overlay posture label and raw metrics (helpful for tuning)
            cv2.putText(
                frame,
                f"Posture: {posture_class.value}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0) if posture_class == PostureClass.GOOD else (0, 0, 255),
                2
            )

            cv2.putText(
                frame,
                f"Back:{back_angle:.1f} Neck:{neck_angle:.1f}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                1
            )

        return frame, posture_class, alert_triggered

    # ======================================
    # UTILITY
    # ======================================

    def _get_point(self, landmarks, landmark_enum):
        lm = landmarks[landmark_enum]
        return (lm.x, lm.y)

    # ======================================
    # RELEASE CAMERA
    # ======================================

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
