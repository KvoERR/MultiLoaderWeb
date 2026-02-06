import { activateButton } from './authorization.js'
const authPopup = document.getElementById('auth-popup');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginTabBtn = document.getElementById('loginTabBtn');
const registerTabBtn = document.getElementById('registerTabBtn');
const authBtn = document.getElementById('auth-btn');
const tgInfoBtn = document.getElementById('tg-info-btn');
const tgAuthBtn = document.getElementById('tg-connect-btn');
const channelName = document.getElementById('channel-name');

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
async function login(e) {
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
        authUpdate(data);
    } else {
        alert('Ошибка: ' + data.error);
    }
}

async function register(e) {
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
        authUpdate(data);
    } else {
        alert('Ошибка: ' + data.error);
    }
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

// Проверка токена при загрузке страницы
window.addEventListener('load', function() {
    const token = localStorage.getItem('token');

    if (!authBtn) return;

    if (token) {
        authBtn.textContent = '👤';
        authBtn.title = 'Выйти';
        authBtn.onclick = function() {
            localStorage.removeItem('token');
            location.reload();
        };
        if (localStorage.getItem('token')) {
            activateButton('telegram');
        }
    } else {
        authBtn.textContent = 'ℹ️';
        authBtn.title = 'Войти';
        authBtn.onclick = function() {
            openAuthPopup('login');
        };
    }
});

