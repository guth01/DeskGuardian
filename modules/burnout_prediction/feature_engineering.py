import numpy as np


class FeatureEngineering:
    """
    Converts behavioral statistics into
    ML-ready feature vectors.
    """

    @staticmethod
    def build_feature_vector(
        total_screen_time_minutes,
        bad_posture_count,
        total_breaks,
        session_duration_minutes
    ):
        """
        Returns numpy array:
        [
            avg_screen_time_per_hour,
            avg_bad_posture_per_hour,
            avg_breaks_per_hour
        ]
        """

        if session_duration_minutes == 0:
            session_duration_minutes = 1  # prevent division by zero

        hours = session_duration_minutes / 60

        avg_screen_time_per_hour = total_screen_time_minutes / hours
        avg_bad_posture_per_hour = bad_posture_count / hours
        avg_breaks_per_hour = total_breaks / hours

        return np.array([[
            avg_screen_time_per_hour,
            avg_bad_posture_per_hour,
            avg_breaks_per_hour
        ]])
