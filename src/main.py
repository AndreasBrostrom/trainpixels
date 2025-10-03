#!/usr/bin/env python3
import os
import sys
import json
import time
import random
import multiprocessing
from typing import Tuple
from localtypes import ConfigType, TrackType, UtilsType


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

# Tracks
global TRACKS
TRACKS: list[TrackType] = []
# Utility Lights
global INIT_UTILS
INIT_UTILS: list[UtilsType] = []
global TRIGGER_UTILS
TRIGGER_UTILS: list[UtilsType] = []
global RANDOM_UTILS
RANDOM_UTILS: list[UtilsType] = []

# HANDLE CONFIG


def fetch_config() -> ConfigType:
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
                track_pixel_length = config.get("TRACK_PIXEL_LENGTH", 0)
                util_pixel_length = config.get("UTIL_PIXEL_LENGTH", 0)
                track_pin = config.get("TRACK_PIN", "")
                util_pin = config.get("UTIL_PIN", "")
                status_util_led = config.get("STATUS_UTIL_LED", 0)
                brightness = config.get("BRIGHTNESS", 0.2)
                track_speed_modifier = config.get("TRACK_SPEED_MODIFIER", 1.0)
                random_util_trigger_chance = config.get(
                    "RANDOM_UTIL_TRIGGER_CHANCE", 0)
                color_table = config.get("COLOR_TABLE", {})

                return ConfigType(
                    track_pixel_length=track_pixel_length,
                    util_pixel_length=util_pixel_length,
                    track_pin=track_pin,
                    util_pin=util_pin,
                    status_util_led=status_util_led,
                    brightness=brightness,
                    track_speed_modifier=track_speed_modifier,
                    random_util_trigger_chance=random_util_trigger_chance,
                    color_table=color_table
                )
        except json.JSONDecodeError:
            print("Error decoding config file.")
    print("Config file not found in ScriptRoot or ~/.config/trailpixel/.")
    sys.exit(1)


# GLOBAL VARIABLES
config = fetch_config()
TRACK_PIXEL_LENGTH = config["track_pixel_length"]
UTIL_PIXEL_LENGTH = config["util_pixel_length"]
TRACK_PIN = config["track_pin"]
UTIL_PIN = config["util_pin"]
STATUS_UTIL_LED = config.get("STATUS_UTIL_LED", 0)
BRIGHTNESS = config["brightness"]
TRACK_SPEED_MODIFIER = config["track_speed_modifier"]
RANDOM_UTIL_TRIGGER_CHANCE = config["random_util_trigger_chance"]
COLOR_TABLE = config["color_table"]


try:
    import board
    import neopixel

    if UTIL_PIN == 0 or TRACK_PIN == 0:
        print("Error: TRACK_PIN and UTIL_PIN must be set in config file.")
        sys.exit(1)
    if TRACK_PIXEL_LENGTH == 0 or UTIL_PIXEL_LENGTH == 0:
        print("Error: TRACK_PIXEL_LENGTH and UTIL_PIXEL_LENGTH must be set in config file.")
        sys.exit(1)

    # GLOBAL LED VARIABLES
    TRACK_PIN = getattr(board, TRACK_PIN)
    t_pixels = neopixel.NeoPixel(
        TRACK_PIN,
        TRACK_PIXEL_LENGTH,
        brightness=BRIGHTNESS,
        auto_write=False)

    UTIL_PIN = getattr(board, UTIL_PIN)
    u_pixels = neopixel.NeoPixel(
        UTIL_PIN,
        UTIL_PIXEL_LENGTH,
        brightness=BRIGHTNESS,
        auto_write=False)

except Exception as error:
    print("\033[93mWARNING: Neopixel library not supported on this platform. Using dummy classes.\033[0m")
    print(f"\033[93m         Error details: {error}\033[0m")
    from debug import DummyBoard, DummyPixels
    board = DummyBoard()

    TRACK_PIN = getattr(board, TRACK_PIN)
    t_pixels = DummyPixels(TRACK_PIN, TRACK_PIXEL_LENGTH,
                           brightness=BRIGHTNESS, auto_write=False)
    UTIL_PIN = getattr(board, UTIL_PIN)
    u_pixels = DummyPixels(UTIL_PIN, UTIL_PIXEL_LENGTH,
                           brightness=BRIGHTNESS, auto_write=False)


