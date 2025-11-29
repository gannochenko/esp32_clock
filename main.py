# main.py -- ESP32 Clock Application
import time
import machine
from src.lib.display import Display
from src.lib.rtc import RTCManager
from src.config.settings import config

def main():
    """Main application loop for ESP32 clock"""
    print("Starting ESP32 Clock...")

    # Initialize components
    display = Display(config)
    rtc = RTCManager(config)

    # Main loop
    try:
        while True:
            # Get current time from RTC
            current_time = rtc.get_time()

            # Update display
            display.show_time(current_time)

            # Sleep for 1 second
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nClock stopped by user")
        display.clear()
    except Exception as e:
        print(f"Error: {e}")
        display.clear()
    finally:
        print("Cleaning up...")
        machine.reset()

if __name__ == "__main__":
    main()
