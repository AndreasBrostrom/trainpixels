#!/usr/bin/env python3
import os
import sys
import json
import time
import random
import multiprocessing
from typing import Tuple
from localtypes import ConfigType, TrackType, EventType


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
TRACKS: list[TrackType] = []
global EVENTS
EVENTS: list[EventType] = []
global INIT_EVENTS
INIT_EVENTS: list[EventType] = []

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
                track_speed_modifier = config.get('TRACK_SPEED_MODIFIER', 1.0)
                num_pixels = config.get('NUM_PIXELS')
                led_pin_name = config.get('LED_PIN', 'D21')
                brightness = config.get('BRIGHTNESS', 0.5)
                random_event_chance = config.get('RANDOM_EVENT_CHANCE')
                next_track_wait = config.get('NEXT_TRACK_WAIT')
                color_table = config.get('COLOR_TABLE', {})
                return ConfigType(
                    track_speed_modifier=track_speed_modifier,
                    num_pixels=num_pixels,
                    led_pin_name=led_pin_name,
                    brightness=brightness,
                    random_event_chance=random_event_chance,
                    next_track_wait=next_track_wait,
                    color_table=color_table
                )
        except json.JSONDecodeError:
            print("Error decoding config file.")
    print("Config file not found in ScriptRoot or ~/.config/trailpixel/.")
    sys.exit(1)

# GLOBAL VARIABLES
config = fetch_config()
TRACK_SPEED_MODIFIER = config['track_speed_modifier']
NUM_PIXELS = config['num_pixels']
LED_PIN_NAME = config['led_pin_name']
BRIGHTNESS = config['brightness']
RANDOM_EVENT_CHANCE = config['random_event_chance']
NEXT_TRACK_WAIT = config['next_track_wait']
COLOR_TABLE = config['color_table']

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
except:
    print("\033[93mWARNING: Neopixel library not supported on this platform. Using dummy classes.\033[0m")
    from debug import DummyBoard, DummyPixels
    board = DummyBoard()
    LED_PIN = getattr(board, LED_PIN_NAME)
    pixels = DummyPixels(LED_PIN, NUM_PIXELS,
                         brightness=BRIGHTNESS, auto_write=False)


