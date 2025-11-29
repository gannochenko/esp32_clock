from machine import Pin, I2C
import ssd1306
from writer import Writer

def draw_digit(display, digit, x, y, width=12, height=20, thickness=3):
    """
    Draw a large digit using rectangles
    digit: character '0'-'9' or ':'
    x, y: top-left position
    width, height: size of digit
    thickness: line thickness
    """
    
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
    """
    Draw a multi-digit number/time string
    number: string like '20:00' or '1234'
    """
    current_x = x
    for char in str(number):
        draw_digit(display, char, current_x, y, digit_width, digit_height)
        if char == ':':
            current_x += digit_width//2 + spacing  # Colon is narrower
        else:
            current_x += digit_width + spacing

# SCL -> A5 -> GPIO12, SDA -> A4 -> GPIO11
i2c = I2C(0, scl=Pin(12), sda=Pin(11))

devices = i2c.scan()
if devices:
    display = ssd1306.SSD1306_I2C(128, 64, i2c)

    display.fill(0)  # Clear screen
    draw_number(display, '23:59', 10, 20, digit_width=18, digit_height=30)

    display.contrast(10)  # Adjust contrast (0-255)

    # wri = Writer(display, freesans50)

    # # Write text
    # Writer.set_textpos(display, 0, 0)  # Set position (row, col)
    # wri.printstring('20:00')

    # display.text('Hello, World!', 10, 10, 1)
    display.show()
else:
    print("No device found - check connections!")
