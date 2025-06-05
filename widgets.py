from PyQt6.QtWidgets import *
from PyQt6.QtGui import QCursor, QPainter, QColor, QPen
from PyQt6.QtCore import Qt

from paths import *

class AddLinkWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Link")
        self.setFixedSize(700, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  # Block main window

        form_layout = QFormLayout()

        self.url_input = QLineEdit()
        self.title_input = QLineEdit()
        self.tags_input = QLineEdit()
        self.category_input = QLineEdit()

        form_layout.addRow("URL *", self.url_input)
        form_layout.addRow("Title", self.title_input)
        form_layout.addRow("Tags", self.tags_input)
        form_layout.addRow("Category", self.category_input)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_link)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def save_link(self):
        url = self.url_input.text().strip()
        title = self.title_input.text().strip()
        tags = self.tags_input.text().strip()
        category = self.category_input.text().strip()

        if url.strip() == "":
            print("URL is required!")
            return
        
        entry = {
        "url": url,
        "title": title,
        "tags": tags,
        "category": category
        }

        file_path = get_data_file_path()

        # Load existing data and append
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception:
            data = []
        
        data.append(entry)

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        print("Link saved successfully")
        self.close()

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