import os
import ssl
import json
import random
import requests
import certifi
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
import vk_api
from vk_api.upload import VkUpload

ssl_context = ssl.create_default_context(cafile=certifi.where())

class Uploader:
    def __init__(self, title, video_path, description, category, image_path, tags, privacy):
        self.title = title
        self.video_path = video_path
        self.description = description
        self.category = category
        self.image_path = image_path
        self.tags = tags
        self.privacy = privacy

    @staticmethod
    def get_category_id(category):
        categories = {
            'Film & Animation': '1', 'Cars & Vehicles': '2', 'Music': '10',
            'Pets & Animals': '15', 'Sport': '17', 'Travel & Events': '19',
            'Gaming': '20', 'People & Blogs': '22', 'Comedy': '23',
            'Entertainment': '24', 'News & Politics': '25', 'How-to & Style': '26',
            'Education': '27', 'Science & Technology': '28', 'Non-profits & Activism': '29'
        }
        return categories.get(category, '22')

    def upload_video(self):
        raise NotImplementedError


class YouTubeUploader(Uploader):
    def __init__(self, title, video_path, description, category, image_path, tags, privacy, creds_dict):
        super().__init__(title, video_path, description, category, image_path, tags, privacy)
        self.creds = Credentials(**creds_dict)

    # TODO проблемы с большой загрузкой, нужно чанками, но не работает
    def upload_video(self):
        try:
            if not os.path.exists(self.video_path):
                return {'success': False, 'error': 'File not found'}

            if self.creds.expired:
                self.creds.refresh(Request())

            access_token = self.creds.token

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

            if not video_id:
                return {'success': False, 'error': 'No video ID in response'}

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
        self.session = vk_api.VkApi(token=access_token)
        self.api = self.session.get_api()

    def upload_video(self):
        try:
            if not os.path.exists(self.video_path):
                return {'success': False, 'error': 'File not found'}

            video_info = self.api.video.save(
                name=self.title,
                description=self.description,
                group_id=self.group_id,
                privacy_view=self.privacy,
                wallpost=False,
                no_comments=False,
                repeat=True
            )

            with open(self.video_path, 'rb') as f:
                response = requests.post(video_info['upload_url'], files={'video_file': f})

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'video_id': result.get('video_id', video_info.get('video_id')),
                    'message': 'Video uploaded successfully'
                }

            return {'success': False, 'error': f'Upload failed: {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}