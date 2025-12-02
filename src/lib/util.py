import time

def throttle(interval_ms):
    """Decorator that throttles function execution to once per interval_ms milliseconds"""
    def decorator(func):
        last_run = [0]  # Use list to maintain mutable state in closure

        def wrapper(*args, **kwargs):
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, last_run[0]) >= interval_ms:
                last_run[0] = current_time
                return func(*args, **kwargs)

        return wrapper
    return decorator