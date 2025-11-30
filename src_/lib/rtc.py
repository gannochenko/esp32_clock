# rtc.py -- RTC (Real-Time Clock) manager for ESP32 Clock
import machine
import time

try:
    import ntptime
    HAS_NTP = True
except ImportError:
    HAS_NTP = False
    print("Warning: ntptime not available")


class RTCManager:
    """Manages real-time clock functionality"""

    def __init__(self, config):
        self.config = config["rtc"]
        self.wifi_config = config["wifi"]
        self.rtc = machine.RTC()
        self.timezone_offset = self.config["timezone"] * 3600

        self._init_rtc()

    def _init_rtc(self):
        """Initialize the RTC based on configuration"""
        rtc_type = self.config["type"]

        if rtc_type == "internal":
            print("Using internal RTC")
            # Set a default time if not set (2025-01-01 00:00:00)
            # In production, you'd sync with NTP or external RTC
            try:
                current = self.rtc.datetime()
                if current[0] < 2020:  # Year check
                    self.rtc.datetime((2025, 1, 1, 0, 0, 0, 0, 0))
                    print("Internal RTC initialized with default time")
            except:
                self.rtc.datetime((2025, 1, 1, 0, 0, 0, 0, 0))

        elif rtc_type == "ntp":
            if self.wifi_config["enabled"] and HAS_NTP:
                self._sync_ntp()
            else:
                print("NTP sync requires WiFi to be enabled")
                print("Falling back to internal RTC")

        elif rtc_type == "ds3231":
            print("DS3231 RTC support - implement I2C communication")
            # TODO: Implement DS3231 I2C driver
            print("Falling back to internal RTC for now")

    def _sync_ntp(self):
        """Synchronize time with NTP server"""
        if not HAS_NTP:
            print("NTP not available")
            return

        import network

        # Connect to WiFi
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)

        if not sta_if.isconnected():
            print("Connecting to WiFi...")
            sta_if.connect(self.wifi_config["ssid"], self.wifi_config["password"])

            timeout = 10
            while not sta_if.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1

        if sta_if.isconnected():
            print(f"Connected to WiFi: {sta_if.ifconfig()}")
            try:
                ntptime.settime()
                print("Time synchronized with NTP")
            except Exception as e:
                print(f"NTP sync failed: {e}")
        else:
            print("WiFi connection failed")

    def get_time(self):
        """Get current time as a tuple"""
        try:
            # Get time from RTC
            dt = self.rtc.datetime()
            # RTC datetime format: (year, month, day, weekday, hours, minutes, seconds, subseconds)
            # Convert to time tuple: (year, month, day, hour, minute, second, weekday, yearday)
            year, month, day, weekday, hour, minute, second, _ = dt

            # Apply timezone offset
            timestamp = time.mktime((year, month, day, hour, minute, second, weekday, 0))
            timestamp += self.timezone_offset
            adjusted_time = time.localtime(timestamp)

            return adjusted_time
        except Exception as e:
            print(f"Error getting time: {e}")
            return None

    def set_time(self, year, month, day, hour, minute, second):
        """Manually set the RTC time"""
        try:
            # Set RTC datetime
            # Format: (year, month, day, weekday, hours, minutes, seconds, subseconds)
            weekday = 0  # Calculate if needed
            self.rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
            print(f"RTC time set to {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
            return True
        except Exception as e:
            print(f"Error setting time: {e}")
            return False
