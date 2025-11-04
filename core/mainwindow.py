# --- MainWindow & Essentials ---
print("7 Running MainWindow")
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

from core.browser import *

# main window
class MainWindow(QMainWindow):

    class WebEnginePage(QWebEnginePage):
        def mouseReleaseEvent(self, event):
            if event.button() == Qt.MiddleButton and hasattr(self, "main_window") and self.main_window:
                try:
                    self.main_window.add_new_tab(self.url())
                except Exception:
                    self.main_window.add_new_tab(QUrl("about:blank"))
            super().mouseReleaseEvent(event)

        def mousePressEvent(self, event):
            super().mousePressEvent(event)
            
        def __init__(self, parent=None, main_window=None):
            super().__init__(parent)
            self.main_window = main_window
            self.loadFinished.connect(self.on_load_finished)
        
        def on_load_finished(self, ok):
            if not ok:
                url = self.url().toString()
                custom_html = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Page Unreachable</title>
                <style>
                /* Reset & global styles */
                * {{
                    margin:0; padding:0; box-sizing:border-box; 
                    font-family:"Segoe UI", Roboto, sans-serif;
                }}
                html {{ font-size:16px; }}
                body {{
                    min-height:100vh;
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    align-items:center;
                    text-align:center;
                    padding:2rem;
                    background:white;
                    color:#080808;
                    transition:background 0.5s, color 0.5s;
                    animation: fadeIn 0.8s ease-in-out;
                }}
                h1, p, footer, a {{
                    -webkit-user-select:none;
                    -moz-user-select:none;
                    -ms-user-select:none;
                    user-select:none;
                }}
                a {{ text-decoration:none; }}
                @keyframes fadeIn {{
                    from {{ opacity:0; transform:translateY(10px); }}
                    to {{ opacity:1; transform:translateY(0); }}
                }}
                h1 {{ font-size:3rem; font-weight:700; margin-bottom:1rem; letter-spacing:0.125rem; }}
                p {{ font-size:1.125rem; margin-bottom:1.5rem; }}
                a.button {{
                    display:inline-block;
                    padding:0.75rem 1.5rem;
                    border-radius:50rem;
                    background:#42a0ff;
                    color:#fff;
                    font-weight:600;
                    transition:0.3s;
                }}
                a.button:hover {{ background:#3390e0; }}
                footer {{ margin-top:2rem; font-size:0.9rem; color:rgba(0,0,0,0.5); }}
                /* Dark mode */
                body.dark-mode {{ background:#1c1c1c; color:#f5f5f5; }}
                body.dark-mode footer {{ color:rgba(255,255,255,0.5); }}
                body.dark-mode a.button {{ background:#42a0ff; color:#fff; }}
                body.dark-mode a.button:hover {{ background:#3390e0; }}
                /* Logo */
                .logo {{ width:120px; margin-bottom:2rem; pointer-events:none; }}
                .logo img {{ width:100%; height:auto; display:block; }}
                </style>
                </head>
                <body>

                <h1>Oops!</h1>
                <p>The page <strong>{url}</strong> could not be loaded.</p>
                <a href="local://home" class="button">Go Home</a>
                <footer>© Noxe Browser 2025</footer>

                <script>
                    if(window.matchMedia('(prefers-color-scheme: dark)').matches) {{
                        document.body.classList.add('dark-mode');
                    }}
                </script>
                </body>
                </html>
                """
                self.setHtml(custom_html, QUrl("about:blank"))


        def acceptNavigationRequest(self, url, _type, isMainFrame):
            if _type == QWebEnginePage.NavigationTypeLinkClicked:
                modifiers = QApplication.keyboardModifiers()
                buttons = QApplication.mouseButtons()

                # Ctrl + click opens new tab
                if modifiers & Qt.ControlModifier:
                    if self.main_window:
                        self.main_window.add_new_tab(url)
                    return False

                # Middle-click opens new tab
                if buttons & Qt.MiddleButton:
                    if self.main_window:
                        self.main_window.add_new_tab(url)
                    return False

            return super().acceptNavigationRequest(url, _type, isMainFrame)

        def handle_feature_permission_request(self, origin, feature):
            if feature == QWebEnginePage.Geolocation:
                self.setFeaturePermission(origin, feature, QWebEnginePage.PermissionDeniedByUser)

    # --- history ---
    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def update_history_list(self):
        self.history_list.clear()
        for h in self.history[-100:]:
            self.history_list.addItem(f'{h["title"]} - {h["url"]}')
            
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        self.update_history_list()


    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
	    # --- Define bookmarks & history file paths first ---

        import os
        import sys

        def get_data_folder():
            if getattr(sys, 'frozen', False):
                # running as exe
                base_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "NoxeBrowser")
            else:
                # running as script
                base_dir = os.path.dirname(os.path.abspath(__file__))

            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            return base_dir

        data_folder = get_data_folder()
        self.bookmarks_file = os.path.join(data_folder, "bookmarks.json")
        self.history_file = os.path.join(data_folder, "history.json")
        self.bookmarks = []
        self.history = []

        # profiles for downloads
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)
        try:
            interceptor = Blocker()
            if hasattr(profile, "setUrlRequestInterceptor"):
                profile.setUrlRequestInterceptor(Blocker())
            elif hasattr(profile, "setRequestInterceptor"):
                profile.setRequestInterceptor(Blocker())
            else:
                print("Warning: Could not set request interceptor on profile.")
        except Exception:
            pass

        try:
            blocker = Blocker()
            profile.setRequestInterceptor(blocker)
        except Exception:
            print("Blocker Interceptor Failed;")

        self.local_scheme_handler = LocalScheme()
        profile.installUrlSchemeHandler(b"local", self.local_scheme_handler)

        # Injecting Parameters from browser for websites
        set_privacy_overrides(profile, dark_mode=is_os_dark_mode())

        # homepage
        self.local_home = "local://home"
        self.local_home_file = os.path.join(os.path.dirname(__file__), "home.html")  # optional, for editing/saving

        # tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)  

        # shortcuts
        QShortcut(QKeySequence("Ctrl+T"), self, activated=self.add_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, activated=lambda: self.close_current_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+R"), self, activated=lambda: self.tabs.currentWidget().reload())
        self.last_closed_tabs = []
        QShortcut(QKeySequence("Ctrl+Shift+T"), self, activated=self.reopen_last_closed_tab)
        QShortcut(QKeySequence("Ctrl+Tab"), self, activated=lambda: self.tabs.setCurrentIndex((self.tabs.currentIndex()+1) % self.tabs.count()))
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, activated=lambda: self.tabs.setCurrentIndex((self.tabs.currentIndex()-1) % self.tabs.count()))
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self.add_bookmark)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=lambda: self.urlbar.setFocus())
        QShortcut(QKeySequence("F11"), self, activated=self.toggle_fullscreen)
        QShortcut(QKeySequence("F12"), self, activated=self.toggle_devtools)

        # status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # navigation toolbar
        self.navtb = QToolBar("Navigation")
        self.addToolBar(self.navtb)

        self.navtb.setStyleSheet("""
        QToolButton {
            border: none;
            padding: 4px;
        }
        QToolButton:hover {
            background-color: rgba(255,255,255,0.1);
            border-radius: 4px;
        }
        QToolButton:pressed {
            background-color: rgba(255,255,255,0.2);
        }
        """)

        back_btn = QAction(QIcon('./img/back.svg'), '', self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.navtb.addAction(back_btn)

        next_btn = QAction(QIcon('./img/forward.svg'), '', self)
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.navtb.addAction(next_btn)

        tab_btn = QAction(QIcon('./img/add.svg'), '', self)
        tab_btn.triggered.connect(lambda: self.add_new_tab())
        self.navtb.addAction(tab_btn)

        reload_btn = QAction(QIcon('./img/reload.svg'), '', self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.navtb.addAction(reload_btn)

        home_btn = QAction(QIcon('./img/home.svg'), '', self)
        home_btn.triggered.connect(self.navigate_home)
        self.navtb.addAction(home_btn)
        self.navtb.addSeparator()

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.navtb.addWidget(self.urlbar)

        stop_btn = QAction("Stop", self)
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        self.navtb.addAction(stop_btn)

        # Download Manager Dock
        self.download_dock = QDockWidget("Downloads", self)
        self.download_dock.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        self.download_container = QWidget()
        self.download_layout = QVBoxLayout()
        self.download_container.setLayout(self.download_layout)
        self.download_dock.setWidget(self.download_container)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.download_dock)

        # Bookmarks Dock
        self.bookmarks_dock = QDockWidget("Bookmarks", self)
        self.bookmarks_list = BookmarkListWidget(self, self.bookmarks_dock)
        self.bookmarks_list.setSelectionMode(QListWidget.SingleSelection)
        self.bookmarks_list.setDragDropMode(QListWidget.InternalMove)
        self.bookmarks_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.bookmarks_list.customContextMenuRequested.connect(self.bookmark_context_menu)
        self.bookmarks_list.itemDoubleClicked.connect(self.open_bookmark)
        self.bookmarks_dock.setWidget(self.bookmarks_list)
        self.bookmarks_list.setAcceptDrops(True)
        self.addDockWidget(Qt.RightDockWidgetArea, self.bookmarks_dock)
        self.load_bookmarks()

        # History Dock
        self.history_dock = QDockWidget("History", self)
        self.history_list = QListWidget()
        self.history_dock.setWidget(self.history_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.history_dock)
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.history_context_menu)

        
        # First load history from file
        self.load_history()
        # Then update the list widget
        self.update_history_list()

        # Settings Dropdown
        self.settings_btn = QPushButton("⁝")
        self.settings_btn.setFixedSize(40, 30)
        self.navtb.addWidget(self.settings_btn)
        self.menu = QMenu()
        self.dl_action = QAction("Downloads", self, checkable=True, checked=True)
        self.bm_action = QAction("Bookmarks", self, checkable=True, checked=True)
        self.history_action = QAction("History", self, checkable=True, checked=True)
        self.menu.addAction(self.dl_action)
        self.menu.addAction(self.bm_action)
        self.menu.addAction(self.history_action)
        self.settings_btn.setMenu(self.menu)
        self.dl_action.toggled.connect(self.toggle_downloads)
        self.bm_action.toggled.connect(self.toggle_bookmarks)
        self.history_action.toggled.connect(self.toggle_history)

        # load tabs
        load_tab_order(self)

        # create first tab
        if self.tabs.count() == 0:
            self.add_new_tab(QUrl("local://home"), "Home")

        # load settings 
        self.load_settings()

        # show window
        self.show()
        self.showMaximized()
        self.setWindowTitle("Noxe Browser")
        icon = QIcon("core/icon.ico")
        self.setWindowIcon(icon)
        if sys.platform.startswith("win"):
            import ctypes
            app_id = u"noxe.browser.1.6"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        profile.setCachePath("./browser/cache")
        profile.setPersistentStoragePath("./browser/storage")
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.6723.91 Safari/537.36 Noxe/1.6"
        )
        profile.setHttpCacheMaximumSize(1024 * 1024 * 1024)
        profile.settings().setAttribute(QWebEngineSettings.DnsPrefetchEnabled, False)
        profile.settings().setAttribute(QWebEngineSettings.WebGLEnabled, True)
        profile.settings().setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        profile.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        profile.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        
        profile.setSpellCheckEnabled(False)
        profile.setHttpAcceptLanguage("en-US,en;q=0.9")
        profile.setHttpUserAgent(profile.httpUserAgent() + " +Brotli/HTTP2")

        view = QWebEngineView()
        view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)

        QTimer.singleShot(200, lambda: self.tabs.currentWidget().resize(
        self.tabs.currentWidget().parentWidget().size()))


    # --- history context menu ---
    def history_context_menu(self, pos):
        item = self.history_list.itemAt(pos)
        menu = QMenu()

        # Add actions
        delete_all_action = QAction("Delete All History", self)
        delete_all_action.triggered.connect(self.delete_all_history)
        menu.addAction(delete_all_action)

        if item:
            delete_item_action = QAction("Delete This Entry", self)
            delete_item_action.triggered.connect(lambda: self.delete_history_item(item))
            menu.addAction(delete_item_action)

        delete_7days_action = QAction("Delete Last 7 Days", self)
        delete_7days_action.triggered.connect(lambda: self.delete_history_days(7))
        menu.addAction(delete_7days_action)

        delete_30days_action = QAction("Delete Last 30 Days", self)
        delete_30days_action.triggered.connect(lambda: self.delete_history_days(30))
        menu.addAction(delete_30days_action)

        # Show menu
        menu.exec_(self.history_list.mapToGlobal(pos))
        
	# --- delete helpers ---
    def delete_all_history(self):
        self.history.clear()
        self.save_history()
        self.update_history_list()
        
    def delete_history_item(self, item):
        url_text = item.text().split(" - ", 1)[1]
        self.history = [h for h in self.history if h["url"] != url_text]
        self.save_history()
        self.update_history_list()
        
    def delete_history_days(self, days):
        try:
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=days)
            # Keep items older than cutoff (i.e. delete the last `days` entries)
            self.history = [h for h in self.history if "timestamp" in h and datetime.fromisoformat(h["timestamp"]) < cutoff]
            self.save_history()
            self.update_history_list()
        except Exception as e:
            print("delete_history_days failed:", e)

        
    # --- SETTINGS PERSISTENCE ---
    def load_settings(self):
        """Load settings from file."""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
            dl = settings.get("downloads_visible", True)
            bm = settings.get("bookmarks_visible", True)
            h = settings.get("history_visible", True)
        else:
            dl, bm, h = False, False, False

        self.dl_action.setChecked(dl)
        self.bm_action.setChecked(bm)
        self.history_action.setChecked(h)
        self.download_dock.setVisible(dl)
        self.bookmarks_dock.setVisible(bm)
        self.history_dock.setVisible(h)

    def save_settings(self):
        """Save settings to file."""
        settings = {
            "downloads_visible": self.dl_action.isChecked(),
            "bookmarks_visible": self.bm_action.isChecked(),
            "history_visible": self.history_action.isChecked()
        }
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        
    # --- docks ---
    def toggle_downloads(self, enabled):
        self.download_dock.setVisible(enabled)
        self.save_settings()

    def toggle_bookmarks(self, enabled):
        self.bookmarks_dock.setVisible(enabled)
        self.save_settings()
    
    def toggle_history(self, enabled):
        self.history_dock.setVisible(enabled)
        self.save_settings()

    # --- tabs ---
    def add_new_tab(self, qurl=None, label="New Tab"):

        browser = QWebEngineView()
        patch_js = """
        if (window.matchMedia) {
            const mq = window.matchMedia('(prefers-color-scheme: dark)');
            if (!mq.addEventListener) { mq.addEventListener = mq.addListener; }
        }
        """
        browser.page().runJavaScript(patch_js)
        browser.setAttribute(Qt.WA_OpaquePaintEvent, False)
        browser.setUpdatesEnabled(True)

        page = MainWindow.WebEnginePage(parent=browser, main_window=self)
        browser.setPage(page)
        page.featurePermissionRequested.connect(page.handle_feature_permission_request)
        
        browser.setParent(self)
        browser.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        browser.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        browser.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        browser.setContentsMargins(0, 0, 0, 0)

        browser.page().runJavaScript("""
            document.documentElement.style.scrollBehavior = 'smooth';
        """)


        browser.iconChanged.connect(lambda icon, browser=browser: self.update_tab_icon(browser, icon))

        if qurl is None or isinstance(qurl, bool):
            qurl = QUrl(self.local_home)
        browser.setUrl(qurl)

        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(browser)
        container.setLayout(layout)

        browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        browser.setMinimumSize(0, 0)
        browser.setContentsMargins(0, 0, 0, 0)

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # --- CONNECT SIGNALS ---
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.title()))
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda ok, browser=browser: self.track_history(browser))
        browser.page().titleChanged.connect(lambda title, browser=browser: self.update_tab_title(title, browser))
    
        return browser


    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title)
        # update window title if this is current tab
        if browser == self.tabs.currentWidget():
            self.setWindowTitle(f"{title} - Noxe Browser")

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(f"{title} - Noxe Browser")
      
    def track_history(self, browser):
        url = browser.url().toString()
        title = browser.page().title()
        from datetime import datetime
        if not self.history or self.history[-1]["url"] != url or self.history[-1]["title"] != title:
            entry = {
                "title": title,
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
            self.history.append(entry)
            self.save_history()
            self.update_history_list()




    # --- navigation ---
    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("local://home"))


    def navigate_to_url(self):
        text = self.urlbar.text()
        q = QUrl(text)
        if q.scheme() == "":
            if "." in text:
                q.setScheme("http")
            else:
                # treat it as a search
                q = QUrl(f"https://google.com/search?q={text}")
        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def reopen_last_closed_tab(self):
        if self.last_closed_tabs:
            url, title = self.last_closed_tabs.pop()
            self.add_new_tab(QUrl(url), title)

    # --- bookmarks ---
    def add_bookmark(self):
        browser = self.tabs.currentWidget()
        url = browser.url().toString()
        title = browser.page().title()

        if not any(b["url"] == url for b in self.bookmarks):
            self.bookmarks.append({"title": title, "url": url})
            self.bookmarks_list.addItem(f"{title} - {url}")
            self.save_bookmarks()  # save only once
            

    def open_bookmark(self, item):
        url = item.text().split(" - ", 1)[1]
        self.tabs.currentWidget().setUrl(QUrl(url))

    def bookmark_context_menu(self, pos):
        item = self.bookmarks_list.itemAt(pos)
        if not item:
            return
        menu = QMenu()
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_bookmark(item))
        menu.addAction(delete_action)
        menu.exec_(self.bookmarks_list.mapToGlobal(pos))

    def delete_bookmark(self, item):
        index = self.bookmarks_list.row(item)
        self.bookmarks_list.takeItem(index)
        url_text = item.text().split(" - ", 1)[1]
        url_norm = QUrl(url_text).toString()  # normalize
        self.bookmarks = [b for b in self.bookmarks if QUrl(b["url"]).toString() != url_norm]
        self.save_bookmarks()

    def load_bookmarks(self):
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, "r") as f:
                self.bookmarks = json.load(f)
        self.bookmarks_list.clear()
        for b in self.bookmarks:
            self.bookmarks_list.addItem(f'{b["title"]} - {b["url"]}')

    def save_bookmarks(self):
        # always overwrite bookmarks.json, even if empty
        with open(self.bookmarks_file, "w", encoding="utf-8") as f:
            json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)


    # --- fullscreen & devtools ---
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def toggle_devtools(self):
        browser = self.tabs.currentWidget()
        browser.page().runJavaScript("console.log('prefers-color-scheme dark:', window.matchMedia('(prefers-color-scheme: dark)').matches);")
        if hasattr(browser, 'devtools') and browser.devtools.isVisible():
            browser.devtools.close()
            return
        else:
            browser.devtools = QWebEngineView()
        
        browser.page().setDevToolsPage(browser.devtools.page())
        browser.devtools.show()
        
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
                q.setQuery("")
                q.setFragment("")
                url_norm = q.toString()
                if not any(QUrl(b["url"]).toString() == url_norm for b in self.bookmarks):
                    title = url_norm
                    self.bookmarks.append({"title": title, "url": url_norm})
                    self.bookmarks_list.addItem(f"{title} - {url_norm}")
            self.save_bookmarks()
            event.acceptProposedAction()
        else:
            event.ignore()

    # --- downloads ---
    def handle_download(self, download):
        filename = download.suggestedFileName()
        ext = os.path.splitext(filename)[1]
        if not ext:
            mime_part = download.mimeType().split('/')[-1] if download.mimeType() else ""
            mime_ext = ''.join(ch for ch in mime_part if ch.isalnum())
            if mime_ext:
                ext = f".{mime_ext}"
                filename += ext

        path, _ = QFileDialog.getSaveFileName(self, "Save File", filename, f"{ext.upper()} Files (*{ext});;All Files (*.*)")
        if not path:
            # user cancelled, cancel the download
            try:
                download.cancel()
            except Exception:
                pass
            return

        if not os.path.splitext(path)[1] and ext:
            path += ext

        try:
            download.setPath(path)
            download.accept()
            item = DownloadItem(download)
            self.download_layout.addWidget(item)
        except Exception as e:
            print("Download failed:", e)
            try:
                download.cancel()
            except Exception:
                pass
      
    # --- save on exit ---
    def closeEvent(self, event):
        try:
            self.save_bookmarks()   # save bookmarks before closing
            self.save_settings()    # save settings before closing
            self.save_history()     # save history before closing
            save_tab_order(self)        # save tab order before closing
            print("exitting with normal save;")
        except Exception:
            print("exitting with bad save;")

        try:
            cleanup_cache()
        except Exception:
            print("Failed to cleanup cache on exit;")

        event.accept()

    def update_tab_icon(self, browser, icon):
        index = self.tabs.indexOf(browser)
        if index != -1:
            if not icon.isNull():
                self.tabs.setTabIcon(index, icon)

    def showEvent(self, event):
        super().showEvent(event)
        if sys.platform.startswith("win"):
            update_windows_titlebar(self)