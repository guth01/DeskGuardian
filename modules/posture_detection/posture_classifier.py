import time
from utils.enums import PostureClass
from config.constants import (
    GOOD_POSTURE_MAX_BACK_ANGLE,
    GOOD_POSTURE_MAX_NECK_ANGLE,
    SLIGHT_BAD_POSTURE_MAX_BACK_ANGLE,
    SLIGHT_BAD_POSTURE_MAX_NECK_ANGLE,
    BAD_POSTURE_MAX_BACK_ANGLE,
    BAD_POSTURE_MAX_NECK_ANGLE,
    POSTURE_ALERT_THRESHOLD_SECONDS
)


class PostureClassifier:
    """
    Classifies posture based on computed angles
    and determines if alert should be triggered.
    """

    def __init__(self):
        self.bad_posture_start_time = None

    # ======================================
    # CLASSIFY POSTURE
    # ======================================

    def classify(self, back_angle, neck_angle):
        """
        Convert raw landmark angles into a posture category.

        The pose detection routines supply *raw* angles computed at the
        shoulder/ear landmarks.  When the body is perfectly vertical these
        values are close to 180 degrees, which means a naive comparison with the
        small thresholds defined in ``config.constants`` would incorrectly label
        everything as "Very Bad".  To make the thresholds meaningful we first
        translate each measurement into a *deviation* from vertical.

        Args:
            back_angle: angle (degrees) returned by
                ``PostureMetrics.compute_back_angle``
            neck_angle: angle (degrees) returned by
                ``PostureMetrics.compute_neck_angle``

        Returns:
            posture_class (PostureClass), alert_triggered (bool)
        """

        # the posture metrics now return the *deviations* from vertical for
        # both the back and the neck; lower numbers are better.  We just pass
        # them through directly.
        back_dev = back_angle
        neck_dev = neck_angle

        posture_class = self._determine_posture_class(back_dev, neck_dev)

        alert_triggered = False

        if posture_class in (PostureClass.BAD, PostureClass.VERY_BAD):
            if self.bad_posture_start_time is None:
                self.bad_posture_start_time = time.time()

            elapsed = time.time() - self.bad_posture_start_time

            if elapsed >= POSTURE_ALERT_THRESHOLD_SECONDS:
                alert_triggered = True
        else:
            # Reset timer if posture corrected
            self.bad_posture_start_time = None

        return posture_class, alert_triggered

    # ======================================
    # INTERNAL CLASS LOGIC
    # ======================================

    def _determine_posture_class(self, back_angle, neck_angle):

        # Good posture
        if (back_angle <= GOOD_POSTURE_MAX_BACK_ANGLE and
                neck_angle <= GOOD_POSTURE_MAX_NECK_ANGLE):
            return PostureClass.GOOD

        # Slightly bad
        if (back_angle <= SLIGHT_BAD_POSTURE_MAX_BACK_ANGLE and
                neck_angle <= SLIGHT_BAD_POSTURE_MAX_NECK_ANGLE):
            return PostureClass.SLIGHTLY_BAD

        # Bad
        if (back_angle <= BAD_POSTURE_MAX_BACK_ANGLE and
                neck_angle <= BAD_POSTURE_MAX_NECK_ANGLE):
            return PostureClass.BAD

        # Very bad
        return PostureClass.VERY_BAD
