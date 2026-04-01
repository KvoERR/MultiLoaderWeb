import { connectYouTube } from './youtube-auth.js';
import { VKAuth } from './vk-auth.js';

window.submitForm = async function() {
    console.log('Кнопка нажата! Отправляем данные...');
    
    // Находим элементы
    const form = document.getElementById('uploadForm');
    const resultDiv = document.getElementById('result');

    const button = event.target; // Кнопка, на которую нажали
    
    // Показываем загрузку
    button.disabled = true;
    button.textContent = 'Обработка...';
    
    if (resultDiv) {
        resultDiv.style.display = 'none';
    }

    // Собираем данные формы
    const formData = new FormData(form);

    // Авторизация YouTube (если выбрано)
    if (document.querySelector('input[value="youtube"]:checked')) {
        try {
            await connectYouTube();
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
            const vkAuth = new VKAuth(window.location.href);
            await vkAuth.startAuth();
        } catch (err) {
            showError('Не удалось авторизоваться в VK: ' + err.message);
            button.disabled = false;
            button.textContent = 'Обработать данные';
            return;
        }
    }

    // Проверка токена
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Вы не авторизованы');
        button.disabled = false;
        button.textContent = 'Обработать данные';
        return;
    }

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

// Функция показа успешного результата
function showSuccess(result) {
    const resultDiv = document.getElementById('result');
    if (!resultDiv) return;
    
    resultDiv.className = 'result success';
    resultDiv.innerHTML = `
        <h3>✅ Данные успешно обработаны!</h3>
        <p><small>Запрос обработан: ${new Date().toLocaleString()}</small></p>
    `;
    resultDiv.style.display = 'block';
    
    // Плавная прокрутка к результату
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Функция показа ошибки
function showError(errorMessage) {
    const resultDiv = document.getElementById('result');
    if (!resultDiv) return;
    
    resultDiv.className = 'result error';
    resultDiv.innerHTML = `
        <h3>❌ Ошибка обработки</h3>
        <p>${errorMessage}</p>
    `;
    resultDiv.style.display = 'block';
    
    // Плавная прокрутка к ошибке
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}