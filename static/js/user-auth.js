const authPopup = document.getElementById('auth-popup');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginTabBtn = document.getElementById('loginTabBtn');
const registerTabBtn = document.getElementById('registerTabBtn');

// Открыть попап и переключиться на нужную вкладку
function openAuthPopup(tab = 'login') {
    authPopup.style.display = 'flex';
    switchAuthTab(tab);
    document.body.style.overflow = 'hidden'; // Запрет прокрутки
}

// Закрыть попап
function closeAuthPopup() {
    authPopup.style.display = 'none';
    document.body.style.overflow = ''; // Разрешить прокрутку
}

// Переключение между вкладками: Вход / Регистрация
function switchAuthTab(tab) {
    loginForm.style.display = tab === 'login' ? 'flex' : 'none';
    registerForm.style.display = tab === 'register' ? 'flex' : 'none';

    loginTabBtn.classList.toggle('active', tab === 'login');
    registerTabBtn.classList.toggle('active', tab === 'register');
}

// Обработка формы входа
function login(e) {
    e.preventDefault();
    const formData = new FormData(loginForm);
    const username = formData.get('username');
    const password = formData.get('password');

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem('token', data.token);
            alert('Успешный вход!');
            closeAuthPopup();
            // Можно добавить перезагрузку или переход: window.location.reload();
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(err => {
        console.error('Ошибка входа:', err);
        alert('Ошибка соединения с сервером');
    });
}

// Обработка формы регистрации
function register(e) {
    e.preventDefault();
    const formData = new FormData(registerForm);
    const username = formData.get('username');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');

    if (password !== confirmPassword) {
        alert('Пароли не совпадают');
        return;
    }

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (response.ok) {
            alert('Регистрация успешна! Войдите в аккаунт.');
            switchAuthTab('login');
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(err => {
        console.error('Ошибка регистрации:', err);
        alert('Ошибка соединения с сервером');
    });
}

// Закрытие попапа по клику на подложку
authPopup.addEventListener('click', function(e) {
    if (e.target === authPopup) {
        closeAuthPopup();
    }
});

// Закрытие по клавише Esc
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && authPopup.style.display === 'flex') {
        closeAuthPopup();
    }
});