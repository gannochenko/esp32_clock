from lib.application import Application
from lib.settings import Settings

def main():
    settings = Settings()
    app = Application(settings)
    app.run()

if __name__ == "__main__":
    main()
