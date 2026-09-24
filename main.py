from fastapi import FastAPI, HTTPException, UploadFile, File
from analytics.vehicle_analytics import VehicleAnalytics
from schemas.vehicle import VehicleHealth
from services.vehicle_service import VehicleAnalyticsService
from repositories.vehicle_repository import VehicleRepository
from services.prediction_service import PredictionService
import pandas as pd
from io import BytesIO
from agents.predictive_maintenance_agent import PredictiveMaintenanceAgent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Automotive Predictive Maintenance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATABASE_URL = "postgresql://postgres:django@localhost:5432/automotive_ai"

repository = VehicleRepository(DATABASE_URL)
analytics  = VehicleAnalytics(repository)
vehicle_service = VehicleAnalyticsService(analytics, repository)

#ML
prediction_service = PredictionService(repository)
prediction_service.load_models()

maintenance_agent = PredictiveMaintenanceAgent(prediction_service)

@app.get("/vehicles/{vehicle_id}/prediction")
def get_vehicle_prediction(vehicle_id: str):
    try:
        return prediction_service.predict_vehicle(vehicle_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


#-----------------------------------

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        content = await file.read()

        data = pd.read_csv(BytesIO(content))

        vehicle_service.repository.insert_telemetry(data)

        return {
            "message": "CSV uploaded successfully",
            "rows_inserted": len(data)
        }

    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/vehicles")
def get_vehicles():
    vehicles = repository.get_all_vehicles()
    return {"vehicles": vehicles}


@app.get("/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: str):   
    try:
        vehicle = analytics.get_vehicle(vehicle_id)
        return vehicle.to_dict(orient="records")

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@app.get("/vehicles/{vehicle_id}/latest")
def get_latest_vehicle(vehicle_id: str):
    try:
        latest = analytics.get_latest_record(vehicle_id)
        return latest.to_dict()

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
        
@app.get("/vehicles/{vehicle_id}/previous")
def get_previous_vehicle(vehicle_id: str):
    try:
        previous = analytics.get_previous_records(vehicle_id, window=10)
        return previous.to_dict(orient="records")

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
        
@app.get("/vehicles/{vehicle_id}/sensor_average")
def get_vehicle_average(vehicle_id: str, sensor: str):
    try:
        average = analytics.get_sensor_average(vehicle_id, sensor, 10)
        return {
            "vehicle_id": vehicle_id,
            "sensor": sensor,
            "historical_average": round(average, 2)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error))
        
@app.get("/vehicles/{vehicle_id}/compare")
def compare_vehicle_sensor(vehicle_id: str, sensor: str):
    try:
        result = analytics.compare_sensor(vehicle_id, sensor, 10)
        return result

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@app.get("/vehicles/{vehicle_id}/health", response_model=VehicleHealth)
def get_vehicle_health(vehicle_id: str):
    try:
        result = vehicle_service.get_vehicle_health(vehicle_id)
        return result

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@app.get("/vehicles/{vehicle_id}/explanation")
def get_vehicle_explanation(vehicle_id: str):
    try:
        return prediction_service.explain_prediction(vehicle_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@app.get("/vehicles/{vehicle_id}/agent")
def get_vehicle_agent(vehicle_id: str):
    try:
        return maintenance_agent.run(vehicle_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
@app.post("/models/train")
def train_models():
    try:
        prediction_service.train()
        return {
            "message": "Models trained and saved successfully"
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))