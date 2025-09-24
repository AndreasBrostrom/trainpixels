# TrainPixels LED Control System

## Overview
TrainPixels are a track simulation built with python to simulate a "Retro Swedish Trainway Tacking Wall" previously used by the Swedish Railway Institution; Banverket (today Trafikverket). The script uses NeoPixel (WS2812) LED strips and is built for a RaspberryPie. It also support local debugging without the hardware by using dummy functions.

## Configuration
Edit `config.json` to set:
- `NUM_PIXELS`: Number of LEDs
- `LED_PIN`: Pin name (e.g., "D19")
- `RANDOM_EVENT_CHANCE`: Probability for random event triggering
- `color_table`: Custom colors and brightness

Example:
```json
{
    "NUM_PIXELS": 10,
    "LED_PIN": "D19",
    "RANDOM_EVENT_CHANCE": 0.2,
    "color_table": {
        "red": [255, 0, 0, 0.3],
        "green": [0, 255, 0, 0.2],
        "white": [255, 255, 255, 0.2],
        "blue": [0, 0, 255, 0.5],
        "yellow": [255, 255, 0, 0.5],
        "purple": [128, 0, 128, 0.5],
        "off": [0, 0, 0, 0.5]
    }
}
```

## Track & Event Files
- Place track files in `src/tracks.d/` (see `track_01.json`, `track_02.json` for format)
- Place event files in `src/events.d/`

## Usage
1. run `start.sh` 

## Troubleshooting
- Ensure your config and track/event files are valid JSON
- If no tracks/events are found, the script will exit
- For hardware errors, check your wiring and pin settings

## License
MIT
