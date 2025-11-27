import vk_api
from vk_api.upload import VkUpload
import os
import requests
import webbrowser
import threading
import time

class VideoUploader:
    token_storage={}
    app_id="54311529"
    def __init__(self, access_token):
        self.session = vk_api.VkApi(token=access_token)
        self.upload = VkUpload(self.session)
        self.api = self.session.get_api()

    @staticmethod
    def get_token():
        auth_url = (f"https://oauth.vk.com/authorize?"
                f"client_id={VideoUploader.app_id}"
                f"&display=page"
                f"&redirect_uri=http://localhost:5000/auth/vk/callback"
                f"&scope=video,offline,wall"
                f"&response_type=token"
                f"&v=5.131")
        
        webbrowser.open(auth_url)
        for i in range(30):
            if VideoUploader.token_storage.get('received'):
                return VideoUploader.token_storage['token']
            time.sleep(1)
    
        return None

    def upload_video(self, video_path, title, description="", group_id=None, album_id=None):
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
            video = self.upload.video(
                video_file=video_path,
                name=title,
                description=description,
                group_id=group_id,      # Для загрузки в группу
                album_id=album_id,      # ID альбома (опционально)
                wall_post=False,        # Исправлено: wall_post вместо wallpost
                no_comments=False,      # Разрешить комментарии
                repeat=True             # Зациклить воспроизведение
            )
            
            print("Видео успешно загружено!")
            print(f"Ссылка: https://vk.com/video{video['owner_id']}_{video['id']}")
            print(f"ID видео: {video['id']}")
            print(f"Владелец: {video['owner_id']}")
            
            return video
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return None

# Пример использования
if __name__ == "__main__":
    APP_ID = "54311529"  # Твой App ID
    
    # Получаем токен
    token = VKVideoUploader.get_token(APP_ID)
    
    if not token:
        print("❌ Не удалось получить токен")
        exit()
    
    # Создаем загрузчик
    uploader = VKVideoUploader(token)
    
    # Загружаем видео
    result = uploader.upload_video(
        video_path="my_video.mp4",  # Укажи правильный путь к файлу
        title="Мое первое видео через VK API",
        description="Это видео было загружено автоматически через VK Video API\n\n#автозагрузка #python",
        group_id=181950182  # Опционально: ID группы
    )
    
    if result:
        print("🎉 Видео загружено! Вот детали:")
        print(f"ID: {result['id']}")
        print(f"Владелец: {result['owner_id']}")
        print(f"Длительность: {result.get('duration', 'N/A')} сек")
        print(f"Дата: {result.get('date', 'N/A')}")