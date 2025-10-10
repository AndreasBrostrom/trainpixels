#!/usr/bin/env python3
"""
Numpad Key Logger for TrainPixels Controller
Captures numpad key events and writes to cache file with locking mechanism.
Designed to run as a systemd service.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
import signal
import threading

try:
    import evdev
    from evdev import InputDevice, categorize, ecodes
    print("INFO: evdev library loaded successfully")
except ImportError as e:
    print(f"ERROR: Failed to import evdev: {e}")
    print("Try one of these solutions:")
    print("1. In virtual environment: pip install evdev")
    print("2. System-wide: sudo apt-get install python3-evdev")
    print("3. Check if you're in the correct virtual environment")
    sys.exit(1)

# Configuration - Handle sudo case to use original user's home directory
def get_user_cache_dir():
    """Get the cache directory for the original user, even when running as sudo"""
    # Check if running under sudo
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and os.geteuid() == 0:
        # Running as sudo, use the original user's home directory
        user_home = os.path.expanduser(f"~{sudo_user}")
        return os.path.join(user_home, ".cache", "trainpixels")
    else:
        # Normal execution, use current user's home
        return os.path.expanduser("~/.cache/trainpixels")

CACHE_DIR = get_user_cache_dir()
CACHE_FILE = os.path.join(CACHE_DIR, "numpad_input.txt")
LOCK_FILE = os.path.join(CACHE_DIR, "numpad_input.lock")
LOG_FILE = os.path.join(CACHE_DIR, "controller.log")

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
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and os.geteuid() == 0:
        try:
            import pwd
            user_info = pwd.getpwnam(sudo_user)
            os.chown(LOG_FILE, user_info.pw_uid, user_info.pw_gid)
        except Exception as e:
            pass  # Don't worry if we can't fix ownership
    
    return logging.getLogger(__name__)

logger = setup_logging()

# Numpad key mapping
NUMPAD_KEYS = {
    ecodes.KEY_KP0: '0',
    ecodes.KEY_KP1: '1',
    ecodes.KEY_KP2: '2',
    ecodes.KEY_KP3: '3',
    ecodes.KEY_KP4: '4',
    ecodes.KEY_KP5: '5',
    ecodes.KEY_KP6: '6',
    ecodes.KEY_KP7: '7',
    ecodes.KEY_KP8: '8',
    ecodes.KEY_KP9: '9',
    ecodes.KEY_KPSLASH: '/',
    ecodes.KEY_KPASTERISK: '*',
    ecodes.KEY_KPMINUS: '-',
    ecodes.KEY_KPPLUS: '+',
    ecodes.KEY_KPCOMMA: ',',
    ecodes.KEY_KPDOT: '.',
    ecodes.KEY_KPENTER: 'ENTER'
}

class NumpadController:
    def __init__(self):
        self.running = True
        self.current_input = ""
        self.input_buffer = []
        self.devices = []
        self.lock = threading.Lock()
    
    def _fix_file_ownership(self, filepath):
        """Fix file ownership when running as sudo"""
        sudo_user = os.environ.get('SUDO_USER')
        if sudo_user and os.geteuid() == 0:
            try:
                import pwd
                user_info = pwd.getpwnam(sudo_user)
                os.chown(filepath, user_info.pw_uid, user_info.pw_gid)
            except Exception as e:
                logger.debug(f"Could not set file ownership for {filepath}: {e}")
        
    def find_keyboard_devices(self):
        """Find all keyboard input devices that support numpad keys"""
        devices = []
        try:
            available_devices = evdev.list_devices()
            logger.info(f"Scanning {len(available_devices)} input devices...")
            
            for device_path in available_devices:
                try:
                    device = InputDevice(device_path)
                    logger.debug(f"Checking device: {device.name} ({device_path})")
                    
                    # Check if device has numpad keys
                    capabilities = device.capabilities()
                    if ecodes.EV_KEY in capabilities:
                        key_codes = capabilities[ecodes.EV_KEY]
                        # Check if any numpad keys are supported
                        numpad_keys_found = [key for key in NUMPAD_KEYS.keys() if key in key_codes]
                        if numpad_keys_found:
                            devices.append(device)
                            logger.info(f"✓ Found numpad device: {device.name} ({device_path}) - supports {len(numpad_keys_found)} numpad keys")
                        else:
                            logger.debug(f"✗ Device has keys but no numpad: {device.name}")
                    else:
                        logger.debug(f"✗ Device has no key events: {device.name}")
                        
                except PermissionError:
                    logger.warning(f"✗ Permission denied for device: {device_path}")
                except Exception as e:
                    logger.debug(f"✗ Error checking device {device_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error finding keyboard devices: {e}")
        
        logger.info(f"Found {len(devices)} devices with numpad support")
        return devices
    
    def create_lock_file(self):
        """Create lock file to prevent concurrent access"""
        try:
            # Check if lock file already exists
            if os.path.exists(LOCK_FILE):
                logger.warning("Lock file already exists - another process may be using the cache")
                return False
            
            with open(LOCK_FILE, 'w') as f:
                f.write(str(os.getpid()))
            
            # Set proper ownership if running as sudo
            self._fix_file_ownership(LOCK_FILE)
            logger.debug("Lock file created")
            return True
        except Exception as e:
            logger.error(f"Error creating lock file: {e}")
            return False
    
    def remove_lock_file(self):
        """Remove lock file"""
        try:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
                logger.debug("Lock file removed")
        except Exception as e:
            logger.error(f"Error removing lock file: {e}")
    
    def write_to_cache(self, input_text):
        """Write completed input to cache file with locking"""
        if not input_text.strip():
            logger.debug("Empty input, not writing to cache")
            return True
        
        # Check if lock file already exists before trying to create one
        if os.path.exists(LOCK_FILE):
            logger.warning(f"Cannot write input '{input_text}' - lock file exists. Another process is using the cache.")
            return False
            
        if not self.create_lock_file():
            logger.warning("Could not create lock file, skipping cache write")
            return False
        
        try:
            # Write just the input text to cache file
            with open(CACHE_FILE, 'w') as f:
                f.write(input_text)
            
            # Set proper ownership if running as sudo
            self._fix_file_ownership(CACHE_FILE)
            logger.info(f"Cache updated with input: '{input_text}' (lock file created)")
            return True
            
        except Exception as e:
            logger.error(f"Error writing to cache file: {e}")
            # Clean up lock file if write failed
            self.remove_lock_file()
            return False
        finally:
            # Note: Lock file is intentionally NOT removed here
            # It should be removed by another program that processes the cache
            pass
    
    def handle_numpad_key(self, key_char):
        """Handle numpad key press"""
        with self.lock:
            if key_char == 'ENTER':
                if self.current_input:
                    logger.info(f"Input confirmed: '{self.current_input}'")
                    # Write to cache file only when ENTER is pressed
                    self.write_to_cache(self.current_input)
                    self.current_input = ""
                else:
                    logger.info("Enter pressed with empty input")
            elif key_char in '0123456789':
                self.current_input += key_char
                logger.info(f"Digit entered: '{key_char}', current input: '{self.current_input}'")
            else:
                # Special characters (/, *, -, +, ,, .)
                self.current_input += key_char
                logger.info(f"Special char entered: '{key_char}', current input: '{self.current_input}'")
    
    def monitor_device(self, device):
        """Monitor a single input device for numpad key events"""
        logger.info(f"Starting to monitor device: {device.name}")
        
        try:
            for event in device.read_loop():
                if not self.running:
                    break
                
                # Only process key press events (not release)
                if event.type == ecodes.EV_KEY and event.value == 1:  # Key press
                    if event.code in NUMPAD_KEYS:
                        key_char = NUMPAD_KEYS[event.code]
                        logger.debug(f"Numpad key pressed: {key_char} (code: {event.code})")
                        self.handle_numpad_key(key_char)
                        
        except OSError as e:
            if self.running:  # Only log if we're still supposed to be running
                logger.warning(f"Device {device.name} disconnected: {e}")
        except Exception as e:
            logger.error(f"Error monitoring device {device.name}: {e}")
    
    def start_monitoring(self):
        """Start monitoring all keyboard devices"""
        self.devices = self.find_keyboard_devices()
        
        if not self.devices:
            logger.error("No keyboard devices found with numpad support!")
            return False
        
        logger.info(f"Starting monitoring on {len(self.devices)} device(s)")
        
        # Start a thread for each device
        threads = []
        for device in self.devices:
            thread = threading.Thread(target=self.monitor_device, args=(device,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
        
        return threads
    
    def stop_monitoring(self):
        """Stop monitoring and cleanup"""
        logger.info("Stopping numpad monitoring...")
        self.running = False
        
        # Close all devices
        for device in self.devices:
            try:
                device.close()
            except:
                pass
        
        # Clean up lock file on exit
        self.remove_lock_file()
        logger.info("Monitoring stopped")

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down...")
    global controller
    if controller:
        controller.stop_monitoring()
    sys.exit(0)

def main():
    global controller
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        logger.setLevel(logging.DEBUG)
        logger.info("Running in TEST mode with debug logging")
    
    # Check if running as root (required for accessing input devices)
    if os.geteuid() != 0:
        logger.warning("Warning: Not running as root. May not be able to access input devices.")
        logger.warning("For systemd service, ensure the service runs as root or user has input group access.")
        logger.warning("Try: sudo ./start-controller.sh")
        logger.warning("Or add your user to input group: sudo usermod -a -G input $USER")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting TrainPixels Numpad Controller")
    
    # Show user information
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user and os.geteuid() == 0:
        logger.info(f"Running as sudo for user: {sudo_user}")
    else:
        logger.info(f"Running as user: {os.environ.get('USER', 'unknown')}")
    
    logger.info(f"Cache directory: {CACHE_DIR}")
    logger.info(f"Cache file: {CACHE_FILE}")
    logger.info(f"Lock file: {LOCK_FILE}")
    
    controller = NumpadController()
    
    try:
        threads = controller.start_monitoring()
        if not threads:
            logger.error("Failed to start monitoring")
            sys.exit(1)
        
        logger.info("Numpad controller is running. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while controller.running:
            time.sleep(1)
            
            # Check if any threads are still alive
            alive_threads = [t for t in threads if t.is_alive()]
            if not alive_threads and controller.running:
                logger.warning("All monitoring threads stopped, restarting...")
                threads = controller.start_monitoring()
                if not threads:
                    logger.error("Failed to restart monitoring")
                    break
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        controller.stop_monitoring()

if __name__ == "__main__":
    main()
