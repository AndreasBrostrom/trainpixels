#!/usr/bin/env python3
from typing import Tuple
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

random.seed(time.time())
SCRIPT_ROOT = os.path.dirname(os.path.abspath(__file__))


global TRACKS
global EVENTS
TRACKS = []
EVENTS = []


# HANDLE CONFIG
def fetch_config():
    home_config = os.path.join(os.path.expanduser(
        "~"), ".config", "trailpixels", "config.json")
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
                brightness = config.get('BRIGHTNESS', 0.5)
                random_event_chance = config.get('RANDOM_EVENT_CHANCE')
                next_track_wait = config.get('NEXT_TRACK_WAIT')
                color_table = config.get('COLOR_TABLE', {})
                return num_pixels, led_pin_name, brightness, random_event_chance, next_track_wait, color_table
        except json.JSONDecodeError:
            print("Error decoding config file.")
    print("Config file not found in $scriptRoot or $HOME/.config/trailpixel.")
    sys.exit(1)


# GLOBAL VARIABLES
NUM_PIXELS, LED_PIN_NAME, BRIGHTNESS, RANDOM_EVENT_CHANCE, NEXT_TRACK_WAIT, COLOR_TABLE = fetch_config()

try:
    import board
    import neopixel

    # Convert LED_PIN_NAME string from config to board attribute
    LED_PIN = getattr(board, LED_PIN_NAME)

    pixels = neopixel.NeoPixel(
        LED_PIN,
        NUM_PIXELS,
        brightness=BRIGHTNESS,
        auto_write=False)
except NotImplementedError:
    print("\033[93mWARNING: Neopixel library not supported on this platform. Using dummy classes.\033[0m")
    from debug import DummyBoard, DummyPixels
    board = DummyBoard()
    LED_PIN = getattr(board, LED_PIN_NAME)
    pixels = DummyPixels(LED_PIN, NUM_PIXELS,
                         brightness=BRIGHTNESS, auto_write=False)


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
            brightness = 0.2  # You can adjust this or fetch from config
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
        pixels.show()
        wait(0.05)
    pixels.fill((0, 0, 0))
    pixels.show()
    wait(3)
    return 0


# HELPER FUNCTIONS
def exit_gracefully():
    print("\nLEDs turned off. Goodbye!")
    pixels.fill((0, 0, 0))
    pixels.show()
    sys.exit(0)


def wait(time_in_seconds):
    try:
        time.sleep(time_in_seconds)
    except KeyboardInterrupt:
        exit_gracefully()
    except Exception as e:
        print(f"Error occurred while waiting: {e}")
    return 0


def get_color(name: str) -> Tuple[int, int, int, int]:
    # Default to off if not found
    return COLOR_TABLE.get(name, (0, 0, 0, 0))


def event_build_init(queue):
    # FIXME
    # This function would pick a random event from events.d folder
    for filename in os.listdir(os.path.join(SCRIPT_ROOT, "events.d")):
        if filename.endswith(".json"):
            with open(os.path.join(SCRIPT_ROOT, "events.d", filename), 'r') as f:
                event = json.load(f)
                EVENTS.append(event)
    if len(EVENTS) == 0:
        print("  No events found in events.d folder")
    queue.put(EVENTS)
    print(f"  {len(EVENTS)} events have been detectred and added")


def event_picker() -> dict:
    return EVENTS[random.randint(0, len(EVENTS) - 1)]


def event_runner(event) -> int:
    for e in event.get('events', []):
        # Blinking LED
        if e.get('blink', False):
            led_index = e.get('led')
            color_name = e.get('color')
            duration = e.get('duration')

            r, g, b, brightness = get_color(color_name)
            for _ in range(e.get('repeat', 1)):
                # Turn on LED
                pixels[led_index] = (int(r * brightness),
                                     int(g * brightness), int(b * brightness))
                pixels.show()
                wait(duration)

                # Turn off LED
                r, g, b, brightness = get_color("off")
                pixels[led_index] = (int(r * brightness),
                                     int(g * brightness), int(b * brightness))
                pixels.show()
                wait(duration)
            return 0
    return 2  # No action taken


