#!/bin/bash

# TrainPixels Installation Script for Debian-based Linux Systems
# This script installs TrainPixels LED controller on the system

set -e  # Exit on any error

# Color definitions for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation directories
INSTALL_PREFIX="/opt"
APP_DIR="/opt/trainpixels"
BIN_DIR="/usr/local/bin"
CONFIG_DIR="/etc/trainpixels"
SYSTEMD_DIR="/etc/systemd/system"
SHARE_DIR="/usr/local/share/trainpixels"

# Files and directories
BINARY_NAME="trainpixels"
SERVICE_NAME="trainpixels.service"

echo -e "${BLUE}TrainPixels Installation Script${NC}"
echo -e "${BLUE}===============================${NC}"
echo -e "${BLUE}Installing TrainPixels LED Controller on Debian-based system${NC}"
echo ""

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]] && [[ -z "$SUDO_USER" ]]; then
        echo -e "${RED}Error: Do not run this script directly as root.${NC}"
        echo -e "${YELLOW}Use 'sudo ./install.sh' instead.${NC}"
        exit 1
    fi
    
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}Error: This script must be run with sudo privileges.${NC}"
        echo -e "${YELLOW}Run: sudo ./install.sh${NC}"
        exit 1
    fi
}

# Get the actual user (not root when using sudo)
get_real_user() {
    if [[ -n "$SUDO_USER" ]]; then
        REAL_USER="$SUDO_USER"
        REAL_HOME=$(eval echo "~$SUDO_USER")
        USER_CONFIG_DIR="$REAL_HOME/.config/trainpixels"
    else
        REAL_USER="$USER"
        REAL_HOME="$HOME"
        USER_CONFIG_DIR="$REAL_HOME/.config/trainpixels"
    fi
    echo -e "${GREEN}Installing for user: $REAL_USER${NC}"
}

# Check if this is a Debian-based system
check_debian() {
    if [[ ! -f /etc/debian_version ]] && [[ ! -f /etc/lsb-release ]]; then
        echo -e "${YELLOW}Warning: This script is designed for Debian-based systems.${NC}"
        echo -e "${YELLOW}Your system may not be fully supported.${NC}"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 1
        fi
    else
        echo -e "${GREEN}Debian-based system detected${NC}"
    fi
}

# Check if required files exist in current directory
check_files() {
    echo -e "${BLUE}Checking installation files...${NC}"
    
    REQUIRED_FILES=(
        "$BINARY_NAME"
        "config/config.json"
    )
    
    REQUIRED_DIRS=(
        "tracks.d"
        "utils.d"
    )
    
    OPTIONAL_FILES=(
        "$SERVICE_NAME"
        "uninstall.sh"
    )
    
    # Check required files
    for file in "${REQUIRED_FILES[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo -e "${RED}Error: Missing required file: $file${NC}"
            echo -e "${YELLOW}Make sure you're running this from the extracted package directory${NC}"
            exit 1
        else
            echo -e "${GREEN}  Found: $file${NC}"
        fi
    done
    
    # Check required directories
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [[ ! -d "$dir" ]]; then
            echo -e "${RED}Error: Missing required directory: $dir${NC}"
            exit 1
        else
            FILE_COUNT=$(find "$dir" -name "*.json" | wc -l)
            echo -e "${GREEN}  Found: $dir ($FILE_COUNT files)${NC}"
        fi
    done
    
    # Check optional files
    for file in "${OPTIONAL_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            echo -e "${GREEN}  Found optional: $file${NC}"
        fi
    done
}

# Create system user for TrainPixels
create_user() {
    echo -e "${BLUE}Creating system user...${NC}"
    
    if ! id "trainpixels" &>/dev/null; then
        echo -e "${YELLOW}Creating trainpixels system user...${NC}"
        adduser --system --group --home /opt/trainpixels --shell /bin/false trainpixels
        echo -e "${GREEN}User 'trainpixels' created${NC}"
    else
        echo -e "${GREEN}User 'trainpixels' already exists${NC}"
    fi
}

