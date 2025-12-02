import network
import time
from lib.state import ApplicationState
from lib.settings import Settings
from lib.util import throttle
from lib.error_codes import ErrorCodes

class Wifi:
    CONNECT_TIMEOUT_MS = 5000  # 5 seconds timeout for connection

    def __init__(self, settings: Settings):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.settings = settings
        self._connect_time = None

    def connect(self):
        self._connect_time = time.ticks_ms()
        self.wlan.connect(self.settings.ssid, self.settings.password)

    def is_connected(self):
        return self.wlan.isconnected()

    @throttle(1000)
    def act(self, state: ApplicationState):
        if self.is_connected():
            state.wifiConnected = True
            self._connect_time = None  # Reset timeout tracking
        else:
            state.wifiConnected = False

            # Check if connection timeout has expired
            if self._connect_time is not None:
                elapsed = time.ticks_diff(time.ticks_ms(), self._connect_time)
                if elapsed >= self.CONNECT_TIMEOUT_MS:
                    # Timeout expired, give up and report error
                    status = self.wlan.status()
                    state.errorCode = ErrorCodes.WIFI_FAILURE
                    if status == 201:
                        state.errorExtra = "AP not found"
                    elif status == 202:
                        state.errorExtra = "Wrong password"
                    elif status in (203, 204, 205):
                        state.errorExtra = "Timeout"
                    else:
                        state.errorExtra = ""
                    self._connect_time = None
