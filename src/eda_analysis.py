"""
Exploratory Data Analysis (EDA) & Visualization Generator for Hotel Bookings.
Calculates statistical summaries and outputs high-resolution charts.
Supports dynamic filtering by Hotel Type, Year, and Market Segment.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_pipeline import load_raw_data, clean_data, engineer_features

PALETTE = {
    'primary': '#3b82f6',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'neutral': '#64748b',
    'city_hotel': '#2563eb',
    'resort_hotel': '#059669',
    'canceled': '#f43f5e',
    'not_canceled': '#10b981'
}

MONTH_ORDER = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# In-memory dataframe cache for fast API slicing
_CACHED_DF = None


def get_cached_df(data_path: str = "hotel_bookings.csv") -> pd.DataFrame:
    global _CACHED_DF
    if _CACHED_DF is None:
        if not os.path.exists(data_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, "hotel_bookings.csv")
        raw = load_raw_data(data_path)
        cleaned = clean_data(raw)
        _CACHED_DF = engineer_features(cleaned)
    return _CACHED_DF


def compute_summary_dict(df: pd.DataFrame) -> dict:
    """Computes executive KPIs, monthly seasonality, lead times, and segments for any dataframe slice."""
    if len(df) == 0:
        return {'executive_kpis': {'total_bookings': 0, 'cancellation_rate': 0, 'avg_adr': 0, 'avg_lead_time': 0}}

    total_bookings = len(df)
    canceled_bookings = int(df['is_canceled'].sum())
    cancellation_rate = float(df['is_canceled'].mean() * 100)
    avg_adr = float(df['adr'].mean())
    avg_lead_time = float(df['lead_time'].mean())
    repeat_guest_pct = float(df['is_repeated_guest'].mean() * 100)
    avg_stay_nights = float(df['total_stay_nights'].mean())

    hotel_stats = df.groupby('hotel').agg(
        total=('is_canceled', 'count'),
        canceled=('is_canceled', 'sum'),
        cancellation_rate=('is_canceled', lambda x: round(float(x.mean() * 100), 2)),
        avg_adr=('adr', lambda x: round(float(x.mean()), 2)),
        avg_lead_time=('lead_time', lambda x: round(float(x.mean()), 1))
    ).to_dict(orient='index')

    monthly_df = df.groupby('arrival_date_month').agg(
        total_bookings=('is_canceled', 'count'),
        cancellations=('is_canceled', 'sum'),
        cancellation_rate=('is_canceled', lambda x: round(float(x.mean() * 100), 2)),
        avg_adr=('adr', lambda x: round(float(x.mean()), 2))
    ).reindex(MONTH_ORDER).fillna(0).reset_index()

    bins = [0, 7, 30, 90, 180, 365, 800]
    labels = ['0-7 days', '8-30 days', '1-3 months', '3-6 months', '6-12 months', '1+ year']
    df_temp = df.copy()
    df_temp['lead_time_bucket'] = pd.cut(df_temp['lead_time'], bins=bins, labels=labels, include_lowest=True)
    lead_time_stats = df_temp.groupby('lead_time_bucket', observed=False).agg(
        total=('is_canceled', 'count'),
        canceled=('is_canceled', 'sum'),
        rate=('is_canceled', lambda x: round(float(x.mean() * 100), 2) if len(x) > 0 else 0)
    ).to_dict(orient='index')

    market_stats = df.groupby('market_segment').agg(
        total=('is_canceled', 'count'),
        rate=('is_canceled', lambda x: round(float(x.mean() * 100), 2)),
        avg_adr=('adr', lambda x: round(float(x.mean()), 2))
    ).sort_values(by='total', ascending=False).to_dict(orient='index')

    deposit_stats = df.groupby('deposit_type').agg(
        total=('is_canceled', 'count'),
        rate=('is_canceled', lambda x: round(float(x.mean() * 100), 2))
    ).to_dict(orient='index')

    top_countries = df.groupby('country').agg(
        total=('is_canceled', 'count'),
        rate=('is_canceled', lambda x: round(float(x.mean() * 100), 2))
    ).sort_values(by='total', ascending=False).head(10).to_dict(orient='index')

    special_req_stats = df.groupby('total_of_special_requests').agg(
        total=('is_canceled', 'count'),
        rate=('is_canceled', lambda x: round(float(x.mean() * 100), 2))
    ).head(6).to_dict(orient='index')

    # Room allocation mismatch analysis
    data_room = df.copy()
    data_room['room_upgraded'] = (data_room['reserved_room_type'] != data_room['assigned_room_type']).astype(int)
    exact_match = data_room[data_room['room_upgraded'] == 0]
    upgraded = data_room[data_room['room_upgraded'] == 1]

    room_allocation = {
        'same_room': {
            'total': int(len(exact_match)),
            'pct_share': round(float(len(exact_match) / total_bookings * 100), 1),
            'cancellation_rate': round(float(exact_match['is_canceled'].mean() * 100), 2) if len(exact_match) > 0 else 0,
            'avg_adr': round(float(exact_match['adr'].mean()), 2) if len(exact_match) > 0 else 0
        },
        'upgraded_room': {
            'total': int(len(upgraded)),
            'pct_share': round(float(len(upgraded) / total_bookings * 100), 1),
            'cancellation_rate': round(float(upgraded['is_canceled'].mean() * 100), 2) if len(upgraded) > 0 else 0,
            'avg_adr': round(float(upgraded['adr'].mean()), 2) if len(upgraded) > 0 else 0
        },
        'upgrade_retention_advantage': round(float((exact_match['is_canceled'].mean() - upgraded['is_canceled'].mean()) * 100), 1) if len(exact_match) > 0 and len(upgraded) > 0 else 0
    }

    return {
        'executive_kpis': {
            'total_bookings': total_bookings,
            'canceled_bookings': canceled_bookings,
            'cancellation_rate': round(cancellation_rate, 2),
            'avg_adr': round(avg_adr, 2),
            'avg_lead_time': round(avg_lead_time, 1),
            'repeat_guest_pct': round(repeat_guest_pct, 2),
            'avg_stay_nights': round(avg_stay_nights, 1)
        },
        'hotel_breakdown': hotel_stats,
        'monthly_trends': monthly_df.to_dict(orient='records'),
        'lead_time_breakdown': {str(k): v for k, v in lead_time_stats.items()},
        'market_segments': market_stats,
        'deposit_types': deposit_stats,
        'top_countries': top_countries,
        'special_requests': {str(k): v for k, v in special_req_stats.items()},
        'room_allocation_matrix': room_allocation
    }


def get_filtered_summary(hotel: str = None, year: int = None, market_segment: str = None) -> dict:
    """Returns dynamic summary metrics filtered by hotel, year, and/or market segment."""
    df = get_cached_df()
    if hotel and hotel != "All":
        df = df[df['hotel'] == hotel]
    if year and year != "All" and str(year).isdigit():
        df = df[df['arrival_date_year'] == int(year)]
    if market_segment and market_segment != "All":
        df = df[df['market_segment'] == market_segment]
    return compute_summary_dict(df)


def run_full_eda(data_path: str = "hotel_bookings.csv", output_dir: str = "outputs"):
    os.makedirs(os.path.join(output_dir, "figures"), exist_ok=True)
    df_raw = load_raw_data(data_path)
    df = clean_data(df_raw)
    df = engineer_features(df)

    summary_data = compute_summary_dict(df)
    json_path = os.path.join(output_dir, "eda_summary.json")
    with open(json_path, 'w') as f:
        json.dump(summary_data, f, indent=2)
    print(f"Saved summary JSON to {json_path}")

    monthly_df = pd.DataFrame(summary_data['monthly_trends'])
    _generate_figures(df, monthly_df, output_dir)
    print("All EDA figures generated successfully!")
    return summary_data


def _generate_figures(df: pd.DataFrame, monthly_df: pd.DataFrame, output_dir: str):
    fig_dir = os.path.join(output_dir, "figures")
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # 1. Hotel Type vs Cancellation Rate
    plt.figure(figsize=(8, 5))
    hotel_cancel = df.groupby(['hotel', 'is_canceled']).size().unstack(fill_value=0)
    hotel_cancel_pct = hotel_cancel.div(hotel_cancel.sum(axis=1), axis=0) * 100
    ax = hotel_cancel_pct.plot(kind='bar', stacked=True, color=[PALETTE['not_canceled'], PALETTE['canceled']], figsize=(8, 5))
    plt.title('Booking Status Proportion by Hotel Type', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Hotel Type', fontsize=11)
    plt.ylabel('Percentage (%)', fontsize=11)
    plt.xticks(rotation=0)
    plt.legend(['Checked Out / Retained', 'Canceled'], frameon=True)
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        if height > 5:
            x, y = p.get_xy()
            ax.text(x + width/2, y + height/2, f'{height:.1f}%', ha='center', va='center', color='white', fontweight='bold', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "1_cancellation_by_hotel.png"), dpi=300)
    plt.close()

    # 2. Monthly Booking Volume & Cancellation Rate
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    x = np.arange(len(MONTH_ORDER))
    width = 0.5
    ax1.bar(x, monthly_df['total_bookings'], width, color='#38bdf8', alpha=0.85, label='Total Bookings')
    ax2.plot(x, monthly_df['cancellation_rate'], color='#e11d48', marker='o', linewidth=2.5, label='Cancellation Rate (%)')
    
    ax1.set_xlabel('Arrival Month', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Total Bookings', color='#0284c7', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Cancellation Rate (%)', color='#e11d48', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(MONTH_ORDER, rotation=45, ha='right')
    plt.title('Monthly Booking Volume and Cancellation Rate Dynamics', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(False)
    ax2.grid(True, linestyle='--', alpha=0.5)
    fig.tight_layout()
    plt.savefig(os.path.join(fig_dir, "2_monthly_seasonality.png"), dpi=300)
    plt.close()

    # 3. Lead Time vs Cancellation
    plt.figure(figsize=(9, 5))
    bins = [0, 7, 30, 90, 180, 365, 800]
    labels = ['0-7d', '8-30d', '1-3m', '3-6m', '6-12m', '1y+']
    df_temp = df.copy()
    df_temp['lt_group'] = pd.cut(df_temp['lead_time'], bins=bins, labels=labels, include_lowest=True)
    lt_rates = df_temp.groupby('lt_group', observed=False)['is_canceled'].mean() * 100
    bars = plt.bar(lt_rates.index, lt_rates.values, color='#6366f1', edgecolor='#4338ca', alpha=0.85)
    plt.title('Cancellation Probability by Lead Time Horizon', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Lead Time Horizon (Days between Booking & Check-in)', fontsize=11)
    plt.ylabel('Cancellation Rate (%)', fontsize=11)
    plt.ylim(0, 100)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 2, f'{h:.1f}%', ha='center', fontweight='bold', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "3_lead_time_cancellation.png"), dpi=300)
    plt.close()

    # 4. Market Segment Cancellation Rate
    plt.figure(figsize=(10, 5))
    ms_order = df['market_segment'].value_counts().index
    ms_rate = df.groupby('market_segment')['is_canceled'].mean().loc[ms_order] * 100
    bars = plt.barh(ms_order[::-1], ms_rate.values[::-1], color='#0ea5e9', edgecolor='#0284c7')
    plt.title('Cancellation Rate Across Market Segments', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Cancellation Rate (%)', fontsize=11)
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 1, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center', fontweight='bold', fontsize=10)
    plt.xlim(0, max(ms_rate.values) + 12)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "4_market_segment_analysis.png"), dpi=300)
    plt.close()

    # 5. Deposit Type Paradox
    plt.figure(figsize=(7, 5))
    dt_rates = df.groupby('deposit_type')['is_canceled'].mean() * 100
    bars = plt.bar(dt_rates.index, dt_rates.values, color=['#10b981', '#ef4444', '#f59e0b'])
    plt.title('Deposit Type Cancellation Rate (The Deposit Paradox)', fontsize=14, fontweight='bold', pad=15)
    plt.ylabel('Cancellation Rate (%)', fontsize=11)
    plt.ylim(0, 110)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 2, f'{h:.1f}%', ha='center', fontweight='bold', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "5_deposit_type_paradox.png"), dpi=300)
    plt.close()

    # 6. ADR Distribution by Hotel Type
    plt.figure(figsize=(9, 5))
    sns.boxplot(x='hotel', y='adr', hue='is_canceled', data=df[df['adr'] <= 350],
                palette=[PALETTE['not_canceled'], PALETTE['canceled']])
    plt.title('Average Daily Rate (ADR) Distribution by Hotel & Status', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Hotel Type', fontsize=11)
    plt.ylabel('Average Daily Rate ($)', fontsize=11)
    plt.legend(['Not Canceled', 'Canceled'], title='Booking Status', frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "6_adr_distribution_by_hotel.png"), dpi=300)
    plt.close()

    # 7. Special Requests vs Cancellation
    plt.figure(figsize=(8, 5))
    sr_df = df[df['total_of_special_requests'] <= 4]
    sr_rate = sr_df.groupby('total_of_special_requests')['is_canceled'].mean() * 100
    bars = plt.bar(sr_rate.index.astype(str), sr_rate.values, color='#8b5cf6', edgecolor='#6d28d9')
    plt.title('Cancellation Rate by Number of Special Requests', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Total Special Requests', fontsize=11)
    plt.ylabel('Cancellation Rate (%)', fontsize=11)
    plt.ylim(0, 60)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 1.5, f'{h:.1f}%', ha='center', fontweight='bold', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "7_special_requests_impact.png"), dpi=300)
    plt.close()

    # 8. Top 10 Origin Countries
    plt.figure(figsize=(10, 5))
    top10_c = df['country'].value_counts().head(10)
    bars = plt.bar(top10_c.index, top10_c.values, color='#059669', edgecolor='#047857')
    plt.title('Top 10 Origin Countries of Hotel Guests', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Country Code', fontsize=11)
    plt.ylabel('Total Bookings', fontsize=11)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, h + 500, f'{h:,}', ha='center', fontweight='bold', fontsize=8, rotation=25)
    plt.ylim(0, max(top10_c.values) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "8_top_origin_countries.png"), dpi=300)
    plt.close()
