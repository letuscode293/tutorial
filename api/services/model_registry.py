from dataclasses import dataclass, field

import joblib
import numpy as np

from api.config import CROP_FEATURES, FERT_FEATURES, MODELS_DIR


@dataclass
class ModelRegistry:
    crop_model: object | None = None
    crop_scaler: object | None = None
    crop_encoder: object | None = None
    fert_model: object | None = None
    fert_scaler: object | None = None
    fert_encoder: object | None = None
    fert_cat_encoders: dict | None = None
    errors: dict[str, str] = field(default_factory=dict)

    def load_all(self) -> None:
        self._load_crop()
        self._load_fertilizer()

    def _load_crop(self) -> None:
        try:
            self.crop_model = joblib.load(MODELS_DIR / "crop_recommendation_model.pkl")
            self.crop_scaler = joblib.load(MODELS_DIR / "crop_scaler.pkl")
            self.crop_encoder = joblib.load(MODELS_DIR / "crop_label_encoder.pkl")
        except Exception as exc:
            self.errors["crop"] = str(exc)

    def _load_fertilizer(self) -> None:
        try:
            self.fert_model = joblib.load(MODELS_DIR / "fertilizer_recommendation_model.pkl")
            self.fert_scaler = joblib.load(MODELS_DIR / "fert_scaler.pkl")
            self.fert_encoder = joblib.load(MODELS_DIR / "fert_label_encoder.pkl")
            self.fert_cat_encoders = joblib.load(MODELS_DIR / "fert_categorical_encoders.pkl")
        except Exception as exc:
            self.errors["fertilizer"] = str(exc)

    @property
    def status(self) -> dict[str, bool]:
        return {
            "crop": self.crop_model is not None,
            "fertilizer": self.fert_model is not None,
        }

    def predict_crop(self, features: dict) -> tuple[str, float]:
        if not self.crop_model:
            raise RuntimeError(self.errors.get("crop", "Crop model not loaded"))
        row = np.array([[features[k] for k in CROP_FEATURES]])
        scaled = self.crop_scaler.transform(row)
        proba = self.crop_model.predict_proba(scaled)[0]
        idx = int(np.argmax(proba))
        return self.crop_encoder.classes_[idx], float(proba[idx])

    def predict_fertilizer(self, features: dict) -> tuple[str, float]:
        if not self.fert_model:
            raise RuntimeError(self.errors.get("fertilizer", "Fertilizer model not loaded"))
        row = features.copy()
        for col, encoder in self.fert_cat_encoders.items():
            row[col] = encoder.transform([row[col]])[0]
        matrix = np.array([[row[k] for k in FERT_FEATURES]])
        scaled = self.fert_scaler.transform(matrix)
        proba = self.fert_model.predict_proba(scaled)[0]
        idx = int(np.argmax(proba))
        return self.fert_encoder.classes_[idx], float(proba[idx])


registry = ModelRegistry()
