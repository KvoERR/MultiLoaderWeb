import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from traitlets import This

class VideoUploader:
    # Настройки OAuth 2.0
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    CLIENT_SECRETS_FILE = 'client_secret.json'  # Файл с учетными данными OAuth 2.0

    @staticmethod
    def get_authenticated_service(self):
        #Аутентификация и создание сервиса YouTube
        creds = None
    
        # Файл token.json сохраняет токены доступа/обновления
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
    
        # Если нет валидных учетных данных, запрашиваем авторизацию
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request()) # Обновляем истекший токен
            else:
                # Запрашиваем новые учетные данные
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRETS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
        
            # Сохраняем учетные данные для следующего запуска
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    
        return build('youtube', 'v3', credentials=creds)
    
    @staticmethod
    def upload_video(self, video_file, title, description, category_id="22", privacy_status="private", tags=None):
        # Создаем сервис YouTube
        youtube = self.authenticated_service()
    
        # Метаданные видео
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                # Дополнительные настройки статуса
                'selfDeclaredMadeForKids': False
            }
        }
    
        # Создаем медиа-объект для загрузки
        media = MediaFileUpload(
            video_file,
            chunksize=1024*1024,
            resumable=True
        )
    
        # Выполняем запрос на загрузку
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
    
        # Выполняем загрузку
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Загружено {int(status.progress() * 100)}%")
    
        print("Загрузка завершена!")
        print(f"ID видео: {response['id']}")
        print(f"Название: {response['snippet']['title']}")
        print(f"Ссылка: https://www.youtube.com/watch?v={response['id']}")
    
        return response



# Пример использования
if __name__ == "__main__":
    video_path = "my_video.mp4"
    video_title = "Мое первое видео через API"
    video_description = "Это видео было загружено с помощью YouTube Data API."
    
    # Категории YouTube:
    # 1 - Film & Animation
    # 2 - Autos & Vehicles  
    # 10 - Music
    # 15 - Pets & Animals
    # 17 - Sports
    # 20 - Gaming
    # 22 - People & Blogs
    # 23 - Comedy
    # 24 - Entertainment
    # 25 - News & Politics
    # 26 - Howto & Style
    # 27 - Education
    # 28 - Science & Technology
    
    # Загружаем видео
    YouTubeVideoUploader.upload_video(
        video_file=video_path,
        title=video_title,
        description=video_description,
        category_id="27",  # Education
        privacy_status="private",  # "public", "private", "unlisted"
        tags=["api", "python", "youtube", "программирование"]
    )
