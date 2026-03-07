import {activateButton} from './authz.js';
const channelName = document.getElementById('channel-name');
const tgAuthBtn = document.getElementById('tg-connect-btn');
window.tgAuth = async function() {
    if (!channelName.value.trim()) {
        alert('Введите название канала');
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Вы не авторизованы');
        openAuthPopup('login');
        return;
    }

    tgAuthBtn.disabled = true;
    tgAuthBtn.textContent = 'Привязываем...';

    try {
        const response = await fetch('/auth/tg', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ channel_name: channelName.value.trim() })
        });

        const result = await response.json();

        if (response.ok) {
            activateButton('telegram');
            localStorage.setItem('tg_auth', true);
            document.getElementById('info-telegram').style.display = 'none';
        } else {
            alert('Ошибка: ' + result.error);
        }
    } catch (err) {
        alert('Ошибка подключения: ' + err.message);
    } finally {
        tgAuthBtn.disabled = false;
        tgAuthBtn.textContent = 'Привязать канал';
    }
}