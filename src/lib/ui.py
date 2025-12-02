from lib.writer import Writer
import lib.font6 as font6
import lib.freesans20 as sans20
from lib.constants import DISPLAY_CONTRAST, TEMP_ICON, CLOCK_ICON, LOCATION_ICON
from lib.state import ApplicationState
import random
from lib.error_codes import ErrorCodes

def draw_icon_pixel_by_pixel(display, icon_data, x, y, width=16, height=16):
    """Draw icon pixel-by-pixel from MONO_HLSB format data"""
    for row in range(height):
        byte1 = icon_data[row * 2]
        byte2 = icon_data[row * 2 + 1]
        # Draw first 8 pixels (byte1, LSB first)
        for bit in range(8):
            if byte1 & (1 << bit):
                display.pixel(x + bit, y + row, 1)
        # Draw next 8 pixels (byte2, LSB first)
        for bit in range(8):
            if byte2 & (1 << bit):
                display.pixel(x + 8 + bit, y + row, 1)

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

def draw_text(display, text, x, y):
    writer = Writer(display, font6, verbose=False)
    writer.set_textpos(display, x, y)
    writer.printstring(text)

def draw_text_big(display, text, x, y):
    writer = Writer(display, sans20, verbose=False)
    writer.set_textpos(display, x, y)
    writer.printstring(text)

def draw_icon_text(display, text, icon, x, y):
    draw_icon_pixel_by_pixel(display, icon, y, x)
    draw_text(display, text, x + 1, y + 20)

class Time_Display_Painter:
    def __init__(self, display):
        self.display = display

    def draw(self, state: ApplicationState):
        self.display.fill(0)
        self.display.contrast(DISPLAY_CONTRAST)

        if state.errorCode > 0:
            draw_text_big(self.display, "ERROR", 25, 30)
        else:
            if state.wifiConnected:

                draw_number(self.display, f"{state.hour:02d}:{state.minute:02d}", 12, 10, digit_width=18, digit_height=30, spacing=4)
                draw_text(self.display, f"{state.day:02d} {self.get_month_name(state.month)} {state.year}", 50, 25)
            else:
                draw_text_big(self.display, "Connecting...", 25, 10)

        self.display.show()

    def get_month_name(self, month: int) -> str:
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return month_names[month - 1]

class Stat_Display_Painter:
    def __init__(self, display):
        self.display = display

    def draw(self, state: ApplicationState):
        self.display.fill(0)
        self.display.contrast(DISPLAY_CONTRAST)

        if state.errorCode > 0:
            draw_text(self.display, ErrorCodes.get_error_message(state.errorCode), 10, 10)
            draw_text_big(self.display, f"{state.errorCode}", 25, 40)
            draw_text(self.display, state.errorExtra, 45, 10)
        else:
            if state.wifiConnected:
                offset = 5
                v_grid_step = 20
                draw_icon_text(self.display, f"{state.eventCount} events", TEMP_ICON, offset, offset)
                draw_icon_text(self.display, f"{state.messageCount} messages", CLOCK_ICON, offset + v_grid_step, offset)
                draw_icon_text(self.display, state.location, LOCATION_ICON, offset + v_grid_step * 2, offset)
            else:
                draw_text_big(self.display, "Connecting...", 25, 10)

        self.display.show()

class Temp_Display_Painter:
    def __init__(self, display):
        self.display = display

    def draw(self, state: ApplicationState):
        self.display.fill(0)
        self.display.contrast(DISPLAY_CONTRAST)

        if state.errorCode > 0:
            draw_text_big(self.display, self.get_random_emoji(), 25, 45)
        else:
            draw_text_big(self.display, f"{state.temperature}°C", 25, 50)
        
        self.display.show()

    def get_random_emoji(self) -> str:
        emojis = [">_<", "   :(", "o_O"]
        return emojis[random.randint(0, len(emojis) - 1)]