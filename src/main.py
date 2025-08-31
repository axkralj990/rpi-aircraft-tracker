from fetch import fetch_aircraft_within_radius
from aircraft import parse_aircraft
from temperature import get_latest_room_temperature

raw_ac = fetch_aircraft_within_radius(radius=100)

if raw_ac is None:
    raise SystemExit("No aircraft data fetched.")

aircraft = parse_aircraft(raw_ac)
for ac in aircraft:
    print("=======")
    print(ac)
    print("=======")
    break
print(get_latest_room_temperature())
