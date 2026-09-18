/**
 * GrandHorizon Hotel Analytics, Batch Audit & ML Suite
 * Frontend Interactive Dashboard Controller (v2.0)
 * Features: Count-Up Animations, SVG Gauge, Toast System, Live Table Search
 */

let charts = {};
let currentBatchRecords = [];

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initFormControls();
  initFilters();
  initBatchAudit();
  initOverbookingSimulator();
  initPredictionForm();
  initGeoSearch();
  
  fetchSummaryData();
  fetchModelBenchmark();
  fetchGeoAnalytics();
  runOverbookingSimulation(); // Initial calculation
  
  showToast("Welcome to GrandHorizon Analytics v3.0", "info", "fa-hotel");
});

// TOAST NOTIFICATION SYSTEM
function showToast(message, type = 'info', icon = 'fa-circle-info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentNode) toast.parentNode.removeChild(toast);
  }, 4000);
}

// NUMBER COUNT-UP ANIMATION
function animateCountUp(element, endVal, prefix = '', suffix = '', decimals = 0, duration = 1000) {
  if (!element) return;
  const startVal = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const easeOut = 1 - Math.pow(1 - progress, 3);
    const currentVal = startVal + (endVal - startVal) * easeOut;

    let formattedVal;
    if (decimals > 0) {
      formattedVal = currentVal.toFixed(decimals);
    } else {
      formattedVal = Math.round(currentVal).toLocaleString();
    }

    element.textContent = `${prefix}${formattedVal}${suffix}`;

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

// 1. TAB SWITCHING
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

// 2. SLIDER BADGES
function initFormControls() {
  const leadSlider = document.getElementById('p-lead-time');
  const leadVal = document.getElementById('val-lead-time');
  if (leadSlider && leadVal) {
    leadSlider.addEventListener('input', (e) => {
      leadVal.textContent = `${e.target.value} days`;
    });
  }

  // Simulator sliders
  const setupSlider = (id, badgeId, prefix = '', suffix = '') => {
    const s = document.getElementById(id);
    const b = document.getElementById(badgeId);
    if (s && b) {
      s.addEventListener('input', (e) => {
        b.textContent = `${prefix}${e.target.value}${suffix}`;
      });
    }
  };

  setupSlider('sim-capacity', 'val-sim-capacity', '', ' rooms');
  setupSlider('sim-adr', 'val-sim-adr', '$', '');
  setupSlider('sim-cancel-rate', 'val-sim-cancel', '', '%');
  setupSlider('sim-walk-cost', 'val-sim-walk', '$', '');
}

// 3. DYNAMIC FILTER SLICERS
function initFilters() {
  const fHotel = document.getElementById('filter-hotel');
  const fYear = document.getElementById('filter-year');
  const fMarket = document.getElementById('filter-market');
  const btnReset = document.getElementById('btn-reset-filters');

  const onFilterChange = () => {
    fetchSummaryData(true);
  };

  if (fHotel) fHotel.addEventListener('change', onFilterChange);
  if (fYear) fYear.addEventListener('change', onFilterChange);
  if (fMarket) fMarket.addEventListener('change', onFilterChange);

  if (btnReset) {
    btnReset.addEventListener('click', () => {
      if (fHotel) fHotel.value = 'All';
      if (fYear) fYear.value = 'All';
      if (fMarket) fMarket.value = 'All';
      fetchSummaryData(true);
      showToast("Filters reset to default view", "info", "fa-rotate-left");
    });
  }
}

// 4. FETCH SUMMARY DATA & RENDER CHARTS
async function fetchSummaryData(isUserFilter = false) {
  const fHotel = document.getElementById('filter-hotel')?.value || 'All';
  const fYear = document.getElementById('filter-year')?.value || 'All';
  const fMarket = document.getElementById('filter-market')?.value || 'All';
  const spinner = document.getElementById('filter-loading');

  if (spinner) spinner.style.display = 'inline-block';

  try {
    const params = new URLSearchParams();
    if (fHotel !== 'All') params.append('hotel', fHotel);
    if (fYear !== 'All') params.append('year', fYear);
    if (fMarket !== 'All') params.append('market', fMarket);

    const res = await fetch(`/api/summary?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch summary');
    const data = await res.json();

    // Update KPIs with count-up animation
    const kpis = data.executive_kpis;
    if (kpis) {
      animateCountUp(document.getElementById('kpi-total'), kpis.total_bookings);
      animateCountUp(document.getElementById('kpi-cancel-rate'), kpis.cancellation_rate, '', '%', 2);
      animateCountUp(document.getElementById('kpi-adr'), kpis.avg_adr, '$', '', 2);
      animateCountUp(document.getElementById('kpi-lead-time'), kpis.avg_lead_time, '', ' Days', 1);

      if (kpis.canceled_bookings !== undefined) {
        document.getElementById('kpi-cancel-count').innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${kpis.canceled_bookings.toLocaleString()} Canceled`;
      }
    }

    // Update Hotel Breakdown
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

    // Render Charts
    renderMonthlyChart(data.monthly_trends);
    renderLeadTimeChart(data.lead_time_breakdown);
    renderMarketSegmentChart(data.market_segments);
    renderDepositTypeChart(data.deposit_types);
    renderSpecialRequestsChart(data.special_requests);

    if (isUserFilter) {
      showToast(`Filters applied: ${kpis.total_bookings.toLocaleString()} bookings found`, "success", "fa-filter");
    }

  } catch (err) {
    console.warn("Summary fetch error:", err.message);
  } finally {
    if (spinner) spinner.style.display = 'none';
  }
}