# FUNCTIONS
def boot_startup_sequence():
    global TRACKS
    global EVENTS
    global INIT_EVENTS
    print("Initializing...")
    track_queue = multiprocessing.Queue()
    event_queue = multiprocessing.Queue()
    track_proc = multiprocessing.Process(
        target=track_build_init, args=(track_queue,))
    event_proc = multiprocessing.Process(
        target=event_build_init, args=(event_queue,))
    track_proc.start()
    event_proc.start()

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
    while track_proc.is_alive() or event_proc.is_alive():
        for i in range(NUM_PIXELS):
            pixel_index = (i * 256 // NUM_PIXELS) + boot_anim_frame * 8
            r, g, b = wheel(pixel_index & 255)
            brightness = 0.2
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
        pixels.show()
        boot_anim_frame += 1
        wait(0.05)
    # Ensure both processes are joined
    track_proc.join()
    event_proc.join()

    if track_proc.exitcode != 0:
        print("Track process failed. Exiting.")
        sys.exit(1)
    if event_proc.exitcode != 0:
        print("Event process failed. Exiting.")
        sys.exit(1)

    TRACKS = track_queue.get()
    INIT_EVENTS, EVENTS = event_queue.get()  # Unpack the separated events

    # Continue rainbow animation while processing is finishing
    print("Processing complete, finishing rainbow animation...")
    for _ in range(20):  # A few more rainbow cycles
        for i in range(NUM_PIXELS):
            pixel_index = (i * 256 // NUM_PIXELS) + boot_anim_frame * 8
            r, g, b = wheel(pixel_index & 255)
            brightness = 0.2
            pixels[i] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
        pixels.show()
        boot_anim_frame += 1
        wait(0.05)

    # Turn off LEDs after boot animation
    pixels.fill((0, 0, 0))
    pixels.show()
    wait(1)
    
    print("Initialization complete.")
    return 0


# HELPER FUNCTIONS
def execute_init_events():
    """
    Execute all initialization events (separate from boot sequence)
    """
    global INIT_EVENTS
    
    if len(INIT_EVENTS) > 0:
        print(f"Executing {len(INIT_EVENTS)} initialization events...")
        for init_event in INIT_EVENTS:
            print(f"  Executing: {init_event.get('name', init_event.get('id', 'unnamed'))}")
            event_runner(init_event)
        print("Initialization events completed.")
    else:
        print("No initialization events to execute.")


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

def set_led_light(led_index: int, color_name: str, show: bool = False) -> int:
    r, g, b, brightness = get_color(color_name)
    pixels[led_index] = (int(r * brightness),
                         int(g * brightness), int(b * brightness))
    if show:
        pixels.show()
    return 0


def event_build_init(queue):
    """
    Load all events from events.d folder, then separate them into:
    - INIT_EVENTS: events with enabled_on_init=true
    - EVENTS: events with is_random=true (excluding those with is_random=false)
    """
    all_events = []
    
    # First, load all events
    for filename in os.listdir(os.path.join(SCRIPT_ROOT, "events.d")):
        if filename.endswith(".json"):
            with open(os.path.join(SCRIPT_ROOT, "events.d", filename), 'r') as f:
                event = json.load(f)
                all_events.append(event)
    
    if len(all_events) == 0:
        print("  No events found in events.d folder")
        queue.put(([], []))  # Return empty lists for both
        return
    
    print(f"  {len(all_events)} total events loaded")
    
    # Now separate them
    init_events = []
    random_events = []
    
    for event in all_events:
        # Check if this is an initialization event
        if event.get('enabled_on_init', False):
            init_events.append(event)
            print(f"    -> Init event: {event.get('name', event.get('id', 'unnamed'))}")
        
        # Check if this should be in random events (exclude if is_random=false)
        if event.get('is_random', True):  # Default to True for backward compatibility
            random_events.append(event)
            print(f"    -> Random event: {event.get('name', event.get('id', 'unnamed'))}")
        else:
            print(f"    -> Excluded from random: {event.get('name', event.get('id', 'unnamed'))} (is_random=false)")
    
    print(f"  {len(init_events)} initialization events processed")
    print(f"  {len(random_events)} random events processed")
    
    # Return both lists as a tuple
    queue.put((init_events, random_events))


def event_picker() -> dict:
    return EVENTS[random.randint(0, len(EVENTS) - 1)]


def event_runner(event) -> int:
    """
    Execute an event's actions
    Supports both blinking LEDs and static LED setting
    """
    actions_executed = 0
    
    for e in event.get('events', []):
        led_index = e.get('led')
        color_name = e.get('color')
        
        if led_index is None or color_name is None:
            print(f"    Warning: Event missing 'led' or 'color' property")
            continue
            
        # Blinking LED
        if e.get('blink', False):
            duration = e.get('duration', 0.5)  # Default blink duration
            r, g, b, brightness = get_color(color_name)
            
            for _ in range(e.get('repeat', 1)):
                # Turn on LED
                pixels[led_index] = (int(r * brightness),
                                     int(g * brightness), int(b * brightness))
                pixels.show()
                wait(duration)

                # Turn off LED
                r_off, g_off, b_off, brightness_off = get_color("off")
                pixels[led_index] = (int(r_off * brightness_off),
                                     int(g_off * brightness_off), int(b_off * brightness_off))
                pixels.show()
                wait(duration)
            actions_executed += 1
            
        else:
            # Static LED setting (for initialization events)
            r, g, b, brightness = get_color(color_name)
            pixels[led_index] = (int(r * brightness),
                                 int(g * brightness), int(b * brightness))
            actions_executed += 1
    
    # Show all changes at once for static events
    if actions_executed > 0:
        pixels.show()
    
    return 0 if actions_executed > 0 else 2  # 0 = success, 2 = no action taken


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

def start_screen_animation() -> int:
    try:
        print("\n\033[1mPicking track\033[0m")
        track_config = track_pick_tracker()
        print(f"  Selected track: {track_config['name']} ({track_config['id']})")

        # Initialize path led path
        print(f"  Path:      {track_config['track_path']}")
        print(f"  Speed:     {track_config['speed']} x {TRACK_SPEED_MODIFIER} modifier")
        print(f"  ---")
        
        # Enabling track
        for i in track_config['track_path']:
            track = -1
            
            if isinstance(i, list) and len(i) > 0:
                track = i[0]
            else:
                track = i 
    
            if track != -1:
                print(f"  Enabling track LED {track}")
                set_led_light(track, "white")
        pixels.show()
    
        
    except KeyboardInterrupt:
        exit_gracefully()
        
        #if not track_led_path:
        #    print("No LED path provided.")
        #    return 2  # No action taken
#
        ## initialize path led path
        #print(f"  Path:      {track_led_path}")
        #print(f"  Speed:     {track_speed}")
        #print(f"  ---")
#
        #for i in track_led_path:
        #    r, g, b, brightness = get_color("white")
        #    pixels[i] = (int(r * brightness),
        #                 int(g * brightness), int(b * brightness))
        #    pixels.show()
        #wait(track_speed * 0.5)
#
        ## animate path
        #for idx, i in enumerate(track_led_path):
        #    r, g, b, brightness = get_color("red")
        #    print(
        #        f"  Traveling to LED {i} {f'disabling {track_led_path[idx - 1]}' if idx > 0 else ''}")
        #    pixels[i] = (int(r * brightness),
        #                 int(g * brightness), int(b * brightness))
        #    pixels.show()
#
        #    # Turn off previous LED in path
        #    if idx > 0:
        #        prev = track_led_path[idx - 1]
        #        r_off, g_off, b_off, brightness_off = get_color("off")
        #        pixels[prev] = (int(r_off * brightness_off),
        #                        int(g_off * brightness_off), int(b_off * brightness_off))
        #        pixels.show()
#
        #    # Temporarily disabled
        #    # add possible event
        #    # if len(EVENTS) > 0:
        #    #    if (random.randint(0, 10) < RANDOM_EVENT_CHANCE):
        #    #        print("    ---")
        #    #        print("    Triggering random event")
        #    #        event = event_picker()
        #    #        print(f"    Event:     {event['name']} ({event['id']})")
        #    #        print("    ---")
        #    #        p = multiprocessing.Process(
        #    #            target=event_runner, args=(event,))
        #    #        p.start()
        #    #        pixels.show()
        #    # wait(track_speed)
#
        ## turn off path
        #print("  Track completed resetting")
        #r, g, b, brightness = get_color("off")
        #for i in track_led_path:
        #    pixels[i] = (int(r * brightness),
        #                 int(g * brightness), int(b * brightness))
        #pixels.show()
        #wait(NEXT_TRACK_WAIT)
        #return 0

    except KeyboardInterrupt:
        exit_gracefully()

    return 0


def main():
    try:
        print("\033[1mStarting TrainPixels\033[0m")
        print(f"  Pixels: {NUM_PIXELS}")
        print(f"  Pin:    {LED_PIN_NAME}")
        print("")

        boot_startup_sequence()

        # Execute initialization events after boot sequence
        execute_init_events()

        # MAIN LOOP
        print("\nStarting main track loop")
        while True:
            start_screen_animation()
            wait(1 * TRACK_SPEED_MODIFIER)

    except NotImplementedError:
        print("Functionality not yet implemented.")
    except KeyboardInterrupt:
        exit_gracefully()


if __name__ == "__main__":
    main()
