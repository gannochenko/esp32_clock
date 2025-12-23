import urequests
import ujson
from lib.state import ApplicationState
from lib.settings import Settings


class CalendarService:
    """
    Google Calendar API service that fetches daily event counts.
    Uses a Cloudflare Worker proxy to handle OAuth 2.0 authentication.

    The worker handles all JWT signing and token management,
    providing a simple JSON endpoint for the ESP32.
    """

    def __init__(self, settings: Settings, logger=None):
        self.settings = settings
        self.logger = logger
        self.fetchDone = False

    def _log(self, level: str, message: str, **attributes):
        if self.logger:
            getattr(self.logger, level)(message, **attributes)
        else:
            print(f"Calendar: {message}")

    def act(self, state: ApplicationState):
        # Only proceed if wifi is connected
        if not state.wifiConnected:
            self.fetchDone = False  # resync when wifi is back
            return

        # Only fetch once per day (or when not yet fetched)
        if not self.fetchDone:
            self._fetch_calendar_events(state)
            self.fetchDone = True

    def _fetch_calendar_events(self, state: ApplicationState):
        """
        Fetches today's calendar events from the Cloudflare Worker proxy.
        """
        if not hasattr(self.settings, 'calendar_worker_url'):
            self._log("error", "calendar_worker_url not configured in settings")
            return

        try:
            url = self.settings.calendar_worker_url

            self._log("info", "Fetching calendar events from worker")

            response = urequests.get(url, timeout=10)

            if response.status_code == 200:
                data = ujson.loads(response.text)

                if "eventCount" in data:
                    state.eventCount = data["eventCount"]

                    self._log("info", "Calendar events fetched",
                             event_count=state.eventCount,
                             date=data.get("date", "unknown"))
                else:
                    self._log("error", "Invalid response format from worker")
                    state.eventCount = 0
            else:
                self._log("error", "Worker HTTP error",
                         status_code=response.status_code)
                state.eventCount = 0

            response.close()

        except Exception as e:
            self._log("error", "Calendar fetch exception", error=str(e))
            state.eventCount = 0
