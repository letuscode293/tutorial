from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT_DIR / "models"

CROP_FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

FERT_NUMERIC = ["Temparature", "Humidity ", "Moisture", "Nitrogen", "Potassium", "Phosphorous"]
FERT_CATEGORICAL = ["Soil Type", "Crop Type"]
FERT_FEATURES = FERT_NUMERIC + FERT_CATEGORICAL
