const authPopup = document.getElementById('auth-popup');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginTabBtn = document.getElementById('loginTabBtn');
const registerTabBtn = document.getElementById('registerTabBtn');
const authBtn = document.getElementById('auth-btn');
const closeBtn = document.querySelector('.close-btn');

export function openAuthPopup(tab = 'login') {
    if (!authPopup) return;
    authPopup.style.display = 'flex';
    switchAuthTab(tab);
    document.body.style.overflow = 'hidden';
}

export function closeAuthPopup() {
    if (!authPopup) return;
    authPopup.style.display = 'none';
    document.body.style.overflow = '';
}

export function switchAuthTab(tab) {
    if (loginForm) loginForm.style.display = tab === 'login' ? 'flex' : 'none';
    if (registerForm) registerForm.style.display = tab === 'register' ? 'flex' : 'none';

    if (loginTabBtn) loginTabBtn.classList.toggle('active', tab === 'login');
    if (registerTabBtn) registerTabBtn.classList.toggle('active', tab === 'register');
}

// Вешаем обработчики после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    if (authBtn) {
        authBtn.addEventListener('click', () => openAuthPopup('login'));
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closeAuthPopup);
    }

    if (authPopup) {
        authPopup.addEventListener('click', (e) => {
            if (e.target === authPopup) closeAuthPopup();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && authPopup?.style.display === 'flex') {
            closeAuthPopup();
        }
    });
});