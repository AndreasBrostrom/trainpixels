#!/usr/bin/env python3
"""
LED Strip Rainbow Controller
This script controls a WS2812/WS2811 LED strip to display rainbow colors
across 10 pixels with smooth animation.
"""

import time
import board
import neopixel

# Configuration
NUM_PIXELS = 10      # Number of LEDs in the strip
LED_PIN = board.D18  # GPIO pin connected to the LED strip (change if needed)
BRIGHTNESS = 0.3     # LED brightness (0.0 to 1.0)
UPDATE_DELAY = 0.05  # Delay between updates in seconds (controls animation speed)

# Initialize the LED strip
pixels = neopixel.NeoPixel(LED_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)

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
    for i in range(num_pixels):
        hue = (i * 360 / num_pixels + hue_offset) % 360
        colors.append(hsv_to_rgb(hue, 1.0, 1.0))
    return colors

def rainbow_cycle():
    """
    Continuously cycle through rainbow colors on the LED strip.
    """
    print("Starting rainbow animation... Press Ctrl+C to stop")
    hue_offset = 0
    
    try:
        while True:
            # Generate rainbow colors with current offset
            colors = generate_rainbow_colors(NUM_PIXELS, hue_offset)
            
            # Set each pixel to its rainbow color
            for i, color in enumerate(colors):
                pixels[i] = color
            
            # Update the strip
            pixels.show()
            
            # Increment hue offset for smooth animation
            hue_offset = (hue_offset + 5) % 360
            
            # Wait before next update
            time.sleep(UPDATE_DELAY)
            
    except KeyboardInterrupt:
        print("\nStopping rainbow animation...")
        # Turn off all LEDs
        pixels.fill((0, 0, 0))
        pixels.show()
        print("LEDs turned off. Goodbye!")

def static_rainbow():
    """
    Display a static rainbow across the LED strip.
    """
    print("Displaying static rainbow colors...")
    colors = generate_rainbow_colors(NUM_PIXELS)
    
    for i, color in enumerate(colors):
        pixels[i] = color
    
    pixels.show()
    print("Static rainbow displayed. The LEDs will stay on until the script is stopped.")

def main():
    """
    Main function - starts the rainbow animation immediately.
    """
    print("LED Strip Rainbow Controller")
    print("=" * 30)
    print(f"Number of pixels: {NUM_PIXELS}")
    print(f"LED pin: {LED_PIN}")
    print(f"Brightness: {BRIGHTNESS}")
    print()
    
    # Start rainbow animation directly
    rainbow_cycle()

if __name__ == "__main__":
    main()
