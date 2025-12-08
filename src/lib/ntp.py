import ntptime
from lib.state import ApplicationState
from lib.util import throttle

class NTP:
    def __init__(self):
        self.syncDone = False

    # needs wifi to sync
    def act(self, state: ApplicationState):
        if state.wifiConnected:
            if not self.syncDone:
                ntptime.settime()
                self.syncDone = True
        else:
            self.syncDone = False # resync when the wifi is back
