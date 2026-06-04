# Создание презентаций
На главном экране нажмите кнопку «Создать презентацию».
### index.html
    <button type="button" onclick="openPopup()" id="openPopupBtn" class="btn btn-success btn-lg fw-semibold px-4 py-3">Создать презентацию</button>
Во всплывающем окне введите название презентации и нажмите «Создать».
### index.html
    <div id="popupWindow" ...>
    <h5 class="text-center mb-3">Создание презентации</h5>
    <form id="createPresentationForm" onsubmit="createPresentation(event)">
        {% csrf_token %}
        <div class="mb-3">
            <input type="text" name="title" id="presentationTitle" class="form-control" placeholder="Название презентации" required>
            <div class="invalid-feedback" id="titleError" style="display:none;"></div>
        </div>
        <div class="d-grid">
            <button type="submit" class="btn btn-success">Создать</button>
        </div>
    </form>
    </div>
### main.js
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
            errorDiv.textContent = 'Введите название презентации';
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
                    <h2>Создание презентации...</h2>
                    <p>Пожалуйста, подождите</p>
                </div>
            </body>
            </html>
        `);
        newTab.document.close();
        ...    
       }
После этого отправляется асинхронный запрос на сервер. 
### main.js
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
            successDiv.textContent = `Презентация "${data.name}" успешно создана!`;
            document.getElementById('createPresentationForm').reset();
            
            newTab.document.title = data.name;
            newTab.document.body.innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Inter', sans-serif;">
                    <div style="text-align: center;">
                        <h1 style="color: #198754; font-size: 2rem;">${data.name}</h1>
                        <p style="color: #666; font-size: 1.2rem;">Презентация создана. Редактирование будет доступно позже.</p>
                        <p style="color: #999;">ID: ${data.id}</p>
                    </div>
                </div>
            `;
            
            setTimeout(() => {
                closePopup();
                successDiv.style.display = 'none';
            }, 2000);
        } else {
            newTab.close();
            errorDiv.textContent = data.error || 'Ошибка при создании';
            errorDiv.style.display = 'block';
        }
    })
    .catch(error => {
        newTab.close();
        errorDiv.textContent = 'Произошла ошибка. Попробуйте позже.';
        errorDiv.style.display = 'block';
    });

При успешном ответе открывается новая вкладка с информацией о созданной презентации, а всплывающее окно автоматически закрывается.
### index.html
    <div id="popupWindow" ...>
            <div id="successMessage" style="display:none;" class="alert alert-success mt-3">
                Презентация успешно создана!
            </div>
    </div>