// Chart Helpers
function destroyChart(key) {
  if (charts[key]) {
    charts[key].destroy();
    charts[key] = null;
  }
}

function renderMonthlyChart(trends) {
  const ctx = document.getElementById('chart-monthly');
  if (!ctx || !trends) return;
  destroyChart('monthly');

  const months = trends.map(t => t.arrival_date_month);
  const bookings = trends.map(t => t.total_bookings);
  const rates = trends.map(t => t.cancellation_rate);

  charts['monthly'] = new Chart(ctx, {
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
          borderRadius: 8,
          yAxisID: 'y'
        },
        {
          label: 'Cancellation Rate (%)',
          data: rates,
          type: 'line',
          borderColor: '#f43f5e',
          backgroundColor: 'rgba(244, 63, 94, 0.1)',
          fill: true,
          borderWidth: 3,
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: '#f43f5e',
          tension: 0.35,
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
        legend: { labels: { color: '#f8fafc', font: { family: 'Plus Jakarta Sans', size: 12 } } }
      }
    }
  });
}

function renderLeadTimeChart(leadData) {
  const ctx = document.getElementById('chart-leadtime');
  if (!ctx || !leadData) return;
  destroyChart('leadtime');

  const labels = Object.keys(leadData);
  const rates = labels.map(k => leadData[k].rate);

  charts['leadtime'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Cancellation Rate (%)',
        data: rates,
        backgroundColor: ['#10b981', '#34d399', '#f59e0b', '#f97316', '#ef4444', '#b91c1c'],
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
          max: 85
        }
      },
      plugins: { legend: { display: false } }
    }
  });
}

function renderMarketSegmentChart(segmentData) {
  const ctx = document.getElementById('chart-market');
  if (!ctx || !segmentData) return;
  destroyChart('market');

  const labels = Object.keys(segmentData).filter(s => s !== 'Undefined');
  const rates = labels.map(k => segmentData[k].rate);

  charts['market'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        axis: 'y',
        label: 'Cancellation Rate (%)',
        data: rates,
        backgroundColor: 'rgba(99, 102, 241, 0.75)',
        borderColor: '#6366f1',
        borderWidth: 1.5,
        borderRadius: 8
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
      plugins: { legend: { display: false } }
    }
  });
}

function renderDepositTypeChart(depositData) {
  const ctx = document.getElementById('chart-deposit');
  if (!ctx || !depositData) return;
  destroyChart('deposit');

  const labels = Object.keys(depositData);
  const rates = labels.map(k => depositData[k].rate);

  charts['deposit'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Cancellation Rate (%)',
        data: rates,
        backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
        borderRadius: 10
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
      plugins: { legend: { display: false } }
    }
  });
}

