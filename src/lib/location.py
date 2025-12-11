import urequests
import ujson
from lib.state import ApplicationState
from lib.error_codes import ErrorCodes

class Location:
    API_URL = "http://ip-api.com/json/?fields=status,message,timezone,offset,lat,lon,city"

    def __init__(self, logger=None):
        self.fetchDone = False
        self.logger = logger

    def _log(self, level: str, message: str, **attributes):
        if self.logger:
            getattr(self.logger, level)(message, **attributes)
        else:
            print(f"Location: {message}")

    def act(self, state: ApplicationState):
        if state.wifiConnected:
            if not self.fetchDone:
                self._fetch_timezone_data(state)
                self.fetchDone = True # fetch done
        else:
            self.fetchDone = False # resync when the wifi is back

    def _fetch_timezone_data(self, state: ApplicationState):
        try:
            response = urequests.get(self.API_URL, timeout=5)
            if response.status_code == 200:
                data = ujson.loads(response.text)
                if data.get("status") == "success":
                    state.timezoneOffset = data.get("offset", 3600)
                    state.locationCode = data.get("timezone", "Europe/Berlin")
                    state.location = data.get("city", "Unknown")
                    state.latitude = data.get("lat", 0.0)
                    state.longitude = data.get("lon", 0.0)
                    offset_hours = state.timezoneOffset / 3600
                    self._log("info", "Location data fetched",
                             location=state.location,
                             location_code=state.locationCode,
                             latitude=state.latitude,
                             longitude=state.longitude,
                             offset_hours=offset_hours)
                else:
                    error_message = data.get("message", "Unknown error")
                    self._log("error", "Location API error", error=error_message)
                    # state.errorCode = ErrorCodes.TIMEZONE_FETCH_FAILED
                    # state.errorExtra = error_message[:20]
            else:
                self._log("error", "Location API fetch HTTP error", status_code=response.status_code)
                # state.errorCode = ErrorCodes.TIMEZONE_FETCH_FAILED
                # state.errorExtra = str(response.status_code)

            response.close()

        except Exception as e:
            self._log("error", "Location fetch exception", error=str(e))
