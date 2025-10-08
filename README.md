# TrainPixels LED Control System

## Overview
TrainPixels are a track simulation built with python to simulate a "Retro Swedish Trainway Tacking Wall" previously used by the Swedish Railway Institution; Banverket (today Trafikverket). The script uses NeoPixel (WS2812) LED strips and is built for a RaspberryPie. It also support local debugging without the hardware by using dummy functions.

## Configuration Examples
The configs are read from `$scriptRoot/src/` or `~/.config/trainpixels/`.

### config.json
```json
{
  "TRACK_PIXEL_LENGTH": 42,
  "UTIL_PIXEL_LENGTH": 44,
  "TRACK_PIN": "D19",
  "UTIL_PIN": "D21",
  "STATUS_UTIL_LED": 13,
  "BRIGHTNESS": 0.2,
  "TRACK_SPEED_MODIFIER": 0.2,
  "RANDOM_UTIL_TRIGGER_CHANCE": 0,
  "COLOR_TABLE": {
    "red": [255, 0, 0, 0.3],
    "green": [0, 255, 0, 0.2],
    "white": [255, 255, 255, 0.2],
    "blue": [0, 0, 255, 0.5],
    "yellow": [255, 255, 0, 0.5],
    "purple": [128, 0, 128, 0.5],
    "off": [0, 0, 0, 0.5],
    "status_indicator_green": [0, 255, 0, 0.1],
    "status_indicator_yellow": [255, 255, 0, 0.1],
    "status_indicator_red": [255, 0, 0, 0.1]
  }
}
```

### tracks.d/sandviken_1.json
```json 
{
  "id": "sandviken_1",
  "name": "Sandviken to Gävle",
  "track_path": [[34, ["track_arrow_26"]], 35, [36, "track_arrow_26_off"], 24, 18, 19],
  "speed": 1
}
```

### utils.d/track_arrow_26.json
```json 
{
  "id": "track_arrow_26",
  "name": "Util Lights - West > Arrow",
  "enabled_on_init": false,
  "is_random": false,
  "utils": [
    {
      "led": 26,
      "color": "white"
    }
  ]
}
```

## Track & Event Files
- Place track files in `src/tracks.d/` (see `track_01.json`, `track_02.json` for format)
- Supported `~/.config/trainpixels/tracks.d/` or `~/Desktop/tracks.d/`
- Place event files in `src/utils.d/`
- Supported `~/.config/trainpixels/utils.d/` or `~/Desktop/utils.d/`

## Usage
1. run `start.sh` 
 
## Systemd install & start example

If you want TrainPixels to run as a systemd service, copy the provided service file to the system directory, reload systemd and enable the service. Example commands (run on the target machine):

```bash
# Copy the service file (adjust path if you placed the repo elsewhere)
sudo cp utils/trainpixels.service /etc/systemd/system/trainpixels.service
sudo chmod 644 /etc/systemd/system/trainpixels.service

# Reload systemd to pick up the new unit
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable --now trainpixels.service

# View status and logs
sudo systemctl status trainpixels.service
journalctl -u trainpixels.service -f
```

## Troubleshooting
- Ensure your config and track/event files are valid JSON
- If no tracks/events are found, the script will exit
- For hardware errors, check your wiring and pin settings

## License
MIT
