#!/usr/bin/env python3
"""
GPIO 18 Diagnostic Tool
This script tests GPIO 18 to see what's connected and how it responds.
"""

import time

def check_gpio_status():
    """Check if GPIO 18 is already exported or in use"""
    import os
    
    print("🔍 Checking GPIO 18 status...")
    
    # Check if GPIO 18 is already exported
    if os.path.exists('/sys/class/gpio/gpio18'):
        print("⚠️  GPIO 18 is already exported")
        try:
            with open('/sys/class/gpio/gpio18/direction', 'r') as f:
                direction = f.read().strip()
            print(f"   Current direction: {direction}")
            
            with open('/sys/class/gpio/gpio18/value', 'r') as f:
                value = f.read().strip()
            print(f"   Current value: {value}")
            
            return True
        except Exception as e:
            print(f"   Error reading GPIO status: {e}")
            return False
    else:
        print("✅ GPIO 18 is not currently exported")
        return False

def cleanup_gpio():
    """Clean up GPIO 18 if it's already exported"""
    try:
        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write('18')
        print("✅ GPIO 18 cleaned up")
        return True
    except Exception as e:
        print(f"⚠️  Cleanup failed: {e}")
        return False

def test_gpio_basic():
    """Test GPIO 18 using basic Linux GPIO interface"""
    print("🔍 Testing GPIO 18 with basic Linux GPIO interface...")
    
    # First check if GPIO is already in use
    gpio_already_exported = check_gpio_status()
    
    try:
        # If already exported, try to clean up first
        if gpio_already_exported:
            print("🧹 Attempting to clean up existing GPIO export...")
            cleanup_gpio()
            time.sleep(0.5)  # Give system time to clean up
        
        # Export GPIO 18
        print("📤 Exporting GPIO 18...")
        with open('/sys/class/gpio/export', 'w') as f:
            f.write('18')
        print("✅ GPIO 18 exported successfully")
        
        # Small delay to ensure export is complete
        time.sleep(0.1)
        
        # Set as output
        print("📝 Setting GPIO 18 as output...")
        with open('/sys/class/gpio/gpio18/direction', 'w') as f:
            f.write('out')
        print("✅ GPIO 18 set as output")
        
        # Test high/low states
        print("\n🧪 Testing GPIO 18 states (watch for any activity on your hardware):")
        
        for i in range(5):
            # Set HIGH
            print(f"  Cycle {i+1}: Setting GPIO 18 HIGH", end="", flush=True)
            with open('/sys/class/gpio/gpio18/value', 'w') as f:
                f.write('1')
            time.sleep(1)
            
            # Set LOW  
            print(" -> LOW", flush=True)
            with open('/sys/class/gpio/gpio18/value', 'w') as f:
                f.write('0')
            time.sleep(1)
        
        # Clean up
        print("🧹 Cleaning up...")
        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write('18')
        print("✅ GPIO 18 unexported (cleaned up)")
        
        return True
        
    except PermissionError:
        print("❌ Permission denied - try running with sudo")
        print("   Command: sudo python gpio_diagnostic.py")
        return False
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("   This might indicate GPIO subsystem issues")
        return False
    except OSError as e:
        if "Device or resource busy" in str(e):
            print(f"❌ GPIO 18 is busy (already in use by another process)")
            print("   Try: sudo lsof | grep gpio")
            print("   Or: sudo fuser /sys/class/gpio/gpio18/*")
        elif "Invalid argument" in str(e):
            print(f"❌ Invalid argument - GPIO 18 might not be available")
            print("   This could mean:")
            print("   - GPIO 18 is reserved by system")
            print("   - PWM is active on this pin")
            print("   - Pin is used by device tree overlay")
        else:
            print(f"❌ OS Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_gpio_with_blinka():
    """Test GPIO 18 using Adafruit Blinka library"""
    print("\n🔍 Testing GPIO 18 with Adafruit Blinka...")
    
    try:
        import board
        import digitalio
        
        # Initialize GPIO 18 as digital output
        pin18 = digitalio.DigitalInOut(board.D18)
        pin18.direction = digitalio.Direction.OUTPUT
        print("✅ GPIO 18 initialized with Blinka")
        
        print("\n🧪 Testing GPIO 18 with Blinka (watch for activity):")
        
        for i in range(5):
            print(f"  Cycle {i+1}: Setting GPIO 18 HIGH", end="", flush=True)
            pin18.value = True
            time.sleep(1)
            
            print(" -> LOW", flush=True)
            pin18.value = False
            time.sleep(1)
        
        pin18.deinit()
        print("✅ GPIO 18 deinitialized")
        return True
        
    except ImportError:
        print("❌ Adafruit Blinka not installed")
        print("   Install with: pip install adafruit-blinka")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_pwm_output():
    """Test PWM output on GPIO 18"""
    print("\n🔍 Testing PWM output on GPIO 18...")
    
    try:
        import board
        import pwmio
        
        # Initialize PWM on GPIO 18
        pwm18 = pwmio.PWMOut(board.D18, frequency=1000, duty_cycle=0)
        print("✅ PWM initialized on GPIO 18 (1kHz)")
        
        print("\n🧪 Testing PWM fade (0% -> 100% -> 0%):")
        
        # Fade up
        print("  Fading up (0% -> 100%)", end="", flush=True)
        for duty in range(0, 65536, 1000):
            pwm18.duty_cycle = duty
            time.sleep(0.02)
        print(" ✅")
        
        time.sleep(0.5)
        
        # Fade down
        print("  Fading down (100% -> 0%)", end="", flush=True)
        for duty in range(65535, -1, -1000):
            pwm18.duty_cycle = duty
            time.sleep(0.02)
        print(" ✅")
        
        pwm18.deinit()
        print("✅ PWM deinitialized")
        return True
        
    except ImportError:
        print("❌ PWM not available (adafruit-blinka not installed)")
        return False
    except Exception as e:
        print(f"❌ PWM Error: {e}")
        return False

def read_gpio_state():
    """Read current state of GPIO 18"""
    print("\n🔍 Reading current GPIO 18 state...")
    
    try:
        import board
        import digitalio
        
        # Set as input to read current state
        pin18 = digitalio.DigitalInOut(board.D18)
        pin18.direction = digitalio.Direction.INPUT
        pin18.pull = digitalio.Pull.UP  # Enable pull-up
        
        print("✅ GPIO 18 set as input with pull-up")
        
        for i in range(10):
            state = pin18.value
            print(f"  Reading {i+1}: GPIO 18 = {'HIGH' if state else 'LOW'}")
            time.sleep(0.5)
        
        pin18.deinit()
        return True
        
    except Exception as e:
        print(f"❌ Error reading GPIO: {e}")
        return False

def check_what_uses_gpio18():
    """Check what processes or drivers might be using GPIO 18"""
    import subprocess
    import os
    
    print("🔍 Checking what might be using GPIO 18...")
    
    checks = []
    
    # Check if PWM is active
    try:
        if os.path.exists('/sys/class/pwm/pwmchip0/pwm0'):
            checks.append("⚠️  Hardware PWM0 is active (GPIO 18 might be used for PWM)")
        else:
            checks.append("✅ Hardware PWM0 is not active")
    except:
        checks.append("❓ Could not check PWM status")
    
    # Check device tree overlays
    try:
        result = subprocess.run(['dtoverlay', '-l'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            overlays = result.stdout
            if 'pwm' in overlays.lower():
                checks.append("⚠️  PWM overlay detected in device tree")
            if 'audio' in overlays.lower() or 'pcm' in overlays.lower():
                checks.append("⚠️  Audio/PCM overlay detected (might use GPIO 18)")
            if not any(['pwm' in overlays.lower(), 'audio' in overlays.lower(), 'pcm' in overlays.lower()]):
                checks.append("✅ No conflicting overlays detected")
        else:
            checks.append("❓ Could not check device tree overlays")
    except:
        checks.append("❓ Device tree check failed")
    
    # Check if any processes are using GPIO files
    try:
        result = subprocess.run(['sudo', 'lsof', '+D', '/sys/class/gpio/'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            checks.append("⚠️  Processes are accessing GPIO subsystem:")
            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                if line.strip():
                    checks.append(f"     {line}")
        else:
            checks.append("✅ No processes accessing GPIO subsystem")
    except:
        checks.append("❓ Could not check GPIO process usage")
    
    # Check kernel modules
    try:
        result = subprocess.run(['lsmod'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            modules = result.stdout
            gpio_modules = []
            for line in modules.split('\n'):
                if any(mod in line.lower() for mod in ['gpio', 'pwm', 'spi', 'i2c']):
                    gpio_modules.append(line.split()[0])
            
            if gpio_modules:
                checks.append(f"ℹ️  Active GPIO-related modules: {', '.join(gpio_modules[:5])}")
            else:
                checks.append("✅ No obvious GPIO modules loaded")
    except:
        checks.append("❓ Could not check kernel modules")
    
    for check in checks:
        print(f"  {check}")
    
    return checks

def check_gpio_info():
    """Display GPIO 18 information"""
    print("📋 GPIO 18 Pin Information")
    print("=" * 30)
    print("Physical Pin: 12")
    print("GPIO Number: 18")
    print("Alt Functions:")
    print("  - PCM_CLK (Audio)")
    print("  - PWM0 (Hardware PWM)")
    print("  - General Purpose I/O")
    print()
    print("Common uses:")
    print("  - LED strips (WS2812, etc.)")
    print("  - PWM devices (servos, LEDs)")
    print("  - Digital sensors")
    print("  - Audio clock signals")
    print()
    
    # Check what might be using it
    check_what_uses_gpio18()
    print()

def main():
    print("🔧 GPIO 18 Diagnostic Tool")
    print("=" * 40)
    
    check_gpio_info()
    
    print("What would you like to test?")
    print("1. Basic GPIO toggle (Linux GPIO)")
    print("2. GPIO with Blinka library")
    print("3. PWM output test")
    print("4. Read GPIO input state")
    print("5. All tests (comprehensive)")
    print("6. Exit")
    
    while True:
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            test_gpio_basic()
            break
        elif choice == "2":
            test_gpio_with_blinka()
            break
        elif choice == "3":
            test_pwm_output()
            break
        elif choice == "4":
            read_gpio_state()
            break
        elif choice == "5":
            print("\n🔄 Running comprehensive GPIO 18 tests...\n")
            test_gpio_basic()
            test_gpio_with_blinka()
            test_pwm_output()
            read_gpio_state()
            break
        elif choice == "6":
            print("👋 Goodbye!")
            return
        else:
            print("Invalid choice. Please enter 1-6.")
    
    print(f"\n💡 What to look for:")
    print("- LEDs should blink/fade during tests")
    print("- Multimeter should show voltage changes (0V <-> 3.3V)")
    print("- Oscilloscope should show square wave (digital) or PWM signal")
    print("- Connected devices should respond to signal changes")

if __name__ == "__main__":
    main()