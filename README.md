# LED Rainbow Control Script

This project controls a WS2812/WS2811 LED strip to display beautiful rainbow colors across 10 pixels.

## Hardware Requirements

- **Raspberry Pi** (or compatible single-board computer)
- **WS2812/WS2811 LED strip** (or compatible addressable LED strip)
- **Power supply** (5V, adequate amperage for your LED count)
- **Resistor** (330-470 ohm, recommended for data line protection)
- **Jumper wires** for connections

## Wiring

Connect your LED strip to the Raspberry Pi:

```
LED Strip    Raspberry Pi
VCC (5V)  -> 5V (Pin 2 or 4)
GND       -> GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
DIN       -> GPIO 18 (Pin 12) - through 330-470Ω resistor
```

**Important**: Make sure to use a proper 5V power supply for the LED strip if you have more than a few LEDs, as the Raspberry Pi's 5V pin has limited current capacity.

## Software Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Enable SPI** (required for CircuitPython libraries):
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options -> SPI -> Enable
   ```

3. **Run the script**:
   ```bash
   python src/main.py
   ```

## Usage

The script automatically starts the animated rainbow cycle when run. It will:

- Display configuration information (number of pixels, GPIO pin, brightness)
- Immediately begin the rainbow animation across all 10 LEDs
- Continue running until you press **Ctrl+C** to stop
- Automatically turn off all LEDs when exiting

## Configuration

You can modify these settings in `src/main.py`:

- `NUM_PIXELS`: Number of LEDs in your strip (default: 10)
- `LED_PIN`: GPIO pin connected to LED strip (default: board.D18/GPIO 18)
- `BRIGHTNESS`: LED brightness from 0.0 to 1.0 (default: 0.3)
- `UPDATE_DELAY`: Animation speed in seconds (default: 0.05)

## Troubleshooting

### Import Errors
If you get import errors for `board` or `neopixel`, make sure you've installed the requirements:
```bash
pip install adafruit-circuitpython-neopixel adafruit-blinka
```

### Permission Issues
If you get permission errors, you might need to run with sudo:
```bash
sudo python src/main.py
```

### LEDs Not Working
1. Check your wiring connections
2. Verify your power supply is adequate
3. Make sure SPI is enabled in raspi-config
4. Try a different GPIO pin and update `LED_PIN` in the code

### Alternative Library
If the CircuitPython libraries don't work, you can use the `rpi_ws281x` library instead. Uncomment the alternative line in `requirements.txt` and modify the imports in the script.

## Safety Notes

- Always disconnect power when making wiring changes
- Use appropriate resistors to protect the data line
- Ensure your power supply can handle the current requirements of your LED strip
- Be mindful of LED brightness to avoid eye strain