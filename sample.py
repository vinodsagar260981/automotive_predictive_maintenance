from analytics.feature_engineering import VehicleFeatureEngineering
from ml.anomaly_detector import AnomalyDetector
import pandas as pd

data = pd.read_csv("data/vehicle_telemetry.csv")

feature_engineering = VehicleFeatureEngineering()
features = feature_engineering.create_features(data)
features = features.dropna()

detector = AnomalyDetector()
detector.train(features)

predictions = detector.predict(features)

features["anomaly"] = predictions

print(features.head())