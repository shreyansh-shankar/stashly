# preview_worker.py
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from utils import extract_link_preview

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
