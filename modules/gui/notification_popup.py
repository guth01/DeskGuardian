"""
Custom desktop notification popup that appears in the bottom-right corner
of the screen. Guaranteed to work on all platforms since it's a native
Qt widget — no dependency on Windows toast APIs.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication,
    QGraphicsOpacityEffect, QPushButton, QDesktopWidget
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QColor


# Stack of currently visible popups (newest at end)
_active_popups: list = []

# Popup dimensions
POPUP_WIDTH = 380
POPUP_HEIGHT = 110
POPUP_MARGIN = 16
POPUP_SPACING = 8


class NotificationPopup(QWidget):
    """
    A frameless, always-on-top popup that slides in from the bottom-right
    corner and auto-closes after a configurable duration.
    """

    # Map of alert keywords to accent colours
    _COLOURS = {
        "posture":  ("#ff4444", "#fff0f0"),
        "screen":   ("#f59e0b", "#fffbeb"),
        "burnout":  ("#ef4444", "#fef2f2"),
        "break":    ("#10b981", "#ecfdf5"),
        "user":     ("#3b82f6", "#eff6ff"),
        "default":  ("#6366f1", "#eef2ff"),
    }

    def __init__(self, title: str, message: str, duration_ms: int = 6000):
        super().__init__()

        self._duration_ms = duration_ms

        # Frameless, always-on-top, tool window (no taskbar entry)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(POPUP_WIDTH, POPUP_HEIGHT)

        # Pick accent colour based on title keywords
        accent, bg = self._pick_colour(title)

        # --- Build UI ---
        container = QWidget(self)
        container.setObjectName("popupContainer")
        container.setFixedSize(POPUP_WIDTH, POPUP_HEIGHT)
        container.setStyleSheet(f"""
            #popupContainer {{
                background: {bg};
                border: 2px solid {accent};
                border-left: 5px solid {accent};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 12, 12)
        layout.setSpacing(4)

        # Top row: title + close button
        top_row = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet(f"color: {accent}; background: transparent;")
        top_row.addWidget(title_label)

        close_btn = QPushButton("\u2715")
        close_btn.setFixedSize(22, 22)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #999;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ color: {accent}; }}
        """)
        close_btn.clicked.connect(self._close_popup)
        top_row.addWidget(close_btn)

        layout.addLayout(top_row)

        # Message
        msg_label = QLabel(message)
        msg_label.setFont(QFont("Segoe UI", 10))
        msg_label.setStyleSheet("color: #333; background: transparent;")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)

        # Opacity effect for fade-out
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity)

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def popup(self):
        """Show this popup and schedule auto-close."""
        _active_popups.append(self)
        self._reposition_all()
        self.show()

        # Auto-close timer
        QTimer.singleShot(self._duration_ms, self._close_popup)

    # ------------------------------------------------------------------
    # PRIVATE
    # ------------------------------------------------------------------

    def _close_popup(self):
        """Fade out and remove from stack."""
        if self in _active_popups:
            _active_popups.remove(self)

        # Fade-out animation
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(300)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InQuad)
        anim.finished.connect(self._on_fade_done)
        anim.start()
        self._fade_anim = anim  # prevent GC

    def _on_fade_done(self):
        self.close()
        self.deleteLater()
        self._reposition_all()

    @staticmethod
    def _reposition_all():
        """Stack all active popups from the bottom-right corner upward."""
        screen = QDesktopWidget().availableGeometry()
        x = screen.right() - POPUP_WIDTH - POPUP_MARGIN
        y = screen.bottom() - POPUP_MARGIN

        for p in reversed(_active_popups):
            y -= POPUP_HEIGHT + POPUP_SPACING
            p.move(x, y)

    @classmethod
    def _pick_colour(cls, title: str):
        t = title.lower()
        for key, (accent, bg) in cls._COLOURS.items():
            if key in t:
                return accent, bg
        return cls._COLOURS["default"]


# ------------------------------------------------------------------
# Convenience function (called from NotificationEngine)
# ------------------------------------------------------------------

def show_popup(title: str, message: str, duration_ms: int = 6000):
    """
    Create and display a notification popup.
    Must be called from the Qt main thread.
    """
    popup = NotificationPopup(title, message, duration_ms)
    popup.popup()
