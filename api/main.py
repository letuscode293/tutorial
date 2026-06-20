from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    CropRequest,
    CropResponse,
    FertilizerRequest,
    FertilizerResponse,
    HealthResponse,
)
from api.services.model_registry import registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry.load_all()
    yield


app = FastAPI(
    title="CropAI API",
    description="Crop & fertilizer recommendation API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", models_loaded=registry.status)


@app.post("/predict/crop", response_model=CropResponse)
def predict_crop(body: CropRequest):
    try:
        crop, confidence = registry.predict_crop(body.model_dump())
        return CropResponse(crop=crop, confidence=confidence)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/predict/fertilizer", response_model=FertilizerResponse)
def predict_fertilizer(body: FertilizerRequest):
    features = {
        "Temparature": body.temperature,
        "Humidity ": body.humidity,
        "Moisture": body.moisture,
        "Soil Type": body.soil_type,
        "Crop Type": body.crop_type,
        "Nitrogen": body.nitrogen,
        "Potassium": body.potassium,
        "Phosphorous": body.phosphorous,
    }
    try:
        fertilizer, confidence = registry.predict_fertilizer(features)
        return FertilizerResponse(fertilizer=fertilizer, confidence=confidence)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
