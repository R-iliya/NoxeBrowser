# --- Browser & WebView ---
print("6 Running Browser")
# importing required libraries
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess
if sys.platform.startswith("win"):
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

def apply_blur_transparent(menu: QMenu):
    menu.setAttribute(Qt.WA_TranslucentBackground, True)
    menu.setStyleSheet("""
        QMenu {
            background: rgba(45, 45, 45, 220);
            border-radius: 10px;
            padding: 6px;
        }
        QMenu::item {
            padding: 4px 30px 4px 10px;
            color: #f0f0f0;
            border-radius: 6px;
        }
        QMenu::item:selected {
            background: rgba(70, 70, 70, 180);
        }
    """)
    # Optional fade-in animation
    menu.setWindowOpacity(0.0)
    anim = QPropertyAnimation(menu, b"windowOpacity")
    anim.setDuration(120)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutQuad)
    anim.start(QPropertyAnimation.DeleteWhenStopped)
    return anim

original_show = QMenu.show
def show_with_blur(self):
    apply_blur_transparent(self)
    original_show(self)

QMenu.show = show_with_blur

def animate_menu(menu):
    menu.setWindowOpacity(0.0)
    anim = QPropertyAnimation(menu, b"windowOpacity")
    anim.setDuration(120)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutQuad)
    anim.start(QPropertyAnimation.DeleteWhenStopped)
    return anim

from core.blocker import *

from core.scheme import *

from core.optimizations import *

def cleanup_cache():
    if os.path.exists("./cache"):
        for fname in os.listdir("./cache"):
            fp = os.path.join("./cache", fname)
            if os.path.isfile(fp):
                try:
                    if os.path.getsize(fp) > 50*1024*1024:
                        os.remove(fp)
                except (OSError, PermissionError, Exception):
                    pass

def save_tab_order(self):
    try:
        order = [self.tabs.widget(i).url().toString() for i in range(self.tabs.count())]
        with open("tabs.json", "w", encoding="utf-8") as f:
            json.dump(order, f, indent=2)
    except Exception as e:
        print("Failed to save tab order:", e)

def load_tab_order(self):
    if os.path.exists("tabs.json"):
        with open("tabs.json", "r") as f:
            urls = json.load(f)
        for url in urls:
            try:
                qurl = QUrl(url)
                if qurl.isValid():
                    self.add_new_tab(qurl)
            except Exception as e:
                print("Failed to load tab:", url, e)


class Blocker(QWebEngineUrlRequestInterceptor):
    BLOCK_LIST = [
        "doubleclick.net", "googlesyndication.com", "adservice.google.com",
        "googletagmanager.com", "googletagservices.com", "taboola.com",
        "outbrain.com", "criteo.net", "adroll.com", "scorecardresearch.com",
    ]
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if any(b in url for b in self.BLOCK_LIST):
            info.block(True)

