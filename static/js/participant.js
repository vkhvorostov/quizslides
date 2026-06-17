const SESSION_CODE = document.getElementById('session-code').value;
const CSRF_TOKEN = document.getElementById('csrf-token').value;
const PANEL = document.getElementById('participant-panel');

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

function renderWaiting(message) {
    PANEL.innerHTML = `<p class="text-center text-muted mb-0">${escapeHtml(message)}</p>`;
}

function renderContentSlide(state) {
    PANEL.innerHTML = `
        <h5 class="text-center mb-3">Слайд ${state.current_slide} / ${state.total_slides}</h5>
        <p class="text-center text-muted mb-0">Сейчас показ контента. Ожидайте опрос.</p>
    `;
}

function renderPollSlide(state) {
    const optionsHtml = (state.options || []).map(opt => {
        const selected = state.my_vote_option_id === opt.id;
        const cls = selected ? 'btn-success' : 'btn-outline-primary';
        return `
            <button type="button" class="btn ${cls} w-100 text-start mb-2 poll-vote-btn"
                    data-option-id="${opt.id}">
                ${escapeHtml(opt.text)}
            </button>
        `;
    }).join('');

    const voted = state.my_vote_option_id != null;
    const allowChange = Boolean(state.allow_change_answer);
    const hasTimer = state.timer && state.timer > 0;
    const remaining = Number(state.remaining_seconds) || 0;

    PANEL.innerHTML = `
        <h5 class="text-center mb-2 slide-multiline" style="white-space:pre-wrap;">${escapeHtml(state.question || 'Опрос')}</h5>
        <p class="text-center text-muted small mb-2">Слайд ${state.current_slide} / ${state.total_slides}</p>
        <div class="text-center mb-3">
            <span class="badge bg-info text-dark" id="participant-timer-display">${hasTimer ? 'Осталось: ' + remaining + ' сек' : 'Таймер не задан'}</span>
        </div>
        <div class="mb-3">${optionsHtml}</div>
        <p id="participant-vote-info" class="text-center small ${voted ? 'text-success' : 'text-muted'} mb-0">
            ${voted ? (allowChange ? 'Вы проголосовали. Можно выбрать другой вариант.' : 'Вы проголосовали.') : 'Нажмите вариант, чтобы проголосовать'}
        </p>
    `;

    // wire buttons
    PANEL.querySelectorAll('.poll-vote-btn').forEach(btn => {
        btn.addEventListener('click', () => castVote(btn.dataset.optionId));
        // disable if already voted and changing not allowed
        if (voted && !allowChange) btn.disabled = true;
        // disable if time expired
        if (hasTimer && remaining <= 0) btn.disabled = true;
    });

    // setup per-second local countdown synced with server
    window._participantRemaining = remaining;
    const timerEl = document.getElementById('participant-timer-display');
    if (window._participantTimerInterval) clearInterval(window._participantTimerInterval);
    if (hasTimer) {
        window._participantTimerInterval = setInterval(() => {
            if (window._participantRemaining > 0) {
                window._participantRemaining -= 1;
                if (timerEl) timerEl.textContent = `Осталось: ${window._participantRemaining} сек`;
            }
            if (window._participantRemaining <= 0) {
                // time's up: disable buttons and update info
                document.querySelectorAll('.poll-vote-btn').forEach(b => b.disabled = true);
                const info = document.getElementById('participant-vote-info');
                if (info) info.textContent = 'Время для голосования истекло';
                clearInterval(window._participantTimerInterval);
                window._participantTimerInterval = null;
            }
        }, 1000);
    } else {
        if (timerEl) timerEl.textContent = 'Таймер не задан';
    }
}

function castVote(optionId) {
    fetch(`/api/session/${SESSION_CODE}/vote/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN,
        },
        body: JSON.stringify({ answer_option_id: parseInt(optionId, 10) }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            refreshState();
        } else {
            alert(data.error || 'Не удалось проголосовать');
        }
    })
    .catch(() => alert('Ошибка сети'));
}

function refreshState() {
    fetch(`/api/session/${SESSION_CODE}/state/`)
    .then(r => r.json())
    .then(state => {
        if (!state.active) {
            renderWaiting(state.error || 'Сессия не активна');
            return;
        }
        if (state.slide_type === 'POLL') {
            renderPollSlide(state);
        } else {
            renderContentSlide(state);
        }
    })
    .catch(() => renderWaiting('Нет связи с сервером'));
}

refreshState();
setInterval(refreshState, 2500);
