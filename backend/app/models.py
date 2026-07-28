from pydantic import BaseModel
from datetime import datetime

class AircraftState(BaseModel):
    icao24: str
    callsign: str | None
    origin_country: str
    time_position: datetime | None
    last_contact: datetime
    longitude: float | None
    latitude: float | None
    barometric_altitude: float | None
    on_ground: bool
    velocity: float | None
    true_track: float | None
    vertical_rate: float | None
    sensors: list[int] | None
    geo_altitude: float | None
    position_source: int

class PredictedPoint(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    t_offset_s: int # secondes dans le futur

class TrajectoryPrediction(BaseModel):
    icao24: str
    predicted_points: list[PredictedPoint]

class ConflictAlert(BaseModel):
    icao24_1: str
    icao24_2: str
    time_to_conflict_s: int
    horizontal_dist_nm: float
    vertical_dist_ft: float
    severity: str  # "warning", "critical"
    detected_at: datetime
