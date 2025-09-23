#!/usr/bin/env python3
"""
LED Strip Rainbow Controller
This script supports multiple LED types and displays rainbow colors
across pixels with smooth animation.

Supported LED types:
- WS2812/WS2811 (NeoPixel)
- APA102/SK9822 (DotStar)  
- WS2801
- PWM RGB LEDs
"""

import time
import board
import sys

# Configuration
LED_TYPE = "NEOPIXEL"    # Options: "NEOPIXEL", "DOTSTAR", "WS2801", "PWM"
NUM_PIXELS = 10          # Number of LEDs in the strip
BRIGHTNESS = 1.0         # LED brightness (0.0 to 1.0)
UPDATE_DELAY = 0.05      # Delay between updates in seconds (controls animation speed)

# Pin configurations for different LED types
PIN_CONFIGS = {
    "NEOPIXEL": {
        "data_pin": board.D18,  # GPIO pin for data
    },
    "DOTSTAR": {
        "data_pin": board.D10,  # MOSI (GPIO 10)
        "clock_pin": board.D11, # SCLK (GPIO 11)
    },
    "WS2801": {
        "data_pin": board.D10,  # MOSI (GPIO 10)
        "clock_pin": board.D11, # SCLK (GPIO 11)
    },
    "PWM": {
        "red_pin": board.D18,   # Red channel
        "green_pin": board.D19, # Green channel
        "blue_pin": board.D20,  # Blue channel
    }
}

def initialize_leds():
    """
    Initialize the LED strip based on the configured LED_TYPE.
    Returns the initialized LED object or None if initialization fails.
    """
    try:
        if LED_TYPE == "NEOPIXEL":
            import neopixel
            print(f"Initializing NeoPixel LEDs on pin {PIN_CONFIGS['NEOPIXEL']['data_pin']}")
            return neopixel.NeoPixel(
                PIN_CONFIGS["NEOPIXEL"]["data_pin"], 
                NUM_PIXELS, 
                brightness=BRIGHTNESS, 
                auto_write=False
            )
            
        elif LED_TYPE == "DOTSTAR":
            import adafruit_dotstar
            print(f"Initializing DotStar LEDs on data pin {PIN_CONFIGS['DOTSTAR']['data_pin']}, clock pin {PIN_CONFIGS['DOTSTAR']['clock_pin']}")
            return adafruit_dotstar.DotStar(
                PIN_CONFIGS["DOTSTAR"]["clock_pin"],
                PIN_CONFIGS["DOTSTAR"]["data_pin"],
                NUM_PIXELS,
                brightness=BRIGHTNESS,
                auto_write=False
            )
            
        elif LED_TYPE == "WS2801":
            import adafruit_ws2801
            print(f"Initializing WS2801 LEDs on data pin {PIN_CONFIGS['WS2801']['data_pin']}, clock pin {PIN_CONFIGS['WS2801']['clock_pin']}")
            return adafruit_ws2801.WS2801(
                PIN_CONFIGS["WS2801"]["clock_pin"],
                PIN_CONFIGS["WS2801"]["data_pin"],
                NUM_PIXELS,
                brightness=BRIGHTNESS,
                auto_write=False
            )
            
        elif LED_TYPE == "PWM":
            import pwmio
            print(f"Initializing PWM RGB LEDs on pins R:{PIN_CONFIGS['PWM']['red_pin']}, G:{PIN_CONFIGS['PWM']['green_pin']}, B:{PIN_CONFIGS['PWM']['blue_pin']}")
            return {
                'red': pwmio.PWMOut(PIN_CONFIGS["PWM"]["red_pin"]),
                'green': pwmio.PWMOut(PIN_CONFIGS["PWM"]["green_pin"]),
                'blue': pwmio.PWMOut(PIN_CONFIGS["PWM"]["blue_pin"]),
                'type': 'PWM'
            }
            
        else:
            print(f"Error: Unsupported LED type '{LED_TYPE}'")
            print("Supported types: NEOPIXEL, DOTSTAR, WS2801, PWM")
            return None
            
    except ImportError as e:
        print(f"Error: Missing library for {LED_TYPE} LEDs: {e}")
        print("Please install the required library:")
        if LED_TYPE == "NEOPIXEL":
            print("  pip install adafruit-circuitpython-neopixel")
        elif LED_TYPE == "DOTSTAR":
            print("  pip install adafruit-circuitpython-dotstar")
        elif LED_TYPE == "WS2801":
            print("  pip install adafruit-circuitpython-ws2801")
        elif LED_TYPE == "PWM":
            print("  PWM functionality is included in adafruit-blinka (already installed)")
        return None
        
    except Exception as e:
        print(f"Error initializing {LED_TYPE} LEDs: {e}")
        print("Please check your wiring and pin configuration.")
        return None

