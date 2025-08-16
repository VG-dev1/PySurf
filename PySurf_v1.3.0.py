from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QTabWidget, QMenu, QAction, QDialog,
                             QToolButton, QFileDialog, QShortcut, QFrame, QScrollArea, QProgressBar)
from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEngineDownloadItem, QWebEngineProfile,
                                     QWebEngineSettings, QWebEnginePage)
from PyQt5.QtCore import Qt, QTimer, QUrl, QSize, QProcess
from PyQt5.QtGui import QKeySequence, QFont, QCursor, QIcon
import sys, os, json, html
import qtmodern.windows, qtmodern.styles

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-gpu --ignore-gpu-blocklist --enable-smooth-scrolling"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
SHORTCUTS_FILE = "shortcuts.json"
BOOKMARKS_FILE = "bookmarks.json"
HISTORY_FILE = "history.json"
DOWNLOADS_FILE = "downloads.json"

# --- Utility Functions ---

def create_separator():
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    return separator

def load_data(filename, default_data=[]):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default_data
    return default_data

def save_data(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- Global Application and Dialogs (Order Fixed) ---

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("C:/Users/vitoh/PySurf_Dev/PySurf_v1.2.0/PySurf_Icon.ico"))
app.setFont(QFont("Segoe UI"))
qtmodern.styles.light(app)
app.setStyleSheet("""
QPushButton {background-color: #ffffff;color: black;border: none;padding: 8px 16px;border-radius: 6px;}
QPushButton:hover {border: 1px solid #aeb6bf;}
QLineEdit {border: 1px solid #ccc;border-radius: 4px;padding: 6px;}
QTabWidget::pane {border: 1px solid #ccc;border-radius: 4px;}
QTabBar::tab {background: #ecf0f1;padding: 8px 16px;margin: 2px;border-top-left-radius: 6px;border-top-right-radius: 66px;}
QTabBar::tab:selected {background: #aeb6bf;font-weight: bold;}
QLabel {color: #2c3e50;}
QDialog {background-color: #f8f9fa;}
QToolButton {background-color: #ffffff;color: black;border: none;padding: 8px 16px;border-radius: 6px;}
QFrame.HistoryItem {border: 1px solid #ccc; border-radius: 5px; margin: 5px; background-color: #f0f0f0;}
QPushButton.DeleteButton {background-color: #dc3545; color: white; border-radius: 4px; padding: 4px 8px; font-weight: bold; border: none;}
QPushButton.DeleteButton:hover {background-color: #c82333;}
QFrame.DownloadItem {border: 1px solid #aaa; border-radius: 5px; margin: 5px; background-color: #fafafa;}
QProgressBar {border: 1px solid grey; border-radius: 5px; text-align: center;}
QProgressBar::chunk {background-color: #5d9cec;}
""")

# Our custom, manual list to track active downloads
downloads_list = {}

class DownloadsDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Downloads")
        self.setMinimumSize(400, 300)
        self.main_window = main_window

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.clear_button = QPushButton("Clear All Downloads")
        self.clear_button.clicked.connect(self.main_window.clear_all_downloads)
        self.main_layout.addWidget(self.clear_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.downloads_container = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_container)
        scroll_area.setWidget(self.downloads_container)
        self.main_layout.addWidget(scroll_area)
        
    def refresh_downloads(self):
        # Clear existing widgets
        for i in reversed(range(self.downloads_layout.count())):
            widget = self.downloads_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Combine active downloads and persistent downloads
        all_downloads = list(downloads_list.values()) + self.main_window.downloads_data

        # Add updated downloads items
        for download_info in all_downloads:
            frame = QFrame()
            frame.setObjectName("DownloadItem")
            layout = QHBoxLayout(frame)
            
            # File name and status
            file_name = os.path.basename(download_info['path'])
            name_label = QLabel(file_name)
            layout.addWidget(name_label)
            
            # Progress bar for in-progress downloads
            if download_info['state'] == QWebEngineDownloadItem.DownloadInProgress:
                progress_bar = QProgressBar()
                
                # --- Fix 1: Progress bar and size display ---
                if download_info['total_bytes'] > 0:
                    progress_bar.setValue(int(download_info.get('progress', 0) * 100))
                    status_text = f"{download_info['received_mb']:.2f} MB / {download_info['total_mb']:.2f} MB"
                else:
                    progress_bar.setRange(0, 0) # Indeterminate progress bar
                    status_text = f"{download_info['received_mb']:.2f} MB / Unknown Size"
                
                status_label = QLabel(status_text)
                
                layout.addWidget(progress_bar)
                layout.addWidget(status_label)

                # --- Fix 2: Pause/Resume button text and checked state ---
                pause_btn = QPushButton("Pause")
                pause_btn.setCheckable(True)
                if download_info['q_object'].isPaused():
                    pause_btn.setText("Resume")
                    pause_btn.setChecked(True)
                
                pause_btn.toggled.connect(lambda checked, d=download_info['q_object']: self.main_window.pause_resume_download(d, checked))
                layout.addWidget(pause_btn)
                
                cancel_btn = QPushButton("Cancel")
                cancel_btn.clicked.connect(lambda ch, d=download_info['q_object']: self.main_window.cancel_download(d))
                layout.addWidget(cancel_btn)
                # --------------------------------------------------------

            else:
                status_text = {
                    QWebEngineDownloadItem.DownloadCompleted: "Finished",
                    QWebEngineDownloadItem.DownloadCancelled: "Cancelled",
                    QWebEngineDownloadItem.DownloadInterrupted: "Interrupted",
                    QWebEngineDownloadItem.DownloadRequested: "Waiting...",
                }.get(download_info['state'], 'Unknown')
                
                status_label = QLabel(status_text)
                layout.addStretch()
                layout.addWidget(status_label)

                # Show in Folder Button for finished downloads
                if download_info['state'] == QWebEngineDownloadItem.DownloadCompleted:
                    show_folder_btn = QPushButton("Show in Folder")
                    show_folder_btn.clicked.connect(lambda ch, p=download_info['path']: self.main_window.show_in_folder(p))
                    layout.addWidget(show_folder_btn)

            self.downloads_layout.addWidget(frame)

class FindDialog(QDialog):
    def __init__(self, webview: QWebEngineView):
        super().__init__()
        self.webview = webview
        self.setWindowTitle("Find on Page")
        self.setFixedSize(400, 100)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Type to search...")
        self.query_input.returnPressed.connect(self.next_match)

        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.result_label = QLabel("")

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.query_input)
        h_layout.addWidget(self.prev_btn)
        h_layout.addWidget(self.next_btn)
        h_layout.addWidget(self.result_label)
        
        self.setLayout(h_layout)

        self.matches = 0
        self.current_index = 0

        self.next_btn.clicked.connect(self.next_match)
        self.prev_btn.clicked.connect(self.prev_match)
        self.query_input.textChanged.connect(self.start_search)

    def start_search(self, query):
        if not query:
            self.webview.findText("", QWebEnginePage.FindFlags())
            self.result_label.clear()
            return
        
        def on_find_finished(matches):
            self.matches = matches
            if self.matches > 0:
                self.current_index = 0
                self.result_label.setText(f"1 of {self.matches}")
                self.webview.findText(query)
            else:
                self.result_label.setText("No results")

        self.webview.findText(query, QWebEnginePage.FindFlags(), on_find_finished)
    
    def next_match(self):
        if self.matches == 0:
            return
        self.current_index = (self.current_index + 1) % self.matches
        self.webview.findText(self.query_input.text())
        self.result_label.setText(f"{self.current_index+1} of {self.matches}")
    
    def prev_match(self):
        if self.matches == 0:
            return
        self.current_index = (self.current_index - 1 + self.matches) % self.matches
        self.webview.findText(self.query_input.text(), QWebEnginePage.FindBackward)
        self.result_label.setText(f"{self.current_index+1} of {self.matches}")

