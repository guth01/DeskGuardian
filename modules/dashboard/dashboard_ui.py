import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton
)
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from modules.dashboard.analytics_engine import AnalyticsEngine


class DashboardUI(QWidget):
    """
    PyQt5 Dashboard Window
    Displays:
    - Session summary
    - Burnout trend graph
    """

    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.analytics = AnalyticsEngine(user_id)

        self.setWindowTitle("DeskGuardian Dashboard")
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()

        # Summary Labels
        self.summary_label = QLabel("Loading summary...")
        self.layout.addWidget(self.summary_label)

        # Burnout Graph
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Refresh Button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_dashboard)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)

        # Auto-refresh every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_dashboard)
        self.timer.start(5000)

        self.refresh_dashboard()

    # ======================================
    # REFRESH DASHBOARD
    # ======================================

    def refresh_dashboard(self):
        summary = self.analytics.get_session_summary()

        self.summary_label.setText(
            f"Total Sessions: {summary['total_sessions']}\n"
            f"Total Screen Time (min): {summary['total_screen_time_minutes']:.2f}\n"
            f"Total Bad Posture Count: {summary['total_bad_posture_count']}"
        )

        self.plot_burnout_trend()

    # ======================================
    # PLOT BURNOUT TREND
    # ======================================

    def plot_burnout_trend(self):
        trend = self.analytics.get_burnout_trend()

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if trend:
            x = list(range(len(trend)))
            y = [item["burnout_probability"] for item in trend]

            ax.plot(x, y)
            ax.set_title("Burnout Probability Trend")
            ax.set_ylabel("Probability (0–1)")
            ax.set_xlabel("Assessment Index")
        else:
            ax.text(0.5, 0.5, "No Burnout Data",
                    horizontalalignment='center',
                    verticalalignment='center')

        self.canvas.draw()


# ======================================
# STANDALONE RUN
# ======================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardUI(user_id=1)
    window.show()
    sys.exit(app.exec_())
