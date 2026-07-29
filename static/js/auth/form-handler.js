window.submitForm = async function(event) {
    console.log('Кнопка нажата! Отправляем данные...');
    
    const form = document.getElementById('uploadForm');
    const resultDiv = document.getElementById('result');
    const button = event?.target || document.querySelector('button[onclick="submitForm()"]');
    
    button.disabled = true;
    button.textContent = 'Обработка...';
    
    if (resultDiv) {
        resultDiv.style.display = 'none';
    }

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Вы не авторизованы');
        button.disabled = false;
        button.textContent = 'Обработать данные';
        return;
    }

    // Проверяем выбранные платформы
    const selectedPlatforms = document.querySelectorAll('input[name="platforms"]:checked');
    if (selectedPlatforms.length === 0) {
        alert('Выберите хотя бы одну платформу');
        button.disabled = false;
        button.textContent = 'Обработать данные';
        return;
    }

    // Авторизация YouTube (если выбрано)
    if (document.querySelector('input[value="youtube"]:checked')) {
        try {
            await window.authYouTube();
        } catch (err) {
            showError('Не удалось авторизоваться в YouTube: ' + err.message);
            button.disabled = false;
            button.textContent = 'Обработать данные';
            return;
        }
    }

    // Авторизация VK (если выбрано)
    if (document.querySelector('input[value="vk"]:checked')) {
        try {
            await window.authVK();
        } catch (err) {
            showError('Не удалось авторизоваться в VK: ' + err.message);
            button.disabled = false;
            button.textContent = 'Обработать данные';
            return;
        }
    }
    // Собираем данные формы
    const formData = new FormData(form);

    fetch('/process', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    })
    .then(response => {
        console.log('Получен ответ от сервера:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Данные от сервера:', data);
        
        if (data.success) {
            showSuccess(data.result);
        } else {
            showError(data.error || 'Неизвестная ошибка');
        }
    })
    .catch(error => {
        console.error('Ошибка при отправке:', error);
        showError('Ошибка сети: ' + error.message);
    })
    .finally(() => {
        button.disabled = false;
        button.textContent = 'Обработать данные';
    });
}

function showSuccess(result) {
    const resultDiv = document.getElementById('result');
    if (!resultDiv) return;
    
    resultDiv.className = 'result success';
    resultDiv.innerHTML = `
        <h3>✅ Данные успешно обработаны!</h3>
        <p>${result || 'Видео отправлено на выбранные платформы'}</p>
        <p><small>Запрос обработан: ${new Date().toLocaleString()}</small></p>
    `;
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(errorMessage) {
    const resultDiv = document.getElementById('result');
    if (!resultDiv) return;
    
    resultDiv.className = 'result error';
    resultDiv.innerHTML = `
        <h3>❌ Ошибка обработки</h3>
        <p>${errorMessage}</p>
    `;
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}