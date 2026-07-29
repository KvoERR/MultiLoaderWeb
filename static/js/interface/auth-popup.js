const authPopup = document.getElementById('auth-popup');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginTabBtn = document.getElementById('loginTabBtn');
const registerTabBtn = document.getElementById('registerTabBtn');
const authBtn = document.getElementById('auth-btn');
const closeBtn = document.querySelector('.close-btn');

window.openAuthPopup = function(tab = 'login') {
    if (!authPopup) return;
    authPopup.style.display = 'flex';
    window.switchAuthTab(tab);
    document.body.style.overflow = 'hidden';
}

window.closeAuthPopup = function() {
    if (!authPopup) return;
    authPopup.style.display = 'none';
    document.body.style.overflow = '';
}

window.switchAuthTab = function(tab) {
    if (loginForm) loginForm.style.display = tab === 'login' ? 'flex' : 'none';
    if (registerForm) registerForm.style.display = tab === 'register' ? 'flex' : 'none';

    if (loginTabBtn) loginTabBtn.classList.toggle('active', tab === 'login');
    if (registerTabBtn) registerTabBtn.classList.toggle('active', tab === 'register');
}

window.authUpdate = function(data) {
    const authBtn = document.getElementById('auth-btn');
    authBtn.textContent = '👤';
    authBtn.title = 'Выйти';
    authBtn.onclick = function() {
        if (confirm('Вы уверены, что хотите выйти?')) {
            localStorage.removeItem('token');
            localStorage.removeItem('tg_auth');
            localStorage.removeItem('vk_auth');
            location.reload();
        }
    };
    
    if (data.tg_chat_id) {
        window.activateButton('telegram');
        localStorage.setItem('tg_auth', 'true');
    }
    if (data.vk_group_id) {
        window.activateButton('vk');
        localStorage.setItem('vk_auth', 'true');
        const groupName = document.getElementById('vk-group-name');
        if (groupName) groupName.value = data.vk_group_id;
    }
    
    localStorage.setItem('token', data.token);
}

// Вешаем обработчики после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    if (authBtn) {
        authBtn.addEventListener('click', () => window.openAuthPopup('login'));
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', window.closeAuthPopup);
    }

    if (authPopup) {
        authPopup.addEventListener('click', (e) => {
            if (e.target === authPopup) window.closeAuthPopup();
        });
    }

    if (registerTabBtn) {
        registerTabBtn.addEventListener('click', () => {
            window.switchAuthTab('register');
        });
    }

    if (loginTabBtn) {
        loginTabBtn.addEventListener('click', () => {
            window.switchAuthTab('login');
        });
    }

    if (localStorage.getItem('tg_auth') === 'true') {
        window.activateButton('telegram');
    }
    
    if (localStorage.getItem('vk_auth') === 'true') {
        window.activateButton('vk');
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && authPopup?.style.display === 'flex') {
            window.closeAuthPopup();
        }
    });
});