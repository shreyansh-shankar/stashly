from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage
import os, requests, json

from utils import extract_link_preview

class ImageLoaderSignals(QObject):
    finished = pyqtSignal(QImage, QImage)  # thumbnail, favicon

class ImageLoaderWorker(QRunnable):
    def __init__(self, cache_folder):
        super().__init__()
        self.cache_folder = cache_folder
        self.signals = ImageLoaderSignals()

    def run(self):
        thumb_img = None
        favicon_img = None

        thumb_path = os.path.join(self.cache_folder, "thumbnail.png")
        favicon_path = os.path.join(self.cache_folder, "favicon.png")
        meta_path = os.path.join(self.cache_folder, "preview.txt")

        headers = {"User-Agent": "Mozilla/5.0"}

        if os.path.exists(thumb_path):
            try:
                image = QImage(thumb_path)
                if not image.isNull():
                    thumb_img = image
            except Exception as e:
                print("Thumbnail load failed:", e)

        if os.path.exists(favicon_path):
            try:
                image = QImage(favicon_path)
                if not image.isNull():
                    favicon_img = image
            except Exception as e:
                print("Favicon load failed:", e)
        
        # If either image is missing, try fetching using URLs in meta.txt
        if (thumb_img is None or favicon_img is None) and os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Load missing thumbnail
                if thumb_img is None:
                    url = data.get("thumbnail", "")
                    if url.startswith("http"):
                        response = requests.get(url, headers=headers, timeout=5)
                        if response.status_code == 200:
                            with open(thumb_path, "wb") as f_out:
                                f_out.write(response.content)
                            image = QImage()
                            image.loadFromData(response.content)
                            if not image.isNull():
                                thumb_img = image

                # Load missing favicon
                if favicon_img is None:
                    url = data.get("favicon", "")
                    if url.startswith("http"):
                        response = requests.get(url, headers=headers, timeout=5)
                        if response.status_code == 200:
                            with open(favicon_path, "wb") as f_out:
                                f_out.write(response.content)
                            image = QImage()
                            image.loadFromData(response.content)
                            if not image.isNull():
                                favicon_img = image

            except Exception as e:
                print("[ImageWorker] Error reading preview.txt or downloading images:", e)
            
        # === Safety: Return empty QImages if needed ===
        if thumb_img is None:
            thumb_img = QImage()  # Empty image
        if favicon_img is None:
            favicon_img = QImage()

        self.signals.finished.emit(thumb_img, favicon_img)

class PreviewWorkerSignals(QObject):
    finished = pyqtSignal(dict)

class PreviewWorker(QRunnable):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = PreviewWorkerSignals()

    @pyqtSlot()
    def run(self):
        preview = extract_link_preview(self.url)
        self.signals.finished.emit(preview)

