async function tgAuth() {
    const channelName = document.getElementById('channel-name').value.trim();

    if (!channelName) {
        alert('Введите название канала');
        return;
    }

    const button = document.getElementById('tg-connect-btn');
    button.disabled = true;
    button.textContent = 'Привязываем...';

    try {
        const response = await fetch('/auth/tg', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ channel_name: channelName }) 
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById('info-telegram').style.display = 'none';
            //сюда добавить изменение кнопки после привязки
        } else {
            alert('Ошибка: ' + result.error);
        }
    } catch (err) {
        alert('Ошибка подключения: ' + err.message);
    } finally {
        button.disabled = false;
        button.textContent = 'Привязать канал';
    }
}