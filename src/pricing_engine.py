"""
Dynamic Pricing & ADR Recommendation Engine for Hotel Revenue Management.
Calculates optimal daily room rates based on seasonality, room type, lead time, and market segment.
"""

from typing import Dict, Any

MONTH_SEASONALITY_MULTIPLIERS = {
    'January': 0.78,
    'February': 0.82,
    'March': 0.88,
    'April': 0.95,
    'May': 1.08,
    'June': 1.20,
    'July': 1.35,
    'August': 1.42,
    'September': 1.15,
    'October': 1.02,
    'November': 0.80,
    'December': 0.84
}

ROOM_TYPE_MULTIPLIERS = {
    'A': 1.00,  # Standard Room
    'B': 1.08,  # Standard Plus
    'C': 1.18,  # Superior Room
    'D': 1.28,  # Deluxe Room
    'E': 1.45,  # Junior Suite
    'F': 1.70,  # Executive Suite
    'G': 2.05,  # Presidential Suite
    'H': 2.40   # Royal Suite
}

MARKET_SEGMENT_MULTIPLIERS = {
    'Direct': 1.08,
    'Online TA': 1.00,
    'Offline TA/TO': 0.92,
    'Corporate': 0.88,
    'Groups': 0.82
}


class DynamicPricingEngine:
    """Calculates data-driven pricing targets and bounds for hospitality rooms."""

    def __init__(self):
        self.base_city_rate = 98.0
        self.base_resort_rate = 88.0

    def recommend_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        hotel = params.get('hotel', 'City Hotel')
        month = params.get('arrival_date_month', 'July')
        room = params.get('reserved_room_type', 'A')
        segment = params.get('market_segment', 'Online TA')
        lead_time = int(params.get('lead_time', 30))
        adults = int(params.get('adults', 2))
        children = int(params.get('children', 0))

        # Base rate
        base = self.base_city_rate if hotel == 'City Hotel' else self.base_resort_rate

        # Multipliers
        season_mult = MONTH_SEASONALITY_MULTIPLIERS.get(month, 1.00)
        room_mult = ROOM_TYPE_MULTIPLIERS.get(room, 1.00)
        seg_mult = MARKET_SEGMENT_MULTIPLIERS.get(segment, 1.00)

        # Lead time elasticity
        if lead_time <= 3:
            lead_mult = 1.12  # Last-minute urgency premium
        elif lead_time <= 14:
            lead_mult = 1.04
        elif lead_time > 90:
            lead_mult = 0.92  # Early bird incentive
        else:
            lead_mult = 1.00

        # Guest count adjustment (extra guest fee beyond 2 adults)
        guest_mult = 1.0
        if adults > 2:
            guest_mult += (adults - 2) * 0.18
        if children > 0:
            guest_mult += children * 0.10

        target_adr = base * season_mult * room_mult * seg_mult * lead_mult * guest_mult
        target_adr = round(target_adr, 2)

        # Pricing bounds
        min_adr = round(target_adr * 0.82, 2)
        max_adr = round(target_adr * 1.25, 2)

        # Seasonality assessment
        if season_mult >= 1.25:
            season_category = "Peak High Season"
            season_badge = "danger"
            strategy = "High demand window: enforce minimum night stays and strict deposit policies."
        elif season_mult >= 1.0:
            season_category = "Regular Shoulder Season"
            season_badge = "warning"
            strategy = "Moderate demand: optimize room upgrades and package inclusions."
        else:
            season_category = "Low Value Season"
            season_badge = "info"
            strategy = "Off-peak window: implement promotions and flexible cancellation terms to stimulate occupancy."

        return {
            'target_adr': target_adr,
            'price_range': {
                'min': min_adr,
                'max': max_adr
            },
            'seasonality_multiplier': round(season_mult, 2),
            'season_category': season_category,
            'season_badge': season_badge,
            'strategic_guidance': strategy
        }
