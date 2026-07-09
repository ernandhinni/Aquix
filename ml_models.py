from pathlib import Path

import joblib
import numpy as np
import pandas as pd


class MLModels:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.model_dir = self.base_dir / "trained_models"
        self.models = self._load_models()

    def _load_models(self):
        models = {}
        if not self.model_dir.exists():
            return models

        for path in self.model_dir.glob("*.joblib"):
            try:
                models[path.stem] = joblib.load(path)
            except Exception:
                continue
        return models

    def _predict(self, model_name, overrides):
        artifact = self.models.get(model_name)
        if not artifact:
            return None

        features = artifact.get("features", [])
        row = {feature: overrides.get(feature, np.nan) for feature in features}
        prediction = artifact["pipeline"].predict(pd.DataFrame([row], columns=features))[0]

        label_encoder = artifact.get("label_encoder")
        if label_encoder is not None:
            return label_encoder.inverse_transform([int(prediction)])[0]
        return float(prediction)

    def predict_demand(self, temperature, humidity, population_density, rainfall, user_type):
        prediction = self._predict("india_rainfall", {
            "Actual Rainfall: JUN": rainfall,
            "Actual Rainfall: JUL": rainfall + humidity,
            "Actual Rainfall: AUG": rainfall,
            "Actual Rainfall: SEPT": temperature,
            "Departure Percentage: JUN": humidity - 60,
            "Departure Percentage: JUL": population_density,
        })
        demand = prediction if prediction is not None else temperature * 8 + humidity * 1.5
        return {"demand_lpd": round(float(demand), 2), "user_type": user_type}

    def predict_leak(self, pressure, flow, turbidity):
        prediction = self._predict("water_leak_status", {
            "Pressure (bar)": pressure,
            "Flow Rate (L/s)": flow,
            "Temperature (°C)": 25,
            "Burst Status": 0,
        })
        leak = int(prediction) if prediction is not None else int(flow > 80 or pressure < 1.5)
        return {
            "leak_detected": bool(leak),
            "risk_score": round(min(max(flow / 100 + turbidity / 200, 0), 1), 3),
        }

    def predict_flood(self, monsoon_intensity, topography_drainage, river_management, deforestation):
        score = float(np.mean([monsoon_intensity, topography_drainage, river_management, deforestation]))
        prediction = self._predict("flood_train", {
            "MonsoonIntensity": monsoon_intensity,
            "TopographyDrainage": topography_drainage,
            "RiverManagement": river_management,
            "Deforestation": deforestation,
            "Urbanization": score,
            "ClimateChange": score,
            "DrainageSystems": max(10 - score, 0),
        })
        probability = prediction if prediction is not None else score / 10
        return {"flood_probability": round(float(probability), 3)}

    def predict_potability(self, data):
        prediction = self._predict("water_potability", {
            "ph": float(data.get("ph", 7)),
            "Hardness": float(data.get("hardness", 200)),
            "Solids": float(data.get("solids", 15000)),
            "Chloramines": float(data.get("chloramines", 7)),
            "Sulfate": float(data.get("sulfate", 330)),
            "Conductivity": float(data.get("conductivity", 400)),
            "Organic_carbon": float(data.get("organic_carbon", 14)),
            "Trihalomethanes": float(data.get("trihalomethanes", 65)),
            "Turbidity": float(data.get("turbidity", 4)),
        })
        potable = int(prediction) if prediction is not None else int(6.5 <= float(data.get("ph", 7)) <= 8.5)
        return {"potable": bool(potable)}

    def predict_crop(self, data):
        prediction = self._predict("crop_recommendation", {
            "N": float(data.get("N", 90)),
            "P": float(data.get("P", 40)),
            "K": float(data.get("K", 40)),
            "temperature": float(data.get("temperature", 25)),
            "humidity": float(data.get("humidity", 70)),
            "ph": float(data.get("ph", 6.5)),
            "rainfall": float(data.get("rainfall", 120)),
        })
        return {"crop": prediction or "rice"}
