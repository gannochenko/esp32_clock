from lib.application import Application
from secrets import WIFI_SSID, WIFI_PASSWORD

app = Application()
app.connect_wifi(WIFI_SSID, WIFI_PASSWORD)
app.run()
