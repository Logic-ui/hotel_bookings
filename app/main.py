"""
FastAPI Application for Hotel Bookings Analytics, Batch Audit, and Revenue Optimization Suite.
Extended in v3.0 with Geographic Intelligence, Retention Playbook Generator, and Executive Briefing Export.
"""

import os
import io
import json
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from src.predictor import BookingCancellationPredictor
from src.pricing_engine import DynamicPricingEngine
from src.eda_analysis import get_filtered_summary, get_cached_df
from src.geo_analytics import analyze_geographic_distribution
from src.retention_playbook import GuestRetentionPlaybookGenerator

app = FastAPI(
    title="Hotel Bookings Intelligence & Prediction Suite",
    description="Data Analysis, Business Intelligence, Batch Risk Audit, and Revenue Optimization Engine",
    version="3.0.0"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")
FIGURES_DIR = os.path.join(BASE_DIR, "outputs", "figures")
METRICS_JSON = os.path.join(BASE_DIR, "models", "model_metrics.json")
CSV_PATH = os.path.join(BASE_DIR, "hotel_bookings.csv")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/figures", StaticFiles(directory=FIGURES_DIR), name="figures")

_predictor_instance = None
_pricing_engine = DynamicPricingEngine()
_retention_generator = GuestRetentionPlaybookGenerator()


def get_predictor():
    global _predictor_instance
    if _predictor_instance is None:
        model_path = os.path.join(BASE_DIR, "models", "best_cancellation_model.joblib")
        if not os.path.exists(model_path):
            raise RuntimeError("Model artifact not found. Please train models first.")
        _predictor_instance = BookingCancellationPredictor(model_path)
    return _predictor_instance


class BookingRequest(BaseModel):
    hotel: str = Field(default="City Hotel")
    lead_time: int = Field(default=45, ge=0, le=1000)
    arrival_date_month: str = Field(default="July")
    stays_in_weekend_nights: int = Field(default=1, ge=0)
    stays_in_week_nights: int = Field(default=2, ge=0)
    adults: int = Field(default=2, ge=1)
    children: int = Field(default=0, ge=0)
    market_segment: str = Field(default="Online TA")
    deposit_type: str = Field(default="No Deposit")
    reserved_room_type: str = Field(default="A")
    customer_type: str = Field(default="Transient")
    adr: float = Field(default=105.0, ge=0.0)
    required_car_parking_spaces: int = Field(default=0, ge=0)
    total_of_special_requests: int = Field(default=1, ge=0)
    previous_cancellations: int = Field(default=0, ge=0)
    is_repeated_guest: int = Field(default=0, ge=0, le=1)


class OverbookingSimRequest(BaseModel):
    hotel_capacity: int = Field(default=250, ge=10, le=5000)
    adr: float = Field(default=110.0, ge=10.0)
    expected_cancellation_rate: float = Field(default=35.0, ge=0.0, le=95.0)
    walked_guest_cost: float = Field(default=180.0, ge=0.0)


class RetentionPlaybookRequest(BaseModel):
    booking_data: Dict[str, Any]
    cancellation_probability: float = Field(default=50.0, ge=0.0, le=100.0)


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse("<h1>Dashboard HTML under construction</h1>")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/executive-report", response_class=HTMLResponse)
async def serve_executive_report():
    """Serves print-ready, publication-formatted Executive Hospitality Intelligence Briefing."""
    report_path = os.path.join(TEMPLATES_DIR, "executive_report.html")
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Executive report template not found.")
    with open(report_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/summary")
async def get_summary(
    hotel: Optional[str] = Query(None),
    year: Optional[str] = Query(None),
    market: Optional[str] = Query(None)
):
    try:
        data = get_filtered_summary(hotel=hotel, year=year, market_segment=market)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/geo-analytics")
async def get_geo_analytics():
    """Returns country-level cancellation rankings and domestic vs international metrics."""
    try:
        df = get_cached_df()
        geo_data = analyze_geographic_distribution(df)
        return geo_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/room-matrix")
async def get_room_matrix():
    """Returns room upgrade vs exact room assignment retention advantage."""
    try:
        df = get_cached_df()
        summary = get_filtered_summary()
        return summary.get('room_allocation_matrix', {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/model-metrics")
async def get_model_metrics():
    if not os.path.exists(METRICS_JSON):
        raise HTTPException(status_code=404, detail="Model metrics not found.")
    with open(METRICS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/figures-list")
async def get_figures_list():
    if not os.path.exists(FIGURES_DIR):
        return {"figures": []}
    files = [f for f in os.listdir(FIGURES_DIR) if f.endswith(('.png', '.jpg'))]
    return {"figures": sorted(files)}


@app.post("/api/predict")
async def predict_cancellation(booking: BookingRequest):
    try:
        predictor = get_predictor()
        input_data = booking.model_dump()
        result = predictor.predict_booking(input_data)
        
        # Include dynamic pricing recommendation
        pricing = _pricing_engine.recommend_rate(input_data)
        result['pricing_recommendation'] = pricing

        # Include retention playbook
        playbook = _retention_generator.generate_playbook(input_data, result['cancellation_probability'])
        result['retention_playbook'] = playbook

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/retention-playbook")
async def get_retention_playbook(req: RetentionPlaybookRequest):
    """Generates structured omnichannel engagement sequence and calculates retention ROI."""
    try:
        playbook = _retention_generator.generate_playbook(req.booking_data, req.cancellation_probability)
        return playbook
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predict-batch")
async def predict_batch_reservations(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df_upload = pd.read_csv(io.BytesIO(contents))
        
        predictor = get_predictor()
        batch_results = predictor.predict_batch(df_upload)
        return batch_results
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV file: {str(e)}")


@app.get("/api/sample-batch-csv")
async def get_sample_batch_csv():
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df_raw = pd.read_csv(CSV_PATH)
    sample_df = df_raw.sample(n=50, random_state=101).copy()
    
    cols_to_drop = ['reservation_status', 'reservation_status_date', 'is_canceled']
    cols_to_drop = [c for c in cols_to_drop if c in sample_df.columns]
    sample_df = sample_df.drop(columns=cols_to_drop)

    stream = io.StringIO()
    sample_df.to_csv(stream, index=False)
    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=sample_upcoming_reservations.csv"
    return response


@app.post("/api/simulate-overbooking")
async def simulate_overbooking(req: OverbookingSimRequest):
    cap = req.hotel_capacity
    adr = req.adr
    c_rate = req.expected_cancellation_rate / 100.0
    walk_cost = req.walked_guest_cost

    rates = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]
    curve = []

    for r in rates:
        bookings_taken = int(round(cap * (1.0 + r)))
        expected_shows = bookings_taken * (1.0 - c_rate)
        occupied = min(expected_shows, cap)
        walked = max(0.0, expected_shows - cap)

        revenue = occupied * adr
        penalty = walked * walk_cost
        net_revenue = revenue - penalty
        occupancy_pct = round((occupied / cap) * 100, 1)

        curve.append({
            'overbooking_rate_pct': int(r * 100),
            'bookings_accepted': bookings_taken,
            'expected_shows': round(expected_shows, 1),
            'occupied_rooms': round(occupied, 1),
            'occupancy_pct': occupancy_pct,
            'walked_guests': round(walked, 1),
            'gross_revenue': round(revenue, 2),
            'walk_penalty': round(penalty, 2),
            'net_expected_revenue': round(net_revenue, 2)
        })

    optimal = max(curve, key=lambda x: x['net_expected_revenue'])
    baseline = curve[0]
    incremental_revenue = optimal['net_expected_revenue'] - baseline['net_expected_revenue']

    return {
        'optimal_overbooking_rate_pct': optimal['overbooking_rate_pct'],
        'optimal_bookings_to_accept': optimal['bookings_accepted'],
        'expected_occupancy_pct': optimal['occupancy_pct'],
        'net_revenue_at_optimal': optimal['net_expected_revenue'],
        'baseline_net_revenue': baseline['net_expected_revenue'],
        'incremental_revenue_gain': round(incremental_revenue, 2),
        'curve': curve
    }
