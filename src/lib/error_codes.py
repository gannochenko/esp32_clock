class ErrorCodes:
    WIFI_FAILURE = 300
    WIFI_AP_NOT_FOUND = 301
    WIFI_WRONG_PASSWORD = 302
    WIFI_TIMEOUT = 303
    TIMEZONE_FETCH_FAILED = 310
    SHIT_HAPPENED = 400

    def get_error_message(self) -> str:
        return {
            ErrorCodes.WIFI_FAILURE: "Wifi failure",
            ErrorCodes.WIFI_AP_NOT_FOUND: "AP not found",
            ErrorCodes.WIFI_WRONG_PASSWORD: "Wifi wrong password",
            ErrorCodes.WIFI_TIMEOUT: "Wifi conn timeout",
            ErrorCodes.TIMEZONE_FETCH_FAILED: "Timezone fetch fail",
            ErrorCodes.SHIT_HAPPENED: "Shit happened",
        }[self]