const hash = window.location.hash.substr(1); //ищет url страницы
const params = {};
hash.split('&').forEach(param => {
    const [key, value] = param.split('=');
    params[key] = value;
});

if (params.access_token) {
       fetch('/save-token?token=' + params.access_token)
        .then(() => {
            document.body.innerHTML = '<h1>✅ Успех!</h1>';
            setTimeout(() => window.close(), 2000);
        });
}