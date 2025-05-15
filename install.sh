#!/bin/bash

# Unique Browser Installation Script
# This script installs Unique Browser and creates a desktop shortcut

echo "=== Unique Browser Installation ==="
echo "Installing Unique Browser..."

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif type lsb_release >/dev/null 2>&1; then
        DISTRO=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        DISTRO=$DISTRIB_ID
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    else
        DISTRO=$(uname -s)
    fi
    echo $DISTRO
}

# Get the Linux distribution
DISTRO=$(detect_distro)
echo "Detected Linux distribution: $DISTRO"

# Install system dependencies based on distribution
echo "Installing system dependencies..."

case $DISTRO in
    ubuntu|debian|linuxmint|pop|elementary|zorin)
        echo "Using apt package manager..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-pyqt5 python3-pyqt5.qtwebengine python3-pyqt5.qtwebchannel \
            python3-pyqt5.qtprintsupport python3-pyqt5.qtsvg python3-pillow xdg-utils
        ;;
    fedora|centos|rhel)
        echo "Using dnf package manager..."
        sudo dnf -y install python3 python3-pip python3-qt5 python3-qt5-webengine python3-pillow xdg-utils
        ;;
    arch|manjaro|endeavouros)
        echo "Using pacman package manager..."
        sudo pacman -Sy --noconfirm python python-pip python-pyqt5 python-pyqt5-webengine python-pillow xdg-utils
        ;;
    opensuse|suse)
        echo "Using zypper package manager..."
        sudo zypper -n install python3 python3-pip python3-qt5 python3-qt5-webengine python3-Pillow xdg-utils
        ;;
    *)
        echo "Unsupported distribution. Trying to install dependencies with pip..."
        # Check if Python is installed
        if ! command -v python3 &> /dev/null; then
            echo "Python 3 is not installed. Please install Python 3 and try again."
            exit 1
        fi

        # Check if pip is installed
        if ! command -v pip3 &> /dev/null; then
            echo "pip3 is not installed. Please install pip3 and try again."
            exit 1
        fi

        # Install dependencies with pip
        pip3 install --user PyQt5 PyQtWebEngine Pillow
        ;;
esac

# Verify Python and pip are installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 installation failed. Please install Python 3 manually and try again."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip3 installation failed. Please install pip3 manually and try again."
    exit 1
fi

# Install Python dependencies that might not be covered by system packages
echo "Installing additional Python dependencies..."
pip3 install --user PyQt5 PyQtWebEngine Pillow

# Create directories for the application
INSTALL_DIR="$HOME/.local/share/unique-browser"
BIN_DIR="$HOME/.local/bin"
ICONS_DIR="$HOME/.local/share/icons/hicolor"
APPLICATIONS_DIR="$HOME/.local/share/applications"

echo "Creating application directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$APPLICATIONS_DIR"
mkdir -p "$ICONS_DIR/16x16/apps"
mkdir -p "$ICONS_DIR/32x32/apps"
mkdir -p "$ICONS_DIR/48x48/apps"
mkdir -p "$ICONS_DIR/64x64/apps"
mkdir -p "$ICONS_DIR/128x128/apps"
mkdir -p "$ICONS_DIR/256x256/apps"

# Copy application files
echo "Copying application files..."
cp unique_browser.py "$INSTALL_DIR/"
cp ultimate_browser.py "$INSTALL_DIR/" 2>/dev/null || echo "Warning: ultimate_browser.py not found, skipping..."
cp README.md "$INSTALL_DIR/" 2>/dev/null || echo "Warning: README.md not found, skipping..."
cp test_browser.py "$INSTALL_DIR/" 2>/dev/null || echo "Warning: test_browser.py not found, skipping..."

# Copy create_icon.py if it exists
if [ -f "create_icon.py" ]; then
    cp create_icon.py "$INSTALL_DIR/"
fi

# Create a virtual environment for the application
echo "Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# Activate the virtual environment and install dependencies
echo "Installing dependencies in virtual environment..."
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip
pip install PyQt5 PyQtWebEngine Pillow
deactivate

# Create executable script
EXECUTABLE="$BIN_DIR/unique-browser"

echo "Creating executable script..."
cat > "$EXECUTABLE" << EOF
#!/bin/bash
# Unique Browser Launcher

# Activate the virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# Run the browser
cd "$INSTALL_DIR"
python3 "$INSTALL_DIR/unique_browser.py" "\$@"

# Deactivate the virtual environment when done
deactivate
EOF

chmod +x "$EXECUTABLE"

