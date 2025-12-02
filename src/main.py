from lib.application import Application
from lib.settings import Settings

settings = Settings()
app = Application(settings)
app.run()
