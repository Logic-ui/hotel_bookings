# GrandHorizon Hotel Bookings Analytics, Batch Audit & ML Suite (v4.0)

An end-to-end, production-grade **Data Science, Machine Learning & Hospitality Operating System** built on the Hotel Booking Demand dataset (119,390 reservations across City and Resort hotels).

---

## 🌟 Platform Capabilities & Features

### 1. 🔀 Distribution Channel Net Yield & Intermediary Commission Optimizer *(v4.0)*
- **Gross vs. Net ADR**: Quantifies true room revenue by deducting distributor commission drag across Online Travel Agencies (18% OTAs like Expedia/Booking.com), Offline Tour Operators (12%), Corporate (5%), and Direct booking (0%).
- **Effective Realized Yield**: Calculates net revenue earned per reservation attempt taking both cancellation churn and commission deductions into account.
- **Direct Booking Shift Simulator**: Interactively models shifting 1% to 35% of OTA booking volume to direct brand channels, calculating exact commission dollars saved, cancellations avoided, and net profit expansion after marketing costs.

### 2. 👑 Guest Loyalty, LTV & VIP Persona Segmentation Engine *(v4.0)*
- **RFM-H Behavioral Cohorts**: Segments all 119k+ guests into 6 actionable profiles:
  - *Platinum VIP Champions*: Repeat guests with zero cancellation history (14% cancel rate, top upgrade candidates).
  - *High-Value Luxury Leisure*: High ADR guests booking Suites and Deluxe rooms.
  - *Corporate Road Warriors*: Predictable mid-week corporate stays with low cancellation volatility.
  - *Family & Group Leisure*: High stay duration, multi-guest configurations.
  - *Speculative Churn Risk*: Extended lead time, no deposit, past cancellation history (>60% cancel rate).
  - *Standard Transient*: Independent leisure and retail guests.
- **Interactive Guest LTV & Concierge Protocol Calculator**: Real-time 3-year discounted Customer Lifetime Value (LTV) calculator producing loyalty tiers (Platinum VIP, Gold, Silver, Bronze), front-desk welcoming scripts, and personalized VIP amenity allocations.

### 3. 🧪 Interactive What-If Policy Scenario Sandbox *(v4.0)*
- **Proactive Policy Testing**: Evaluates portfolio-level revenue and churn impacts before enforcing real-world property policy changes:
  - *Policy 1: Long Lead-Time Deposit Mandate*: Requires deposits on reservations booked >60 days in advance (reduces speculative churn by ~32%).
  - *Policy 2: Discretionary Room Upgrade Allocation*: Strategically allocates surplus premium inventory to high-risk standard bookings (capturing the 36.3% upgrade retention advantage).
  - *Policy 3: Direct Booking Value Perks*: Complimentary breakfast/parking vouchers for direct bookers to eliminate channel re-shopping.
  - *Policy 4: ADR Pricing Elasticity*: Models rate adjustments from -15% to +15% on booking volume retention vs room yield.
- **Impact Metrics**: Computes exact cancellations saved, churn reduction %, net preserved revenue ($), and per-policy contribution breakdowns.

### 4. ⚡ Live ML Feature Explainability Breakdown *(v4.0)*
- Real-time factor waterfall visualization in the Live Predictor showing how specific parameters (e.g., lead time, deposit type, special requests, past cancellations) push cancellation probability up or down.

### 5. 🌍 Geographic Intelligence & Country Risk Matrix *(v3.0)*
- **Global Origin Profiling**: Analyzes guest volume, cancellation rates, and average room rates across 170+ guest origin countries (Portugal, UK, France, Spain, Germany, USA, etc.).
- **Domestic vs. International Risk Split**:
  - **Domestic (Portugal)**: ~40.7% volume, **56.7% cancellation rate** (local transient bookings that easily reschedule).
  - **International Travelers**: ~59.3% volume, **23.6% cancellation rate** (high flight & travel commitment).
- **Interactive Country Search Table**: Live filterable search table with color-coded risk classifications.

### 6. 🛏️ Room Upgrade & Allocation Retention Matrix *(v3.0)*
- **The Upgrade Effect**: Empirically quantifies the retention benefit of room upgrades (`reserved_room_type` vs `assigned_room_type`).
  - **Same Room Assigned**: 41.6% cancellation rate.
  - **Upgraded Room Assigned**: **5.3% cancellation rate** (a **36.3% absolute reduction in cancellations**).
- **Strategic Lever**: Front desks can strategically assign discretionary upgrades to high-risk bookings to lock in guest commitment.

### 7. 🛡️ Automated Guest Retention Playbook & ROI Generator *(v3.0)*
- **Personalized Omnichannel Timelines**: Generates a pre-arrival touchpoint schedule (T-30, T-14, T-7, T-2 days before arrival).
- **Targeted Incentive Allocation**: Suggests optimal perks based on total booking value (e.g. Free parking, dining voucher, or executive lounge pass).
- **Financial ROI Calculation**: Computes expected preserved revenue, cost of incentive, and net ROI multiple (e.g. **4.5x - 8.5x ROI**).

