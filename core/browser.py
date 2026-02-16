# blocker.py - Main browser class for the Noxe web browser application, handling the main window, tabs, bookmarks, downloads, and settings

# importing required libraries
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QDesktopServices
import os
import sys

# Platform-specific imports for dark mode detection and title bar theming on Windows
if sys.platform.startswith("win"):
    import winreg
    import ctypes

from core.blocker import *
from core.scheme import *
from core.optimizations import *

# Cleanup old cache files that are larger than 50MB to prevent excessive disk usage over time
def cleanup_cache(profile):
    cache_path = profile.cachePath()
    if not os.path.exists(cache_path):
        return
    for root, _, files in os.walk(cache_path):
        for fname in files:
            fp = os.path.join(root, fname)
            try:
                if os.path.getsize(fp) > 50 * 1024 * 1024:
                    os.remove(fp)
            except (OSError, PermissionError):
                pass  # file in use or permission issue

# Set up JavaScript overrides to enhance privacy by blocking common ad/tracker patterns and spoofing dark mode preferences
def set_privacy_overrides(profile, dark_mode=True):
    js = f"""
    (function() {{
        try {{
            if (window.__matchMediaOverridden) return;
            window.__matchMediaOverridden = true;

            // safe matchMedia override
            var nativeMatchMedia = window.matchMedia;
            window.matchMedia = function(query) {{
                if (query.includes("prefers-color-scheme: dark")) {{
                    return {{ matches: {str(dark_mode).lower()}, media: query }};
                }}
                if (query.includes("prefers-color-scheme: light")) {{
                    return {{ matches: {str(not dark_mode).lower()}, media: query }};
                }}
                return nativeMatchMedia ? nativeMatchMedia.call(window, query) : {{ matches: false, media: query }};
            }};

            // simple ad patterns for beacons + DOM
            const adPatterns = [
                /doubleclick\\.net/i, /googlesyndication\\.com/i, /adservice\\.google\\.com/i,
                /googletagservices\\.com/i, /googletagmanager\\.com/i, /taboola\\.com/i,
                /outbrain\\.com/i, /criteo\\.net/i, /scorecardresearch\\.com/i
            ];

            function isAdUrl(url) {{
                if (!url) return false;
                url = typeof url === 'string' ? url : (url.url || url.toString() || '');
                return adPatterns.some(p => p.test(url));
            }}

            // block beacons
            if (navigator && navigator.sendBeacon) {{
                const _sendBeacon = navigator.sendBeacon.bind(navigator);
                navigator.sendBeacon = function(url, data) {{
                    if (isAdUrl(url)) {{
                        console.debug("[AdBlock] blocked beacon", url);
                        return false;
                    }}
                    return _sendBeacon(url, data);
                }};
            }}

            // DOM cleanup for iframes + class-based ads
            const observer = new MutationObserver(mutations => {{
                for (const m of mutations) {{
                    for (const node of m.addedNodes) {{
                        try {{
                            if (node.tagName === 'IFRAME') {{
                                const src = node.src || node.getAttribute('src') || '';
                                if (isAdUrl(src)) node.remove();
                            }}
                            if (node.className && /(^|\\s)(ad|ads|banner|sponsor|sponsored)(\\s|$)/i.test(node.className)) {{
                                node.remove();
                            }}
                        }} catch(e) {{ }}
                    }}
                }}
            }});
            observer.observe(document.documentElement || document, {{ childList: true, subtree: true }});

            window.__lightAdBlock = {{ isAdUrl, patterns: adPatterns }};
        }} catch(e) {{
            console.warn("privacyOverrides failed:", e);
        }}
    }})();
    """

    script = QWebEngineScript()
    script.setName("privacyOverrides")
    script.setInjectionPoint(QWebEngineScript.DocumentReady)
    script.setRunsOnSubFrames(False)
    script.setWorldId(QWebEngineScript.MainWorld)
    script.setSourceCode(js)
    scripts = profile.scripts()

    # Use insert if available to avoid duplicates, otherwise fallback to addScript (Qt5)
    try:
        if hasattr(scripts, "insert"):
            scripts.insert(script)
        else:
            scripts.addScript(script)
    except Exception as e:
        print("Could not add JS override script:", e)

