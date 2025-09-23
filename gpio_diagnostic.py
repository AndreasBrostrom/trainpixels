#!/usr/bin/env python3
"""
GPIO 18 Diagnostic Tool
This script tests GPIO 18 to see what's connected and how it responds.
"""

import time

def test_gpio_basic():
    """Test GPIO 18 using basic Linux GPIO interface"""
    print("🔍 Testing GPIO 18 with basic Linux GPIO interface...")
    
    try:
        # Export GPIO 18
        with open('/sys/class/gpio/export', 'w') as f:
            f.write('18')
        print("✅ GPIO 18 exported successfully")
        
        # Set as output
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
        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write('18')
        print("✅ GPIO 18 unexported (cleaned up)")
        
        return True
        
    except PermissionError:
        print("❌ Permission denied - try running with sudo")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
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