def track_build_init(queue):
    # This function build all the tracks from json files from tracks.d folder
    for filename in os.listdir(os.path.join(SCRIPT_ROOT, "tracks.d")):
        if filename.endswith(".json"):
            with open(os.path.join(SCRIPT_ROOT, "tracks.d", filename), 'r') as f:
                track = json.load(f)
                TRACKS.append(track)
    if len(TRACKS) == 0:
        print("  No tracks found in tracks.d folder exiting")
        sys.exit(1)

    queue.put(TRACKS)
    print(f"  {len(TRACKS)} tracks have been detected and added")
    return 0


def track_pick_tracker() -> dict:
    return TRACKS[random.randint(0, len(TRACKS) - 1)]


def start_path_animation(track_led_path: list, track_led_indicator: int, track_speed: int) -> int:
    try:
        if not track_led_path:
            print("No LED path provided.")
            return 2  # No action taken

        # initialize path led path
        print(f"  Path:      {track_led_path}")
        print(f"  Indicator: {track_led_indicator}")
        print(f"  Speed:     {track_speed}")
        print(f"  ---")

        # turn on track indicator
        r, g, b, brightness = get_color("green")
        pixels[track_led_indicator] = (int(r * brightness),
                                       int(g * brightness), int(b * brightness))
        pixels.show()

        for i in track_led_path:
            r, g, b, brightness = get_color("white")
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
            pixels.show()
        wait(track_speed * 0.5)

        # animate path
        for idx, i in enumerate(track_led_path):
            r, g, b, brightness = get_color("red")
            print(
                f"  Traveling to LED {i} {f'disabling {track_led_path[idx - 1]}' if idx > 0 else ''}")
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
            pixels.show()

            # Turn off previous LED in path
            if idx > 0:
                prev = track_led_path[idx - 1]
                r_off, g_off, b_off, brightness_off = get_color("off")
                pixels[prev] = (int(r_off * brightness_off),
                                int(g_off * brightness_off), int(b_off * brightness_off))
                pixels.show()

            # add possible event
            if len(EVENTS) > 0:
                if (random.randint(0, 10) < RANDOM_EVENT_CHANCE):
                    print("    ---")
                    print("    Triggering random event")
                    event = event_picker()
                    print(f"    Event:     {event['name']} ({event['id']})")
                    print("    ---")
                    p = multiprocessing.Process(
                        target=event_runner, args=(event,))
                    p.start()
                    pixels.show()
            wait(track_speed)

        # turn off path
        print("  Track completed resetting")
        r, g, b, brightness = get_color("off")
        for i in track_led_path:
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
        pixels[track_led_indicator] = (int(r * brightness),
                                       int(g * brightness), int(b * brightness))
        pixels.show()
        wait(NEXT_TRACK_WAIT)
        return 0

    except KeyboardInterrupt:
        exit_gracefully()


def main():
    global TRACKS
    global EVENTS
    try:
        print("\033[1mStarting TrainPixels\033[0m")
        print(f"  Pixels: {NUM_PIXELS}")
        print(f"  Pin: {LED_PIN_NAME}")
        print("")

        # INIT (start both processes before boot animation)
        print("Initializing Tracks...")
        track_queue = multiprocessing.Queue()
        event_queue = multiprocessing.Queue()
        track_proc = multiprocessing.Process(
            target=track_build_init, args=(track_queue,))
        event_proc = multiprocessing.Process(
            target=event_build_init, args=(event_queue,))
        track_proc.start()
        event_proc.start()

        # Run boot animation
        led_boot_startup_sequence()

        # Wait for both processes to finish if not done
        if track_proc.is_alive():
            track_proc.join()
        if event_proc.is_alive():
            event_proc.join()

        if track_proc.exitcode != 0:
            print("Track process failed. Exiting.")
            sys.exit(1)
        if event_proc.exitcode != 0:
            print("Event process failed. Exiting.")
            sys.exit(1)

        TRACKS = track_queue.get()
        EVENTS = event_queue.get()

        print("Initialization complete.")

        print("\nStarting main track loop")
        # MAIN LOOP
        while True:
            wait(2)
            print("\nPicking track")
            track = track_pick_tracker()

            print(f"  Selected track: {track['name']} ({track['id']})")
            start_path_animation(
                track["led_path"], track["led_path_indicator"], track["speed"])

    except NotImplementedError:
        print("Functionality not yet implemented.")
    except KeyboardInterrupt:
        exit_gracefully()


if __name__ == "__main__":
    main()
