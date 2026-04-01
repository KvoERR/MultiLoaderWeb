export function connectYouTube() {
    return new Promise((resolve, reject) => {
        const popup = window.open('/auth/youtube/login', '_blank');

        const interval = setInterval(() => {
            try {
                const currentUrl = new URL(popup.location.href);

                if (currentUrl.pathname === '/') {
                    clearInterval(interval);
                    resolve(currentUrl.href);
                    popup.close();
                }
            } catch (error) {
                console.log('Не могу прочитать URL — возможно, разные домены');
            }
            if (popup.closed) {
                clearInterval(interval);
                reject(new Error('Окно было закрыто пользователем'));
            }
        }, 500);
        setTimeout(() => {
            if (interval) {
                clearInterval(interval);
                if (!popup.closed) popup.close();
                reject(new Error('Таймаут ожидания редиректа'));
            }
        }, 60000);
    });
}