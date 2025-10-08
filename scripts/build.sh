#!/bin/bash

# TrainPixels Build Script
# Creates a standalone binary from the Python application and prepares artifacts

set -e  # Exit on any error

# Get the project root directory (one level up from scripts folder)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$PROJECT_DIR/src"
DIST_DIR="$PROJECT_DIR/dist"
BUILD_DIR="$PROJECT_DIR/build"
BINARY_NAME="trainpixels"

echo "TrainPixels Build Script"
echo "========================"

# Change to project directory
cd "$PROJECT_DIR"

# Check if we're in the right directory
if [[ ! -f "$SRC_DIR/main.py" ]]; then
    echo "Error: main.py not found in src/ directory"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
if [[ -d "$DIST_DIR" ]]; then
    rm -rf "$DIST_DIR"
fi
if [[ -d "$BUILD_DIR" ]]; then
    rm -rf "$BUILD_DIR"
fi

# Create/activate virtual environment
echo "Setting up Python environment..."
if [[ ! -d venv ]]; then
    python -m venv venv
fi
source venv/bin/activate

# Install/upgrade build dependencies
echo "Installing build dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r scripts/requirements-build.txt

# Create PyInstaller spec file for better control
echo "Creating PyInstaller spec file..."
cat > trainpixels.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/tracks.d', 'tracks.d'),
        ('src/utils.d', 'utils.d'),
        ('src/config.json', '.'),
    ],
    hiddenimports=[
        'adafruit_blinka',
        'adafruit_circuitpython_neopixel',
        'board',
        'neopixel',
        'digitalio',
        'busio',
        'microcontroller',
        'multiprocessing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='trainpixels',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Build the binary
echo "Building binary with PyInstaller..."
pyinstaller --clean trainpixels.spec

# Check if build was successful
if [[ -f "$DIST_DIR/$BINARY_NAME" ]]; then
    echo "Build successful!"
    echo "Binary location: $DIST_DIR/$BINARY_NAME"
    
    # Make binary executable
    chmod +x "$DIST_DIR/$BINARY_NAME"
    
    # Get binary info
    BINARY_SIZE=$(du -h "$DIST_DIR/$BINARY_NAME" | cut -f1)
    echo "Binary size: $BINARY_SIZE"
    
else
    echo "Build failed!"
    exit 1
fi

# Create installation package directory structure
echo "Creating installation package..."
PACKAGE_DIR="$DIST_DIR/trainpixels-package"
mkdir -p "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR/config"
mkdir -p "$PACKAGE_DIR/tracks.d"
mkdir -p "$PACKAGE_DIR/utils.d"

# Copy binary
cp "$DIST_DIR/$BINARY_NAME" "$PACKAGE_DIR/"

# Copy configuration files
cp "$SRC_DIR/config.json" "$PACKAGE_DIR/config/"
cp "$SRC_DIR"/tracks.d/* "$PACKAGE_DIR/tracks.d/"
cp "$SRC_DIR"/utils.d/* "$PACKAGE_DIR/utils.d/"

# Copy systemd service file if it exists
if [[ -f "$PROJECT_DIR/scripts/trainpixels.service" ]]; then
    cp "$PROJECT_DIR/scripts/trainpixels.service" "$PACKAGE_DIR/"
    echo "Systemd service file included: trainpixels.service"
else
    echo "Warning: Systemd service file not found at scripts/trainpixels.service"
fi

# Copy installation script if it exists
if [[ -f "$PROJECT_DIR/scripts/install.sh" ]]; then
    cp "$PROJECT_DIR/scripts/install.sh" "$PACKAGE_DIR/"
    chmod +x "$PACKAGE_DIR/install.sh"
    echo "Installation script included"
fi

# Copy uninstall script if it exists
if [[ -f "$PROJECT_DIR/scripts/uninstall.sh" ]]; then
    cp "$PROJECT_DIR/scripts/uninstall.sh" "$PACKAGE_DIR/"
    chmod +x "$PACKAGE_DIR/uninstall.sh"
    echo "Uninstall script included"
fi

# Create a simple README for the package
cat > "$PACKAGE_DIR/README.md" << EOF
# TrainPixels Binary Package

This package contains the compiled TrainPixels LED controller binary.

## Contents

- \`trainpixels\` - Main executable binary
- \`config/config.json\` - Default configuration file
- \`tracks.d/\` - Track configuration files
- \`utils.d/\` - Utility configuration files
- \`trainpixels.service\` - Systemd service file (if available)
- \`install.sh\` - Installation script (if available)
- \`uninstall.sh\` - Uninstall script (if available)

## Quick Start

### Option 1: Direct execution
\`\`\`bash
./trainpixels
\`\`\`

### Option 2: System installation (if install.sh is present)
\`\`\`bash
sudo ./install.sh
\`\`\`

## Configuration

The binary looks for configuration files in this priority order:
1. \`~/.config/trainpixels/\`
2. \`~/Desktop/\`
3. Built-in defaults (from this package)

To customize configuration:
1. Create directory: \`mkdir -p ~/.config/trainpixels\`
2. Copy config: \`cp config/config.json ~/.config/trainpixels/\`
3. Copy tracks: \`cp -r tracks.d ~/.config/trainpixels/\`
4. Copy utils: \`cp -r utils.d ~/.config/trainpixels/\`
5. Edit as needed: \`vim ~/.config/trainpixels/config.json\`

## Hardware Requirements

- Raspberry Pi or compatible SBC with GPIO support
- WS2812B LED strips connected to GPIO pin (configured in config.json)
- Python libraries for hardware access (included in binary)

Built on: $(date)
EOF

# Create compressed archive for easy distribution
echo "Creating compressed archive..."
cd "$DIST_DIR"
tar -czf "trainpixels-linux-x64.tar.gz" -C trainpixels-package .
cd "$PROJECT_DIR"

# Create build info for artifacts
echo "Creating build information..."
cat > "$DIST_DIR/build-info.txt" << EOF
TrainPixels Build Information
============================

Build Date: $(date)
Build Host: $(hostname)
Git Branch: $(git branch --show-current 2>/dev/null || echo "unknown")
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "unknown")
Git Status: $(git status --porcelain 2>/dev/null | wc -l) modified files

Binary: $DIST_DIR/$BINARY_NAME
Size: $(du -h "$DIST_DIR/$BINARY_NAME" | cut -f1)
Package: $DIST_DIR/trainpixels-linux-x64.tar.gz
Package Size: $(du -h "$DIST_DIR/trainpixels-linux-x64.tar.gz" | cut -f1)

Contents:
$(ls -la "$PACKAGE_DIR")

Configuration Files:
- Config: $(ls -1 "$PACKAGE_DIR/config/" | wc -l) files
- Tracks: $(ls -1 "$PACKAGE_DIR/tracks.d/" | wc -l) files  
- Utils: $(ls -1 "$PACKAGE_DIR/utils.d/" | wc -l) files
EOF

# Clean up spec file
rm -f trainpixels.spec

echo ""
echo "Build Complete!"
echo "==============="
echo "Binary: $DIST_DIR/$BINARY_NAME"
echo "Package: $DIST_DIR/trainpixels-linux-x64.tar.gz"
echo "Installation Package: $DIST_DIR/trainpixels-package/"
echo ""
echo "Artifacts ready for upload:"
echo "- Binary file: dist/$BINARY_NAME"
echo "- Archive: dist/trainpixels-linux-x64.tar.gz"  
echo "- Package directory: dist/trainpixels-package/"
echo "- Build info: dist/build-info.txt"
echo ""
echo "Ready for deployment!"