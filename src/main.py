#!/usr/bin/env python3
import multiprocessing
import random
import time
import json
import sys
import os

"""
status codes
0 - success
1 - error
2 - no action taken
3 - invalid input
4 - already in desired state
5 - timeout
6 - not supported
7 - hardware failure
8 - software failure
9 - unknown error
"""

COLOR_TABLE = {
    # Define colors with RGBA values
    "red": (255, 0, 0, 0.5),
    "green": (0, 255, 0, 0.5),
    "white": (255, 255, 255, 0.2),
    "blue": (0, 0, 255, 0.5),
    "yellow": (255, 255, 0, 0.5),
    "purple": (128, 0, 128, 0.5),
    "off": (0, 0, 0, 0.5)
}

TEST_EVENT = {
    "id": "event_01",
    "name": "blink_led_9",
    "events": [
        {
            "led": 9,
            "blink": True,
            "duration": 5,
            "color": "blue"
        }
    ]
}
global TRACKS
TRACKS = []

random.seed(time.time())
SCRIPT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Get configs


def fetch_config():
    home_config = os.path.join(os.path.expanduser(
        "~"), ".config", "trailpixel", "config.json")
    local_config = os.path.join(SCRIPT_ROOT, "config.json")
    config_path = None
    if os.path.exists(local_config):
        config_path = local_config
    elif os.path.exists(home_config):
        config_path = home_config
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                num_pixels = config.get('NUM_PIXELS')
                led_pin_name = config.get('LED_PIN', 'D21')
                random_event_chance = config.get('RANDOM_EVENT_CHANCE')
                return num_pixels, led_pin_name, random_event_chance
        except json.JSONDecodeError:
            print("Error decoding config file.")
            sys.exit(1)
    print("Config file not found in $scriptRoot or $HOME/.config/trailpixel.")
    sys.exit(1)


NUM_PIXELS, LED_PIN_NAME, RANDOM_EVENT_CHANCE = fetch_config()
try:
    import board
    import neopixel

    # Convert LED_PIN_NAME string from config to board attribute
    LED_PIN = getattr(board, LED_PIN_NAME)

    pixels = neopixel.NeoPixel(
        LED_PIN,
        NUM_PIXELS,
        brightness=1.0,
        auto_write=False)
except NotImplementedError:
    print("WARNING: Neopixel library not supported on this platform. Using dummy classes.")
    from debug import DummyBoard, DummyPixels
    board = DummyBoard()
    LED_PIN = getattr(board, LED_PIN_NAME)
    pixels = DummyPixels(LED_PIN, NUM_PIXELS, brightness=1.0, auto_write=False)


# FUNCTIONS

def led_boot_startup_sequence():
    def wheel(pos):
        # Generate rainbow colors across 0-255 positions.
        if pos < 85:
            return (int(pos * 3), int(255 - pos * 3), 0)
        elif pos < 170:
            pos -= 85
            return (int(255 - pos * 3), 0, int(pos * 3))
        else:
            pos -= 170
            return (0, int(pos * 3), int(255 - pos * 3))

    # Rainbow animation across all LEDs
    for j in range(32):  # Number of animation frames
        for i in range(NUM_PIXELS):
            pixel_index = (i * 256 // NUM_PIXELS) + j * 8
            r, g, b = wheel(pixel_index & 255)
            brightness = 0.5  # You can adjust this or fetch from config
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
        pixels.show()
        time.sleep(0.05)
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(3)
    return 0


def get_color(name):
    return COLOR_TABLE.get(name, (0, 0, 0, 0))  # Default to off if not found


def event_picker():
    # This function would pick a random event from events.d folder
    return TEST_EVENT


def event_runner(event) -> int:
    for e in event.get('events', []):
        if e.get('blink', False):
            led_index = e.get('led')
            color_name = e.get('color')
            duration = e.get('duration')

            r, g, b, brightness = get_color(color_name)
            pixels[led_index] = (int(r * brightness),
                                 int(g * brightness), int(b * brightness))
            pixels.show()
            time.sleep(duration)

            # Turn off LED
            r, g, b, brightness = get_color("off")
            pixels[led_index] = (int(r * brightness),
                                 int(g * brightness), int(b * brightness))
            pixels.show()
            return 0
    return 2  # No action taken


def track_build_init():
    # This function build all the tracks from json files from tracks.d folder
    print("Assembling tracks..")

    # ADD FUNCTION ASSEMBLY HERE
    for filename in os.listdir(os.path.join(SCRIPT_ROOT, "tracks.d")):
        if filename.endswith(".json"):
            with open(os.path.join(SCRIPT_ROOT, "tracks.d", filename), 'r') as f:
                track = json.load(f)
                TRACKS.append(track)
    if len(TRACKS) == 0:
        print("No tracks found in tracks.d folder exiting.")
        sys.exit(1)

    print(f"  {len(TRACKS)} tracks have been assembled.")
    return 0


def track_pick_tracker() -> dict:
    # pick a random track from TRACKS
    if TRACKS is None or len(TRACKS) == 0:
        print("No tracks can be selected from tracks.d folder exiting.")
        sys.exit(1)
    return TRACKS[random.randint(0, len(TRACKS) - 1)]


def start_path_animation(track_led_path: list, track_led_indicator: int) -> int:
    try:
        if not track_led_path:
            print("No LED path provided.")
            return 2  # No action taken

        # initialize path led path
        print(f"  Path:      {track_led_path}")
        print(f"  Indicator: {track_led_indicator}")

        # turn on track indicator
        r, g, b, brightness = get_color("yellow")
        pixels[track_led_indicator] = (int(r * brightness),
                                       int(g * brightness), int(b * brightness))
        pixels.show()

        for i in track_led_path:
            r, g, b, brightness = get_color("white")
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
            pixels.show()
        time.sleep(3)

        # animate path
        for i in track_led_path:
            r, g, b, brightness = get_color("red")
            print(f"  Setting LED {i} to red")
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
            pixels.show()

            # add possible event
            if (random.randint(0, 10) < RANDOM_EVENT_CHANCE):
                print("  Random event triggered...")
                event = event_picker()
                p = multiprocessing.Process(target=event_runner, args=(event,))
                p.start()
                pixels.show()
            time.sleep(3)

        # turn off path
        print("  Turning off path")
        r, g, b, brightness = get_color("off")
        for i in track_led_path:
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
        pixels[track_led_indicator] = (int(r * brightness),
                                       int(g * brightness), int(b * brightness))
        pixels.show()
        time.sleep(2)
        return 0
    except KeyboardInterrupt:
        print("\nLEDs turned off. Goodbye!")
        pixels.fill((0, 0, 0))
        pixels.show()
        sys.exit(0)


def main():
    try:
        print("Starting TrainPixels")
        print(f"  Pixels: {NUM_PIXELS}")
        print(f"  Pin: {LED_PIN_NAME}")
        print("")

        led_boot_startup_sequence()
        track_build_init()

        while True:
            time.sleep(2)
            print("Picking track")
            track = track_pick_tracker()

            print(f"  Selected track: {track['name']}")
            start_path_animation(
                track["led_path"], track["led_path_indicator"])

    except NotImplementedError:
        print("Functionality not yet implemented.")
    except KeyboardInterrupt:
        print("\nLEDs turned off. Goodbye!")
        pixels.fill((0, 0, 0))
        pixels.show()
        sys.exit(0)


if __name__ == "__main__":
    main()
