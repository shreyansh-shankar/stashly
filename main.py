from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
from PyQt6.QtGui import QCursor, QIcon, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QSize, QRect, QPoint
import sys

from widgets import PlusButton

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stashly - Smart Link Manager")
        self.resize(1400, 800)

        # Create the plus button
        self.plus_button = PlusButton(self)
        self.update_plus_button_position()

        self.plus_button.clicked.connect(self.on_plus_clicked)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_plus_button_position()

    def update_plus_button_position(self):
        margin = 30
        x = self.width() - self.plus_button.width() - margin
        y = self.height() - self.plus_button.height() - margin
        self.plus_button.move(x, y)

    def on_plus_clicked(self):
        print("Plus button clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
