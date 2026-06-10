const PRESENTATION_ID = document.getElementById('presentation-id').value;
const RESULTS_EL = document.getElementById('poll-results-live');
const TOTAL_EL = document.getElementById('poll-total-voters');
let chartType = 'bar';
const COLORS = ['#198754', '#0d6efd', '#fd7e14', '#dc3545', '#6f42c1', '#20c997'];

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

function buildPieGradient(options) {
    const total = options.reduce((s, o) => s + o.count, 0) || 1;
    let acc = 0;
    const parts = options.map((opt, i) => {
        const start = (acc / total) * 100;
        acc += opt.count;
        const end = (acc / total) * 100;
        return `${COLORS[i % COLORS.length]} ${start}% ${end}%`;
    });
    return `conic-gradient(${parts.join(', ')})`;
}

function renderResults(results) {
    if (!results || !results.options) return;
    const opts = results.options;
    const total = results.total_voters || 0;
    if (TOTAL_EL) TOTAL_EL.textContent = total;

    if (opts.length === 0) {
        RESULTS_EL.innerHTML = '<p class="text-center text-muted">Нет вариантов ответа</p>';
        return;
    }

    if (chartType === 'pie') {
        RESULTS_EL.innerHTML = `
            <div class="poll-pie mb-4" style="background:${buildPieGradient(opts)}"></div>
            <div class="d-flex flex-wrap justify-content-center gap-3">
                ${opts.map((o, i) => `
                    <span><span style="display:inline-block;width:12px;height:12px;background:${COLORS[i % COLORS.length]};border-radius:2px;"></span>
                    ${escapeHtml(o.text)} — <strong>${o.count}</strong> (${o.percent}%)</span>
                `).join('')}
            </div>
        `;
        return;
    }

    if (chartType === 'bar') {
        RESULTS_EL.innerHTML = `
            <div class="d-flex justify-content-center align-items-end gap-3" style="min-height:160px;">
                ${opts.map((o, i) => `
                    <div class="text-center" style="width:72px;">
                        <div class="poll-bar-track d-flex align-items-end" style="height:120px;width:48px;margin:0 auto;">
                            <div class="poll-bar-fill w-100" style="height:${Math.max(o.percent, 5)}%;background:${COLORS[i % COLORS.length]}"></div>
                        </div>
                        <div class="small fw-semibold mt-2">${escapeHtml(o.text)}</div>
                        <div class="text-muted small">${o.count}</div>
                    </div>
                `).join('')}
            </div>
        `;
        return;
    }

    RESULTS_EL.innerHTML = opts.map((o, i) => `
        <div class="mb-3">
            <div class="d-flex justify-content-between small mb-1">
                <span>${escapeHtml(o.text)}</span>
                <span><strong>${o.count}</strong> (${o.percent}%)</span>
            </div>
            <div class="poll-bar-track">
                <div class="poll-bar-fill" style="width:${o.percent}%;background:${COLORS[i % COLORS.length]}"></div>
            </div>
        </div>
    `).join('');
}

document.querySelectorAll('.chart-toggle [data-chart]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.chart-toggle [data-chart]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        chartType = btn.dataset.chart;
        if (window._lastPollResults) renderResults(window._lastPollResults);
    });
});

function refreshPoll() {
    fetch(`/api/presentation/${PRESENTATION_ID}/poll-results/`)
    .then(r => r.json())
    .then(data => {
        if (data.success && data.results) {
            window._lastPollResults = data.results;
            renderResults(data.results);
        }
    })
    .catch(() => {});
}

const initialEl = document.getElementById('initial-poll-results');
if (initialEl) {
    try {
        window._lastPollResults = JSON.parse(initialEl.textContent);
        renderResults(window._lastPollResults);
    } catch (e) {
        refreshPoll();
    }
} else {
    refreshPoll();
}

setInterval(refreshPoll, 2500);