# detect if OS is in dark mode (Windows) to sync browser theme and provide a better user experience, also used for JS overrides to spoof dark mode preference to websites
def is_os_dark_mode():
    if sys.platform.startswith("win"):
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except:
            return False
    return False

# Update Windows title bar to match dark mode preference through DwmSetWindowAttribute for a more integrated look on Windows 10/11 when dark mode is enabled. 
# This is called after the main window is created to ensure the title bar matches the rest of the application's dark theme.
def update_windows_titlebar(window):
    if sys.platform.startswith("win"):
        try:
            import ctypes
            hwnd = int(window.winId())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1 if is_os_dark_mode() else 0)),
                ctypes.sizeof(ctypes.c_int)
            )
        except:
            pass

# Apply dark theme to the entire application using a custom palette and stylesheet for a consistent dark mode experience across all widgets and controls
def apply_dark_theme(app):
    app.setStyle("Fusion")
    dark_palette = QPalette()

    dark_color = QColor(45, 45, 45)
    disabled_color = QColor(127, 127, 127)

    dark_palette.setColor(QPalette.Window, dark_color)
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(16, 20, 24))
    dark_palette.setColor(QPalette.AlternateBase, dark_color)
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, dark_color)
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, disabled_color)
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_color)

    app.setPalette(dark_palette)

    # Stylesheet for additional theming of widgets to match the dark mode.
    app.setStyleSheet("""
        QWidget { background-color: #2d2d2d; color: #ffffff; border-radius: 8px; }
        QLineEdit, QProgressBar, QListWidget, QDockWidget { background-color: #3a3a3a; border-radius: 8px; padding: 6px; }
        QMenu { background: rgba(45, 45, 45, 220); border: 1px solid #3c3c3c; border-radius: 8px; padding: 6px; }
        QMenu::item { padding: 6px 32px; color: #f0f0f0; }
        QMenu::item:selected { background-color: #3d3d3d; }
        QPushButton { background-color: #444; border-radius: 6px; padding: 6px; }
        QPushButton:hover { background-color: #555; }
        QTabBar::tab { background: #3a3a3a; border-radius: 8px; padding: 6px; margin: 2px; }
        QTabBar::tab:selected { background: #555; }
    """)


# Download item widget to show download progress and allow opening/canceling downloads in the download manager.
class DownloadItem(QWidget):
    def __init__(self, download):
        super().__init__()
        self.download = download
        self.file_path = None

        layout = QHBoxLayout()
        self.label = QLabel(download.suggestedFileName())
        self.progress = QProgressBar()
        self.open_btn = QPushButton("Open")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_file)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_download)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.open_btn)
        layout.addWidget(self.cancel_btn)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.setLayout(layout)

        download.downloadProgress.connect(self.on_progress)
        download.finished.connect(self.on_finished)

    def on_progress(self, received, total):
        if total > 0:
            self.progress.setValue(int(received / total * 100))

    # When the download finishes, update the UI to allow opening the file and change the cancel button to a remove button. 
    # Also, try to get the file path for opening later, but handle cases where it may not be available.
    def on_finished(self):
        self.progress.setValue(100)
        self.progress.setFormat("Finished")
        self.cancel_btn.setText("Remove")
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.remove_self)
        self.open_btn.setEnabled(True)
        # Try to get path after finish
        try:
            self.file_path = self.download.path()
        except AttributeError:
            self.file_path = None  # Qt5 doesn't expose path reliably
        QTimer.singleShot(10000, self.remove_self)

    # Open the downloaded file using the default application, or show an error if the path is not available
    def open_file(self):
        if self.file_path and os.path.exists(self.file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.file_path))
        else:
            print("Cannot open file - path not available")

    # Cancel the download if it's still in progress, or remove the item if it's already finished. 
    # Also update the UI to reflect the canceled state.
    def cancel_download(self):
        self.download.cancel()
        self.progress.setFormat("Canceled")
        self.cancel_btn.setDisabled(True)
        QTimer.singleShot(5000, self.remove_self)

    def remove_self(self):
        self.setParent(None)
        self.deleteLater()


from core.bookmarkswidget import *