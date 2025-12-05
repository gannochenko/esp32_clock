class ApplicationState:
    def __init__(self):
        self.wifiConnected: bool = False
        self.wifiIpAddress: str = ""
        self.eventCount: int = 0
        self.messageCount: int = 0
        self.location: str = "Spandau" # this is temporary
        self.locationCode: str = "Europe/Berlin"
        self.latitude: float = 0
        self.longitude: float = 0
        self.timezoneOffset: int = 3600 # default to +1 hour (Berlin winter time) in seconds
        self.hour: int = 0
        self.minute: int = 0
        self.second: int = 0
        self.day: int = 0
        self.month: int = 0
        self.year: int = 2025
        self.temperature: int = 0
        self.errorCode: int = 0
        self.errorExtra: str = ""
