import numpy as np
import math


class PostureMetrics:
    """
    Computes posture-related angles and alignment metrics
    from pose landmark coordinates.
    """

    @staticmethod
    def calculate_angle(pointA, pointB, pointC):
        """
        Calculates angle at pointB formed by A-B-C.
        Points are (x, y) tuples.
        """

        a = np.array(pointA)
        b = np.array(pointB)
        c = np.array(pointC)

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (
            np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6
        )

        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        return np.degrees(angle)

    # ======================================
    # BACK ANGLE
    # ======================================

    @staticmethod
    def compute_back_angle(hip, shoulder, ear=None):
        """
        Compute the deviation of the spine from the vertical axis.

        The previous implementation used a three‑point angle (hip → shoulder →
        ear) which meant that any head tilt would influence the back measurement.
        In practice the position of the ear can be noisy and is irrelevant for
        assessing whether the torso is upright.  Instead we form a vector from
        shoulder to hip and compute its angle relative to the vertical direction
        (y‑axis of the image).

        The result is 0° when the hip lies directly below the shoulder and grows
        as the torso leans forward or backward.
        """
        # vector pointing from shoulder down towards hip
        v = np.array(hip) - np.array(shoulder)
        vertical = np.array([0.0, 1.0])  # y increases downward in image coords
        cosine = np.dot(v, vertical) / (
            (np.linalg.norm(v) * np.linalg.norm(vertical)) + 1e-6
        )
        angle = np.arccos(np.clip(cosine, -1.0, 1.0))
        return np.degrees(angle)

    # ======================================
    # NECK ANGLE
    # ======================================

    @staticmethod
    def compute_neck_angle(shoulder, ear, nose):
        """
        Calculate how far the head is displaced from vertical using the ear–nose
        vector.  A straight neck places the nose directly above the ear (small
        angle); a forward head increases the deviation.

        The shoulder argument is kept for API compatibility but is unused.
        """
        # vector from ear toward nose
        v = np.array(nose) - np.array(ear)
        vertical = np.array([0.0, -1.0])  # upward in image coords
        cosine = np.dot(v, vertical) / (
            (np.linalg.norm(v) * np.linalg.norm(vertical)) + 1e-6
        )
        angle = np.arccos(np.clip(cosine, -1.0, 1.0))
        return np.degrees(angle)

    # ======================================
    # SHOULDER ALIGNMENT
    # ======================================

    @staticmethod
    def compute_shoulder_alignment(left_shoulder, right_shoulder):
        """
        Returns vertical misalignment between shoulders.
        """
        return abs(left_shoulder[1] - right_shoulder[1])
