// Функции для всплывающего окна
function openPopup() {
    document.getElementById("popupWindow").style.display = "flex";
}

function closePopup() {
    document.getElementById("popupWindow").style.display = "none";
}

// Закрытие всплывающего окна при клике вне окна
window.onclick = function(event) {
    let popup = document.getElementById("popupWindow");
    if (event.target === popup) {
        popup.style.display = "none";
    }
}

// Создание презентации
function createPresentation(event) {
    event.preventDefault();
    
    const title = document.getElementById('presentationTitle').value.trim();
    const errorDiv = document.getElementById('titleError');
    const successDiv = document.getElementById('successMessage');
    
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';
    
    if (!title) {
        errorDiv.textContent = gettext('Введите название презентации');
        errorDiv.style.display = 'block';
        return;
    }
    
    const newTab = window.open('', '_blank');
    newTab.document.write(`
        <html>
        <head>
            <title>${title}</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    font-family: 'Inter', sans-serif;
                    margin: 0;
                }
                .container {
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>${gettext('Создание презентации...')}</h2>
                <p>${gettext('Пожалуйста, подождите')}</p>
            </div>
        </body>
        </html>
    `);
    newTab.document.close();
    
    fetch('/create/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'title=' + encodeURIComponent(title)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            successDiv.style.display = 'block';
            successDiv.textContent = interpolate(
                gettext('Презентация "%(name)s" успешно создана! Перенаправление...'),
                { name: data.name },
                true
            );
            document.getElementById('createPresentationForm').reset();
            
            newTab.location.href = `/editor/${data.id}/`;
            
            setTimeout(() => {
                closePopup();
                successDiv.style.display = 'none';
            }, 1000);
        } else {
            newTab.close();
            errorDiv.textContent = data.error || gettext('Ошибка при создании');
            errorDiv.style.display = 'block';
        }
    })
    .catch(error => {
        newTab.close();
        errorDiv.textContent = gettext('Произошла ошибка. Попробуйте позже.');
        errorDiv.style.display = 'block';
    });
}
