# TrainPixels LED Control System

## Overview

TrainPixels are a track simulation built with python to simulate a "Retro Swedish Trainway Tacking Wall" previously used by the Swedish Railway Institution; Banverket (today Trafikverket). The script uses NeoPixel (WS2812) LED strips and is built for a RaspberryPie. It also support local debugging without the hardware by using dummy functions.

## Configuration

Example:

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

## Track & Event Files

- Place track files in `src/tracks.d/` (see `track_01.json`, `track_02.json` for format)
- Supported `~/.config/trainpixels/tracks.d/` or `~/Desktop/tracks.d/`
- Place event files in `src/utils.d/`
- Supported `~/.config/trainpixels/utils.d/` or `~/Desktop/utils.d/`

## Usage

1. run `start.sh`

## Control Center

TrainPixels includes a control center that can manage services via numpad input. The control center reads numpad key presses and executes corresponding actions.

### Control Center Key Commands

- `*` - Restart all services
- `1` - Start trainpixels-main service
- `2` - Start trainpixels-controller service
- `3` - Stop all services
- `** start` - Reboot the system

### Running the Control Center

```bash
# Start the control center (requires root for service management)
sudo ./start-controlcenter.sh

# Or as a systemd service
sudo systemctl start trainpixels-controlcenter
```

## Service Management

TrainPixels can be managed as systemd services using the master service:

```bash
# Start all services in proper order
sudo systemctl start trainpixels

# Stop all services
sudo systemctl stop trainpixels

# Restart all services
sudo systemctl restart trainpixels

# Enable auto-start at boot
sudo systemctl enable trainpixels

# Check status
sudo systemctl status trainpixels

# Follow logs
sudo journalctl -u trainpixels -f
```

### Creating Service Files

Use the build script to generate systemd service files:

```bash
# Create all service files
./scripts/buildservices.sh

# Create only specific services
./scripts/buildservices.sh controller
./scripts/buildservices.sh main
./scripts/buildservices.sh controlcenter
./scripts/buildservices.sh master
```

## Troubleshooting

- Ensure your config and track/event files are valid JSON
- If no tracks/events are found, the script will exit
- For hardware errors, check your wiring and pin settings

## License

MIT