function renderSpecialRequestsChart(srData) {
  const ctx = document.getElementById('chart-special-requests');
  if (!ctx || !srData) return;
  destroyChart('special');

  const labels = Object.keys(srData).map(k => `${k} Requests`);
  const rates = Object.keys(srData).map(k => srData[k].rate);

  charts['special'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Cancellation Rate (%)',
        data: rates,
        borderColor: '#a855f7',
        backgroundColor: 'rgba(168, 85, 247, 0.18)',
        fill: true,
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 8,
        pointBackgroundColor: '#a855f7',
        tension: 0.35
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
      plugins: { legend: { display: false } }
    }
  });
}

// 5. FETCH MODEL BENCHMARK
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
            ${isBest ? '<span class="badge badge-success" style="margin-left: 6px;"><i class="fa-solid fa-crown"></i> Champion</span>' : ''}
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
  destroyChart('features');

  const labels = features.map(f => f.feature.replace(/_/g, ' '));
  const values = features.map(f => f.importance);

  charts['features'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        axis: 'y',
        label: 'Importance Score',
        data: values,
        backgroundColor: 'rgba(14, 165, 233, 0.75)',
        borderColor: '#0ea5e9',
        borderWidth: 1.5,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#94a3b8' } },
        y: { grid: { display: false }, ticks: { color: '#f8fafc', font: { size: 11, weight: '500' } } }
      },
      plugins: { legend: { display: false } }
    }
  });
}

// 6. LIVE PREDICTION FORM & DYNAMIC PRICING
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
      reserved_room_type: formData.get('reserved_room_type'),
      market_segment: formData.get('market_segment'),
      deposit_type: formData.get('deposit_type'),
      adr: parseFloat(formData.get('adr')),
      total_of_special_requests: parseInt(formData.get('total_of_special_requests')),
      previous_cancellations: parseInt(formData.get('previous_cancellations'))
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
      showToast(`Risk Evaluated: ${result.risk_tier} (${result.cancellation_probability}%)`, result.risk_badge, "fa-wand-magic-sparkles");

    } catch (err) {
      alert(`Prediction Error: ${err.message}`);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });
}

// Modern SVG Circle Gauge Updater
function updateSVGGauge(percent, color) {
  const circle = document.getElementById('gauge-svg-fill');
  if (!circle) return;

  // Circumference for r=68 is ~427.26
  const totalLength = 427.26;
  const offset = totalLength - (percent / 100) * totalLength;

  circle.style.strokeDashoffset = offset;
  circle.style.stroke = color;
  circle.style.filter = `drop-shadow(0 0 12px ${color}80)`;
}

function displayPredictionResult(result) {
  const gaugePercent = document.getElementById('gauge-percent');
  const riskBadge = document.getElementById('risk-badge');
  const driversList = document.getElementById('drivers-list');
  const recList = document.getElementById('rec-list');

  const pct = result.cancellation_probability;
  animateCountUp(gaugePercent, pct, '', '%', 1, 800);
  gaugePercent.style.color = result.risk_color;

  updateSVGGauge(pct, result.risk_color);

  riskBadge.textContent = result.risk_tier.toUpperCase();
  riskBadge.className = `risk-badge-large badge-${result.risk_badge}`;
  riskBadge.style.background = `${result.risk_color}20`;
  riskBadge.style.color = result.risk_color;
  riskBadge.style.borderColor = result.risk_color;
  riskBadge.style.boxShadow = `0 0 15px ${result.risk_color}30`;

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

  // Dynamic Pricing Guidance
  const pBox = document.getElementById('pricing-box');
  if (pBox && result.pricing_recommendation) {
    pBox.style.display = 'block';
    const pr = result.pricing_recommendation;
    document.getElementById('price-target').textContent = `$${pr.target_adr.toFixed(2)}`;
    document.getElementById('price-range').textContent = `$${pr.price_range.min.toFixed(2)} - $${pr.price_range.max.toFixed(2)}`;
    document.getElementById('price-guidance').textContent = pr.strategic_guidance;

    const sBadge = document.getElementById('price-season-badge');
    sBadge.textContent = pr.season_category;
    sBadge.className = `badge badge-${pr.season_badge}`;
  }

  // Retention Playbook (NEW in v3.0)
  const pbBox = document.getElementById('playbook-box');
  if (pbBox && result.retention_playbook) {
    pbBox.style.display = 'block';
    const pb = result.retention_playbook;

    document.getElementById('playbook-roi-badge').textContent = `ROI: ${pb.financial_roi.roi_multiple}`;
    document.getElementById('incentive-title').textContent = pb.incentive.title;
    document.getElementById('incentive-desc').textContent = pb.incentive.description;
    document.getElementById('incentive-cost').textContent = `$${pb.incentive.cost.toFixed(2)}`;
    document.getElementById('incentive-saved').textContent = `+$${pb.financial_roi.net_preserved_revenue.toFixed(2)}`;

    const tList = document.getElementById('playbook-timeline');
    if (tList) {
      tList.innerHTML = '';
      pb.timeline.forEach(step => {
        const div = document.createElement('div');
        div.className = 'timeline-step';
        div.innerHTML = `
          <span class="step-timing"><i class="fa-solid fa-clock"></i> ${step.timing}</span>
          <div class="step-action">
            <strong>${step.objective}</strong>
            <p>${step.action}</p>
          </div>
        `;
        tList.appendChild(div);
      });
    }
  }
}