def set_privacy_overrides(profile, dark_mode=True):
    js = f"""
    (function() {{
        try {{
            // --- avoid double-inject ---
            if (window.__matchMediaOverridden) return;
            window.__matchMediaOverridden = true;

            // --- safe matchMedia override (falls back to native) ---
            var desc;
            try {{ desc = Object.getOwnPropertyDescriptor(window, 'matchMedia'); }} catch(e) {{ desc = null; }}
            if (!(desc && desc.writable === false)) {{
                var mqlDark = {{
                    matches: {str(dark_mode).lower()},
                    media: "(prefers-color-scheme: dark)",
                    onchange: null,
                    addEventListener: function(){{}},
                    removeEventListener: function(){{}},
                    addListener: function(){{}},
                    removeListener: function(){{}}
                }};
                var mqlLight = {{
                    matches: {str(not dark_mode).lower()},
                    media: "(prefers-color-scheme: light)",
                    onchange: null,
                    addEventListener: function(){{}},
                    removeEventListener: function(){{}},
                    addListener: function(){{}},
                    removeListener: function(){{}}
                }};
                var nativeMatchMedia = window.matchMedia;
                window.matchMedia = function(query) {{
                    try {{
                        if (query.indexOf("prefers-color-scheme: dark") !== -1) return mqlDark;
                        if (query.indexOf("prefers-color-scheme: light") !== -1) return mqlLight;
                        return nativeMatchMedia ? nativeMatchMedia.call(window, query) : {{ matches: false, media: query }};
                    }} catch(e) {{
                        console.warn("matchMedia override error:", e);
                        return {{ matches: false, media: query }};
                    }}
                }};
            }}

            // --- Lightweight in-page network blocker (simple patterns) ---
            const adPatterns = [
                /doubleclick\\.net/i,
                /googlesyndication\\.com/i,
                /adservice\\.google\\.com/i,
                /googletagservices\\.com/i,
                /googletagmanager\\.com/i,
                /adsystem\\.com/i,
                /adsafeprotected\\.com/i,
                /adroll\\.com/i,
                /taboola\\.com/i,
                /outbrain\\.com/i,
                /scorecardresearch\\.com/i,
                /amazon-adsystem\\.com/i,
                /yahoo-ads\\.com/i,
                /criteo\\.net/i,
                /zedo\\.com/i
            ];

            function isAdUrl(url) {{
                try {{
                    if (!url) return false;
                    url = typeof url === 'string' ? url : (url.url || url.toString());
                    return adPatterns.some(p => p.test(url));
                }} catch(e) {{
                    return false;
                }}
            }}

            // --- override fetch ---
            const _fetch = window.fetch;
            window.fetch = function(input, init) {{
                try {{
                    const url = (typeof input === 'string') ? input :
                                (input && input.url) ? input.url : '';
                    if (isAdUrl(url)) {{
                        console.debug("[AdBlock] blocked fetch", url);
                        // return a rejected promise so caller sees a network error
                        return Promise.reject(new TypeError('Network request blocked by lightweight ad blocker'));
                    }}
                }} catch(e){{ /* ignore */ }}
                return _fetch.apply(this, arguments);
            }};

            // --- override XMLHttpRequest (capture URL on open, block on send) ---
            const _xhrOpen = XMLHttpRequest.prototype.open;
            const _xhrSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.open = function(method, url) {{
                try {{ this.__adblock_url = url; }} catch(e){{ this.__adblock_url = null; }}
                return _xhrOpen.apply(this, arguments);
            }};
            XMLHttpRequest.prototype.send = function(body) {{
                try {{
                    if (isAdUrl(this.__adblock_url)) {{
                        console.debug("[AdBlock] blocked XHR", this.__adblock_url);
                        // Abort silently:
                        this.abort && this.abort();
                        // Fire readyState changes to mimic a failed request (optional)
                        if (typeof this.onerror === 'function') {{
                            try {{ this.onerror(new Error('Blocked by adblock')); }} catch(e){{ }}
                        }}
                        return;
                    }}
                }} catch(e){{ /* ignore */ }}
                return _xhrSend.apply(this, arguments);
            }};

            // --- block WebSocket connections to known ad hosts (throw on construction) ---
            const WS = window.WebSocket;
            if (WS) {{
                window.WebSocket = function(url, protocols) {{
                    if (isAdUrl(url)) {{
                        console.debug("[AdBlock] blocked WebSocket", url);
                        throw new Error('Blocked WebSocket to ad host');
                    }}
                    return new WS(url, protocols);
                }};
                // copy static properties
                window.WebSocket.prototype = WS.prototype;
                window.WebSocket.CONNECTING = WS.CONNECTING;
                window.WebSocket.OPEN = WS.OPEN;
                window.WebSocket.CLOSING = WS.CLOSING;
                window.WebSocket.CLOSED = WS.CLOSED;
            }}

            // --- block navigator.sendBeacon to ad endpoints ---
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

            // --- simple DOM cleanup: remove common ad iframes/elements as they appear ---
            const observer = new MutationObserver(mutations => {{
                for (const m of mutations) {{
                    for (const node of m.addedNodes) {{
                        try {{
                            if (!node) continue;
                            if (node.tagName === 'IFRAME') {{
                                const src = node.src || node.getAttribute('src') || '';
                                if (isAdUrl(src)) {{
                                    node.remove();
                                    continue;
                                }}
                            }}
                            if (node.className && /(^|\\s)(ad|ads|banner|sponsor|sponsored)(\\s|$)/i.test('' + node.className)) {{
                                node.remove();
                                continue;
                            }}
                        }} catch(e){{ }}
                    }}
                }}
            }});
            observer.observe(document.documentElement || document, {{ childList: true, subtree: true }});

            // keep the list accessible from console for debugging:
            window.__lightAdBlock = {{ isAdUrl: isAdUrl, patterns: adPatterns }};
        }} catch(e) {{
            console.warn("privacyOverrides failed:", e);
        }}
    }})();
    """

    script = QWebEngineScript()
    script.setName("privacyOverrides")
    script.setInjectionPoint(QWebEngineScript.DocumentCreation)
    script.setRunsOnSubFrames(False)
    script.setWorldId(QWebEngineScript.ApplicationWorld)
    script.setSourceCode(js)

    scripts = profile.scripts()
    try:
        if hasattr(scripts, "insert"):
            scripts.insert(script)
        else:
            scripts.addScript(script)
    except Exception as e:
        print("Could not add JS override script:", e)

