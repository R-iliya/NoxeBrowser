# mainwindow.py - Main window and core functionality of Noxe Browser, including tabs, navigation, history, bookmarks, AI assistant, and settings management.

# importing required libraries
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import sys
import os

from core.browser import *

# MainWindow class including Major parts of the code. 
class MainWindow(QMainWindow):

    class WebEnginePage(QWebEnginePage):
        # The init for web engine page.
        def __init__(self, profile, main_window=None):
            super().__init__(profile)
            self.main_window = main_window
            self.loadFinished.connect(self.on_load_finished)
        
        # Function for when loading a page is finished.
        def on_load_finished(self, ok):
            if not ok:
                url = self.url().toString()

        # Accept navigation requests.
        def acceptNavigationRequest(self, url, _type, isMainFrame):
            if _type == QWebEnginePage.NavigationTypeLinkClicked:
                modifiers = QApplication.keyboardModifiers()
                buttons = QApplication.mouseButtons()

                if modifiers & Qt.ControlModifier:
                    if self.main_window:
                        self.main_window.add_new_tab(url)
                    return False

                if buttons & Qt.MiddleButton:
                    if self.main_window:
                        self.main_window.add_new_tab(url)
                    return False

                return True
            
            return super().acceptNavigationRequest(url, _type, isMainFrame)

        # Handle permission requests for browser.
        def handle_feature_permission_request(self, origin, feature):
            if feature == QWebEnginePage.Geolocation:
                self.setFeaturePermission(origin, feature, QWebEnginePage.PermissionDeniedByUser)

    # ----- History -----

    # Save history as a json file.
    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    # Update history list through additem.
    def update_history_list(self):
        self.history_list.clear()
        for h in self.history[-100:]:
            self.history_list.addItem(f'{h["title"]} - {h["url"]}')

    # Load history and update history list.
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        self.update_history_list()

    # Init for the main window.
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
	    # Define bookmarks & history file paths first

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

        # Set profiles including the normal and private profiles.
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)

        self.normal_profile = QWebEngineProfile.defaultProfile()
        self.private_profile = QWebEngineProfile(None)
        self.private_profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.private_profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.is_private = False

        # Interceptor blocker request.
        interceptor = Blocker()
        if hasattr(profile, 'setUrlRequestInterceptor'):
            profile.setUrlRequestInterceptor(interceptor)
        elif hasattr(profile, 'setRequestInterceptor'):
            profile.setRequestInterceptor(interceptor)
        else:
            print("No request interceptor method available — adblock dead")

        self.local_scheme_handler = LocalScheme()
        profile.installUrlSchemeHandler(b"local", self.local_scheme_handler)

        # Injecting Parameters from browser for websites.
        set_privacy_overrides(profile, dark_mode=is_os_dark_mode())

        # Set up Homepage.
        self.local_home = "local://home"
        self.local_home_file = os.path.join(os.path.dirname(__file__), "home.html")  # optional, for editing/saving

        # Set up the tabs widget.
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)  

        # Set up the shortcuts and their actions.
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

        # Set up the status bar.
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Set up the navigation toolbar.
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

        # Set up the back button on the navigation toolbar.
        back_btn = QAction(QIcon('./img/back.svg'), '', self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.navtb.addAction(back_btn)

        # Set up the next button on the navigation toolbar.
        next_btn = QAction(QIcon('./img/forward.svg'), '', self)
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.navtb.addAction(next_btn)

        # Set up the add new tab button on the navigation toolbar.
        tab_btn = QAction(QIcon('./img/add.svg'), '', self)
        tab_btn.triggered.connect(lambda: self.add_new_tab())
        self.navtb.addAction(tab_btn)

        # Set up the reload button on the navigation toolbar.
        reload_btn = QAction(QIcon('./img/reload.svg'), '', self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.navtb.addAction(reload_btn)

        # Set up the home button on the navigation toolbar.
        home_btn = QAction(QIcon('./img/home.svg'), '', self)
        home_btn.triggered.connect(self.navigate_home)
        self.navtb.addAction(home_btn)

        self.navtb.addSeparator()

        # Set up the URL bar on the navigation toolbar.
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.navtb.addWidget(self.urlbar)

        # Set up the stop button on the navigation toolbar.
        stop_btn = QAction("Stop", self)
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        self.navtb.addAction(stop_btn)

        # AI Chat Dock.
        self.ai_dock = QDockWidget("Noxe AI Assistant", self)
        self.ai_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.ai_dock.setFixedWidth(350)
        self.ai_dock.setStyleSheet("""
            QDockWidget {
                background-color: #1e1e2f;
                border: 2px solid #3a3a5a;
                border-radius: 10px;
            }
        """)
        

        # Set up the AI Widget as a QWidget.
        self.ai_widget = QWidget()
        self.ai_layout = QVBoxLayout()
        self.ai_layout.setSpacing(5)
        self.ai_widget.setLayout(self.ai_layout)

        # Scroll area for chat bubbles.
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_container.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_container)

        # Input text box for the AI Chat.
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Ask NoxeAI…")
        self.ai_input.returnPressed.connect(self.send_ai_query)

        self.ai_layout.addWidget(self.chat_scroll)
        self.ai_layout.addWidget(self.ai_input)

        self.ai_dock.setWidget(self.ai_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.ai_dock)
        self.ai_dock.setVisible(True)

        # AI Toggle Button that toggles visiblity of the AI chat dock.
        toggle_ai_btn = QAction("AI", self)
        toggle_ai_btn.setCheckable(True)
        toggle_ai_btn.setChecked(True)
        toggle_ai_btn.triggered.connect(lambda checked: self.ai_dock.setVisible(checked))
        self.navtb.addAction(toggle_ai_btn)

        # Title bar for the AI chat dock.
        self.ai_dock.setTitleBarWidget(QWidget())
        title = QLabel("NoxeAI 🌀")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #4b8bf5;
                font-weight: bold;
                font-size: 14pt;
            }
        """)
        self.ai_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border-radius: 10px;
                border: 2px solid #3a3a5a;
                background-color: #2b2b3b;
                color: #eee;
            }
            QLineEdit:focus {
                border: 2px solid #4b8bf5;
                background-color: #353545;
            }
        """)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.setContentsMargins(5, 2, 5, 2)
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        self.ai_dock.setTitleBarWidget(header_widget)




        # Download Manager Dock.
        self.download_dock = QDockWidget("Downloads", self)
        self.download_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.download_dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )
        self.download_container = QWidget()
        self.download_layout = QVBoxLayout()
        self.download_layout.setAlignment(Qt.AlignTop)
        self.download_container.setLayout(self.download_layout)
        self.download_dock.setWidget(self.download_container)
        self.addDockWidget(Qt.RightDockWidgetArea, self.download_dock)
        self.download_dock.setFloating(True)
        self.download_dock.resize(700, 140)
        self.download_dock.setTitleBarWidget(QWidget())

        self.download_dock.hide()  # hide on start
        
        # Install event filter. Later used for interacting with visiblity of the Download Manager Dock.
        QApplication.instance().installEventFilter(self)

        # Bookmarks Dock.
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

        # History Dock.
        self.history_dock = QDockWidget("History", self)
        self.history_list = QListWidget()
        self.history_dock.setWidget(self.history_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.history_dock)
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.history_context_menu)

        
        # First load history from file.
        self.load_history()
        # Next update the list widget.
        self.update_history_list()

        # Settings Dropdown.
        self.settings_btn = QPushButton("⁝")
        self.settings_btn.setFixedSize(40, 30)
        self.navtb.addWidget(self.settings_btn)
        self.menu = QMenu()

        # Add Startup visiblity options to the Settings Dropdown.
        self.dl_action = QAction("Downloads", self, checkable=True, checked=True)
        self.bm_action = QAction("Bookmarks", self, checkable=True, checked=True)
        self.history_action = QAction("History", self, checkable=True, checked=True)
        self.ai_action = QAction("AI Assistant", self, checkable=True, checked=True)

        # Add AI Settings sub menu to the Settings Dropdown.
        self.ai_menu = QMenu("AI Settings", self)
        self.ai_clear_action = QAction("Clear Chat", self)
        self.ai_float_action = QAction("Float Window", self)

        # Add Private Session option to the Settings Dropdown.
        self.private_action = QAction("Private Session", self, checkable=True)

        # Add options to the AI Settings sub menu.
        self.ai_menu.addSeparator()
        self.ai_menu.addAction(self.ai_clear_action)
        self.ai_menu.addAction(self.ai_float_action)

        # Add options to the Settings Dropdown.
        self.menu.addAction(self.dl_action)
        self.menu.addAction(self.bm_action)
        self.menu.addAction(self.history_action)
        self.menu.addSeparator()
        self.menu.addAction(self.ai_action)

        # Add AI Settings sub menu to the Settings Dropdown.
        self.menu.addMenu(self.ai_menu)

        # Add Private Session option to the Settings Dropdown.
        self.menu.addSeparator()
        self.menu.addAction(self.private_action)

        # Connect the actions to their respective functions and set the menu for the settings button.
        self.settings_btn.setMenu(self.menu)
        self.dl_action.toggled.connect(self.toggle_downloads)
        self.bm_action.toggled.connect(self.toggle_bookmarks)
        self.history_action.toggled.connect(self.toggle_history)
        self.ai_action.toggled.connect(self.toggle_ai_dock)
        self.ai_clear_action.triggered.connect(self.clear_ai_chat)
        self.ai_float_action.triggered.connect(self.float_ai_dock)
        self.private_action.toggled.connect(self.toggle_private_mode)

        # Network manager for handling the AI responses.
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.handle_ai_response)

        # set the normal and private stylesheets.
        self.normal_stylesheet = ""
        self.private_stylesheet = """
            QDockWidget {
                background-color: #111115;
                border: 2px solid #22222e;
                border-radius: 8px;
            }

            QWidget {
                background-color: #0d0d12;
                color: #e4e4e4;
            }

            QLineEdit {
                background-color: #15151c;
                border: 1px solid #2a2a35;
                padding: 6px;
                border-radius: 6px;
                color: #ffffff;
            }

            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: #0f0f14;
                width: 8px;
                margin: 4px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: #2a2a35;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical:hover {
                background: #3a3a48;
            }
            """

        # Load tabs from stored file.
        self.load_tab_order()

        # If no tabs avaible, create the first tab.
        if self.tabs.count() == 0:
            self.add_new_tab(QUrl("local://home"), "Home")

        # Load settings from stored file.
        self.load_settings()

        # Show the browser's window.
        self.setWindowTitle("Noxe Browser")
        self.showMaximized()
        icon = QIcon("core/icon.ico")
        self.setWindowIcon(icon)
        if sys.platform.startswith("win"):
            import ctypes
            app_id = u"noxe.browser.1.6"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        # Set profile's settings.
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

        self.profile = profile

        self.download_dock.hide()

    # Toggle AI Chat Dock.
    def toggle_ai_dock(self, enabled):
        self.ai_dock.setVisible(enabled)
        self.save_settings()

    # Clear AI Chat's history.
    def clear_ai_chat(self):
        self.chat_container.deleteLater()

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_container.setLayout(self.chat_layout)

        self.chat_scroll.setWidget(self.chat_container)

    # Float AI Chat Dock.
    def float_ai_dock(self):
        self.ai_dock.setFloating(True)

    # Toggle the Private Session.
    def toggle_private_mode(self, enabled):
        self.is_private = enabled

        if enabled:
            self.setWindowTitle("Noxe Browser — Private Mode")
            self.setStyleSheet(self.private_stylesheet)
            self.status.showMessage("Private session active — nothing will be saved.", 3000)
        else:
            self.setWindowTitle("Noxe Browser")
            self.setStyleSheet(self.normal_stylesheet)
            self.status.showMessage("Private session disabled.", 2000)


    # History Context Menu.
    def history_context_menu(self, pos):
        item = self.history_list.itemAt(pos)
        menu = QMenu()

        # Add actions.
        delete_all_action = QAction("Delete All History", self)
        delete_all_action.triggered.connect(self.delete_all_history)
        menu.addAction(delete_all_action)

        # Delete the entry selected.
        if item:
            delete_item_action = QAction("Delete This Entry", self)
            delete_item_action.triggered.connect(lambda: self.delete_history_item(item))
            menu.addAction(delete_item_action)

        # Delete entries from the last 7 days.
        delete_7days_action = QAction("Delete Last 7 Days", self)
        delete_7days_action.triggered.connect(lambda: self.delete_history_days(7))
        menu.addAction(delete_7days_action)

        # Delete entries from the last 30 days.
        delete_30days_action = QAction("Delete Last 30 Days", self)
        delete_30days_action.triggered.connect(lambda: self.delete_history_days(30))
        menu.addAction(delete_30days_action)

        # Show menu.
        menu.exec_(self.history_list.mapToGlobal(pos))
        
	# Delete all history items.
    def delete_all_history(self):
        self.history.clear()
        self.save_history()
        self.update_history_list()
        
    # Delete history item.
    def delete_history_item(self, item):
        url_text = item.text().split(" - ", 1)[1]
        self.history = [h for h in self.history if h["url"] != url_text]
        self.save_history()
        self.update_history_list()
        
    # Delete history items by days.
    def delete_history_days(self, days):
        try:
            from datetime import datetime, timedelta
            now = datetime.now()
            cutoff = now - timedelta(days=days)
            self.history = [
                h for h in self.history
                if "timestamp" not in h or datetime.fromisoformat(h["timestamp"]) <= cutoff
            ]
            self.save_history()
            self.update_history_list()
        except Exception as e:
            print(f"delete_history_days({days}) failed: {e}")

        
    # Load settings from stored json file.
    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
            dl = settings.get("downloads_visible", True)
            bm = settings.get("bookmarks_visible", True)
            h = settings.get("history_visible", True)
            ai = settings.get("ai_visible", True)
            force_dark = settings.get("force_dark_mode", False)
        else:
            dl, bm, h, ai, force_dark = True, True, True, True, False

        # Apply visibility.
        self.download_dock.setVisible(dl)
        self.bookmarks_dock.setVisible(bm)
        self.history_dock.setVisible(h)
        self.ai_dock.setVisible(ai)

        # Sync quick dropdown toggles.
        self.dl_action.setChecked(dl)
        self.bm_action.setChecked(bm)
        self.hist_action.setChecked(h)
        self.ai_action.setChecked(ai)

        # Apply force dark.
        set_privacy_overrides(self.profile, dark_mode=force_dark)

    # Save settings to json file.
    def save_settings(self):
        """Save settings to file."""
        settings = {
            "bookmarks_visible": self.bm_action.isChecked(),
            "history_visible": self.history_action.isChecked(),
            "ai_visible": self.ai_action.isChecked()
        }
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        
    # Toggle Downloads Dock.
    def toggle_downloads(self, enabled):
        self.download_dock.setVisible(enabled)
        self.save_settings()

    # Set positions for the Downloads Dock.
    def position_download_dock(self):
        if not self.download_dock.isFloating():
            return

        margin = 20
        dock_width = self.download_dock.width()
        dock_height = self.download_dock.height()

        window_geo = self.frameGeometry()
        x = window_geo.x() + window_geo.width() - dock_width - margin
        y = window_geo.y() + 80  # below titlebar

        self.download_dock.move(x, y)

    # EventFilter for visiblity of the Download Dock.
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.download_dock.isVisible():
                if not self.download_dock.geometry().contains(event.globalPos()):
                    self.download_dock.hide()
        return super().eventFilter(obj, event)

    # Toggle Bookmarks Dock.
    def toggle_bookmarks(self, enabled):
        self.bookmarks_dock.setVisible(enabled)
        self.save_settings()
    
    # Toggle History Dock.
    def toggle_history(self, enabled):
        self.history_dock.setVisible(enabled)
        self.save_settings()

    # ----- Tabs -----
    # Add new tab.
    def add_new_tab(self, qurl=None, label="New Tab"):

        browser = QWebEngineView()

        # Check if in Private Session as sets the page.
        if self.is_private:
            page = MainWindow.WebEnginePage(self.private_profile, self)
        else:
            page = MainWindow.WebEnginePage(self.normal_profile, self)

        patch_js = """
        if (window.matchMedia) {
            const mq = window.matchMedia('(prefers-color-scheme: dark)');
            if (!mq.addEventListener) { mq.addEventListener = mq.addListener; }
        }
        """

        browser.page().runJavaScript(patch_js)
        browser.setAttribute(Qt.WA_OpaquePaintEvent, False)
        browser.setUpdatesEnabled(True)

        browser.setPage(page)
        page.featurePermissionRequested.connect(page.handle_feature_permission_request)
        
        # Set the Browser's Settings.
        browser.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        browser.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        browser.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        browser.setContentsMargins(0, 0, 0, 0)

        # Smooth the scrollbar behavior. 
        browser.page().runJavaScript("""
            document.documentElement.style.scrollBehavior = 'smooth';
        """)

        browser.iconChanged.connect(lambda icon, browser=browser: self.update_tab_icon(browser, icon))

        if qurl is None or isinstance(qurl, bool):
            qurl = QUrl(self.local_home)
        browser.setUrl(qurl)

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # Browser Connection signals.
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.title()))
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda ok, browser=browser: self.track_history(browser))
        browser.page().titleChanged.connect(lambda title, browser=browser: self.update_tab_title(title, browser))
    
        return browser

    # Update tab title.
    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title)
        # update window title if this is current tab
        if browser == self.tabs.currentWidget():
            self.setWindowTitle(f"{title} - Noxe Browser")

    # Tab open behavior through doubleclick.
    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    # Update URLBar and title from current tab.
    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    # Close current tab.
    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        browser = self.tabs.widget(i)
        url = browser.url().toString()
        title = browser.title() or "Untitled"
        self.last_closed_tabs.append((url, title))
        if len(self.last_closed_tabs) > 20:
            self.last_closed_tabs.pop(0)
        self.tabs.removeTab(i)

    # Update the title bar.
    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(f"{title} - Noxe Browser")
      
    # Track history and save.
    def track_history(self, browser):
        if self.is_private:
            return
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

    # ----- Navigations -----

    # Navigate to home.
    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("local://home"))

    # Navigate to URL from URLBar. Also detects if the text in URLBar is a link or a search.
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

    # Update the URLBar's text to current URL.
    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def reopen_last_closed_tab(self):
        if self.last_closed_tabs:
            url, title = self.last_closed_tabs.pop()
            self.add_new_tab(QUrl(url), title)

    # ----- Bookmarks -----

    # Add the given URL as a Bookmark and saves.
    def add_bookmark(self):
        browser = self.tabs.currentWidget()
        url = browser.url().toString()
        title = browser.page().title()

        if not any(b["url"] == url for b in self.bookmarks):
            self.bookmarks.append({"title": title, "url": url})
            self.bookmarks_list.addItem(f"{title} - {url}")
            self.save_bookmarks()  # save only once
            
    # Open the selected Bookmark on tab.
    def open_bookmark(self, item):
        url = item.text().split(" - ", 1)[1]
        self.tabs.currentWidget().setUrl(QUrl(url))

    # Context menu for Bookmarks.
    def bookmark_context_menu(self, pos):
        item = self.bookmarks_list.itemAt(pos)
        if not item:
            return
        menu = QMenu()
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_bookmark(item))
        menu.addAction(delete_action)
        menu.exec_(self.bookmarks_list.mapToGlobal(pos))

    #  Delete Selected Bookmark.
    def delete_bookmark(self, item):
        index = self.bookmarks_list.row(item)
        self.bookmarks_list.takeItem(index)
        url_text = item.text().split(" - ", 1)[1]
        url_norm = QUrl(url_text).toString()  # normalize
        self.bookmarks = [b for b in self.bookmarks if QUrl(b["url"]).toString() != url_norm]
        self.save_bookmarks()

    # Load Bookmarks from stored json file.
    def load_bookmarks(self):
        if os.path.exists(self.bookmarks_file):
            with open(self.bookmarks_file, "r") as f:
                self.bookmarks = json.load(f)
        self.bookmarks_list.clear()
        for b in self.bookmarks:
            self.bookmarks_list.addItem(f'{b["title"]} - {b["url"]}')

    # Save Bookmarks to json file.
    def save_bookmarks(self):
        # always overwrite bookmarks.json, even if empty
        with open(self.bookmarks_file, "w", encoding="utf-8") as f:
            json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)

    # ----- AI Assistant -----

    # Send AI Query if prompt avaible. Uses Dock's Input text box's text as prompt.
    def send_ai_query(self):
        prompt = self.ai_input.text().strip()
        if not prompt:
            return

        # Clears the input text box after send.
        self.ai_input.clear()
        self.add_user_bubble(prompt)

        key = os.environ.get("GAPGPT_KEY")
        if not key:
            self.add_ai_bubble("<error> API key not found")
            return

        current_url = self.tabs.currentWidget().url().toString()
        body = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": f"You are NoxeAI, a helpful AI assistant embedded in a browser. Current page URL: {current_url}."},
                {"role": "user", "content": prompt}
            ]
        }

        url = QUrl("https://api.gapgpt.app/v1/chat/completions")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        request.setRawHeader(b"Authorization", f"Bearer {key}".encode())

        data = QByteArray(json.dumps(body).encode("utf-8"))
        self.network_manager.post(request, data)

    # Handle AI responses.
    def handle_ai_response(self, reply):
        raw = bytes(reply.readAll()).decode("utf-8")
        if reply.error():
            self.add_ai_bubble(f"<error> {reply.errorString()}")
            print("RAW ERROR RESPONSE:", raw)
            return

        data = json.loads(raw)
        try:
            response_text = data["choices"][0]["message"]["content"]
        except Exception:
            response_text = str(data)

        self.add_ai_bubble(response_text)


    # Chat bubble helpers
    def add_user_bubble(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            QLabel {
                background-color: #4b8bf5;
                color: white;
                padding: 6px 10px;
                border-radius: 12px;
                max-width: 250px;
            }
        """)
        lbl.setWordWrap(True)
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(lbl)
        self.chat_layout.addLayout(hbox)
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())

    # Add AI Bubble.
    def add_ai_bubble(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            QLabel {
                background-color: #2e2e3e;
                color: #eee;
                padding: 6px 10px;
                border-radius: 12px;
                max-width: 250px;
            }
        """)
        lbl.setWordWrap(True)
        hbox = QHBoxLayout()
        hbox.addWidget(lbl)
        hbox.addStretch()
        self.chat_layout.addLayout(hbox)
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())
        self.chat_scroll.setStyleSheet("""
            QScrollBar:vertical {
                background: #1e1e2f;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #4b8bf5;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6ba0f8;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                height: 0px;
            }

            QScrollBar:horizontal {
                background: #1e1e2f;
                height: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #4b8bf5;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #6ba0f8;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                width: 0px;
            }
        """)





    # ----- Fullscreen & DevTools -----

    # Toggle fullscreen mode.
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # Toggle DevTools.
    def toggle_devtools(self):
        browser = self.tabs.currentWidget()
        if hasattr(browser, 'devtools'):
            if browser.devtools.isVisible():
                browser.devtools.close()
                return
            else:
                browser.devtools.show()
                return

        # First time
        dev_view = QWebEngineView()
        browser.page().setDevToolsPage(dev_view.page())
        dev_view.show()
        browser.devtools = dev_view  # still keep reference
        
    # Drag Enter Event.
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    # Drag Move Event.
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    # Drag's Drop Event.
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

    # ----- Downloads System -----

    # Handle download.
    def handle_download(self, download):
        # Auto-open download dock
        if not self.download_dock.isVisible():
            self.download_dock.show()
            self.download_dock.setFloating(True)
            self.position_download_dock()
            self.download_dock.raise_()

        filename = download.suggestedFileName()
        ext = os.path.splitext(filename)[1]
        if not ext:
            mime_part = download.mimeType().split('/')[-1] if download.mimeType() else ""
            mime_ext = ''.join(ch for ch in mime_part if ch.isalnum())
            if mime_ext:
                ext = f".{mime_ext}"
                filename += ext

        path, _ = QFileDialog.getSaveFileName(self, "Save File", filename, "...")
        if not path:
            self.status.showMessage("Download canceled", 3000)
            download.cancel()
            return

        if not os.path.splitext(path)[1]:
            path += ext

        try:
            download.setPath(path)
            download.accept()
            item = DownloadItem(download)
            self.download_layout.addWidget(item)
        except Exception as e:
            print("Download failed:", e)
            download.cancel()

    # ----- Tab Save & Load System ---

    # Save Tabs to json file.
    def save_tab_order(self):
        try:
            order = []
            for i in range(self.tabs.count()):
                qurl = self.tabs.widget(i).url()
                url_str = qurl.toString()
                if qurl.isValid() and url_str and "about:" not in url_str and "data:" not in url_str:
                    order.append(url_str)
            with open("tabs.json", "w", encoding="utf-8") as f:
                json.dump(order, f, indent=2)
        except Exception as e:
            print("Failed to save tab order:", e)

    # Load tab orders at startup.
    def load_tab_order(self):
        if os.path.exists("tabs.json"):
            try:
                with open("tabs.json", "r", encoding="utf-8") as f:
                    urls = json.load(f)
                for url in urls:
                    qurl = QUrl(url)
                    if qurl.isValid():
                        # Try to use last known title if you saved it, or just URL
                        label = qurl.toString()[:30] + "..." if len(qurl.toString()) > 30 else qurl.toString()
                        self.add_new_tab(qurl, label)
            except Exception as e:
                print("Failed to load tab order:", e)
      

    # Close event. Saves Bookmarks, Settings, History and Tab order on exit and cleans up cache.
    def closeEvent(self, event):
        try:
            if not self.is_private:
                self.save_bookmarks()   # save bookmarks before closing
                self.save_settings()    # save settings before closing
                self.save_history()     # save history before closing
                self.save_tab_order()    # save tab order before closing
                print("exitting with normal save;")
            else:
                print("exitting without save;")
        except Exception:
            print("exitting with bad save;")
        try:
            cleanup_cache(self.profile)
        except Exception:
            print("Failed to cleanup cache on exit;")

        event.accept()

    # Update tab icon.
    def update_tab_icon(self, browser, icon):
        index = self.tabs.indexOf(browser)
        if index != -1:
            if not icon.isNull():
                self.tabs.setTabIcon(index, icon)

    # Show event to position the download dock and update titlebar on Windows.
    def showEvent(self, event):
        super().showEvent(event)
        self.position_download_dock()
        if sys.platform.startswith("win"):
            update_windows_titlebar(self)
            