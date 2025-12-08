import network
import time
from lib.state import ApplicationState
from lib.settings import Settings
from lib.util import throttle

class Wifi:
    # Connection cycle: every 15 minutes
    CONNECTION_CYCLE_MS = 15 * 60 * 1000  # 15 minutes
    # Stay connected for 2 minutes
    CONNECTED_DURATION_MS = 10 * 1000  # 10 seconds
    # Timeout if can't connect within 1 minute
    CONNECT_TIMEOUT_MS = 60 * 1000  # 1 minute

    # States
    STATE_IDLE = 0
    STATE_CONNECTING = 1
    STATE_CONNECTED = 2
    STATE_DISCONNECTING = 3

    def __init__(self, settings: Settings):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(False)  # Start with wifi off
        self.settings = settings

        # State machine
        self.state = self.STATE_IDLE
        self.last_cycle_start = None  # When the last connection cycle started
        self.connection_start_time = None  # When we started connecting
        self.connected_time = None  # When we successfully connected

    def is_connected(self):
        return self.wlan.isconnected()

    def _start_connection(self):
        """Initiate wifi connection"""
        self.wlan.active(True)
        self.wlan.connect(self.settings.ssid, self.settings.password)
        self.connection_start_time = time.ticks_ms()
        self.state = self.STATE_CONNECTING

    def _disconnect(self):
        """Disconnect from wifi"""
        self.wlan.disconnect()
        self.wlan.active(False)
        self.connected_time = None
        self.connection_start_time = None
        self.state = self.STATE_IDLE

    @throttle(1000)
    def act(self, state: ApplicationState):
        now = time.ticks_ms()

        if self.state == self.STATE_IDLE:
            # Check if it's time to start a new connection cycle
            if self.last_cycle_start is None or time.ticks_diff(now, self.last_cycle_start) >= self.CONNECTION_CYCLE_MS:
                print("Wifi: Starting new connection cycle...")
                state.wifiError = False
                self.last_cycle_start = now
                self._start_connection()

        elif self.state == self.STATE_CONNECTING:
            if self.is_connected():
                print("Wifi: Connected successfully")
                state.wifiConnected = True
                state.wifiError = False
                self.connected_time = now
                self.connection_start_time = None
                self.state = self.STATE_CONNECTED
            else:
                if time.ticks_diff(now, self.connection_start_time) >= self.CONNECT_TIMEOUT_MS:
                    print("Wifi: Connection timeout")
                    state.wifiError = True
                    state.wifiConnected = False
                    self._disconnect()

        elif self.state == self.STATE_CONNECTED:
            if not self.is_connected():
                print("Wifi: Lost connection unexpectedly")
                state.wifiError = True
                state.wifiConnected = False
                self._disconnect()
            elif time.ticks_diff(now, self.connected_time) >= self.CONNECTED_DURATION_MS:
                print("Wifi: Connection held for some time, time to disconnect")
                state.wifiConnected = False
                self._disconnect()
