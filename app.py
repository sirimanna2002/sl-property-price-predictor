import streamlit as st
import pandas as pd
import joblib
import os
import gdown

# ---------- Load model (auto-download from Drive if not present) ----------
MODEL_PATH = "rf_model.pkl"
COLUMNS_PATH = "model_columns.pkl"

if not os.path.exists(MODEL_PATH):
    gdown.download(id="1xk63f_MTT3HWCPHmrHSZKIEEer4mh2ly", output=MODEL_PATH, quiet=False)

model = joblib.load(MODEL_PATH)
model_columns = joblib.load(COLUMNS_PATH)

st.set_page_config(
    page_title="SL Property Price Predictor",
    page_icon="🏠",
    layout="centered"
)

# ---------- Custom styling ----------
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        max-width: 780px;
    }
    .hero {
        background: linear-gradient(135deg, #1E3A5F 0%, #2E5A8F 100%);
        padding: 2.5rem 2rem;
        border-radius: 18px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(30,58,95,0.25);
    }
    .hero-icon { font-size: 3rem; }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: white;
        margin: 0.3rem 0 0.4rem 0;
    }
    .hero-subtitle {
        color: #CBD9E8;
        font-size: 1rem;
    }
    .section-label {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1E3A5F;
        margin: 1.5rem 0 0.8rem 0;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #1E3A5F 0%, #2E5A8F 100%);
        color: white;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 0.75rem 1.2rem;
        border-radius: 10px;
        border: none;
        width: 100%;
        box-shadow: 0 4px 14px rgba(30,58,95,0.3);
        transition: 0.2s;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(30,58,95,0.4);
        color: white;
    }
    .result-box {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 2px solid #10B981;
        border-radius: 16px;
        padding: 1.8rem;
        text-align: center;
        margin-top: 1.5rem;
        box-shadow: 0 6px 18px rgba(16,185,129,0.15);
    }
    .result-label {
        color: #065F46;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .result-price {
        font-size: 2.6rem;
        font-weight: 900;
        color: #047857;
        margin-top: 0.3rem;
    }
    .footer-note {
        text-align: center;
        color: #9CA3AF;
        font-size: 0.85rem;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Hero header ----------
st.markdown("""
    <div class="hero">
        <div class="hero-icon">🏠</div>
        <div class="hero-title">Sri Lankan Property Price Predictor</div>
        <div class="hero-subtitle">AI-powered price estimates for houses, land & apartments across Sri Lanka</div>
    </div>
""", unsafe_allow_html=True)

# ---------- Input form ----------
st.markdown('<div class="section-label">🏷️ Property Type & Location</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    property_type = st.selectbox("Property Type", ["House", "Land", "Apartment"])
with col2:
    district = st.selectbox("District", [
        "Colombo", "Gampaha", "Kalutara", "Kurunegala", "Galle",
        "Kandy", "Matara", "Hambantota", "Anuradhapura", "Ratnapura"
    ])

st.markdown('<div class="section-label">📐 Size Details</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    land_perches = st.number_input("Land Size (perches)", min_value=0.0, value=10.0)
with col4:
    floor_area_sqft = st.number_input("Floor Area (sqft)", min_value=0.0, value=1500.0)

st.markdown('<div class="section-label">🛏️ Rooms</div>', unsafe_allow_html=True)
col5, col6 = st.columns(2)
with col5:
    bedrooms = st.number_input("Bedrooms", min_value=0, value=3)
with col6:
    bathrooms = st.number_input("Bathrooms", min_value=0, value=2)

st.markdown('<div class="section-label">📋 Land Type (for Land only)</div>', unsafe_allow_html=True)
land_type = st.selectbox("Select land type", ["Residential", "Commercial", "Agricultural"], label_visibility="collapsed")

st.write("")

# ---------- Predict button ----------
if st.button("🔍 Predict Price"):
    input_dict = {
        "land_perches": land_perches,
        "floor_area_sqft": floor_area_sqft,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "is_residential": 1 if land_type == "Residential" else 0,
        "is_commercial": 1 if land_type == "Commercial" else 0,
        "is_agricultural": 1 if land_type == "Agricultural" else 0,
    }

    for col in model_columns:
        if col.startswith("property_type_"):
            input_dict[col] = 1 if col == f"property_type_{property_type}" else 0
        elif col.startswith("district_"):
            input_dict[col] = 1 if col == f"district_{district}" else 0

    input_df = pd.DataFrame([input_dict])[model_columns]
    log_pred = model.predict(input_df)[0]
    price = (2.71828 ** log_pred) - 1