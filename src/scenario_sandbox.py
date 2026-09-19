"""
Interactive Policy What-If Scenario Sandbox & Revenue Impact Modeler.
Simulates property-level policy interventions:
  1. Long Lead-Time Deposit Rule (Deposit on lead time > 60 days)
  2. Proactive Room Upgrade Allocation (Leveraging the 36.3% upgrade retention advantage)
  3. Direct Guest Loyalty Perk Campaign (Breakfast/Parking perks for direct bookings)
  4. Dynamic ADR Price Adjustment (-15% to +15% elasticity)
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def simulate_policy_intervention(
    df: pd.DataFrame,
    policies: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates baseline vs simulated policy intervention scenarios across the active dataset slice.
    """
    data = df.copy()
    total_bookings = len(data)
    if total_bookings == 0:
        return {'error': 'Dataset slice is empty.'}

    # Extract policy toggles
    apply_deposit_rule = bool(policies.get('deposit_rule', False))
    apply_upgrade_rule = bool(policies.get('upgrade_rule', False))
    apply_direct_perk = bool(policies.get('direct_perk', False))
    adr_adjust_pct = float(policies.get('adr_adjustment_pct', 0.0))

    # Baseline calculations
    baseline_cancels = int(data['is_canceled'].sum())
    baseline_cancel_rate = float(data['is_canceled'].mean())
    baseline_realized = total_bookings - baseline_cancels
    
    # Stay nights & revenue
    stays = data['total_stay_nights'].clip(lower=1)
    adrs = data['adr'].clip(lower=0)
    baseline_booking_values = stays * adrs
    baseline_realized_revenue = float(baseline_booking_values[data['is_canceled'] == 0].sum())

    # Simulated cancellation tracking
    # Start with individual cancel probabilities
    # If is_canceled == 1, probability is 1.0; else 0.0
    simulated_canceled = data['is_canceled'].copy().astype(float)
    policy_contributions = {}

    # 1. Long Lead-Time Deposit Rule:
    # Bookings with lead_time > 60 days and 'No Deposit' are highly speculative.
    # Mandating deposit filters or commits these guests, reducing cancellations by ~32%.
    if apply_deposit_rule:
        target_mask = (data['lead_time'] > 60) & (data['deposit_type'] == 'No Deposit') & (simulated_canceled > 0)
        reduction_rate = 0.32
        saved_deposit = int(round(target_mask.sum() * reduction_rate))
        simulated_canceled.loc[target_mask] = simulated_canceled.loc[target_mask] * (1.0 - reduction_rate)
        policy_contributions['deposit_rule'] = {
            'policy_name': 'Long Lead-Time Deposit Mandate (>60 days)',
            'cancellations_prevented': saved_deposit,
            'description': 'Filters speculative bookings and locks in customer financial commitment.'
        }

    # 2. Proactive Room Upgrade Allocation:
    # In GrandHorizon room matrix, upgraded guests cancel at only 5.3% vs 41.6% for same-room.
    # Applying proactive upgrade strategy to standard Room A at-risk bookings cuts cancellations by 45%.
    if apply_upgrade_rule:
        target_mask = (data['reserved_room_type'] == 'A') & (simulated_canceled > 0)
        reduction_rate = 0.45
        saved_upgrade = int(round(target_mask.sum() * reduction_rate))
        simulated_canceled.loc[target_mask] = simulated_canceled.loc[target_mask] * (1.0 - reduction_rate)
        policy_contributions['upgrade_rule'] = {
            'policy_name': 'Strategic Discretionary Room Upgrades',
            'cancellations_prevented': saved_upgrade,
            'description': 'Assigns surplus premium inventory to high-risk standard bookings to secure commitment.'
        }

    # 3. Direct Loyalty Perk Campaign:
    # Direct guests given complimentary parking or breakfast voucher; reduces direct churn by 35%.
    if apply_direct_perk:
        target_mask = (data['market_segment'] == 'Direct') & (simulated_canceled > 0)
        reduction_rate = 0.35
        saved_direct = int(round(target_mask.sum() * reduction_rate))
        simulated_canceled.loc[target_mask] = simulated_canceled.loc[target_mask] * (1.0 - reduction_rate)
        policy_contributions['direct_perk'] = {
            'policy_name': 'Direct Booking Loyalty Perks (Parking / Breakfast)',
            'cancellations_prevented': saved_direct,
            'description': 'Deters re-shopping by providing guaranteed property value additions.'
        }

    # 4. ADR Price Elasticity Adjustment:
    # Price elasticity in hospitality demand: ~ -0.4 to -0.6
    # Higher prices (+5%) slightly elevate cancellations (+2%); lower prices reduce cancellations.
    adjusted_adrs = adrs * (1.0 + (adr_adjust_pct / 100.0))
    if adr_adjust_pct != 0.0:
        elasticity_cancellation_factor = 1.0 + (adr_adjust_pct / 100.0 * 0.35)
        simulated_canceled = (simulated_canceled * elasticity_cancellation_factor).clip(0.0, 1.0)
        policy_contributions['adr_adjustment'] = {
            'policy_name': f'ADR Adjustment ({adr_adjust_pct:+.1f}%)',
            'cancellations_prevented': int(round(baseline_cancels - simulated_canceled.sum())),
            'description': f'Evaluates price elasticity impact with an ADR shift of {adr_adjust_pct:+.1f}%.'
        }

    # Simulated totals
    simulated_cancel_count = int(round(simulated_canceled.sum()))
    simulated_cancel_rate = round(float(simulated_cancel_count / total_bookings * 100), 2)
    cancellations_prevented = max(0, baseline_cancels - simulated_cancel_count)

    # Simulated revenue
    sim_realized_mask = (1.0 - simulated_canceled)
    simulated_realized_revenue = float((adjusted_adrs * stays * sim_realized_mask).sum())
    net_revenue_impact = round(simulated_realized_revenue - baseline_realized_revenue, 2)
    revenue_growth_pct = round((net_revenue_impact / baseline_realized_revenue * 100), 2) if baseline_realized_revenue > 0 else 0

    return {
        'baseline': {
            'total_bookings': total_bookings,
            'cancellations': baseline_cancels,
            'cancellation_rate_pct': round(baseline_cancel_rate * 100, 2),
            'realized_bookings': baseline_realized,
            'realized_revenue': round(baseline_realized_revenue, 2)
        },
        'scenario': {
            'total_bookings': total_bookings,
            'cancellations': simulated_cancel_count,
            'cancellation_rate_pct': simulated_cancel_rate,
            'realized_bookings': total_bookings - simulated_cancel_count,
            'realized_revenue': round(simulated_realized_revenue, 2)
        },
        'impact': {
            'cancellations_prevented': cancellations_prevented,
            'cancellation_rate_reduction_pct': round((baseline_cancel_rate * 100) - simulated_cancel_rate, 2),
            'net_revenue_impact': net_revenue_impact,
            'revenue_growth_pct': revenue_growth_pct
        },
        'policy_contributions': policy_contributions
    }
