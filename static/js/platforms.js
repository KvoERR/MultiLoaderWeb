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
    const allBoxes = document.querySelectorAll('.info-box');
    const targetBox = document.getElementById(`info-${platform}`);
    const targetButton = document.getElementById(`${platform}-button`);

    // Если целевой блок не найден — выходим
    if (!targetBox) return;

    // Сохраняем оригинальный цвет кнопки при первом клике
    if (!targetButton.dataset.originalColor) {
        targetButton.dataset.originalColor = getComputedStyle(targetButton).backgroundColor;
    }

    // Проверяем, открыт ли целевой блок СЕЙЧАС
    const isOpen = targetBox.style.display === 'block';

    // Сначала закрываем ВСЕ блоки
    allBoxes.forEach(box => {
        const button = document.getElementById(box.id.replace('info-', '') + '-button');
        box.style.display = 'none';
        if (button && button.dataset.originalColor) {
            button.style.backgroundColor = button.dataset.originalColor;
        }
    });

    // Если целевой блок был открыт — мы его уже закрыли → ничего больше не делаем
    if (isOpen) {
        // Уже закрыт, ничего не открываем
        return;
    }

    // Иначе — открываем целевой блок
    targetBox.style.display = 'block';
    targetButton.style.backgroundColor = 'yellow';
}