// 7. BATCH CSV AUDIT
function initBatchAudit() {
  const dropzone = document.getElementById('csv-dropzone');
  const fileInput = document.getElementById('batch-file-input');
  const btnSample = document.getElementById('btn-load-sample');
  const btnExport = document.getElementById('btn-export-enriched-csv');
  const searchInput = document.getElementById('batch-search-input');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleBatchUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleBatchUpload(e.target.files[0]);
    }
  });

  // Live Table Search Filter
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      filterBatchTable(e.target.value);
    });
  }

  // Load sample demo batch
  if (btnSample) {
    btnSample.addEventListener('click', async () => {
      btnSample.disabled = true;
      btnSample.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating 50 Bookings...';
      try {
        const res = await fetch('/api/sample-batch-csv');
        if (!res.ok) throw new Error('Failed to load sample batch');
        const blob = await res.blob();
        const file = new File([blob], 'sample_reservations.csv', { type: 'text/csv' });
        await handleBatchUpload(file);
      } catch (err) {
        alert(`Sample Load Error: ${err.message}`);
      } finally {
        btnSample.disabled = false;
        btnSample.innerHTML = '<i class="fa-solid fa-flask"></i> Load Demo Sample (50 Bookings)';
      }
    });
  }

  // Export Enriched CSV
  if (btnExport) {
    btnExport.addEventListener('click', () => {
      if (currentBatchRecords.length === 0) return;
      const headers = ["Row", "Hotel", "Lead Time", "Arrival Month", "ADR", "Stay Nights", "Total Value", "Cancellation Risk (%)", "Predicted Cancellation", "Risk Tier"];
      const rows = currentBatchRecords.map(r => [
        r.row_id,
        r.hotel,
        r.lead_time,
        r.arrival_date_month,
        r.adr,
        r.total_stay_nights,
        r.total_value,
        r.cancellation_probability,
        r.predicted_cancellation,
        r.risk_tier
      ]);

      const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `audited_reservations_risk_report.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      showToast("Audited CSV downloaded successfully!", "success", "fa-download");
    });
  }
}

async function handleBatchUpload(file) {
  const formData = new FormData();
  formData.append('file', file);

  const dropzone = document.getElementById('csv-dropzone');
  const origHTML = dropzone.innerHTML;
  dropzone.innerHTML = `
    <i class="fa-solid fa-spinner fa-spin dropzone-icon"></i>
    <p class="dropzone-text">Auditing reservations & calculating revenue at risk...</p>
  `;

  try {
    const res = await fetch('/api/predict-batch', {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Batch prediction failed');
    }

    const data = await res.json();
    renderBatchResults(data);
    showToast(`Batch Audit Complete: ${data.summary.total_reservations} bookings analyzed`, "success", "fa-file-circle-check");

  } catch (err) {
    alert(`Batch Processing Error: ${err.message}`);
  } finally {
    dropzone.innerHTML = origHTML;
  }
}

function renderBatchResults(data) {
  const resultsArea = document.getElementById('batch-results-area');
  if (!resultsArea) return;
  resultsArea.style.display = 'block';

  const s = data.summary;
  currentBatchRecords = data.records || [];

  // Animate Batch KPIs
  animateCountUp(document.getElementById('batch-kpi-total'), s.total_reservations);
  document.getElementById('batch-kpi-revenue').textContent = `Pipeline: $${s.total_pipeline_revenue.toLocaleString()}`;
  animateCountUp(document.getElementById('batch-kpi-cancels'), s.predicted_cancellations);
  document.getElementById('batch-kpi-rate').textContent = `Rate: ${s.predicted_cancellation_rate}%`;
  animateCountUp(document.getElementById('batch-kpi-risk'), s.revenue_at_risk, '$', '', 0);
  document.getElementById('batch-kpi-risk-pct').textContent = `${s.revenue_at_risk_pct}% of pipeline at risk`;
  document.getElementById('batch-kpi-buffer').textContent = `+${s.recommended_overbooking_buffer} Rooms`;

  // Render Table
  renderBatchTableRows(currentBatchRecords);

  resultsArea.scrollIntoView({ behavior: 'smooth' });
}

function renderBatchTableRows(records) {
  const tbody = document.getElementById('batch-tbody');
  const countLabel = document.getElementById('table-record-count');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (countLabel) {
    countLabel.textContent = `Displaying ${Math.min(records.length, 100)} of ${records.length} reservations`;
  }

  records.slice(0, 100).forEach(r => {
    const tr = document.createElement('tr');
    const badgeClass = r.risk_tier === 'High Risk' ? 'badge-danger' : (r.risk_tier === 'Moderate Risk' ? 'badge-warning' : 'badge-success');
    tr.innerHTML = `
      <td>${r.row_id}</td>
      <td><strong>${r.hotel}</strong></td>
      <td>${r.lead_time}d</td>
      <td>${r.arrival_date_month}</td>
      <td>${r.total_stay_nights} nights</td>
      <td>$${r.adr.toFixed(2)}</td>
      <td><strong>$${r.total_value.toFixed(2)}</strong></td>
      <td><strong style="color: ${r.predicted_cancellation ? '#f87171' : '#34d399'}">${r.cancellation_probability}%</strong></td>
      <td><span class="badge ${badgeClass}">${r.risk_tier}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function filterBatchTable(query) {
  if (!query || query.trim() === '') {
    renderBatchTableRows(currentBatchRecords);
    return;
  }
  const q = query.toLowerCase();
  const filtered = currentBatchRecords.filter(r => 
    r.hotel.toLowerCase().includes(q) ||
    r.arrival_date_month.toLowerCase().includes(q) ||
    r.risk_tier.toLowerCase().includes(q) ||
    String(r.lead_time).includes(q) ||
    String(r.adr).includes(q)
  );
  renderBatchTableRows(filtered);
}

// 8. OVERBOOKING OPTIMIZATION SIMULATOR
function initOverbookingSimulator() {
  const btnRun = document.getElementById('btn-run-simulation');
  if (btnRun) {
    btnRun.addEventListener('click', () => {
      runOverbookingSimulation(true);
    });
  }
}

async function runOverbookingSimulation(showFeedback = false) {
  const cap = parseInt(document.getElementById('sim-capacity')?.value || 250);
  const adr = parseFloat(document.getElementById('sim-adr')?.value || 110);
  const cancelRate = parseFloat(document.getElementById('sim-cancel-rate')?.value || 35);
  const walkCost = parseFloat(document.getElementById('sim-walk-cost')?.value || 180);

  const payload = {
    hotel_capacity: cap,
    adr: adr,
    expected_cancellation_rate: cancelRate,
    walked_guest_cost: walkCost
  };

  try {
    const res = await fetch('/api/simulate-overbooking', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('Simulation failed');
    const data = await res.json();

    // Update banner
    document.getElementById('opt-overbook-pct').textContent = `+${data.optimal_overbooking_rate_pct}% Overbooking`;
    document.getElementById('opt-bookings').textContent = `${data.optimal_bookings_to_accept} bookings`;
    document.getElementById('opt-occ').textContent = `${data.expected_occupancy_pct}%`;
    document.getElementById('opt-gain').textContent = `+$${data.incremental_revenue_gain.toLocaleString()}`;

    renderSimulationChart(data.curve);

    if (showFeedback) {
      showToast(`Optimal Buffer: +${data.optimal_overbooking_rate_pct}% (+${data.incremental_revenue_gain.toLocaleString()})`, "success", "fa-chart-line");
    }

  } catch (err) {
    console.warn("Overbooking simulator notice:", err.message);
  }
}

function renderSimulationChart(curve) {
  const ctx = document.getElementById('chart-simulation');
  if (!ctx || !curve) return;
  destroyChart('simulation');

  const labels = curve.map(c => `+${c.overbooking_rate_pct}%`);
  const netRevenue = curve.map(c => c.net_expected_revenue);
  const grossRevenue = curve.map(c => c.gross_revenue);
  const penalties = curve.map(c => c.walk_penalty);

  charts['simulation'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Net Expected Revenue ($)',
          data: netRevenue,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          fill: true,
          borderWidth: 3.5,
          pointRadius: 5,
          pointHoverRadius: 8,
          pointBackgroundColor: '#10b981',
          tension: 0.3
        },
        {
          label: 'Gross Room Revenue ($)',
          data: grossRevenue,
          borderColor: '#38bdf8',
          borderDash: [5, 5],
          borderWidth: 2,
          pointRadius: 0
        },
        {
          label: 'Walked Guest Penalty ($)',
          data: penalties,
          borderColor: '#ef4444',
          borderDash: [3, 3],
          borderWidth: 2,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#94a3b8' },
          title: { display: true, text: 'Overbooking Buffer Percentage', color: '#94a3b8' }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#94a3b8', callback: v => `$${v.toLocaleString()}` }
        }
      },
      plugins: {
        legend: { labels: { color: '#f8fafc', font: { family: 'Plus Jakarta Sans', size: 12 } } }
      }
    }
  });
}

