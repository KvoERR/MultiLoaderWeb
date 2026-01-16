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
    .then(response => {
        if (!response.ok) {
            return response.json().then(errData => {
                throw new Error(errData.error || 'Ошибка входа');
            });
        }
        return response.json();
    })
    .then(data => {
        localStorage.setItem('token', data.token);
        alert('Успешный вход!');
        closeAuthPopup();
    })
    .catch(err => {
        console.error('Ошибка входа:', err);
        alert('Ошибка: ' + err.message);
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
    .then(response => {
        if (!response.ok) {
            // Если ошибка (например, 400, 500)
            return response.json().then(errData => {
                throw new Error(errData.error || 'Неизвестная ошибка');
            });
        }
        // Если всё ок — возвращаем JSON
        return response.json();
    })
    .then(data => {
        alert('Регистрация успешна! Войдите в аккаунт.');
        switchAuthTab('login');
    })
    .catch(err => {
        console.error('Ошибка регистрации:', err);
        alert('Ошибка: ' + err.message);
    });
}

function auth()
{
    
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

