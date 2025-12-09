import network
import time
from lib.state import ApplicationState
from lib.settings import Settings
from lib.util import throttle

class Wifi:
    CONNECTION_CYCLE_MS = 15 * 60 * 1000  # 15 minutes
    CONNECTED_DURATION_MS = 10 * 1000  # 10 seconds
    CONNECT_TIMEOUT_MS = 60 * 1000  # 1 minute

    # States
    STATE_IDLE = 0
    STATE_CONNECTING = 1
    STATE_CONNECTED = 2
    STATE_DISCONNECTING = 3

    def __init__(self, settings: Settings, logger=None):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(False)  # Start with wifi off
        self.settings = settings
        self.logger = logger

        # State machine
        self.state = self.STATE_IDLE
        self.last_cycle_start = None  # When the last connection cycle started
        self.connection_start_time = None  # When we started connecting
        self.connected_time = None  # When we successfully connected

    def is_connected(self):
        return self.wlan.isconnected()

    def _log(self, level: str, message: str, **attributes):
        """Helper to log with fallback to print"""
        if self.logger:
            getattr(self.logger, level)(message, **attributes)
        else:
            print(f"Wifi: {message}")

    def _start_connection(self):
        """Initiate wifi connection"""
        self.wlan.active(True)
        self.wlan.connect(self.settings.ssid, self.settings.password)
        self.connection_start_time = time.ticks_ms()
        self.state = self.STATE_CONNECTING
        self._log("info", "Initiating wifi connection", ssid=self.settings.ssid)

    def _disconnect(self):
        """Disconnect from wifi"""
        self.wlan.disconnect()
        self.wlan.active(False)
        self.connected_time = None
        self.connection_start_time = None
        self.state = self.STATE_IDLE

        # Update logger wifi status
        if self.logger:
            self.logger.set_wifi_status(False)

    @throttle(1000)
    def act(self, state: ApplicationState):
        now = time.ticks_ms()

        if self.state == self.STATE_IDLE:
            # Check if it's time to start a new connection cycle
            if self.last_cycle_start is None or time.ticks_diff(now, self.last_cycle_start) >= self.CONNECTION_CYCLE_MS:
                self._log("info", "Starting new connection cycle")
                state.wifiError = False
                self.last_cycle_start = now
                self._start_connection()

        elif self.state == self.STATE_CONNECTING:
            if self.is_connected():
                connection_duration_sec = time.ticks_diff(now, self.connection_start_time) / 1000
                self._log("info", "Connected successfully",
                         duration_sec=f"{connection_duration_sec:.2f}",
                         ip=self.wlan.ifconfig()[0])

                state.wifiConnected = True
                state.wifiError = False
                self.connected_time = now
                self.connection_start_time = None
                self.state = self.STATE_CONNECTED

                # Update logger wifi status
                if self.logger:
                    self.logger.set_wifi_status(True)
            else:
                if time.ticks_diff(now, self.connection_start_time) >= self.CONNECT_TIMEOUT_MS:
                    self._log("error", "Connection timeout after 1 minute",
                             ssid=self.settings.ssid,
                             status=self.wlan.status())
                    state.wifiError = True
                    state.wifiConnected = False
                    self._disconnect()

        elif self.state == self.STATE_CONNECTED:
            if not self.is_connected():
                self._log("error", "Lost connection unexpectedly")
                state.wifiError = True
                state.wifiConnected = False
                self._disconnect()
            elif time.ticks_diff(now, self.connected_time) >= self.CONNECTED_DURATION_MS:
                self._log("info", "Disconnecting after holding connection")
                state.wifiConnected = False
                self._disconnect()
