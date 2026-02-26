import vk_api
from vk_api.upload import VkUpload
import os
import requests

class VideoUploader:
    
    def __init__(self, access_token=None):
        self.session = vk_api.VkApi(token=access_token)
        self.upload = VkUpload(self.session)
        self.api = self.session.get_api()

    def upload_video(self, video_path, title, description="", group_id=None):
        try:
            print(f"Начинаем загрузку видео: {title}")
            
            # Проверяем существование файла
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Файл {video_path} не найден")
            
            # Проверяем размер файла (VK ограничение ~2GB)
            file_size = os.path.getsize(video_path)
            if file_size > 2 * 1024 * 1024 * 1024:  # 2GB
                print("Файл очень большой, загрузка может занять время")
            
            # Загружаем видео
            video_info = self.api.video.save(
                video_file=video_path,
                name=title,
                description=description,
                group_id=group_id,
                wallpost=False,
                no_comments=False,
                repeat=True
            )
            #print(video_path)
            upload_url = video_info['upload_url']

            with open(video_path, 'rb') as f:
                file = {'video_file': f}
                response = requests.post(upload_url, files=file)

            print(response)
            
            return response
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return None