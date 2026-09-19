"""
Distribution Channel Net Yield & Commission Optimizer for GrandHorizon Hospitality Suite.
Evaluates gross ADR, intermediary commission friction, cancellation exposure,
net realized yield, and simulates profit lift from OTA-to-Direct channel shifts.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

# Standard industry distribution channel commission rates
CHANNEL_COMMISSION_RATES = {
    'Direct': 0.00,       # 0% direct brand website / call center
    'Online TA': 0.18,    # 18% OTAs (Booking.com, Expedia, Agoda, etc.)
    'Offline TA/TO': 0.12, # 12% Wholesalers, traditional tour operators
    'Corporate': 0.05,    # 5% Corporate travel management fee
    'Groups': 0.10        # 10% Group organizer discount / net rate friction
}

DEFAULT_COMMISSION = 0.12


def analyze_channel_economics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes gross ADR, commission expense, net ADR, cancellation attrition,
    and net realized yield per channel across the dataset.
    """
    data = df.copy()
    if len(data) == 0:
        return {'channels': [], 'summary': {}}

    total_bookings_all = len(data)
    channels_data: List[Dict[str, Any]] = []

    # Segments to analyze
    target_segments = ['Direct', 'Online TA', 'Offline TA/TO', 'Corporate', 'Groups']

    total_gross_revenue_all = 0.0
    total_commission_paid_all = 0.0
    total_net_revenue_all = 0.0

    for seg in target_segments:
        seg_df = data[data['market_segment'] == seg]
        if len(seg_df) == 0:
            continue

        bookings_count = len(seg_df)
        pct_volume = round(bookings_count / total_bookings_all * 100, 1)
        canceled_count = int(seg_df['is_canceled'].sum())
        realized_count = bookings_count - canceled_count
        cancellation_rate = round(float(seg_df['is_canceled'].mean() * 100), 1)

        gross_adr = round(float(seg_df['adr'].mean()), 2)
        avg_nights = round(float(seg_df['total_stay_nights'].mean()), 1)
        if avg_nights <= 0:
            avg_nights = 2.5

        comm_rate = CHANNEL_COMMISSION_RATES.get(seg, DEFAULT_COMMISSION)
        commission_per_night = round(gross_adr * comm_rate, 2)
        net_adr = round(gross_adr * (1.0 - comm_rate), 2)

        # Realized Yield: revenue earned per reservation attempt taking both cancellation & commission into account
        completion_rate = (1.0 - (cancellation_rate / 100.0))
        realized_yield = round(gross_adr * completion_rate * (1.0 - comm_rate), 2)

        # Total channel financials
        channel_gross_revenue = round(realized_count * avg_nights * gross_adr, 2)
        channel_commission_paid = round(realized_count * avg_nights * commission_per_night, 2)
        channel_net_revenue = round(channel_gross_revenue - channel_commission_paid, 2)

        total_gross_revenue_all += channel_gross_revenue
        total_commission_paid_all += channel_commission_paid
        total_net_revenue_all += channel_net_revenue

        channels_data.append({
            'market_segment': seg,
            'total_bookings': bookings_count,
            'volume_share_pct': pct_volume,
            'canceled_bookings': canceled_count,
            'realized_bookings': realized_count,
            'cancellation_rate': cancellation_rate,
            'gross_adr': gross_adr,
            'commission_rate_pct': int(comm_rate * 100),
            'commission_per_night': commission_per_night,
            'net_adr': net_adr,
            'avg_stay_nights': avg_nights,
            'realized_yield_per_attempt': realized_yield,
            'total_gross_revenue': channel_gross_revenue,
            'total_commission_paid': channel_commission_paid,
            'total_net_revenue': channel_net_revenue
        })

    # Sort by volume
    channels_data.sort(key=lambda x: x['total_bookings'], reverse=True)

    summary = {
        'total_bookings_evaluated': total_bookings_all,
        'total_gross_revenue': round(total_gross_revenue_all, 2),
        'total_commissions_paid': round(total_commission_paid_all, 2),
        'total_net_realized_revenue': round(total_net_revenue_all, 2),
        'effective_portfolio_take_rate_pct': round((total_commission_paid_all / total_gross_revenue_all * 100), 1) if total_gross_revenue_all > 0 else 0
    }

    return {
        'channels': channels_data,
        'summary': summary
    }


def simulate_channel_shift(
    df: pd.DataFrame,
    shift_pct: float = 10.0,
    marketing_cost_per_direct_booking: float = 15.0
) -> Dict[str, Any]:
    """
    Simulates shifting a percentage of Online TA volume directly to Direct brand booking.
    Calculates:
      - OTA bookings shifted
      - Commission expenses eliminated
      - Cancellations prevented (due to direct booking commitment)
      - Net revenue & profit expansion after direct acquisition costs.
    """
    ota_df = df[df['market_segment'] == 'Online TA']
    direct_df = df[df['market_segment'] == 'Direct']

    if len(ota_df) == 0:
        return {'error': 'No Online TA bookings found in current dataset slice'}

    ota_volume = len(ota_df)
    ota_cancel_rate = float(ota_df['is_canceled'].mean())
    direct_cancel_rate = float(direct_df['is_canceled'].mean()) if len(direct_df) > 0 else 0.175

    ota_adr = float(ota_df['adr'].mean())
    ota_stay = float(ota_df['total_stay_nights'].mean())
    ota_comm_rate = CHANNEL_COMMISSION_RATES.get('Online TA', 0.18)

    # Shift volume
    shift_ratio = max(0.01, min(0.50, shift_pct / 100.0))
    shifted_bookings = int(round(ota_volume * shift_ratio))

    # Baseline under OTA:
    # Realized bookings out of shifted:
    ota_realized = shifted_bookings * (1.0 - ota_cancel_rate)
    baseline_ota_gross_rev = ota_realized * ota_stay * ota_adr
    baseline_ota_commission = baseline_ota_gross_rev * ota_comm_rate
    baseline_ota_net_rev = baseline_ota_gross_rev - baseline_ota_commission

    # Shifted to Direct:
    direct_realized = shifted_bookings * (1.0 - direct_cancel_rate)
    direct_gross_rev = direct_realized * ota_stay * ota_adr
    direct_commission = 0.0  # 0% on direct
    direct_acq_cost = shifted_bookings * marketing_cost_per_direct_booking
    direct_net_rev = direct_gross_rev - direct_acq_cost

    # Metrics
    cancellations_avoided = int(round(shifted_bookings * (ota_cancel_rate - direct_cancel_rate)))
    commission_dollars_saved = round(baseline_ota_commission, 2)
    net_revenue_lift = round(direct_net_rev - baseline_ota_net_rev, 2)
    roi_multiple = round(net_revenue_lift / direct_acq_cost, 1) if direct_acq_cost > 0 else 5.0

    return {
        'shift_pct_selected': shift_pct,
        'total_ota_volume': ota_volume,
        'bookings_shifted_to_direct': shifted_bookings,
        'cancellations_avoided': cancellations_avoided,
        'baseline_cancellation_rate_pct': round(ota_cancel_rate * 100, 1),
        'new_direct_cancellation_rate_pct': round(direct_cancel_rate * 100, 1),
        'commission_dollars_saved': commission_dollars_saved,
        'direct_acquisition_investment': round(direct_acq_cost, 2),
        'net_profit_expansion': net_revenue_lift,
        'direct_shift_roi': f"{roi_multiple}x",
        'recommendation': f"Shifting {shift_pct}% of OTA reservations to Direct recovers ~{cancellations_avoided} bookings and captures ${net_revenue_lift:,.2f} in net profit after marketing expenses."
    }
