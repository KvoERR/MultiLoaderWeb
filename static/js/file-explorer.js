document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('videoFile');
    const browseBtn = document.querySelector('.browse-btn');
    const fileInfo = document.getElementById('fileInfo');

    // 1. Клик по кнопке "Выберите файл"
    browseBtn.addEventListener('click', function(e) {
        e.stopPropagation(); // Предотвращаем всплытие
        fileInput.click();
    });

    // 2. Обработчик выбора файла через input
    fileInput.addEventListener('change', function(e) {
        handleFiles(this.files);
    });

    // 3. Отключаем стандартное поведение браузера при drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Отключает срабатывание события
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // 4. Подсветка при перетаскивании
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    // 5. Обработка сброса файлов
    dropZone.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    // 6. Обработка выбранных файлов
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            
            // Проверка типа файла
            if (!file.type.startsWith('video/')) {
                alert('Пожалуйста, выберите видео файл');
                return;
            }

            // Проверка размера файла (макс. 100MB) FIXME
            if (file.size > 100 * 1024 * 1024) {
                alert('Файл слишком большой. Максимальный размер: 100MB');
                return;
            }

            // Показываем информацию о файле
            showFileInfo(file);

            // Создаем FileList для input
            const dt = new DataTransfer(); // переносчик данных
            dt.items.add(file); // добавляем в переносчик выбранный файл
            fileInput.files = dt.files; // добавляем файл в поле input
        }
    }

    // 7. Показ информации о файле
    function showFileInfo(file) {
        fileInfo.innerHTML = `
            <div class="file-name">📹 ${file.name}</div>
            <div class="file-size">Размер: ${formatFileSize(file.size)}</div>
            <div class="file-type">Тип: ${file.type || 'Неизвестно'}</div>
        `;
        fileInfo.classList.add('show');
    }

    // 8. Форматирование размера файла
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
});