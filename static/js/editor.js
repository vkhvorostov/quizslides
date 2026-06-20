document.addEventListener('DOMContentLoaded', function() {
    const titleElement = document.getElementById('presentation-title');
    const csrfToken = document.getElementById('csrf-token').value;
    const presentationId = document.getElementById('presentation-id').value;
    const saveStatus = document.getElementById('save-status');
    let originalTitle = titleElement.innerText.trim();

    // 1. Логика сохранения названия (Инлайн-редактирование)
    function saveTitle() {
        const newTitle = titleElement.innerText.trim();
        if (newTitle === originalTitle) return; // Не сохраняем, если не изменилось
        if (newTitle === '') {
            titleElement.innerText = originalTitle; // Откат при пустом названии
            return;
        }

        saveStatus.style.display = 'inline';
        saveStatus.innerText = 'Сохранение...';

        fetch(`/api/presentation/${presentationId}/update-title/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ title: newTitle })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                originalTitle = newTitle;
                saveStatus.innerText = 'Сохранено';
                setTimeout(() => saveStatus.style.display = 'none', 2000);
            }
        }).catch(err => {
            saveStatus.innerText = 'Ошибка сохранения';
        });
    }

    // Сохранение по потере фокуса (blur)
    titleElement.addEventListener('blur', saveTitle);

    // Сохранение по нажатию Enter
    titleElement.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault(); // Предотвращаем перенос строки
            titleElement.blur(); // Вызовет событие blur
        }
    });

    // Визуальный отклик при фокусе
    titleElement.addEventListener('focus', function() {
        this.style.backgroundColor = '#f8f9fa';
    });
    titleElement.addEventListener('blur', function() {
        this.style.backgroundColor = 'transparent';
    });


    const slidesList = document.getElementById('slides-list');
    let draggedItem = null;

    // Начало перетаскивания
    slidesList.addEventListener('dragstart', function(e) {
        const target = e.target.closest('.slide-thumbnail');
        if (target) {
            draggedItem = target;

            document.body.classList.add('dragging-active');
            // Добавляем класс для синего пунктира и прозрачности
            setTimeout(() => target.classList.add('dragging'), 0);
            
            e.dataTransfer.effectAllowed = 'move';
        }
    });

    // Конец перетаскивания
    slidesList.addEventListener('dragend', function(e) {
        document.body.classList.remove('dragging-active');
        if (draggedItem) {
            draggedItem.classList.remove('dragging');
            draggedItem = null;
        }
    });

    // Движение над другими элементами
    slidesList.addEventListener('dragover', function(e) {
        e.preventDefault();

        e.dataTransfer.dropEffect = 'move';
        const target = e.target.closest('.slide-thumbnail');
        if (target && target !== draggedItem) {
            
            const rect = target.getBoundingClientRect();
            const next = (e.clientY - rect.top) / (rect.bottom - rect.top) > 0.5;
            slidesList.insertBefore(draggedItem, next && target.nextSibling || target);
        }
    });

    // Элемент отпущен
    slidesList.addEventListener('drop', function(e) {
        e.preventDefault();
        updateOrderAndSave();
    });

    // Функция обновления номеров на фронте и отправки на бэк
    function updateOrderAndSave() {
        const slides = document.querySelectorAll('.slide-thumbnail');
        const slideIds = [];
        
        slides.forEach((slide, index) => {
            // Мгновенно обновляем номер в интерфейсе
            const numberBadge = slide.querySelector('.badge');
            if (numberBadge) {
                numberBadge.innerText = `# ${index + 1}`;
            }
            slideIds.push(slide.getAttribute('data-slide-id'));
        });

        // Отправляем новый порядок на сервер
        fetch(`/api/presentation/${presentationId}/reorder-slides/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ slide_ids: slideIds })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('Ошибка при сохранении порядка на сервере');
            }
        })
        .catch(err => console.error("Ошибка сети:", err));
    }

});

function addSlide(type, event) {
    
    if (event) event.preventDefault();

    const csrfToken = document.getElementById('csrf-token').value;
    const presentationId = document.getElementById('presentation-id').value;
    
    // Блокируем кнопку на время запроса (опционально, чтобы не спамили)
    const btn = event ? event.currentTarget : null;
    if (btn) btn.style.pointerEvents = 'none';

    fetch(`/api/presentation/${presentationId}/add-slide/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ type: type })
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сервера');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const container = document.getElementById('slides-list');
            const noMsg = document.getElementById('no-slides-msg');
            if (noMsg) noMsg.remove();

            const slideHtml = `
                <div class="card mb-3 slide-thumbnail border-success" 
                     draggable="true"
                     data-slide-id="${data.id_slide}" 
                     onclick="selectSlide('${data.id_slide}')"
                     style="cursor: grab; opacity: 0; transform: translateY(10px); transition: all 0.3s;">
                    <div class="card-body p-2">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="badge bg-secondary"># ${data.number}</span>
                            <div class="d-flex align-items-center gap-1">
                                <span class="text-success" style="font-size: 10px;">● Active</span>
                                <button type="button" class="btn btn-sm btn-link text-danger p-0 lh-1"
                                        onclick="event.stopPropagation(); deleteSlide('${data.id_slide}')">&times;</button>
                            </div>
                        </div>
                        <div class="preview-placeholder bg-light border rounded d-flex align-items-center justify-content-center" style="height: 80px;">
                            <small class="text-muted">Новый слайд</small>
                        </div>
                    </div>
                </div>
            `;
            
            container.insertAdjacentHTML('beforeend', slideHtml);
            
            // Анимация
            const newElement = container.lastElementChild;
            setTimeout(() => {
                newElement.style.opacity = '1';
                newElement.style.transform = 'translateY(0)';
            }, 50);

            newElement.scrollIntoView({ behavior: 'smooth' });
        }
    })
    .catch(err => {
        console.error("Ошибка:", err);
        alert("Не удалось добавить слайд. Проверьте консоль (F12).");
    })
    .finally(() => {
        if (btn) btn.style.pointerEvents = 'auto';
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

function parseApiResponse(response) {
    return response.text().then(text => {
        try {
            return { ok: response.ok, data: JSON.parse(text) };
        } catch (e) {
            return {
                ok: false,
                data: {
                    success: false,
                    error: response.ok ? 'Неверный ответ сервера' : `Ошибка ${response.status}. Перезапустите сервер (Ctrl+C, затем runserver).`
                }
            };
        }
    });
}

function deleteSlideButtonHtml(id) {
    return `<button type="button" class="btn btn-outline-danger" onclick="deleteSlide(${id})">Удалить слайд</button>`;
}

function getPollOptionsList(data) {
    if (data.answer_options && data.answer_options.length > 0) {
        return data.answer_options;
    }
    return [{ text: 'Вариант 1' }, { text: 'Вариант 2' }];
}

function selectSlide(id) {

    document.querySelectorAll('.slide-thumbnail').forEach(el => {
        el.classList.remove('border-primary', 'shadow-sm');
        el.classList.add('border-success');
    });

    const active = document.querySelector(`[data-slide-id="${id}"]`);

    if (active) {
        active.classList.remove('border-success');
        active.classList.add('border-primary', 'shadow-sm');
    }

    const editor = document.getElementById('slide-editor');

    editor.innerHTML = `
        <div class="text-center mt-5">
            Загрузка...
        </div>
    `;

    fetch(`/api/slide/${id}/`)
    .then(response => response.json())
    .then(data => {

if (data.slide_type === 'POLL') {
    renderPollPreview(id, data);
}
else {
    renderContentPreview(id, data);
}
    });
}

function renderContentPreview(id, data) {

    const editor = document.getElementById('slide-editor');

    editor.innerHTML = `
        <div class="h-100 d-flex flex-column">

            ${
                data.picture_url
                ?
                `
                <div class="text-center mb-4">
                    <img src="${data.picture_url}"
                         class="img-fluid rounded border"
                         style="max-height:250px;">
                </div>
                `
                :
                ''
            }

            <div class="border rounded p-3 bg-light flex-grow-1 slide-multiline">
                ${escapeHtml(data.content) || 'Нет текста'}
            </div>

            <div class="mt-4 d-flex flex-wrap gap-2">
                <button class="btn btn-primary" onclick="openEditMode(${id})">Редактировать</button>
                ${deleteSlideButtonHtml(id)}
            </div>

        </div>
    `;
}

function renderPollPreview(id, data) {

    const editor = document.getElementById('slide-editor');
    const options = getPollOptionsList(data);
    const optionsHtml = options.map(opt => `
        <button type="button" class="btn btn-outline-primary text-start" disabled>
            ${escapeHtml(opt.text)}
        </button>
    `).join('');

    editor.innerHTML = `
        <div class="h-100 d-flex flex-column justify-content-center">

            <h3 class="mb-4 slide-multiline">${escapeHtml(data.content || 'Новый опрос')}</h3>

            <div class="d-grid gap-2">${optionsHtml}</div>

            <p class="text-center text-muted small">Голосуют зрители по коду сессии (кнопки у вас неактивны).</p>
            <div class="mt-2 d-flex flex-wrap gap-2 justify-content-center">
                <button class="btn btn-primary" onclick="openPollEditMode(${id})">Редактировать опрос</button>
                ${deleteSlideButtonHtml(id)}
            </div>

        </div>
    `;
}

function appendPollOptionRow(container, value = '', isCorrect = false) {
    const row = document.createElement('div');
    row.className = 'input-group mb-2 poll-option-row';

    const radioWrapper = document.createElement('span');
    radioWrapper.className = 'input-group-text d-flex align-items-center';
    const radio = document.createElement('input');
    radio.type = 'radio';
    radio.name = 'correct-answer';
    radio.className = 'form-check-input mt-0 poll-correct-radio';
    radio.checked = isCorrect;
    radio.title = 'Правильный ответ';
    radioWrapper.appendChild(radio);

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control poll-option-input';
    input.maxLength = 50;
    input.placeholder = 'Вариант ответа';
    input.value = value || '';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-outline-secondary';
    btn.textContent = '×';
    btn.addEventListener('click', () => removePollOptionRow(btn));

    row.appendChild(radioWrapper);
    row.appendChild(input);
    row.appendChild(btn);
    container.appendChild(row);
}

function addPollOptionRow() {
    const container = document.getElementById('poll-options-list');
    if (container) appendPollOptionRow(container, '', false);
}

function removePollOptionRow(btn) {
    const container = document.getElementById('poll-options-list');
    if (!container) return;
    if (container.querySelectorAll('.poll-option-row').length <= 1) {
        alert('Нужен хотя бы один вариант ответа');
        return;
    }
    btn.closest('.poll-option-row').remove();
}

function openPollEditMode(id) {

    const editor = document.getElementById('slide-editor');

    fetch(`/api/slide/${id}/`)
    .then(response => response.json())
    .then(data => {
        const options = getPollOptionsList(data);

        editor.innerHTML = `
            <div class="mb-3">
                <label class="form-label">Вопрос</label>
                <textarea id="slide-content" class="form-control" rows="6"></textarea>
            </div>

            <div class="mb-3">
                <label class="form-label">Варианты ответа</label>
                <div id="poll-options-list"></div>
                <button type="button" class="btn btn-sm btn-outline-primary mt-1" onclick="addPollOptionRow()">+ Добавить вариант</button>
            </div>

            <div class="row g-3 mb-3">
                <div class="col-md-6">
                    <label class="form-label">Время на ответ (сек)</label>
                    <input id="poll-timer" type="number" min="0" step="15" class="form-control" placeholder="0">
                </div>
                <div class="col-md-6 d-flex align-items-end">
                    <div class="form-check">
                        <input id="allow-change-answer" class="form-check-input" type="checkbox">
                        <label class="form-check-label" for="allow-change-answer">Разрешить изменить ответ</label>
                    </div>
                </div>
            </div>

            <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-success" onclick="savePollSlide(${id})">Сохранить</button>
                <button class="btn btn-secondary" onclick="selectSlide(${id})">Отмена</button>
                ${deleteSlideButtonHtml(id)}
            </div>

            <div id="slide-save-status" class="mt-3 text-muted"></div>
        `;
        document.getElementById('slide-content').value = data.content || '';
        document.getElementById('poll-timer').value = data.timer || 0;
        document.getElementById('allow-change-answer').checked = Boolean(data.allow_change_answer);

        const list = document.getElementById('poll-options-list');
        options.forEach(opt => appendPollOptionRow(list, opt.text, Boolean(opt.is_correct)));
    });
}

function openEditMode(id) {

    const editor = document.getElementById('slide-editor');

    fetch(`/api/slide/${id}/`)
    .then(response => response.json())
    .then(data => {

        editor.innerHTML = `
            <div class="mb-3">

                <label class="form-label">Текст</label>

                <textarea id="slide-content" class="form-control" rows="8"></textarea>

            </div>

            <div class="mb-3">

                <label class="form-label">Картинка</label>

                <input
                    type="file"
                    id="slide-picture"
                    class="form-control">

            </div>

            ${
                data.picture_url
                ?
                `
                <img src="${data.picture_url}"
                     class="img-fluid rounded border mb-3"
                     style="max-height:200px;">
                `
                :
                ''
            }

            <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-success" onclick="saveSlideContent(${id})">Сохранить</button>
                <button class="btn btn-secondary" onclick="selectSlide(${id})">Отмена</button>
                ${deleteSlideButtonHtml(id)}
            </div>

            <div id="slide-save-status" class="mt-3 text-muted"></div>
        `;
        document.getElementById('slide-content').value = data.content || '';
    });
}

function savePollSlide(slideId) {
    const csrfToken = document.getElementById('csrf-token').value;
    const content = document.getElementById('slide-content').value;
    const options = Array.from(document.querySelectorAll('.poll-option-row'))
        .map(row => {
            const textInput = row.querySelector('.poll-option-input');
            const radio = row.querySelector('.poll-correct-radio');
            return {
                text: textInput ? textInput.value.trim() : '',
                isCorrect: radio ? radio.checked : false,
            };
        })
        .filter(option => option.text.length > 0);
    const timerValue = Number(document.getElementById('poll-timer').value || 0);
    const allowChangeAnswer = document.getElementById('allow-change-answer').checked;

    const status = document.getElementById('slide-save-status');
    if (options.length === 0) {
        if (status) status.innerText = 'Добавьте хотя бы один вариант';
        return;
    }

    fetch(`/api/slide/${slideId}/update-poll/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ content, options, timer: timerValue, allowChangeAnswer })
    })
    .then(parseApiResponse)
    .then(({ ok, data }) => {
        if (ok && data.success) {
            if (status) status.innerText = 'Сохранено';
            const slideElement = document.querySelector(
                `[data-slide-id="${slideId}"] .preview-placeholder`
            );
            if (slideElement) {
                slideElement.innerHTML = `
                    <small class="text-muted d-block slide-multiline" style="overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">
                        ${escapeHtml(content)}
                    </small>
                `;
            }
            setTimeout(() => selectSlide(slideId), 300);
        } else if (status) {
            status.innerText = data.error || 'Ошибка сохранения';
        }
    })
    .catch(() => {
        if (status) status.innerText = 'Ошибка сети';
    });
}

function deleteSlide(slideId, event = null) {
    if (event) event.stopPropagation();
    if (!confirm('Удалить этот слайд?')) return;

    const csrfToken = document.getElementById('csrf-token').value;
    fetch(`/api/slide/${slideId}/delete/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken }
    })
    .then(parseApiResponse)
    .then(({ ok, data }) => {
        if (!ok || !data.success) {
            alert(data.error || 'Не удалось удалить слайд. Перезапустите сервер.');
            return;
        }
        const thumb = document.querySelector(`[data-slide-id="${slideId}"]`);
        if (thumb) thumb.remove();

        const slides = document.querySelectorAll('.slide-thumbnail');
        slides.forEach((slide, index) => {
            const badge = slide.querySelector('.badge');
            if (badge) badge.innerText = `# ${index + 1}`;
        });

        const editor = document.getElementById('slide-editor');
        if (slides.length === 0) {
            const container = document.getElementById('slides-list');
            container.innerHTML = '<div id="no-slides-msg" class="text-center py-5 text-muted"><p>Слайдов пока нет</p></div>';
            editor.innerHTML = '<h3 class="text-center mt-5 text-muted">Выберите или создайте слайд</h3>';
        } else {
            editor.innerHTML = '<h3 class="text-center mt-5 text-muted">Выберите или создайте слайд</h3>';
        }
    })
    .catch(() => alert('Не удалось удалить слайд'));
}

