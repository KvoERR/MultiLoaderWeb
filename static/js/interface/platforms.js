function toggleInfo(platform) {
    const allBoxes = document.querySelectorAll('.info-box');
    const targetBox = document.getElementById(`info-${platform}`);
    const targetButton = document.getElementById(`${platform}-button`);

    if (!targetBox) return;

    if (!targetButton.dataset.originalColor) {
        targetButton.dataset.originalColor = getComputedStyle(targetButton).backgroundColor;
        targetButton.dataset.originalTextColor = getComputedStyle(targetButton).color;
    }

    const isOpen = targetBox.style.display === 'block';

    allBoxes.forEach(box => {
        const button = document.getElementById(box.id.replace('info-', '') + '-button');
        box.style.display = 'none';
        if (button && button.dataset.originalColor) {
            button.style.backgroundColor = button.dataset.originalColor;
            button.style.color = button.dataset.originalTextColor;
        }
    });

    if (isOpen) {
        return;
    }

    targetBox.style.display = 'block';
    targetButton.style.backgroundColor = 'orange';
    targetButton.style.color = 'black';
}
