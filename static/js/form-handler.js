function submitForm() {
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
    
    console.log('FormData содержимое:');
    for (let [key, value] of formData.entries()) {
        console.log(key + ': ', value);
    }

    
    // Отправляем AJAX запрос во Flask
    fetch('/process', {
        method: 'POST',
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
        // Восстанавливаем кнопку
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
        <p><strong>Название:</strong> ${result.title || 'Не указано'}</p>
        <p><strong>Описание:</strong> ${result.description || 'Не указано'}</p>
        <p><strong>Категория:</strong> ${result.category_name || 'Не выбрана'}</p>
        <p><strong>Платформы:</strong> ${result.platforms_str || 'Не выбраны'}</p>
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

// Дополнительная функция валидации (опционально)
function validateForm() {
    const title = document.getElementById('title')?.value.trim();
    const platforms = document.querySelectorAll('input[name="platforms"]:checked');
    
    if (!title) {
        showError('Пожалуйста, введите название видео');
        return false;
    }
    
    if (platforms.length === 0) {
        showError('Пожалуйста, выберите хотя бы одну платформу');
        return false;
    }
    
    return true;
}

// Обновляем основную функцию с валидацией
const originalSubmitForm = submitForm;
submitForm = function() {
    if (validateForm()) {
        originalSubmitForm.call(this);
    }
};

console.log('Form handler loaded successfully!');