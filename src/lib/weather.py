import urequests
import ujson
from lib.state import ApplicationState
from lib.settings import Settings

class Weather:
    # OpenWeatherMap Current Weather Data API
    # API documentation: https://openweathermap.org/current
    API_URL = "http://api.openweathermap.org/data/2.5/weather"

    def __init__(self, settings: Settings, logger=None):
        self.fetchDone = False
        self.logger = logger
        self.settings = settings

    def _log(self, level: str, message: str, **attributes):
        if self.logger:
            getattr(self.logger, level)(message, **attributes)
        else:
            print(f"Weather: {message}")

    def act(self, state: ApplicationState):
        # Only proceed if wifi is connected
        if not state.wifiConnected:
            self.fetchDone = False  # resync when wifi is back
            return

        # Only fetch if we have location data (latitude and longitude are set)
        if state.latitude == 0 and state.longitude == 0:
            return  # location not available yet

        # Only fetch once
        if not self.fetchDone:
            self._fetch_weather_data(state)
            self.fetchDone = True

    def _fetch_weather_data(self, state: ApplicationState):
        if not self.settings.weather_api_key:
            self._log("error", "Weather API key not configured")
            return

        try:
            # Build URL with parameters
            url = f"{self.API_URL}?lat={state.latitude}&lon={state.longitude}&appid={self.settings.weather_api_key}&units=metric"

            self._log("info", "Fetching weather data",
                     latitude=state.latitude,
                     longitude=state.longitude)

            response = urequests.get(url, timeout=5)

            if response.status_code == 200:
                data = ujson.loads(response.text)

                # Extract temperature from the response
                if "main" in data and "temp" in data["main"]:
                    state.temperature = int(data["main"]["temp"])

                    self._log("info", "Weather data fetched",
                             temperature=state.temperature,
                             location=state.location)
                else:
                    self._log("error", "Weather data format unexpected")
            else:
                self._log("error", "Weather API HTTP error",
                         status_code=response.status_code)

            response.close()

        except Exception as e:
            self._log("error", "Weather fetch exception", error=str(e))
