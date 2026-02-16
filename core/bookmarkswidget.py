# bookmarkswidget.py - A QListWidget subclass for managing bookmarks in the browser

# importing required libraries
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# bookmard list widget for the manager
class BookmarkListWidget(QListWidget):
    # A QListWidget subclass to manage bookmarks with drag-and-drop support
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setAcceptDrops(True)

    # Override drag-and-drop events to allow adding bookmarks by dragging URLs into the widget
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    # Override dragMoveEvent to allow moving the dragged item within the widget
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    # Override dropEvent to handle dropped URLs and add them as bookmarks if they are not already present
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                url_str = url.toString()
                q = QUrl(url_str)
                q.setQuery("")
                q.setFragment("")
                url_norm = q.toString()

                # Check if the URL is already in bookmarks to avoid duplicates
                if not any(QUrl(b["url"]).toString() == url_norm for b in self.main_window.bookmarks):
                    title = url_norm
                    self.main_window.bookmarks.append({"title": title, "url": url_norm})
                    self.addItem(f"{title} - {url_norm}")
            self.main_window.save_bookmarks()
            event.acceptProposedAction()
        else:
            event.ignore()
