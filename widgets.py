from PyQt6.QtWidgets import *
from PyQt6.QtGui import QCursor, QPainter, QColor, QPen
from PyQt6.QtCore import Qt

from paths import *
from flowlayout import *

class AddLinkWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Link")
        self.setFixedSize(700, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  # Block main window

        form_layout = QFormLayout()

        self.url_input = QLineEdit()
        self.title_input = QLineEdit()
        
        self.tags_input = QComboBox()
        self.tags_input.setEditable(True)
        self.tags_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.tags_input.lineEdit().setPlaceholderText("Select one or more tags...")
        self.tags_input.lineEdit().returnPressed.connect(self.add_tag)
        self.tags_list = []
        self.tags_display = FlowLayout()
        self.tags_display_widget = QWidget()
        self.tags_display_widget.setLayout(self.tags_display)
        
        self.category_input = QComboBox()
        self.category_input.setEditable(True)

        form_layout.addRow("URL *", self.url_input)
        form_layout.addRow("Title", self.title_input)
        tag_layout = QVBoxLayout()
        tag_layout.addWidget(self.tags_input)
        tag_layout.addWidget(self.tags_display_widget)
        form_layout.addRow("Tags", tag_layout)
        form_layout.addRow("Category", self.category_input)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_link)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.load_existing_tags_categories()

    def add_tag(self):
        tag_text = self.tags_input.currentText().strip()
        if tag_text and tag_text not in self.tags_list:
            self.tags_list.append(tag_text)

            tag_label = QLabel(tag_text)
            tag_label.setStyleSheet("color: #000000; background-color: #d1ecf1; border-radius: 5px; padding: 5px; margin-right: 5px;")
            
            # Optional: remove tag on click
            tag_label.mousePressEvent = lambda e, t=tag_text, w=tag_label: self.remove_tag(t, w)

            self.tags_display.addWidget(tag_label)
            self.tags_input.setCurrentText("")

    def load_existing_tags_categories(self):
        file_path = get_data_file_path()

        tags_set = set()
        categories_set = set()

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        if item.get("tags"):
                            if isinstance(item["tags"], list):
                                tags_set.update(map(str.strip, item["tags"]))
                            elif isinstance(item["tags"], str):
                                tags_set.update(map(str.strip, item["tags"].split(",")))
                        if item.get("category"):
                            categories_set.add(item["category"].strip())
            except Exception as e:
                print("Error reading data file:", e)

        self.tags_input.addItems(sorted(tags_set))
        self.category_input.addItems(sorted(categories_set))

    def remove_tag(self, tag_text, widget):
        if tag_text in self.tags_list:
            self.tags_list.remove(tag_text)
            widget.setParent(None)  # removes the QLabel

    def save_link(self):
        url = self.url_input.text().strip()
        title = self.title_input.text().strip()
        raw_tags = self.tags_input.currentText().strip()
        tags = self.tags_list
        category = self.category_input.currentText().strip()

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