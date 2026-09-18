/**
 * GrandHorizon Hotel Analytics & Prediction Suite
 * Frontend Interactive Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initFormControls();
  fetchSummaryData();
  fetchModelBenchmark();
  initPredictionForm();
});

// TAB SWITCHING
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');

      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add('active');
      }
    });
  });
}

// SLIDER BADGE UPDATER
function initFormControls() {
  const leadSlider = document.getElementById('p-lead-time');
  const leadVal = document.getElementById('val-lead-time');
  if (leadSlider && leadVal) {
    leadSlider.addEventListener('input', (e) => {
      leadVal.textContent = `${e.target.value} days`;
    });
  }
}

// FETCH SUMMARY DATA & RENDER EDA CHARTS
async function fetchSummaryData() {
  try {
    const res = await fetch('/api/summary');
    if (!res.ok) throw new Error('EDA summary not ready yet');
    const data = await res.json();

    // 1. Update Executive KPIs
    const kpis = data.executive_kpis;
    if (kpis) {
      document.getElementById('kpi-total').textContent = kpis.total_bookings.toLocaleString();
      document.getElementById('kpi-cancel-rate').textContent = `${kpis.cancellation_rate}%`;
      document.getElementById('kpi-adr').textContent = `$${kpis.avg_adr.toFixed(2)}`;
      document.getElementById('kpi-lead-time').textContent = `${kpis.avg_lead_time.toFixed(1)} Days`;
    }

    // 2. Update Hotel Breakdown
    const hotels = data.hotel_breakdown;
    if (hotels) {
      if (hotels['City Hotel']) {
        document.getElementById('city-total').textContent = hotels['City Hotel'].total.toLocaleString();
        document.getElementById('city-rate').textContent = `${hotels['City Hotel'].cancellation_rate}%`;
        document.getElementById('city-adr').textContent = `$${hotels['City Hotel'].avg_adr.toFixed(2)}`;
        document.getElementById('city-lead').textContent = `${hotels['City Hotel'].avg_lead_time} days`;
      }
      if (hotels['Resort Hotel']) {
        document.getElementById('resort-total').textContent = hotels['Resort Hotel'].total.toLocaleString();
        document.getElementById('resort-rate').textContent = `${hotels['Resort Hotel'].cancellation_rate}%`;
        document.getElementById('resort-adr').textContent = `$${hotels['Resort Hotel'].avg_adr.toFixed(2)}`;
        document.getElementById('resort-lead').textContent = `${hotels['Resort Hotel'].avg_lead_time} days`;
      }
    }

    // 3. Render Monthly Chart
    renderMonthlyChart(data.monthly_trends);

    // 4. Render Lead Time Chart
    renderLeadTimeChart(data.lead_time_breakdown);

    // 5. Render Market Segment Chart
    renderMarketSegmentChart(data.market_segments);

    // 6. Render Deposit Type Chart
    renderDepositTypeChart(data.deposit_types);

    // 7. Render Special Requests Chart
    renderSpecialRequestsChart(data.special_requests);

  } catch (err) {
    console.warn("Summary data notice:", err.message);
  }
}

// 1. Monthly Seasonality Chart
function renderMonthlyChart(trends) {
  const ctx = document.getElementById('chart-monthly');
  if (!ctx || !trends) return;

  const months = trends.map(t => t.arrival_date_month);
  const bookings = trends.map(t => t.total_bookings);
  const rates = trends.map(t => t.cancellation_rate);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: months,
      datasets: [
        {
          label: 'Total Bookings',
          data: bookings,
          backgroundColor: 'rgba(56, 189, 248, 0.45)',
          borderColor: '#38bdf8',
          borderWidth: 1.5,
          borderRadius: 6,
          yAxisID: 'y'
        },
        {
          label: 'Cancellation Rate (%)',
          data: rates,
          type: 'line',
          borderColor: '#f43f5e',
          backgroundColor: '#f43f5e',
          borderWidth: 3,
          pointRadius: 4,
          pointHoverRadius: 6,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#94a3b8' } },
        y: {
          type: 'linear',
          position: 'left',
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#38bdf8' },
          title: { display: true, text: 'Total Bookings', color: '#38bdf8' }
        },
        y1: {
          type: 'linear',
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#f43f5e', callback: v => `${v}%` },
          title: { display: true, text: 'Cancellation Rate (%)', color: '#f43f5e' }
        }
      },
      plugins: {
        legend: { labels: { color: '#f8fafc', font: { family: 'Plus Jakarta Sans' } } }
      }
    }
  });
}

// 2. Lead Time Horizon Chart
function renderLeadTimeChart(leadData) {
  const ctx = document.getElementById('chart-leadtime');
  if (!ctx || !leadData) return;

  const labels = Object.keys(leadData);
  const rates = labels.map(k => leadData[k].rate);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Cancellation Rate (%)',
        data: rates,
        backgroundColor: [
          '#10b981', '#34d399', '#f59e0b', '#f97316', '#ef4444', '#b91c1c'
        ],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#94a3b8', callback: v => `${v}%` },
          max: 80
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// 3. Market Segment Chart
function renderMarketSegmentChart(segmentData) {
  const ctx = document.getElementById('chart-market');
  if (!ctx || !segmentData) return;

  const labels = Object.keys(segmentData).filter(s => s !== 'Undefined');
  const rates = labels.map(k => segmentData[k].rate);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        axis: 'y',
        label: 'Cancellation Rate (%)',
        data: rates,
        backgroundColor: 'rgba(99, 102, 241, 0.7)',
        borderColor: '#6366f1',
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#94a3b8', callback: v => `${v}%` },
          max: 100
        },
        y: { grid: { display: false }, ticks: { color: '#94a3b8' } }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// 4. Deposit Type Chart
function renderDepositTypeChart(depositData) {
  const ctx = document.getElementById('chart-deposit');
  if (!ctx || !depositData) return;

  const labels = Object.keys(depositData);
  const rates = labels.map(k => depositData[k].rate);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Cancellation Rate (%)',
        data: rates,
        backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#94a3b8', callback: v => `${v}%` },
          max: 100
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// 5. Special Requests Chart
function renderSpecialRequestsChart(srData) {
  const ctx = document.getElementById('chart-special-requests');
  if (!ctx || !srData) return;

  const labels = Object.keys(srData).map(k => `${k} Requests`);
  const rates = Object.keys(srData).map(k => srData[k].rate);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Cancellation Rate (%)',
        data: rates,
        borderColor: '#a855f7',
        backgroundColor: 'rgba(168, 85, 247, 0.15)',
        fill: true,
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#94a3b8' } },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#94a3b8', callback: v => `${v}%` },
          min: 0,
          max: 50
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// FETCH MODEL BENCHMARK & RENDER FEATURE IMPORTANCES
async function fetchModelBenchmark() {
  try {
    const res = await fetch('/api/model-metrics');
    if (!res.ok) throw new Error('Metrics not available yet');
    const data = await res.json();

    const tbody = document.getElementById('benchmark-tbody');
    if (tbody && data.models_benchmark) {
      tbody.innerHTML = '';
      const best = data.best_model;

      for (const [modelName, m] of Object.entries(data.models_benchmark)) {
        const isBest = modelName === best;
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>
            <strong>${modelName}</strong>
            ${isBest ? '<span class="badge badge-success" style="margin-left: 6px;">Champion</span>' : ''}
          </td>
          <td>${(m.accuracy * 100).toFixed(2)}%</td>
          <td>${(m.precision * 100).toFixed(2)}%</td>
          <td>${(m.recall * 100).toFixed(2)}%</td>
          <td>${m.f1_score.toFixed(4)}</td>
          <td><strong style="color: #38bdf8;">${m.roc_auc.toFixed(4)}</strong></td>
          <td>${m.train_time_seconds ? m.train_time_seconds + 's' : 'N/A'}</td>
          <td>
            <span class="badge ${isBest ? 'badge-primary' : 'badge-info'}">
              ${isBest ? 'Active Production' : 'Evaluated'}
            </span>
          </td>
        `;
        tbody.appendChild(tr);
      }
    }

    // Render Feature Importances Chart
    if (data.top_feature_importances && data.top_feature_importances.length > 0) {
      renderFeaturesChart(data.top_feature_importances.slice(0, 10));
    }
  } catch (err) {
    console.warn("Benchmark notice:", err.message);
  }
}

function renderFeaturesChart(features) {
  const ctx = document.getElementById('chart-features');
  if (!ctx || !features) return;

  const labels = features.map(f => f.feature.replace(/_/g, ' '));
  const values = features.map(f => f.importance);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        axis: 'y',
        label: 'Importance Score',
        data: values,
        backgroundColor: 'rgba(14, 165, 233, 0.7)',
        borderColor: '#0ea5e9',
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { display: false }, ticks: { color: '#f8fafc', font: { size: 11 } } }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// LIVE PREDICTION FORM HANDLER
function initPredictionForm() {
  const form = document.getElementById('prediction-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const payload = {
      hotel: formData.get('hotel'),
      arrival_date_month: formData.get('arrival_date_month'),
      lead_time: parseInt(formData.get('lead_time')),
      stays_in_weekend_nights: parseInt(formData.get('stays_in_weekend_nights')),
      stays_in_week_nights: parseInt(formData.get('stays_in_week_nights')),
      adults: parseInt(formData.get('adults')),
      children: parseInt(formData.get('children')),
      market_segment: formData.get('market_segment'),
      deposit_type: formData.get('deposit_type'),
      adr: parseFloat(formData.get('adr')),
      total_of_special_requests: parseInt(formData.get('total_of_special_requests')),
      previous_cancellations: parseInt(formData.get('previous_cancellations')),
      is_repeated_guest: parseInt(formData.get('is_repeated_guest'))
    };

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Evaluating Reservation Risk...';

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errJson = await res.json();
        throw new Error(errJson.detail || 'Prediction failed');
      }

      const result = await res.json();
      displayPredictionResult(result);

    } catch (err) {
      alert(`Prediction Error: ${err.message}`);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });
}

function displayPredictionResult(result) {
  const gaugePercent = document.getElementById('gauge-percent');
  const gaugeCircle = document.getElementById('gauge-circle');
  const riskBadge = document.getElementById('risk-badge');
  const driversList = document.getElementById('drivers-list');
  const recList = document.getElementById('rec-list');

  // Probability and Color
  const pct = result.cancellation_probability;
  gaugePercent.textContent = `${pct}%`;
  gaugePercent.style.color = result.risk_color;
  gaugeCircle.style.borderColor = result.risk_color;
  gaugeCircle.style.boxShadow = `0 0 30px ${result.risk_color}40`;

  // Badge
  riskBadge.textContent = result.risk_tier.toUpperCase();
  riskBadge.className = `risk-badge-large badge-${result.risk_badge}`;
  riskBadge.style.background = `${result.risk_color}20`;
  riskBadge.style.color = result.risk_color;
  riskBadge.style.borderColor = result.risk_color;

  // Drivers
  driversList.innerHTML = '';
  result.key_drivers.forEach(driver => {
    const li = document.createElement('li');
    li.textContent = driver;
    driversList.appendChild(li);
  });

  // Recommendations
  recList.innerHTML = '';
  result.recommended_actions.forEach(rec => {
    const li = document.createElement('li');
    li.textContent = rec;
    recList.appendChild(li);
  });
}
