from pydantic import BaseModel


class SensorAnalysis(BaseModel):
    sensor: str
    current_value: float
    historical_average: float
    difference: float
    change_percent: float
    trend: str


class VehicleHealth(BaseModel):
    vehicle_id: str
    risk_points: int
    health_status: str
    sensors: list[SensorAnalysis]