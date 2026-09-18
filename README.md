# GrandHorizon Hotel Bookings Analytics, Batch Audit & ML Suite (v3.0)

An end-to-end, production-grade **Data Science, Machine Learning & Hospitality Operating System** built on the Hotel Booking Demand dataset (119,390 reservations across City and Resort hotels).

---

## 🌟 Platform Capabilities & Features

### 1. 🌍 Geographic Intelligence & Country Risk Matrix *(v3.0)*
- **Global Origin Profiling**: Analyzes guest volume, cancellation rates, and average room rates across 170+ guest origin countries (Portugal, UK, France, Spain, Germany, USA, etc.).
- **Domestic vs. International Risk Split**:
  - **Domestic (Portugal)**: ~40.7% volume, **56.7% cancellation rate** (local transient bookings that easily reschedule).
  - **International Travelers**: ~59.3% volume, **23.6% cancellation rate** (high flight & travel commitment).
- **Interactive Country Search Table**: Live filterable search table with color-coded risk classifications.

### 2. 🛏️ Room Upgrade & Allocation Retention Matrix *(v3.0)*
- **The Upgrade Effect**: Empirically quantifies the retention benefit of room upgrades (`reserved_room_type` vs `assigned_room_type`).
  - **Same Room Assigned**: 41.6% cancellation rate.
  - **Upgraded Room Assigned**: **5.3% cancellation rate** (a **36.3% absolute reduction in cancellations**).
- **Strategic Lever**: Front desks can strategically assign discretionary upgrades to high-risk bookings to lock in guest commitment.

### 3. 🛡️ Automated Guest Retention Playbook & ROI Generator *(v3.0)*
- **Personalized Omnichannel Timelines**: Generates a pre-arrival touchpoint schedule (T-30, T-14, T-7, T-2 days before arrival).
- **Targeted Incentive Allocation**: Suggests optimal perks based on total booking value (e.g. Free parking, dining voucher, or executive lounge pass).
- **Financial ROI Calculation**: Computes expected preserved revenue, cost of incentive, and net ROI multiple (e.g. **4.5x - 8.5x ROI**).

### 4. 📄 One-Click Executive Intelligence Briefing Export *(v3.0)*
- Pinned in the top header: click **"Executive Report"** to open a print-ready, publication-formatted briefing report (`/api/executive-report`).
- Formatted with print media styles for instant PDF export and C-level executive presentations.

### 5. 📁 Batch Reservation CSV Audit & Revenue-at-Risk Engine *(v2.0)*
- **Bulk Risk Scoring**: Upload any CSV file of upcoming reservations for instant ML inference.
- **Revenue at Risk ($)**: Automatically calculates total financial exposure from predicted cancellations (`ADR × Stay Nights`).
- **Overbooking Recommendation**: Advises the exact buffer of rooms the property can safely re-list to maintain 100% occupancy without walking guests.
- **Enriched CSV Export**: One-click download of the audited batch with individual probability scores, risk tiers, and recommended mitigation actions.
- **Built-in Demo Generator**: Includes a one-click sample reservation generator (`GET /api/sample-batch-csv`) for instant testing.

### 6. 🎛️ Dynamic Dashboard Slicers & Global Filters
- Filter all KPIs, monthly demand, lead times, and distributions dynamically by:
  - **Property**: All Properties, City Hotel, or Resort Hotel.
  - **Year**: All Years (2015-2017), 2015, 2016, or 2017.
  - **Market Segment**: Online TA, Direct, Corporate, Groups, Offline TA/TO.

### 7. 📈 Hotel Overbooking & Capacity Optimization Simulator
- Evaluates room capacity, quoted ADR, cancellation rate, and walked-guest penalties across overbooking buffers (0% to 20%).
- Visualizes Gross Revenue, Walk Costs, and Net Expected Profit to pinpoint the **revenue-maximizing buffer** (e.g. +10% overbooking yielding +$4,250 in net gain).

### 8. 💰 Dynamic ADR & Room Pricing Engine
- Evaluates seasonality indices, room tier multipliers (Standard to Presidential Suite), lead-time elasticity (last-minute urgency vs early-bird discounts), and market segments.
- Generates **Target Optimal ADR ($)**, fair pricing bounds `[Min - Max]`, and seasonal revenue strategies.

### 9. 🤖 Zero-Leakage Machine Learning Benchmark
- **Champion Model**: **Random Forest Classifier (83.39% Accuracy | 0.9157 ROC-AUC | 0.7436 F1)**.
- Benchmarked against **Hist Gradient Boosting (84.10% Acc | 0.9143 ROC-AUC)** and **Logistic Regression (81.08% Acc)**.
- **Leakage Prevention**: Strictly dropped post-stay columns (`reservation_status`, `reservation_status_date`).

---

## 📂 Project Structure

```
hotel_bookings project/
├── hotel_bookings.csv                   # Raw dataset (119,390 rows)
├── requirements.txt                     # Dependencies
├── hotel_analysis_notebook.ipynb        # Complete Jupyter Notebook
├── run_all.py                           # Master CLI pipeline runner
├── README.md                            # Complete technical documentation
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py                 # Data cleaning & feature engineering
│   ├── eda_analysis.py                  # Statistical metrics, summaries & room matrix
│   ├── geo_analytics.py                 # Geographic intelligence & country risk tiers
│   ├── retention_playbook.py            # Automated retention timelines & ROI modeling
│   ├── model_trainer.py                 # Multi-model training & benchmarking
│   ├── predictor.py                     # Single & batch inference + revenue at risk
│   └── pricing_engine.py                # Dynamic ADR pricing & room tier multipliers
├── models/
│   ├── best_cancellation_model.joblib   # Serialized champion model
│   └── model_metrics.json               # Benchmark results & feature importances
├── outputs/
│   ├── figures/                         # Generated publication visualization charts
│   └── eda_summary.json                 # Precomputed dataset statistics
└── app/
    ├── main.py                          # FastAPI server & REST endpoints
    ├── templates/
    │   ├── index.html                   # Modern glassmorphic dashboard UI
    │   └── executive_report.html        # Print-ready Executive Briefing document
    └── static/
        ├── css/style.css                # Dark theme aurora mesh styling & animations
        └── js/dashboard.js              # Chart.js frontend, SVG gauge, and live engines
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
| `GET` | `/api/executive-report` | Print-ready, publication-formatted Executive Briefing Document |
| `GET` | `/api/summary` | Dynamic summary metrics (supports `?hotel=...&year=...&market=...`) |
| `GET` | `/api/geo-analytics` | Country-level cancellation rankings & domestic vs international metrics |
| `GET` | `/api/room-matrix` | Room upgrade vs exact room assignment retention advantage |
| `GET` | `/api/model-metrics` | Benchmark metrics (Accuracy, ROC-AUC, F1) & feature importances |
| `GET` | `/api/sample-batch-csv` | Generates & downloads 50 realistic reservations for instant testing |
| `POST` | `/api/predict` | Single reservation cancellation scoring & dynamic pricing guidance |
| `POST` | `/api/retention-playbook` | Generates personalized pre-arrival engagement timeline & ROI |
| `POST` | `/api/predict-batch` | High-speed multipart CSV upload for batch risk & revenue-at-risk audit |
| `POST` | `/api/simulate-overbooking` | Calculates optimal overbooking buffer and incremental revenue curve |
| `GET` | `/api/figures-list` | List of exported publication figures |
