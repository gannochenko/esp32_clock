import machine
from lib.state import ApplicationState

class RTC:
    def __init__(self):
        self.rtc = machine.RTC() # using internal RTC for now

    def get_time(self):
        return self.rtc.datetime()

    def act(self, state: ApplicationState):
        time = self.get_time()
        year, month, day, weekday, hour, minute, second, _ = time
        state.hour = hour
        state.minute = minute
        state.day = day
        state.month = month
        state.year = year