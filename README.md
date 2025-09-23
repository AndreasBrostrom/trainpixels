# WS2812B LED White Blink Controller

A simple Python script to control WS2812B LED strips, blinking all LEDs with white light. Perfect for testing your WS2812B LED setup!

## ✨ Features

- **Simple white blinking** - All LEDs blink white on/off
- **WS2812B optimized** - Specifically designed for WS2812B LEDs
- **Easy to use** - Just run and watch your LEDs blink
- **Safe exit** - Automatically turns off LEDs when stopped
- **Configurable** - Adjust LED count, brightness, and timing

## 🔧 Hardware Requirements

- **Raspberry Pi** (or compatible single-board computer)
- **WS2812B LED strip** (addressable RGB LEDs)
- **Power supply** (5V, adequate for your LED count)
- **Resistor** (330-470Ω recommended for data line protection)
- **Jumper wires** for connections

## 🚀 Quick Start

1. **Connect your WS2812B LEDs** to GPIO 18 (see wiring below)
2. **Adjust LED count** in `src/main.py` if needed:
   ```python
   NUM_PIXELS = 10        # Set to your actual LED count
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the blink script**:
   ```bash
   python src/main.py
   # or with sudo if needed:
   sudo python src/main.py
   ```

## 📋 Wiring Guide

### WS2812B LED Strip Connection
```
WS2812B Strip    Raspberry Pi
VCC (5V)      -> 5V (Physical Pin 2 or 4)
GND           -> GND (Physical Pin 6)
Data (DIN)    -> GPIO 18 (Physical Pin 12) + 330Ω resistor
```

**Important Notes:**
- Use a 330-470Ω resistor between GPIO 18 and the data line
- For more than 10 LEDs, use an external 5V power supply
- Connect all grounds together (Pi GND, LED GND, Power GND)

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AndreasBrostrom/trainpixels.git
   cd trainpixels
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your setup** (optional):
   - Edit `NUM_PIXELS` in `src/main.py` to match your LED count
   - Adjust `BRIGHTNESS` (0.1 to 1.0) for desired brightness

## 🎮 Usage

Simple white blinking operation:

```bash
python src/main.py
# or if permissions needed:
sudo python src/main.py
```

**What happens:**
1. **All LEDs turn white** for 1 second
2. **All LEDs turn off** for 1 second  
3. **Repeats continuously** until you press Ctrl+C
4. **Clean exit** - Automatically turns off all LEDs when stopped

**Terminal output:**
```
WS2812B White Blink - Press Ctrl+C to stop
ON
OFF
ON
OFF
...
```

## ⚙️ Configuration

Edit these settings in `src/main.py`:

```python
NUM_PIXELS = 10          # Number of LEDs in your strip
LED_PIN = board.D18      # GPIO 18 (Physical Pin 12)
BRIGHTNESS = 0.5         # Brightness: 0.1 (dim) to 1.0 (full)
```

**Timing adjustment:**
```python
time.sleep(1)            # Change to 0.5 for faster, 2 for slower blinking
```

## 🔧 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Import errors | Install libraries: `pip install -r requirements.txt` |
| Permission denied | Run with `sudo python src/main.py` |
| No LEDs light up | Check wiring, power supply, and LED count |
| LEDs stay dim | Increase `BRIGHTNESS` value (up to 1.0) |
| Only first LED works | Check data line connection and LED strip continuity |

### Quick Fixes
1. **Check wiring** - Ensure GPIO 18 connects to DIN with resistor
2. **Power supply** - Use external 5V supply for >10 LEDs  
3. **LED count** - Verify `NUM_PIXELS` matches your strip
4. **Try sudo** - GPIO access may require elevated permissions

### Testing
For advanced GPIO testing, use the diagnostic tool:
```bash
python gpio_diagnostic.py
```

## 🛡️ Safety Notes

- **Power off** when making wiring changes
- **Use a resistor** (330-470Ω) to protect the data line
- **External power** for strips with >10 LEDs
- **Don't look directly** at bright LEDs
- **Connect grounds** - Pi, LEDs, and power supply

## 📚 Learn More

- **WS2812B Datasheet**: [Official specifications](https://www.adafruit.com/product/1138)
- **Adafruit NeoPixel Guide**: [CircuitPython tutorials](https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel)
- **Raspberry Pi GPIO**: [GPIO pinout reference](https://pinout.xyz/)

---

**Enjoy your blinking WS2812B LEDs! 🤍✨**