from machine import Pin, I2C
import ssd1306

# SCL -> A5 -> GPIO12, SDA -> A4 -> GPIO11
i2c = I2C(0, scl=Pin(12), sda=Pin(11))

devices = i2c.scan()
if devices:
    print("I2C device found at:", [hex(device) for device in devices])
    display = ssd1306.SSD1306_I2C(128, 64, i2c)
    display.text('Hello, World!', 10, 10, 1)
    display.show()
else:
    print("No device found - check connections!")
