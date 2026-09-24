from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class MaintenanceState(TypedDict):
    vehicle_id: str
    prediction: dict
    documents: list
    explanation: str


class PredictiveMaintenanceAgent:

    def __init__(self, prediction_service):
        self.prediction_service = prediction_service

        graph = StateGraph(MaintenanceState)

        graph.add_node("predict", self.predict)
        graph.add_node("retrieve", self.retrieve)
        graph.add_node("explain", self.explain)

        graph.add_edge(START, "predict")
        graph.add_edge("predict", "retrieve")
        graph.add_edge("retrieve", "explain")
        graph.add_edge("explain", END)

        self.graph = graph.compile()

    def predict(self, state: MaintenanceState):
        prediction = self.prediction_service.predict_vehicle(
            state["vehicle_id"]
        )

        return {
            "prediction": prediction
        }

    def retrieve(self, state: MaintenanceState):
        prediction = state["prediction"]

        query = f"Vehicle {state['vehicle_id']} has an {prediction['anomaly_status']} status."

        documents = self.prediction_service.retriever.retrieve(query)

        return {
            "documents": documents
        }

    def explain(self, state: MaintenanceState):
        explanation = self.prediction_service.llm_service.explain_prediction(
            state["prediction"],
            state["documents"]
        )

        return {
            "explanation": explanation
        }

    def run(self, vehicle_id: str):
        result = self.graph.invoke({
            "vehicle_id": vehicle_id
        }) # type: ignore

        return {
            **result["prediction"],
            "explanation": result["explanation"]
        }