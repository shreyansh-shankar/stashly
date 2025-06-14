from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QDesktopServices, QImage, QCursor, QPainter, QPainterPath, QAction
from PyQt6.QtCore import Qt, QUrl, QThreadPool
import requests
from utils import *
from paths import get_data_file_path
from preview_worker import *

class LinkCard(QWidget):
    thread_pool = QThreadPool.globalInstance()
    delete_requested = pyqtSignal(str)

    def __init__(self, url, tags=None):

        super().__init__()
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

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
        self.tags_widget = QWidget()
        self.tags_layout = QHBoxLayout()
        self.tags_layout.setSpacing(6)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for tag in self.tags:
            tag_label = QLabel(tag)
            tag_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
            tag_label.setStyleSheet("""
                color: #020202;
                background-color: #f0f0f0;
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 20px;
                margin: 4px;
            """)
            self.tags_layout.addWidget(tag_label)
        self.tags_widget.setLayout(self.tags_layout)

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

        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
            }
        """)
        self.content_frame.setLayout(content_inner_layout)

        # === Final Layout ===
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addLayout(title_row)
        main_layout.addWidget(self.tags_widget)
        main_layout.addWidget(self.content_frame)

        self.setLayout(main_layout)
        self.load_preview()

    def show_context_menu(self, position):
        menu = QMenu(self)

        modify_action = QAction("Modify Tags", self)
        modify_action.triggered.connect(self.modify_tags)

        delete_action = QAction("Delete Link", self)
        delete_action.triggered.connect(self.delete_link)

        menu.addAction(modify_action)
        menu.addSeparator()
        menu.addAction(delete_action)

        menu.exec(self.mapToGlobal(position))

    def modify_tags(self):
        current_tags = ", ".join(self.tags)
        new_tags, ok = QInputDialog.getText(self, "Modify Tags", "Enter new tags :", text=current_tags)
        if not ok:
            return
        
        self.tags = [tag.strip() for tag in new_tags.split(",") if tag.strip()]

        # Refresh tag labels
        while self.tags_layout.count():
            widget = self.tags_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        for tag in self.tags:
            tag_label = QLabel(tag)
            tag_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
            tag_label.setStyleSheet("""
                color: #020202;
                background-color: #f0f0f0;
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 20px;
                margin: 4px;
            """)
            self.tags_layout.addWidget(tag_label)
        
        # Persist changes into the files
        try:
            file_path = get_data_file_path()
            if not os.path.exists(file_path):
                return

            with open(file_path, 'r') as f:
                data = json.load(f)

            # Find and update the matching link by URL
            for entry in data:
                if entry.get("url") == self.url:
                    entry["tags"] = self.tags
                    break

            # Save the updated data
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update tags:\n{str(e)}")


    def delete_link(self):
        confirm = QMessageBox.question(self, "Delete Link",
        f"Are you sure you want to delete this link?\n{self.url}",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                cache_folder = get_cache_folder_for_url(self.url)
                if os.path.exists(cache_folder):
                    import shutil
                    shutil.rmtree(cache_folder)
            except Exception as e:
                QMessageBox.warning(self, "Cache Deletion Failed", f"Failed to delete cached data:\n{str(e)}")
            
            self.delete_requested.emit(self.url)

    def load_preview(self):
        worker = PreviewWorker(self.url)
        worker.signals.finished.connect(self.set_preview_data)
        LinkCard.thread_pool.start(worker)

    def set_preview_data(self, preview):
        self.title_label.setText(f"<b>{preview.get('title', self.url)}</b>")
        
        description = preview.get("description", "")
        if description:
            self.desc_label.setText(description)
            self.desc_label.show()
        else:
            self.desc_label.hide()

        self.thumbnail_label.setText("Loading...")
        self.favicon_label.clear()

        # === Load Images from Disk in Background Thread ===
        cache_folder = get_cache_folder_for_url(self.url)
        image_worker = ImageLoaderWorker(cache_folder)
        image_worker.signals.finished.connect(self.set_images_from_cache)
        LinkCard.thread_pool.start(image_worker)
    
    def set_images_from_cache(self, thumbnail_img, favicon_img):
        # Handle thumbnail
        if thumbnail_img and not thumbnail_img.isNull():
            # Resize and apply rounded corners
            image = thumbnail_img.scaled(160, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                        Qt.TransformationMode.SmoothTransformation)

            rounded_pixmap = QPixmap(image.size())
            rounded_pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            path = QPainterPath()
            radius = 12
            path.addRoundedRect(0, 0, image.width(), image.height(), radius, radius)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, QPixmap.fromImage(image))
            painter.end()
            
            self.thumbnail_label.setPixmap(rounded_pixmap)
            self.thumbnail_label.show()
        else:
            self.thumbnail_label.hide()

        # Handle favicon
        if favicon_img and not favicon_img.isNull():
            pixmap = QPixmap(favicon_img).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation)
            self.favicon_label.setPixmap(pixmap)
        else:
            self.favicon_label.clear()
        
        # Final cleanup: if both are hidden, also hide the content_frame (optional)
        if self.thumbnail_label.isHidden() and self.desc_label.isHidden():
            self.content_frame.hide()  # This hides the whole content_frame
        else:
            self.content_frame.show()