from analytics.vehicle_analytics import VehicleAnalytics
from repositories.vehicle_repository import VehicleRepository

class VehicleAnalyticsService:

    def __init__(self, analytics: VehicleAnalytics, repository: VehicleRepository):
        self.analytics = analytics
        self.repository = repository

    def get_vehicle_health(self, vehicle_id: str):
        return self.analytics.calculate_health(vehicle_id, 10)

    def get_vehicle(self, vehicle_id: str):
        return self.analytics.get_vehicle(vehicle_id)

    def get_latest_vehicle(self, vehicle_id: str):
        return self.analytics.get_latest_record(vehicle_id)

    def get_previous_vehicle(self, vehicle_id: str):
        return self.analytics.get_previous_records(vehicle_id, 10)

    def get_vehicle_average(self, vehicle_id: str, sensor: str):
        return self.analytics.get_sensor_average(vehicle_id, sensor, 10)

    def compare_vehicle_sensor(self, vehicle_id: str, sensor: str):
        return self.analytics.compare_sensor(vehicle_id, sensor, 10)