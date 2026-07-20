import secrets
import hashlib
import base64
import string
from typing import List, Optional
import requests
from flask import session

from google_auth_oauthlib.flow import Flow


class Platform:
    def __init__(self, code_verifier: str, client_id: str, client_secret: str, redirect_uri: str):
        self.code_verifier = code_verifier
        self.code_challenge = self.generate_code_challenge(self.code_verifier)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @staticmethod
    def generate_code_verifier() -> str:
        alphabet = string.ascii_letters + string.digits + "_-"
        return ''.join(secrets.choice(alphabet) for _ in range(64))

    @staticmethod
    def generate_code_challenge(code_verifier: str) -> str:
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').strip('=')

class YouTube(Platform):
    def __init__(self, code_verifier: str, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(code_verifier, client_id, client_secret, redirect_uri)

    @property
    def scopes(self):
        return ["https://www.googleapis.com/auth/youtube.upload"]

    def get_authorization_url(self) -> str:
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

    def get_creds(self, code) -> dict:
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
        creds = flow.credentials

        return creds

class VK(Platform):
    def __init__(self, code_verifier: str, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(code_verifier, client_id, client_secret, redirect_uri)

    @property
    def scopes(self):
        return ["video groups wall"]

    @property
    def auth_url(self):
        return "https://oauth.vk.com/oauth/authorize"

    @property
    def token_url(self):
        return "https://oauth.vk.com/oauth/access_token"

    def get_authorization_url(self) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256"
        }
        import urllib.parse
        query = urllib.parse.urlencode(params)
        return f"{self.auth_url}?{query}"

    def get_token(self, code: str) -> dict:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "grant_type": "authorization_code",
            "code_verifier": self.code_verifier,
        }

        response = requests.post(self.token_url, data=data)
        result = response.json()
        
        return result

