import os

import requests
import streamlit as st

API_URL = os.getenv("CROP_AI_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="CropAI", page_icon="🌾", layout="wide")
st.title("CropAI")
st.caption("Crop & fertilizer recommendations — powered by FastAPI")


def api_post(path, **kwargs):
    try:
        return requests.post(f"{API_URL}{path}", **kwargs)
    except requests.Timeout:
        return None


try:
    with st.spinner("Connecting to API..."):
        health = requests.get(f"{API_URL}/health", timeout=15).json()
    loaded = health.get("models_loaded", {})
    cols = st.columns(2)
    cols[0].metric("Crop model", "Ready" if loaded.get("crop") else "Missing")
    cols[1].metric("Fertilizer model", "Ready" if loaded.get("fertilizer") else "Missing")
except requests.RequestException:
    st.error(f"Cannot reach API at `{API_URL}`. Start it with: `uvicorn api.main:app --reload`")
    st.stop()

tab1, tab2 = st.tabs(["Crop Recommendation", "Fertilizer Recommendation"])

with tab1:
    st.subheader("Soil & climate parameters")
    c1, c2 = st.columns(2)
    with c1:
        n = st.slider("Nitrogen (N)", 0, 140, 90)
        p = st.slider("Phosphorus (P)", 0, 145, 42)
        k = st.slider("Potassium (K)", 0, 205, 43)
        ph = st.slider("pH", 0.0, 14.0, 6.5)
    with c2:
        temperature = st.slider("Temperature (°C)", 0.0, 50.0, 20.9)
        humidity = st.slider("Humidity (%)", 0.0, 100.0, 82.0)
        rainfall = st.slider("Rainfall (mm)", 0.0, 300.0, 202.9)
    if st.button("Recommend crop", key="crop"):
        payload = {
            "N": n, "P": p, "K": k, "temperature": temperature,
            "humidity": humidity, "ph": ph, "rainfall": rainfall,
        }
        with st.spinner("Model is processing your soil & climate data…"):
            r = api_post("/predict/crop", json=payload, timeout=30)
        if r is None:
            st.warning("Request timed out. Is the API running?")
        elif r.ok:
            data = r.json()
            st.success(f"Plant **{data['crop']}** ({data['confidence']:.1%} confidence)")
        else:
            st.error(r.json().get("detail", r.text))

with tab2:
    st.subheader("Fertilizer recommendation")
    c1, c2 = st.columns(2)
    with c1:
        temperature = st.number_input("Temperature", 0, 50, 26)
        humidity = st.number_input("Humidity", 0, 100, 52)
        moisture = st.number_input("Moisture", 0, 100, 38)
        soil_type = st.selectbox("Soil type", ["Sandy", "Loamy", "Black", "Red", "Clayey"])
    with c2:
        crop_type = st.selectbox(
            "Crop type",
            ["Maize", "Wheat", "Cotton", "Sugarcane", "Barley", "Paddy", "Pulses",
             "Millets", "Tobacco", "Ground Nuts", "Oil seeds"],
        )
        nitrogen = st.number_input("Nitrogen", 0, 50, 37)
        potassium = st.number_input("Potassium", 0, 50, 0)
        phosphorous = st.number_input("Phosphorous", 0, 50, 0)
    if st.button("Recommend fertilizer", key="fert"):
        payload = {
            "temperature": temperature, "humidity": humidity, "moisture": moisture,
            "soil_type": soil_type, "crop_type": crop_type,
            "nitrogen": nitrogen, "potassium": potassium, "phosphorous": phosphorous,
        }
        with st.spinner("Model is processing your fertilizer inputs…"):
            r = api_post("/predict/fertilizer", json=payload, timeout=30)
        if r is None:
            st.warning("Request timed out. Is the API running?")
        elif r.ok:
            data = r.json()
            st.success(f"Use **{data['fertilizer']}** ({data['confidence']:.1%} confidence)")
        else:
            st.error(r.json().get("detail", r.text))
