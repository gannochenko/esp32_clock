from machine import Pin, I2C
import network
import time
from lib.ssd1306 import SSD1306_I2C
from lib.ui import Time_Display_Painter, Stat_Display_Painter, Temp_Display_Painter
from lib.state import ApplicationState
from lib.error_codes import ErrorCodes

class Application:
    def __init__(self):
        # SCL -> A5 -> GPIO12, SDA -> A4 -> GPIO11
        self.i2c_time_display = I2C(0, scl=Pin(12), sda=Pin(11))
        # SCL -> A1 -> GPIO2, SDA -> A2 -> GPIO3
        self.i2c_temp_display = I2C(1, scl=Pin(2), sda=Pin(3))

        self.time_display_painter = Time_Display_Painter(SSD1306_I2C(128, 64, self.i2c_time_display))
        self.stat_display_painter = Stat_Display_Painter(SSD1306_I2C(128, 64, self.i2c_temp_display))
        #self.stat_display_painter = Temp_Display_Painter(SSD1306_I2C(128, 64, self.i2c_temp_display))

        self.state = ApplicationState()

    def connect_wifi(self, ssid, password, timeout=10):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        if not wlan.isconnected():
            wlan.connect(ssid, password)

            start = time.time()
            while not wlan.isconnected():
                status = wlan.status()

                if time.time() - start > timeout:
                    self.state.wifiStatus = status
                    self.state.errorCode = ErrorCodes.WIFI_FAILURE
                    if status == 201:
                        self.state.errorExtra = "AP not found"
                    elif status == 202:
                        self.state.errorExtra = "Wrong password"
                    elif status in (203, 204, 205):
                        self.state.errorExtra = "Timeout"
                    else:
                        self.state.errorExtra = ""
                    return

                time.sleep(0.5)

            # Connection successful - get details
            ip, subnet, gateway, dns = wlan.ifconfig()
            rssi = wlan.config('rssi')

            # Store connection info
            self.state.connected = True
            self.state.ip = ip
            self.state.rssi = rssi
            self.state.wifiStatus = wlan.status()

    def render_state(self):
        self.time_display_painter.draw(self.state)
        self.stat_display_painter.draw(self.state)

    def run(self):
        # self.state.errorCode = ErrorCodes.SHIT_HAPPENED
        # self.state.errorExtra = "Fuck you fuck"
        self.render_state()
