from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QDesktopServices, QImage, QCursor, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QUrl, QThreadPool
import requests
from utils import extract_link_preview
from preview_worker import *

class LinkCard(QWidget):
    thread_pool = QThreadPool.globalInstance()

    def __init__(self, url, tags=None):
        super().__init__()
        self.url = url
        self.tags = tags or []
        self.preview_data = None

        # === Title ===
        self.title_label = QLabel("<b>Loading title...</b>")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.favicon_label = QLabel()
        self.favicon_label.setFixedSize(24, 24)  # Increased size
        self.favicon_label.setScaledContents(True)

        # === Open Button ===
        self.open_button = QPushButton("Open")
        self.open_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 22px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        self.open_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.url)))

        # === Title Row ===
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_with_icon = QHBoxLayout()
        title_with_icon.addWidget(self.favicon_label)
        title_with_icon.addWidget(self.title_label)
        title_with_icon.addStretch()

        title_row.addLayout(title_with_icon)
        title_row.addWidget(self.open_button)

        # === Tags Row ===
        self.tags_layout = QHBoxLayout()
        self.tags_layout.setSpacing(6)
        for tag in self.tags:
            tag_label = QLabel(tag)
            tag_label.setStyleSheet("""
                color: #020202;
                background-color: #f0f0f0;
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 20px;
                margin: 4px;
            """)
            self.tags_layout.addWidget(tag_label)
        self.tags_layout.addStretch()

        # === Description ===
        self.desc_label = QLabel("Fetching preview...")
        self.desc_label.setWordWrap(True)
        self.desc_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.desc_label.setMaximumHeight(500)
        self.desc_label.setStyleSheet("border: none; background: transparent; padding: 4px;")

        # === Thumbnail ===
        self.thumbnail_label = QLabel("No Image")
        self.thumbnail_label.setFixedSize(120, 90)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setStyleSheet("border: none; background: transparent; padding: 4px;")

        # === Content (Thumbnail + Description) with border ===
        content_inner_layout = QHBoxLayout()
        content_inner_layout.addWidget(self.thumbnail_label)
        content_inner_layout.addWidget(self.desc_label)

        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
            }
        """)
        content_frame.setLayout(content_inner_layout)

        # === Final Layout ===
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addLayout(title_row)
        main_layout.addLayout(self.tags_layout)
        main_layout.addWidget(content_frame)

        self.setLayout(main_layout)
        self.load_preview()

    def load_preview(self):
        worker = PreviewWorker(self.url)
        worker.signals.finished.connect(self.set_preview_data)
        LinkCard.thread_pool.start(worker)

    def set_preview_data(self, preview):
        self.title_label.setText(f"<b>{preview.get('title', self.url)}</b>")
        self.desc_label.setText(preview.get("description", ""))
        thumbnail_url = preview.get("thumbnail", "")
        favicon_url = preview.get("favicon", "")

        headers = {"User-Agent": "Mozilla/5.0"}

        # 🌄 Load Thumbnail with Rounded Corners
        if thumbnail_url:
            try:
                response = requests.get(thumbnail_url, headers=headers, timeout=5)
                response.raise_for_status()

                image = QImage()
                image.loadFromData(response.content)

                # Resize image first
                image = image.scaled(160, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                    Qt.TransformationMode.SmoothTransformation)

                # Create a rounded pixmap
                rounded_pixmap = QPixmap(image.size())
                rounded_pixmap.fill(Qt.GlobalColor.transparent)

                painter = QPainter(rounded_pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                path = QPainterPath()
                radius = 12  # Adjust corner radius here
                path.addRoundedRect(0, 0, image.width(), image.height(), radius, radius)

                painter.setClipPath(path)
                painter.drawPixmap(0, 0, QPixmap.fromImage(image))
                painter.end()

                self.thumbnail_label.setPixmap(rounded_pixmap)

            except Exception as e:
                print("Thumbnail load failed:", e)
                self.thumbnail_label.setText("No Image")
        else:
            self.thumbnail_label.setText("No Image")


        # 🌐 Load Favicon
        if favicon_url:
            try:
                response = requests.get(favicon_url, headers=headers, timeout=5)
                response.raise_for_status()

                image = QImage()
                image.loadFromData(response.content)
                pixmap = QPixmap(image).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                self.favicon_label.setPixmap(pixmap)
            except Exception as e:
                print("Favicon load failed:", e)
                self.favicon_label.clear()
        else:
            self.favicon_label.clear()
