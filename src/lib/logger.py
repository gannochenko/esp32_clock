import time
import json

try:
    import urequests as requests
except ImportError:
    import requests

from lib.settings import Settings

DASH0_ENDPOINT = "https://esp32clock-dash0-relay.gannochenko-dev.workers.dev"

class Logger:
    LEVEL_DEBUG = 0
    LEVEL_INFO = 1
    LEVEL_WARN = 2
    LEVEL_ERROR = 3

    LEVEL_NAMES = {
        LEVEL_DEBUG: "DEBUG",
        LEVEL_INFO: "INFO",
        LEVEL_WARN: "WARN",
        LEVEL_ERROR: "ERROR"
    }


    def __init__(self, settings: Settings, service_name: str = "esp32_clock"):
        self.settings = settings
        self.service_name = service_name
        self.log_queue = []
        self.max_queue_size = 50
        self.is_wifi_connected = False

    def set_wifi_status(self, connected: bool):
        """Update wifi connection status"""
        self.is_wifi_connected = connected

        # Try to flush queue when wifi connects
        if connected and len(self.log_queue) > 0:
            self._flush_queue()

    def debug(self, message: str, **attributes):
        """Log debug message"""
        self._log(self.LEVEL_DEBUG, message, attributes)

    def info(self, message: str, **attributes):
        """Log info message"""
        self._log(self.LEVEL_INFO, message, attributes)

    def warn(self, message: str, **attributes):
        """Log warning message"""
        self._log(self.LEVEL_WARN, message, attributes)

    def error(self, message: str, **attributes):
        """Log error message"""
        self._log(self.LEVEL_ERROR, message, attributes)

    def _log(self, level: int, message: str, attributes: dict):
        """Internal logging method"""
        timestamp_ns = time.time_ns() if hasattr(time, 'time_ns') else int(time.time() * 1_000_000_000)
        level_name = self.LEVEL_NAMES[level]

        # Always print to terminal
        print(f"[{level_name}] {message}")
        if attributes:
            print(f"  Attributes: {attributes}")

        # Always send to Dash0
        log_entry = {
            "timestamp": timestamp_ns,
            "level": level,
            "message": message,
            "attributes": attributes
        }

        if self.is_wifi_connected:
            self._send_to_dash0([log_entry])
        else:
            # Queue for later if wifi is not connected
            self._queue_log(log_entry)

    def _queue_log(self, log_entry: dict):
        """Add log to queue"""
        self.log_queue.append(log_entry)

        # Prevent queue from growing too large
        if len(self.log_queue) > self.max_queue_size:
            self.log_queue.pop(0)

    def _flush_queue(self):
        """Send queued logs to Dash0"""
        if len(self.log_queue) == 0:
            return

        try:
            self._send_to_dash0(self.log_queue)
            self.log_queue = []
        except Exception as e:
            print(f"[Logger] Failed to flush queue: {e}")

    def _send_to_dash0(self, log_entries: list):
        """Send logs to Dash0 via relay"""
        try:
            # Build relay-format JSON payload
            logs = []
            for entry in log_entries:
                log = {
                    "level": self.LEVEL_NAMES[entry["level"]].lower(),
                    "service.name": self.service_name,
                    "message": entry["message"],
                    "attributes": entry["attributes"]
                }
                logs.append(log)

            payload = json.dumps(logs)

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.dash0_auth_token}",
                "Dash0-Dataset": self.service_name
            }

            print(f"[Logger] Sending to {DASH0_ENDPOINT}")

            response = requests.post(
                DASH0_ENDPOINT,
                data=payload,
                headers=headers
            )

            print(f"[Logger] Response status: {response.status_code}")

            if hasattr(response, 'text'):
                print(f"[Logger] Response body: {response.text}")

            if response.status_code >= 400:
                print(f"[Logger] Dash0 error: {response.status_code}")
            else:
                print(f"[Logger] Successfully sent {len(log_entries)} logs to Dash0")

            response.close()

        except Exception as e:
            print(f"[Logger] Failed to send to Dash0: {e}")
            import traceback
            traceback.print_exc()