# Create a symlink to make it available system-wide
echo "Creating system-wide symlink..."
if [ -d "/usr/local/bin" ] && [ -w "/usr/local/bin" ]; then
    sudo ln -sf "$EXECUTABLE" "/usr/local/bin/unique-browser" 2>/dev/null || echo "Warning: Could not create system-wide symlink. The browser will still be available in your user bin directory."
fi

# Handle icons
echo "Setting up application icons..."

# Main icon path for the .desktop file
MAIN_ICON_PATH="$ICONS_DIR/128x128/apps/unique-browser.png"

# Process icons if the icons directory exists
if [ -d "icons" ]; then
    echo "Copying icons to system locations..."

    # Copy icons to the appropriate directories
    if [ -f "icons/unique_browser_16.png" ]; then
        cp "icons/unique_browser_16.png" "$ICONS_DIR/16x16/apps/unique-browser.png"
    fi

    if [ -f "icons/unique_browser_32.png" ]; then
        cp "icons/unique_browser_32.png" "$ICONS_DIR/32x32/apps/unique-browser.png"
    fi

    if [ -f "icons/unique_browser_48.png" ]; then
        cp "icons/unique_browser_48.png" "$ICONS_DIR/48x48/apps/unique-browser.png"
    fi

    if [ -f "icons/unique_browser_64.png" ]; then
        cp "icons/unique_browser_64.png" "$ICONS_DIR/64x64/apps/unique-browser.png"
    fi

    if [ -f "icons/unique_browser_128.png" ]; then
        cp "icons/unique_browser_128.png" "$ICONS_DIR/128x128/apps/unique-browser.png"
    fi

    if [ -f "icons/unique_browser_256.png" ]; then
        cp "icons/unique_browser_256.png" "$ICONS_DIR/256x256/apps/unique-browser.png"
    fi

    # Also copy icons to the application directory
    mkdir -p "$INSTALL_DIR/icons"
    cp -r icons/* "$INSTALL_DIR/icons/"

    # If we have create_icon.py, run it to generate icons in the installation directory
    if [ -f "$INSTALL_DIR/create_icon.py" ]; then
        echo "Generating icons in installation directory..."
        cd "$INSTALL_DIR"
        python3 create_icon.py
        cd - > /dev/null
    fi
else
    # Create a default icon if icons directory doesn't exist
    echo "Icons directory not found, creating default icons..."

    # Base64 encoded simple browser icon
    ICON_DATA="iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABhGlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9TpSIVBzuIOGSoThZERRy1CkWoEGqFVh1MbvqhNGlIUlwcBdeCgx+LVQcXZ10dXAVB8APE0clJ0UVK/F9SaBHjwXE/3t173L0DhGaVqWbPOKBqlpFOxMVcflUMvCKIEYQxICJTLzETi2l4jq97+Ph6F+dZ3uf+HP1KwWSATySeY7phEW8QT29aOud94jArSQrxOfGYQRckfuS67PIb56LDAs8MG5n0PHGYWCx2sdLFrGRqxFPEEVXTKV/INVnlvMVZq9ZY+578heGCvrLMdZpDSGAJSaQgQkYdFVRhIUarRoqJNO3HPfzDjj9FLplcFTByLKAGFZLjB/+D392axalJNykUB4JfjvVjDAjsAs2643wfO07zBPA/A1d621+uATOfpDe7WvQIGNgGLq67mrwHXO4AkSddMiRH8tMUCgXg/Yy+KQcM3wL9a25v7X2cPgAZ6mr5Bjg4BMaKlL3u8e5gZ2//nmn19wOZ/HK9yJOGWwAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAAuIwAALiMBeKU/dgAAAAd0SU1FB+QEBhQOGxtlhAAAAAZJREFUeNrt2r1KA0EUhuFnNxFERLCwsLCwEGwECwsLwUoQrAQLwUawEGwECwsLCwsLwUawECwsLCwsLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBAsBAvBQrAQLAQLwUKwECwEC8FCsBA+Wy6KYqSqqsOu6/ZCCLNt2y7XdX3Vtu1tSulxMBi8/OkFRVGMV1V11nXdQQhhIcY4NRwOJ+q6vkgp3aSUHmKMz/8W4A14B7KCxAuqm+C1AAAAAElFTkSuQmCC"

    # Create icons in different sizes
    for SIZE in 16 32 48 64 128 256; do
        ICON_FILE="$ICONS_DIR/${SIZE}x${SIZE}/apps/unique-browser.png"
        echo $ICON_DATA | base64 -d > "$ICON_FILE"
    done

    # Also create an icon in the application directory
    mkdir -p "$INSTALL_DIR/icons"
    echo $ICON_DATA | base64 -d > "$INSTALL_DIR/icons/unique_browser.png"

    # If we have create_icon.py, run it to generate better icons
    if [ -f "$INSTALL_DIR/create_icon.py" ]; then
        echo "Generating better icons..."
        cd "$INSTALL_DIR"
        python3 create_icon.py
        cd - > /dev/null

        # Update system icons with the better ones
        if [ -d "$INSTALL_DIR/icons" ]; then
            for SIZE in 16 32 48 64 128 256; do
                if [ -f "$INSTALL_DIR/icons/unique_browser_${SIZE}.png" ]; then
                    cp "$INSTALL_DIR/icons/unique_browser_${SIZE}.png" "$ICONS_DIR/${SIZE}x${SIZE}/apps/unique-browser.png"
                fi
            done
        fi
    fi
fi

# Update icon cache if gtk-update-icon-cache is available
if command -v gtk-update-icon-cache &> /dev/null; then
    echo "Updating icon cache..."
    gtk-update-icon-cache -f -t "$ICONS_DIR" || echo "Warning: Could not update icon cache."
fi

# Create desktop entry file
echo "Creating desktop entry..."
DESKTOP_FILE="$APPLICATIONS_DIR/unique-browser.desktop"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Unique Browser
GenericName=Web Browser
Comment=A lightweight and feature-rich web browser
Exec=unique-browser %U
Icon=unique-browser
Terminal=false
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/rss+xml;application/rdf+xml;x-scheme-handler/http;x-scheme-handler/https;
StartupNotify=true
Actions=NewWindow;PrivateBrowsing;

[Desktop Action NewWindow]
Name=New Window
Exec=unique-browser --new-window

[Desktop Action PrivateBrowsing]
Name=New Private Window
Exec=unique-browser --private-window
EOF

# Update desktop database if update-desktop-database is available
if command -v update-desktop-database &> /dev/null; then
    echo "Updating desktop database..."
    update-desktop-database "$APPLICATIONS_DIR" || echo "Warning: Could not update desktop database."
fi

# Set as default browser if xdg-settings is available
if command -v xdg-settings &> /dev/null; then
    echo "Would you like to set Unique Browser as your default browser? (y/n)"
    read -r SET_DEFAULT
    if [ "$SET_DEFAULT" = "y" ] || [ "$SET_DEFAULT" = "Y" ]; then
        echo "Setting Unique Browser as default browser..."
        xdg-settings set default-web-browser unique-browser.desktop || echo "Warning: Could not set as default browser."
    fi
fi

# Create uninstaller script
echo "Creating uninstaller script..."
UNINSTALLER="$INSTALL_DIR/uninstall.sh"

cat > "$UNINSTALLER" << EOF
#!/bin/bash

echo "=== Unique Browser Uninstaller ==="
echo "This will remove Unique Browser from your system."
echo "Are you sure you want to continue? (y/n)"
read -r CONFIRM

if [ "\$CONFIRM" != "y" ] && [ "\$CONFIRM" != "Y" ]; then
    echo "Uninstallation cancelled."
    exit 0
fi

echo "Removing Unique Browser..."

# Remove desktop entry
rm -f "$APPLICATIONS_DIR/unique-browser.desktop"

# Remove icons
for SIZE in 16 32 48 64 128 256; do
    rm -f "$ICONS_DIR/\${SIZE}x\${SIZE}/apps/unique-browser.png"
done

# Remove executables
rm -f "$BIN_DIR/unique-browser"
sudo rm -f "/usr/local/bin/unique-browser" 2>/dev/null

# Remove application directory
rm -rf "$INSTALL_DIR"

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$ICONS_DIR" || echo "Warning: Could not update icon cache."
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPLICATIONS_DIR" || echo "Warning: Could not update desktop database."
fi

echo "Unique Browser has been successfully uninstalled."
EOF

chmod +x "$UNINSTALLER"

# Final message
echo "=============================================="
echo "Installation completed successfully!"
echo "=============================================="
echo ""
echo "Unique Browser has been installed on your system."
echo ""
echo "You can launch it in the following ways:"
echo "1. From your application menu (look for 'Unique Browser')"
echo "2. By running 'unique-browser' in terminal"
echo "3. By clicking on web links (if set as default browser)"
echo ""
echo "The browser is installed at: $INSTALL_DIR"
echo "To uninstall, run: $UNINSTALLER"
echo ""
echo "Thank you for installing Unique Browser!"
echo "=============================================="

# Launch the browser if requested
echo "Would you like to launch Unique Browser now? (y/n)"
read -r LAUNCH_NOW
if [ "$LAUNCH_NOW" = "y" ] || [ "$LAUNCH_NOW" = "Y" ]; then
    echo "Launching Unique Browser..."
    unique-browser &
fi
