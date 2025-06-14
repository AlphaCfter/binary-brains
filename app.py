from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
import joblib
import numpy as np
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:8080"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


model = joblib.load("random_forest_model.pkl")

WAQI_API_TOKEN = "4037b40c52a901a191eee5575b9986c3c1a473da"

def fetch_pollutants(city):
    """Fetch real-time pollutant data from WAQI API."""
    url = f"http://api.waqi.info/feed/{city}/?token={WAQI_API_TOKEN}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "ok":
        pollutants = data["data"]["iaqi"]

        pm25 = pollutants.get("pm25", {}).get("v", 0)
        no = pollutants.get("no", {}).get("v", 0)
        no2 = pollutants.get("no2", {}).get("v", 0)
        co = pollutants.get("co", {}).get("v", 0)
        so2 = pollutants.get("so2", {}).get("v", 0)
        benzene = pollutants.get("benzene", {}).get("v", 0)
        toluene = pollutants.get("toluene", {}).get("v", 0)

        return np.array([[co, pm25, toluene, no2, benzene, so2, no]])
    
    return None

@app.get("/predict/")
def predict_aqi(city: str):
    try:
        input_data = fetch_pollutants(city)

        if input_data is None:
            return {"error": "Could not fetch AQI data for the given city."}

        predicted_aqi = model.predict(input_data)[0] / 2  
        return {
            "city": city,
            "predicted_aqi": float(predicted_aqi) 
        }

    except Exception as e:
        return {"error": str(e)}
