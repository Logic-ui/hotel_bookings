"""
Data Pipeline Module for Hotel Bookings Analysis & Prediction.
Handles data ingestion, anomaly detection, cleaning, and feature engineering.
"""

from typing import Tuple, List, Dict, Any
import pandas as pd
import numpy as np

# Columns that represent post-booking outcomes or leak cancellation status
LEAKAGE_COLUMNS = ['reservation_status', 'reservation_status_date']

# High cardinality or raw identifier columns to drop or transform
RAW_ID_COLUMNS = ['agent', 'company']

# Default categorical columns for ML modeling
CATEGORICAL_FEATURES = [
    'hotel',
    'arrival_date_month',
    'meal',
    'market_segment',
    'distribution_channel',
    'reserved_room_type',
    'deposit_type',
    'customer_type'
]

# Default numerical features for ML modeling
NUMERICAL_FEATURES = [
    'lead_time',
    'arrival_date_week_number',
    'arrival_date_day_of_month',
    'stays_in_weekend_nights',
    'stays_in_week_nights',
    'adults',
    'children',
    'babies',
    'is_repeated_guest',
    'previous_cancellations',
    'previous_bookings_not_canceled',
    'booking_changes',
    'days_in_waiting_list',
    'adr',
    'required_car_parking_spaces',
    'total_of_special_requests',
    'total_stay_nights',
    'total_guests',
    'is_family',
    'room_type_mismatch',
    'has_special_requests',
    'has_agent',
    'has_company',
    'net_cancellations'
]


def load_raw_data(filepath: str = "hotel_bookings.csv") -> pd.DataFrame:
    """Load raw dataset from CSV file."""
    df = pd.read_csv(filepath)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw hotel bookings dataset:
    - Handle missing values in agent, company, country, children.
    - Remove invalid guest rows (adults + children + babies == 0).
    - Remove extreme ADR outliers (negative values or unrealistically high rates > 1000).
    """
    cleaned = df.copy()

    # Impute missing values
    cleaned['children'] = cleaned['children'].fillna(0).astype(int)
    cleaned['country'] = cleaned['country'].fillna('Unknown')
    
    # Replace string 'NULL' or NaN in agent/company
    cleaned['agent'] = cleaned['agent'].replace('NULL', np.nan).fillna(0)
    cleaned['company'] = cleaned['company'].replace('NULL', np.nan).fillna(0)

    # Filter out entries with 0 total guests
    cleaned = cleaned[(cleaned['adults'] + cleaned['children'] + cleaned['babies']) > 0]

    # Clean ADR: remove negative values and unrealistic outliers (> $1000/night)
    cleaned = cleaned[(cleaned['adr'] >= 0) & (cleaned['adr'] <= 1000)]

    return cleaned


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create domain-specific engineered features:
    - total_stay_nights
    - total_guests
    - is_family
    - room_type_mismatch (reserved vs assigned)
    - has_special_requests
    - has_agent
    - has_company
    - net_cancellations (previous cancellations - non-canceled bookings)
    """
    data = df.copy()

    # Stay and guest aggregations
    data['total_stay_nights'] = data['stays_in_weekend_nights'] + data['stays_in_week_nights']
    data['total_guests'] = data['adults'] + data['children'] + data['babies']
    data['is_family'] = ((data['children'] + data['babies']) > 0).astype(int)

    # Room allocation mismatch (e.g. upgrades)
    data['room_type_mismatch'] = (data['reserved_room_type'] != data['assigned_room_type']).astype(int)

    # Behavioral indicators
    data['has_special_requests'] = (data['total_of_special_requests'] > 0).astype(int)
    data['has_agent'] = (data['agent'] != 0).astype(int)
    data['has_company'] = (data['company'] != 0).astype(int)

    # Net cancellation risk score from past booking history
    data['net_cancellations'] = data['previous_cancellations'] - data['previous_bookings_not_canceled']

    return data


def prepare_ml_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str], List[str]]:
    """
    Prepares features X and target y for machine learning,
    ensuring zero leakage from reservation outcome columns.
    Returns:
        X: Feature dataframe
        y: Target series (is_canceled)
        numerical_cols: List of numeric column names
        categorical_cols: List of categorical column names
    """
    cleaned = clean_data(df)
    engineered = engineer_features(cleaned)

    # Extract target
    y = engineered['is_canceled'].astype(int)

    # Columns to drop from training features
    drop_cols = LEAKAGE_COLUMNS + ['is_canceled', 'agent', 'company', 'country', 'assigned_room_type']
    drop_cols = [c for c in drop_cols if c in engineered.columns]

    X = engineered.drop(columns=drop_cols)

    # Identify numerical and categorical columns present in X
    num_cols = [c for c in NUMERICAL_FEATURES if c in X.columns]
    cat_cols = [c for c in CATEGORICAL_FEATURES if c in X.columns]

    return X, y, num_cols, cat_cols


if __name__ == "__main__":
    import os
    csv_path = os.path.join(os.path.dirname(__file__), "..", "hotel_bookings.csv")
    print(f"Loading data from {csv_path}...")
    raw = load_raw_data(csv_path)
    print(f"Raw shape: {raw.shape}")
    X, y, num_cols, cat_cols = prepare_ml_data(raw)
    print(f"Prepared Features X shape: {X.shape}")
    print(f"Target distribution:\n{y.value_counts(normalize=True)}")
    print(f"Numerical features ({len(num_cols)}): {num_cols}")
    print(f"Categorical features ({len(cat_cols)}): {cat_cols}")
