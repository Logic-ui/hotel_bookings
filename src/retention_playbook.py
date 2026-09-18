"""
Automated Guest Retention Playbook & ROI Generator for Hotel Revenue Operations.
Constructs pre-arrival engagement timelines, tailored retention incentives, and ROI calculations.
"""

from typing import Dict, Any, List


class GuestRetentionPlaybookGenerator:
    """Generates personalized pre-arrival retention sequences and calculates retention ROI."""

    def generate_playbook(self, booking_data: Dict[str, Any], cancellation_prob: float) -> Dict[str, Any]:
        lead_time = int(booking_data.get('lead_time', 30))
        adr = float(booking_data.get('adr', 100.0))
        weekend = int(booking_data.get('stays_in_weekend_nights', 1))
        week = int(booking_data.get('stays_in_week_nights', 2))
        total_nights = max(1, weekend + week)
        total_booking_value = round(adr * total_nights, 2)
        special_reqs = int(booking_data.get('total_of_special_requests', 0))
        deposit_type = str(booking_data.get('deposit_type', 'No Deposit'))

        # 1. Construct Engagement Timeline
        timeline: List[Dict[str, Any]] = []

        if lead_time >= 30:
            timeline.append({
                'timing': 'T-30 Days Prior',
                'channel': 'Email / Mobile Notification',
                'objective': 'Early Trip Commitment & Itinerary Engagement',
                'action': 'Deliver personalized destination guide, airport transfer options, and dining reservation preview.',
                'status_indicator': 'blue'
            })

        if lead_time >= 14:
            timeline.append({
                'timing': 'T-14 Days Prior',
                'channel': 'WhatsApp / SMS Concierge',
                'objective': 'Incentive Delivery & Cancellation Prevention',
                'action': 'Provide a complimentary value-add perk (e.g. Welcome Beverage, Early Check-In Priority).',
                'status_indicator': 'amber'
            })

        timeline.append({
            'timing': 'T-7 Days Prior',
            'channel': 'Email & Web Portal',
            'objective': 'Preference Confirmation & Personalization',
            'action': 'Invite guest to select room preferences (pillow menu, quiet floor, arrival window confirmation).',
            'status_indicator': 'purple'
        })

        timeline.append({
            'timing': 'T-2 Days Prior',
            'channel': 'Direct Mobile Push',
            'objective': 'Frictionless Arrival & Final Commitment',
            'action': 'Send 1-click contactless mobile check-in link and direct contact with front-desk host.',
            'status_indicator': 'green'
        })

        # 2. Tailored Incentive Recommendation
        if total_booking_value >= 500:
            incentive_title = "Complimentary Room Upgrade & Executive Lounge Access"
            incentive_cost = 25.0
            incentive_desc = "Offer a complimentary 1-tier room upgrade or late check-out voucher to secure high-value booking."
        elif total_booking_value >= 250:
            incentive_title = "Welcome Beverage & Dining Credit Voucher"
            incentive_cost = 15.0
            incentive_desc = "Deliver a $15 food & beverage welcome credit redeemable at the property restaurant or bar."
        else:
            incentive_title = "Priority Early Check-in & Welcome Drink Pass"
            incentive_cost = 8.0
            incentive_desc = "Grant priority 12:00 PM check-in and complimentary arrival mocktail/coffee."

        # 3. Financial ROI Modeling
        # Typical targeted hospitality retention interventions recover ~35% of at-risk bookings
        recovery_rate = 0.35
        expected_loss_without_action = round(total_booking_value * (cancellation_prob / 100.0), 2)
        expected_preserved_revenue = round(expected_loss_without_action * recovery_rate, 2)
        net_saved = round(max(0.0, expected_preserved_revenue - incentive_cost), 2)
        roi_multiple = round(net_saved / incentive_cost, 1) if incentive_cost > 0 else 1.0

        return {
            'total_booking_value': total_booking_value,
            'expected_loss_without_action': expected_loss_without_action,
            'expected_preserved_revenue': expected_preserved_revenue,
            'incentive': {
                'title': incentive_title,
                'cost': incentive_cost,
                'description': incentive_desc
            },
            'financial_roi': {
                'net_preserved_revenue': net_saved,
                'roi_multiple': f"{roi_multiple}x",
                'recovery_rate_pct': 35
            },
            'timeline': timeline
        }
