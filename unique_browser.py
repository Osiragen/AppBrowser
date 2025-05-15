import sys
import os
import time
import json
import webbrowser
import platform
import subprocess
import shutil
from PyQt5.QtCore import QUrl, Qt, QStandardPaths, QTimer, QSize, QPoint, QProcess
from PyQt5.QtGui import QIcon, QKeySequence, QDesktopServices, QColor, QPalette, QCursor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QToolBar, QLineEdit,
                            QAction, QMenu, QMessageBox, QStatusBar, QFileDialog,
                            QInputDialog, QShortcut, QLabel, QStyleFactory, QSystemTrayIcon,
                            QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
                            QGroupBox, QComboBox, QRadioButton, QProgressBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineDownloadItem, QWebEngineSettings, QWebEnginePage
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtNetwork import QNetworkProxyFactory


# คลาสสำหรับจัดการการเปิดลิงก์ในแท็บใหม่
class CustomWebEnginePage(QWebEnginePage):
    """คลาสที่ใช้สำหรับจัดการการเปิดลิงก์ในแท็บใหม่"""

    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.main_browser = parent

    def createWindow(self, window_type):
        """เมธอดที่ถูกเรียกเมื่อต้องการเปิดหน้าต่างใหม่"""
        try:
            print(f"Creating new window of type: {window_type}")

            # ตรวจสอบประเภทของหน้าต่าง
            if window_type == QWebEnginePage.WebBrowserWindow:
                # เปิดในหน้าต่างใหม่
                new_browser = UniqueBrowser()
                new_browser.show()
                # คืนค่า page ของแท็บแรกในหน้าต่างใหม่
                return new_browser.current_browser().page()
            else:
                # สร้างแท็บใหม่และคืนค่า QWebEnginePage
                if hasattr(self.main_browser, 'browser_window'):
                    # ใช้เมธอดของคลาสหลักที่จะสร้างแท็บใหม่
                    new_tab = self.main_browser.browser_window.add_new_tab()
                    if new_tab:
                        # คืนค่า page ไม่ใช่ view
                        return new_tab.page()
            return None
        except Exception as e:
            print(f"Error in CustomWebEnginePage.createWindow: {e}")
            return None

class UniqueBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # ตั้งค่าพื้นฐาน
        self.app_name = "Unique Browser"
        self.version = "3.0"
        self.dark_mode = False
        self.private_mode = False
        self.downloads = []
        self.extensions = []

        # ตรวจสอบระบบปฏิบัติการ
        self.is_linux = platform.system() == "Linux"
        self.is_wayland = self.check_wayland()

        # ตั้งค่าหน้าต่าง
        self.setWindowTitle(self.app_name)
        # ใช้ไอคอนที่สร้างขึ้นเอง
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "unique_browser.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # ใช้ไอคอนเบราว์เซอร์ของระบบถ้าไม่พบไอคอนที่สร้างขึ้น
            if self.is_linux:
                self.setWindowIcon(QIcon.fromTheme("web-browser"))
        self.setGeometry(100, 100, 1400, 900)

        # โหลดการตั้งค่า
        self.load_settings()

        # สร้างระบบแท็บ
        self.setup_tabs()

        # ระบบแถบเครื่องมือ (ต้องสร้างก่อน setup_ui เพราะมี url_bar)
        self.setup_toolbars()

        # ระบบแถบสถานะ
        self.setup_statusbar()

        # สร้าง UI
        self.setup_ui()

        # ตั้งค่าคีย์ลัด
        self.setup_shortcuts()

        # ระบบเมนู
        self.setup_menus()

        # ระบบ Tray Icon
        self.setup_tray_icon()

        # เริ่มต้นด้วยแท็บแรก
        self.add_new_tab(QUrl(self.settings.get('homepage', 'https://www.google.com')), "หน้าแรก")

        # ตั้งค่าการรองรับวิดีโอเพิ่มเติม
        self.setup_video_support()

        # ตัวจับเวลาอัพเดท UI
        self.ui_update_timer = QTimer()
        self.ui_update_timer.timeout.connect(self.update_ui)
        self.ui_update_timer.start(1000)

    def resource_path(self, relative_path):
        """หาที่อยู่ของไฟล์ทรัพยากร"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_settings(self):
        """โหลดการตั้งค่าจากไฟล์"""
        self.settings_file = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
            "UniqueBrowser",
            "settings.json"
        )

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except:
            self.settings = {
                'homepage': 'https://www.google.com',
                'search_engine': 'https://www.google.com/search?q=',
                'download_location': QStandardPaths.writableLocation(QStandardPaths.DownloadLocation),
                'dark_mode': False,
                'zoom_level': 1.0,
                'bookmarks': {
                    'เครื่องมือค้นหา': [
                        {'name': 'Google', 'url': 'https://www.google.com'},
                        {'name': 'Bing', 'url': 'https://www.bing.com'}
                    ]
                },
                'history': [],
                'extensions': []
            }

    def save_settings(self):
        """บันทึกการตั้งค่า"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def setup_tabs(self):
        """ตั้งค่าระบบแท็บ"""
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.setCentralWidget(self.tabs)

    def setup_ui(self):
        """ตั้งค่า UI พื้นฐาน"""
        # ตั้งค่า proxy (ถ้ามี)
        QNetworkProxyFactory.setUseSystemConfiguration(True)

        # ตั้งค่า style
        self.setStyle(QStyleFactory.create('Fusion'))

        # ตั้งค่า WebEngine Settings
        self.setup_web_settings()

        # ตั้งค่าสีตามโหมด
        self.update_theme()

    def setup_web_settings(self):
        """ตั้งค่า WebEngine Settings"""
        try:
            # ตั้งค่าสำหรับทุก profile
            settings = QWebEngineSettings.globalSettings()

            # เปิดใช้งาน JavaScript
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)

            # เปิดใช้งาน Plugins (สำหรับ Flash และอื่นๆ)
            settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)

            # เปิดใช้งานการเล่นวิดีโอและเสียงอัตโนมัติ
            settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)

            # เปิดใช้งานการเล่นวิดีโอแบบ Autoplay
            settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)

            # เปิดใช้งาน Media Source Extensions
            if hasattr(QWebEngineSettings, 'AllowWindowActivationFromJavaScript'):
                settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)

            # เปิดใช้งาน WebRTC
            if hasattr(QWebEngineSettings, 'WebRTCPublicInterfacesOnly'):
                settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, False)

            # เปิดใช้งาน HTML5 Storage APIs
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

            # เปิดใช้งาน WebGL
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)

            # เปิดใช้งาน Accelerated 2D Canvas
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)

            # เปิดใช้งาน Fullscreen API
            settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)

            # เปิดใช้งาน PDF Viewer
            if hasattr(QWebEngineSettings, 'PdfViewerEnabled'):
                settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)

            # เปิดใช้งาน Autoload Images
            settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)

            # เปิดใช้งาน JavaScript Access Clipboard
            if hasattr(QWebEngineSettings, 'JavascriptCanAccessClipboard'):
                settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)

            # เปิดใช้งาน JavaScript Can Open Windows
            if hasattr(QWebEngineSettings, 'JavascriptCanOpenWindows'):
                settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)

            # เปิดใช้งาน Screen Capture
            if hasattr(QWebEngineSettings, 'ScreenCaptureEnabled'):
                settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)

            # เปิดใช้งาน WebAudio
            if hasattr(QWebEngineSettings, 'WebAudioEnabled'):
                settings.setAttribute(QWebEngineSettings.WebAudioEnabled, True)

            print("WebEngine settings configured successfully")
        except Exception as e:
            print(f"Error setting up WebEngine settings: {e}")

    def update_theme(self):
        """อัพเดทธีมตามการตั้งค่า"""
        try:
            palette = QPalette()

            if self.dark_mode:
                # ตั้งค่าสีสำหรับโหมดกลางคืน
                palette.setColor(QPalette.Window, QColor(53, 53, 53))
                palette.setColor(QPalette.WindowText, Qt.white)
                palette.setColor(QPalette.Base, QColor(25, 25, 25))
                palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
                palette.setColor(QPalette.ToolTipBase, Qt.white)
                palette.setColor(QPalette.ToolTipText, Qt.white)
                palette.setColor(QPalette.Text, Qt.white)
                palette.setColor(QPalette.Button, QColor(53, 53, 53))
                palette.setColor(QPalette.ButtonText, Qt.white)
                palette.setColor(QPalette.BrightText, Qt.red)
                palette.setColor(QPalette.Link, QColor(42, 130, 218))
                palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
                palette.setColor(QPalette.HighlightedText, Qt.black)
            else:
                # ใช้ธีมปกติ
                palette = QApplication.style().standardPalette()

            # ตั้งค่าธีมให้กับแอพพลิเคชัน
            self.setPalette(palette)

            # อัพเดทแท็บทั้งหมด
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                if browser:
                    # ตั้งค่าพื้นหลังของ WebView
                    if self.dark_mode:
                        browser.setStyleSheet("background-color: #333333;")
                    else:
                        browser.setStyleSheet("")

            # อัพเดทแถบสถานะ
            status_style = "QStatusBar { background-color: #333333; color: white; }" if self.dark_mode else ""
            self.status.setStyleSheet(status_style)

            # อัพเดทแถบแท็บ
            tab_style = """
                QTabWidget::pane { border: none; }
                QTabBar::tab { background-color: #444444; color: white; padding: 8px; }
                QTabBar::tab:selected { background-color: #666666; }
            """ if self.dark_mode else ""
            self.tabs.setStyleSheet(tab_style)

            # อัพเดท URL bar
            url_style = "QLineEdit { background-color: #444444; color: white; border: 1px solid #555555; }" if self.dark_mode else ""
            self.url_bar.setStyleSheet(url_style)

        except Exception as e:
            print(f"Error in update_theme: {e}")

    def setup_toolbars(self):
        """ตั้งค่าแถบเครื่องมือ"""
        # แถบเครื่องมือหลัก
        self.main_toolbar = QToolBar("แถบเครื่องมือหลัก")
        self.main_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.main_toolbar)

        # ปุ่มต่างๆ
        self.setup_toolbar_buttons()

        # แถบเครื่องมือรอง
        self.secondary_toolbar = QToolBar("แถบเครื่องมือรอง")
        self.addToolBar(Qt.BottomToolBarArea, self.secondary_toolbar)

        # ปุ่มเพิ่มเติม
        self.setup_secondary_toolbar()

    def setup_toolbar_buttons(self):
        """ตั้งค่าปุ่มแถบเครื่องมือ"""
        actions = [
            ('แท็บใหม่', 'Ctrl+T', lambda: self.add_new_tab()),
            ('←', 'Alt+Left', self.navigate_back),
            ('→', 'Alt+Right', self.navigate_forward),
            ('⟳', 'F5', self.refresh_page),
            ('หน้าแรก', 'Alt+Home', self.navigate_home),
            ('ดาวน์โหลด', 'Ctrl+J', self.show_downloads),
            ('บุ๊กมาร์ก', 'Ctrl+D', self.add_current_to_bookmarks),
            ('ประวัติ', 'Ctrl+H', self.show_history),
            ('ส่วนขยาย', 'Ctrl+Shift+E', self.show_extensions),
            ('เมนู', None, self.show_main_menu)
        ]

        for tip, shortcut, func in actions:
            action = QAction(tip, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(func)
            self.main_toolbar.addAction(action)

        # ช่อง URL
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("พิมพ์ URL หรือคำค้นหา...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.main_toolbar.addWidget(self.url_bar)

    def setup_secondary_toolbar(self):
        """ตั้งค่าแถบเครื่องมือรอง"""
        actions = [
            ('ซูมเข้า', 'Ctrl++', self.zoom_in),
            ('ซูมออก', 'Ctrl+-', self.zoom_out),
            ('รีเซ็ตซูม', 'Ctrl+0', self.zoom_reset),
            ('พิมพ์', 'Ctrl+P', self.print_page),
            ('เต็มจอ', 'F11', self.toggle_fullscreen),
            ('ส่วนตัว', 'Ctrl+Shift+P', self.toggle_private_mode),
            ('กลางคืน', 'Ctrl+Shift+D', self.toggle_dark_mode),
            ('นักพัฒนา', 'F12', self.toggle_dev_tools)
        ]

        for tip, shortcut, func in actions:
            action = QAction(tip, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(func)
            self.secondary_toolbar.addAction(action)

    def setup_menus(self):
        """ตั้งค่าเมนูบาร์"""
        menubar = self.menuBar()

        # เมนู File
        file_menu = menubar.addMenu("&ไฟล์")
        self.setup_file_menu(file_menu)

        # เมนู Edit
        edit_menu = menubar.addMenu("&แก้ไข")
        self.setup_edit_menu(edit_menu)

        # เมนู View
        view_menu = menubar.addMenu("&มุมมอง")
        self.setup_view_menu(view_menu)

        # เมนู Bookmarks
        bookmarks_menu = menubar.addMenu("&บุ๊กมาร์ก")
        self.setup_bookmarks_menu(bookmarks_menu)

        # เมนู Tools
        tools_menu = menubar.addMenu("&เครื่องมือ")
        self.setup_tools_menu(tools_menu)

        # เมนู Help
        help_menu = menubar.addMenu("&ช่วยเหลือ")
        self.setup_help_menu(help_menu)

    def setup_file_menu(self, menu):
        """ตั้งค่าเมนู File"""
        actions = [
            ('แท็บใหม่', 'Ctrl+T', lambda: self.add_new_tab()),
            ('แท็บส่วนตัว', 'Ctrl+Shift+T', lambda: self.add_new_tab(QUrl(self.settings['homepage']), "แท็บส่วนตัว", private=True)),
            ('ปิดแท็บปัจจุบัน', 'Ctrl+W', self.close_current_tab),
            ('ปิดเบราว์เซอร์', 'Ctrl+Q', self.close),
            None,  # Separator
            ('บันทึกหน้าเว็บ...', 'Ctrl+S', self.save_page),
            ('พิมพ์...', 'Ctrl+P', self.print_page),
            None,  # Separator
            ('ตั้งค่า...', 'Ctrl+,', self.show_settings),
            ('นำเข้า/ส่งออก...', None, self.show_import_export),
            None,  # Separator
            ('ออกจากระบบ', None, self.close)
        ]

        self.add_menu_actions(menu, actions)

    def setup_edit_menu(self, menu):
        """ตั้งค่าเมนู Edit"""
        actions = [
            ('ตัด', 'Ctrl+X', self.cut),
            ('คัดลอก', 'Ctrl+C', self.copy),
            ('วาง', 'Ctrl+V', self.paste),
            None,
            ('เลือกทั้งหมด', 'Ctrl+A', self.select_all),
            None,
            ('ค้นหาในหน้า...', 'Ctrl+F', self.find_in_page)
        ]

        self.add_menu_actions(menu, actions)

    def setup_view_menu(self, menu):
        """ตั้งค่าเมนู View"""
        zoom_menu = menu.addMenu("การซูม")
        zoom_actions = [
            ('ซูมเข้า', 'Ctrl++', self.zoom_in),
            ('ซูมออก', 'Ctrl+-', self.zoom_out),
            ('รีเซ็ตซูม', 'Ctrl+0', self.zoom_reset)
        ]
        self.add_menu_actions(zoom_menu, zoom_actions)

        appearance_menu = menu.addMenu("รูปลักษณ์")
        appearance_actions = [
            ('โหมดกลางคืน', 'Ctrl+Shift+D', self.toggle_dark_mode),
            ('โหมดเต็มหน้าจอ', 'F11', self.toggle_fullscreen),
            ('แสดงแถบเครื่องมือ', None, self.toggle_toolbar)
        ]
        self.add_menu_actions(appearance_menu, appearance_actions)

        menu.addSeparator()
        refresh_action = QAction('รีเฟรช', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_page)
        menu.addAction(refresh_action)

    def setup_bookmarks_menu(self, menu):
        """ตั้งค่าเมนู Bookmarks"""
        # เพิ่มบุ๊กมาร์กจากข้อมูล
        for category, items in self.settings['bookmarks'].items():
            category_menu = menu.addMenu(category)
            for item in items:
                action = QAction(item['name'], self)
                action.triggered.connect(lambda _, url=item['url']: self.navigate_in_current_tab(QUrl(url)))
                category_menu.addAction(action)

        menu.addSeparator()

        add_bookmark_action = QAction('เพิ่มบุ๊กมาร์กปัจจุบัน...', self)
        add_bookmark_action.setShortcut('Ctrl+D')
        add_bookmark_action.triggered.connect(self.add_current_to_bookmarks)
        menu.addAction(add_bookmark_action)

        manage_bookmark_action = QAction('จัดการบุ๊กมาร์ก...', self)
        manage_bookmark_action.triggered.connect(self.manage_bookmarks)
        menu.addAction(manage_bookmark_action)

    def setup_tools_menu(self, menu):
        """ตั้งค่าเมนู Tools"""
        actions = [
            ('ดาวน์โหลด', 'Ctrl+J', self.show_downloads),
            ('ประวัติ', 'Ctrl+H', self.show_history),
            ('ส่วนขยาย', 'Ctrl+Shift+E', self.show_extensions),
            None,
            ('เครื่องมือนักพัฒนา', 'F12', self.toggle_dev_tools),
            ('คอนโซล JavaScript', 'Ctrl+Shift+J', self.show_js_console),
            None,
            ('ตั้งค่าการเล่นวิดีโอ', None, self.setup_video_support),
            ('ตั้งค่าโปรxy...', None, self.setup_proxy),
            ('เคลียร์ข้อมูลการท่องเว็บ...', None, self.clear_browsing_data),
            None,
            ('ปรับแต่งประสิทธิภาพ', None, self.optimize_for_linux)
        ]

        self.add_menu_actions(menu, actions)

    def setup_help_menu(self, menu):
        """ตั้งค่าเมนู Help"""
        actions = [
            ('เกี่ยวกับ Unique Browser', None, self.show_about),
            ('ตรวจสอบอัปเดต', None, self.check_for_updates),
            None,
            ('เอกสารประกอบ', 'F1', self.show_documentation),
            ('รายงานปัญหา', None, self.report_issue),
            None,
            ('ปุ่มลัด', None, self.show_shortcuts)
        ]

        self.add_menu_actions(menu, actions)

    def add_menu_actions(self, menu, actions):
        """เพิ่ม action ลงในเมนู"""
        for action_item in actions:
            if action_item is None:
                menu.addSeparator()
            else:
                name, shortcut, func = action_item
                action = QAction(name, self)
                if shortcut:
                    action.setShortcut(shortcut)
                action.triggered.connect(func)
                menu.addAction(action)

    def setup_shortcuts(self):
        """ตั้งค่าคีย์ลัด"""
        shortcuts = [
            ('Ctrl+Tab', self.next_tab),
            ('Ctrl+Shift+Tab', self.previous_tab),
            ('Ctrl+1', lambda: self.switch_to_tab(0)),
            ('Ctrl+2', lambda: self.switch_to_tab(1)),
            ('Ctrl+3', lambda: self.switch_to_tab(2)),
            ('Ctrl+4', lambda: self.switch_to_tab(3)),
            ('Ctrl+5', lambda: self.switch_to_tab(4)),
            ('Ctrl+N', self.new_window),
            ('Ctrl+Shift+N', self.new_private_window),
            ('Ctrl+Shift+Del', self.clear_browsing_data),
            ('F6', self.focus_url_bar),
            ('Esc', self.stop_loading)
        ]

        for key, func in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)

    def setup_statusbar(self):
        """ตั้งค่าแถบสถานะ"""
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # ตัวชี้วัดความคืบหน้า
        self.progress_label = QLabel()
        self.status.addPermanentWidget(self.progress_label)

        # ตัวชี้วัดโหมด
        self.mode_label = QLabel()
        self.status.addPermanentWidget(self.mode_label)
        self.update_mode_label()

    def setup_tray_icon(self):
        """ตั้งค่าระบบ Tray Icon"""
        # ใช้ไอคอนที่สร้างขึ้นเอง
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "unique_browser.ico")
        if os.path.exists(icon_path):
            # สร้าง tray icon
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(icon_path))
            self.tray_icon.setToolTip(f"{self.app_name} {self.version}")

            # สร้างเมนูสำหรับ tray icon
            tray_menu = QMenu()

            # เพิ่มตัวเลือกในเมนู
            show_action = QAction("แสดงเบราว์เซอร์", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            new_tab_action = QAction("แท็บใหม่", self)
            new_tab_action.triggered.connect(lambda: self.add_new_tab())
            tray_menu.addAction(new_tab_action)

            tray_menu.addSeparator()

            exit_action = QAction("ออกจากโปรแกรม", self)
            exit_action.triggered.connect(self.close)
            tray_menu.addAction(exit_action)

            # ตั้งค่าเมนูและเปิดใช้งาน tray icon
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            self.tray_icon.show()
        else:
            # ปิดการใช้งาน Tray Icon เนื่องจากไม่พบไอคอน
            pass

    def tray_icon_activated(self, reason):
        """เมื่อคลิกที่ tray icon"""
        if reason == QSystemTrayIcon.Trigger:
            self.show()
            self.activateWindow()

    def current_browser(self):
        """รับ browser ปัจจุบัน"""
        try:
            return self.tabs.currentWidget()
        except Exception as e:
            print(f"Error in current_browser: {e}")
            return None

    def update_ui(self):
        """อัพเดท UI เป็นระยะ"""
        current_browser = self.current_browser()
        if current_browser:
            # อัพเดท URL บาร์
            if current_browser.hasFocus() or self.url_bar.hasFocus():
                return

            self.url_bar.setText(current_browser.url().toString())

    def current_browser(self):
        """คืนค่าเบราว์เซอร์ปัจจุบัน"""
        return self.tabs.currentWidget()

    def add_new_tab(self, qurl=None, label="แท็บใหม่", private=False):
        """เพิ่มแท็บใหม่"""
        try:
            if qurl is None:
                qurl = QUrl(self.settings['homepage'])

            browser = QWebEngineView()

            # ตั้งค่าโพรไฟล์หากเป็นโหมดส่วนตัว
            if private or self.private_mode:
                profile = QWebEngineProfile("PrivateProfile", browser)
                # สร้าง page ใหม่ด้วย profile ส่วนตัว
                page = QWebEnginePage(profile, browser)
                browser.setPage(page)
            else:
                # ตั้งค่าการดาวน์โหลด
                browser.page().profile().downloadRequested.connect(self.download_requested)

            # ตั้งค่าการจัดการลิงก์ภายนอก
            browser.page().linkHovered.connect(self.link_hovered)

            # สร้าง custom WebEnginePage ที่จัดการการเปิดลิงก์ในแท็บใหม่
            browser.browser_window = self

            # ใช้ profile ที่มีอยู่แล้ว
            current_profile = browser.page().profile()
            custom_page = CustomWebEnginePage(current_profile, browser)
            custom_page.main_browser = browser  # ตั้งค่า main_browser attribute
            browser.setPage(custom_page)

            # เพิ่มเมนูคลิกขวา
            browser.setContextMenuPolicy(Qt.CustomContextMenu)
            browser.customContextMenuRequested.connect(lambda pos, browser=browser: self.show_context_menu(pos, browser))

            browser.setUrl(qurl)

            # เชื่อมต่อสัญญาณ
            browser.urlChanged.connect(lambda qurl, browser=browser:
                self.update_urlbar(qurl, browser))

            # ปิดการใช้งาน loadProgress เนื่องจากอาจทำให้เกิดข้อผิดพลาด
            # browser.loadProgress.connect(self.update_progress)

            browser.loadFinished.connect(lambda _, browser=browser:
                self.on_load_finished(browser))

            # เพิ่มแท็บ
            index = self.tabs.addTab(browser, label)
            self.tabs.setCurrentIndex(index)

            # บันทึกประวัติ (ยกเว้นโหมดส่วนตัว)
            if not private and not self.private_mode:
                # ใช้ label แทน title เพื่อหลีกเลี่ยงข้อผิดพลาด
                self.add_to_history(qurl.toString(), label)

            return browser
        except Exception as e:
            print(f"Error in add_new_tab: {e}")
            return None

    def show_context_menu(self, pos, browser):
        """แสดงเมนูคลิกขวา"""
        try:
            # สร้างเมนูคลิกขวา
            menu = QMenu()

            # ใช้ JavaScript เพื่อตรวจสอบว่าตำแหน่งที่คลิกมีลิงก์หรือไม่
            # เก็บข้อมูลลิงก์ไว้ในตัวแปรชั่วคราว
            self.context_link_url = None

            # ตัวเลือกทั่วไปที่แสดงเสมอ
            back_action = menu.addAction("ย้อนกลับ")
            forward_action = menu.addAction("ไปข้างหน้า")
            refresh_action = menu.addAction("รีเฟรช")
            menu.addSeparator()

            # เชื่อมต่อการกระทำทั่วไป
            back_action.triggered.connect(browser.back)
            forward_action.triggered.connect(browser.forward)
            refresh_action.triggered.connect(browser.reload)

            # ตรวจสอบว่ามีข้อความที่เลือกไว้หรือไม่
            browser.page().triggerAction(QWebEnginePage.Copy)
            selected_text = QApplication.clipboard().text()

            if selected_text:
                # เพิ่มตัวเลือกสำหรับข้อความที่เลือก
                copy_action = menu.addAction("คัดลอก")
                search_action = menu.addAction("ค้นหา")

                # เชื่อมต่อการกระทำ
                copy_action.triggered.connect(lambda: browser.page().triggerAction(QWebEnginePage.Copy))
                search_action.triggered.connect(lambda: self.search_text(selected_text))

                menu.addSeparator()

            # เพิ่มตัวเลือกสำหรับลิงก์ (ถ้ามี)
            # ใช้ JavaScript เพื่อตรวจสอบลิงก์ที่ตำแหน่งที่คลิก
            browser.page().runJavaScript("""
                (function() {
                    var element = document.elementFromPoint(%d, %d);
                    while (element && element.tagName !== 'A') {
                        element = element.parentElement;
                    }
                    if (element && element.tagName === 'A') {
                        return element.href;
                    }
                    return '';
                })();
            """ % (pos.x(), pos.y()), self.handle_link_context_menu_result)

            # เพิ่มตัวเลือกทั่วไป
            menu.addSeparator()
            view_source_action = menu.addAction("ดูซอร์สโค้ด")
            inspect_action = menu.addAction("ตรวจสอบองค์ประกอบ")

            # เชื่อมต่อการกระทำ
            view_source_action.triggered.connect(lambda: browser.page().triggerAction(QWebEnginePage.ViewSource))
            inspect_action.triggered.connect(lambda: browser.page().triggerAction(QWebEnginePage.InspectElement))

            # แสดงเมนู
            menu.exec_(browser.mapToGlobal(pos))

        except Exception as e:
            print(f"Error in show_context_menu: {e}")

    def handle_link_context_menu_result(self, result):
        """จัดการผลลัพธ์จาก JavaScript สำหรับเมนูคลิกขวาที่ลิงก์"""
        try:
            if result and isinstance(result, str) and result.startswith(('http://', 'https://')):
                # เก็บ URL ไว้ในตัวแปรชั่วคราว
                self.context_link_url = QUrl(result)

                # สร้างเมนูเพิ่มเติมสำหรับลิงก์
                link_menu = QMenu("ตัวเลือกลิงก์")

                # เพิ่มตัวเลือกสำหรับลิงก์
                open_in_new_tab_action = link_menu.addAction("เปิดในแท็บใหม่")
                open_in_new_window_action = link_menu.addAction("เปิดในหน้าต่างใหม่")
                open_in_private_window_action = link_menu.addAction("เปิดในหน้าต่างส่วนตัว")
                link_menu.addSeparator()
                copy_link_action = link_menu.addAction("คัดลอกลิงก์")

                # เชื่อมต่อการกระทำ
                open_in_new_tab_action.triggered.connect(lambda: self.open_link_in_new_tab(self.context_link_url))
                open_in_new_window_action.triggered.connect(lambda: self.open_link_in_new_window(self.context_link_url))
                open_in_private_window_action.triggered.connect(lambda: self.open_link_in_private_window(self.context_link_url))
                copy_link_action.triggered.connect(lambda: QApplication.clipboard().setText(self.context_link_url.toString()))

                # แสดงเมนู
                link_menu.exec_(QCursor.pos())
        except Exception as e:
            print(f"Error in handle_link_context_menu_result: {e}")

    def search_text(self, text):
        """ค้นหาข้อความในเครื่องมือค้นหา"""
        try:
            search_url = self.settings.get('search_engine', 'https://www.google.com/search?q=')
            qurl = QUrl(search_url + text.replace(' ', '+'))
            self.open_link_in_new_tab(qurl)
        except Exception as e:
            print(f"Error in search_text: {e}")

    def open_link_in_new_window(self, url):
        """เปิดลิงก์ในหน้าต่างใหม่"""
        try:
            print(f"Opening link in new window: {url.toString()}")

            # สร้างหน้าต่างใหม่
            new_browser = UniqueBrowser()
            new_browser.add_new_tab(url, url.toString())
            new_browser.show()

            # แสดงข้อความสถานะ
            self.status.showMessage(f"เปิดลิงก์ในหน้าต่างใหม่: {url.toString()}", 3000)

        except Exception as e:
            print(f"Error in open_link_in_new_window: {e}")

    def open_link_in_private_window(self, url):
        """เปิดลิงก์ในหน้าต่างส่วนตัว"""
        try:
            print(f"Opening link in private window: {url.toString()}")

            # สร้างหน้าต่างส่วนตัวใหม่
            new_browser = UniqueBrowser()
            new_browser.private_mode = True
            new_browser.update_mode_label()
            new_browser.add_new_tab(url, url.toString(), private=True)
            new_browser.show()

            # แสดงข้อความสถานะ
            self.status.showMessage(f"เปิดลิงก์ในหน้าต่างส่วนตัว: {url.toString()}", 3000)

        except Exception as e:
            print(f"Error in open_link_in_private_window: {e}")

    def create_window_for_tab(self, window_type):
        """สร้างหน้าต่างใหม่สำหรับแท็บ (เมื่อคลิกลิงก์ที่ต้องการเปิดในแท็บใหม่)"""
        try:
            print(f"Creating new tab for window type: {window_type}")

            # สร้างแท็บใหม่และคืนค่า WebEngineView
            new_tab = self.add_new_tab()

            # แสดงข้อความสถานะ
            self.status.showMessage("เปิดในแท็บใหม่", 3000)

            return new_tab
        except Exception as e:
            print(f"Error in create_window_for_tab: {e}")
            return None

    def link_hovered(self, url):
        """แสดง URL เมื่อเมาส์ชี้ที่ลิงก์"""
        if url:
            self.status.showMessage(url, 3000)

    def open_link_in_new_tab(self, url, background=False):
        """เปิดลิงก์ในแท็บใหม่"""
        try:
            print(f"Opening link in new tab: {url.toString()}")

            # สร้างแท็บใหม่
            new_tab = self.add_new_tab(url, url.toString())

            # ถ้าไม่ใช่แท็บพื้นหลัง ให้เปลี่ยนไปที่แท็บใหม่
            if not background:
                self.tabs.setCurrentWidget(new_tab)

            # แสดงข้อความสถานะ
            self.status.showMessage(f"เปิดลิงก์ในแท็บใหม่: {url.toString()}", 3000)

            return new_tab
        except Exception as e:
            print(f"Error in open_link_in_new_tab: {e}")
            return None

    def download_image(self, url):
        """ดาวน์โหลดรูปภาพ"""
        try:
            print(f"Downloading image: {url.toString()}")

            # เลือกตำแหน่งที่จะบันทึกไฟล์
            file_name = url.fileName()
            if not file_name:
                file_name = "image.jpg"

            save_path, _ = QFileDialog.getSaveFileName(
                self, "บันทึกรูปภาพ",
                QStandardPaths.writableLocation(QStandardPaths.DownloadLocation) + "/" + file_name,
                "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
            )

            if save_path:
                # ดาวน์โหลดไฟล์
                self.status.showMessage(f"กำลังดาวน์โหลดรูปภาพไปยัง {save_path}...", 3000)

                # ใช้ QWebEngineDownloadItem เพื่อดาวน์โหลด
                self.current_browser().page().profile().download(url, save_path)
        except Exception as e:
            print(f"Error in download_image: {e}")

    def on_load_finished(self, browser):
        """เมื่อโหลดหน้าเสร็จสิ้น"""
        try:
            title = browser.page().title()
            index = self.tabs.indexOf(browser)

            if title:
                self.tabs.setTabText(index, title[:20] + '...' if len(title) > 20 else title)
                self.tabs.setTabToolTip(index, title)
        except Exception as e:
            # ป้องกันข้อผิดพลาดที่อาจเกิดขึ้น
            print(f"Error in on_load_finished: {e}")

        # อัพเดท favicon (ตัวอย่างเท่านั้น)
        # ในทางปฏิบัติต้องใช้ QWebEnginePage.iconChanged signal

    def update_progress(self, progress):
        """อัพเดทความคืบหน้า"""
        try:
            self.progress_label.setText(f"{progress}%" if progress < 100 else "")
        except Exception as e:
            # ป้องกันข้อผิดพลาดที่อาจเกิดขึ้น
            print(f"Error in update_progress: {e}")

    def update_urlbar(self, q, browser=None):
        """อัพเดท URL บาร์"""
        if browser != self.current_browser():
            return

        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

        # แสดง URL ในแถบสถานะ
        self.status.showMessage(q.toString())

    def tab_changed(self, index):
        """เมื่อเปลี่ยนแท็บ"""
        if index >= 0:
            # พักการทำงานของแท็บที่ไม่ได้ใช้งาน
            self.suspend_inactive_tabs(index)

            # อัพเดท URL บาร์
            browser = self.tabs.widget(index)
            if browser:
                self.update_urlbar(browser.url(), browser)

    def suspend_inactive_tabs(self, active_index):
        """พักการทำงานของแท็บที่ไม่ได้ใช้งาน"""
        try:
            # พักการทำงานของมีเดียในแท็บที่ไม่ได้ใช้งาน
            for i in range(self.tabs.count()):
                if i != active_index:  # ข้ามแท็บที่กำลังใช้งาน
                    browser = self.tabs.widget(i)
                    if browser:
                        # พักการเล่นมีเดียในแท็บที่ไม่ได้ใช้งาน
                        browser.page().runJavaScript("""
                            // พักการเล่นวิดีโอ
                            document.querySelectorAll('video').forEach(v => {
                                if (!v.paused) v.pause();
                            });

                            // พักการเล่นเสียง
                            document.querySelectorAll('audio').forEach(a => {
                                if (!a.paused) a.pause();
                            });
                        """)
        except Exception as e:
            print(f"Error suspending inactive tabs: {e}")

    def close_tab(self, index):
        """ปิดแท็บที่ระบุ"""
        if self.tabs.count() <= 1:
            self.close()
            return

        # ดึง browser widget ที่จะปิด
        browser = self.tabs.widget(index)
        if browser:
            try:
                # หยุดการเล่นมีเดียทั้งหมดในแท็บ
                browser.page().runJavaScript("""
                    // หยุดวิดีโอทั้งหมด
                    document.querySelectorAll('video').forEach(v => {
                        v.pause();
                        v.src = '';
                    });

                    // หยุดเสียงทั้งหมด
                    document.querySelectorAll('audio').forEach(a => {
                        a.pause();
                        a.src = '';
                    });

                    // หยุด iframe ที่อาจมีมีเดีย
                    document.querySelectorAll('iframe').forEach(i => {
                        i.src = 'about:blank';
                    });

                    // ล้างแหล่งข้อมูลมีเดีย
                    document.querySelectorAll('source').forEach(s => {
                        s.src = '';
                    });
                """)

                # ล้างหน่วยความจำและหยุดการทำงานของเพจ
                browser.stop()
                browser.page().deleteLater()
                browser.deleteLater()
            except Exception as e:
                print(f"Error cleaning up tab resources: {e}")

        # ลบแท็บ
        self.tabs.removeTab(index)

    def close_current_tab(self):
        """ปิดแท็บปัจจุบัน"""
        self.close_tab(self.tabs.currentIndex())

    def next_tab(self):
        """ไปแท็บถัดไป"""
        current = self.tabs.currentIndex()
        if current < self.tabs.count() - 1:
            self.tabs.setCurrentIndex(current + 1)

    def previous_tab(self):
        """ไปแท็บก่อนหน้า"""
        current = self.tabs.currentIndex()
        if current > 0:
            self.tabs.setCurrentIndex(current - 1)

    def switch_to_tab(self, index):
        """สลับไปแท็บที่ระบุ"""
        if index < self.tabs.count():
            self.tabs.setCurrentIndex(index)

    def navigate_to_url(self):
        """ไปยัง URL ที่ป้อน"""
        text = self.url_bar.text().strip()

        if not text:
            return

        # ตรวจสอบว่าเป็น URL หรือคำค้นหา
        if '.' in text and ' ' not in text:
            if not text.startswith(('http://', 'https://')):
                text = 'https://' + text
            qurl = QUrl(text)
        else:
            # ใช้เครื่องมือค้นหา
            search_url = self.settings.get('search_engine', 'https://www.google.com/search?q=')
            qurl = QUrl(search_url + text.replace(' ', '+'))

        self.navigate_in_current_tab(qurl)

    def navigate_in_current_tab(self, qurl):
        """นำทางในแท็บปัจจุบัน"""
        browser = self.current_browser()
        if browser:
            browser.setUrl(qurl)

            # บันทึกประวัติ (ยกเว้นโหมดส่วนตัว)
            if not self.private_mode:
                try:
                    title = browser.page().title()
                    if not title:
                        title = qurl.toString()
                    self.add_to_history(qurl.toString(), title)
                except Exception as e:
                    # ป้องกันข้อผิดพลาดที่อาจเกิดขึ้น
                    print(f"Error in navigate_in_current_tab: {e}")
                    self.add_to_history(qurl.toString(), qurl.toString())

    def add_to_history(self, url, title):
        """เพิ่มรายการในประวัติ"""
        self.settings['history'].append({
            'url': url,
            'title': title,
            'timestamp': int(time.time())
        })

        # จำกัดจำนวนประวัติ
        if len(self.settings['history']) > 500:
            self.settings['history'] = self.settings['history'][-500:]

        self.save_settings()

    def navigate_back(self):
        """ย้อนกลับ"""
        browser = self.current_browser()
        if browser:
            browser.back()

    def navigate_forward(self):
        """ไปข้างหน้า"""
        browser = self.current_browser()
        if browser:
            browser.forward()

    def refresh_page(self):
        """รีเฟรชหน้า"""
        browser = self.current_browser()
        if browser:
            browser.reload()

    def stop_loading(self):
        """หยุดโหลด"""
        browser = self.current_browser()
        if browser:
            browser.stop()

    def navigate_home(self):
        """กลับหน้าแรก"""
        self.navigate_in_current_tab(QUrl(self.settings['homepage']))

    def zoom_in(self):
        """ซูมเข้า"""
        browser = self.current_browser()
        if browser:
            browser.setZoomFactor(min(browser.zoomFactor() + 0.1, 3.0))

    def zoom_out(self):
        """ซูมออก"""
        browser = self.current_browser()
        if browser:
            browser.setZoomFactor(max(browser.zoomFactor() - 0.1, 0.25))

    def zoom_reset(self):
        """รีเซ็ตซูม"""
        browser = self.current_browser()
        if browser:
            browser.setZoomFactor(1.0)

    def toggle_fullscreen(self):
        """สลับโหมดเต็มหน้าจอ"""
        try:
            if self.isFullScreen():
                self.showNormal()
            else:
                # บันทึกสถานะก่อนเข้าโหมดเต็มหน้าจอ
                self.was_dark_mode = self.dark_mode

                # เข้าสู่โหมดเต็มหน้าจอ
                self.showFullScreen()

            # อัพเดทธีมเพื่อให้แน่ใจว่าสีถูกต้อง
            self.update_theme()

            # อัพเดทสถานะ
            mode = "เต็มหน้าจอ" if self.isFullScreen() else "ปกติ"
            self.status.showMessage(f"โหมด: {mode}", 3000)
        except Exception as e:
            print(f"Error in toggle_fullscreen: {e}")

    def toggle_dark_mode(self):
        """สลับโหมดกลางคืน"""
        try:
            # สลับโหมด
            self.dark_mode = not self.dark_mode

            # บันทึกการตั้งค่า
            self.settings['dark_mode'] = self.dark_mode
            self.save_settings()

            # อัพเดทธีมและป้ายสถานะ
            self.update_theme()
            self.update_mode_label()

            # แสดงข้อความแจ้งเตือน
            mode = "เปิด" if self.dark_mode else "ปิด"
            self.status.showMessage(f"โหมดกลางคืน: {mode}", 3000)

            # อัพเดทเนื้อหาเว็บ (ถ้าต้องการ)
            current_browser = self.current_browser()
            if current_browser:
                # รีเฟรชหน้าเว็บเพื่ออัพเดทสี
                current_browser.reload()
        except Exception as e:
            print(f"Error in toggle_dark_mode: {e}")

    def toggle_private_mode(self):
        """สลับโหมดส่วนตัว"""
        self.private_mode = not self.private_mode
        self.update_mode_label()
        self.status.showMessage(f"โหมดส่วนตัว: {'เปิด' if self.private_mode else 'ปิด'}", 3000)

    def update_mode_label(self):
        """อัพเดทป้ายโหมด"""
        modes = []
        if self.private_mode:
            modes.append("ส่วนตัว")
        if self.dark_mode:
            modes.append("กลางคืน")

        self.mode_label.setText(" | ".join(modes) if modes else "")

    def add_current_to_bookmarks(self):
        """เพิ่มหน้าปัจจุบันลงบุ๊กมาร์ก"""
        browser = self.current_browser()
        if not browser:
            return

        url = browser.url().toString()
        title = browser.page().title()

        # ถามชื่อและหมวดหมู่
        name, ok = QInputDialog.getText(self, 'เพิ่มบุ๊กมาร์ก', 'ชื่อ:', text=title)
        if not ok or not name:
            return

        categories = list(self.settings['bookmarks'].keys())
        category, ok = QInputDialog.getItem(
            self, 'เลือกหมวดหมู่', 'หมวดหมู่:',
            categories + ["สร้างหมวดหมู่ใหม่"], 0, False
        )

        if not ok:
            return

        if category == "สร้างหมวดหมู่ใหม่":
            category, ok = QInputDialog.getText(self, 'สร้างหมวดหมู่', 'ชื่อหมวดหมู่ใหม่:')
            if not ok or not category:
                return
            self.settings['bookmarks'][category] = []

        # เพิ่มบุ๊กมาร์กใหม่
        self.settings['bookmarks'][category].append({
            'name': name,
            'url': url
        })

        self.save_settings()
        QMessageBox.information(self, 'สำเร็จ', 'เพิ่มบุ๊กมาร์กเรียบร้อยแล้ว!')

    def manage_bookmarks(self):
        """จัดการบุ๊กมาร์ก"""
        QMessageBox.information(self, 'จัดการบุ๊กมาร์ก',
                              'ระบบจัดการบุ๊กมาร์กแบบเต็มจะมาในเวอร์ชันถัดไป!')

    def show_history(self):
        """แสดงประวัติ"""
        from datetime import datetime
        history_text = ""

        for item in reversed(self.settings['history'][-20:]):
            dt = datetime.fromtimestamp(item['timestamp'])
            history_text += f"{dt.strftime('%Y-%m-%d %H:%M')} - {item['title']}\n{item['url']}\n\n"

        QMessageBox.information(self, 'ประวัติการเข้าชม', history_text or 'ไม่มีประวัติ')

    def clear_history(self):
        """ล้างประวัติ"""
        reply = QMessageBox.question(
            self, 'ยืนยันการล้างประวัติ',
            'คุณแน่ใจว่าต้องการล้างประวัติการเข้าชมทั้งหมด?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.settings['history'] = []
            self.save_settings()
            QMessageBox.information(self, 'สำเร็จ', 'ล้างประวัติเรียบร้อยแล้ว')

    def clear_browsing_data(self):
        """เคลียร์ข้อมูลการท่องเว็บ"""
        items = ['ประวัติการเข้าชม', 'คุกกี้และข้อมูลไซต์', 'แคชและไฟล์ชั่วคราว']

        item, ok = QInputDialog.getItem(
            self, 'เคลียร์ข้อมูลการท่องเว็บ',
            'เลือกประเภทข้อมูลที่จะล้าง:', items, 0, False
        )

        if ok and item:
            if item == 'ประวัติการเข้าชม':
                self.settings['history'] = []
                self.save_settings()
                QMessageBox.information(self, 'สำเร็จ', 'ล้างประวัติเรียบร้อยแล้ว')
            else:
                QMessageBox.information(self, 'กำลังพัฒนา',
                                      'ฟังก์ชันนี้จะพร้อมใช้งานในเวอร์ชันถัดไป')

    def download_requested(self, download: QWebEngineDownloadItem):
        """จัดการการดาวน์โหลด"""
        # ตั้งค่า path เริ่มต้น
        download_dir = self.settings.get('download_location',
                                       QStandardPaths.writableLocation(QStandardPaths.DownloadLocation))
        default_path = os.path.join(download_dir, download.url().fileName())

        # ถามตำแหน่งบันทึก
        path, _ = QFileDialog.getSaveFileName(
            self, "บันทึกไฟล์", default_path,
            "ไฟล์ทั้งหมด (*);;ไฟล์ข้อความ (*.txt);;ไฟล์รูปภาพ (*.png *.jpg *.jpeg)"
        )

        if path:
            download.setPath(path)
            download.accept()

            # บันทึกข้อมูลดาวน์โหลด
            self.downloads.append({
                'path': path,
                'url': download.url().toString(),
                'start_time': time.time()
            })

            # แสดงสถานะ
            self.status.showMessage(f'กำลังดาวน์โหลด: {os.path.basename(path)}')

            # เชื่อมต่อสัญญาณ
            download.finished.connect(lambda: self.download_finished(path))
            download.downloadProgress.connect(
                lambda bytes_received, bytes_total:
                    self.update_download_progress(path, bytes_received, bytes_total))

    def download_finished(self, path):
        """เมื่อดาวน์โหลดเสร็จสิ้น"""
        self.status.showMessage(f'ดาวน์โหลดเสร็จสิ้น: {os.path.basename(path)}', 5000)

        # เปิดไฟล์ที่ดาวน์โหลด (ถามผู้ใช้ก่อน)
        reply = QMessageBox.question(
            self, 'ดาวน์โหลดเสร็จสิ้น',
            'ต้องการเปิดไฟล์ที่ดาวน์โหลดหรือไม่?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def update_download_progress(self, path, bytes_received, bytes_total):
        """อัพเดทความคืบหน้าการดาวน์โหลด"""
        if bytes_total > 0:
            percent = int((bytes_received / bytes_total) * 100)
            self.status.showMessage(
                f'กำลังดาวน์โหลด {os.path.basename(path)}: {percent}%', 1000)

    def show_downloads(self):
        """แสดงรายการดาวน์โหลด"""
        if not self.downloads:
            QMessageBox.information(self, 'ดาวน์โหลด', 'ไม่มีรายการดาวน์โหลด')
            return

        downloads_text = "\n".join([
            f"{os.path.basename(d['path'])} - {d['url']}"
            for d in self.downloads[-10:]
        ])

        QMessageBox.information(self, 'ดาวน์โหลดล่าสุด', downloads_text)

    def print_page(self):
        """พิมพ์หน้าเว็บ"""
        browser = self.current_browser()
        if not browser:
            return

        printer = QPrinter()
        dialog = QPrintDialog(printer, self)

        if dialog.exec_() == QPrintDialog.Accepted:
            browser.page().print(printer, lambda _: None)

    def save_page(self):
        """บันทึกหน้าเว็บ"""
        browser = self.current_browser()
        if not browser:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "บันทึกหน้าเว็บ",
            os.path.join(
                self.settings.get('download_location',
                                QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)),
                browser.page().title() + '.html'
            ),
            "เว็บเพจ (*.html *.htm);;ไฟล์ข้อความ (*.txt);;ไฟล์ทั้งหมด (*)"
        )

        if path:
            browser.page().save(path)
            self.status.showMessage(f'บันทึกหน้าเว็บเรียบร้อยที่ {path}', 5000)

    def find_in_page(self):
        """ค้นหาในหน้า"""
        browser = self.current_browser()
        if not browser:
            return

        text, ok = QInputDialog.getText(self, 'ค้นหาในหน้า', 'คำค้นหา:')
        if ok and text:
            browser.findText(text)

    def toggle_dev_tools(self):
        """สลับเครื่องมือนักพัฒนา"""
        browser = self.current_browser()
        if browser:
            browser.page().setDevToolsPage(browser.page().devToolsPage())
            browser.page().triggerAction(QWebEnginePage.InspectElement)

    def show_js_console(self):
        """แสดงคอนโซล JavaScript"""
        browser = self.current_browser()
        if browser:
            browser.page().runJavaScript("console.log('เปิดคอนโซล JavaScript');")
            self.toggle_dev_tools()

    def show_extensions(self):
        """แสดงส่วนขยาย"""
        QMessageBox.information(self, 'ส่วนขยาย',
                              'ระบบส่วนขยายจะมาในเวอร์ชันถัดไป!')

    def show_settings(self):
        """แสดงหน้าตั้งค่า"""
        QMessageBox.information(self, 'ตั้งค่า',
                              'หน้าตั้งค่าแบบเต็มจะมาในเวอร์ชันถัดไป!')

    def setup_proxy(self):
        """ตั้งค่า proxy"""
        QMessageBox.information(self, 'ตั้งค่า Proxy',
                              'การตั้งค่า Proxy จะมาในเวอร์ชันถัดไป!')

    def show_main_menu(self):
        """แสดงเมนูหลัก"""
        menu = QMenu(self)

        actions = [
            ('แท็บใหม่', 'Ctrl+T', lambda: self.add_new_tab()),
            ('แท็บส่วนตัว', 'Ctrl+Shift+N', lambda: self.add_new_tab(QUrl(self.settings['homepage']), "แท็บส่วนตัว", private=True)),
            ('ปิดแท็บปัจจุบัน', 'Ctrl+W', self.close_current_tab),
            None,
            ('ประวัติ', 'Ctrl+H', self.show_history),
            ('ดาวน์โหลด', 'Ctrl+J', self.show_downloads),
            None,
            ('ตั้งค่า', 'Ctrl+,', self.show_settings),
            ('เกี่ยวกับ', None, self.show_about),
            None,
            ('ออกจากระบบ', 'Ctrl+Q', self.close)
        ]

        self.add_menu_actions(menu, actions)

        menu.exec_(self.main_toolbar.mapToGlobal(
            self.main_toolbar.actions()[-1].associatedWidgets()[-1].pos() +
            QPoint(0, self.main_toolbar.actions()[-1].associatedWidgets()[-1].height())
        ))

    def show_about(self):
        """แสดงเกี่ยวกับโปรแกรม"""
        about_text = f"""
        <b>{self.app_name}</b><br><br>
        เวอร์ชัน {self.version}<br>
        สร้างด้วย Python และ PyQt5<br><br>
        คุณสมบัติ:<br>
        - ระบบแท็บขั้นสูง<br>
        - โหมดส่วนตัว<br>
        - โหมดกลางคืน<br>
        - การจัดการบุ๊กมาร์ก<br>
        - ประวัติการเข้าชม<br>
        - ระบบดาวน์โหลด<br>
        - เครื่องมือนักพัฒนา<br><br>
        © 2023 ผู้พัฒนาซอฟต์แวร์
        """

        QMessageBox.about(self, "เกี่ยวกับโปรแกรม", about_text)

    def check_for_updates(self):
        """ตรวจสอบอัปเดต"""
        QMessageBox.information(self, "ตรวจสอบอัปเดต",
                              "คุณกำลังใช้เวอร์ชันล่าสุดแล้ว")

    def show_documentation(self):
        """แสดงเอกสารประกอบ"""
        webbrowser.open("https://github.com/yourusername/ultimate-browser/wiki")

    def report_issue(self):
        """รายงานปัญหา"""
        webbrowser.open("https://github.com/yourusername/ultimate-browser/issues/new")

    def show_shortcuts(self):
        """แสดงปุ่มลัด"""
        shortcuts = """
        <b>ปุ่มลัดหลัก:</b><br>
        Ctrl+T - แท็บใหม่<br>
        Ctrl+W - ปิดแท็บปัจจุบัน<br>
        Ctrl+Tab - แท็บถัดไป<br>
        Ctrl+Shift+Tab - แท็บก่อนหน้า<br>
        Ctrl+1-8 - ไปแท็บที่ 1-8<br>
        Ctrl+9 - ไปแท็บสุดท้าย<br>
        Alt+Left - ย้อนกลับ<br>
        Alt+Right - ไปข้างหน้า<br>
        F5 - รีเฟรช<br>
        Ctrl+F - ค้นหาในหน้า<br>
        F11 - โหมดเต็มหน้าจอ<br>
        Ctrl+Shift+D - โหมดกลางคืน<br>
        Ctrl+Shift+P - โหมดส่วนตัว<br>
        F12 - เครื่องมือนักพัฒนา<br><br>
        <b>การนำทาง:</b><br>
        Alt+Home - หน้าแรก<br>
        Ctrl+L - โฟกัสที่แถบที่อยู่<br>
        Ctrl+Enter - เพิ่ม www. และ .com<br><br>
        <b>อื่นๆ:</b><br>
        Ctrl+Shift+Del - เคลียร์ข้อมูลการท่องเว็บ<br>
        Ctrl+, - ตั้งค่า<br>
        F1 - วิธีใช้
        """

        QMessageBox.information(self, "ปุ่มลัด", shortcuts)

    def new_window(self):
        """หน้าต่างใหม่"""
        new_browser = UniqueBrowser()
        new_browser.show()

    def new_private_window(self):
        """หน้าต่างส่วนตัว"""
        new_browser = UniqueBrowser()
        new_browser.private_mode = True
        new_browser.update_mode_label()
        new_browser.show()

    def focus_url_bar(self):
        """โฟกัสที่แถบ URL"""
        self.url_bar.setFocus()
        self.url_bar.selectAll()

    def cut(self):
        """ตัด"""
        browser = self.current_browser()
        if browser:
            browser.page().triggerAction(QWebEnginePage.Cut)

    def copy(self):
        """คัดลอก"""
        browser = self.current_browser()
        if browser:
            browser.page().triggerAction(QWebEnginePage.Copy)

    def paste(self):
        """วาง"""
        browser = self.current_browser()
        if browser:
            browser.page().triggerAction(QWebEnginePage.Paste)

    def select_all(self):
        """เลือกทั้งหมด"""
        browser = self.current_browser()
        if browser:
            browser.page().triggerAction(QWebEnginePage.SelectAll)

    def toggle_toolbar(self):
        """สลับแสดงแถบเครื่องมือ"""
        self.main_toolbar.setVisible(not self.main_toolbar.isVisible())

    def show_import_export(self):
        """นำเข้า/ส่งออกข้อมูล"""
        QMessageBox.information(self, "นำเข้า/ส่งออก",
                              "ระบบนำเข้า/ส่งออกจะมาในเวอร์ชันถัดไป!")

    def closeEvent(self, event):
        """ยืนยันก่อนปิดโปรแกรม"""
        # บันทึกขนาดหน้าต่างล่าสุด
        self.settings['window_size'] = {
            'width': self.width(),
            'height': self.height()
        }
        self.save_settings()

        reply = QMessageBox.question(
            self, 'ยืนยันการปิดโปรแกรม',
            'คุณแน่ใจว่าต้องการปิดเบราว์เซอร์?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # ทำความสะอาดทุกแท็บก่อนปิดโปรแกรม
            self.cleanup_all_tabs()
            event.accept()
        else:
            event.ignore()

    def cleanup_all_tabs(self):
        """ทำความสะอาดทรัพยากรทั้งหมดในทุกแท็บ"""
        try:
            # หยุดการเล่นมีเดียในทุกแท็บ
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                if browser:
                    # หยุดการโหลดและการเล่นมีเดีย
                    browser.stop()

                    # รันสคริปต์ JavaScript เพื่อหยุดมีเดียทั้งหมด
                    browser.page().runJavaScript("""
                        // หยุดวิดีโอทั้งหมด
                        document.querySelectorAll('video').forEach(v => {
                            v.pause();
                            v.src = '';
                            v.load();
                        });

                        // หยุดเสียงทั้งหมด
                        document.querySelectorAll('audio').forEach(a => {
                            a.pause();
                            a.src = '';
                            a.load();
                        });

                        // หยุด iframe ที่อาจมีมีเดีย
                        document.querySelectorAll('iframe').forEach(i => {
                            i.src = 'about:blank';
                        });

                        // ล้างแหล่งข้อมูลมีเดีย
                        document.querySelectorAll('source').forEach(s => {
                            s.src = '';
                        });

                        // ล้างแคช
                        if (window.caches) {
                            caches.keys().then(function(names) {
                                for (let name of names) caches.delete(name);
                            });
                        }
                    """)

                    # ล้างหน่วยความจำ
                    browser.page().deleteLater()

            # ล้างแคชของ WebEngine
            QWebEngineProfile.defaultProfile().clearHttpCache()

        except Exception as e:
            print(f"Error cleaning up tabs: {e}")

    def check_wayland(self):
        """ตรวจสอบว่ากำลังใช้ Wayland หรือไม่"""
        if not self.is_linux:
            return False

        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        xdg_session_type = os.environ.get('XDG_SESSION_TYPE')

        return wayland_display is not None or xdg_session_type == 'wayland'

    def setup_video_support(self):
        """ตั้งค่าการรองรับวิดีโอเพิ่มเติม"""
        try:
            # ตรวจสอบและติดตั้งโคเดกที่จำเป็นสำหรับ Linux
            if self.is_linux:
                # ตรวจสอบว่ามีโคเดกที่จำเป็นหรือไม่
                codecs_installed = False

                try:
                    # ตรวจสอบว่ามี gstreamer plugins หรือไม่
                    result = subprocess.run(
                        ["gst-inspect-1.0", "playbin"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    codecs_installed = result.returncode == 0
                except:
                    codecs_installed = False

                if not codecs_installed:
                    # แสดงข้อความแนะนำการติดตั้งโคเดก
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("ต้องการโคเดกเพิ่มเติม")
                    msg.setText("เบราว์เซอร์ต้องการโคเดกเพิ่มเติมเพื่อเล่นวิดีโอ")
                    msg.setInformativeText(
                        "คุณอาจต้องติดตั้งแพ็คเกจต่อไปนี้เพื่อรองรับการเล่นวิดีโอ:\n\n"
                        "สำหรับ Ubuntu/Debian:\n"
                        "sudo apt install gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav\n\n"
                        "สำหรับ Fedora:\n"
                        "sudo dnf install gstreamer1-plugins-base gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-ugly gstreamer1-libav\n\n"
                        "สำหรับ Arch Linux:\n"
                        "sudo pacman -S gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly gst-libav"
                    )
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()

            # ตั้งค่าเพิ่มเติมสำหรับการเล่นวิดีโอ
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                if browser:
                    # ตั้งค่า page ให้รองรับการเล่นวิดีโอ
                    page = browser.page()

                    # อนุญาตให้เล่นวิดีโอโดยไม่ต้องมีการโต้ตอบจากผู้ใช้
                    page.settings().setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)

                    # อนุญาตให้เข้าถึงเนื้อหาจากแหล่งอื่น
                    page.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)

                    # เปิดใช้งาน WebGL และ WebAudio
                    page.settings().setAttribute(QWebEngineSettings.WebGLEnabled, True)
                    if hasattr(QWebEngineSettings, 'WebAudioEnabled'):
                        page.settings().setAttribute(QWebEngineSettings.WebAudioEnabled, True)

            print("Video support configured successfully")
        except Exception as e:
            print(f"Error setting up video support: {e}")

    def create_desktop_shortcut(self):
        """สร้างทางลัดบนเดสก์ท็อปสำหรับ Linux"""
        if not self.is_linux:
            QMessageBox.information(self, "ไม่รองรับ", "ฟีเจอร์นี้รองรับเฉพาะบน Linux เท่านั้น")
            return

        try:
            # สร้างไฟล์ .desktop
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop_path, "unique-browser.desktop")

            # ตรวจสอบว่าโฟลเดอร์ Desktop มีอยู่หรือไม่
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~")
                shortcut_path = os.path.join(desktop_path, "unique-browser.desktop")

            # หาตำแหน่งของไฟล์ปัจจุบัน
            current_file = os.path.abspath(sys.argv[0])

            # หาตำแหน่งของไอคอน
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "unique_browser.ico")
            if not os.path.exists(icon_path):
                # ใช้ไอคอนเริ่มต้นถ้าไม่พบไอคอนที่สร้างขึ้น
                icon_path = "web-browser"

            with open(shortcut_path, 'w') as f:
                f.write(f"""[Desktop Entry]
Name=Unique Browser
Comment=A lightweight and feature-rich web browser
Exec=python3 {current_file}
Icon={icon_path}
Terminal=false
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/rss+xml;application/rdf+xml;x-scheme-handler/http;x-scheme-handler/https;
""")

            # ทำให้ไฟล์สามารถเรียกใช้งานได้
            os.chmod(shortcut_path, 0o755)

            QMessageBox.information(self, "สำเร็จ", f"สร้างทางลัดบนเดสก์ท็อปแล้วที่:\n{shortcut_path}")

        except Exception as e:
            QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถสร้างทางลัดได้: {str(e)}")

    def optimize_for_linux(self):
        """ปรับแต่งเบราว์เซอร์ให้เหมาะสมกับ Linux"""
        if not self.is_linux:
            QMessageBox.information(self, "ไม่รองรับ", "ฟีเจอร์นี้รองรับเฉพาะบน Linux เท่านั้น")
            return

        try:
            # ปรับแต่งการตั้งค่าสำหรับ Linux
            settings = QWebEngineSettings.globalSettings()

            # เปิดใช้งานฮาร์ดแวร์แอคเซลเลอเรชัน
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)

            # ปรับแต่งสำหรับ Wayland ถ้าจำเป็น
            if self.is_wayland:
                # ตั้งค่าเฉพาะสำหรับ Wayland
                os.environ["QT_QPA_PLATFORM"] = "wayland"

            # ปรับแต่งฟอนต์ให้เหมาะสมกับ Linux
            font = QApplication.font()
            font.setFamily("Noto Sans")  # ฟอนต์ที่มีในระบบ Linux ส่วนใหญ่
            QApplication.setFont(font)

            # ปรับแต่งการใช้งานหน่วยความจำ
            QWebEngineProfile.defaultProfile().setHttpCacheMaximumSize(100 * 1024 * 1024)  # 100MB cache

            QMessageBox.information(self, "สำเร็จ", "ปรับแต่งเบราว์เซอร์สำหรับ Linux แล้ว")

        except Exception as e:
            QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถปรับแต่งได้: {str(e)}")

    def setup_linux_integration(self):
        """ตั้งค่าการทำงานร่วมกับระบบ Linux"""
        if not self.is_linux:
            return

        # เพิ่มเมนูสำหรับ Linux
        linux_menu = self.menuBar().addMenu("&Linux")

        # เพิ่มตัวเลือกในเมนู
        actions = [
            ('สร้างทางลัดบนเดสก์ท็อป', None, self.create_desktop_shortcut),
            ('ปรับแต่งสำหรับ Linux', None, self.optimize_for_linux),
            None,  # Separator
            ('ตั้งเป็นเบราว์เซอร์เริ่มต้น', None, self.set_as_default_browser),
            ('เปิดใช้งานการแจ้งเตือนระบบ', None, self.toggle_system_notifications)
        ]

        self.add_menu_actions(linux_menu, actions)

    def set_as_default_browser(self):
        """ตั้งเป็นเบราว์เซอร์เริ่มต้นบน Linux"""
        if not self.is_linux:
            QMessageBox.information(self, "ไม่รองรับ", "ฟีเจอร์นี้รองรับเฉพาะบน Linux เท่านั้น")
            return

        try:
            # หาตำแหน่งของไฟล์ปัจจุบัน
            current_file = os.path.abspath(sys.argv[0])

            # หาตำแหน่งของไอคอน
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "unique_browser.ico")
            if not os.path.exists(icon_path):
                # ใช้ไอคอนเริ่มต้นถ้าไม่พบไอคอนที่สร้างขึ้น
                icon_path = "web-browser"

            # สร้างไฟล์ .desktop ในตำแหน่งที่ถูกต้อง
            desktop_file = os.path.expanduser("~/.local/share/applications/unique-browser.desktop")
            os.makedirs(os.path.dirname(desktop_file), exist_ok=True)

            with open(desktop_file, 'w') as f:
                f.write(f"""[Desktop Entry]
Name=Unique Browser
Comment=A lightweight and feature-rich web browser
Exec=python3 {current_file} %U
Icon={icon_path}
Terminal=false
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/rss+xml;application/rdf+xml;x-scheme-handler/http;x-scheme-handler/https;
""")

            # ทำให้ไฟล์สามารถเรียกใช้งานได้
            os.chmod(desktop_file, 0o755)

            # ตั้งค่าเป็นเบราว์เซอร์เริ่มต้น
            subprocess.run(["xdg-settings", "set", "default-web-browser", "unique-browser.desktop"])

            QMessageBox.information(self, "สำเร็จ", "ตั้งค่า Unique Browser เป็นเบราว์เซอร์เริ่มต้นแล้ว")

        except Exception as e:
            QMessageBox.warning(self, "ข้อผิดพลาด", f"ไม่สามารถตั้งค่าเป็นเบราว์เซอร์เริ่มต้นได้: {str(e)}")

    def toggle_system_notifications(self):
        """เปิด/ปิดการแจ้งเตือนระบบบน Linux"""
        if not self.is_linux:
            QMessageBox.information(self, "ไม่รองรับ", "ฟีเจอร์นี้รองรับเฉพาะบน Linux เท่านั้น")
            return

        # สลับการตั้งค่า
        current_setting = self.settings.get('system_notifications', False)
        self.settings['system_notifications'] = not current_setting
        self.save_settings()

        status = "เปิด" if self.settings['system_notifications'] else "ปิด"
        QMessageBox.information(self, "การแจ้งเตือนระบบ", f"การแจ้งเตือนระบบถูก{status}แล้ว")

def main():
    """ฟังก์ชันหลักสำหรับการรันแอปพลิเคชัน"""
    app = QApplication(sys.argv)

    # ตั้งค่าฟอนต์
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    # สร้างและแสดงเบราว์เซอร์
    browser = UniqueBrowser()
    browser.show()

    # ตั้งค่าการทำงานร่วมกับ Linux ถ้าจำเป็น
    if platform.system() == "Linux":
        browser.setup_linux_integration()

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())