class HistoryDialog(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Browsing History")
        self.setMinimumSize(400, 300)
        self.main_window = main_window

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        clear_button = QPushButton("Clear All History")
        clear_button.clicked.connect(self.main_window.delete_all_history)
        self.main_layout.addWidget(clear_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        scroll_area.setWidget(self.history_container)
        self.main_layout.addWidget(scroll_area)
        
    def refresh_history(self):
        # Clear existing widgets
        for i in reversed(range(self.history_layout.count())):
            widget = self.history_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add updated history items
        for title, url in self.main_window.history_data:
            history_item_frame = QFrame()
            history_item_frame.setObjectName("HistoryItem")
            history_item_frame.setFrameShape(QFrame.StyledPanel)
            history_item_frame.setFrameShadow(QFrame.Sunken)
            
            history_row = QHBoxLayout(history_item_frame)
            title_label = QLabel(title)
            title_label.setWordWrap(True)
            url_label = QLabel(url)
            url_label.setWordWrap(True)
            
            delete_button = QPushButton("X")
            delete_button.setObjectName("DeleteButton")
            delete_button.setFixedSize(24, 24)
            delete_button.clicked.connect(lambda ch, t=title, u=url: self.main_window.delete_history_item(t, u))
            
            history_row.addWidget(title_label, 3)
            history_row.addWidget(url_label, 5)
            history_row.addStretch()
            history_row.addWidget(delete_button)
            
            self.history_layout.addWidget(history_item_frame)

class ShortcutButton(QPushButton):
    def __init__(self, name, url, remove_callback, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.url = url
        self.remove_callback = remove_callback

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        delete = QAction("Delete", self)
        delete.triggered.connect(lambda: self.remove_callback(self, self.url))
        menu.addAction(delete)
        menu.exec_(e.globalPos())

# --- Core Browser Classes ---

class BrowserTab(QWidget):
    def __init__(self, parent, url_string, main_window):
        super().__init__(parent)
        self.url_bar = QLineEdit()
        self.browser = QWebEngineView()
        self.bookmarks_menu = QMenu()
        self.parent_tabs = parent
        self.main_window = main_window

        self.find_dialog = FindDialog(self.browser)
        self.find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.find_shortcut.activated.connect(self.find_dialog.show)

        self.setup_ui(url_string)

    def zoom_in(self):
        zoom = self.browser.zoomFactor()
        new_zoom = min(zoom + 0.25, 3.0)
        self.browser.setZoomFactor(new_zoom)

    def zoom_out(self):
        zoom = self.browser.zoomFactor()
        new_zoom = max(zoom - 0.25, 0.25)
        self.browser.setZoomFactor(new_zoom)
    
    def add_page_to_history(self):
        title = self.browser.page().title()
        url = self.browser.url().toString()
        self.main_window.add_page_to_global_history(title, url)

    def setup_ui(self, url_string):
        sidebar = QVBoxLayout()
        
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("C:/Users/vitoh/PySurf_Dev/PySurf_v1.3.0/Icons/Back_Icon.svg"))
        back_btn.setIconSize(QSize(24, 24))
        sidebar.addWidget(back_btn)
        
        forward_btn = QPushButton()
        forward_btn.setIcon(QIcon("C:/Users/vitoh/PySurf_Dev/PySurf_v1.3.0/Icons/Forward_Icon.svg"))
        forward_btn.setIconSize(QSize(24, 24))
        sidebar.addWidget(forward_btn)
        
        refresh_btn = QPushButton()
        refresh_btn.setIcon(QIcon("C:/Users/vitoh/PySurf_Dev/PySurf_v1.3.0/Icons/Refresh_Icon.svg"))
        refresh_btn.setIconSize(QSize(24, 24))
        sidebar.addWidget(refresh_btn)

        sidebar.addWidget(create_separator())
        
        bookmarks_btn = QToolButton()
        bookmarks_btn.setIcon(QIcon("C:/Users/vitoh/PySurf_Dev/PySurf_v1.3.0/Icons/Bookmarks_Icon.svg"))
        bookmarks_btn.setIconSize(QSize(24, 24))
        bookmarks_btn.setPopupMode(QToolButton.InstantPopup)
        bookmarks_btn.setMenu(self.bookmarks_menu)
        sidebar.addWidget(bookmarks_btn)
        
        downloads_btn = QToolButton()
        downloads_btn.setIcon(QIcon("C:/Users/vitoh/PySurf_Dev/PySurf_v1.3.0/Icons/Downloads_Icon.svg"))
        downloads_btn.setIconSize(QSize(24, 24))
        downloads_btn.clicked.connect(self.main_window.show_downloads_dialog)
        sidebar.addWidget(downloads_btn)

        history_btn = QPushButton()
        history_btn.setIcon(QIcon("C:/Users/vitoh/PySurf_Dev/PySurf_v1.3.0/Icons/History_Icon.svg"))
        history_btn.setIconSize(QSize(24, 24))
        history_btn.clicked.connect(self.main_window.show_history_dialog) 
        sidebar.addWidget(history_btn)

        sidebar.addWidget(create_separator())

        zoom_in_btn = QToolButton()
        zoom_in_btn.setIcon(QIcon("C:/Users/vitoh/PySurf_Dev/PySurf_v1.3.0/Icons/Zoom_In_Icon.svg"))
        zoom_in_btn.setIconSize(QSize(24, 24))
        zoom_in_btn.clicked.connect(self.zoom_in)
        sidebar.addWidget(zoom_in_btn)

        zoom_out_btn = QToolButton()
        zoom_out_btn.setIcon(QIcon("C:/Users/vitoh/PySurf_Dev/PySurf_v1.3.0/Icons/Zoom_Out_Icon.svg"))
        zoom_out_btn.setIconSize(QSize(24, 24))
        zoom_out_btn.clicked.connect(self.zoom_out)
        sidebar.addWidget(zoom_out_btn)
        
        sidebar.addStretch()
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_bar)

        content_layout = QVBoxLayout()
        content_layout.addLayout(url_layout)
        content_layout.addWidget(self.browser)

        main_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        main_layout.addLayout(sidebar)
        
        self.setLayout(main_layout)

        self.browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.browser.page().fullScreenRequested.connect(self.handle_fullscreen_request)
        self.browser.urlChanged.connect(self.update_url_bar)
        self.browser.loadFinished.connect(self.update_tab_title)
        
        self.url_bar.returnPressed.connect(self.navigate)
        back_btn.clicked.connect(self.browser.back)
        forward_btn.clicked.connect(self.browser.forward)
        refresh_btn.clicked.connect(self.browser.reload)

        self.browser.load(QUrl(url_string))
        self.refresh_bookmarks_menu()
        
        self.browser.loadFinished.connect(self.add_page_to_history)

    def navigate(self):
        text = self.url_bar.text()
        if "." not in text:
            text = "https://www.google.com/search?q=" + text
        if not text.startswith("http"):
            text = "https://" + text
        self.browser.load(QUrl(text))
    
    def update_url_bar(self, qurl):
        self.url_bar.setText(qurl.toString())
    
    def update_tab_title(self):
        index = self.parent_tabs.indexOf(self)
        self.browser.page().runJavaScript("document.title", lambda title: self.parent_tabs.setTabText(index, title or "New Tab"))

    def handle_fullscreen_request(self, request):
        if request.toggleOn():
            window.showFullScreen()
        else:
            window.showNormal()
        request.accept()

    def add_current_to_bookmarks(self):
        bookmarks_data = load_data(BOOKMARKS_FILE, default_data=[])
        title = self.browser.title()
        current_url = self.browser.url().toString()
        if not any(bm[1] == current_url for bm in bookmarks_data):
            bookmarks_data.append([title, current_url])
            save_data(bookmarks_data, BOOKMARKS_FILE)
            self.refresh_bookmarks_menu()

    def remove_bookmark(self, url_to_remove):
        bookmarks_data = load_data(BOOKMARKS_FILE, default_data=[])
        bookmarks_data = [bm for bm in bookmarks_data if bm[1] != url_to_remove]
        save_data(bookmarks_data, BOOKMARKS_FILE)
        self.refresh_bookmarks_menu()

    def refresh_bookmarks_menu(self):
        self.bookmarks_menu.clear()
        add_action = QAction("Add This Page to Bookmarks", self.bookmarks_menu)
        add_action.triggered.connect(self.add_current_to_bookmarks)
        self.bookmarks_menu.addAction(add_action)
        self.bookmarks_menu.addSeparator()
        for name, link in load_data(BOOKMARKS_FILE, default_data=[]):
            action = QAction(name, self.bookmarks_menu)
            action.triggered.connect(lambda ch, u=link: self.browser.load(QUrl(u)))
            submenu = QMenu()
            delete_action = QAction("Delete", submenu)
            delete_action.triggered.connect(lambda ch=False, u=link: self.remove_bookmark(u))
            submenu.addAction(delete_action)
            action.setMenu(submenu)
            self.bookmarks_menu.addAction(action)

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 700)
        
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        plus_button = QToolButton()
        plus_button.setText("+")
        plus_button.clicked.connect(self.create_homepage)
        self.tabs.setCornerWidget(plus_button)
        
        main_layout.addWidget(self.tabs)
        self.setCentralWidget(main_container)
        
        self.history_data = load_data(HISTORY_FILE, default_data=[])
        self.history_dialog = HistoryDialog(self)

        self.downloads_data = load_data(DOWNLOADS_FILE, default_data=[])
        self.downloads_dialog = DownloadsDialog(self)
        
        self.create_homepage()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

    def create_homepage(self):
        title_label = QLabel("PySurf Search")
        title_label.setFont(QFont("Segoe UI", 48))
        title_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search for anything...")
        search_bar.setFont(QFont("Arial", 18))
        
        search_button = QPushButton("Search")
        search_button.setFont(QFont("Arial", 18))

        def search():
            query = search_bar.text().strip()
            if query:
                self.open_site("https://www.google.com/search?q=" + query)

        search_button.clicked.connect(search)
        search_bar.returnPressed.connect(search)

        shortcuts_layout = QHBoxLayout()
        shortcuts_data = load_data(SHORTCUTS_FILE, default_data=[("YouTube", "https://www.youtube.com"), ("Google", "https://www.google.com")])

        def remove_shortcut(btn, url):
            nonlocal shortcuts_data
            shortcuts_data = [sc for sc in shortcuts_data if sc[1] != url]
            save_data(shortcuts_data, SHORTCUTS_FILE)
            btn.setParent(None)

        def add_shortcut_dialog():
            dialog = QDialog()
            dialog.setWindowTitle("Add Shortcut")
            dialog.setFixedSize(300, 150)
            name_input = QLineEdit()
            name_input.setPlaceholderText("Name")
            url_input = QLineEdit()
            url_input.setPlaceholderText("URL (include https://)")
            ok_button = QPushButton("OK")

            def on_ok():
                name = name_input.text().strip()
                url = url_input.text().strip()
                if name and url:
                    shortcuts_data.append([name, url])
                    save_data(shortcuts_data, SHORTCUTS_FILE)
                    button = ShortcutButton(name, url, remove_shortcut)
                    button.clicked.connect(lambda ch, u=url: self.open_site(u))
                    shortcuts_layout.addWidget(button)
                    dialog.accept()
            ok_button.clicked.connect(on_ok)
            dialog_layout = QVBoxLayout()
            dialog_layout.addWidget(name_input)
            dialog_layout.addWidget(url_input)
            dialog_layout.addWidget(ok_button)
            dialog.setLayout(dialog_layout)
            dialog.exec_()
            
        add_shortcut_button = QPushButton("Add Shortcut")
        add_shortcut_button.clicked.connect(add_shortcut_dialog)
        shortcuts_layout.addWidget(add_shortcut_button)

        for name, url in shortcuts_data:
            button = ShortcutButton(name, url, remove_shortcut)
            button.clicked.connect(lambda ch, u=url: self.open_site(u))
            shortcuts_layout.addWidget(button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addWidget(search_bar)
        main_layout.addLayout(shortcuts_layout)
        main_layout.addWidget(search_button)
        
        homepage_widget = QWidget()
        homepage_widget.setLayout(main_layout)
        
        self.tabs.addTab(homepage_widget, "Home")
        self.tabs.setCurrentWidget(homepage_widget)

    def close_tab(self, i):
        w = self.tabs.widget(i)
        self.tabs.removeTab(i)
        w.deleteLater()

    def open_site(self, url):
        tab_widget = BrowserTab(self.tabs, url, self) 
        tab_index = self.tabs.addTab(tab_widget, "New Tab")
        self.tabs.setCurrentIndex(tab_index)
        tab_widget.browser.load(QUrl(url))
    
    def add_page_to_global_history(self, title, url):
        if not self.history_data or (title, url) != self.history_data[-1]:
            self.history_data.append([title, url])
            save_data(self.history_data, HISTORY_FILE)
            
    def show_history_dialog(self):
        self.history_dialog.refresh_history()
        self.history_dialog.exec_()

    def delete_history_item(self, title, url):
        self.history_data = [item for item in self.history_data if item != [title, url]]
        save_data(self.history_data, HISTORY_FILE)
        self.history_dialog.refresh_history()

    def delete_all_history(self):
        self.history_data = []
        save_data(self.history_data, HISTORY_FILE)
        self.history_dialog.refresh_history()

    def show_downloads_dialog(self):
        self.downloads_dialog.refresh_downloads()
        self.downloads_dialog.show()

    def handle_download_requested(self, download):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", os.path.basename(download.path()))
        if path:
            download.setPath(path)
            download.accept()
            
            # --- Key change: Store the download object itself ---
            downloads_list[download.id()] = {
                'id': download.id(),
                'path': path,
                'state': download.state(),
                'q_object': download,
                'received_bytes': 0,
                'total_bytes': download.totalBytes(),
                'received_mb': 0.0,
                'total_mb': download.totalBytes() / (1024*1024),
                'progress': 0.0,
            }
            # ---------------------------------------------------
            
            download.downloadProgress.connect(lambda received, total: self.update_download_progress(download, received, total))
            download.stateChanged.connect(lambda state: self.handle_download_state_change(download, state))
            
            self.downloads_dialog.refresh_downloads()
            self.downloads_dialog.show()

    def update_download_progress(self, download, received_bytes, total_bytes):
        # --- Fix 3: Removed duplicated lines that were causing a logic error ---
        if download.id() in downloads_list:
            if total_bytes > 0:
                progress = received_bytes / total_bytes
            else:
                progress = 0
            
            downloads_list[download.id()]['received_bytes'] = received_bytes
            downloads_list[download.id()]['total_bytes'] = total_bytes
            downloads_list[download.id()]['received_mb'] = received_bytes / (1024 * 1024)
            downloads_list[download.id()]['total_mb'] = total_bytes / (1024 * 1024)
            downloads_list[download.id()]['progress'] = progress
            
            self.downloads_dialog.refresh_downloads()

    def handle_download_state_change(self, download, state):
        if download.id() in downloads_list:
            downloads_list[download.id()]['state'] = state
        
            # When finished or cancelled, remove from active list and move to persistent list
            if state in [QWebEngineDownloadItem.DownloadCompleted, QWebEngineDownloadItem.DownloadCancelled]:
                download_info = downloads_list.pop(download.id())
                
                # --- Fix 4: Removed the QWebEngineDownloadItem object before saving to JSON ---
                if 'q_object' in download_info:
                    del download_info['q_object']
                # ---------------------------------------------------------------------------------
                
                self.downloads_data.append(download_info)
                save_data(self.downloads_data, DOWNLOADS_FILE)
            
            self.downloads_dialog.refresh_downloads()

    # --- Key change: Use the object directly, no lookup required ---
    def pause_resume_download(self, download_obj, checked):
        if checked:
            download_obj.pause()
        else:
            download_obj.resume()

    def cancel_download(self, download_obj):
        download_obj.cancel()
    # --------------------------------------------------------------
    
    def show_in_folder(self, path):
        if sys.platform == "win32":
            QProcess.startDetached("explorer.exe", ["/select,", os.path.normpath(path)])
        elif sys.platform == "darwin":
            QProcess.startDetached("open", ["-R", path])
        else: # Linux
            QProcess.startDetached("xdg-open", [os.path.dirname(path)])

    def clear_all_downloads(self):
        # This will not affect active downloads, just the persistent history
        self.downloads_data = []
        save_data(self.downloads_data, DOWNLOADS_FILE)
        self.downloads_dialog.refresh_downloads()

# --- Application Startup ---

if __name__ == "__main__":
    window = MyMainWindow()
    window.show()

    profile = QWebEngineProfile.defaultProfile()
    profile.downloadRequested.connect(window.handle_download_requested)

    sys.exit(app.exec_())