// 9. GEOGRAPHIC INTELLIGENCE (NEW in v3.0)
let cachedGeoCountries = [];

async function fetchGeoAnalytics() {
  try {
    const res = await fetch('/api/geo-analytics');
    if (!res.ok) throw new Error('Failed to fetch geographic analytics');
    const data = await res.json();

    // Domestic vs International KPIs
    const dom = data.domestic_vs_international.domestic;
    const intl = data.domestic_vs_international.international;

    animateCountUp(document.getElementById('geo-dom-pct'), dom.pct_of_total, '', '%', 1);
    document.getElementById('geo-dom-count').textContent = `${dom.total_bookings.toLocaleString()} Bookings`;
    animateCountUp(document.getElementById('geo-dom-cancel'), dom.cancellation_rate, '', '%', 1);

    animateCountUp(document.getElementById('geo-intl-pct'), intl.pct_of_total, '', '%', 1);
    document.getElementById('geo-intl-count').textContent = `${intl.total_bookings.toLocaleString()} Bookings`;
    animateCountUp(document.getElementById('geo-intl-cancel'), intl.cancellation_rate, '', '%', 1);

    cachedGeoCountries = data.top_origin_countries || [];
    renderGeoTableRows(cachedGeoCountries);

  } catch (err) {
    console.warn("Geo analytics notice:", err.message);
  }
}

