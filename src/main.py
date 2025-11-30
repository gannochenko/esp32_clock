from machine import Pin, I2C
import ssd1306
import time
from ui import Time_Display_Painter, Stat_Display_Painter

# SCL -> A5 -> GPIO12, SDA -> A4 -> GPIO11
i2c_time_display = I2C(0, scl=Pin(12), sda=Pin(11))
# SCL -> A1 -> GPIO2, SDA -> A2 -> GPIO3
i2c_temp_display = I2C(1, scl=Pin(2), sda=Pin(3))

time_display_painter = Time_Display_Painter(ssd1306.SSD1306_I2C(128, 64, i2c_time_display))
stat_display_painter = Stat_Display_Painter(ssd1306.SSD1306_I2C(128, 64, i2c_temp_display))

current_time = time.localtime()
time_display_painter.draw(current_time[3], current_time[4])
stat_display_painter.draw()
