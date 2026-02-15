# --- Main Code ---
# importing required libraries
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess
import platform
import winreg
import ctypes
import json
import sys
import os
from PyQt5.QtWebEngineCore import (
    QWebEngineUrlRequestInterceptor,
    QWebEngineUrlSchemeHandler,
    QWebEngineUrlScheme,
)

# importing browser modules
from core.optimizations import *
from core.bookmarkswidget import *
from core.blocker import *
from core.scheme import *
from core.browser import *
from core.mainwindow import *


if sys.platform.startswith("win"):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        if __debug__:
            print("DPI awareness set to per-monitor")
    except Exception as e:
        if __debug__:
            print("DPI awareness failed:", e)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller exe."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


print("\n[Browser Loaded]")
if __debug__:
    print("GPU:", gpu.strip())
    print("QT_OPENGL:", os.environ.get('QT_OPENGL'))
    print(f"Flags: {len(flags)} applied")
    print(OPT_RESULT, "\n")

# ---- MAIN ENTRYPOINT ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setApplicationName("Noxe Browser")
    if is_os_dark_mode():
        apply_dark_theme(app)
    else:
        app.setStyle("Fusion")
    window = MainWindow()
    window.setAutoFillBackground(True)
    icon_path = resource_path("core/icon.ico")  # bundled with --add-data "core;core"
    window.setWindowIcon(QIcon(icon_path))
    window.show()
    sys.exit(app.exec_())