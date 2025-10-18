#!/bin/bash

# handleConfigs.sh - Setup TrainPixels configuration in ~/.config/trainpixels/
# This script allows you to either copy or symlink configuration files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$PROJECT_ROOT/src"
TARGET_DIR="$HOME/.config/trainpixels"

echo -e "${BLUE}TrainPixels Configuration Setup${NC}"
echo "==============================="
echo

# Check if source files exist
if [[ ! -d "$SRC_DIR" ]]; then
    echo -e "${RED}Error: Source directory '$SRC_DIR' not found${NC}"
    exit 1
fi

if [[ ! -f "$SRC_DIR/config.json" ]]; then
    echo -e "${RED}Error: config.json not found in '$SRC_DIR'${NC}"
    exit 1
fi

echo "Source directory: $SRC_DIR"
echo "Target directory: $TARGET_DIR"
echo

# Prompt for copy or link
echo "Choose how to setup configuration files:"
echo "  1) Copy - Create independent copies of config files"
echo "  2) Link - Create symbolic links to source files (changes affect both)"
echo

while true; do
    read -p "Enter your choice [1-2]: " choice
    case $choice in
        1)
            MODE="copy"
            echo -e "${GREEN}Selected: Copy mode${NC}"
            break
            ;;
        2)
            MODE="link"
            echo -e "${GREEN}Selected: Link mode${NC}"
            break
            ;;
        *)
            echo "Please enter 1 or 2"
            ;;
    esac
done

echo

# Create target directory
echo "Creating directory structure..."
mkdir -p "$TARGET_DIR"

# Function to copy or link a file/directory
handle_item() {
    local src_item="$1"
    local target_item="$2"
    local item_name="$3"
    
    # Remove existing target if it exists
    if [[ -e "$target_item" ]]; then
        echo -e "  ${YELLOW}Removing existing${NC} $item_name..."
        rm -rf "$target_item"
    fi
    
    if [[ "$MODE" == "copy" ]]; then
        echo -e "  ${BLUE}Copying${NC} $item_name..."
        if [[ -d "$src_item" ]]; then
            cp -r "$src_item" "$target_item"
        else
            cp "$src_item" "$target_item"
        fi
    else
        if [[ -d "$src_item" ]]; then
            echo -e "  ${BLUE}Setting up${NC} $item_name directory with individual file links..."
            # Create the target directory
            mkdir -p "$target_item"
            # Link each file individually
            for file in "$src_item"/*; do
                if [[ -f "$file" ]]; then
                    local filename=$(basename "$file")
                    echo -e "    ${BLUE}Linking${NC} $filename"
                    ln -sf "$file" "$target_item/$filename"
                fi
            done
        else
            echo -e "  ${BLUE}Linking${NC} $item_name..."
            ln -sf "$src_item" "$target_item"
        fi
    fi
}

# Handle config.json
if [[ -f "$SRC_DIR/config.json" ]]; then
    handle_item "$SRC_DIR/config.json" "$TARGET_DIR/config.json" "config.json"
fi

# Handle tracks.d directory
if [[ -d "$SRC_DIR/tracks.d" ]]; then
    handle_item "$SRC_DIR/tracks.d" "$TARGET_DIR/tracks.d" "tracks.d/"
fi

# Handle utils.d directory  
if [[ -d "$SRC_DIR/utils.d" ]]; then
    handle_item "$SRC_DIR/utils.d" "$TARGET_DIR/utils.d" "utils.d/"
fi

echo
echo -e "${GREEN}Configuration setup complete!${NC}"
echo
echo "Files are now available at: $TARGET_DIR"
echo

# Show what was created
echo "Created files/links:"
ls -la "$TARGET_DIR"

echo
if [[ "$MODE" == "copy" ]]; then
    echo -e "${YELLOW}Note:${NC} Files were copied. Changes to ~/.config/trainpixels/ will not affect the source files."
else
    echo -e "${YELLOW}Note:${NC} Files are symbolically linked. Changes to ~/.config/trainpixels/ will affect the source files and vice versa."
fi

echo
echo -e "${GREEN}You can now run TrainPixels and it will use these configuration files.${NC}"