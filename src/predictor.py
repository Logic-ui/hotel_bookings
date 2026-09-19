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
        input_df = pd.DataFrame([booking_input])
        input_df = self._apply_fallbacks(input_df)
        engineered = engineer_features(input_df)

        proba = float(self.model.predict_proba(engineered)[0, 1])
        predicted_class = int(proba >= 0.5)

        if proba < 0.35:
            risk_tier = "Low Risk"
            risk_color = "#10b981"
            risk_badge = "success"
        elif proba < 0.65:
            risk_tier = "Moderate Risk"
            risk_color = "#f59e0b"
            risk_badge = "warning"
        else:
            risk_tier = "High Risk"
            risk_color = "#ef4444"
            risk_badge = "danger"

        drivers, recommendations = self._generate_insights(booking_input, proba)
        factor_contributions = self._compute_factor_contributions(booking_input)

        return {
            'cancellation_probability': round(proba * 100, 1),
            'will_cancel_prediction': bool(predicted_class),
            'risk_tier': risk_tier,
            'risk_color': risk_color,
            'risk_badge': risk_badge,
            'key_drivers': drivers,
            'recommended_actions': recommendations,
            'factor_contributions': factor_contributions
        }

    def predict_batch(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executes high-speed batch inference on a DataFrame of reservations.
        Calculates aggregate cancellation counts, revenue at risk, and overbooking advice.
        """
        data = self._apply_fallbacks(df.copy())
        engineered = engineer_features(data)

        probas = self.model.predict_proba(engineered)[:, 1]
        preds = (probas >= 0.5).astype(int)

        # Calculate revenue at risk: adr * total_stay_nights for predicted cancellations
        stays = data['stays_in_weekend_nights'] + data['stays_in_week_nights']
        stays = stays.clip(lower=1)
        adrs = data['adr'].clip(lower=0)
        booking_values = stays * adrs

        total_bookings = len(data)
        predicted_cancellations = int(np.sum(preds))
        cancellation_rate_pct = round(float(predicted_cancellations / total_bookings * 100), 1) if total_bookings > 0 else 0
        
        # Revenue at risk
        revenue_at_risk = float(np.sum(booking_values[preds == 1]))
        total_pipeline_revenue = float(np.sum(booking_values))

        # Risk tier counts
        low_risk_count = int(np.sum(probas < 0.35))
        moderate_risk_count = int(np.sum((probas >= 0.35) & (probas < 0.65)))
        high_risk_count = int(np.sum(probas >= 0.65))

        # Recommended overbooking buffer (conservative 85% of expected cancellations)
        recommended_buffer = int(round(predicted_cancellations * 0.85))

        # Enrich records with predictions for export and display
        enriched_records = []
        for i in range(len(data)):
            p = float(probas[i])
            tier = "Low Risk" if p < 0.35 else ("Moderate Risk" if p < 0.65 else "High Risk")
            enriched_records.append({
                'row_id': i + 1,
                'hotel': str(data.iloc[i].get('hotel', 'City Hotel')),
                'lead_time': int(data.iloc[i].get('lead_time', 0)),
                'arrival_date_month': str(data.iloc[i].get('arrival_date_month', '')),
                'adr': round(float(data.iloc[i].get('adr', 0)), 2),
                'total_stay_nights': int(stays.iloc[i]),
                'total_value': round(float(booking_values.iloc[i]), 2),
                'cancellation_probability': round(p * 100, 1),
                'predicted_cancellation': int(preds[i]),
                'risk_tier': tier
            })

        return {
            'summary': {
                'total_reservations': total_bookings,
                'predicted_cancellations': predicted_cancellations,
                'predicted_cancellation_rate': cancellation_rate_pct,
                'total_pipeline_revenue': round(total_pipeline_revenue, 2),
                'revenue_at_risk': round(revenue_at_risk, 2),
                'revenue_at_risk_pct': round((revenue_at_risk / total_pipeline_revenue * 100), 1) if total_pipeline_revenue > 0 else 0,
                'recommended_overbooking_buffer': recommended_buffer,
                'risk_tiers': {
                    'low': low_risk_count,
                    'moderate': moderate_risk_count,
                    'high': high_risk_count
                }
            },
            'records': enriched_records
        }

    def _apply_fallbacks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fills standard fallback columns for any missing fields."""
        data = df.copy()
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
            if k not in data.columns:
                data[k] = v
            else:
                data[k] = data[k].fillna(v)
        
        if 'assigned_room_type' not in data.columns:
            data['assigned_room_type'] = data['reserved_room_type']

        return data

    def _generate_insights(self, data: Dict[str, Any], proba: float) -> Tuple[List[str], List[str]]:
        drivers = []
        recommendations = []

        lead_time = int(data.get('lead_time', 0))
        deposit_type = str(data.get('deposit_type', 'No Deposit'))
        special_requests = int(data.get('total_of_special_requests', 0))
        previous_cancellations = int(data.get('previous_cancellations', 0))
        is_repeated_guest = int(data.get('is_repeated_guest', 0))
        hotel = str(data.get('hotel', 'City Hotel'))

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
        
    def _compute_factor_contributions(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Computes relative percentage impact weights for key risk factors for waterfall explainability."""
        factors = []
        lead_time = int(data.get('lead_time', 0))
        deposit_type = str(data.get('deposit_type', 'No Deposit'))
        special_requests = int(data.get('total_of_special_requests', 0))
        previous_cancellations = int(data.get('previous_cancellations', 0))
        is_repeated_guest = int(data.get('is_repeated_guest', 0))
        market_segment = str(data.get('market_segment', 'Online TA'))
        parking = int(data.get('required_car_parking_spaces', 0))

        # 1. Lead Time
        if lead_time > 150:
            factors.append({'factor': f'Lead Time ({lead_time}d)', 'impact': 25, 'direction': 'risk_up', 'category': 'Booking Window'})
        elif lead_time > 60:
            factors.append({'factor': f'Lead Time ({lead_time}d)', 'impact': 14, 'direction': 'risk_up', 'category': 'Booking Window'})
        elif lead_time <= 14:
            factors.append({'factor': f'Short Lead Time ({lead_time}d)', 'impact': -18, 'direction': 'risk_down', 'category': 'Booking Window'})

        # 2. Deposit
        if deposit_type == 'Non Refund':
            factors.append({'factor': 'Non-Refund Deposit Group Policy', 'impact': 28, 'direction': 'risk_up', 'category': 'Deposit Type'})
        elif deposit_type == 'Refundable':
            factors.append({'factor': 'Refundable Deposit Hold', 'impact': -12, 'direction': 'risk_down', 'category': 'Deposit Type'})

        # 3. Special Requests
        if special_requests >= 2:
            factors.append({'factor': f'{special_requests} Special Requests (High Commitment)', 'impact': -16, 'direction': 'risk_down', 'category': 'Engagement'})
        elif special_requests == 1:
            factors.append({'factor': '1 Special Request Registered', 'impact': -8, 'direction': 'risk_down', 'category': 'Engagement'})
        else:
            factors.append({'factor': 'Zero Special Requests Submitted', 'impact': 10, 'direction': 'risk_up', 'category': 'Engagement'})

        # 4. Loyalty
        if is_repeated_guest == 1:
            factors.append({'factor': 'Verified Repeat Guest', 'impact': -22, 'direction': 'risk_down', 'category': 'Loyalty'})

        # 5. Prior cancellations
        if previous_cancellations > 0:
            impact_val = min(30, previous_cancellations * 12)
            factors.append({'factor': f'{previous_cancellations} Historical Cancellations', 'impact': impact_val, 'direction': 'risk_up', 'category': 'History'})

        # 6. Market segment
        if market_segment == 'Direct':
            factors.append({'factor': 'Direct Booking Channel', 'impact': -14, 'direction': 'risk_down', 'category': 'Channel'})
        elif market_segment == 'Groups':
            factors.append({'factor': 'Group Block Allocation', 'impact': 24, 'direction': 'risk_up', 'category': 'Channel'})
        elif market_segment == 'Corporate':
            factors.append({'factor': 'Corporate Contract Stay', 'impact': -10, 'direction': 'risk_down', 'category': 'Channel'})

        # 7. Parking
        if parking > 0:
            factors.append({'factor': 'Vehicle Parking Space Reserved', 'impact': -24, 'direction': 'risk_down', 'category': 'Commitment'})

        return factors

