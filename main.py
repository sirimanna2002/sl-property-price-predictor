import os
import requests as req

def download_from_drive(file_id, destination):
    URL = "https://drive.google.com/uc?export=download"
    session = req.Session()
    response = session.get(URL, params={"id": file_id}, stream=True)

    token = None
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value

    if token:
        response = session.get(URL, params={"id": file_id, "confirm": token}, stream=True)

    with open(destination, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

MODEL_PATH = "rf_model.pkl"
COLUMNS_PATH = "model_columns.pkl"

if not os.path.exists(MODEL_PATH):
    download_from_drive("1xk63f_MTT3HWCPHmrHSZKIEEer4mh2ly", MODEL_PATH)

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