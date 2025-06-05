from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QCursor, QPainter, QColor, QPen
from PyQt6.QtCore import Qt

class PlusButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.default_color = "#4682B4"
        self.hover_color = "#6495ED"
        self.current_color = self.default_color

        self.setFixedSize(60, 60)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("background-color: #4682B4; border-radius: 30px;")
        self.setToolTip("Add new link")

    def enterEvent(self, event):
        self.current_color = self.hover_color
        self.setStyleSheet(f"background-color: {self.current_color}; border-radius: 30px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.current_color = self.default_color
        self.setStyleSheet(f"background-color: {self.current_color}; border-radius: 30px;")
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        # Draw plus sign in the center
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor('white'))
        pen.setWidth(3)
        painter.setPen(pen)
        w, h = self.width(), self.height()
        # Draw vertical line
        painter.drawLine(w//2, 3*h//10, w//2, 7*h//10)
        # Draw horizontal line
        painter.drawLine(3*w//10, h//2, 7*w//10, h//2)