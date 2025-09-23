#!/usr/bin/env python3
"""
WS2812B Multi-Pin Test
Automatically tries different GPIO pins to find one that works with your LEDs
"""

import time
import board
import neopixel

def test_pin(pin_name, pin, num_pixels=3):
    """Test a specific GPIO pin with WS2812B LEDs"""
    print(f"\n🧪 Testing {pin_name}...")
    
    try:
        # Initialize NeoPixel with this pin
        pixels = neopixel.NeoPixel(pin, num_pixels, brightness=0.3, auto_write=False)
        print(f"  ✅ {pin_name} initialized successfully")
        
        # Test sequence: Red -> Green -> Blue -> White -> Off
        colors = [
            ("Red", (255, 0, 0)),
            ("Green", (0, 255, 0)),
            ("Blue", (0, 0, 255)),
            ("White", (255, 255, 255))
        ]
        
        print(f"  🎨 Testing colors on {pin_name} (watch your LEDs!)...")
        
        for color_name, color_value in colors:
            print(f"    {color_name}...", end=" ", flush=True)
            pixels.fill(color_value)
            pixels.show()
            time.sleep(1.5)
            print("done")
        
        # Turn off
        pixels.fill((0, 0, 0))
        pixels.show()
        print(f"  ✅ {pin_name} test completed")
        
        # Ask user if it worked
        response = input(f"  ❓ Did you see LEDs light up on {pin_name}? (y/n): ").lower().strip()
        
        pixels.deinit()
        
        if response in ['y', 'yes']:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"  ❌ {pin_name} failed: {e}")
        return False

def main():
    print("🔍 WS2812B Multi-Pin Test")
    print("=" * 40)
    print("This will test different GPIO pins to find one that works with your LEDs.")
    print("Make sure your LED data wire can be moved to different pins for testing.")
    print()
    
    # List of pins to test (avoiding GPIO 18 since it's problematic)
    test_pins = [
        ("GPIO 21 (Pin 40)", board.D21),
        ("GPIO 19 (Pin 35)", board.D19),
        ("GPIO 12 (Pin 32)", board.D12),
        ("GPIO 16 (Pin 36)", board.D16),
        ("GPIO 20 (Pin 38)", board.D20),
        ("GPIO 13 (Pin 33)", board.D13)
    ]
    
    working_pins = []
    
    for pin_name, pin in test_pins:
        print(f"\n📍 Connect your LED data wire to {pin_name}")
        input("Press Enter when ready to test this pin...")
        
        if test_pin(pin_name, pin):
            print(f"🎉 SUCCESS! {pin_name} works with your LEDs!")
            working_pins.append((pin_name, pin))
            
            # Ask if they want to continue testing
            continue_test = input("Test more pins? (y/n): ").lower().strip()
            if continue_test not in ['y', 'yes']:
                break
    
    # Summary
    print(f"\n{'='*50}")
    print("🎯 Test Results Summary")
    print("=" * 25)
    
    if working_pins:
        print("✅ Working GPIO pins found:")
        for pin_name, pin in working_pins:
            print(f"   • {pin_name}")
        
        print(f"\n💡 Recommendation:")
        best_pin_name, best_pin = working_pins[0]
        print(f"   Use {best_pin_name} in your main script")
        print(f"   Update LED_PIN = {best_pin}")
        
        # Show wiring
        print(f"\n🔌 Final wiring for {best_pin_name}:")
        print("   VCC (Red) → 5V (Pin 2)")
        print("   GND (Black) → GND (Pin 6)")
        print(f"   Data (Green/White) → {best_pin_name} + 330Ω resistor")
        
    else:
        print("❌ No working pins found")
        print("\nThis suggests a hardware issue:")
        print("   • Check LED strip is actually WS2812B")
        print("   • Verify power connections (5V, GND)")
        print("   • Test with multimeter")
        print("   • Try different LED strip")

if __name__ == "__main__":
    main()