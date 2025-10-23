# --- Main Code ---
print("1 Running Main code")
# importing required libraries
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess
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
    import ctypes
    # Make the app DPI aware so it scales correctly on high-DPI displays
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # System DPI aware
    except Exception:
        pass

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
    sys.exit(app.exec_())