import subprocess

from modules.cssclasses import CSSClasses
from modules.message import send


def execute(command):
    try:
        response = subprocess.getoutput(command)
        send('msg', [response])
    except Exception:
        send('msg', ['Command could not be executed.'], classes=[CSSClasses.RED])