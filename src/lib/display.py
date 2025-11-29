# display.py -- Display driver for ESP32 Clock
import machine
from time import sleep

try:
    from ssd1306 import SSD1306_I2C
    HAS_SSD1306 = True
except ImportError:
    HAS_SSD1306 = False
    print("Warning: ssd1306 driver not found")


class Display:
    """Handles display operations for the clock"""

    def __init__(self, config):
        self.config = config["display"]
        self.format_config = config["format"]
        self.display = None

        self._init_display()

    def _init_display(self):
        """Initialize the display based on configuration"""
        display_type = self.config["type"]

        if display_type == "ssd1306":
            if not HAS_SSD1306:
                print("SSD1306 driver not available, using console output")
                return

            try:
                i2c = machine.I2C(
                    0,
                    scl=machine.Pin(self.config["i2c_scl"]),
                    sda=machine.Pin(self.config["i2c_sda"]),
                    freq=self.config["i2c_freq"]
                )
                self.display = SSD1306_I2C(
                    self.config["width"],
                    self.config["height"],
                    i2c
                )
                print("Display initialized: SSD1306")
            except Exception as e:
                print(f"Failed to initialize display: {e}")
        else:
            print(f"Unsupported display type: {display_type}")

    def show_time(self, time_tuple):
        """Display the current time"""
        if time_tuple is None:
            return

        year, month, day, hour, minute, second, weekday, yearday = time_tuple

        # Format time string
        if self.format_config["24hour"]:
            time_str = f"{hour:02d}:{minute:02d}"
        else:
            am_pm = "AM" if hour < 12 else "PM"
            hour_12 = hour % 12
            if hour_12 == 0:
                hour_12 = 12
            time_str = f"{hour_12:02d}:{minute:02d} {am_pm}"

        if self.format_config["show_seconds"]:
            time_str += f":{second:02d}"

        # Format date string
        date_str = f"{year}-{month:02d}-{day:02d}" if self.format_config["show_date"] else ""

        # Display on hardware or console
        if self.display:
            self.display.fill(0)
            self.display.text(time_str, 10, 20, 1)
            if date_str:
                self.display.text(date_str, 5, 35, 1)
            self.display.show()
        else:
            # Fallback to console output
            print(f"\r{time_str} {date_str}", end="")

    def clear(self):
        """Clear the display"""
        if self.display:
            self.display.fill(0)
            self.display.show()
        else:
            print("\nDisplay cleared")

    def show_message(self, message, x=0, y=0):
        """Show a custom message on the display"""
        if self.display:
            self.display.fill(0)
            self.display.text(message, x, y, 1)
            self.display.show()
        else:
            print(message)