# Create installation directories
create_directories() {
    echo -e "${BLUE}Creating installation directories...${NC}"
    
    # System directories
    mkdir -p "$APP_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$SHARE_DIR"
    mkdir -p "$CONFIG_DIR/tracks.d"
    mkdir -p "$CONFIG_DIR/utils.d"
    
    # User config directory (as real user, not root)
    if [[ -n "$REAL_USER" ]] && [[ "$REAL_USER" != "root" ]]; then
        sudo -u "$REAL_USER" mkdir -p "$USER_CONFIG_DIR"
        sudo -u "$REAL_USER" mkdir -p "$USER_CONFIG_DIR/tracks.d"
        sudo -u "$REAL_USER" mkdir -p "$USER_CONFIG_DIR/utils.d"
        echo -e "${GREEN}User config directory: $USER_CONFIG_DIR${NC}"
    fi
    
    echo -e "${GREEN}Directories created${NC}"
}

# Install binary
install_binary() {
    echo -e "${BLUE}Installing binary...${NC}"
    
    # Copy binary to application directory
    cp "$BINARY_NAME" "$APP_DIR/"
    chmod +x "$APP_DIR/$BINARY_NAME"
    chown trainpixels:trainpixels "$APP_DIR/$BINARY_NAME"
    
    # Create symlink in system PATH
    ln -sf "$APP_DIR/$BINARY_NAME" "$BIN_DIR/$BINARY_NAME"
    
    echo -e "${GREEN}Binary installed: $APP_DIR/$BINARY_NAME${NC}"
    echo -e "${GREEN}Symlink created: $BIN_DIR/$BINARY_NAME${NC}"
}

