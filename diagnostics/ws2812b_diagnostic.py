#!/usr/bin/env python3
"""
WS2812B LED Diagnostic Tool
Tests WS2812B LEDs with detailed debugging
"""

import time
import sys

def test_imports():
    """Test if required libraries are available"""
    print("🔍 Testing imports...")
    
    try:
        import board
        print("✅ board module imported")
    except ImportError as e:
        print(f"❌ board import failed: {e}")
        return False
    
    try:
        import neopixel
        print("✅ neopixel module imported")
    except ImportError as e:
        print(f"❌ neopixel import failed: {e}")
        return False
    
    return True

def test_basic_led():
    """Test basic LED functionality"""
    print("\n🧪 Testing WS2812B LEDs...")
    
    try:
        import board
        import neopixel
        
        # Try different configurations
        configs = [
            {"pixels": 1, "brightness": 0.1},
            {"pixels": 1, "brightness": 0.5},
            {"pixels": 3, "brightness": 0.3},
            {"pixels": 10, "brightness": 0.2}
        ]
        
        for i, config in enumerate(configs):
            print(f"\n  Test {i+1}: {config['pixels']} LED(s), brightness {config['brightness']}")
            
            try:
                # Initialize with current config
                pixels = neopixel.NeoPixel(
                    board.D18, 
                    config['pixels'], 
                    brightness=config['brightness'], 
                    auto_write=False
                )
                print(f"    ✅ NeoPixel initialized ({config['pixels']} LEDs)")
                
                # Test colors
                colors = [
                    ("Red", (255, 0, 0)),
                    ("Green", (0, 255, 0)), 
                    ("Blue", (0, 0, 255)),
                    ("White", (255, 255, 255))
                ]
                
                for color_name, color_value in colors:
                    print(f"    🎨 Testing {color_name}... ", end="", flush=True)
                    pixels.fill(color_value)
                    pixels.show()
                    time.sleep(2)
                    print("done")
                
                # Turn off
                pixels.fill((0, 0, 0))
                pixels.show()
                print(f"    ✅ Test {i+1} completed")
                
                # Ask user for feedback
                response = input(f"    ❓ Did you see {color_name} LEDs? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    print(f"    🎉 SUCCESS! LEDs working with {config['pixels']} pixels")
                    return True
                
                pixels.deinit()
                
            except Exception as e:
                print(f"    ❌ Test {i+1} failed: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ LED test failed: {e}")
        return False

def test_different_pins():
    """Test WS2812B on different GPIO pins"""
    print("\n🔌 Testing different GPIO pins...")
    
    try:
        import board
        import neopixel
        
        # Try different pins
        pins = [
            ("GPIO 18", board.D18),
            ("GPIO 19", board.D19),
            ("GPIO 21", board.D21),
            ("GPIO 12", board.D12)
        ]
        
        for pin_name, pin in pins:
            print(f"\n  Testing {pin_name}...")
            
            try:
                pixels = neopixel.NeoPixel(pin, 1, brightness=0.3, auto_write=False)
                print(f"    ✅ {pin_name} initialized")
                
                # Quick red test
                pixels.fill((255, 0, 0))
                pixels.show()
                time.sleep(2)
                
                pixels.fill((0, 0, 0))
                pixels.show()
                
                response = input(f"    ❓ Did LED light up on {pin_name}? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    print(f"    🎉 {pin_name} works!")
                    pixels.deinit()
                    return pin_name, pin
                
                pixels.deinit()
                
            except Exception as e:
                print(f"    ❌ {pin_name} failed: {e}")
        
        return None, None
        
    except Exception as e:
        print(f"❌ Pin test failed: {e}")
        return None, None

def hardware_checklist():
    """Print hardware checklist"""
    print("\n📋 WS2812B Hardware Checklist")
    print("=" * 40)
    print("Check these connections:")
    print("  🔴 VCC (Red wire) → 5V (Pin 2 or 4)")
    print("  ⚫ GND (Black wire) → GND (Pin 6)")  
    print("  🟢 Data (Green/White wire) → GPIO 18 (Pin 12) + 330Ω resistor")
    print()
    print("Power requirements:")
    print("  • 1-3 LEDs: Pi power OK")
    print("  • 4+ LEDs: Use external 5V supply")
    print("  • Each LED: ~60mA at full brightness")
    print()
    print("Common issues:")
    print("  • No resistor on data line")
    print("  • Insufficient power supply")
    print("  • Wrong LED type (not WS2812B)")
    print("  • Reversed connections")
    print("  • Bad connections/soldering")
    print()

def main():
    print("🚀 WS2812B LED Diagnostic Tool")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Cannot proceed - missing required libraries")
        print("Install with: pip install adafruit-circuitpython-neopixel adafruit-blinka")
        return
    
    print("\n" + "="*50)
    hardware_checklist()
    
    # Test basic LED functionality
    if test_basic_led():
        print("\n🎉 WS2812B LEDs are working!")
        print("Your main script should work now.")
    else:
        print("\n🔧 LEDs not responding. Trying different pins...")
        working_pin_name, working_pin = test_different_pins()
        
        if working_pin:
            print(f"\n✅ Found working pin: {working_pin_name}")
            print(f"Update your main.py to use: LED_PIN = {working_pin}")
        else:
            print("\n❌ No working pins found.")
            print("This suggests a hardware issue:")
            print("  • Check wiring connections")
            print("  • Verify power supply")
            print("  • Test with a multimeter")
            print("  • Try a different LED strip")

if __name__ == "__main__":
    main()