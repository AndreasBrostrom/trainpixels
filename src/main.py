#!/usr/bin/env python3
import multiprocessing
from random import randint
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
    "white": (255, 255, 255, 0.5),
    "blue": (0, 0, 255, 0.5),
    "yellow": (255, 255, 0, 0.5),
    "purple": (128, 0, 128, 0.5),
    "off": (0, 0, 0, 0.5)
}

TEST_TRACK = {
    "id": "track_01",
    "name": "Sample Track",
    "led_path": [0, 1, 2, 3, 4, 5, 6, 7],
    "led_path_indicator": 8
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


# Get configs
def fetch_config():
    script_root = os.path.dirname(os.path.abspath(__file__))
    home_config = os.path.join(os.path.expanduser(
        "~"), ".config", "trailpixel", "config.json")
    local_config = os.path.join(script_root, "config.json")
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


NUM_PIXELS, LED_PIN, RANDOM_EVENT_CHANCE = fetch_config()

try:
    import board
    import neopixel

    pixels = neopixel.NeoPixel(
        LED_PIN,
        NUM_PIXELS,
        brightness=1.0,
        auto_write=False)

except NotImplementedError:
    print("Neopixel library not supported on this platform. Using dummy classes.")
    from debug import DummyBoard, DummyPixels
    board = DummyBoard()
    LED_PIN = board.D21
    pixels = DummyPixels(LED_PIN, NUM_PIXELS, brightness=1.0, auto_write=False)


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
    return 0


def track_pick_tracker():
    # In a real scenario, this function would dynamically select a track
    # this from a array of tracks from track.d folder
    # [{},{},{}]
    return TEST_TRACK  # In real scenario, this would be dynamic


def start_path_animation(track_led_path=[]) -> int:
    if not track_led_path:
        print("No LED path provided.")
        return 2  # No action taken

    # initialize path led path
    for i in track_led_path:
        r, g, b, brightness = get_color("white")
        print(f"Setting LED {i} to white")
        pixels[i] = (int(r * brightness),
                     int(g * brightness), int(b * brightness))
        pixels.show()
    time.sleep(3)

    # animate path
    for i in track_led_path:
        r, g, b, brightness = get_color("red")
        print(f"Setting LED {i} to red")
        pixels[i] = (int(r * brightness),
                     int(g * brightness), int(b * brightness))

    # add possible event
        if (randint(0, 10) < RANDOM_EVENT_CHANCE):
            print("Random event triggered...")
            event = event_picker()
            p = multiprocessing.Process(target=event_runner, args=(event,))
            p.start()

            pixels.show()
        time.sleep(3)

        # turn off path
        for i in track_led_path:
            r, g, b, brightness = get_color("off")
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
            pixels.show()

    return 0


def led_boot_startup_sequence():
    pass


def main():
    try:
        print("Starting LED...")
        led_boot_startup_sequence()

        while True:
            print("Picking track...")
            track = track_pick_tracker()

            print(f"Selected track: {track['name']}")
            status = start_path_animation(track["led_path"])

    except NotImplementedError:
        print("Functionality not yet implemented.")
    except KeyboardInterrupt:
        # Turn off all LEDs when stopping
        pixels.fill((0, 0, 0))
        pixels.show()
        print("\nLEDs turned off. Goodbye!")


if __name__ == "__main__":
    main()
