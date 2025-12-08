import machine
import time
from lib.state import ApplicationState

class RTC:
    def __init__(self):
        self.rtc = machine.RTC() # using internal RTC for now

    def get_time(self):
        return self.rtc.datetime()

    # it doesn't need wifi, can run independently
    def act(self, state: ApplicationState):
        rtc_time = self.get_time()
        year, month, day, weekday, hour, minute, second, _ = rtc_time

        # Apply timezone offset (RTC stores UTC time from NTP)
        # Convert to timestamp, add offset in seconds, convert back
        timestamp = time.mktime((year, month, day, hour, minute, second, weekday, 0)) + state.timezoneOffset
        adjusted_time = time.localtime(timestamp)

        state.year = adjusted_time[0]
        state.month = adjusted_time[1]
        state.day = adjusted_time[2]
        state.hour = adjusted_time[3]
        state.minute = adjusted_time[4]
        state.second = adjusted_time[5]