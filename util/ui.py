from machine import Pin, I2C
import ssd1306
from writer import Writer
import time
import freesans20
import framebuf

# Temperature icon (16x16 thermometer)
TEMP_ICON = bytearray([
    0x00, 0x00, 0xC0, 0x01, 0x20, 0x02, 0x20, 0x02,
    0x20, 0x02, 0x20, 0x02, 0x20, 0x02, 0x20, 0x02,
    0xE0, 0x03, 0x50, 0x05, 0x50, 0x05, 0x50, 0x05,
    0xE0, 0x03, 0xC0, 0x01, 0x00, 0x00, 0x00, 0x00
])

# Clock icon (16x16)
CLOCK_ICON = bytearray([
    0x00, 0x00, 0xF0, 0x07, 0x08, 0x08, 0x04, 0x10,
    0x04, 0x10, 0x82, 0x20, 0x82, 0x20, 0x02, 0x20,
    0x02, 0x20, 0x04, 0x10, 0x04, 0x10, 0x08, 0x08,
    0xF0, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])

LOCATION_ICON = bytearray([
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE0, 0x07, 0x60, 0x06, 0x30, 0x0C, 
    0x30, 0x0C, 0x20, 0x04, 0xE0, 0x07, 0xC0, 0x07, 0xC0, 0x03, 0x80, 0x01, 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])

temp_fb = framebuf.FrameBuffer(TEMP_ICON, 16, 16, framebuf.MONO_HLSB)
clock_fb = framebuf.FrameBuffer(CLOCK_ICON, 16, 16, framebuf.MONO_HLSB)
loc_fb = framebuf.FrameBuffer(LOCATION_ICON, 16, 16, framebuf.MONO_HLSB)

def draw_digit(display, digit, x, y, width=12, height=20, thickness=3):
    # Segment positions (7-segment display style)
    # Top horizontal
    top = (x, y, width, thickness)
    # Middle horizontal
    mid = (x, y + height//2 - thickness//2, width, thickness)
    # Bottom horizontal
    bot = (x, y + height - thickness, width, thickness)
    # Top-left vertical
    tl = (x, y, thickness, height//2)
    # Top-right vertical
    tr = (x + width - thickness, y, thickness, height//2)
    # Bottom-left vertical
    bl = (x, y + height//2, thickness, height//2)
    # Bottom-right vertical
    br = (x + width - thickness, y + height//2, thickness, height//2)
    
    # Define which segments to draw for each digit
    segments = {
        '0': [top, tl, tr, bl, br, bot],
        '1': [tr, br],
        '2': [top, tr, mid, bl, bot],
        '3': [top, tr, mid, br, bot],
        '4': [tl, mid, tr, br],
        '5': [top, tl, mid, br, bot],
        '6': [top, tl, mid, bl, br, bot],
        '7': [top, tr, br],
        '8': [top, tl, tr, mid, bl, br, bot],
        '9': [top, tl, tr, mid, br, bot],
        ':': None  # Special case
    }
    
    if digit == ':':
        # Draw two dots for colon
        dot_size = thickness
        display.fill_rect(x + width//2 - dot_size//2, y + height//3, dot_size, dot_size, 1)
        display.fill_rect(x + width//2 - dot_size//2, y + 2*height//3, dot_size, dot_size, 1)
    elif digit in segments:
        for seg in segments[digit]:
            display.fill_rect(seg[0], seg[1], seg[2], seg[3], 1)

def draw_number(display, number, x, y, digit_width=12, digit_height=20, spacing=2):
    current_x = x
    for char in str(number):
        draw_digit(display, char, current_x, y, digit_width, digit_height)
        current_x += digit_width + spacing

class Time_Display_Painter:
    def __init__(self, display):
        self.display = display

    def draw(self, hour, minute):
        self.display.fill(0)
        self.display.contrast(10)
        draw_number(self.display, f"{hour:02d}:{minute:02d}", 12, 20, digit_width=18, digit_height=30, spacing=4)
        self.display.show()

class Temp_Display_Painter:
    def __init__(self, display):
        self.display = display
        self.writer = Writer(self.display, freesans20)

    def draw(self, temp):
        sign = " " if temp >= 0 else ""

        self.display.fill(0)
        self.display.contrast(10)
        self.writer.set_textpos(self.display, 0, 0)  # top left
        # self.writer.printstring(f"{sign}{temp} grad")
        self.display.blit(loc_fb, 10, 10)    # Draw at position (0, 0)
        # self.display.blit(clock_fb, 10, 34)
        self.display.show()

# SCL -> A5 -> GPIO12, SDA -> A4 -> GPIO11
i2c_time_display = I2C(0, scl=Pin(12), sda=Pin(11))
# SCL -> A1 -> GPIO2, SDA -> A2 -> GPIO3
i2c_temp_display = I2C(1, scl=Pin(2), sda=Pin(3))

time_display_painter = Time_Display_Painter(ssd1306.SSD1306_I2C(128, 64, i2c_time_display))
temp_display_painter = Temp_Display_Painter(ssd1306.SSD1306_I2C(128, 64, i2c_temp_display))

current_time = time.localtime()
time_display_painter.draw(current_time[3], current_time[4])
temp_display_painter.draw(-99)
