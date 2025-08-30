import math
from config import LAT, LON


def haversine_distance(lat: float, lon: float) -> float:
    R = 6371

    lat1_rad = math.radians(lat)
    lon1_rad = math.radians(lon)
    lat2_rad = math.radians(LAT)
    lon2_rad = math.radians(LON)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return R * c
