export class VKAuth {

    constructor(href) {
        this.client_id = '54311529';
        this.redirect_url = href + 'auth/vk/callback';
        this.APP_NAME = 'MultiLoader';
    }
    generateState() {
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return Array.from(array, b => b.toString(16).padStart(2, '0')).join('');
    }
    generateCodeVerifier() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
        const length = 128;
        
        let verifier = '';
        const randomValues = new Uint8Array(length);
        crypto.getRandomValues(randomValues);
        
        for (let i = 0; i < length; i++) {
        verifier += chars[randomValues[i] % chars.length];
        }
        
        return verifier;
    }
    async generateCodeChallenge(verifier) {
        const encoder = new TextEncoder();
        const data = encoder.encode(verifier);
        const digest = await crypto.subtle.digest('SHA-256', data);
        
        return btoa(String.fromCharCode(...new Uint8Array(digest)))
        .replace(/=/g, '')
        .replace(/\+/g, '-')
        .replace(/\//g, '_');
    }
    validateState(receivedState) {
        const savedState = sessionStorage.getItem('vk_state');
        sessionStorage.removeItem('vk_state'); // Одноразовый
        
        return savedState === receivedState;
    }
    getCodeVerifier() {
        const verifier = sessionStorage.getItem('vk_code_verifier');
        sessionStorage.removeItem('vk_code_verifier'); // Одноразовый
        return verifier;
    }
    async startAuth() {
        console.log(this.client_id,this.redirect_url,this.APP_NAME)
        const VKID = window.VKIDSDK;
        const codeVerifier = this.generateCodeVerifier();
        const codeChallenge = await this.generateCodeChallenge(codeVerifier);
        const state = this.generateState();

        sessionStorage.setItem('vk_state', state);
        sessionStorage.setItem('vk_code_verifier', codeVerifier);

        VKID.Config.init({
            app: this.client_id, //id приложения
            redirectUrl: this.redirect_url, //адрес для редиректа
            state: state, //state для защиты от CSRF
            codeChallenge: codeChallenge, //код верификатор
            scope: 'video groups wall', 
            responseMode: VKID.ConfigResponseMode.Callback
        });

        // Открываем окно авторизации
        const result = await VKID.Auth.login();
        console.log(result)
        if (result.code != '102')
        {
            const returnedState = result.state;
            const savedState = sessionStorage.getItem('vk_state');
            const savedCodeVerifier = sessionStorage.getItem('vk_code_verifier');
            const deviceId = result.device_id;
            const code = result.code;

            // Проверка state
            if (!returnedState || returnedState !== savedState) {
                sessionStorage.removeItem('vk_state');
                sessionStorage.removeItem('vk_code_verifier');
                throw new Error('CSRF: state mismatch');
            }

            // Удаляем из хранилища после проверки
            sessionStorage.removeItem('vk_state');
            sessionStorage.removeItem('vk_code_verifier');

            // Передаём все необходимые данные на бэкенд
            const response = await fetch('/auth/vk/callback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: code,
                    state: returnedState,
                    code_verifier: savedCodeVerifier,
                    device_id: deviceId
                })
            });

            if (!response.ok) {
                const error = await response.text();
                console.error('Backend error:', error);
                throw new Error('Server validation failed');
            }

            const data = await response.json();
            console.log('Авторизация VK успешна:', data);
            return data; 
        }           
        else if (result.code === '102') {
            console.error('VK Auth error:', result.payload.error);
            throw new Error(`VK Auth failed: ${result.payload.error}`);
        }
    }
}