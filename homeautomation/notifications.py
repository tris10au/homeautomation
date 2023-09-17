import os
import requests


PUSHOVER_API = os.environ.get("PUSHOVER_TOKEN")
PUSHOVER_USER = os.environ.get("PUSHOVER_USER")


def send(title, message=None):
    requests.post("https://api.pushover.net/1/messages.json", json={
        "token": PUSHOVER_API,
        "user": PUSHOVER_USER,
        "title": "Power: " + title,
        "message": title if message is None else message
    })

