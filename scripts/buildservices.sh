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
PartOf=trainpixels.service
Before=trainpixels-main.service

[Service]
Type=simple
User=root
Group=input
ExecStart=/bin/bash $controller_start_script
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
After=multi-user.target trainpixels-controller.service trainpixels-controlcenter.service
Wants=multi-user.target
PartOf=trainpixels.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
ExecStart=/bin/bash $start_script
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

# Function to create TrainPixels Control Center service
create_controlcenter_service() {
    local service_name="trainpixels-controlcenter"
    local service_file="$SERVICE_DIR/${service_name}.service"
    local controlcenter_script="$PROJECT_ROOT/start-controlcenter.sh"
    
    echo -e "${YELLOW}Creating $service_name service...${NC}"
    
    # Check if control center script exists
    if [[ ! -f "$controlcenter_script" ]]; then
        echo -e "${RED}ERROR: Control center script not found at $controlcenter_script${NC}"
        return 1
    fi
    
    # Make control center script executable
    chmod +x "$controlcenter_script"
    
    # Create the service file
    cat > "$service_file" << EOF
[Unit]
Description=TrainPixels Control Center
Documentation=https://github.com/AndreasBrostrom/trainpixels
After=multi-user.target
Wants=multi-user.target
PartOf=trainpixels.service
Before=trainpixels-main.service

[Service]
Type=simple
User=root
Group=root
ExecStart=/bin/bash $controlcenter_script
WorkingDirectory=$PROJECT_ROOT
Restart=always
RestartSec=10
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

# Function to create TrainPixels Master service (manages all services)
create_master_service() {
    local service_name="trainpixels"
    local service_file="$SERVICE_DIR/${service_name}.service"
    
    echo -e "${YELLOW}Creating $service_name master service...${NC}"
    
    # Create the service file
    cat > "$service_file" << EOF
[Unit]
Description=TrainPixels Master Service
Documentation=https://github.com/AndreasBrostrom/trainpixels
After=multi-user.target
Wants=multi-user.target

# Require and order the child services
Requires=trainpixels-controller.service trainpixels-controlcenter.service trainpixels-main.service
After=trainpixels-controller.service trainpixels-controlcenter.service
Before=trainpixels-main.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=root
Group=root
WorkingDirectory=$PROJECT_ROOT

# Start services in proper order: controller and controlcenter first, then main
ExecStart=/bin/bash -c 'systemctl start trainpixels-controller trainpixels-controlcenter && systemctl start trainpixels-main'

# Stop all TrainPixels services in reverse order
ExecStop=/bin/bash -c 'systemctl stop trainpixels-main && systemctl stop trainpixels-controlcenter trainpixels-controller'

# Reload all TrainPixels services
ExecReload=/bin/bash -c 'systemctl reload-or-restart trainpixels-controller trainpixels-controlcenter && systemctl reload-or-restart trainpixels-main'

StandardOutput=journal
StandardError=journal

# Environment variables
Environment=PYTHONUNBUFFERED=1

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
    
    if create_controlcenter_service; then
        echo -e "${GREEN}✓ Control center service created${NC}"
    else
        echo -e "${RED}✗ Failed to create control center service${NC}"
        exit 1
    fi
    
    if create_master_service; then
        echo -e "${GREEN}✓ Master service created${NC}"
    else
        echo -e "${RED}✗ Failed to create master service${NC}"
        exit 1
    fi
    
    echo
    echo -e "${GREEN}=== Service Files Created ===${NC}"
    echo
    echo "Service files location: $SERVICE_DIR"
    echo "  • trainpixels.service               - Master service (controls all other services)"
    echo "  • trainpixels-controller.service    - Numpad input controller (main_controller.py)"
    echo "  • trainpixels-main.service          - Main TrainPixels application (main.py)"
    echo "  • trainpixels-controlcenter.service - Control center (main_controlcenter.py)"
    echo
    echo -e "${BLUE}Available Python Scripts:${NC}"
    echo "  • src/main_controller.py    - Captures numpad input and writes to cache"
    echo "  • src/main.py               - Main TrainPixels application logic"
    echo "  • src/main_controlcenter.py - Reads cache and manages services via systemctl"
    echo
    
    if [[ "$SERVICE_DIR" == "/etc/systemd/system" ]]; then
        echo "Services are ready to use:"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable --now trainpixels"
        echo
        echo -e "${BLUE}TrainPixels Service Commands:${NC}"
        echo -e "  ${YELLOW}Start all services in proper order:${NC}"
        echo "  sudo systemctl start trainpixels"
        echo
        echo -e "  ${YELLOW}Stop all services:${NC}"
        echo "  sudo systemctl stop trainpixels"
        echo
        echo -e "  ${YELLOW}Restart all services:${NC}"
        echo "  sudo systemctl restart trainpixels"
        echo
        echo -e "  ${YELLOW}Enable auto-start at boot:${NC}"
        echo "  sudo systemctl enable trainpixels"
        echo
        echo -e "  ${YELLOW}Check status:${NC}"
        echo "  sudo systemctl status trainpixels"
        echo
        echo -e "  ${YELLOW}Follow logs:${NC}"
        echo "  sudo journalctl -u trainpixels -f"
        echo
        echo -e "${BLUE}Control Center Commands:${NC}"
        echo -e "  ${YELLOW}Control center will read numpad input and:${NC}"
        echo "    * = restart all services"
        echo "    1 = start trainpixels-main"
        echo "    2 = start trainpixels-controller"
        echo "    3 = stop all services"
        echo "    ** start = reboot system"
        echo

    else
        echo "To install services manually:"
        echo "  sudo cp $SERVICE_DIR/*.service /etc/systemd/system/"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable --now trainpixels"
        echo
        echo "Or use as user services:"
        echo "  mkdir -p ~/.config/systemd/user"
        echo "  cp $SERVICE_DIR/*.service ~/.config/systemd/user/"
        echo "  systemctl --user daemon-reload"
        echo "  systemctl --user enable --now trainpixels"
        echo
        echo -e "${BLUE}User Service Commands:${NC}"
        echo -e "  ${YELLOW}Start all services in proper order:${NC}"
        echo "  systemctl --user start trainpixels"
        echo
        echo -e "  ${YELLOW}Stop all services:${NC}"
        echo "  systemctl --user stop trainpixels"
        echo
        echo -e "  ${YELLOW}Restart all services:${NC}"
        echo "  systemctl --user restart trainpixels"
        echo
        echo -e "  ${YELLOW}Enable auto-start at boot:${NC}"
        echo "  systemctl --user enable trainpixels"
        echo
        echo -e "  ${YELLOW}Check status:${NC}"
        echo "  systemctl --user status trainpixels"
        echo
        echo -e "  ${YELLOW}Follow logs:${NC}"
        echo "  journalctl --user -u trainpixels -f"
    fi
}

# Parse command line arguments
case "${1:-}" in
    "controller")
        echo "Creating only controller service..."
        if create_controller_service; then
            echo -e "${GREEN}Controller service created at: $SERVICE_DIR/trainpixels-controller.service${NC}"
        else
            echo -e "${RED}Failed to create controller service${NC}"
            exit 1
        fi
        ;;
    "main")
        echo "Creating only main service..."
        if create_main_service; then
            echo -e "${GREEN}Main service created at: $SERVICE_DIR/trainpixels-main.service${NC}"
        else
            echo -e "${RED}Failed to create main service${NC}"
            exit 1
        fi
        ;;
    "controlcenter")
        echo "Creating only control center service..."
        if create_controlcenter_service; then
            echo -e "${GREEN}Control center service created at: $SERVICE_DIR/trainpixels-controlcenter.service${NC}"
        else
            echo -e "${RED}Failed to create control center service${NC}"
            exit 1
        fi
        ;;
    "master")
        echo "Creating only master service..."
        if create_master_service; then
            echo -e "${GREEN}Master service created at: $SERVICE_DIR/trainpixels.service${NC}"
        else
            echo -e "${RED}Failed to create master service${NC}"
            exit 1
        fi
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [controller|main|controlcenter|master]"
        echo "  controller    - Create only the numpad controller service (main_controller.py)"
        echo "  main          - Create only the main application service (main.py)"
        echo "  controlcenter - Create only the control center service (main_controlcenter.py)"
        echo "  master        - Create only the master service (controls all other services)"
        echo "  (no args)     - Create all services"
        exit 1
        ;;
esac