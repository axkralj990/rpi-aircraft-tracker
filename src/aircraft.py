from pydantic import BaseModel, Field, field_validator, computed_field
from utils import haversine_distance


class Aircraft(BaseModel):
    latitude: float = Field(alias="lat")
    longitude: float = Field(alias="lon")
    altitude_baro: float | None = Field(default=None, alias="alt_baro")
    altitude_geom: float | None = Field(default=None, alias="alt_geom")  # Made optional
    true_heading: float | None = Field(default=None, alias="true_heading")
    outside_air_temp: float | None = Field(default=None, alias="oat")
    ground_speed: float | None = Field(default=None, alias="gs")
    indicated_airspeed: float | None = Field(default=None, alias="ias")
    mach_number: float | None = Field(default=None, alias="mach")
    flight_number: str | None = Field(default=None, alias="flight")  # Made optional
    registration: str | None = Field(default=None, alias="r")  # Made optional
    aircraft_type: str | None = Field(default=None, alias="t")  # Made optional
    owner_operator: str | None = Field(default=None, alias="ownOp")

    @field_validator("altitude_baro", mode="before")
    @classmethod
    def parse_altitude(cls, v):
        return None if v == "ground" else v

    @computed_field
    @property
    def is_military(self) -> bool:
        return self.owner_operator is not None

    @computed_field
    @property
    def distance_km(self) -> float:
        return haversine_distance(self.latitude, self.longitude)


def parse_aircraft(raw_aircraft: list[dict]) -> list[Aircraft]:
    aircraft = []
    for raw in raw_aircraft:
        aircraft.append(Aircraft.model_validate(raw))

    return sorted(aircraft, key=lambda x: x.distance_km)
