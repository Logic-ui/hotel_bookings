"""
Inference & Risk Scoring Engine for Hotel Booking Cancellation Prediction.
Provides single-record and batch predictions with risk explanations and actionable recommendations.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List

from src.data_pipeline import engineer_features, NUMERICAL_FEATURES, CATEGORICAL_FEATURES


class BookingCancellationPredictor:
    """Predictor class that loads the trained model pipeline and performs inference."""

    def __init__(self, model_path: str = None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "best_cancellation_model.joblib")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}. Please train the model first.")
        
        self.model = joblib.load(model_path)

    def predict_booking(self, booking_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw booking input parameters, processes them through feature engineering,
        runs model inference, and returns risk assessment, key drivers, and recommendations.
        """
        # Convert input dictionary to DataFrame
        input_df = pd.DataFrame([booking_input])

        # Fill default fallback values for any omitted fields
        defaults = {
            'hotel': 'City Hotel',
            'lead_time': 30,
            'arrival_date_year': 2026,
            'arrival_date_month': 'July',
            'arrival_date_week_number': 28,
            'arrival_date_day_of_month': 15,
            'stays_in_weekend_nights': 1,
            'stays_in_week_nights': 2,
            'adults': 2,
            'children': 0,
            'babies': 0,
            'meal': 'BB',
            'country': 'PRT',
            'market_segment': 'Online TA',
            'distribution_channel': 'TA/TO',
            'is_repeated_guest': 0,
            'previous_cancellations': 0,
            'previous_bookings_not_canceled': 0,
            'reserved_room_type': 'A',
            'assigned_room_type': booking_input.get('reserved_room_type', 'A'),
            'booking_changes': 0,
            'deposit_type': 'No Deposit',
            'agent': 0,
            'company': 0,
            'days_in_waiting_list': 0,
            'customer_type': 'Transient',
            'adr': 100.0,
            'required_car_parking_spaces': 0,
            'total_of_special_requests': 0
        }

        for k, v in defaults.items():
            if k not in input_df.columns or pd.isna(input_df.at[0, k]):
                input_df[k] = v

        # Apply feature engineering
        engineered = engineer_features(input_df)

        # Predict probability
        proba = float(self.model.predict_proba(engineered)[0, 1])
        predicted_class = int(proba >= 0.5)

        # Determine risk tier
        if proba < 0.35:
            risk_tier = "Low Risk"
            risk_color = "#10b981"  # Emerald Green
            risk_badge = "success"
        elif proba < 0.65:
            risk_tier = "Moderate Risk"
            risk_color = "#f59e0b"  # Amber Orange
            risk_badge = "warning"
        else:
            risk_tier = "High Risk"
            risk_color = "#ef4444"  # Crimson Red
            risk_badge = "danger"

        # Generate intelligent business drivers and recommendations
        drivers, recommendations = self._generate_insights(booking_input, proba)

        return {
            'cancellation_probability': round(proba * 100, 1),
            'will_cancel_prediction': bool(predicted_class),
            'risk_tier': risk_tier,
            'risk_color': risk_color,
            'risk_badge': risk_badge,
            'key_drivers': drivers,
            'recommended_actions': recommendations
        }

    def _generate_insights(self, data: Dict[str, Any], proba: float) -> Tuple[List[str], List[str]]:
        drivers = []
        recommendations = []

        lead_time = int(data.get('lead_time', 0))
        deposit_type = str(data.get('deposit_type', 'No Deposit'))
        market_segment = str(data.get('market_segment', 'Online TA'))
        special_requests = int(data.get('total_of_special_requests', 0))
        previous_cancellations = int(data.get('previous_cancellations', 0))
        is_repeated_guest = int(data.get('is_repeated_guest', 0))
        hotel = str(data.get('hotel', 'City Hotel'))

        # Driver checks
        if lead_time > 120:
            drivers.append(f"Extended lead time ({lead_time} days) significantly amplifies cancellation risk.")
            recommendations.append("Trigger automated guest engagement & itinerary check-in 30 and 14 days before arrival.")
        elif lead_time <= 14:
            drivers.append(f"Short booking horizon ({lead_time} days) indicates strong immediate travel intent.")

        if deposit_type == 'Non Refund':
            drivers.append("Non-Refund deposit type historically associated with high group/agency cancellation rates.")
            recommendations.append("Verify corporate/agent contract terms and enforce pre-arrival payment confirmation.")

        if previous_cancellations > 0:
            drivers.append(f"Guest profile has {previous_cancellations} previous cancellations.")
            recommendations.append("Require credit card pre-authorization or refundable deposit for room hold.")

        if special_requests == 0:
            drivers.append("Zero special requests submitted, reflecting low initial engagement.")
            recommendations.append("Offer complimentary upgrade options or personalized amenities to increase engagement.")
        else:
            drivers.append(f"Guest specified {special_requests} special request(s), reflecting positive commitment.")

        if is_repeated_guest == 1:
            drivers.append("Verified repeated guest with established property loyalty.")
            recommendations.append("Acknowledge loyalty status at check-in; minimal cancellation retention required.")

        if hotel == 'City Hotel' and proba > 0.5:
            recommendations.append("City Hotel bookings benefit from active overbooking buffer rules (5-8% target).")

        if not drivers:
            drivers.append("Booking parameters reflect standard transient reservation dynamics.")
        if not recommendations:
            recommendations.append("Standard automated confirmation email and standard 24h pre-arrival reminder.")

        return drivers, recommendations


if __name__ == "__main__":
    # Quick test if model exists
    try:
        predictor = BookingCancellationPredictor()
        sample = {
            'hotel': 'City Hotel',
            'lead_time': 180,
            'arrival_date_month': 'August',
            'stays_in_weekend_nights': 1,
            'stays_in_week_nights': 3,
            'adults': 2,
            'meal': 'BB',
            'market_segment': 'Online TA',
            'deposit_type': 'No Deposit',
            'customer_type': 'Transient',
            'adr': 120.0,
            'total_of_special_requests': 0
        }
        res = predictor.predict_booking(sample)
        print("Prediction Result:", res)
    except FileNotFoundError as e:
        print("Model not trained yet:", e)
