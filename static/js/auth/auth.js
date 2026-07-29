window.authYouTube = async function() {
    return new Promise((resolve, reject) => {
        const popup = window.open('/auth/youtube/login', '_blank');

        if (!popup) {
            reject(new Error('Браузер заблокировал всплывающее окно'));
            return;
        }

        const interval = setInterval(() => {
            try {
                if (popup.location.href) {
                    const currentUrl = new URL(popup.location.href);
                    if (currentUrl.pathname === '/') {
                        clearInterval(interval);
                        resolve(currentUrl.href);
                        popup.close();
                    }
                }
            } catch (error) {
            }

            // Если окно закрыто
            if (popup.closed) {
                clearInterval(interval);
                reject(new Error('Окно было закрыто пользователем'));
            }
        }, 500);

        setTimeout(() => {
            clearInterval(interval);
            if (!popup.closed) popup.close();
            reject(new Error('Таймаут ожидания редиректа'));
        }, 60000);
    });
}

window.authVK = async function() {
    return new Promise((resolve, reject) => {
        const popup = window.open('/auth/vk/login', '_blank');

        if (!popup) {
            reject(new Error('Браузер заблокировал всплывающее окно'));
            return;
        }

        const interval = setInterval(() => {
            try {
                if (popup.location.href) {
                    const currentUrl = new URL(popup.location.href);
                    if (currentUrl.pathname === '/') {
                        clearInterval(interval);
                        resolve(currentUrl.href);
                        popup.close();
                    }
                }
            } catch (error) {
            }

            // Если окно закрыто
            if (popup.closed) {
                clearInterval(interval);
                reject(new Error('Окно было закрыто пользователем'));
            }
        }, 500);

        setTimeout(() => {
            clearInterval(interval);
            if (!popup.closed) popup.close();
            reject(new Error('Таймаут ожидания редиректа'));
        }, 60000);
    });
}
