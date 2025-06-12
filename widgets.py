from PyQt6.QtWidgets import *
from PyQt6.QtGui import QCursor, QPainter, QColor, QPen, QPixmap, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
import os, json

from utils import *
from paths import *
from flowlayout import *
from linkcard import *

class CategoryLinksWindow(QWidget):
    def __init__(self, category_name):
        super().__init__()
        self.setWindowTitle(f"Links in Category: {category_name}")
        self.resize(1800, 900)

        layout = QVBoxLayout()

        title = QLabel(f"Links for category: {category_name}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.setLayout(layout)
        self.load_links(category_name)

    def load_links(self, category_name):
        file_path = get_data_file_path()
        if not os.path.exists(file_path):
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        for link in data:
            if link.get("category", "").strip() == category_name:
                url = link.get("url", "")
                tags =  link.get("tags", [])

                link_card = LinkCard(url, tags)

                item = QListWidgetItem()
                item.setSizeHint(link_card.sizeHint())
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, link_card)

class CategoryCard(QFrame):
    clicked = pyqtSignal(str)
    rightclicked = pyqtSignal(str)

    def __init__(self, category_name, icon_path=None, fallback_icon_path="minimize.png"):
        super().__init__()

        self.category_name = category_name
        self.setObjectName("CategoryCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame#CategoryCard {
                background-color: rgba(255, 255, 255, 30);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 40);
            }
            QFrame#CategoryCard:hover {
                background-color: rgba(255, 255, 255, 50);
            }
            QLabel {
                background: transparent;
                color: white;
                font-size: 14px;
            }
        """)

        # Mouse tracking for hover and click
        self.setMouseTracking(True)

        self.setFixedSize(150, 150)  # Uniform size for all cards

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon container
        icon_container = QWidget()
        icon_container_layout = QVBoxLayout(icon_container)
        icon_container_layout.setContentsMargins(0, 0, 0, 0)
        icon_container_layout.setSpacing(0)
        icon_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_mapping = load_icon_mapping()
        mapped_icon_path = icon_mapping.get(category_name)

        # Check icon_path validity; else fallback
        pixmap = None
        if mapped_icon_path and os.path.exists(mapped_icon_path):
            pixmap = QPixmap(mapped_icon_path)
        elif icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
        elif fallback_icon_path and os.path.exists(fallback_icon_path):
            pixmap = QPixmap(fallback_icon_path)
        else:
            # Create a simple colored pixmap fallback (e.g., gray square)
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor(180, 180, 180))

        icon_label.setPixmap(
            pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        )
        icon_container_layout.addWidget(icon_label)
        icon_container.setLayout(icon_container_layout)

        # Category name
        name_label = QLabel(category_name)
        name_label.setFont(QFont("Arial", 11, QFont.Weight.Medium))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("color: white;")

        layout.addWidget(icon_container)
        layout.addWidget(name_label)

        self.setLayout(layout)
        # Unified translucent card styling
        self.setStyleSheet("""
            QFrame#CategoryCard {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
            QFrame#CategoryCard:hover {
                background-color: rgba(0, 122, 204, 0.3);
                border: 1px solid #007acc;
            }
        """)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.category_name)
        if event.button() == Qt.MouseButton.RightButton:
            self.rightclicked.emit(self.category_name)
    
    def get_pixmap(self, icon_path):
        """Returns QPixmap from icon_path, or fallback if not found."""
        fallback_path = "minimize.png"
        if icon_path and os.path.exists(icon_path):
            return QPixmap(icon_path)
        elif os.path.exists(fallback_path):
            return QPixmap(fallback_path)
        else:
            # Final fallback: empty transparent pixmap
            pixmap = QPixmap(40, 40)
            pixmap.fill(Qt.GlobalColor.transparent)
            return pixmap

class AddLinkWindow(QWidget):

    link_saved = pyqtSignal(str)

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
        
        preview = extract_link_preview(url)

        entry = {
            "url": url,
            "title": title,
            "tags": tags,
            "category": category,
            "preview" : {
                "title" : title or preview["title"],
                "description" : preview["description"],
                "thumbnail" : preview["thumbnail"]
            }
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
        self.link_saved.emit(category)
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