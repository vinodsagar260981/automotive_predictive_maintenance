from sklearn.ensemble import RandomForestClassifier
import joblib


class FailurePredictor:

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def train(self, features, target):
        self.model.fit(features, target)

    def predict(self, features):
        return self.model.predict(features)

    def predict_probability(self, features):
        return self.model.predict_proba(features)[:, 1]

    def save(self, path):
        joblib.dump(self.model, path)

    def load(self, path):
        self.model = joblib.load(path)