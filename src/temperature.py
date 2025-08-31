import requests
from tenacity import retry, stop_after_attempt


@retry(stop=stop_after_attempt(3))
def get_latest_room_temperature():
    response = requests.get("http://raspberrypi.local:8000/temperatures/latest")

    if response.ok:
        return response.json()["temperature_c"]
