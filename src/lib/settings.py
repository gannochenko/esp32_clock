from secrets import WIFI_SSID, WIFI_PASSWORD, DASH0_AUTH_TOKEN, WEATHER_API_KEY

class Settings:
    def __init__(self):
        self.ssid = WIFI_SSID
        self.password = WIFI_PASSWORD
        self.dash0_auth_token = DASH0_AUTH_TOKEN
        self.weather_api_key = WEATHER_API_KEY
