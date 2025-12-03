from lib.util import throttle
import gc

class Housekeeper:
    @throttle(5000)
    def act(self):
        gc.collect()
