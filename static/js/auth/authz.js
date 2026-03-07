window.addEventListener('load', function() {
    authz();
});

export function activateButton(platform) {
    const button = document.getElementById(`${platform}-button`);
    button.style.backgroundColor = 'green';
    button.style.color = 'white';
    button.textContent='Привязано';
}

export function authUpdate(data) {
    authBtn.textContent = '👤';
    authBtn.title = 'Выйти';
    authBtn.onclick = function() {
        localStorage.removeItem('token');
        location.reload();
    };
    if (data.tg_auth) {
        activateButton('telegram');
    }
    if (data.yt_auth) {
        activateButton('youtube');
    }
    if (data.vk_auth) {
        activateButton('vk');
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

//нужно написать функцию, отправляющую POST на /login - это авторизация, будем вызывать при изменениях