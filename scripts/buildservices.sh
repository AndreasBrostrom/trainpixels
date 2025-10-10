#!/bin/bash

# TrainPixels Systemd Service Builder
# This script creates systemd service files for TrainPixels components

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
CURRENT_USER="${SUDO_USER:-$USER}"
CURRENT_USER_HOME=$(eval echo "~$CURRENT_USER")

echo -e "${BLUE}=== TrainPixels Systemd Service Builder ===${NC}"
echo "Project root: $PROJECT_ROOT"
echo "Current user: $CURRENT_USER"
echo "User home: $CURRENT_USER_HOME"
echo

# Ask user where to create services
echo -e "${YELLOW}Where would you like to create the systemd service files?${NC}"
echo "1) System directory (/etc/systemd/system/) - requires root"
echo "2) Project directory (./services/) - no root needed"
echo
read -p "Choose option (1 or 2): " install_choice

case "$install_choice" in
    1)
        SERVICE_DIR="/etc/systemd/system"
        if [[ $EUID -ne 0 ]]; then
           echo -e "${RED}System directory requires root privileges${NC}"
           echo "Please run: sudo $0"
           exit 1
        fi
        echo -e "${GREEN}Creating services in system directory${NC}"
        ;;
    2)
        SERVICE_DIR="$PROJECT_ROOT/services"
        mkdir -p "$SERVICE_DIR"
        echo -e "${GREEN}Creating services in project directory: $SERVICE_DIR${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac
echo

# Function to create TrainPixels Controller service
create_controller_service() {
    local service_name="trainpixels-controller"
    local service_file="$SERVICE_DIR/${service_name}.service"
    local controller_start_script="$PROJECT_ROOT/start-controller.sh"
    
    echo -e "${YELLOW}Creating $service_name service...${NC}"
    
    # Check if controller start script exists
    if [[ ! -f "$controller_start_script" ]]; then
        echo -e "${RED}ERROR: Controller start script not found at $controller_start_script${NC}"
        return 1
    fi
    
    # Make controller start script executable
    chmod +x "$controller_start_script"
    
    # Create the service file
    cat > "$service_file" << EOF
[Unit]
Description=TrainPixels Numpad Controller
Documentation=https://github.com/AndreasBrostrom/trainpixels
After=multi-user.target
Wants=multi-user.target

[Service]
Type=simple
User=root
Group=input
ExecStart=$PROJECT_ROOT/start-controller.sh
WorkingDirectory=$PROJECT_ROOT
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Environment variables
Environment=PYTHONUNBUFFERED=1
Environment=SUDO_USER=$CURRENT_USER

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$CURRENT_USER_HOME/.cache/trainpixels
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    echo -e "${GREEN}✓ Created $service_file${NC}"
    return 0
}

# Function to create TrainPixels Main service
create_main_service() {
    local service_name="trainpixels-main"
    local service_file="$SERVICE_DIR/${service_name}.service"
    local start_script="$PROJECT_ROOT/start.sh"
    
    echo -e "${YELLOW}Creating $service_name service...${NC}"
    
    # Check if start script exists
    if [[ ! -f "$start_script" ]]; then
        echo -e "${RED}ERROR: Start script not found at $start_script${NC}"
        return 1
    fi
    
    # Make start script executable
    chmod +x "$start_script"
    
    # Create the service file
    cat > "$service_file" << EOF
[Unit]
Description=TrainPixels Main Application
Documentation=https://github.com/AndreasBrostrom/trainpixels
After=multi-user.target
Wants=multi-user.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
ExecStart=$PROJECT_ROOT/start.sh
WorkingDirectory=$PROJECT_ROOT
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment variables
Environment=PYTHONUNBUFFERED=1
Environment=HOME=$CURRENT_USER_HOME
Environment=USER=$CURRENT_USER

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=$PROJECT_ROOT
ReadWritePaths=$CURRENT_USER_HOME/.config/trailpixels
ReadWritePaths=$CURRENT_USER_HOME/.cache/trainpixels
ReadWritePaths=$CURRENT_USER_HOME/Desktop
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    echo -e "${GREEN}✓ Created $service_file${NC}"
    return 0
}