### 8. 📄 Executive Intelligence Briefing & Print Audit Export
- Pinned in the top header: click **"Executive Report"** to open a print-ready, publication-formatted briefing report (`/api/executive-report`).
- In Batch CSV Audit: one-click **"Print Audit Briefing"** button with dedicated print media styles.

### 9. 📁 Batch Reservation CSV Audit & Revenue-at-Risk Engine *(v2.0)*
- **Bulk Risk Scoring**: Upload any CSV file of upcoming reservations for instant ML inference.
- **Revenue at Risk ($)**: Automatically calculates total financial exposure from predicted cancellations (`ADR × Stay Nights`).
- **Overbooking Recommendation**: Advises the exact buffer of rooms the property can safely re-list to maintain 100% occupancy without walking guests.
- **Enriched CSV Export**: One-click download of the audited batch with individual probability scores, risk tiers, and recommended mitigation actions.

### 10. 📈 Hotel Overbooking & Capacity Optimization Simulator
- Evaluates room capacity, quoted ADR, cancellation rate, and walked-guest penalties across overbooking buffers (0% to 20%).
- Visualizes Gross Revenue, Walk Costs, and Net Expected Profit to pinpoint the **revenue-maximizing buffer** (e.g. +10% overbooking yielding +$4,250 in net gain).

### 11. 💰 Dynamic ADR & Room Pricing Engine
- Evaluates seasonality indices, room tier multipliers (Standard to Presidential Suite), lead-time elasticity (last-minute urgency vs early-bird discounts), and market segments.
- Generates **Target Optimal ADR ($)**, fair pricing bounds `[Min - Max]`, and seasonal revenue strategies.

### 12. 🤖 Zero-Leakage Machine Learning Benchmark
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
│   ├── channel_analytics.py             # Channel net yield & OTA commission optimizer (NEW v4.0)
│   ├── loyalty_ltv.py                   # Loyalty cohorts, 3-yr LTV & VIP concierge protocol (NEW v4.0)
│   ├── scenario_sandbox.py              # What-if policy sandbox & revenue impact modeler (NEW v4.0)
│   ├── retention_playbook.py            # Automated retention timelines & ROI modeling
│   ├── model_trainer.py                 # Multi-model training & benchmarking
│   ├── predictor.py                     # Single & batch inference + factor explainability
│   └── pricing_engine.py                # Dynamic ADR pricing & room tier multipliers
├── models/
│   ├── best_cancellation_model.joblib   # Serialized champion model
│   └── model_metrics.json               # Benchmark results & feature importances
├── outputs/
│   ├── figures/                         # Generated publication visualization charts
│   └── eda_summary.json                 # Precomputed dataset statistics
└── app/
    ├── main.py                          # FastAPI server & v4.0 REST endpoints
    ├── templates/
    │   ├── index.html                   # Modern glassmorphic dashboard UI with v4.0 tabs
    │   └── executive_report.html        # Print-ready Executive Briefing document
    └── static/
        ├── css/style.css                # Aurora mesh styling, toggle switches & LTV badges
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
| `GET` | `/api/channel-analytics` | Gross vs net ADR, commission costs, and realized yield per channel *(v4.0)* |
| `POST` | `/api/simulate-channel-shift` | Calculates commission savings & profit lift from OTA-to-Direct shifts *(v4.0)* |
| `GET` | `/api/loyalty-segments` | Guest behavioral cohort segmentation, volume share, and churn rates *(v4.0)* |
| `POST` | `/api/calculate-ltv` | Calculates 3-year LTV, loyalty tier, and front-desk VIP concierge protocol *(v4.0)* |
| `POST` | `/api/simulate-scenario` | Evaluates what-if policy interventions on cancellation rates and net revenue *(v4.0)* |
| `GET` | `/api/geo-analytics` | Country-level cancellation rankings & domestic vs international metrics |
| `GET` | `/api/room-matrix` | Room upgrade vs exact room assignment retention advantage |
| `GET` | `/api/model-metrics` | Benchmark metrics (Accuracy, ROC-AUC, F1) & feature importances |
| `GET` | `/api/sample-batch-csv` | Generates & downloads 50 realistic reservations for instant testing |
| `POST` | `/api/predict` | Single reservation cancellation scoring, pricing guidance & factor explainability |
| `POST` | `/api/retention-playbook` | Generates personalized pre-arrival engagement timeline & ROI |
| `POST` | `/api/predict-batch` | High-speed multipart CSV upload for batch risk & revenue-at-risk audit |
| `POST` | `/api/simulate-overbooking` | Calculates optimal overbooking buffer and incremental revenue curve |
| `GET` | `/api/figures-list` | List of exported publication figures |
