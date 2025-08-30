from config import LAT, LON
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (requests.ConnectionError, requests.Timeout, requests.HTTPError)
    ),
)
def fetch_aircraft_within_radius(radius: float) -> list[dict] | None:
    url = f"https://api.airplanes.live/v2/point/{LAT}/{LON}/{radius}"

    response = requests.get(url)

    if response.ok:
        return response.json()["ac"]
    else:
        print("Error with the API")
