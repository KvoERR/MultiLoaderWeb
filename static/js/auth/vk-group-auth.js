import {activateButton} from './authz.js';
const groupName = document.getElementById('group-name');
const vkAuthBtn = document.getElementById('vk-connect-btn');
window.vkGroupAuth = async function() {
    if (!groupName.value.trim()) {
        alert('Введите название группы');
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Вы не авторизованы');
        openAuthPopup('login');
        return;
    }

    vkAuthBtn.disabled = true;
    vkAuthBtn.textContent = 'Привязываем...';

    try {
        const response = await fetch('/auth/vk', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ group_id: groupName.value.trim() })
        });

        const result = await response.json();

        if (response.ok) {
            activateButton('vk');
            localStorage.setItem('vk_auth', true);
            document.getElementById('info-vk').style.display = 'none';
        } else {
            alert('Ошибка: ' + result.error);
        }
    } catch (err) {
        alert('Ошибка подключения: ' + err.message);
    } finally {
        vkAuthBtn.disabled = false;
        vkAuthBtn.textContent = 'Привязать канал';
    }
}