document.addEventListener('DOMContentLoaded', () => {
    const telegram = document.querySelector('input[value="telegram"]');
    const youtube = document.querySelector('input[value="youtube"]');
    const zen = document.getElementById('zenCheckbox');
    const rutube = document.getElementById('rutubeCheckbox');

    // Функция обновления состояния
    const updateDependencies = () => {
        zen.disabled = !telegram.checked;
        if (!telegram.checked) zen.checked = false;

        rutube.disabled = !youtube.checked;
        if (!youtube.checked) rutube.checked = false;
    };

    // Назначаем слушатели
    telegram.addEventListener('change', updateDependencies);
    youtube.addEventListener('change', updateDependencies);

    // Инициализация при загрузке
    updateDependencies();
});

function toggleInfo(platform) {
    const box = document.getElementById(`info-${platform}`);
    if (box.style.display === 'none' || box.style.display === '') {
        box.style.display = 'block';
    } else {
        box.style.display = 'none';
    }
}