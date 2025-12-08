import urequests
import ujson
from lib.state import ApplicationState
from lib.error_codes import ErrorCodes

class Location:
    API_URL = "http://ip-api.com/json/?fields=status,message,timezone,offset,lat,lon,city"

    def __init__(self):
        self.fetchDone = False

    def act(self, state: ApplicationState):
        if state.wifiConnected:
            if not self.fetchDone:
                self._fetch_timezone_data(state)
                self.fetchDone = True # fetch done
        else:
            self.fetchDone = False # resync when the wifi is back

    def _fetch_timezone_data(self, state: ApplicationState):
        """Fetch timezone and location data from ip-api.com"""
        try:
            response = urequests.get(self.API_URL, timeout=5)
            if response.status_code == 200:
                data = ujson.loads(response.text)
                if data.get("status") == "success":
                    # Update state with timezone information
                    # Store offset in seconds (as provided by API)
                    state.timezoneOffset = data.get("offset", 3600)
                    state.locationCode = data.get("timezone", "Europe/Berlin")
                    state.location = data.get("city", "Unknown")
                    state.latitude = data.get("lat", 0.0)
                    state.longitude = data.get("lon", 0.0)
                    offset_hours = state.timezoneOffset / 3600
                    print(f"Location: {state.location} ({state.locationCode}), latitude: {state.latitude}, longitude: {state.longitude}, offset: {offset_hours}h")
                else:
                    # API returned an error
                    error_message = data.get("message", "Unknown error")
                    print(f"Location: API error: {error_message}")
                    state.errorCode = ErrorCodes.TIMEZONE_FETCH_FAILED
                    state.errorExtra = error_message[:20]  # Truncate to save memory
            else:
                print(f"Location: API fetch HTTP error: {response.status_code}")
                state.errorCode = ErrorCodes.TIMEZONE_FETCH_FAILED
                state.errorExtra = str(response.status_code)

            response.close()

        except Exception as e:
            print(f"Location: fetch exception: {e}")
