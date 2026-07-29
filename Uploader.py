import os
import json
import random
import requests
import ssl
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
import vk_api

try:
    ssl._create_default_https_context = ssl.create_default_context()
except AttributeError:
    pass


class Uploader:
    CATEGORIES = {
        'Film & Animation': '1', 'Cars & Vehicles': '2', 'Music': '10',
        'Pets & Animals': '15', 'Sport': '17', 'Travel & Events': '19',
        'Gaming': '20', 'People & Blogs': '22', 'Comedy': '23',
        'Entertainment': '24', 'News & Politics': '25', 'How-to & Style': '26',
        'Education': '27', 'Science & Technology': '28', 'Non-profits & Activism': '29'
    }

    def __init__(self, title, video_path, description, category, image_path, tags, privacy):
        self.title = title
        self.video_path = video_path
        self.description = description
        self.category = category
        self.image_path = image_path
        self.tags = tags
        self.privacy = privacy

    @classmethod
    def get_category_id(cls, category):
        return cls.CATEGORIES.get(category, '22')

    def upload_video(self):
        raise NotImplementedError

class YouTubeUploader(Uploader):
    def __init__(self, title, video_path, description, category, image_path, tags, privacy, creds_dict):
        super().__init__(title, video_path, description, category, image_path, tags, privacy)
        self.creds = Credentials(**creds_dict)

    def upload_video(self):
        try:
            if not os.path.exists(self.video_path):
                return {'success': False, 'error': 'File not found'}

            if self.creds.expired:
                self.creds.refresh(Request())

            access_token = self.creds.token
            file_size = os.path.getsize(self.video_path)

            tags_list = [t.strip() for t in self.tags.split(',')] if self.tags else []
            privacy = self.privacy.lower() if self.privacy else 'private'
            category_id = self.get_category_id(self.category)

            metadata = {
                'snippet': {
                    'title': self.title,
                    'description': self.description or '',
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy,
                    'madeForKids': False
                }
            }
            if tags_list:
                metadata['snippet']['tags'] = tags_list

            # ===== ДЛЯ МАЛЕНЬКИХ ФАЙЛОВ (< 10 MB) - MULTIPART =====
            if file_size < 10 * 1024 * 1024:
                with open(self.video_path, 'rb') as f:
                    video_data = f.read()

                boundary = f"boundary_{random.randint(100000, 999999)}"
                metadata_json = json.dumps(metadata)

                body_parts = [
                    f"--{boundary}".encode(),
                    b"Content-Type: application/json; charset=UTF-8",
                    b"",
                    metadata_json.encode('utf-8'),
                    f"--{boundary}".encode(),
                    b"Content-Type: video/mp4",
                    b"",
                    video_data,
                    f"--{boundary}--".encode()
                ]

                response = requests.post(
                    "https://www.googleapis.com/upload/youtube/v3/videos",
                    params={"part": "snippet,status", "uploadType": "multipart"},
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": f"multipart/related; boundary={boundary}"
                    },
                    data=b"\r\n".join(body_parts),
                    timeout=300
                )

                if response.status_code != 200:
                    return {'success': False, 'error': response.text}

                result = response.json()
                video_id = result.get('id')

            # ===== ДЛЯ БОЛЬШИХ ФАЙЛОВ (> 10 MB) - RESUMABLE =====
            else:
                metadata_json = json.dumps(metadata)

                # Получаем URL для загрузки
                response = requests.post(
                    "https://www.googleapis.com/upload/youtube/v3/videos",
                    params={"part": "snippet,status", "uploadType": "resumable"},
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json; charset=UTF-8",
                        "X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(file_size)
                    },
                    data=metadata_json,
                    timeout=60
                )

                if response.status_code not in [200, 201]:
                    return {'success': False, 'error': response.text}

                upload_url = response.headers.get('Location')
                if not upload_url:
                    return {'success': False, 'error': 'No upload URL'}

                # Загружаем чанками по 10MB
                chunk_size = 10 * 1024 * 1024
                uploaded = 0

                with open(self.video_path, 'rb') as f:
                    while uploaded < file_size:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break

                        start = uploaded
                        end = uploaded + len(chunk) - 1
                        content_range = f"bytes {start}-{end}/{file_size}"

                        response = requests.put(
                            upload_url,
                            headers={
                                "Content-Range": content_range,
                                "Content-Length": str(len(chunk))
                            },
                            data=chunk,
                            timeout=60
                        )

                        if response.status_code in [200, 201]:
                            break
                        elif response.status_code == 308:
                            uploaded += len(chunk)
                        else:
                            return {'success': False, 'error': response.text}

                if response.status_code not in [200, 201]:
                    return {'success': False, 'error': 'Upload incomplete'}

                result = response.json()
                video_id = result.get('id')

            if not video_id:
                return {'success': False, 'error': 'No video ID'}

            if self.image_path and os.path.exists(self.image_path):
                try:
                    with open(self.image_path, 'rb') as f:
                        image_data = f.read()

                    requests.post(
                        "https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                        params={"videoId": video_id},
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "image/jpeg"
                        },
                        data=image_data,
                        timeout=60
                    )
                except Exception:
                    pass

            return {
                'success': True,
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            }

        except HttpError as e:
            return {'success': False, 'error': f'YouTube API error: {e.content}'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class VKUploader(Uploader):
    def __init__(self, title, video_path, description, category, image_path, tags, privacy, group_id=None, access_token=None):
        super().__init__(title, video_path, description, category, image_path, tags, privacy)
        self.group_id = group_id
        self.access_token = access_token
        self.session = vk_api.VkApi(token=access_token)
        self.api = self.session.get_api()

    def upload_video(self):
        try:
            if not os.path.exists(self.video_path):
                return {'success': False, 'error': f'File not found: {self.video_path}'}

            # 🔥 ПРАВИЛЬНЫЙ privacy для VK
            privacy_map = {
                'public': '0',      # Все видят
                'private': '1',     # Только я
                'friends': '2',     # Только друзья
                'group': '3'        # Только участники группы
            }
            
            # Получаем ID группы (без знака минус)
            group_id = self.group_id
            if group_id and str(group_id).startswith('-'):
                group_id = str(group_id)[1:]  # Убираем минус
            
            # 🔥 ПРАВИЛЬНЫЙ ВЫЗОВ video.save
            video_info = self.api.video.save(
                name=self.title[:200],  # Ограничение VK
                description=self.description[:1000] if self.description else '',
                group_id=int(group_id) if group_id else None,
                privacy_view=privacy_map.get(self.privacy, '0'),
                wallpost=0,
                no_comments=0,
                repeat=1
            )
            
            upload_url = video_info['upload_url']
            video_id = video_info.get('video_id')
            owner_id = video_info.get('owner_id')
            
            # 🔥 ЗАГРУЗКА ВИДЕО
            with open(self.video_path, 'rb') as f:
                response = requests.post(
                    upload_url,
                    files={'video_file': f},
                    timeout=300  # 5 минут на загрузку
                )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Проверяем, что видео загружено
                    # VK возвращает разные форматы ответа
                    if 'video_id' in result:
                        video_id = result.get('video_id', video_id)
                        owner_id = result.get('owner_id', owner_id)
                    elif 'id' in result:
                        video_id = result.get('id', video_id)
                        owner_id = result.get('owner_id', owner_id)
                    
                    # Формируем ссылку на видео
                    video_url = f"https://vk.com/video{owner_id}_{video_id}"
                    if self.group_id:
                        video_url = f"https://vk.com/video-{group_id}_{video_id}"
                    
                    return {
                        'success': True,
                        'video_id': video_id,
                        'owner_id': owner_id,
                        'url': video_url,
                        'message': 'Video uploaded successfully'
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Failed to parse VK response: {str(e)}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Upload failed with status {response.status_code}: {response.text}'
                }
                
        except vk_api.exceptions.ApiError as e:
            error_msg = str(e)
            
            # Детальная обработка ошибок VK
            if 'video already exists' in error_msg.lower():
                return {'success': False, 'error': 'Видео с таким названием уже существует'}
            elif 'access denied' in error_msg.lower():
                return {'success': False, 'error': 'Нет доступа к группе. Проверьте права токена'}
            elif 'group id' in error_msg.lower():
                return {'success': False, 'error': f'Неверный ID группы: {self.group_id}'}
            else:
                return {'success': False, 'error': f'VK API error: {error_msg}'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Network error: {str(e)}'}
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}