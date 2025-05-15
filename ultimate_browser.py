import sys
import os
import time
import json
import webbrowser
from PyQt5.QtCore import QUrl, Qt, QStandardPaths, QTimer, QSize, QPoint
from PyQt5.QtGui import QIcon, QKeySequence, QDesktopServices, QColor, QPalette
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QToolBar, QLineEdit,
                            QAction, QMenu, QMessageBox, QStatusBar, QFileDialog,
                            QInputDialog, QShortcut, QLabel, QStyleFactory, QSystemTrayIcon)
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

class UltimateBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # ตั้งค่าพื้นฐาน
        self.app_name = "Ultimate Browser"
        self.version = "3.0"
        self.dark_mode = False
        self.private_mode = False
        self.downloads = []
        self.extensions = []

        # ตั้งค่าหน้าต่าง
        self.setWindowTitle(self.app_name)
        # ไม่ใช้ไอคอนเนื่องจากไม่มีไฟล์
        # self.setWindowIcon(QIcon(self.resource_path('icons/browser.png')))
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
            "UltimateBrowser",
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

            # เปิดใช้งาน HTML5 Storage APIs
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

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
            ('ตั้งค่าโปรxy...', None, self.setup_proxy),
            ('เคลียร์ข้อมูลการท่องเว็บ...', None, self.clear_browsing_data)
        ]

        self.add_menu_actions(menu, actions)

    def setup_help_menu(self, menu):
        """ตั้งค่าเมนู Help"""
        actions = [
            ('เกี่ยวกับ Ultimate Browser', None, self.show_about),
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
        # ปิดการใช้งาน Tray Icon เนื่องจากไม่มีไอคอน
        pass

    def tray_icon_activated(self, reason):
        """เมื่อคลิกที่ tray icon"""
        if reason == QSystemTrayIcon.Trigger:
            self.show()
            self.activateWindow()

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
            browser = self.tabs.widget(index)
            if browser:
                self.update_urlbar(browser.url(), browser)

    def close_tab(self, index):
        """ปิดแท็บที่ระบุ"""
        if self.tabs.count() <= 1:
            self.close()
            return

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
        new_browser = UltimateBrowser()
        new_browser.show()

    def new_private_window(self):
        """หน้าต่างส่วนตัว"""
        new_browser = UltimateBrowser()
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
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ตั้งค่าฟอนต์
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    # สร้างและแสดงเบราว์เซอร์
    browser = UltimateBrowser()
    browser.show()

    sys.exit(app.exec_())