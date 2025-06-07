from PyQt6.QtWidgets import *
from PyQt6.QtGui import QCursor, QIcon, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QSize, QRect, QPoint
import sys, os, json
from paths import *

from widgets import PlusButton, AddLinkWindow, CategoryCard

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stashly - Smart Link Manager")
        self.resize(1400, 800)

        # Layout for main screen
        self.main_layout = QVBoxLayout(self)

        # Grid layout for category cards inside a scroll area
        self.category_grid = QGridLayout()
        self.category_grid.setSpacing(20)
        self.category_grid.setContentsMargins(20, 20, 20, 20)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_content.setLayout(self.category_grid)
        scroll_area.setWidget(scroll_content)

        self.main_layout.addWidget(scroll_area)

        # Create the plus button
        self.plus_button = PlusButton(self)
        self.update_plus_button_position()

        self.plus_button.clicked.connect(self.show_add_link_window)

        self.load_categories()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_plus_button_position()

    def update_plus_button_position(self):
        margin = 30
        x = self.width() - self.plus_button.width() - margin
        y = self.height() - self.plus_button.height() - margin
        self.plus_button.move(x, y)

    def show_add_link_window(self):
        self.add_window = AddLinkWindow()
        self.add_window.move(
            self.geometry().center() - self.add_window.rect().center()
        )
        self.add_window.show()

    def load_categories(self):
        file_path = get_data_file_path()
        if not os.path.exists(file_path):
            return

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print("Error loading categories:", e)
            return

        categories = set()
        for entry in data:
            if cat := entry.get("category", "").strip():
                categories.add(cat)

        # Populate grid
        for i, category in enumerate(sorted(categories)):
            row, col = divmod(i, 4)
            card = CategoryCard(category)  # Can add icon support later
            self.category_grid.addWidget(card, row, col)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
