class ApplicationState:
    def __init__(self):
        self.wifiConnected: bool = False
        self.eventCount: int = 0
        self.messageCount: int = 0
        self.location: str = "Spandau"
        self.hour: int = 0
        self.minute: int = 0
        self.day: int = 0
        self.month: int = 0
        self.year: int = 2025
        self.temperature: int = 0
        self.errorCode: int = 0
        self.errorExtra: str = ""
