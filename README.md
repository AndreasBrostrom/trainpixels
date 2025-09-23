# Multi-LED Rainbow Controller

This project supports multiple types of LED strips and displays beautiful rainbow colors with smooth animations. Now supports **WS2812/WS2811 (NeoPixel)**, **APA102/SK9822 (DotStar)**, **WS2801**, and **PWM RGB** LEDs!

## ✨ Features

- **Multiple LED Types**: Supports 4 different LED strip/module types
- **Automatic Connection Testing**: Built-in connection verification
- **Easy Configuration**: Simple LED type switching
- **Rainbow Animations**: Smooth, colorful animations
- **Error Handling**: Helpful error messages and troubleshooting

## 🔧 Supported Hardware

### LED Types
1. **WS2812/WS2811 (NeoPixel)** - Most common addressable LEDs
2. **APA102/SK9822 (DotStar)** - High-speed LEDs with separate clock
3. **WS2801** - Older addressable LEDs with clock line
4. **PWM RGB** - Individual RGB LEDs or modules

### Requirements
- **Raspberry Pi** (or compatible single-board computer)  
- **LED strip/module** (any of the supported types above)
- **Power supply** (5V, adequate for your LED count)
- **Resistors** (330-470Ω recommended for data line protection)
- **Jumper wires** for connections

## 🚀 Quick Start

1. **Identify your LED type** (check markings on your LED strip/module)
2. **Edit configuration** in `src/main.py`:
   ```python
   LED_TYPE = "NEOPIXEL"  # Change to: NEOPIXEL, DOTSTAR, WS2801, or PWM
   NUM_PIXELS = 10        # Set your LED count
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the controller**:
   ```bash
   python src/main.py
   ```

## 📋 Wiring Guide

### WS2812/WS2811 (NeoPixel) - Default
```
LED Strip    Raspberry Pi
VCC (5V)  -> 5V (Pin 2 or 4)
GND       -> GND (Pin 6)
Data      -> GPIO 18 (Pin 12) + 330Ω resistor
```

### APA102/SK9822 (DotStar)
```
LED Strip    Raspberry Pi  
VCC (5V)  -> 5V (Pin 2 or 4)
GND       -> GND (Pin 6)
Data      -> GPIO 10 (Pin 19) - MOSI
Clock     -> GPIO 11 (Pin 23) - SCLK
```

### WS2801
```
LED Strip    Raspberry Pi
VCC (5V)  -> 5V (Pin 2 or 4)  
GND       -> GND (Pin 6)
Data      -> GPIO 10 (Pin 19) - MOSI
Clock     -> GPIO 11 (Pin 23) - SCLK
```

### PWM RGB LED
```
RGB LED      Raspberry Pi
VCC       -> 3.3V (Pin 1) or 5V (Pin 2)
Red       -> GPIO 18 (Pin 12)
Green     -> GPIO 19 (Pin 35)  
Blue      -> GPIO 20 (Pin 38)
GND       -> GND (Pin 6)
```

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AndreasBrostrom/trainpixels.git
   cd trainpixels
   ```

2. **Install dependencies**:
   ```bash
   # Install all LED libraries (recommended):
   pip install -r requirements.txt
   
   # Or install only what you need:
   pip install adafruit-blinka  # Required for all
   pip install adafruit-circuitpython-neopixel    # For WS2812/WS2811
   pip install adafruit-circuitpython-dotstar     # For APA102/SK9822  
   pip install adafruit-circuitpython-ws2801      # For WS2801
   pip install adafruit-circuitpython-pwmio       # For PWM RGB
   ```

3. **Enable SPI** (required for DotStar/WS2801):
   ```bash
   sudo raspi-config
   # Interface Options -> SPI -> Enable
   ```

4. **Configure your LED type** in `src/main.py`

## 🎮 Usage

The script now includes automatic connection testing and better error handling:

```bash
python src/main.py
# or if permissions needed:
sudo python src/main.py
```

**What happens:**
1. **Configuration display** - Shows your LED type and settings
2. **Connection test** - Tests Red, Green, Blue, and White colors
3. **Rainbow animation** - Starts the smooth rainbow cycle
4. **Clean exit** - Press Ctrl+C to stop and turn off LEDs

## ⚙️ Configuration

Edit these settings in `src/main.py`:

```python
LED_TYPE = "NEOPIXEL"    # LED type: NEOPIXEL, DOTSTAR, WS2801, PWM
NUM_PIXELS = 10          # Number of LEDs (ignored for PWM type)
BRIGHTNESS = 1.0         # Brightness: 0.0 to 1.0
UPDATE_DELAY = 0.05      # Animation speed in seconds
```

### Pin Configuration
Customize GPIO pins in the `PIN_CONFIGS` dictionary:
```python
PIN_CONFIGS = {
    "NEOPIXEL": {"data_pin": board.D18},
    "DOTSTAR": {"data_pin": board.D10, "clock_pin": board.D11},
    # ... etc
}
```

## 🔧 Troubleshooting

### Connection Issues
The program now includes built-in diagnostics! If LEDs don't work:

1. **Check the connection test output** - it will test each color
2. **Verify your LED type configuration** matches your hardware
3. **Review the wiring** using the diagrams above
4. **Try running with sudo** for GPIO permissions

### Common Problems

| Problem | Solution |
|---------|----------|
| Import errors | Install required libraries: `pip install -r requirements.txt` |
| Permission denied | Run with `sudo python src/main.py` |
| No LEDs light up | Check LED type, wiring, and power supply |
| Wrong colors | Verify voltage levels and connections |
| Only some LEDs work | Check power supply capacity |

### Detailed Help
See **[LED_SETUP_GUIDE.md](LED_SETUP_GUIDE.md)** for comprehensive troubleshooting, including:
- Hardware specifications for each LED type
- Advanced troubleshooting steps
- Performance optimization tips
- Custom pin configurations

## 🛡️ Safety Notes

- **Power off** when making wiring changes
- **Use resistors** (330-470Ω) to protect data lines  
- **Check power requirements** - LED strips can draw significant current
- **Use proper voltage levels** - 5V LEDs may need level shifters with 3.3V controllers
- **Avoid looking directly** at bright LEDs

## 📚 Learn More

- **Hardware specs**: Check [LED_SETUP_GUIDE.md](LED_SETUP_GUIDE.md)
- **Adafruit CircuitPython**: [Official documentation](https://circuitpython.org/)
- **GPIO pinout**: [pinout.xyz](https://pinout.xyz/)