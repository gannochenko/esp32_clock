from machine import Pin, I2C
import network
import time
from lib.ssd1306 import SSD1306_I2C
from lib.ui import Time_Display_Painter, Stat_Display_Painter

class Application:
    def __init__(self):
        # SCL -> A5 -> GPIO12, SDA -> A4 -> GPIO11
        self.i2c_time_display = I2C(0, scl=Pin(12), sda=Pin(11))
        # SCL -> A1 -> GPIO2, SDA -> A2 -> GPIO3
        self.i2c_temp_display = I2C(1, scl=Pin(2), sda=Pin(3))

        self.time_display_painter = Time_Display_Painter(SSD1306_I2C(128, 64, self.i2c_time_display))
        self.stat_display_painter = Stat_Display_Painter(SSD1306_I2C(128, 64, self.i2c_temp_display))

    def connect_wifi(self, ssid, password, timeout=10):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        if not wlan.isconnected():
            print(f'Connecting to {ssid}...')
            wlan.connect(ssid, password)
            
            start = time.time()
            while not wlan.isconnected():
                if time.time() - start > timeout:
                    print('Connection timeout!')
                    return False
                time.sleep(0.5)
        
        print('Connected!')
        print('Network config:', wlan.ifconfig())
        return True

    def run(self):
        self.time_display_painter.draw(99, 99)
        self.stat_display_painter.draw(99, 99, "Spandau")
