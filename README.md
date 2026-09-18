# GrandHorizon Hotel Bookings Data Analysis & Cancellation Prediction Suite

An end-to-end, production-grade **Data Science & Machine Learning** project built on the Hotel Booking Demand dataset (119,390 reservations across City and Resort hotels).

---

## 🌟 Project Highlights

1. **Exploratory Data Analysis & Business Intelligence**:
   - Comprehensive data cleaning: handles missing values in `children`, `country`, `agent`, and `company`.
   - Eliminates anomalous records (zero-guest bookings, extreme ADR outliers like $5,400 and negative rates).
   - Unveils critical hospitality dynamics:
     - **Cancellation Gap**: City Hotels experience higher cancellations (~41.7%) than Resort Hotels (~27.8%).
     - **Lead Time Dynamics**: Cancellation likelihood escalates dramatically past 90 days lead time (>55% for 180+ days).
     - **The "Deposit Paradox"**: Explains why Non-Refundable reservations had high cancellation rates in raw data (agency tour group bulk holds).
     - **Guest Engagement Signal**: Guests with 2+ special requests cancel 60% less frequently.
     - **Seasonality & Pricing**: Summer peak volume (July/August) aligns with maximum ADR (~$125/night).
   - Generates 8 publication-quality visualizations (`outputs/figures/`).

2. **Machine Learning Pipeline (Zero Data Leakage)**:
   - Evaluates and benchmarks:
     - **Histogram-based Gradient Boosting (`HistGradientBoostingClassifier`)** [Champion]
     - **Random Forest Classifier (`RandomForestClassifier`)**
     - **Logistic Regression (`LogisticRegression`)**
   - **Zero Target Leakage Safeguard**: Strictly drops post-booking status columns (`reservation_status`, `reservation_status_date`) so models only learn from pre-stay signals.
   - Comprehensive evaluation: Accuracy, Precision, Recall, F1-Score, ROC-AUC curve, Confusion Matrix, and Feature Importances.
   - Serialized fitted pipeline saved to `models/best_cancellation_model.joblib`.

3. **Interactive Web Dashboard & Live Risk Simulator**:
   - Modern, responsive, glassmorphic UI powered by **FastAPI** & **Chart.js**.
   - Executive KPI cards and interactive charts for monthly demand, lead times, and market segments.
   - **Live What-If Prediction Form**: Input custom booking parameters (lead time, room type, deposit type, special requests, ADR) to receive real-time cancellation probability, risk tier badges, key risk drivers, and actionable hotel mitigation strategies.
   - Publication Figures Gallery.

4. **Reproducible Notebook**:
   - Step-by-step Jupyter Notebook (`hotel_analysis_notebook.ipynb`) for academic or data science review.

---

## 📂 Project Structure

```
hotel_bookings project/
├── hotel_bookings.csv                   # Raw dataset (119,390 rows, 32 columns)
├── requirements.txt                     # Python dependencies
├── hotel_analysis_notebook.ipynb        # Comprehensive Jupyter Notebook
├── run_all.py                           # Master end-to-end execution script
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py                 # Cleaning, anomaly filtering & feature engineering
│   ├── eda_analysis.py                  # Statistical metrics, summaries & figure generator
│   ├── model_trainer.py                 # Multi-model training, benchmarking & serialization
│   └── predictor.py                     # Inference engine & business recommendation generator
├── models/
│   ├── best_cancellation_model.joblib   # Trained champion pipeline
│   └── model_metrics.json               # Benchmark results & feature importances
├── outputs/
│   ├── figures/                         # Generated high-resolution visualization charts
│   └── eda_summary.json                 # Precomputed statistics for instant dashboard loading
└── app/
    ├── main.py                          # FastAPI application & REST endpoints
    ├── templates/
    │   └── index.html                   # Modern glassmorphism dashboard UI
    └── static/
        ├── css/style.css                # Dark theme styling, glassmorphism & animations
        └── js/dashboard.js              # Chart.js rendering, KPIs, and live prediction engine
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full Analytics & ML Pipeline
Execute data preprocessing, EDA figure generation, and model training:
```bash
python run_all.py
```

### 3. Launch the Interactive Web Dashboard
```bash
python -m uvicorn app.main:app --reload --port 8000
```
Open your browser at **http://127.0.0.1:8000**.

---

## 📊 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Interactive analytics and prediction dashboard |
| `GET` | `/api/summary` | Precomputed dataset KPIs, monthly trends & distributions |
| `GET` | `/api/model-metrics` | Multi-model benchmark metrics & top feature importances |
| `GET` | `/api/figures-list` | List of generated publication figures |
| `POST` | `/api/predict` | Real-time cancellation risk scoring and recommendation engine |

### Example Prediction Request (`POST /api/predict`):
```json
{
  "hotel": "City Hotel",
  "lead_time": 120,
  "arrival_date_month": "August",
  "stays_in_weekend_nights": 1,
  "stays_in_week_nights": 3,
  "adults": 2,
  "children": 0,
  "market_segment": "Online TA",
  "deposit_type": "No Deposit",
  "adr": 125.0,
  "total_of_special_requests": 0,
  "previous_cancellations": 1,
  "is_repeated_guest": 0
}
```

### Example Prediction Response:
```json
{
  "cancellation_probability": 72.4,
  "will_cancel_prediction": true,
  "risk_tier": "High Risk",
  "risk_color": "#ef4444",
  "risk_badge": "danger",
  "key_drivers": [
    "Extended lead time (120 days) significantly amplifies cancellation risk.",
    "Guest profile has 1 previous cancellations.",
    "Zero special requests submitted, reflecting low initial engagement."
  ],
  "recommended_actions": [
    "Trigger automated guest engagement & itinerary check-in 30 and 14 days before arrival.",
    "Require credit card pre-authorization or refundable deposit for room hold.",
    "Offer complimentary upgrade options or personalized amenities to increase engagement."
  ]
}
```
