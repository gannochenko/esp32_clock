from machine import Pin, I2C
from lib.ssd1306 import SSD1306_I2C
from lib.ui import Time_Display_Painter, Stat_Display_Painter, Temp_Display_Painter

def get_displays():
    # SCL -> A5 -> GPIO12, SDA -> A4 -> GPIO11
    i2c_time_display = I2C(0, scl=Pin(12), sda=Pin(11))
    # SCL -> A1 -> GPIO2, SDA -> A2 -> GPIO3
    i2c_temp_display = I2C(1, scl=Pin(2), sda=Pin(3))

    time_display_painter = Time_Display_Painter(SSD1306_I2C(128, 64, i2c_time_display))
    stat_display_painter = Temp_Display_Painter(SSD1306_I2C(128, 64, i2c_temp_display))

    return time_display_painter, stat_display_painter