def set_pixel_color(pixels, index, color):
    """
    Set a pixel color, handling different LED types.
    """
    if pixels is None:
        return
        
    if hasattr(pixels, 'type') and pixels['type'] == 'PWM':
        # For PWM LEDs, we only control one RGB LED (index is ignored)
        r, g, b = color
        pixels['red'].duty_cycle = int(r * 65535 / 255)
        pixels['green'].duty_cycle = int(g * 65535 / 255)
        pixels['blue'].duty_cycle = int(b * 65535 / 255)
    else:
        # For addressable LEDs (NeoPixel, DotStar, WS2801)
        if index < len(pixels):
            pixels[index] = color

def show_pixels(pixels):
    """
    Update the LED display, handling different LED types.
    """
    if pixels is None:
        return
        
    if hasattr(pixels, 'type') and pixels['type'] == 'PWM':
        # PWM LEDs are updated immediately when duty_cycle is set
        pass
    else:
        # For addressable LEDs
        pixels.show()

def fill_pixels(pixels, color):
    """
    Fill all pixels with the same color, handling different LED types.
    """
    if pixels is None:
        return
        
    if hasattr(pixels, 'type') and pixels['type'] == 'PWM':
        set_pixel_color(pixels, 0, color)
    else:
        pixels.fill(color)

# Initialize the LED strip
pixels = initialize_leds()

