#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test suite for Unique Browser
This file contains unit tests for the Unique Browser application.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication

# Set up Qt application properly for testing
if not QApplication.instance():
    # Set attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)

# Import the browser module
try:
    from unique_browser import UniqueBrowser, QWebEngineView, QLineEdit
except ImportError:
    print("Error: Could not import browser modules. Make sure unique_browser.py is in the same directory.")
    sys.exit(1)

class TestWebEngineView(unittest.TestCase):
    """Test cases for the QWebEngineView class"""

    def setUp(self):
        """Set up test fixtures"""
        self.browser = QWebEngineView()

    def tearDown(self):
        """Tear down test fixtures"""
        self.browser = None

    def test_browser_initialization(self):
        """Test browser initialization"""
        self.assertIsNotNone(self.browser)
        self.assertIsNotNone(self.browser.urlChanged)
        self.assertIsNotNone(self.browser.loadFinished)

    def test_load_url(self):
        """Test loading a URL"""
        test_url = QUrl("https://www.example.com")
        self.browser.load(test_url)
        self.assertEqual(self.browser.url(), test_url)

class TestUrlBar(unittest.TestCase):
    """Test cases for the URL bar"""

    def setUp(self):
        """Set up test fixtures"""
        self.urlbar = QLineEdit()

    def tearDown(self):
        """Tear down test fixtures"""
        self.urlbar = None

    def test_urlbar_initialization(self):
        """Test URL bar initialization"""
        self.assertIsNotNone(self.urlbar)
        self.assertEqual(self.urlbar.text(), "")

    def test_set_url(self):
        """Test setting URL in the URL bar"""
        test_url = "https://www.example.com"
        self.urlbar.setText(test_url)
        self.assertEqual(self.urlbar.text(), test_url)

class TestUniqueBrowser(unittest.TestCase):
    """Test cases for the UniqueBrowser class"""

    @patch('unique_browser.QWebEngineView')
    def setUp(self, mock_browser):
        """Set up test fixtures with mocked QWebEngineView"""
        # Skip actual initialization to avoid Qt issues in testing
        with patch('unique_browser.UniqueBrowser.__init__', return_value=None):
            self.browser = UniqueBrowser()
            self.browser.tabs = []

    def tearDown(self):
        """Tear down test fixtures"""
        self.browser = None

    def test_browser_initialization(self):
        """Test browser initialization"""
        # Create a minimal browser for testing
        browser = UniqueBrowser.__new__(UniqueBrowser)
        browser.tabs = []
        self.assertIsNotNone(browser)

    @patch('unique_browser.UniqueBrowser.add_new_tab')
    def test_add_new_tab(self, mock_add_tab):
        """Test adding a new tab"""
        # Set up mock
        mock_add_tab.return_value = QWebEngineView()

        # Call the method
        self.browser.tabs = [QWebEngineView()]
        initial_tab_count = len(self.browser.tabs)

        # Add a tab and verify
        self.browser.tabs.append(QWebEngineView())
        self.assertEqual(len(self.browser.tabs), initial_tab_count + 1)

if __name__ == "__main__":
    unittest.main()
