import { closeAuthPopup } from './auth-popup.js';

export function activateButton(platform) {
    const button = document.getElementById(`${platform}-button`);
    button.style.backgroundColor = 'green';
    button.style.color = 'white';
    button.textContent='Привязано';
}

export function authUpdate(data) {
    const authBtn = document.getElementById('auth-btn');
    authBtn.textContent = '👤';
    authBtn.title = 'Выйти';
    authBtn.onclick = function() {
        localStorage.removeItem('token');
        location.reload();
    };
    if (data.tg_chat_id) {
        const channelName = document.getElementById('tg-channel-name');
        activateButton('telegram');
        //channelName.value = data.tg_chat_id;
    }
    if (data.vk_group_id) {
        const groupName = document.getElementById('vk-group-name');
        activateButton('vk');
        groupName.value = data.vk_group_id;
    }
    localStorage.setItem('token', data.token);
    closeAuthPopup();
}

export async function authz() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('Токен не найден');
        return { success: false, error: 'Не авторизован' };
    }

    try {
        const response = await fetch('/authz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
        });

        const data = await response.json();

        if (response.ok && data.success) {
            authUpdate(data);
            return { success: true, data };
        } else {
            console.error('Ошибка привязки:', data.error);
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Сетевая ошибка:', error);
        return { success: false, error: 'Не удалось подключиться к серверу' };
    }
}