from secrets import WIFI_SSID, WIFI_PASSWORD, DASH0_AUTH_TOKEN

class Settings:
    def __init__(self):
        self.ssid = WIFI_SSID
        self.password = WIFI_PASSWORD
        self.dash0_auth_token = DASH0_AUTH_TOKEN
