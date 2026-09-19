"""
Guest Loyalty, Customer Lifetime Value (LTV) & VIP Persona Segmentation Engine.
Segments the hotel guest database into behavioral cohorts and provides an interactive
LTV, loyalty tier, and front-desk VIP concierge protocol calculator.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def analyze_loyalty_cohorts(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Classifies reservations in the dataset into 5 behavioral loyalty cohorts:
      1. Platinum VIP Champions (Repeated guests, 0 prior cancellations)
      2. High-Value Luxury Leisure (Suites/Deluxe rooms or ADR >= $150)
      3. Corporate Road Warriors (Corporate segment or corporate booking)
      4. Family Vacationers (Children/Babies > 0 or 3+ guests)
      5. Speculative Churn Risk (Lead time > 120 days, No deposit, prior cancellations)
      6. Standard Transient (General leisure/transient guests)
    """
    data = df.copy()
    total = len(data)
    if total == 0:
        return {'cohorts': [], 'summary': {}}

    # Define conditions for segmentation
    # 1. Platinum Repeaters
    cond_platinum = (data['is_repeated_guest'] == 1) & (data['previous_cancellations'] == 0)
    # 2. Corporate
    cond_corp = (data['market_segment'] == 'Corporate') | (data['has_company'] == 1)
    # 3. High Value Luxury (not already platinum)
    cond_luxury = (data['adr'] >= 150) | (data['reserved_room_type'].isin(['E', 'F', 'G', 'H']))
    # 4. Family & Group
    cond_family = (data['is_family'] == 1) | (data['total_guests'] >= 3)
    # 5. Speculative High Risk
    cond_risk = (data['lead_time'] > 120) & (data['deposit_type'] == 'No Deposit') & (data['previous_cancellations'] > 0)

    # Assign primary cohort priority
    data['cohort'] = 'Standard Transient'
    data.loc[cond_family, 'cohort'] = 'Family & Group Leisure'
    data.loc[cond_luxury, 'cohort'] = 'High-Value Luxury Leisure'
    data.loc[cond_corp, 'cohort'] = 'Corporate Road Warriors'
    data.loc[cond_risk, 'cohort'] = 'Speculative Churn Risk'
    data.loc[cond_platinum, 'cohort'] = 'Platinum VIP Champions'

    cohort_definitions = {
        'Platinum VIP Champions': {
            'icon': 'fa-crown',
            'badge': 'platinum',
            'color': '#a855f7',
            'description': 'Loyal repeat guests with zero cancellation history; prime candidates for lifetime retention and room upgrades.'
        },
        'High-Value Luxury Leisure': {
            'icon': 'fa-gem',
            'badge': 'gold',
            'color': '#f59e0b',
            'description': 'High ADR guests booking Suites and Deluxe rooms; generate outsized RevPAR and premium amenity revenue.'
        },
        'Corporate Road Warriors': {
            'icon': 'fa-briefcase',
            'badge': 'blue',
            'color': '#3b82f6',
            'description': 'Business travelers with mid-week stays, low lead times, and steady booking frequency.'
        },
        'Family & Group Leisure': {
            'icon': 'fa-people-roof',
            'badge': 'teal',
            'color': '#14b8a6',
            'description': 'Multi-guest and family travelers with higher stay nights, advance planning, and dining needs.'
        },
        'Speculative Churn Risk': {
            'icon': 'fa-triangle-exclamation',
            'badge': 'danger',
            'color': '#ef4444',
            'description': 'High lead time with no financial commitment and past cancellation record; high churn vulnerability.'
        },
        'Standard Transient': {
            'icon': 'fa-user',
            'badge': 'neutral',
            'color': '#64748b',
            'description': 'Regular independent travelers booking standard rooms via retail OTA and direct channels.'
        }
    }

    cohort_results: List[Dict[str, Any]] = []

    for name, meta in cohort_definitions.items():
        c_df = data[data['cohort'] == name]
        c_count = len(c_df)
        if c_count == 0:
            continue

        c_pct = round(c_count / total * 100, 1)
        c_cancels = int(c_df['is_canceled'].sum())
        c_cancel_rate = round(float(c_df['is_canceled'].mean() * 100), 1)
        c_adr = round(float(c_df['adr'].mean()), 2)
        c_stay = round(float(c_df['total_stay_nights'].mean()), 1)
        c_lead = round(float(c_df['lead_time'].mean()), 1)
        c_revenue = round(float((c_df[c_df['is_canceled'] == 0]['adr'] * c_df[c_df['is_canceled'] == 0]['total_stay_nights']).sum()), 2)

        cohort_results.append({
            'cohort_name': name,
            'icon': meta['icon'],
            'badge': meta['badge'],
            'color': meta['color'],
            'description': meta['description'],
            'total_bookings': c_count,
            'portfolio_share_pct': c_pct,
            'cancellation_rate_pct': c_cancel_rate,
            'avg_adr': c_adr,
            'avg_stay_nights': c_stay,
            'avg_lead_time': c_lead,
            'realized_revenue': c_revenue
        })

    # Summary
    repeat_guests = int(data['is_repeated_guest'].sum())
    repeat_pct = round(repeat_guests / total * 100, 2)

    return {
        'cohorts': cohort_results,
        'summary': {
            'total_guests_profiled': total,
            'repeat_guest_count': repeat_guests,
            'repeat_guest_pct': repeat_pct
        }
    }


