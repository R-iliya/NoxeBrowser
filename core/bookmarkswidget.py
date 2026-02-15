# --- Bookmarks & its listwidget ---
# importing required libraries
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# bookmard list widget for the manager
class BookmarkListWidget(QListWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                url_str = url.toString()
                q = QUrl(url_str)
                # remove query and fragment for normalization
                q.setQuery("")
                q.setFragment("")
                url_norm = q.toString()
                if not any(QUrl(b["url"]).toString() == url_norm for b in self.main_window.bookmarks):
                    title = url_norm
                    self.main_window.bookmarks.append({"title": title, "url": url_norm})
                    self.addItem(f"{title} - {url_norm}")
            self.main_window.save_bookmarks()
            event.acceptProposedAction()
        else:
            event.ignore()
