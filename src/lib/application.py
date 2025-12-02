from machine import Pin, I2C
import time
from lib.ssd1306 import SSD1306_I2C
from lib.ui import Time_Display_Painter, Stat_Display_Painter, Temp_Display_Painter
from lib.state import ApplicationState
from lib.error_codes import ErrorCodes
from lib.wifi import Wifi
from lib.settings import Settings
from lib.ntp import NTP
from lib.rtc import RTC

class Application:
    def __init__(self, settings: Settings):
        self.settings = settings

        # SCL -> A5 -> GPIO12, SDA -> A4 -> GPIO11
        self.i2c_time_display = I2C(0, scl=Pin(12), sda=Pin(11))
        # SCL -> A1 -> GPIO2, SDA -> A2 -> GPIO3
        self.i2c_temp_display = I2C(1, scl=Pin(2), sda=Pin(3))

        self.time_display_painter = Time_Display_Painter(SSD1306_I2C(128, 64, self.i2c_time_display))
        self.stat_display_painter = Stat_Display_Painter(SSD1306_I2C(128, 64, self.i2c_temp_display))
        #self.stat_display_painter = Temp_Display_Painter(SSD1306_I2C(128, 64, self.i2c_temp_display))

        self.state = ApplicationState()
        self.wifi = Wifi(self.settings)
        self.rtc = RTC()
        self.ntp = NTP()

    def render_ui(self):
        self.time_display_painter.draw(self.state)
        self.stat_display_painter.draw(self.state)

    def run(self):
        self.wifi.connect()
        try:
            while True:
                self.wifi.act(self.state) # trying to connect
                self.rtc.act(self.state) # populating state with time from RTC
                self.ntp.act(self.state) # syncing time from NTP once in 12 hours
                self.render_ui() # rendering the current state
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            # Cleanup: turn off display, disconnect WiFi, etc.
            self.wifi.wlan.disconnect()
            self.wifi.wlan.active(False)
        finally:
            print("Cleanup complete")
