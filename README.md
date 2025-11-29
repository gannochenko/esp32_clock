# ESP32 Clock

A MicroPython-based clock application for ESP32 microcontrollers with OLED display support.

## Features

- Real-time clock display on SSD1306 OLED (128x64)
- Support for internal RTC or external DS3231 RTC module
- NTP time synchronization over WiFi (optional)
- Configurable 12/24-hour format
- Date display
- Low power mode with WiFi disabled by default

## Hardware Requirements

- ESP32 development board
- SSD1306 OLED display (128x64, I2C)
- (Optional) DS3231 RTC module for battery-backed timekeeping

### Default Pin Configuration

- I2C SDA: GPIO 21
- I2C SCL: GPIO 22

## Project Structure

```
esp32_clock/
├── boot.py                 # Boot configuration
├── main.py                 # Main application entry point
├── src/
│   ├── config/
│   │   └── settings.py     # Configuration settings
│   └── lib/
│       ├── display.py      # Display driver and rendering
│       └── rtc.py          # RTC management and time sync
└── requirements.txt        # MicroPython package dependencies
```

## Setup

### 1. Flash MicroPython

Flash MicroPython firmware to your ESP32:

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

### 2. Install Dependencies

Install required MicroPython packages:

```bash
mpremote connect /dev/ttyUSB0 mip install micropython-ssd1306
```

### 3. Upload Code

Upload the project files to the ESP32:

```bash
# Upload all files
mpremote connect /dev/ttyUSB0 cp -r boot.py main.py src :

# Or use ampy
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put src
```

### 4. Configure

Edit `src/config/settings.py` to match your hardware setup and preferences.

For WiFi/NTP sync, update:
```python
"wifi": {
    "enabled": True,
    "ssid": "YourWiFiSSID",
    "password": "YourPassword",
}
```

## Development

### Running the Clock

Connect to the ESP32 and run:

```bash
# Using mpremote
mpremote connect /dev/ttyUSB0 run main.py

# Or reset the device to auto-run
mpremote connect /dev/ttyUSB0 reset
```

### Testing

Connect via serial REPL:

```bash
mpremote connect /dev/ttyUSB0 repl
```

Then import and test modules:

```python
from src.lib.display import Display
from src.config.settings import config

display = Display(config)
display.show_message("Hello World", 10, 20)
```

### Manually Setting Time

In the REPL:

```python
from src.lib.rtc import RTCManager
from src.config.settings import config

rtc = RTCManager(config)
rtc.set_time(2025, 1, 15, 14, 30, 0)  # year, month, day, hour, minute, second
```

## Configuration Options

See `src/config/settings.py` for all available options:

- Display type and I2C pins
- RTC source (internal, NTP, DS3231)
- Time format (12/24 hour)
- WiFi credentials
- Timezone offset

## Troubleshooting

**Display not working:**
- Check I2C connections (SDA/SCL pins)
- Verify I2C address (usually 0x3C for SSD1306)
- Console fallback will print time if display fails

**Time not keeping:**
- Use external DS3231 RTC with battery backup
- Enable NTP sync with WiFi for automatic updates

## License

MIT
