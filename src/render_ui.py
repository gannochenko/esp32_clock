from lib.application import Application
from lib.settings import Settings
from lib.state import ApplicationState
from lib.displays import get_displays

# use this function to render the UI for debugging purposes, without any other logic
def render_ui():
    state = ApplicationState()
    state.wifiConnected = True
    state.hour = 23
    state.minute = 59
    state.second = 0
    state.day = 31
    state.month = 12
    state.year = 2025
    state.temperature = -99
    state.errorCode = 0
    state.errorExtra = ""
    state.eventCount = 10
    state.messageCount = 20
    state.location = "Berlin"
    state.locationCode = "Europe/Berlin"
    state.latitude = 52.5243700
    state.longitude = 13.4105300
    state.timezoneOffset = 3600

    display1, display2 = get_displays()
    display1.draw(state)
    display2.draw(state)

if __name__ == "__main__":
    render_ui()
