from pydantic import BaseModel, Field, field_validator, computed_field
from utils import haversine_distance
from enum import StrEnum

priority_registrations = ["s5b", "puma", "s5", "toruk", "l4", "l9", "l6"]
priority_types = ["pc9", "c130", "c17", "ef2000", "f16", "pc6", "at8t", "z78", "f35"]


class DisplayPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


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
    def display_priority(self) -> bool:
        if self.registration:
            reg_lower = self.registration.lower()
            if any(reg_lower.startswith(pr) for pr in priority_registrations):
                return DisplayPriority.HIGH

        if self.flight_number:
            flight_lower = self.flight_number.lower()
            if any(flight_lower.startswith(pr) for pr in priority_registrations):
                return DisplayPriority.HIGH

        if self.aircraft_type:
            type_lower = self.aircraft_type.lower()
            if any(pt in type_lower for pt in priority_types):
                return DisplayPriority.HIGH

        if self.owner_operator is not None:
            return DisplayPriority.HIGH

        if self.altitude_baro is not None and self.altitude_baro < 10000:
            if self.distance_km is not None and self.distance_km < 20:
                return DisplayPriority.HIGH

        if self.altitude_baro is not None and self.altitude_baro < 30000:
            if self.distance_km is not None and self.distance_km < 50:
                return DisplayPriority.MEDIUM

        return DisplayPriority.LOW

    @computed_field
    @property
    def distance_km(self) -> float:
        return haversine_distance(self.latitude, self.longitude)


def parse_aircraft(raw_aircraft: list[dict]) -> list[Aircraft]:
    aircraft = []
    for raw in raw_aircraft:
        aircraft.append(Aircraft.model_validate(raw))

    return sorted(aircraft, key=lambda x: x.distance_km)
