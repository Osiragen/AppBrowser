#!/bin/bash

# Unique Browser Installation Script
# This script installs Unique Browser and creates a desktop shortcut

echo "=== Unique Browser Installation ==="
echo "Installing Unique Browser..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Install required dependencies
echo "Installing required dependencies..."
pip3 install PyQt5 PyQtWebEngine

# Create directory for the application
INSTALL_DIR="$HOME/.local/share/unique-browser"
mkdir -p "$INSTALL_DIR"

# Copy application files
echo "Copying application files..."
cp unique_browser.py "$INSTALL_DIR/"
cp ultimate_browser.py "$INSTALL_DIR/" 2>/dev/null || echo "Warning: ultimate_browser.py not found, skipping..."
cp README.md "$INSTALL_DIR/" 2>/dev/null || echo "Warning: README.md not found, skipping..."
cp test_browser.py "$INSTALL_DIR/" 2>/dev/null || echo "Warning: test_browser.py not found, skipping..."

# Create executable script
EXECUTABLE="$HOME/.local/bin/unique-browser"
mkdir -p "$HOME/.local/bin"

echo "Creating executable script..."
cat > "$EXECUTABLE" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 "$INSTALL_DIR/unique_browser.py" "\$@"
EOF

chmod +x "$EXECUTABLE"

# Create desktop shortcut
DESKTOP_FILE="$HOME/.local/share/applications/unique-browser.desktop"

echo "Creating desktop shortcut..."
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Unique Browser
Comment=A lightweight and feature-rich web browser
Exec=$EXECUTABLE %U
Icon=web-browser
Terminal=false
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/rss+xml;application/rdf+xml;x-scheme-handler/http;x-scheme-handler/https;
EOF

echo "Installation completed successfully!"
echo "You can now launch Unique Browser from your application menu or by running 'unique-browser' in terminal."
echo ""
echo "Thank you for installing Unique Browser!"