function renderGeoTableRows(countries) {
  const tbody = document.getElementById('geo-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  countries.forEach(c => {
    const tr = document.createElement('tr');
    const badgeClass = c.risk_tier === 'High Risk' ? 'badge-danger' : (c.risk_tier === 'Moderate Risk' ? 'badge-warning' : 'badge-success');
    tr.innerHTML = `
      <td><strong>${c.country_name}</strong></td>
      <td><span class="badge badge-secondary" style="font-family: var(--font-mono);">${c.country_code}</span></td>
      <td>${c.bookings.toLocaleString()}</td>
      <td>${c.pct_share}%</td>
      <td>$${c.avg_adr.toFixed(2)}</td>
      <td>${c.avg_lead_time.toFixed(1)}d</td>
      <td><strong style="color: ${c.risk_color};">${c.cancellation_rate}%</strong></td>
      <td><span class="badge ${badgeClass}">${c.risk_tier}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function initGeoSearch() {
  const searchInput = document.getElementById('geo-search-input');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      renderGeoTableRows(cachedGeoCountries);
      return;
    }
    const filtered = cachedGeoCountries.filter(c => 
      c.country_name.toLowerCase().includes(q) ||
      c.country_code.toLowerCase().includes(q) ||
      c.risk_tier.toLowerCase().includes(q)
    );
    renderGeoTableRows(filtered);
  });
}