# Main execution
main() {
    echo -e "${BLUE}Creating systemd services...${NC}"
    
    if create_controller_service; then
        echo -e "${GREEN}✓ Controller service created${NC}"
    else
        echo -e "${RED}✗ Failed to create controller service${NC}"
        exit 1
    fi
    
    if create_main_service; then
        echo -e "${GREEN}✓ Main service created${NC}"
    else
        echo -e "${RED}✗ Failed to create main service${NC}"
        exit 1
    fi
    
    echo
    echo -e "${GREEN}=== Service Files Created ===${NC}"
    echo
    echo "Service files location: $SERVICE_DIR"
    echo "  • trainpixels-controller.service - Numpad input controller"
    echo "  • trainpixels-main.service       - Main TrainPixels application"
    echo
    
    if [[ "$SERVICE_DIR" == "/etc/systemd/system" ]]; then
        echo "Services are ready to use:"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable --now trainpixels-controller"
        echo "  sudo systemctl enable --now trainpixels-main"
        echo
        echo -e "${BLUE}Service Management Examples:${NC}"
        echo
        echo -e "${YELLOW}Start services:${NC}"
        echo "  sudo systemctl start trainpixels-controller"
        echo "  sudo systemctl start trainpixels-main"
        echo
        echo -e "${YELLOW}Stop services:${NC}"
        echo "  sudo systemctl stop trainpixels-controller"
        echo "  sudo systemctl stop trainpixels-main"
        echo
        echo -e "${YELLOW}Enable services (auto-start on boot):${NC}"
        echo "  sudo systemctl enable trainpixels-controller"
        echo "  sudo systemctl enable trainpixels-main"
        echo
        echo -e "${YELLOW}Disable services (prevent auto-start):${NC}"
        echo "  sudo systemctl disable trainpixels-controller"
        echo "  sudo systemctl disable trainpixels-main"
        echo
        echo -e "${YELLOW}Check status:${NC}"
        echo "  sudo systemctl status trainpixels-controller"
        echo "  sudo systemctl status trainpixels-main"
        echo
        echo -e "${YELLOW}View logs:${NC}"
        echo "  # Follow live logs"
        echo "  sudo journalctl -u trainpixels-controller -f"
        echo "  sudo journalctl -u trainpixels-main -f"
        echo
    else
        echo "To install services manually:"
        echo "  sudo cp $SERVICE_DIR/*.service /etc/systemd/system/"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable --now trainpixels-controller"
        echo "  sudo systemctl enable --now trainpixels-main"
        echo
        echo "Or use as user services:"
        echo "  mkdir -p ~/.config/systemd/user"
        echo "  cp $SERVICE_DIR/*.service ~/.config/systemd/user/"
        echo "  systemctl --user daemon-reload"
        echo "  systemctl --user enable --now trainpixels-controller"
        echo "  systemctl --user enable --now trainpixels-main"
        echo
        echo -e "${BLUE}User Service Management Examples:${NC}"
        echo
        echo -e "${YELLOW}Start/Stop user services:${NC}"
        echo "  systemctl --user start trainpixels-controller"
        echo "  systemctl --user stop trainpixels-controller"
        echo "  systemctl --user start trainpixels-main"
        echo "  systemctl --user stop trainpixels-main"
        echo
        echo -e "${YELLOW}Enable/Disable user services:${NC}"
        echo "  systemctl --user enable trainpixels-controller"
        echo "  systemctl --user disable trainpixels-controller"
        echo "  systemctl --user enable trainpixels-main"
        echo "  systemctl --user disable trainpixels-main"
        echo
        echo -e "${YELLOW}User service logs:${NC}"
        echo "  journalctl --user -u trainpixels-controller -f"
        echo "  journalctl --user -u trainpixels-main -f"
        echo "  journalctl --user -u trainpixels-controller -n 50"
        echo "  journalctl --user -u trainpixels-main -n 50"
    fi
}

# Parse command line arguments
case "${1:-}" in
    "controller")
        echo "Creating only controller service..."
        create_controller_service
        echo -e "${GREEN}Controller service created at: $SERVICE_DIR/trainpixels-controller.service${NC}"
        ;;
    "main")
        echo "Creating only main service..."
        create_main_service
        echo -e "${GREEN}Main service created at: $SERVICE_DIR/trainpixels-main.service${NC}"
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [controller|main]"
        echo "  controller - Create only the numpad controller service"
        echo "  main       - Create only the main application service"
        echo "  (no args)  - Create both services"
        exit 1
        ;;
esac