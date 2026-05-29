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
                        <div class="d-flex justify-content-between mb-1">
                            <span class="badge bg-secondary"># ${data.number}</span>
                            <span class="text-success" style="font-size: 10px;">● Active</span>
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

            <div class="border rounded p-3 bg-light flex-grow-1">
                ${data.content || 'Нет текста'}
            </div>

            <div class="mt-4">
                <button
                    class="btn btn-primary"
                    onclick="openEditMode(${id})">

                    Редактировать
                </button>
            </div>

        </div>
    `;
}

function renderPollPreview(id, data) {

    const editor = document.getElementById('slide-editor');

    editor.innerHTML = `
        <div class="h-100 d-flex flex-column justify-content-center">

            <h3 class="mb-4">
                ${data.content || 'Новый опрос'}
            </h3>

            <div class="d-grid gap-2">

                <button class="btn btn-outline-primary">
                    Вариант 1
                </button>

                <button class="btn btn-outline-primary">
                    Вариант 2
                </button>

            </div>

            <div class="mt-4">
                <button
                    class="btn btn-primary"
                    onclick="openPollEditMode(${id})">

                    Редактировать опрос
                </button>
            </div>

        </div>
    `;
}

function openPollEditMode(id) {

    const editor = document.getElementById('slide-editor');

    fetch(`/api/slide/${id}/`)
    .then(response => response.json())
    .then(data => {

        editor.innerHTML = `
            <div class="mb-3">

                <label class="form-label">
                    Вопрос
                </label>

                <textarea
                    id="slide-content"
                    class="form-control"
                    rows="3">${data.content || ''}</textarea>

            </div>

            <button
                class="btn btn-success"
                onclick="saveSlideContent(${id})">

                Сохранить
            </button>
        `;
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

                <textarea
                    id="slide-content"
                    class="form-control"
                    rows="6">${data.content || ''}</textarea>

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

            <button
                class="btn btn-success"
                onclick="saveSlideContent(${id})">

                Сохранить
            </button>

            <button
                class="btn btn-secondary ms-2"
                onclick="selectSlide(${id})">

                Отмена
            </button>

            <div id="slide-save-status"
                 class="mt-3 text-muted"></div>
        `;
    });
}

function saveSlideContent(slideId) {

    const csrfToken = document.getElementById('csrf-token').value;

    const content = document.getElementById('slide-content').value;

    const pictureInput = document.getElementById('slide-picture');

    const formData = new FormData();

    formData.append('content', content);

    if (pictureInput.files.length > 0) {
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
            status.innerText = 'Сохранено';
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
            <small class="text-muted d-block"
                   style="
                        overflow: hidden;
                        display: -webkit-box;
                        -webkit-line-clamp: 3;
                        -webkit-box-orient: vertical;
                   ">
                ${content}
            </small>
        `;
    }
}
    setTimeout(() => {
        selectSlide(slideId);
    }, 300);
        }
        else {
            status.innerText = 'Ошибка';
        }
    })
    .catch(() => {
        document.getElementById('slide-save-status').innerText = 'Ошибка';
    });
}