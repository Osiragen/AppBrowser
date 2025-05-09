#!/bin/bash

# Create Desktop Shortcut for Unique Browser
# This script creates a desktop shortcut for Unique Browser

echo "=== Creating Desktop Shortcut for Unique Browser ==="

# Get the current directory
CURRENT_DIR=$(pwd)

# Create desktop shortcut
DESKTOP_FILE="$HOME/Desktop/unique-browser.desktop"

echo "Creating desktop shortcut..."
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Unique Browser
Comment=A lightweight and feature-rich web browser
Exec=python3 $CURRENT_DIR/unique_browser.py
Icon=web-browser
Terminal=false
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/rss+xml;application/rdf+xml;x-scheme-handler/http;x-scheme-handler/https;
EOF

# Make the desktop file executable
chmod +x "$DESKTOP_FILE"

echo "Desktop shortcut created successfully at $DESKTOP_FILE"
echo "You can now launch Unique Browser from your desktop."
