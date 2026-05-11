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
});

function addSlide(type, event) {
    // Предотвращаем стандартное поведение (переход по ссылке #)
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
                     data-slide-id="${data.id_slide}" 
                     onclick="selectSlide('${data.id_slide}')"
                     style="cursor: pointer; opacity: 0; transform: translateY(10px); transition: all 0.3s;">
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
    console.log("Выбран слайд:", id);

    document.querySelectorAll('.slide-thumbnail').forEach(el => {
        el.classList.remove('border-primary', 'shadow-sm');
        el.classList.add('border-success');
    });
    const active = document.querySelector(`[data-slide-id="${id}"]`);
    if(active) {
        active.classList.remove('border-success');
        active.classList.add('border-primary', 'shadow-sm');
    }
}
