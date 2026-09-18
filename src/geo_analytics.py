"""
Geographic Intelligence Module for Hotel Bookings.
Analyzes guest origin countries, domestic vs international trends, and country risk tiers.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

COUNTRY_NAMES = {
    'PRT': 'Portugal',
    'GBR': 'United Kingdom',
    'FRA': 'France',
    'ESP': 'Spain',
    'DEU': 'Germany',
    'ITA': 'Italy',
    'IRL': 'Ireland',
    'BEL': 'Belgium',
    'BRA': 'Brazil',
    'NLD': 'Netherlands',
    'USA': 'United States',
    'CHE': 'Switzerland',
    'CN': 'China',
    'AUT': 'Austria',
    'SWE': 'Sweden',
    'POL': 'Poland',
    'RUS': 'Russia',
    'NOR': 'Norway',
    'ROU': 'Romania',
    'FIN': 'Finland'
}


def analyze_geographic_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes country-level statistics, domestic vs international split, and risk tiers."""
    data = df.copy()
    data['country'] = data['country'].fillna('Unknown')
    
    total = len(data)
    if total == 0:
        return {}

    # Domestic (Portugal) vs International
    data['is_domestic'] = (data['country'] == 'PRT').astype(int)
    
    domestic_df = data[data['is_domestic'] == 1]
    intl_df = data[data['is_domestic'] == 0]

    dom_stats = {
        'total_bookings': int(len(domestic_df)),
        'pct_of_total': round(len(domestic_df) / total * 100, 1),
        'cancellation_rate': round(float(domestic_df['is_canceled'].mean() * 100), 2) if len(domestic_df) > 0 else 0,
        'avg_adr': round(float(domestic_df['adr'].mean()), 2) if len(domestic_df) > 0 else 0,
        'avg_lead_time': round(float(domestic_df['lead_time'].mean()), 1) if len(domestic_df) > 0 else 0
    }

    intl_stats = {
        'total_bookings': int(len(intl_df)),
        'pct_of_total': round(len(intl_df) / total * 100, 1),
        'cancellation_rate': round(float(intl_df['is_canceled'].mean() * 100), 2) if len(intl_df) > 0 else 0,
        'avg_adr': round(float(intl_df['adr'].mean()), 2) if len(intl_df) > 0 else 0,
        'avg_lead_time': round(float(intl_df['lead_time'].mean()), 1) if len(intl_df) > 0 else 0
    }

    # Country level aggregation for top 20 origins
    country_agg = data.groupby('country').agg(
        bookings=('is_canceled', 'count'),
        cancellations=('is_canceled', 'sum'),
        cancellation_rate=('is_canceled', lambda x: round(float(x.mean() * 100), 1)),
        avg_adr=('adr', lambda x: round(float(x.mean()), 2)),
        avg_lead_time=('lead_time', lambda x: round(float(x.mean()), 1))
    ).sort_values(by='bookings', ascending=False)

    top_countries: List[Dict[str, Any]] = []
    for code, row in country_agg.head(20).iterrows():
        rate = float(row['cancellation_rate'])
        if rate < 25.0:
            risk_tier = "Low Risk"
            risk_color = "#10b981"
        elif rate < 40.0:
            risk_tier = "Moderate Risk"
            risk_color = "#f59e0b"
        else:
            risk_tier = "High Risk"
            risk_color = "#ef4444"

        top_countries.append({
            'country_code': str(code),
            'country_name': COUNTRY_NAMES.get(str(code), str(code)),
            'bookings': int(row['bookings']),
            'pct_share': round(float(row['bookings'] / total * 100), 1),
            'cancellation_rate': rate,
            'avg_adr': float(row['avg_adr']),
            'avg_lead_time': float(row['avg_lead_time']),
            'risk_tier': risk_tier,
            'risk_color': risk_color
        })

    return {
        'domestic_vs_international': {
            'domestic': dom_stats,
            'international': intl_stats
        },
        'top_origin_countries': top_countries
    }
