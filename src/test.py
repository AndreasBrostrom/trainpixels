#!/usr/bin/env python3
import time
import multiprocessing
import sys

# Configuration
TRACK_PIN = "D19"
UTIL_PIN = "D26"
TRACK_PIXEL_LENGTH = 41
UTIL_PIXEL_LENGTH = 43
BRIGHTNESS = 0.3

try:
    import board
    import neopixel

    # Get the actual pin objects
    TRACK_PIN_OBJ = getattr(board, TRACK_PIN)
    UTIL_PIN_OBJ = getattr(board, UTIL_PIN)

except Exception as error:
    from debug import DummyBoard, DummyPixels
    print("\033[93mWARNING: Neopixel library not supported. Using dummy classes for testing.\033[0m")
    print(f"\033[93m         Error details: {error}\033[0m")

    class MockNeoPixel:
        NeoPixel = DummyPixels

    board = DummyBoard()
    neopixel = MockNeoPixel()

    TRACK_PIN_OBJ = getattr(board, TRACK_PIN)
    UTIL_PIN_OBJ = getattr(board, UTIL_PIN)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (int(pos * 3), int(255 - pos * 3), 0)
    elif pos < 170:
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))


def rainbow_animation(pin_obj, pixel_length, strip_name):
    """Run rainbow animation on a specific LED strip."""
    try:
        # Initialize the LED strip
        pixels = neopixel.NeoPixel(
            pin_obj,
            pixel_length,
            brightness=BRIGHTNESS,
            auto_write=False
        )

        print(
            f"Starting rainbow animation on {strip_name} ({pixel_length} pixels)")

        frame = 0
        while True:
            # Update all pixels for this frame
            for i in range(pixel_length):
                pixel_index = (i * 256 // pixel_length) + frame * 2
                r, g, b = wheel(pixel_index & 255)
                pixels[i] = (int(r * BRIGHTNESS),
                             int(g * BRIGHTNESS), int(b * BRIGHTNESS))

            pixels.show()
            # Reset frame counter to prevent overflow
            frame = (frame + 1) % 256
            time.sleep(0.05)  # Control animation speed

    except KeyboardInterrupt:
        print(f"\n{strip_name} animation stopped by user")
        # Turn off LEDs
        pixels.fill((0, 0, 0))
        pixels.show()
    except Exception as e:
        print(f"Error in {strip_name} animation: {e}")


def main():
    print("🌈 Independent Rainbow Animation Script 🌈")
    print(f"Track Strip: {TRACK_PIN} ({TRACK_PIXEL_LENGTH} pixels)")
    print(f"Util Strip:  {UTIL_PIN} ({UTIL_PIXEL_LENGTH} pixels)")
    print(f"Brightness: {BRIGHTNESS}")
    print("\nPress Ctrl+C to stop")
    print("-" * 50)

    try:
        # Create processes for parallel execution
        track_process = multiprocessing.Process(
            target=rainbow_animation,
            args=(TRACK_PIN_OBJ, TRACK_PIXEL_LENGTH, "TRACK")
        )

        util_process = multiprocessing.Process(
            target=rainbow_animation,
            args=(UTIL_PIN_OBJ, UTIL_PIXEL_LENGTH, "UTIL")
        )

        # Start both processes
        track_process.start()
        util_process.start()

        # Wait for both processes to complete
        track_process.join()
        util_process.join()

    except KeyboardInterrupt:
        print("Shutting down rainbow animations...")

        # Terminate processes if they're still running
        if track_process.is_alive():
            track_process.terminate()
            track_process.join()

        if util_process.is_alive():
            util_process.terminate()
            util_process.join()

        print("All animations stopped. LEDs turned off.")

    except Exception as e:
        print(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
