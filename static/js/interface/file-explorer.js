document.addEventListener('DOMContentLoaded', function() {
    // Настройки для разных типов файлов
    const uploadConfigs = [
        {
            dropZoneId: 'videoDropZone',
            fileInputId: 'video',
            browseBtnId: 'videoBrowseBtn',
            fileInfoId: 'fileInfo',
            acceptType: 'video/',
            maxSize: 100 * 1024 * 1024 // 100MB
        },
        {
            dropZoneId: 'imageDropZone', 
            fileInputId: 'image',
            browseBtnId: 'imageBrowseBtn',
            fileInfoId: 'fileInfo',
            acceptType: 'image/',
            maxSize: 10 * 1024 * 1024 // 10MB для изображений
        }
    ];

    // Инициализация для каждой конфигурации
    uploadConfigs.forEach(config => {
        initFileUpload(config);
    });

    function initFileUpload(config) {
        const dropZone = document.getElementById(config.dropZoneId);
        const fileInput = document.getElementById(config.fileInputId);
        const browseBtn = document.getElementById(config.browseBtnId);
        const fileInfo = document.getElementById(config.fileInfoId);

        if (!dropZone || !fileInput || !browseBtn) {
            console.error(`Элементы не найдены для ${config.dropZoneId}`);
            return;
        }

        // 1. Клик по кнопке "Выберите файл"
        browseBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            fileInput.click();
        });

        // 2. Обработчик выбора файла через input
        fileInput.addEventListener('change', function(e) {
            handleFiles(this.files, config);
        });

        // 3. Отключаем стандартное поведение браузера
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        // 4. Подсветка при перетаскивании
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => highlight(dropZone), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => unhighlight(dropZone), false);
        });

        // 5. Обработка сброса файлов
        dropZone.addEventListener('drop', function(e) {
            const files = e.dataTransfer.files;
            handleFiles(files, config);
        });
    }

    // Общие функции
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(dropZone) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(dropZone) {
        dropZone.classList.remove('dragover');
    }

    function handleFiles(files, config) {
        if (files.length === 0) return;
        
        const file = files[0];
        
        // Проверка типа файла
        if (!file.type.startsWith(config.acceptType)) {
            alert(`Пожалуйста, выберите ${config.acceptType === 'video/' ? 'видео' : 'изображение'} файл`);
            return;
        }

        // Проверка размера файла
        if (file.size > config.maxSize) {
            const maxSizeMB = config.maxSize / (1024 * 1024);
            alert(`Файл слишком большой. Максимальный размер: ${maxSizeMB}MB`);
            return;
        }

        // Показываем информацию о файле
        showFileInfo(file, config.fileInfoId);

        // Создаем FileList для input
        const fileInput = document.getElementById(config.fileInputId);
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
    }

    function showFileInfo(file, fileInfoId) {
        const fileInfo = document.getElementById(fileInfoId);
        if (!fileInfo) return;
        
        const icon = file.type.startsWith('video/') ? '📹' : '🖼';
        
        fileInfo.innerHTML = `
            <div class="file-name">${icon} ${file.name}</div>
            <div class="file-size">Размер: ${formatFileSize(file.size)}</div>
            <div class="file-type">Тип: ${file.type.split('/')[1]?.toUpperCase() || 'Неизвестно'}</div>
        `;
        fileInfo.classList.add('show');
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
});