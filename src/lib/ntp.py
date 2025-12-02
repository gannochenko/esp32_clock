import ntptime
from lib.state import ApplicationState
from lib.util import throttle

class NTP:
    def __init__(self):
        self.initialSyncDone = False

    def act(self, state: ApplicationState):
        if state.wifiConnected:
            if not self.initialSyncDone:
                ntptime.settime()
                self.initialSyncDone = True
            else:
                self.resync()

    @throttle(1000 * 60 * 60 * 12) # 12 hours
    def resync(self):
        ntptime.settime()