function saveSlideContent(slideId) {

    const csrfToken = document.getElementById('csrf-token').value;

    const content = document.getElementById('slide-content').value;

    const pictureInput = document.getElementById('slide-picture');

    const formData = new FormData();

    formData.append('content', content);

    if (pictureInput && pictureInput.files.length > 0) {
        formData.append('picture', pictureInput.files[0]);
    }

    fetch(`/api/slide/${slideId}/update-content/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {

        const status = document.getElementById('slide-save-status');

        if (data.success) {
            if (status) status.innerText = 'Сохранено';
            const slideElement = document.querySelector(
    `[data-slide-id="${slideId}"] .preview-placeholder`);
    if (slideElement) {
    if (data.picture_url) {

        slideElement.innerHTML = `
            <img src="${data.picture_url}"
                 class="img-fluid w-100 h-100 rounded"
                 style="object-fit: cover;">
        `;
    }
    else {

        slideElement.innerHTML = `
            <small class="text-muted d-block slide-multiline"
                   style="overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;">
                ${escapeHtml(content)}
            </small>
        `;
    }
}
    setTimeout(() => {
        selectSlide(slideId);
    }, 300);
        }
        else {
            if (status) status.innerText = 'Ошибка';
        }
    })
    .catch(() => {
        const status = document.getElementById('slide-save-status');
        if (status) status.innerText = 'Ошибка';
        else alert('Не удалось сохранить. Обновите страницу (Ctrl+F5).');
    });
}