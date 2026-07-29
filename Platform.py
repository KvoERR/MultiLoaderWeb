import secrets
import hashlib
import base64
import string
import urllib.parse
import requests
from google_auth_oauthlib.flow import Flow

class Platform:
    def __init__(self, code_verifier: str, client_id: str, client_secret: str, redirect_uri: str):
        self.code_verifier = code_verifier
        self.code_challenge = self.generate_code_challenge(self.code_verifier)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = self.generate_state()

    @staticmethod
    def generate_code_verifier() -> str:
        alphabet = string.ascii_letters + string.digits + "_-"
        return ''.join(secrets.choice(alphabet) for _ in range(64))

    @staticmethod
    def generate_code_challenge(code_verifier: str) -> str:
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').strip('=')
    
    @staticmethod
    def generate_state() -> str:
        return secrets.token_urlsafe(32)

class YouTube(Platform):
    def __init__(self, code_verifier: str, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(code_verifier, client_id, client_secret, redirect_uri)

    @property
    def scopes(self):
        return ["https://www.googleapis.com/auth/youtube.upload"]

    def get_authorization_url(self):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            code_challenge=self.code_challenge,
            code_challenge_method='S256',
        )
        return authorization_url, state

    def get_creds(self, code):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )

        flow.fetch_token(code=code, code_verifier=self.code_verifier)
        return flow.credentials

class VK(Platform):
    def __init__(self, code_verifier: str, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(code_verifier, client_id, client_secret, redirect_uri)

    def get_authorization_url(self) -> str:
        """
        Генерирует URL для авторизации VK ID.
        ВАЖНО: Использует НОВЫЙ эндпоинт id.vk.ru
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "video groups wall", 
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
            "state": self.state,
        }
        return f"https://id.vk.ru/authorize?{urllib.parse.urlencode(params)}"
    
    def get_token(self, code: str, device_id: str = None) -> dict:
        """
        Обменивает код на токены.
        ВАЖНО: Использует НОВЫЙ эндпоинт id.vk.ru/oauth2/auth
        и POST-запрос с данными в теле.
        """
        # Данные для POST-запроса (application/x-www-form-urlencoded)
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,  # Для конфиденциальных приложений
            "code": code,
            "code_verifier": self.code_verifier,  # Передаем оригинальный verifier
            "redirect_uri": self.redirect_uri,
        }
        
        # device_id может быть получен из редиректа
        if device_id:
            data["device_id"] = device_id
        
        try:
            response = requests.post(
                "https://id.vk.ru/oauth2/auth",
                data=data,  # requests сам закодирует как x-www-form-urlencoded
                timeout=30
            )
            
            print(f"VK token response status: {response.status_code}")
            print(f"VK token response: {response.text}")
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('error_description', error_data.get('error', 'Unknown error'))
                raise Exception(f"VK OAuth error: {error_msg}")
            
            result = response.json()
            
            if 'access_token' not in result:
                raise Exception("No access_token in response")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            raise Exception(f"Network error: {str(e)}")