import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_category_id(category):
        category_to_id = {
        'Film & Animation':'1',
        'Cars & Vehicles':'2',
        'Music':'10',
        'Pets & Animals':'15',
        'Sport':'17',
        'Travel & Events':'19',
        'Gaming':'20',
        'People & Blogs':'22',
        'Comedy':'23',
        'Entertainment':'24',
        'News & Politics':'25',
        'How-to & Style':'26',
        'Education':'27',
        'Science & Technology':'28',
        'Non-profits & Activism':'29'
        }
        return category_to_id.get(category, '22')
class VideoUploader:
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    CLIENT_SECRETS_FILE = 'secrets/client_secret.json' # TODO небезопасно!!! переделать

    # TODO переделать на аутентификацию OAuth или что то вроде
    def get_authenticated_service():
        creds = None
        token_path = 'secrets/token.json'
        
        # Загружаем существующий токен
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, VideoUploader.SCOPES)
            except Exception as e:
                print(f"Ошибка загрузки токена: {e}")
                os.remove(token_path)  # Удаляем поврежденный токен
                creds = None
        
        # Если нет валидных учетных данных
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Ошибка обновления токена: {e}")
                    creds = None
            else:
                # Новая авторизация с получением refresh_token
                flow = InstalledAppFlow.from_client_secrets_file(
                    VideoUploader.CLIENT_SECRETS_FILE, 
                    VideoUploader.SCOPES
                )
                creds = flow.run_local_server(
                    port=0,
                    access_type='offline',  # Получаем refresh_token
                    include_granted_scopes='true'
                )
            
            # Сохраняем новые учетные данные
            os.makedirs('secrets', exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
            print("Токен сохранен с refresh_token")
        
        return build('youtube', 'v3', credentials=creds)
    
    def upload_video(title, description, category, video, image,
                    tags, privacy="private"):
        # Создаем сервис YouTube
        youtube = VideoUploader.get_authenticated_service()
    
        category_id = get_category_id(category)
        # Метаданные видео
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False
            }
        }

        # Создаем медиа-объект для загрузки видео
        media = MediaFileUpload(
            video,
            chunksize=1024*1024,
            resumable=True
        )

        # Выполняем запрос на загрузку видео
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        # Выполняем загрузку видео
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Загружено {int(status.progress() * 100)}%")

        video_id = response['id']
        print("Загрузка видео завершена!")
        print(f"ID видео: {video_id}")
        print(f"Ссылка: https://www.youtube.com/watch?v={video_id}")

        if image:
            try:
                print("Загружаем обложку для видео...")
                
                # Создаем медиа-объект для обложки
                thumbnail_media = MediaFileUpload(
                    image,
                    mimetype='image/jpeg'  # Автоматически определит тип
                )
                
                # Загружаем обложку
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=thumbnail_media
                ).execute()
                
                print("✅ Обложка успешно загружена!")
                
            except Exception as e:
                print(f"⚠️ Ошибка загрузки обложки: {e}")
                # Не прерываем выполнение, т.к. видео уже загружено

        return response