import urequests
import ujson
from lib.state import ApplicationState
from lib.error_codes import ErrorCodes

class Location:
    API_URL = "http://ip-api.com/json/?fields=status,message,timezone,offset,lat,lon,city"

    def __init__(self):
        self.initialFetchDone = False
        self.lastDay = None  # Track the day to detect midnight crossover

    def act(self, state: ApplicationState):
        if state.wifiConnected:
            if not self.initialFetchDone:
                self.initialFetchDone = True
                # Initial fetch on startup
                print(f"Initial fetch of timezone data")
                self._fetch_timezone_data(state)
                # Only set lastDay if we have a valid day value
                if state.day > 0:
                    self.lastDay = state.day
            else:
                # Check if it's a new day (midnight has passed)
                # Only check if both lastDay and state.day are valid
                if state.day > 0 and self.lastDay is not None and state.day != self.lastDay:
                    print(f"Daily fetch of timezone data")
                    self._fetch_timezone_data(state)
                    self.lastDay = state.day
                elif self.lastDay is None and state.day > 0:
                    # Handle case where initial fetch happened before RTC was synced
                    self.lastDay = state.day

    def _fetch_timezone_data(self, state: ApplicationState):
        """Fetch timezone and location data from ip-api.com"""
        try:
            response = urequests.get(self.API_URL, timeout=5)
            if response.status_code == 200:
                data = ujson.loads(response.text)
                print(f"Data: {data}")
                if data.get("status") == "success":
                    # Update state with timezone information
                    # Store offset in seconds (as provided by API)
                    state.timezoneOffset = data.get("offset", 3600)
                    state.locationCode = data.get("timezone", "Europe/Berlin")
                    state.location = data.get("city", "Unknown")
                    state.latitude = data.get("lat", 0.0)
                    state.longitude = data.get("lon", 0.0)
                    offset_hours = state.timezoneOffset / 3600
                    print(f"Timezone data fetched: {state.location} ({state.locationCode}), latitude: {state.latitude}, longitude: {state.longitude}, offset: {offset_hours}h")
                else:
                    # API returned an error
                    error_message = data.get("message", "Unknown error")
                    print(f"Timezone API error: {error_message}")
                    state.errorCode = ErrorCodes.TIMEZONE_FETCH_FAILED
                    state.errorExtra = error_message[:20]  # Truncate to save memory
            else:
                print(f"Timezone fetch HTTP error: {response.status_code}")
                state.errorCode = ErrorCodes.TIMEZONE_FETCH_FAILED
                state.errorExtra = str(response.status_code)

            response.close()

        except Exception as e:
            print(f"Timezone fetch exception: {e}")
            state.errorCode = ErrorCodes.TIMEZONE_FETCH_FAILED
            state.errorExtra = "Network error"
