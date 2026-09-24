from analytics.feature_engineering import VehicleFeatureEngineering
from ml.anomaly_detector import AnomalyDetector
from ml.failure_predictor import FailurePredictor
from services.llm_service import LLMService
from rag.document_loader import DocumentLoader
from rag.text_splitter import TextSplitter
from rag.vector_store import VectorStore
from rag.retriever import RAGRetriever
import os


class PredictionService:

    def __init__(self, repository):
        self.repository = repository
        self.feature_engineering = VehicleFeatureEngineering()
        self.anomaly_detector = AnomalyDetector()
        self.failure_predictor = FailurePredictor()
        self.llm_service = LLMService()

        loader = DocumentLoader()
        documents = loader.load("knowledge/vibration_diagnostics.txt")

        splitter = TextSplitter()
        chunks = splitter.split(documents)

        vector_store = VectorStore()
        store = vector_store.create(chunks)

        self.retriever = RAGRetriever(store)

    def train(self):
        data = self.repository.get_all_telemetry()

        features = self.feature_engineering.create_features(data)
        features = features.dropna()

        self.anomaly_detector.train(features)

        target = (
            (data.loc[features.index, "engine_temperature"] > 105) &
            (data.loc[features.index, "oil_pressure"] < 2.5) &
            (data.loc[features.index, "engine_vibration"] > 3.0)
        ).astype(int)

        self.failure_predictor.train(features, target)
        self.save_models()

    def predict_vehicle(self, vehicle_id: str):
        data = self.repository.get_vehicle(vehicle_id)

        if data.empty:
            raise ValueError(f"Vehicle not found: {vehicle_id}")

        features = self.feature_engineering.create_features(data)
        features = features.dropna()

        if features.empty:
            raise ValueError("Not enough telemetry data for prediction")

        latest_features = features.iloc[[-1]]

        anomaly = self.anomaly_detector.predict(latest_features)[0]
        failure_probability = self.failure_predictor.predict_probability(latest_features)[0]

        anomaly_status = "NORMAL" if anomaly == 1 else "ANOMALY"

        return {
            "vehicle_id": vehicle_id,
            "anomaly_status": anomaly_status,
            "failure_probability": round(float(failure_probability), 2)
        }

    def explain_prediction(self, vehicle_id: str):
        prediction = self.predict_vehicle(vehicle_id)

        query = f"Vehicle {vehicle_id} has an {prediction['anomaly_status']} status."

        documents = self.retriever.retrieve(query)

        explanation = self.llm_service.explain_prediction(prediction, documents)

        return {
            **prediction,
            "explanation": explanation
        }
        
    def save_models(self):
        os.makedirs("models", exist_ok=True)

        self.anomaly_detector.save("models/anomaly_detector.joblib")
        self.failure_predictor.save("models/failure_predictor.joblib")


    def load_models(self):
        self.anomaly_detector.load("models/anomaly_detector.joblib")
        self.failure_predictor.load("models/failure_predictor.joblib")