# Enabling Windows10+ dark window
def enable_dark_titlebar(hwnd):
    """Enable dark mode titlebar if Windows supports it."""
    try:
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # for Windows 10 1809+
        set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
        value = ctypes.c_int(1)
        set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                             ctypes.byref(value), ctypes.sizeof(value))
    except Exception as e:
        print("Dark mode titlebar not supported:", e)


# Darkmode check on Windows
def is_windows_dark_mode():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0  # 0 = dark mode, 1 = light mode
    except Exception:
        return False  # default fallback

# Darkmode check on MacOS
def is_macos_dark_mode():
    try:
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True, text=True
        )
        return "Dark" in result.stdout
    except Exception:
        return False

# Darkmode check on Linux
def is_linux_dark_mode():
    # try GTK setting
    gtk_theme = os.environ.get("GTK_THEME", "").lower()
    return "dark" in gtk_theme

def is_os_dark_mode():
    if sys.platform.startswith("win"):
        return is_windows_dark_mode()
    elif sys.platform.startswith("darwin"):
        return is_macos_dark_mode()
    else:
        return is_linux_dark_mode()

def set_windows_dark_titlebar(hwnd, enable=True):
    """Enable or disable immersive dark mode title bar on Windows 10/11"""
    try:
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
        value = ctypes.c_int(1 if enable else 0)
        set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                             ctypes.byref(value), ctypes.sizeof(value))
    except Exception as e:
        print("Could not set dark mode titlebar:", e)

def update_windows_titlebar(window):
    if sys.platform.startswith("win"):
        hwnd = int(window.winId())
        enable = is_windows_dark_mode()
        set_windows_dark_titlebar(hwnd, enable)

# --- THEME ---
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
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, disabled_color)
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_color)

    app.setPalette(dark_palette)

    # Global stylesheet for rounded edges and dark feel
    app.setStyleSheet("""
        QWidget {
            border-radius: 8px;
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QLineEdit, QProgressBar, QListWidget, QDockWidget {
            border-radius: 8px;
            padding: 6px;
            background-color: #3a3a3a;
        }
        QMenu {
            background: rgba(45, 45, 45, 220);
            border: 1px solid #3c3c3c;
            border-radius: 8px;
            padding: 6px;
        }
        QMenu::item {
            padding: 1px 90px 6px 6px;
            color: #f0f0f0;
            font-size: 13px;
            border-radius: 6px;
        }
        QMenu::item:selected {
            background-color: #3d3d3d;
        }
        QMenu::separator {
            height: 1px;
            background: #444;
            margin: 4px 8px;
        }
        QMenu::icon {
            margin-left: 6px;
        }
        QMenu::indicator {
            width: 0px;
            height: 0px;
        }
        QPushButton {
            border-radius: 6px;
            background-color: #444;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: #555;
        }
        QTabBar::tab {
            border-radius: 8px;
            padding: 6px;
            margin: 2px;
        }
        QTabBar::tab:selected {
            background: #555;
        }
    """)

# Download item widget for the manager
class DownloadItem(QWidget):
    def __init__(self, download):
        super().__init__()
        self.download = download

        layout = QHBoxLayout()
        self.label = QLabel(download.suggestedFileName())
        self.progress = QProgressBar()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_download)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.cancel_btn)
        self.setLayout(layout)

        download.downloadProgress.connect(self.on_progress)
        download.finished.connect(self.on_finished)

    def on_progress(self, received, total):
        if total > 0:
            self.progress.setValue(int(received / total * 100))

    def on_finished(self):
        self.progress.setValue(100)
        self.cancel_btn.setDisabled(True)
        QMessageBox.information(self, "Download Finished", f"{self.download.path()} saved!")

    def cancel_download(self):
        self.download.cancel()
        self.progress.setFormat("Canceled")
        self.cancel_btn.setDisabled(True)


from core.bookmarkswidget import *

class WebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
