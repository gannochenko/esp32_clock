# settings.py -- Configuration for ESP32 Clock

config = {
    # Display settings
    "display": {
        "type": "ssd1306",  # Options: ssd1306, st7789, ili9341, etc.
        "width": 128,
        "height": 64,
        "i2c_scl": 22,      # I2C SCL pin
        "i2c_sda": 21,      # I2C SDA pin
        "i2c_freq": 400000,
    },

    # RTC settings
    "rtc": {
        "type": "ds3231",   # Options: ds3231, internal, ntp
        "i2c_scl": 22,
        "i2c_sda": 21,
        "timezone": 0,      # UTC offset in hours
    },

    # WiFi settings (for NTP sync)
    "wifi": {
        "enabled": False,
        "ssid": "",
        "password": "",
        "ntp_host": "pool.ntp.org",
    },

    # Clock display format
    "format": {
        "24hour": True,
        "show_seconds": True,
        "show_date": True,
    },
}