def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB.
    h: hue (0-360)
    s: saturation (0-1)
    v: value/brightness (0-1)
    Returns: (r, g, b) tuple with values 0-255
    """
    h = h / 60.0
    c = v * s
    x = c * (1 - abs(h % 2 - 1))
    m = v - c
    
    if 0 <= h < 1:
        r, g, b = c, x, 0
    elif 1 <= h < 2:
        r, g, b = x, c, 0
    elif 2 <= h < 3:
        r, g, b = 0, c, x
    elif 3 <= h < 4:
        r, g, b = 0, x, c
    elif 4 <= h < 5:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    
    return (r, g, b)

def generate_rainbow_colors(num_pixels, hue_offset=0):
    """
    Generate rainbow colors for the specified number of pixels.
    num_pixels: number of LEDs
    hue_offset: offset for animation (0-360)
    Returns: list of (r, g, b) tuples
    """
    colors = []
    # For PWM LEDs, we only have one RGB LED, so use the first color
    pixel_count = 1 if LED_TYPE == "PWM" else num_pixels
    
    for i in range(pixel_count):
        hue = (i * 360 / pixel_count + hue_offset) % 360
        colors.append(hsv_to_rgb(hue, 1.0, 1.0))
    return colors

def rainbow_cycle():
    """
    Continuously cycle through rainbow colors on the LED strip.
    """
    if pixels is None:
        print("LEDs not initialized. Cannot start animation.")
        return
        
    print("Starting rainbow animation... Press Ctrl+C to stop")
    hue_offset = 0
    
    try:
        while True:
            # Generate rainbow colors with current offset
            colors = generate_rainbow_colors(NUM_PIXELS, hue_offset)
            
            if LED_TYPE == "PWM":
                # For PWM, just set the single RGB LED to the first color
                set_pixel_color(pixels, 0, colors[0])
            else:
                # Set each pixel to its rainbow color
                for i, color in enumerate(colors):
                    set_pixel_color(pixels, i, color)
            
            # Update the strip
            show_pixels(pixels)
            
            # Increment hue offset for smooth animation
            hue_offset = (hue_offset + 5) % 360
            
            # Wait before next update
            time.sleep(UPDATE_DELAY)
            
    except KeyboardInterrupt:
        print("\nStopping rainbow animation...")
        # Turn off all LEDs
        fill_pixels(pixels, (0, 0, 0))
        show_pixels(pixels)
        print("LEDs turned off. Goodbye!")

def static_rainbow():
    """
    Display a static rainbow across the LED strip.
    """
    if pixels is None:
        print("LEDs not initialized. Cannot display rainbow.")
        return
        
    print("Displaying static rainbow colors...")
    colors = generate_rainbow_colors(NUM_PIXELS)
    
    if LED_TYPE == "PWM":
        # For PWM, just set the single RGB LED to the first color
        set_pixel_color(pixels, 0, colors[0])
    else:
        for i, color in enumerate(colors):
            set_pixel_color(pixels, i, color)
    
    show_pixels(pixels)
    print("Static rainbow displayed. The LEDs will stay on until the script is stopped.")

def test_connection():
    """
    Test LED connection by lighting up LEDs in sequence.
    """
    if pixels is None:
        print("LEDs not initialized. Cannot test connection.")
        return False
        
    print("Testing LED connection...")
    
    try:
        # Test with different colors
        test_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
        color_names = ["Red", "Green", "Blue", "White"]
        
        for color, name in zip(test_colors, color_names):
            print(f"  Testing {name}...")
            fill_pixels(pixels, color)
            show_pixels(pixels)
            time.sleep(1)
        
        # Turn off
        fill_pixels(pixels, (0, 0, 0))
        show_pixels(pixels)
        print("Connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

def test_all_led_variants():
    """
    Test all supported LED variants to find which one works with your hardware.
    This function temporarily changes LED_TYPE and tests each variant.
    """
    global LED_TYPE, pixels
    
    print("🔍 LED Variant Auto-Detection")
    print("=" * 50)
    print("This will test all supported LED types to find which one works")
    print("with your hardware. Watch your LEDs for activity!")
    print()
    
    # Store original configuration
    original_led_type = LED_TYPE
    original_pixels = pixels
    
    # All LED types to test
    led_variants = ["NEOPIXEL", "DOTSTAR", "WS2801", "PWM"]
    working_variants = []
    
    for variant in led_variants:
        print(f"🧪 Testing {variant}...")
        print(f"   Expected wiring:")
        
        # Show expected wiring for this variant
        if variant == "NEOPIXEL":
            print(f"   Data: GPIO 18 (pin 12)")
        elif variant == "DOTSTAR":
            print(f"   Data: GPIO 10 (pin 19), Clock: GPIO 11 (pin 23)")
        elif variant == "WS2801":
            print(f"   Data: GPIO 10 (pin 19), Clock: GPIO 11 (pin 23)")
        elif variant == "PWM":
            print(f"   Red: GPIO 18, Green: GPIO 19, Blue: GPIO 20")
        
        # Temporarily change LED type
        LED_TYPE = variant
        
        # Try to initialize this LED type
        test_pixels = initialize_leds()
        
        if test_pixels is not None:
            print(f"   ✅ {variant} initialized successfully")
            
            # Test with a simple color sequence
            try:
                print(f"   🌈 Testing colors (watch your LEDs)...")
                test_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
                color_names = ["Red", "Green", "Blue"]
                
                for color, name in zip(test_colors, color_names):
                    print(f"      {name}...", end=" ", flush=True)
                    fill_pixels(test_pixels, color)
                    show_pixels(test_pixels)
                    time.sleep(1.5)
                    print("done")
                
                # Turn off
                fill_pixels(test_pixels, (0, 0, 0))
                show_pixels(test_pixels)
                
                print(f"   ✅ {variant} test completed successfully!")
                working_variants.append(variant)
                
                # Ask user if they saw the LEDs work
                response = input(f"   ❓ Did you see the LEDs light up with {variant}? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    print(f"   🎉 {variant} confirmed working by user!")
                else:
                    print(f"   ❌ {variant} not working according to user")
                    if variant in working_variants:
                        working_variants.remove(variant)
                
            except Exception as e:
                print(f"   ❌ {variant} test failed: {e}")
        else:
            print(f"   ❌ {variant} initialization failed")
        
        print()
    
    # Restore original configuration
    LED_TYPE = original_led_type
    pixels = original_pixels
    
    # Report results
    print("🎯 Test Results Summary")
    print("=" * 30)
    
    if working_variants:
        print("✅ Working LED variants found:")
        for variant in working_variants:
            print(f"   • {variant}")
        
        print(f"\n💡 Recommendations:")
        if len(working_variants) == 1:
            recommended = working_variants[0]
            print(f"   Use LED_TYPE = \"{recommended}\" in your configuration")
        else:
            print("   Multiple variants work! Choose based on your hardware:")
            for variant in working_variants:
                if variant == "NEOPIXEL":
                    print(f"   • {variant}: Best for WS2812/WS2811 strips")
                elif variant == "DOTSTAR":
                    print(f"   • {variant}: Best for APA102/SK9822 strips")
                elif variant == "WS2801":
                    print(f"   • {variant}: Best for WS2801 strips")
                elif variant == "PWM":
                    print(f"   • {variant}: Best for single RGB LEDs/modules")
        
        # Offer to update configuration automatically
        if len(working_variants) == 1:
            auto_update = input(f"\n🔧 Auto-update LED_TYPE to \"{working_variants[0]}\"? (y/n): ").lower().strip()
            if auto_update in ['y', 'yes']:
                # Update the configuration in the global variable
                LED_TYPE = working_variants[0]
                # Re-initialize with the working variant
                pixels = initialize_leds()
                print(f"✅ Configuration updated to {LED_TYPE}")
                return True
    else:
        print("❌ No working LED variants found")
        print("\n🔧 Troubleshooting suggestions:")
        print("   1. Check your wiring connections")
        print("   2. Verify power supply (5V for most LEDs)")
        print("   3. Try running with sudo for GPIO permissions")
        print("   4. Check if your LED type is supported")
        print("   5. Measure voltage on data/clock lines")
        
    print(f"\n🔄 Current configuration remains: LED_TYPE = \"{LED_TYPE}\"")
    return len(working_variants) > 0

def main():
    """
    Main function - provides options for different LED operations.
    """
    print("🌈 LED Strip Rainbow Controller")
    print("=" * 40)
    print(f"LED Type: {LED_TYPE}")
    print(f"Number of pixels: {NUM_PIXELS}")
    if LED_TYPE != "PWM":
        print(f"Pin configuration: {PIN_CONFIGS[LED_TYPE]}")
    else:
        print(f"PWM pins - R: {PIN_CONFIGS['PWM']['red_pin']}, G: {PIN_CONFIGS['PWM']['green_pin']}, B: {PIN_CONFIGS['PWM']['blue_pin']}")
    print(f"Brightness: {BRIGHTNESS}")
    print()
    
    # Check if current LED type failed to initialize
    if pixels is None:
        print("❌ Failed to initialize current LED type.")
        print("\n🔧 Options:")
        print("1. Run LED variant test to find working type")
        print("2. Check configuration and wiring manually")
        print("3. Exit and fix issues")
        
        choice = input("\nRun LED variant auto-detection? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            if test_all_led_variants():
                print(f"\n✅ Found working LED type: {LED_TYPE}")
                print("Proceeding with rainbow animation...")
            else:
                print("\n❌ No working LED variants found. Please check wiring and try again.")
                return
        else:
            print("\nPlease check:")
            print("1. LED type configuration")
            print("2. Pin connections") 
            print("3. Required libraries are installed")
            print("4. Hardware permissions (try running with sudo)")
            return
    
    # If we have working LEDs, ask what to do
    print("🎮 Choose an option:")
    print("1. Test current LED connection")
    print("2. Run rainbow animation")
    print("3. Test all LED variants (auto-detect)")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🧪 Testing current LED connection...")
            if test_connection():
                print("✅ Connection test passed!")
            else:
                print("❌ Connection test failed.")
            break
            
        elif choice == "2":
            print("\n🌈 Starting rainbow animation...")
            time.sleep(1)
            rainbow_cycle()
            break
            
        elif choice == "3":
            print("\n🔍 Testing all LED variants...")
            test_all_led_variants()
            # Ask if user wants to continue with animation
            continue_choice = input("\nRun rainbow animation with current settings? (y/n): ").lower().strip()
            if continue_choice in ['y', 'yes']:
                rainbow_cycle()
            break
            
        elif choice == "4":
            print("👋 Goodbye!")
            return
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
