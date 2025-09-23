# LED Setup Guide

This guide will help you configure the LED controller for different types of LED strips and troubleshoot connection issues.

## Supported LED Types

### 1. WS2812/WS2811 (NeoPixel) LEDs
**Most common addressable LEDs**
- **Configuration**: Set `LED_TYPE = "NEOPIXEL"` in `src/main.py`
- **Wiring**: 
  - VCC → 5V (or 3.3V for some variants)
  - GND → Ground
  - Data → GPIO 18 (default, configurable)
- **Library**: `adafruit-circuitpython-neopixel`

### 2. APA102/SK9822 (DotStar) LEDs
**High-speed addressable LEDs with separate clock line**
- **Configuration**: Set `LED_TYPE = "DOTSTAR"` in `src/main.py`
- **Wiring**:
  - VCC → 5V
  - GND → Ground
  - Data → GPIO 10 (MOSI)
  - Clock → GPIO 11 (SCLK)
- **Library**: `adafruit-circuitpython-dotstar`

### 3. WS2801 LEDs
**Older addressable LEDs with separate clock line**
- **Configuration**: Set `LED_TYPE = "WS2801"` in `src/main.py`
- **Wiring**:
  - VCC → 5V
  - GND → Ground
  - Data → GPIO 10 (MOSI)
  - Clock → GPIO 11 (SCLK)
- **Library**: `adafruit-circuitpython-ws2801`

### 4. PWM RGB LEDs
**Single RGB LED or LED strip with separate R, G, B pins**
- **Configuration**: Set `LED_TYPE = "PWM"` in `src/main.py`
- **Wiring**:
  - Red → GPIO 18
  - Green → GPIO 19
  - Blue → GPIO 20
  - Common cathode/anode to GND/VCC
- **Library**: `adafruit-circuitpython-pwmio`

## Quick Setup Steps

1. **Identify your LED type** using the descriptions above
2. **Edit the configuration** in `src/main.py`:
   ```python
   LED_TYPE = "NEOPIXEL"  # Change this to your LED type
   NUM_PIXELS = 10        # Set your number of LEDs
   ```
3. **Check pin connections** in the `PIN_CONFIGS` dictionary
4. **Install required libraries**:
   ```bash
   # Install all libraries (recommended):
   pip install -r requirements.txt
   
   # Or install specific library for your LED type:
   pip install adafruit-circuitpython-neopixel  # for NeoPixel
   pip install adafruit-circuitpython-dotstar   # for DotStar
   pip install adafruit-circuitpython-ws2801    # for WS2801
   pip install adafruit-circuitpython-pwmio     # for PWM
   ```

## Troubleshooting Connection Issues

### Common Problems and Solutions

#### 1. "Import could not be resolved" errors
**Problem**: Missing required libraries
**Solution**: 
```bash
pip install adafruit-blinka
pip install adafruit-circuitpython-[LED_TYPE]
```

#### 2. "Permission denied" errors
**Problem**: GPIO access requires elevated permissions
**Solution**: 
```bash
sudo python3 src/main.py
```

#### 3. LEDs don't light up
**Possible causes and solutions**:
- **Wrong LED type**: Double-check your LED strip type and configuration
- **Incorrect wiring**: Verify connections match the pin configuration
- **Power issues**: Ensure adequate power supply (5V for most LEDs)
- **GPIO conflicts**: Try different GPIO pins if others are in use

#### 4. Only some LEDs work
**Possible causes**:
- **Insufficient power**: Large LED strips need external power supply
- **Data corruption**: Check data line connections and add pull-up resistor if needed
- **Wrong pixel count**: Verify `NUM_PIXELS` matches your actual LED count

#### 5. Colors are wrong
**Possible causes**:
- **Color order**: Some LEDs use GRB instead of RGB order
- **Voltage levels**: 3.3V signals may not work reliably with 5V LEDs (use level shifter)

### Advanced Troubleshooting

#### Test Individual Components
1. **Run connection test**: The program now includes an automatic connection test
2. **Check GPIO functionality**:
   ```bash
   # Test if GPIO is working (replace 18 with your pin)
   echo "18" > /sys/class/gpio/export
   echo "out" > /sys/class/gpio/gpio18/direction
   echo "1" > /sys/class/gpio/gpio18/value
   echo "0" > /sys/class/gpio/gpio18/value
   echo "18" > /sys/class/gpio/unexport
   ```

#### Hardware Considerations
1. **Level shifting**: For 5V LEDs with 3.3V microcontroller, use a level shifter
2. **Pull-up resistors**: Add 1kΩ resistor between data pin and VCC for long cables
3. **Power supply**: Calculate power needs (each LED ≈ 60mA at full brightness)
4. **Grounding**: Ensure common ground between microcontroller and LED power supply

## Pin Configuration Customization

You can customize the GPIO pins by editing the `PIN_CONFIGS` dictionary in `src/main.py`:

```python
PIN_CONFIGS = {
    "NEOPIXEL": {
        "data_pin": board.D21,  # Change to your preferred pin
    },
    "DOTSTAR": {
        "data_pin": board.D10,  # MOSI
        "clock_pin": board.D11, # SCLK
    },
    # ... other configurations
}
```

## Performance Tips

1. **Reduce `UPDATE_DELAY`** for faster animations (minimum ~0.01s)
2. **Lower `BRIGHTNESS`** to reduce power consumption and heat
3. **Use shorter LED strips** for better performance with cheaper controllers
4. **Consider hardware SPI** for DotStar/WS2801 for better performance

## Getting Help

If you're still having issues:
1. Check that your hardware setup matches one of the supported configurations
2. Try the built-in connection test
3. Verify your LED strip specifications with the manufacturer
4. Test with a minimal number of LEDs (1-3) first
5. Check for adequate power supply (especially for >10 LEDs)

Common Raspberry Pi GPIO pins for reference:
- GPIO 18 (Physical pin 12) - PCM_CLK/PWM0
- GPIO 10 (Physical pin 19) - SPI0_MOSI
- GPIO 11 (Physical pin 23) - SPI0_SCLK
- GPIO 19 (Physical pin 35) - PCM_FS/PWM1
- GPIO 20 (Physical pin 38) - PCM_DIN