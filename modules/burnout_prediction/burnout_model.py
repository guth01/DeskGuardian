import os
import joblib
import numpy as np
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from modules.burnout_prediction.feature_engineering import FeatureEngineering
from config.constants import (
    BURNOUT_PROBABILITY_MIN,
    BURNOUT_PROBABILITY_MAX
)


MODEL_PATH = "data/burnout_model.pkl"


class BurnoutModel:
    """
    Handles:
    - Model training
    - Model loading
    - Burnout probability prediction
    """

    def __init__(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = self._train_initial_model()
            joblib.dump(self.model, MODEL_PATH)

    # ======================================
    # TRAIN INITIAL MODEL (Synthetic Dataset)
    # ======================================

    def _train_initial_model(self):
        """
        Trains model on synthetic academic dataset.
        This keeps project fully offline.
        """

        # Synthetic feature data:
        # [avg_screen_time_per_hour, avg_bad_posture_per_hour, avg_breaks_per_hour]
        X = np.array([
            [30, 2, 3],
            [40, 5, 1],
            [50, 7, 0],
            [20, 1, 4],
            [60, 8, 0],
            [25, 2, 3],
            [55, 6, 1],
            [35, 3, 2],
            [70, 9, 0],
            [45, 5, 1]
        ])

        # 0 = Low Risk, 1 = High Risk
        y = np.array([0, 0, 1, 0, 1, 0, 1, 0, 1, 1])

        model = LogisticRegression()
        model.fit(X, y)

        return model

    # ======================================
    # PREDICT BURNOUT PROBABILITY
    # ======================================

    def predict_burnout(
        self,
        total_screen_time_minutes,
        bad_posture_count,
        total_breaks,
        session_duration_minutes
    ):
        """
        Returns burnout probability (0–1)
        """

        features = FeatureEngineering.build_feature_vector(
            total_screen_time_minutes,
            bad_posture_count,
            total_breaks,
            session_duration_minutes
        )

        probability = self.model.predict_proba(features)[0][1]

        # Enforce domain constraint
        probability = max(BURNOUT_PROBABILITY_MIN,
                          min(probability, BURNOUT_PROBABILITY_MAX))

        return probability
