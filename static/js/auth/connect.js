const groupName = document.getElementById('vk-group-name');
const vkAuthBtn = document.getElementById('vk-connect-btn');
const channelName = document.getElementById('tg-channel-name');
const tgAuthBtn = document.getElementById('tg-connect-btn');

window.vkConnect = async function() {
    if (!groupName.value.trim()) {
        alert('Введите ID группы');
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Вы не авторизованы');
        if (typeof openAuthPopup === 'function') {
            openAuthPopup('login');
        }
        return;
    }

    vkAuthBtn.disabled = true;
    vkAuthBtn.textContent = 'Привязываем...';

    try {
        const response = await fetch('/connect/vk', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ group_id: groupName.value.trim() })
        });

        const result = await response.json();

        if (response.ok) {
            window.activateButton('vk');
            localStorage.setItem('vk_auth', 'true');
            document.getElementById('info-vk').style.display = 'none';
            alert('Группа успешно привязана!');
        } else {
            alert('Ошибка: ' + (result.error || 'Неизвестная ошибка'));
        }
    } catch (err) {
        alert('Ошибка подключения: ' + err.message);
    } finally {
        vkAuthBtn.disabled = false;
        vkAuthBtn.textContent = 'Привязать группу';
    }
}

window.tgConnect = async function() {
    if (!channelName.value.trim()) {
        alert('Введите название канала');
        return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Вы не авторизованы');
        if (typeof openAuthPopup === 'function') {
            openAuthPopup('login');
        }
        return;
    }

    tgAuthBtn.disabled = true;
    tgAuthBtn.textContent = 'Привязываем...';

    try {
        const response = await fetch('/connect/tg', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ channel_name: channelName.value.trim() })
        });

        const result = await response.json();

        if (response.ok) {
            window.activateButton('telegram');
            localStorage.setItem('tg_auth', 'true');
            document.getElementById('info-telegram').style.display = 'none';
            alert('Канал успешно привязан!');
        } else {
            alert('Ошибка: ' + (result.error || 'Неизвестная ошибка'));
        }
    } catch (err) {
        alert('Ошибка подключения: ' + err.message);
    } finally {
        tgAuthBtn.disabled = false;
        tgAuthBtn.textContent = 'Привязать канал';
    }
}