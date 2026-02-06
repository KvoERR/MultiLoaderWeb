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
    def __init__(self, creds_dict):
        self.creds = Credentials(
            token=creds_dict['token'],
            refresh_token=creds_dict['refresh_token'],
            token_uri=creds_dict['token_uri'],
            client_id=creds_dict['client_id'],
            client_secret=creds_dict['client_secret'],
            scopes=creds_dict['scopes']
        )

    def get_service(self):
        if self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
        return build('youtube', 'v3', credentials=self.creds)

    def upload_video(self, title, description, category, video_path, image_path=None,
                     tags=None, privacy="private"):
        youtube = self.get_service()

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': get_category_id(category)
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False
            }
        }

        media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)
        request = youtube.videos().insert(part='snippet,status', body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Загружено: {int(status.progress() * 100)}%")

        video_id = response['id']
        print(f"✅ Видео загружено: https://youtu.be/{video_id}")

        if image_path:
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(image_path, mimetype='image/jpeg')
                ).execute()
                print("🖼 Обложка загружена")
            except Exception as e:
                print(f"⚠️ Ошибка обложки: {e}")

        return response