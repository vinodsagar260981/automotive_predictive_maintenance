from sklearn.ensemble import IsolationForest
import joblib


class AnomalyDetector:

    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)

    def train(self, features):
        self.model.fit(features)

    def predict(self, features):
        return self.model.predict(features)

    def save(self, path):
        joblib.dump(self.model, path)

    def load(self, path):
        self.model = joblib.load(path)