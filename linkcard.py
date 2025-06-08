from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QDesktopServices, QImage
from PyQt6.QtCore import Qt, QUrl, QThreadPool
import requests
from io import BytesIO
from utils import extract_link_preview
from preview_worker import *

class LinkCard(QWidget):
    thread_pool = QThreadPool.globalInstance()

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.preview_data = None

        self.thumbnail_label = QLabel("Loading...")
        self.thumbnail_label.setFixedSize(80, 80)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("<b>Loading title...</b>")
        self.desc_label = QLabel("Fetching preview...")
        self.url_label = QLabel(f"<a href='{url}'>{url}</a>")
        self.url_label.setOpenExternalLinks(True)

        self.favicon_label = QLabel()
        self.favicon_label.setFixedSize(16, 16)
        self.favicon_label.setScaledContents(True)

        # Layout for favicon + URL
        favicon_and_url_layout = QHBoxLayout()
        favicon_and_url_layout.setSpacing(5)
        favicon_and_url_layout.addWidget(self.favicon_label)
        favicon_and_url_layout.addWidget(self.url_label)

        self.desc_label.setWordWrap(True)

        # 🔧 Now we define and assign self.text_layout properly
        self.text_layout = QVBoxLayout()
        self.text_layout.setSpacing(4)
        self.text_layout.addWidget(self.title_label)
        self.text_layout.addWidget(self.desc_label)
        self.text_layout.addLayout(favicon_and_url_layout)  # ✔️ URL & favicon together

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self.thumbnail_label)
        layout.addLayout(self.text_layout)

        self.setLayout(layout)

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

        if thumbnail_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(thumbnail_url, headers=headers, timeout=5)
                response.raise_for_status()

                image_data = response.content
                image = QImage()
                image.loadFromData(image_data)
                pixmap = QPixmap(image).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
                self.thumbnail_label.setPixmap(pixmap)
            except Exception as e:
                print("Thumbnail load failed:", e)
                self.thumbnail_label.setText("No Image")
        else:
            self.thumbnail_label.setText("No Image")
        
        # Add favicon
        if favicon_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(favicon_url, headers=headers, timeout=5)
                response.raise_for_status()
                
                image_data = response.content
                image = QImage()
                image.loadFromData(image_data)
                pixmap = QPixmap(image).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.favicon_label.setPixmap(pixmap)
            except Exception as e:
                print("Favicon load failed:", e)
                self.favicon_label.clear()
        else:
            self.favicon_label.clear()
