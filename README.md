# GrandHorizon Hotel Bookings Data Analysis, Batch Audit & ML Prediction Suite (v2.0)

An end-to-end, production-grade **Data Science, Machine Learning & Revenue Optimization** platform built on the Hotel Booking Demand dataset (119,390 reservations across City and Resort hotels).

---

## 🌟 Platform Capabilities & Features

### 1. 📁 Batch Reservation CSV Audit & Revenue at Risk *(NEW)*
- **Bulk Risk Scoring**: Upload any CSV file of upcoming reservations for instant machine learning inference.
- **Revenue at Risk ($)**: Automatically calculates total financial exposure from predicted cancellations (`ADR × Stay Nights`).
- **Overbooking Recommendation**: Advises the exact buffer of rooms the property can safely re-list to reach 100% occupancy without walking guests.
- **Enriched CSV Export**: One-click download of the audited batch with individual probability scores, risk tiers, and recommended mitigation actions.
- **Built-in Demo Generator**: Includes a one-click sample reservation generator (`GET /api/sample-batch-csv`) for instant testing.

### 2. 🎛️ Dynamic Dashboard Slicers & Multi-Dimensional EDA *(NEW)*
- **Interactive Global Filters**: Filter all KPIs, monthly demand, lead times, and distributions by:
  - **Property**: All Properties, City Hotel, or Resort Hotel.
  - **Year**: All Years (2015-2017), 2015, 2016, or 2017.
  - **Market Segment**: Online TA, Direct, Corporate, Groups, Offline TA/TO.
- **Zero-Latency In-Memory Slicing**: Recomputes metrics and re-renders Chart.js visualizations instantaneously without full page reloads.

### 3. 📈 Hotel Overbooking & Capacity Optimization Simulator *(NEW)*
- **Mathematical Optimization Model**: Evaluates room capacity, quoted ADR, cancellation rate, and walked-guest penalties across overbooking buffers (0% to 20%).
- **Interactive Financial Curve**: Visualizes Gross Revenue, Walk Costs, and Net Expected Profit to pinpoint the **revenue-maximizing buffer** (e.g. +10% overbooking yielding +$4,250 in incremental revenue).

### 4. 💰 Dynamic ADR & Room Pricing Engine *(NEW)*
- Evaluates seasonality indices, room tier multipliers (Standard to Presidential Suite), lead-time elasticity (last-minute urgency vs early-bird discounts), and market segments.
- Generates **Target Optimal ADR ($)**, fair pricing bounds `[Min - Max]`, and seasonal revenue strategies.

### 5. 🤖 Zero-Leakage Machine Learning Benchmark
- **Champion Model**: **Random Forest Classifier (83.39% Accuracy | 0.9157 ROC-AUC | 0.7436 F1)**.
- Benchmarked against **Hist Gradient Boosting (84.10% Acc | 0.9143 ROC-AUC)** and **Logistic Regression (81.08% Acc)**.
- **Leakage Prevention**: Strictly dropped post-stay columns (`reservation_status`, `reservation_status_date`) to ensure genuine pre-arrival predictive validity.
- Serialized fitted pipeline stored in `models/best_cancellation_model.joblib`.

### 6. 📊 Publication Figures & Jupyter Notebook
- 8 high-resolution publication charts in `outputs/figures/`.
- Step-by-step reproducible notebook in `hotel_analysis_notebook.ipynb`.

---

## 📂 Project Architecture

```
hotel_bookings project/
├── hotel_bookings.csv                   # Raw dataset (119,390 rows)
├── requirements.txt                     # Dependencies
├── hotel_analysis_notebook.ipynb        # Complete Jupyter Notebook
├── run_all.py                           # Master end-to-end execution script
├── README.md                            # Comprehensive technical documentation
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py                 # Data cleaning & feature engineering
│   ├── eda_analysis.py                  # Statistical metrics, summaries & dynamic slicer
│   ├── model_trainer.py                 # Multi-model training & benchmarking
│   ├── predictor.py                     # Single & batch inference + revenue at risk
│   └── pricing_engine.py                # Dynamic ADR pricing & room tier multipliers
├── models/
│   ├── best_cancellation_model.joblib   # Serialized champion model
│   └── model_metrics.json               # Benchmark results & feature importances
├── outputs/
│   ├── figures/                         # Generated high-resolution visualization charts
│   └── eda_summary.json                 # Precomputed dataset statistics
└── app/
    ├── main.py                          # FastAPI application & REST endpoints
    ├── templates/index.html             # Modern responsive dashboard UI
    └── static/
        ├── css/style.css                # Dark theme glassmorphism styling
        └── js/dashboard.js              # Chart.js frontend & interactive engines
```

---

## 🚀 Quick Start

### 1. Run Pipeline & Train Models
```bash
python run_all.py
```

### 2. Launch Interactive Web Platform
```bash
python -m uvicorn app.main:app --reload --port 8000
```
Open **http://127.0.0.1:8000** in your browser.

---

## 📊 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main interactive web dashboard |
| `GET` | `/api/summary` | Dynamic summary metrics (supports `?hotel=...&year=...&market=...`) |
| `GET` | `/api/model-metrics` | Benchmark metrics (Accuracy, ROC-AUC, F1) & feature importances |
| `GET` | `/api/sample-batch-csv` | Generates & downloads 50 realistic reservations for instant testing |
| `POST` | `/api/predict` | Single reservation cancellation scoring & dynamic pricing guidance |
| `POST` | `/api/predict-batch` | High-speed multipart CSV upload for batch risk & revenue-at-risk audit |
| `POST` | `/api/simulate-overbooking` | Calculates optimal overbooking buffer and incremental revenue curve |
| `GET` | `/api/figures-list` | List of exported publication figures |