def calculate_guest_ltv(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes 3-Year Customer Lifetime Value (LTV), Loyalty Tier, and Front-Desk
    concierge greeting protocol based on individual guest profile parameters.
    """
    past_stays = int(params.get('past_completed_stays', 1))
    past_cancels = int(params.get('past_cancellations', 0))
    projected_annual_stays = float(params.get('projected_annual_stays', 2.0))
    avg_adr = float(params.get('average_adr', 120.0))
    avg_nights = float(params.get('average_nights_per_stay', 2.5))
    room_preference = str(params.get('preferred_room_type', 'A'))
    special_requests = int(params.get('special_requests', 1))

    # Annual gross spend
    annual_spend = projected_annual_stays * avg_nights * avg_adr

    # Retention probability model
    total_past = past_stays + past_cancels
    cancellation_history_ratio = past_cancels / max(1, total_past)
    
    # Base retention factor
    retention_prob = 0.72
    if past_stays >= 3:
        retention_prob += 0.15
    elif past_stays >= 1:
        retention_prob += 0.08

    # Penalty for prior cancellations
    retention_prob -= cancellation_history_ratio * 0.35
    retention_prob = max(0.20, min(0.92, retention_prob))

    # 3-Year Discounted LTV (discount rate r = 8%)
    # LTV = Spend_yr1 + (Spend_yr2 * retention / 1.08) + (Spend_yr3 * retention^2 / 1.08^2)
    yr1 = annual_spend
    yr2 = (annual_spend * retention_prob) / 1.08
    yr3 = (annual_spend * (retention_prob ** 2)) / (1.08 ** 2)
    three_year_ltv = round(yr1 + yr2 + yr3, 2)

    # Determine Loyalty Tier
    if three_year_ltv >= 3500 or past_stays >= 5:
        tier_name = "Platinum VIP Elite"
        tier_badge = "platinum"
        tier_color = "#c084fc"
        tier_multiplier = "1.5x Loyalty Points"
        greeting = "Warm personal welcome from General Manager, pre-allocated complimentary suite upgrade, and chilled beverage amenity in-room."
        amenities = ["Complimentary Room Upgrade", "Executive Lounge Pass", "4:00 PM Late Checkout", "Welcome Champagne & Fruit Platter"]
    elif three_year_ltv >= 2000 or past_stays >= 3:
        tier_name = "Gold Preferred"
        tier_badge = "gold"
        tier_color = "#f59e0b"
        tier_multiplier = "1.25x Loyalty Points"
        greeting = "Express front-desk check-in, complimentary room view enhancement, and welcome breakfast voucher."
        amenities = ["Priority Room Assignment", "Breakfast Buffet Pass", "2:00 PM Late Checkout", "Welcome Beverage Token"]
    elif three_year_ltv >= 1000 or past_stays >= 1:
        tier_name = "Silver Member"
        tier_badge = "silver"
        tier_color = "#94a3b8"
        tier_multiplier = "1.1x Loyalty Points"
        greeting = "Recognition of return visit, preferred floor allocation, and digital room key access."
        amenities = ["Preferred Floor Request", "Complimentary High-Speed Wi-Fi", "1:00 PM Late Checkout"]
    else:
        tier_name = "Bronze Explorer"
        tier_badge = "bronze"
        tier_color = "#b45309"
        tier_multiplier = "1.0x Base Points"
        greeting = "Warm hospitality welcome, property orientation guide, and enrollment invite for GrandHorizon Rewards."
        amenities = ["Standard Check-in", "Property Amenity Guide", "GrandHorizon Rewards Onboarding"]

    return {
        'three_year_ltv': three_year_ltv,
        'annual_spend_estimate': round(annual_spend, 2),
        'retention_probability_pct': round(retention_prob * 100, 1),
        'loyalty_tier': {
            'tier_name': tier_name,
            'tier_badge': tier_badge,
            'tier_color': tier_color,
            'multiplier': tier_multiplier
        },
        'concierge_protocol': {
            'greeting_script': greeting,
            'vip_amenities': amenities
        }
    }
