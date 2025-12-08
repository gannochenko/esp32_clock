import time
from lib.displays import get_displays
from lib.state import ApplicationState
from lib.wifi import Wifi
from lib.settings import Settings
from lib.ntp import NTP
from lib.rtc import RTC
from lib.housekeeper import Housekeeper
from lib.location import Location

class Application:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.time_display_painter, self.stat_display_painter = get_displays()

        self.state = ApplicationState()
        self.wifi = Wifi(self.settings)
        self.rtc = RTC()
        self.ntp = NTP()
        self.location = Location()
        self.housekeeper = Housekeeper()

    def render_ui(self):
        self.time_display_painter.draw(self.state)
        self.stat_display_painter.draw(self.state)

    def run(self):
        try:
            while True:
                self.wifi.act(self.state)
                self.rtc.act(self.state)
                self.ntp.act(self.state)
                self.location.act(self.state)
                self.render_ui()
                self.housekeeper.act()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            # Cleanup: turn off display, disconnect WiFi, etc.
            self.wifi.wlan.disconnect()
            self.wifi.wlan.active(False)
        finally:
            print("Cleanup complete")
