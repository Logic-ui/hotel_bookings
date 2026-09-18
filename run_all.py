"""
Master Orchestration Script for Hotel Bookings Intelligence & ML Prediction.
Executes the end-to-end data pipeline, EDA visualizer, and ML training suite.
"""

import os
import sys
import argparse
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def main():
    parser = argparse.ArgumentParser(description="Hotel Bookings Analytics & Prediction Pipeline")
    parser.add_argument("--skip-eda", action="store_true", help="Skip EDA and figure generation")
    parser.add_argument("--skip-train", action="store_true", help="Skip model training")
    parser.add_argument("--sample-size", type=int, default=None, help="Sample size for faster training benchmark")
    parser.add_argument("--serve", action="store_true", help="Launch FastAPI web dashboard after running pipeline")
    parser.add_argument("--port", type=int, default=8000, help="Web dashboard port (default: 8000)")
    args = parser.parse_args()

    csv_path = os.path.join(BASE_DIR, "hotel_bookings.csv")
    outputs_dir = os.path.join(BASE_DIR, "outputs")
    models_dir = os.path.join(BASE_DIR, "models")

    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        sys.exit(1)

    print("=" * 70)
    print("      GRANDHORIZON HOTEL BOOKING INTELLIGENCE & ML SUITE      ")
    print("=" * 70)

    # 1. Exploratory Data Analysis & Visualizations
    if not args.skip_eda:
        print("\n[PHASE 1/3] Running Exploratory Data Analysis (EDA)...")
        from src.eda_analysis import run_full_eda
        summary = run_full_eda(csv_path, outputs_dir)
        kpis = summary['executive_kpis']
        print(f"  Total Bookings: {kpis['total_bookings']:,}")
        print(f"  Cancellation Rate: {kpis['cancellation_rate']}%")
        print(f"  Average Daily Rate (ADR): ${kpis['avg_adr']}")
        print(f"  Average Lead Time: {kpis['avg_lead_time']} days")
        print("  Visualizations saved to outputs/figures/")

    # 2. Machine Learning Model Training & Benchmarking
    if not args.skip_train:
        print("\n[PHASE 2/3] Training & Benchmarking Machine Learning Classifiers...")
        from src.model_trainer import train_and_evaluate_all
        best_pipeline, metadata = train_and_evaluate_all(csv_path, models_dir, sample_size=args.sample_size)
        print(f"\n>> Best Model Selected: {metadata['best_model']}")
        for name, m in metadata['models_benchmark'].items():
            print(f"   * {name:25s} | Accuracy: {m['accuracy']*100:.2f}% | ROC-AUC: {m['roc_auc']:.4f} | F1: {m['f1_score']:.4f}")

    # 3. Model Inference Test
    print("\n[PHASE 3/3] Validating Inference Engine...")
    from src.predictor import BookingCancellationPredictor
    predictor = BookingCancellationPredictor(os.path.join(models_dir, "best_cancellation_model.joblib"))

    # Test Case 1: High risk scenario (long lead time, no deposit, 0 special requests, 2 previous cancellations)
    high_risk_sample = {
        'hotel': 'City Hotel',
        'lead_time': 240,
        'arrival_date_month': 'August',
        'stays_in_weekend_nights': 1,
        'stays_in_week_nights': 3,
        'adults': 2,
        'market_segment': 'Online TA',
        'deposit_type': 'No Deposit',
        'adr': 130.0,
        'previous_cancellations': 2,
        'total_of_special_requests': 0
    }
    pred_high = predictor.predict_booking(high_risk_sample)
    print(f"  Test Case 1 (High Risk Simulation):")
    print(f"    Probability: {pred_high['cancellation_probability']}% | Tier: {pred_high['risk_tier']}")
    print(f"    Drivers: {pred_high['key_drivers'][0]}")

    # Test Case 2: Low risk scenario (short lead time, repeat guest, special requests)
    low_risk_sample = {
        'hotel': 'Resort Hotel',
        'lead_time': 10,
        'arrival_date_month': 'July',
        'stays_in_weekend_nights': 2,
        'stays_in_week_nights': 5,
        'adults': 2,
        'children': 1,
        'market_segment': 'Direct',
        'deposit_type': 'No Deposit',
        'adr': 180.0,
        'is_repeated_guest': 1,
        'previous_cancellations': 0,
        'total_of_special_requests': 2
    }
    pred_low = predictor.predict_booking(low_risk_sample)
    print(f"  Test Case 2 (Low Risk Simulation):")
    print(f"    Probability: {pred_low['cancellation_probability']}% | Tier: {pred_low['risk_tier']}")
    print(f"    Drivers: {pred_low['key_drivers'][0]}")

    print("\n" + "=" * 70)
    print(" Pipeline execution complete! All artifacts generated successfully.")
    print("=" * 70)

    if args.serve:
        print(f"\nLaunching Interactive Dashboard at http://127.0.0.1:{args.port} ...")
        import uvicorn
        uvicorn.run("app.main:app", host="127.0.0.1", port=args.port, reload=False)
    else:
        print("\nTo launch the interactive dashboard, run:")
        print(f"   python -m uvicorn app.main:app --port {args.port} --reload")
        print(f"   or: python run_all.py --serve --port {args.port}")


if __name__ == "__main__":
    main()
