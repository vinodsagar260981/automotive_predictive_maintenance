import pandas as pd

SENSOR_COLUMNS = [
    "engine_rpm",
    "engine_temperature",
    "oil_temperature",
    "oil_pressure",
    "coolant_temperature",
    "battery_voltage",
    "vehicle_speed",
    "fuel_consumption",
    "engine_vibration",
    "brake_temperature",
]

class VehicleAnalytics:

    def __init__(self, repository):
        self.repository = repository

    def get_vehicle(self, vehicle_id: str):

        vehicle = self.repository.get_vehicle(vehicle_id)

        if vehicle.empty:
            raise ValueError(f"Vehicle not found: {vehicle_id}")
        
        return vehicle
    
    def get_latest_record(self, vehicle_id: str):
        
        vehicle = self.get_vehicle(vehicle_id)
        
        return vehicle.iloc[-1]
    
    def get_previous_records(self, vehicle_id: str, window: int = 10):

        vehicle = self.get_vehicle(vehicle_id)

        return vehicle.iloc[:-1].tail(window)
    
    def get_sensor_average(self, vehicle_id: str, sensor: str, window: int = 10):

        previous = self.get_previous_records(vehicle_id, window)

        average = previous[sensor].mean()

        return average
    
    def compare_sensor(self, vehicle_id: str, sensor: str, window: int = 10):

        latest = self.get_latest_record(vehicle_id)
        average = self.get_sensor_average(vehicle_id, sensor, window)

        current = float(latest[sensor])
        average = float(average)

        difference = current - average

        if average != 0:
            change_percent = (difference / average) * 100
        else:
            change_percent = 0

        if change_percent > 10:
            trend = "INCREASING"
        elif change_percent < -10:
            trend = "DECREASING"
        else:
            trend = "STABLE"

        return {
            "sensor": sensor,
            "current_value": round(current, 2),
            "historical_average": round(average, 2),
            "difference": round(difference, 2),
            "change_percent": round(change_percent, 2),
            "trend": trend
        }
        
    def calculate_health(self, vehicle_id: str, window: int = 10):

        risk_points = 0
        sensor_results = []

        for sensor in SENSOR_COLUMNS:

            result = self.compare_sensor(vehicle_id, sensor, window)
            change = abs(result["change_percent"])

            if change > 10:
                risk_points += 1
            if change > 25:
                risk_points += 2
            if change > 50:
                risk_points += 3
                
            sensor_results.append(result)

        if risk_points >= 8:
            health_status = "CRITICAL"
        elif risk_points >= 4:
            health_status = "DEGRADED"
        else:
            health_status = "HEALTHY"

        return {
            "vehicle_id": vehicle_id,
            "risk_points": risk_points,
            "health_status": health_status,
            "sensors": sensor_results
        }