# FUNCTIONS
def boot_startup_sequence():
    global TRACKS
    global INIT_UTILS
    global TRIGGER_UTILS
    global RANDOM_UTILS

    set_u_led(STATUS_UTIL_LED, "status_indicator_loading", show=True)

    print("Initializing...")
    track_queue = multiprocessing.Queue()
    util_queue = multiprocessing.Queue()
    track_proc = multiprocessing.Process(
        target=track_build_init, args=(track_queue,))
    util_proc = multiprocessing.Process(
        target=util_build_init, args=(util_queue,))
    track_proc.start()
    util_proc.start()

    # Run boot animation until both processes are done
    boot_anim_frame = 0

    def wheel(pos):
        if pos < 85:
            return (int(pos * 3), int(255 - pos * 3), 0)
        elif pos < 170:
            pos -= 85
            return (int(255 - pos * 3), 0, int(pos * 3))
        else:
            pos -= 170
            return (0, int(pos * 3), int(255 - pos * 3))
    while track_proc.is_alive() or util_proc.is_alive():
        for i in range(TRACK_PIXEL_LENGTH):
            pixel_index = (i * 256 // TRACK_PIXEL_LENGTH) + boot_anim_frame * 8
            r, g, b = wheel(pixel_index & 255)
            brightness = 0.2
            t_pixels[i] = (int(r * brightness),
                           int(g * brightness), int(b * brightness))
        t_pixels.show()
        boot_anim_frame += 1
        wait(0.05)

    # Ensure both processes are joined
    track_proc.join()
    util_proc.join()

    if track_proc.exitcode != 0:
        print("Track process failed. Exiting.")
        sys.exit(1)
    if util_proc.exitcode != 0:
        print("Event process failed. Exiting.")
        sys.exit(1)

    TRACKS = track_queue.get()
    INIT_UTILS, TRIGGER_UTILS, RANDOM_UTILS = util_queue.get()  # Unpack the separated utils

    # Continue rainbow animation while processing is finishing
    print("  Processing complete...")
    for _ in range(20):  # A few more rainbow cycles
        for i in range(TRACK_PIXEL_LENGTH):
            pixel_index = (i * 256 // TRACK_PIXEL_LENGTH) + boot_anim_frame * 8
            r, g, b = wheel(pixel_index & 255)
            brightness = 0.2
            t_pixels[i] = (int(r * brightness),
                           int(g * brightness), int(b * brightness))
        t_pixels.show()
        boot_anim_frame += 1
        wait(0.05)

    # Turn off LEDs after boot animation
    t_pixels.fill((0, 0, 0))
    t_pixels.show()
    wait(1)

    print("Initialization complete.")
    return 0


def set_t_led(led_index: int, color_name: str, show: bool = False) -> int:
    try:
        r, g, b, brightness = get_color(color_name)

        t_pixels[led_index] = (int(r * brightness),
                               int(g * brightness), int(b * brightness))
        if show:
            t_pixels.show()
        return 0
    except Exception as e:
        print(f"Error setting T LED {led_index}: {e}")
        return 1


def set_u_led(led_index: int, color_name: str, show: bool = False) -> int:
    try:
        r, g, b, brightness = get_color(color_name)

        u_pixels[led_index] = (int(r * brightness),
                               int(g * brightness), int(b * brightness))
        if show:
            u_pixels.show()
        return 0
    except Exception as e:
        print(f"Error setting U LED {led_index}: {e}")
        return 1


# HELPER FUNCTIONS
def execute_init_utils():
    """
    Execute all initialization events (separate from boot sequence)
    """
    global INIT_UTILS

    if len(INIT_UTILS) > 0:
        print(f"Executing {len(INIT_UTILS)} initialization events...")
        for init_event in INIT_UTILS:
            print(
                f"  Executing: {init_event.get('name', init_event.get('id', 'unnamed'))}")
            run_util_by_id(init_event.get('id'))
        print("Initialization events completed.")
    else:
        print("No initialization events to execute.")


def exit_gracefully():
    print("\nLEDs turned off. Goodbye!")
    t_pixels.fill((0, 0, 0))
    t_pixels.show()
    u_pixels.fill((0, 0, 0))
    u_pixels.show()
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


def util_build_init(queue) -> None:
    try:
        all_utils = []
        # First, load all utils
        for filename in os.listdir(os.path.join(SCRIPT_ROOT, "utils.d")):
            if filename.endswith(".json"):
                with open(os.path.join(SCRIPT_ROOT, "utils.d", filename), 'r') as f:
                    util = json.load(f)
                    all_utils.append(util)

        if len(all_utils) == 0:
            print("  No utils found in utils.d folder")
            queue.put(([], [], []))  # Return empty lists for all three categories
            return

        print(f"  {len(all_utils)} total utility's loaded")

        # Now separate them
        init_utils = []
        trigger_utils = []
        random_utils = []

        for util in all_utils:
            # Check if this is an initialization event
            if util.get('enabled_on_init', False):
                init_utils.append(util)
                print(
                    f"    -> Found Init utils: {util.get('name', util.get('id', 'unnamed'))} [{util.get('id', 'noid')}]")
                continue

            # Check if this should be in random events (exclude if is_random=false)
            if util.get('is_random', False) and not util.get('enabled_on_init', False):  # Default to True for backward compatibility
                random_utils.append(util)
                print(
                    f"    -> Found Random utils: {util.get('name', util.get('id', 'unnamed'))} [{util.get('id', 'noid')}]")
                continue

            if not util.get('is_random', False) and not util.get('enabled_on_init', False):
                trigger_utils.append(util)
                print(
                    f"    -> Found Trigger utils: {util.get('name', util.get('id', 'unnamed'))} [{util.get('id', 'noid')}]")
                continue

            print(
                f"    -> Found Unknown utils: {util.get('name', util.get('id', 'unnamed'))} [{util.get('id', 'noid')}]")

        print(f"  {len(init_utils)} initialization utils processed")
        print(f"  {len(trigger_utils)} trigger utils processed")
        print(f"  {len(random_utils)} random utils processed")

        # Return both lists as a tuple
        queue.put((init_utils, trigger_utils, random_utils))

    except Exception as e:
        print(f"Error loading utils: {e}")
        queue.put(([], [], []))  # Return empty lists for all three categories on error


def get_util_from_id(id: str) -> UtilsType | None:
    for util in INIT_UTILS + TRIGGER_UTILS + RANDOM_UTILS:
        if util.get('id') == id:
            return util
    return None


def get_random_util() -> UtilsType:
    return RANDOM_UTILS[random.randint(0, len(RANDOM_UTILS) - 1)]


def run_util_by_id(util_id: str) -> int:
    """Run a utility by its ID"""
    if not util_id:
        return 2  # No action taken

    # Find the utility by ID
    util_obj = get_util_from_id(util_id)
    if not util_obj:
        print(f"    Warning: Utility '{util_id}' not found")
        return 1  # Error

    print(f"    -> Triggering util: {util_obj.get('name', util_id)} [{util_id}]")

    # Execute the utility actions
    actions_executed = 0
    for action in util_obj.get('utils', []):
        led_index = action.get('led')
        color_name = action.get('color')

        if led_index is None or color_name is None:
            print(f"      Warning: Action missing 'led' or 'color' property")
            continue

        # Handle blinking LEDs
        if action.get('blink', False):
            duration = action.get('duration', 0.5)
            repeat = action.get('repeat', 1)

            for _ in range(repeat):
                set_u_led(led_index, color_name, show=True)
                wait(duration)
                set_u_led(led_index, "off", show=True)
                wait(duration)
            actions_executed += 1
        else:
            # Static LED setting
            set_u_led(led_index, color_name, show=True)
            actions_executed += 1

    return 0 if actions_executed > 0 else 2


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


def get_track_by_id(track_id: str) -> TrackType | None:
    for track in TRACKS:
        if track.get('id') == track_id:
            return track
    return None


def get_random_track() -> TrackType:
    return TRACKS[random.randint(0, len(TRACKS) - 1)]


def get_track_path(track_path: list) -> list:
    """Extract only the LED positions from track path, excluding utils"""
    positions = []
    for step in track_path:
        if isinstance(step, list) and len(step) > 0:
            positions.append(step[0])
        else:
            positions.append(step)
    return positions


def count_track_utils(track_path: list) -> int:
    """Count the total number of utils that will be triggered in a track"""
    total_utils = 0
    for step in track_path:
        if isinstance(step, list) and len(step) > 1:
            # Second element contains utils list
            utils = step[1] if len(step) > 1 else []
            if isinstance(utils, list):
                total_utils += len(utils)
            elif utils:  # Single util (not a list)
                total_utils += 1
    return total_utils


def start_screen_animation() -> int:
    try:
        print("\n\033[1mPicking track\033[0m")

        # track_config = get_random_track()
        track_config = get_track_by_id("passthrue_1")
        if not track_config:
            print(f"  \033[31mERROR: Track 'passthrue_1' not found\033[0m")
            return 1

        print(
            f"  Selected track: {track_config.get('name', 'Unknown')} ({track_config.get('id', 'Unknown')})")

        # Initialize path led path
        track_path = track_config.get('track_path', [])
        track_positions = get_track_path(track_path)
        utils_count = count_track_utils(track_path)

        print(f"  Path:      {track_positions}")
        print(f"  Utils:     {utils_count} util(s) will be triggered")
        print(f"  Speed:     {track_config.get('speed', 1)} x {TRACK_SPEED_MODIFIER} modifier")
        print(f"  ---")

        # Enabling track
        for i in track_config.get('track_path', []):
            track = -1

            if isinstance(i, list) and len(i) > 0:
                track = i[0]
            else:
                track = i

            if track != -1:
                print(f"  Enabling track LED {track}")

        t_pixels.show()

        # Travel the track
        for i in track_config['track_path']:
            track = -1

            if isinstance(i, list) and len(i) > 0:
                track = i[0]
                util = i[1] if len(i) > 1 else None
            else:
                track = i
                util = None

            # Trigger any utils for this step
            if track != -1:
                print(f"  Traveling to track LED {track}")
                set_t_led(track, "red", show=True)
            else:
                print(f"  Traveling is paused and waiting {track}")

            # Trigger any utils for this step
            if util:
                if isinstance(util, list):
                    # Multiple utils
                    for util_id in util:
                        if util_id:  # Skip empty strings
                            run_util_by_id(util_id)
                else:
                    # Single util
                    run_util_by_id(util)

            wait(10 * TRACK_SPEED_MODIFIER)

            # Turn off previous LED (simulate movement)
            if track != -1:
                set_t_led(track, "off", show=True)

    except KeyboardInterrupt:
        exit_gracefully()
    except Exception as e:
        print(f"  \033[31mERROR: main track loop: {e}\033[0m")

    return 0


def main():
    try:
        print("\033[1mStarting TrainPixels\033[0m")
        print(
            f"  Pixels: {TRACK_PIXEL_LENGTH} on track, {UTIL_PIXEL_LENGTH} on utils")
        print(f"  Pin:    {TRACK_PIN} on track, {UTIL_PIN} on utils")
        print("")

        boot_startup_sequence()

        # Execute initialization utilities after boot sequence
        execute_init_utils()

        # Trigger status utility light
        set_u_led(STATUS_UTIL_LED, "status_indicator_green", show=True)

        # MAIN LOOP
        print("\nStarting main track loop")
        while True:
            start_screen_animation()

    except NotImplementedError:
        print("Functionality not yet implemented.")
    except KeyboardInterrupt:
        exit_gracefully()


if __name__ == "__main__":
    main()
