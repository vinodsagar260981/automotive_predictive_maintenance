import psycopg
import pandas as pd

class VehicleRepository:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def get_vehicle(self, vehicle_id: str):
        with psycopg.connect(self.db_url) as connection:
            return pd.read_sql("SELECT * FROM vehicle_telemetry WHERE vehicle_id = %s ORDER BY timestamp", connection, params=(vehicle_id,)) # type: ignore

    def get_all_vehicles(self):
        with psycopg.connect(self.db_url) as connection:
            return pd.read_sql("SELECT DISTINCT vehicle_id FROM vehicle_telemetry", connection)["vehicle_id"].tolist() # type: ignore

    def insert_telemetry(self, data: pd.DataFrame):
        with psycopg.connect(self.db_url) as connection:
            with connection.cursor() as cursor:
                for _, row in data.iterrows():
                    cursor.execute("""
                        INSERT INTO vehicle_telemetry (
                            vehicle_id,
                            timestamp,
                            engine_rpm,
                            engine_temperature,
                            oil_temperature,
                            oil_pressure,
                            coolant_temperature,
                            battery_voltage,
                            vehicle_speed,
                            fuel_consumption,
                            engine_vibration,
                            brake_temperature
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row["Vehicle_ID"],
                        row["Timestamp"],
                        row["Engine_RPM"],
                        row["Engine_Temperature"],
                        row["Oil_Temperature"],
                        row["Oil_Pressure"],
                        row["Coolant_Temperature"],
                        row["Battery_Voltage"],
                        row["Vehicle_Speed"],
                        row["Fuel_Consumption"],
                        row["Engine_Vibration"],
                        row["Brake_Temperature"]
                    ))
                    
    def get_all_telemetry(self):
        with psycopg.connect(self.db_url) as connection:
            return pd.read_sql(
                "SELECT * FROM vehicle_telemetry ORDER BY vehicle_id, timestamp",
                connection # type: ignore
            )