import requests
import os
from dotenv import load_dotenv

load_dotenv()  # загружает .env

bot_token = os.getenv('TG_BOT_TOKEN')

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB

def get_file_size(filepath):
    try:
        return os.path.getsize(filepath)
    except OSError as e:
        raise Exception(f"Файл не найден или недоступен: {e}")

def upload_video(video_path, name, description, chat_id):
    if not os.path.exists(video_path):
        print(f"Ошибка: файл не найден — {video_path}")
        return {'success': False, 'error': 'Файл не найден'}

    try:
        file_size = get_file_size(video_path)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return {'success': False, 'error': str(e)}
    
    caption = name+'\n'+description
    url = f'https://api.telegram.org/bot{bot_token}/sendVideo'

    if file_size > MAX_FILE_SIZE:
        url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
    else:
        url = f'https://api.telegram.org/bot{bot_token}/sendVideo'

    try:
        with open(video_path, 'rb') as video:
            response = requests.post(
                url,
                data={
                    'chat_id': chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML',
                    'supports_streaming': True
                },
                files={'video': video},
                timeout=300  # 5 минут на загрузку большого файла
            )

        result = response.json()

        if result.get('ok'):
            message_id = result['result']['message_id']
            video_url = f"https://t.me/c/{str(chat_id)[4:]}/{message_id}"
            print(f"✅ Видео опубликовано: {video_url}")
            return {'success': True, 'url': video_url}
        else:
            error_msg = result.get('description', 'Неизвестная ошибка')
            print(f"❌ Ошибка Telegram: {error_msg}")
            return {'success': False, 'error': error_msg}

    except requests.exceptions.Timeout:
        print("❌ Ошибка: таймаут при загрузке. Файл слишком большой или медленное соединение.")
        return {'success': False, 'error': 'Таймаут при загрузке'}
    except requests.exceptions.RequestException as e:
        print(f"❌ Сетевая ошибка: {e}")
        return {'success': False, 'error': f'Network error: {str(e)}'}
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return {'success': False, 'error': str(e)}
