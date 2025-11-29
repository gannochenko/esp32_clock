# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a MicroPython-based clock application for ESP32 microcontrollers. The project displays time on an SSD1306 OLED display with support for various time sources (internal RTC, NTP, or external DS3231 RTC).

## Architecture

The application follows a modular architecture:

- **boot.py**: Runs on device startup, configures WiFi state and garbage collection
- **main.py**: Application entry point containing the main loop that coordinates display and RTC modules
- **src/lib/display.py**: Encapsulates all display operations, supports SSD1306 via I2C with console fallback
- **src/lib/rtc.py**: Manages time from multiple sources (internal RTC, NTP, DS3231) with timezone support
- **src/config/settings.py**: Centralized configuration for hardware pins, display settings, RTC type, WiFi credentials, and time format

The main loop (main.py:11-30) continuously fetches time from RTCManager and passes it to Display.show_time(), which handles both hardware rendering and console fallback.

## Development Commands

### Deploying to ESP32

```bash
# Upload all project files to ESP32
mpremote connect /dev/ttyUSB0 cp -r boot.py main.py src :

# Alternative using ampy
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put src
```

### Running and Testing

```bash
# Run main.py directly
mpremote connect /dev/ttyUSB0 run main.py

# Connect to REPL for interactive testing
mpremote connect /dev/ttyUSB0 repl

# Reset device to auto-run main.py
mpremote connect /dev/ttyUSB0 reset
```

### Installing Dependencies

```bash
# Install SSD1306 driver
mpremote connect /dev/ttyUSB0 mip install micropython-ssd1306

# For DS3231 support (when implemented)
mpremote connect /dev/ttyUSB0 mip install micropython-ds3231
```

## Key Implementation Details

### Display System (src/lib/display.py)

- Initializes I2C connection based on config (default: SCL=22, SDA=21)
- Gracefully degrades to console output if hardware unavailable
- show_time() method converts time tuple to formatted string based on 12/24hr setting
- All display operations check for hardware availability before attempting I2C communication

### RTC Management (src/lib/rtc.py)

- Supports three time sources via config["rtc"]["type"]:
  - "internal": Uses ESP32's built-in RTC (loses time on power loss)
  - "ntp": Syncs with NTP server over WiFi (requires WiFi enabled in config)
  - "ds3231": External I2C RTC with battery backup (TODO: implement I2C driver)
- get_time() returns time tuple with timezone offset applied
- _sync_ntp() handles WiFi connection and NTP synchronization

### Configuration Pattern

All hardware and feature configuration lives in src/config/settings.py. When adding features:
- Add new config sections to the config dict
- Access via self.config in class constructors
- Document pin numbers and defaults in comments

## Common Development Tasks

### Adding a New Display Type

1. Import the driver at the top of src/lib/display.py
2. Add elif branch in _init_display() method (display.py:24-44)
3. Update config["display"]["type"] options in settings.py
4. Handle display-specific initialization and rendering

### Adding a New RTC Source

1. Add elif branch in RTCManager._init_rtc() (rtc.py:21-49)
2. Implement time reading to return standard time tuple format
3. Update config["rtc"]["type"] options in settings.py

### Modifying Time Display Format

Edit Display.show_time() method (display.py:50-91) to change time/date formatting. Current format controlled by config["format"] settings.

## Port Configuration

Default ESP32 serial port is /dev/ttyUSB0 (Linux). On macOS use /dev/tty.usbserial-*, on Windows use COM*.

Find your port:
```bash
# Linux/macOS
ls /dev/tty.*
ls /dev/ttyUSB*

# Or use mpremote to auto-detect
mpremote connect list
```
