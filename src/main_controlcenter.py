#!/usr/bin/env python3
"""
TrainPixels Control Center
Monitors numpad input and manages all TrainPixels services based on commands
"""

import os
import sys
import time
import logging
import subprocess
import signal
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_ROOT)

# Get user cache directory (handle sudo case)
def get_user_cache_dir():
    """Get the cache directory for the original user, even when running as sudo"""
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and os.geteuid() == 0:
        user_home = os.path.expanduser(f"~{sudo_user}")
        return os.path.join(user_home, ".cache", "trainpixels")
    else:
        return os.path.expanduser("~/.cache/trainpixels")

CACHE_DIR = get_user_cache_dir()
CACHE_FILE = os.path.join(CACHE_DIR, "numpad_input")
LOCK_FILE = os.path.join(CACHE_DIR, "numpad_input.lock")
LOG_FILE = os.path.join(CACHE_DIR, "controlcenter.log")

# Ensure cache directory exists with proper ownership
def setup_cache_directory():
    """Create cache directory with proper ownership when running as sudo"""
    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
    
    # If running as sudo, change ownership to the original user
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and os.geteuid() == 0:
        try:
            import pwd
            user_info = pwd.getpwnam(sudo_user)
            os.chown(CACHE_DIR, user_info.pw_uid, user_info.pw_gid)
        except Exception as e:
            print(f"Warning: Could not set cache directory ownership: {e}")

def fix_file_ownership(filepath):
    """Fix file ownership when running as sudo"""
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and os.geteuid() == 0:
        try:
            import pwd
            user_info = pwd.getpwnam(sudo_user)
            os.chown(filepath, user_info.pw_uid, user_info.pw_gid)
        except Exception as e:
            print(f"Warning: Could not set file ownership for {filepath}: {e}")

setup_cache_directory()

