#!/usr/bin/env python3
"""
Simple WS2812B LED White Blink
Blinks all LEDs white on/off
"""

import time
import board
import neopixel

# Configuration
NUM_PIXELS = 10      # Number of LEDs
LED_PIN = board.D18  # GPIO 18 (pin 12)
BRIGHTNESS = 0.5     # 50% brightness

# Initialize LEDs
pixels = neopixel.NeoPixel(LED_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)

def main():
    print("WS2812B White Blink - Press Ctrl+C to stop")
    
    try:
        while True:
            # Turn all LEDs white
            pixels.fill((255, 255, 255))
            pixels.show()
            print("ON")
            time.sleep(1)
            
            # Turn all LEDs off
            pixels.fill((0, 0, 0))
            pixels.show()
            print("OFF")
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Turn off all LEDs when stopping
        pixels.fill((0, 0, 0))
        pixels.show()
        print("\nLEDs turned off. Goodbye!")

if __name__ == "__main__":
    main()