document.addEventListener('DOMContentLoaded', () => {
    window.authz();
});

window.login = async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const username = formData.get('username');
    const password = formData.get('password');

    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
        window.closeAuthPopup();
        window.authUpdate(data);
    } else {
        alert('Ошибка: ' + data.error);
    }
}

window.register = async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const username = formData.get('username');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');

    if (password !== confirmPassword) {
        alert('Пароли не совпадают');
        return;
    }

    const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
        window.authUpdate(data);
    } else {
        alert('Ошибка: ' + data.error);
    }
}

window.authz = async function() {
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
            window.authUpdate(data);
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