import time

from modules.message import send
from modules.cssclasses import CSSClasses


ERROR_SECONDS_NOT_SPECIFIED = 'Please specify an amount of seconds.'
ERROR_SECONDS_TYPE_WRONG = 'Please specify the amount of seconds correctly.'


def cmd_sleep(parts):
    if len(parts) < 2:
        send('msg', [ERROR_SECONDS_NOT_SPECIFIED], classes=[CSSClasses.RED])

    try:
        sleep_time = float(parts[1])
        time.sleep(sleep_time)
        send('msg', [])
    except TypeError:
        send('msg', [ERROR_SECONDS_TYPE_WRONG], classes=[CSSClasses.RED])
