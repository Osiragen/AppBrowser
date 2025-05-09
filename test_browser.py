#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test suite for Unique Browser
This file contains unit tests for the Unique Browser application.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl

# Create a QApplication instance for testing
app = QApplication(sys.argv)

# Import the browser module
try:
    from unique_browser import MainWindow, Browser, UrlBar
except ImportError:
    print("Error: Could not import browser modules. Make sure unique_browser.py is in the same directory.")
    sys.exit(1)

class TestBrowser(unittest.TestCase):
    """Test cases for the Browser class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.browser = Browser()
    
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
    """Test cases for the UrlBar class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.urlbar = UrlBar()
    
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

class TestMainWindow(unittest.TestCase):
    """Test cases for the MainWindow class"""
    
    @patch('unique_browser.Browser')
    def setUp(self, mock_browser):
        """Set up test fixtures with mocked Browser"""
        self.main_window = MainWindow()
        self.main_window.browser = mock_browser
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.main_window = None
    
    def test_main_window_initialization(self):
        """Test main window initialization"""
        self.assertIsNotNone(self.main_window)
        self.assertIsNotNone(self.main_window.tabs)
    
    def test_add_new_tab(self):
        """Test adding a new tab"""
        initial_tab_count = len(self.main_window.tabs)
        self.main_window.add_new_tab()
        self.assertEqual(len(self.main_window.tabs), initial_tab_count + 1)
    
    def test_close_tab(self):
        """Test closing a tab"""
        # Add a tab first
        self.main_window.add_new_tab()
        initial_tab_count = len(self.main_window.tabs)
        
        # Close the tab
        self.main_window.close_current_tab(0)
        self.assertEqual(len(self.main_window.tabs), initial_tab_count - 1)

if __name__ == "__main__":
    unittest.main()
