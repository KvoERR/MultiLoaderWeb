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
        if (localStorage.getItem('tg_auth')) {
            activateButton('telegram');
        }
        if (localStorage.getItem('yt_auth')) {
            activateButton('youtube');
        }
    } else {
        authBtn.textContent = 'ℹ️';
        authBtn.title = 'Войти';
        authBtn.onclick = function() {
            openAuthPopup('login');
        };
    }
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
    localStorage.setItem('token', data.token);
    localStorage.setItem('tg_auth', data.tg_auth);
    console.log('tg_auth: ' + data.tg_auth);
    closeAuthPopup();
}