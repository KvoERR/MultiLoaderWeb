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