# Setup logging
def setup_logging():
    """Setup logging with proper file ownership"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Fix log file ownership if running as sudo
    if os.path.exists(LOG_FILE):
        fix_file_ownership(LOG_FILE)
    
    return logging.getLogger(__name__)

logger = setup_logging()

# Service names
SERVICES = {
    'controller': 'trainpixels-controller',
    'main': 'trainpixels-main',
    'controlcenter': 'trainpixels-controlcenter'
}

class TrainPixels:
    def __init__(self):
        self.running = True
        self.last_processed_content = None
        self.cache_file = CACHE_FILE
        self.lock_file = LOCK_FILE
        
    def run_systemctl_command(self, action, service):
        """Run a systemctl command"""
        try:
            cmd = ['systemctl', action, service]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Successfully executed: {' '.join(cmd)}")
                return True
            else:
                logger.error(f"Command failed: {' '.join(cmd)}")
                logger.error(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            return False
        except Exception as e:
            logger.error(f"Error executing command {' '.join(cmd)}: {e}")
            return False
    
    def start_service(self, service_key):
        """Start a specific service"""
        if service_key in SERVICES:
            service_name = SERVICES[service_key]
            logger.info(f"Starting service: {service_name}")
            return self.run_systemctl_command('start', service_name)
        else:
            logger.error(f"Unknown service key: {service_key}")
            return False
    
    def stop_service(self, service_key):
        """Stop a specific service"""
        if service_key in SERVICES:
            service_name = SERVICES[service_key]
            logger.info(f"Stopping service: {service_name}")
            return self.run_systemctl_command('stop', service_name)
        else:
            logger.error(f"Unknown service key: {service_key}")
            return False
    
    def restart_service(self, service_key):
        """Restart a specific service"""
        if service_key in SERVICES:
            service_name = SERVICES[service_key]
            logger.info(f"Restarting service: {service_name}")
            return self.run_systemctl_command('restart', service_name)
        else:
            logger.error(f"Unknown service key: {service_key}")
            return False
    
    def restart_all_services(self):
        """Restart all TrainPixels services including itself"""
        logger.info("Restarting all TrainPixels services...")
        
        # Restart other services first
        for service_key in ['controller', 'main']:
            self.restart_service(service_key)
            time.sleep(2)  # Small delay between restarts
        
        # Restart self last (this will terminate current process)
        logger.info("Restarting control center (this will cause service restart)...")
        self.run_systemctl_command('restart', SERVICES['controlcenter'])
    
    def stop_all_services(self):
        """Stop all TrainPixels services"""
        logger.info("Stopping all TrainPixels services...")
        
        for service_key in ['main', 'controller']:
            self.stop_service(service_key)
            time.sleep(1)
        
        # Stop self last
        logger.info("Stopping control center...")
        self.running = False
    
    def start_all_services(self):
        """Start all TrainPixels services"""
        logger.info("Starting all TrainPixels services...")
        
        for service_key in ['controller', 'main']:
            self.start_service(service_key)
            time.sleep(2)
    
    def get_service_status(self, service_key):
        """Get status of a service"""
        if service_key in SERVICES:
            service_name = SERVICES[service_key]
            try:
                result = subprocess.run(['systemctl', 'is-active', service_name], 
                                      capture_output=True, text=True, timeout=10)
                return result.stdout.strip()
            except:
                return "unknown"
        return "unknown"
    
    def remove_lock_file(self):
        """Remove the lock file if it exists"""
        try:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
                logger.info("Lock file removed")
                return True
            else:
                logger.debug("No lock file to remove")
                return False
        except Exception as e:
            logger.error(f"Error removing lock file: {e}")
            return False
    
    def reboot_system(self):
        """Reboot the entire system"""
        logger.info("SYSTEM REBOOT INITIATED - Device will restart in 10 seconds")
        try:
            # Execute system reboot
            logger.critical("REBOOTING SYSTEM NOW!")
            result = subprocess.run(['systemctl', 'reboot'], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.error(f"Reboot command failed: {result.stderr}")
                # Fallback reboot method
                logger.info("Trying alternative reboot method...")
                subprocess.run(['reboot'], timeout=10)
            
        except Exception as e:
            logger.error(f"Error initiating system reboot: {e}")
            # Emergency fallback
            try:
                os.system('reboot')
            except:
                logger.critical("All reboot methods failed!")
    
    def process_command(self, command):
        """Process a command from numpad input"""
        command = command.strip()
        
        if not command:
            return
        
        logger.info(f"Processing command: '{command}'")
        
        if command == "**":
            logger.info("Command: SYSTEM REBOOT")
            self.remove_lock_file()
            self.reboot_system()
            
        elif command == "*":
            logger.info("Command: Restart all services")
            self.remove_lock_file()
            self.restart_all_services()
            
        else:
            logger.warning(f"Unknown command: '{command}'")
    
    def read_and_process_input(self):
        """Read input from cache file and process commands"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    content = f.read().strip()
                
                if content:
                    logger.info(f"Found command: '{content}'")
                    os.remove(self.cache_file)
                    
                    # Remove lock file if it exists
                    if os.path.exists(self.lock_file):
                        os.remove(self.lock_file)
                    
                    self.process_command(content)
                    
        except Exception as e:
            logger.error(f"Error processing input: {e}")
    
    def run(self):
        """Main control center loop"""
        logger.info("Starting TrainPixels Control Center")
        logger.info(f"Monitoring cache file: {self.cache_file}")
        logger.info("Commands:")
        logger.info("  ** = Reboot system")
        logger.info("  * = Restart all services")
        
        # Add initial status check
        logger.info(f"Control center running status: {self.running}")
        logger.info("Starting main monitoring loop...")
        
        loop_count = 0
        try:
            while self.running:
                loop_count += 1
                if loop_count % 60 == 1:  # Log every minute
                    logger.debug(f"Monitoring loop iteration {loop_count}")
                
                self.read_and_process_input()
                time.sleep(1)  # Check every second
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            logger.error(f"Loop count reached: {loop_count}")
        finally:
            logger.info(f"Control center stopping after {loop_count} iterations...")

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down...")
    global control_center
    if control_center:
        control_center.running = False
    sys.exit(0)

def main():
    global control_center
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Show user information
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and os.geteuid() == 0:
        logger.info(f"Running as sudo for user: {sudo_user}")
    else:
        logger.info(f"Running as user: {os.environ.get('USER', 'unknown')}")
    
    logger.info(f"Cache directory: {CACHE_DIR}")
    
    control_center = TrainPixels()
    control_center.run()

if __name__ == "__main__":
    main()