"""
FastAPI Application for Hotel Bookings Analytics & Live Risk Prediction Dashboard.
"""

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from src.predictor import BookingCancellationPredictor

app = FastAPI(
    title="Hotel Bookings Intelligence & Prediction Suite",
    description="Data Analysis, Business Intelligence, and Machine Learning Churn/Cancellation Risk Engine",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")
FIGURES_DIR = os.path.join(BASE_DIR, "outputs", "figures")
SUMMARY_JSON = os.path.join(BASE_DIR, "outputs", "eda_summary.json")
METRICS_JSON = os.path.join(BASE_DIR, "models", "model_metrics.json")

# Ensure required directories exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# Mount static files and figures
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/figures", StaticFiles(directory=FIGURES_DIR), name="figures")

# Lazy-loaded predictor singleton
_predictor_instance = None


def get_predictor():
    global _predictor_instance
    if _predictor_instance is None:
        model_path = os.path.join(BASE_DIR, "models", "best_cancellation_model.joblib")
        if not os.path.exists(model_path):
            raise RuntimeError("Model artifact not found. Please train models first.")
        _predictor_instance = BookingCancellationPredictor(model_path)
    return _predictor_instance


class BookingRequest(BaseModel):
    hotel: str = Field(default="City Hotel", description="Resort Hotel or City Hotel")
    lead_time: int = Field(default=45, ge=0, le=1000)
    arrival_date_month: str = Field(default="July")
    arrival_date_week_number: Optional[int] = 28
    arrival_date_day_of_month: Optional[int] = 15
    stays_in_weekend_nights: int = Field(default=1, ge=0)
    stays_in_week_nights: int = Field(default=2, ge=0)
    adults: int = Field(default=2, ge=1)
    children: int = Field(default=0, ge=0)
    babies: int = Field(default=0, ge=0)
    meal: str = Field(default="BB")
    country: Optional[str] = "PRT"
    market_segment: str = Field(default="Online TA")
    distribution_channel: Optional[str] = "TA/TO"
    is_repeated_guest: int = Field(default=0, ge=0, le=1)
    previous_cancellations: int = Field(default=0, ge=0)
    previous_bookings_not_canceled: int = Field(default=0, ge=0)
    reserved_room_type: str = Field(default="A")
    deposit_type: str = Field(default="No Deposit")
    customer_type: str = Field(default="Transient")
    adr: float = Field(default=105.0, ge=0.0)
    required_car_parking_spaces: int = Field(default=0, ge=0)
    total_of_special_requests: int = Field(default=1, ge=0)


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse("<h1>Dashboard HTML under construction</h1>")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/summary")
async def get_summary():
    """Returns precomputed exploratory data analysis statistics."""
    if not os.path.exists(SUMMARY_JSON):
        raise HTTPException(status_code=404, detail="EDA summary not generated yet.")
    with open(SUMMARY_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/model-metrics")
async def get_model_metrics():
    """Returns machine learning model benchmarking results and feature importances."""
    if not os.path.exists(METRICS_JSON):
        raise HTTPException(status_code=404, detail="Model metrics not found.")
    with open(METRICS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/figures-list")
async def get_figures_list():
    """Returns list of all available high-res figure images in outputs/figures."""
    if not os.path.exists(FIGURES_DIR):
        return {"figures": []}
    files = [f for f in os.listdir(FIGURES_DIR) if f.endswith(('.png', '.jpg'))]
    return {"figures": sorted(files)}


@app.post("/api/predict")
async def predict_cancellation(booking: BookingRequest):
    """Real-time cancellation probability scoring and risk diagnostics."""
    try:
        predictor = get_predictor()
        input_data = booking.model_dump()
        result = predictor.predict_booking(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