# Install configuration files
install_config() {
    echo -e "${BLUE}Installing configuration files...${NC}"
    
    # Install system-wide default configs
    cp "config/config.json" "$CONFIG_DIR/config.json.example"
    cp -r tracks.d/* "$CONFIG_DIR/tracks.d/"
    cp -r utils.d/* "$CONFIG_DIR/utils.d/"
    
    # Set proper permissions for system configs
    chown -R root:root "$CONFIG_DIR"
    chmod -R 644 "$CONFIG_DIR"/*.json "$CONFIG_DIR"/*/*.json 2>/dev/null || true
    chmod 755 "$CONFIG_DIR" "$CONFIG_DIR/tracks.d" "$CONFIG_DIR/utils.d"
    
    # Set ownership of app directory
    chown -R trainpixels:trainpixels "$APP_DIR"
    
    # Install example configs to user directory (if not already present)
    if [[ -n "$REAL_USER" ]] && [[ "$REAL_USER" != "root" ]]; then
        # Copy example config if user doesn't have one
        if [[ ! -f "$USER_CONFIG_DIR/config.json" ]]; then
            sudo -u "$REAL_USER" cp "config/config.json" "$USER_CONFIG_DIR/config.json"
            echo -e "${GREEN}User config template: $USER_CONFIG_DIR/config.json${NC}"
        else
            echo -e "${YELLOW}User config exists, not overwriting: $USER_CONFIG_DIR/config.json${NC}"
        fi
        
        # Copy example tracks and utils if directories are empty
        if [[ ! "$(ls -A "$USER_CONFIG_DIR/tracks.d" 2>/dev/null)" ]]; then
            sudo -u "$REAL_USER" cp tracks.d/* "$USER_CONFIG_DIR/tracks.d/"
            echo -e "${GREEN}Example tracks copied to user config${NC}"
        fi
        
        if [[ ! "$(ls -A "$USER_CONFIG_DIR/utils.d" 2>/dev/null)" ]]; then
            sudo -u "$REAL_USER" cp utils.d/* "$USER_CONFIG_DIR/utils.d/"
            echo -e "${GREEN}Example utils copied to user config${NC}"
        fi
        
        # Set proper ownership
        chown -R "$REAL_USER:$REAL_USER" "$USER_CONFIG_DIR"
    fi
    
    echo -e "${GREEN}System configs: $CONFIG_DIR${NC}"
    echo -e "${GREEN}User configs: $USER_CONFIG_DIR${NC}"
}

# Install systemd service
install_service() {
    if [[ ! -f "$SERVICE_NAME" ]]; then
        echo -e "${YELLOW}No systemd service file found, skipping service installation${NC}"
        return
    fi
    
    echo -e "${BLUE}Installing systemd service...${NC}"
    
    # Copy and configure service file
    cp "$SERVICE_NAME" "$SYSTEMD_DIR/$SERVICE_NAME"
    chmod 644 "$SYSTEMD_DIR/$SERVICE_NAME"
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    
    echo -e "${GREEN}Service installed and enabled: $SERVICE_NAME${NC}"
    echo -e "${YELLOW}Use 'sudo systemctl start trainpixels' to start the service${NC}"
}

# Set up permissions for GPIO access
setup_permissions() {
    echo -e "${BLUE}Setting up GPIO permissions...${NC}"
    
    # Add trainpixels user to gpio group if it exists
    if getent group gpio > /dev/null 2>&1; then
        usermod -a -G gpio trainpixels
        echo -e "${GREEN}Added trainpixels user to gpio group${NC}"
    fi
    
    # Add real user to gpio group if requested
    if [[ -n "$REAL_USER" ]] && [[ "$REAL_USER" != "root" ]]; then
        read -p "Add user '$REAL_USER' to gpio group for hardware access? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if getent group gpio > /dev/null 2>&1; then
                usermod -a -G gpio "$REAL_USER"
                echo -e "${GREEN}Added $REAL_USER to gpio group${NC}"
                echo -e "${YELLOW}User may need to log out and back in for group changes to take effect${NC}"
            else
                echo -e "${YELLOW}gpio group not found on this system${NC}"
            fi
        fi
    fi
}

# Post-install verification
verify_installation() {
    echo -e "${BLUE}Verifying installation...${NC}"
    
    # Check binary
    if command -v "$BINARY_NAME" >/dev/null 2>&1; then
        echo -e "${GREEN}Binary accessible in PATH${NC}"
    else
        echo -e "${RED}Binary not found in PATH${NC}"
        exit 1
    fi
    
    # Check service
    if [[ -f "$SYSTEMD_DIR/$SERVICE_NAME" ]]; then
        if systemctl is-enabled "$SERVICE_NAME" >/dev/null 2>&1; then
            echo -e "${GREEN}Service enabled${NC}"
        else
            echo -e "${YELLOW}Service not enabled${NC}"
        fi
    fi
    
    # Check configs
    if [[ -f "$CONFIG_DIR/config.json.example" ]]; then
        echo -e "${GREEN}System config installed${NC}"
    else
        echo -e "${RED}System config missing${NC}"
    fi
    
    # Check user
    if id "trainpixels" &>/dev/null; then
        echo -e "${GREEN}System user created${NC}"
    else
        echo -e "${RED}System user missing${NC}"
    fi
}

# Main installation function
main() {
    check_root
    get_real_user
    check_debian
    check_files
    create_user
    create_directories
    install_binary
    install_config
    install_service
    setup_permissions
    verify_installation
    
    echo ""
    echo -e "${GREEN}TrainPixels installation completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "   1. Review config: ${YELLOW}nano $USER_CONFIG_DIR/config.json${NC}"
    echo -e "   2. Start service: ${YELLOW}sudo systemctl start trainpixels${NC}"
    echo -e "   3. Check status:  ${YELLOW}sudo systemctl status trainpixels${NC}"
    echo -e "   4. View logs:     ${YELLOW}journalctl -u trainpixels -f${NC}"
    echo ""
    echo -e "${BLUE}User config:   $USER_CONFIG_DIR/${NC}"
    echo -e "${BLUE}System config: $CONFIG_DIR/${NC}"
    echo ""
    echo -e "${YELLOW}Note: If you added users to gpio group, they may need to log out and back in.${NC}"
}

# Run main installation
main "$@"