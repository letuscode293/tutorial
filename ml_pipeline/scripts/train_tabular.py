"""Reproducible training for tabular models (crop + fertilizer)."""
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "datasets")
MODELS = os.path.join(ROOT, "models")
os.makedirs(MODELS, exist_ok=True)


def train_crop():
    df = pd.read_csv(os.path.join(DATA, "Crop_recommendation.csv"))
    X = df.drop("label", axis=1)
    le = LabelEncoder()
    y = le.fit_transform(df["label"])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train_s, y_train)
    acc = accuracy_score(y_test, model.predict(scaler.transform(X_test)))
    joblib.dump(model, os.path.join(MODELS, "crop_recommendation_model.pkl"))
    joblib.dump(scaler, os.path.join(MODELS, "crop_scaler.pkl"))
    joblib.dump(le, os.path.join(MODELS, "crop_label_encoder.pkl"))
    print(f"Crop model accuracy: {acc:.4f}")


def train_fertilizer():
    df = pd.read_csv(os.path.join(DATA, "Fertilizer_Prediction.csv"))
    cols = ["Temparature", "Humidity ", "Moisture", "Soil Type", "Crop Type",
            "Nitrogen", "Potassium", "Phosphorous"]
    X = df[cols].copy()
    encoders = {}
    for col in ["Soil Type", "Crop Type"]:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
    y_le = LabelEncoder()
    y = y_le.fit_transform(df["Fertilizer Name"])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train_s, y_train)
    acc = accuracy_score(y_test, model.predict(scaler.transform(X_test)))
    joblib.dump(model, os.path.join(MODELS, "fertilizer_recommendation_model.pkl"))
    joblib.dump(scaler, os.path.join(MODELS, "fert_scaler.pkl"))
    joblib.dump(y_le, os.path.join(MODELS, "fert_label_encoder.pkl"))
    joblib.dump(encoders, os.path.join(MODELS, "fert_categorical_encoders.pkl"))
    print(f"Fertilizer model accuracy: {acc:.4f}")


if __name__ == "__main__":
    train_crop()
    train_fertilizer()
