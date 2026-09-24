import pandas as pd
from analytics.feature_engineering import VehicleFeatureEngineering
from ml.failure_predictor import FailurePredictor

data = pd.read_csv("data/vehicle_telemetry.csv")

data["failure"] = (
    (data["Engine_Temperature"] > 105) &
    (data["Oil_Pressure"] < 2.5) &
    (data["Engine_Vibration"] > 3.0)
).astype(int)

feature_engineering = VehicleFeatureEngineering()

features = feature_engineering.create_features(data)
features = features.dropna()

target = data.loc[features.index, "failure"]

print(features.head())
print(target.head())