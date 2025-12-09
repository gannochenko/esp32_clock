import time
import json

try:
    import urequests as requests
except ImportError:
    import requests

from lib.settings import Settings

DASH0_ENDPOINT = "https://ingress.eu-west-1.aws.dash0.com:4318/v1/logs"

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

    # OTLP severity numbers (aligned with OpenTelemetry spec)
    OTLP_SEVERITY = {
        LEVEL_DEBUG: 5,   # DEBUG
        LEVEL_INFO: 9,    # INFO
        LEVEL_WARN: 13,   # WARN
        LEVEL_ERROR: 17   # ERROR
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
        """Send logs to Dash0 via OTLP HTTP"""
        try:
            # Build OTLP JSON payload
            resource_logs = {
                "resourceLogs": [
                    {
                        "resource": {
                            "attributes": [
                                {"key": "service.name", "value": {"stringValue": self.service_name}}
                            ]
                        },
                        "scopeLogs": [
                            {
                                "scope": {
                                    "name": self.service_name
                                },
                                "logRecords": [
                                    self._build_log_record(entry) for entry in log_entries
                                ]
                            }
                        ]
                    }
                ]
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.dash0_auth_token}"
            }

            response = requests.post(
                DASH0_ENDPOINT,
                data=json.dumps(resource_logs),
                headers=headers
            )

            if response.status_code >= 400:
                print(f"[Logger] Dash0 error: {response.status_code}")

            response.close()

        except Exception as e:
            print(f"[Logger] Failed to send to Dash0: {e}")

    def _build_log_record(self, log_entry: dict):
        """Build OTLP log record"""
        record = {
            "timeUnixNano": str(log_entry["timestamp"]),
            "severityNumber": self.OTLP_SEVERITY[log_entry["level"]],
            "severityText": self.LEVEL_NAMES[log_entry["level"]],
            "body": {
                "stringValue": log_entry["message"]
            }
        }

        # Add attributes if present
        if log_entry["attributes"]:
            record["attributes"] = [
                {"key": k, "value": {"stringValue": str(v)}}
                for k, v in log_entry["attributes"].items()
            ]

        return record
