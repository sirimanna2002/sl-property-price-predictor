import os
import requests as req

MODEL_PATH = "rf_model.pkl"
COLUMNS_PATH = "model_columns.pkl"

MODEL_URL = "https://github.com/sirimanna2002/sl-property-price-predictor/releases/download/v1.0/rf_model.pkl"

if not os.path.exists(MODEL_PATH):
    r = req.get(MODEL_URL, stream=True)
    with open(MODEL_PATH, "wb") as f:
        for chunk in r.iter_content(32768):
            if chunk:
                f.write(chunk)

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

model = joblib.load("rf_model.pkl")
model_columns = joblib.load("model_columns.pkl")

app = FastAPI()

class PropertyInput(BaseModel):
    property_type: str    # "House", "Land", "Apartment"
    district: str          # "Colombo", "Gampaha" etc
    land_perches: float = 0
    floor_area_sqft: float = 0
    bedrooms: float = 0
    bathrooms: float = 0
    is_residential: int = 0
    is_commercial: int = 0
    is_agricultural: int = 0

@app.get("/")
def home():
    return {"message": "Property price predictor API is running"}

@app.post("/predict")
def predict(data: PropertyInput):
    input_dict = {
        "land_perches": data.land_perches,
        "floor_area_sqft": data.floor_area_sqft,
        "bedrooms": data.bedrooms,
        "bathrooms": data.bathrooms,
        "is_residential": data.is_residential,
        "is_commercial": data.is_commercial,
        "is_agricultural": data.is_agricultural,
    }

    for col in model_columns:
        if col.startswith("property_type_"):
            input_dict[col] = 1 if col == f"property_type_{data.property_type}" else 0
        elif col.startswith("district_"):
            input_dict[col] = 1 if col == f"district_{data.district}" else 0

    input_df = pd.DataFrame([input_dict])[model_columns]

    log_pred = model.predict(input_df)[0]
    price = (2.71828 ** log_pred) - 1

    return {"predicted_price": round(price)}