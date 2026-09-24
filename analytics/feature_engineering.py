import pandas as pd


class VehicleFeatureEngineering:

    def create_features(self, data: pd.DataFrame):
        features = pd.DataFrame()

        features["engine_temperature"] = data["engine_temperature"]
        features["oil_pressure"] = data["oil_pressure"]
        features["engine_vibration"] = data["engine_vibration"]
        features["battery_voltage"] = data["battery_voltage"]

        features["temperature_average"] = data["engine_temperature"].rolling(10).mean()
        features["vibration_average"] = data["engine_vibration"].rolling(10).mean()

        features["temperature_deviation"] = data["engine_temperature"] - features["temperature_average"]
        features["vibration_deviation"] = data["engine_vibration"] - features["vibration_average"]

        return features