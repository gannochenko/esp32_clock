from lib.writer import Writer
import lib.font6 as font6
import lib.freesans20 as sans20
from lib.constants import DISPLAY_CONTRAST, EMAIL_ICON, CALENDAR_ICON, LOCATION_ICON, RAIN_ICON, SNOW_ICON, SUN_ICON, WIFI_ERROR_ICON, WIFI_ICON
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

def draw_glyph(display, glyph, x, y, width=12, height=20, thickness=3):
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
        '-': [mid],
        'C': [top, tl, bl, bot],
        '°': [top, tl, tr, mid],
        ':': None  # Special case
    }
    
    if glyph == ':':
        # Draw two dots for colon
        dot_size = thickness
        display.fill_rect(x + width//2 - dot_size//2, y + height//3, dot_size, dot_size, 1)
        display.fill_rect(x + width//2 - dot_size//2, y + 2*height//3, dot_size, dot_size, 1)
    elif glyph in segments:
        for seg in segments[glyph]:
            display.fill_rect(seg[0], seg[1], seg[2], seg[3], 1)

def draw_number(display, number, x, y, digit_width=12, digit_height=20, spacing=2):
    current_x = x
    for char in str(number):
        draw_glyph(display, char, current_x, y, digit_width, digit_height)
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
            second_even = state.second % 2 == 0
            render_wifi = state.wifiConnected or state.wifiError

            date_offset = 0 if render_wifi else 10
            
            # Show colon on even seconds, hide on odd seconds (like real digital clocks)
            separator = ":" if second_even else " "
            draw_number(self.display, f"{state.hour:02d}{separator}{state.minute:02d}", 12, 10, digit_width=18, digit_height=30, spacing=4)
            draw_text(self.display, f"{state.day:02d} {self.get_month_name(state.month)} {state.year}", 50, 14 + date_offset)
            if state.wifiConnected:
                if second_even:
                    draw_icon_pixel_by_pixel(self.display, WIFI_ICON, 100, 46)
            elif state.wifiError:
                draw_icon_pixel_by_pixel(self.display, WIFI_ERROR_ICON, 100, 46)

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
            offset = 5
            v_grid_step = 20
            tz_offset_hours = state.timezoneOffset / 3600
            tz_sign = "+" if tz_offset_hours >= 0 else "-"

            draw_icon_text(self.display, f"{state.eventCount} events", CALENDAR_ICON, offset, offset)
            draw_icon_text(self.display, f"{state.messageCount} messages", EMAIL_ICON, offset + v_grid_step, offset)
            draw_icon_text(self.display, f"{state.location} U{tz_sign}{tz_offset_hours}", LOCATION_ICON, offset + v_grid_step * 2, offset)

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
            sign = " " if state.temperature >= 0 else "-"
            temperature = abs(state.temperature)
            draw_number(self.display, f"{sign}{temperature:02d}°C", 25, 10, digit_width=12, digit_height=18, spacing=4)

            offset = 25
            margin = 15
            draw_icon_pixel_by_pixel(self.display, SUN_ICON, offset, 40)
            draw_icon_pixel_by_pixel(self.display, RAIN_ICON, offset + margin + 16, 40)
            draw_icon_pixel_by_pixel(self.display, SNOW_ICON, offset + (margin + 16) * 2, 40)
        
        self.display.show()

    def get_random_emoji(self) -> str:
        emojis = [">_<", "   :(", "o_O"]
        return emojis[random.randint(0, len(emojis) - 1)]