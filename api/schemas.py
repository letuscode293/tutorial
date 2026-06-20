from typing import Literal

from pydantic import BaseModel, Field


class CropRequest(BaseModel):
    N: float = Field(..., ge=0, le=140, example=90)
    P: float = Field(..., ge=0, le=145, example=42)
    K: float = Field(..., ge=0, le=205, example=43)
    temperature: float = Field(..., example=20.88)
    humidity: float = Field(..., ge=0, le=100, example=82.0)
    ph: float = Field(..., ge=0, le=14, example=6.5)
    rainfall: float = Field(..., ge=0, example=202.9)


class CropResponse(BaseModel):
    crop: str
    confidence: float


class FertilizerRequest(BaseModel):
    temperature: float = Field(..., example=26)
    humidity: float = Field(..., example=52)
    moisture: float = Field(..., example=38)
    soil_type: Literal["Black", "Clayey", "Loamy", "Red", "Sandy"] = Field(..., example="Sandy")
    crop_type: Literal[
        "Barley", "Cotton", "Ground Nuts", "Maize", "Millets",
        "Oil seeds", "Paddy", "Pulses", "Sugarcane", "Tobacco", "Wheat",
    ] = Field(..., example="Maize")
    nitrogen: float = Field(..., example=37)
    potassium: float = Field(..., example=0)
    phosphorous: float = Field(..., example=0)


class FertilizerResponse(BaseModel):
    fertilizer: str
    confidence: float


class HealthResponse(BaseModel):
    status: str
    models_loaded: dict[str, bool]
