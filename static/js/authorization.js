export function activateButton(platform) {
    const button = document.getElementById(`${platform}-button`);
    button.style.backgroundColor = 'green';
    button.style.color = 'white';
    button.textContent='Привязано';
}

async function authUpdate(data) {
    authBtn.textContent = '👤';
    authBtn.title = 'Выйти';
    authBtn.onclick = function() {
        localStorage.removeItem('token');
        location.reload();
    };
    if (data.tg_auth) {
        activateButton('telegram');
    }
    localStorage.setItem('token', data.token);
    localStorage.setItem('tg_auth', data.tg_auth);
    console.log('tg_auth: ' + data.tg_auth);
    closeAuthPopup();
}