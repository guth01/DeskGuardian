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
            return None, None, None, None, None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)

        posture_class = None
        alert_triggered = False

        back_angle = None
        neck_angle = None

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Always draw landmarks so the user gets visual feedback
            self.mp_draw.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )

            # Extract key landmarks — both sides for robust front-view measurement
            left_shoulder = self._get_point(landmarks, self.mp_pose.PoseLandmark.LEFT_SHOULDER)
            right_shoulder = self._get_point(landmarks, self.mp_pose.PoseLandmark.RIGHT_SHOULDER)
            left_hip = self._get_point(landmarks, self.mp_pose.PoseLandmark.LEFT_HIP)
            right_hip = self._get_point(landmarks, self.mp_pose.PoseLandmark.RIGHT_HIP)
            left_ear = self._get_point(landmarks, self.mp_pose.PoseLandmark.LEFT_EAR)
            right_ear = self._get_point(landmarks, self.mp_pose.PoseLandmark.RIGHT_EAR)
            nose = self._get_point(landmarks, self.mp_pose.PoseLandmark.NOSE)

            # Check visibility of essential landmarks (shoulders + ear)
            # Hip visibility is checked separately since it's often low in
            # close-up / front-facing webcam views.
            core_vis = min(
                self._get_visibility(landmarks, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
                self._get_visibility(landmarks, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
                self._get_visibility(landmarks, self.mp_pose.PoseLandmark.LEFT_EAR),
            )
            hip_vis = min(
                self._get_visibility(landmarks, self.mp_pose.PoseLandmark.LEFT_HIP),
                self._get_visibility(landmarks, self.mp_pose.PoseLandmark.RIGHT_HIP),
            )

            # Need at least shoulders + ear to compute neck angle
            if core_vis < 0.5:
                return frame, None, False, None, None

            # Use midpoints for symmetric, stable measurements
            mid_shoulder = self._midpoint(left_shoulder, right_shoulder)
            mid_ear = self._midpoint(left_ear, right_ear)

            # Neck angle (shoulder→ear) is always available
            neck_angle = self.metrics.compute_neck_angle(mid_shoulder, mid_ear)

            # Back angle (hip→shoulder) only when hips are visible;
            # otherwise fall back to 0 (assume upright torso)
            if hip_vis >= 0.3:
                mid_hip = self._midpoint(left_hip, right_hip)
                back_angle = self.metrics.compute_back_angle(mid_hip, mid_shoulder)
            else:
                back_angle = 0.0

            shoulder_alignment = self.metrics.compute_shoulder_alignment(
                left_shoulder, right_shoulder
            )

            # Classify posture
            posture_class, alert_triggered = self.classifier.classify(
                back_angle, neck_angle
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

        return frame, posture_class, alert_triggered, back_angle, neck_angle

    # ======================================
    # UTILITY
    # ======================================

    def _get_point(self, landmarks, landmark_enum):
        lm = landmarks[landmark_enum]
        return (lm.x, lm.y)

    def _get_visibility(self, landmarks, landmark_enum):
        """Return the visibility confidence (0-1) for a landmark."""
        return landmarks[landmark_enum].visibility

    @staticmethod
    def _midpoint(p1, p2):
        """Return the midpoint of two (x, y) coordinate tuples."""
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    # ======================================
    # RELEASE CAMERA
    # ======================================

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
