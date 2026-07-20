import tempfile
import flask
from flask import Flask, render_template, request, jsonify, session, redirect
import jwt
import datetime
from datetime import timezone
import bcrypt
import os
from flask_cors import CORS
from utils import VK, YouTube, Telegram
from Uploader import YouTubeUploader, VKUploader
from models import User, SessionLocal
from auth import auth_bp
from dotenv import load_dotenv

app = Flask(__name__)
app.register_blueprint(auth_bp)
CORS(app)

load_dotenv()
app.config['TG_BOT_TOKEN'] = os.getenv('TG_BOT_TOKEN')
app.config['VK_APP_ID'] = os.getenv('VK_APP_ID')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_REDIRECT_URI'] = os.getenv('GOOGLE_REDIRECT_URI')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
app.config['VK_REDIRECT_URI'] = os.getenv('VK_REDIRECT_URI')

def get_file_path(file_storage):
    if not file_storage:
        return None
    
    mime_to_text = {
        'video/mp4': '.mp4',
        'video/avi': '.avi',
        'video/mov': '.mov',
        'video/webm': '.webm',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp'
    }
    extension = mime_to_text.get(file_storage.content_type, '.bin')
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            file_storage.save(temp_file.name)
            return temp_file.name
    except Exception as e:
        print(f"Ошибка сохранения файла: {e}")
        raise

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hash):
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    yt_auth = session.get('yt_auth', False)

    if not username or not password:
        return jsonify({'error': 'Логин и пароль обязательны'}), 400

    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first():
            return jsonify({'error': 'Пользователь уже существует'}), 400

        password_hash = hash_password(password)
        user = User(username=username, password_hash=password_hash)
        db.add(user)
        db.commit()
        db.refresh(user)

        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
                'success': True,
                'token': token,
                'yt_auth': yt_auth,
                'tg_chat_id': user.tg_chat_id,
                'vk_group_id': user.vk_group_id
            }), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Ошибка сервера'}), 500
    finally:
        db.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    yt_auth = session.get('yt_auth', False)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            token = jwt.encode({
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'success': True,
                'token': token,
                'yt_auth': yt_auth,
                'tg_chat_id': user.tg_chat_id,
                'vk_group_id': user.vk_group_id
            }), 200
            
        else:
            return jsonify({'error': 'Неверный логин или пароль'}), 401
    except Exception as e:
        print(f"[ERROR] /login: {type(e).__name__}: {e}") 
        return jsonify({'error': 'Ошибка сервера'}), 500
    finally:
        db.close()

@app.route('/authz', methods=['POST'])
def authz():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'error': 'Требуется авторизация'}), 401

    token = auth_header[7:]

    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'error': 'Токен истёк'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'error': 'Неверный токен'}), 401
    
    yt_auth = session.get('yt_auth', False)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404

        return jsonify({
            'success': True,
            'token': token,
            'yt_auth': yt_auth,
            'tg_chat_id': user.tg_chat_id,
            'vk_group_id': user.vk_group_id
        }), 200

    except Exception as e:
        print(f"Ошибка в /authz: {e}")
        return jsonify({'success': False, 'error': 'Ошибка сервера'}), 500
    finally:
        db.close()

@app.route('/process', methods=['POST'])
def process_form():
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'success': False, 'error': 'Требуется авторизация'}), 401

    token = auth_header[7:]

    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'error': 'Токен истёк'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'error': 'Неверный токен'}), 401
    
    # Инициализируем переменные для finally блока
    video_path = None
    image_path = None
    db = None
    
    try:
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        video_file = request.files.get('video')
        image_file = request.files.get('image')
        tags = request.form.get('tags', '').strip()
        privacy = request.form.get('privacy', '')
        platforms = request.form.getlist('platforms')

        if not title:
            return jsonify({
                'success': False,
                'error': 'Название не может быть пустым'
            }), 400
        if not video_file:
            return jsonify({
                'success': False,
                'error': 'Нужно загрузить видео'
            }), 400
        if not platforms:
            return jsonify({
                'success': False,
                'error': 'Выберите хотя бы одну платформу'
            }), 400
        
        # Проверка размера файла
        MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500 MB
        if video_file.content_length and video_file.content_length > MAX_VIDEO_SIZE:
            return jsonify({
                'success': False, 
                'error': f'Файл слишком большой. Максимальный размер: 500 MB'
            }), 400
        
        video_path = get_file_path(video_file)
        image_path = get_file_path(image_file) if image_file else None

        print(f"🔍 Video file size: {os.path.getsize(video_path) / (1024*1024):.2f} MB")
        if image_path:
            print(f"🔍 Image file size: {os.path.getsize(image_path) / (1024*1024):.2f} MB")

        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404

        youtube_result = None
        vk_result = None
        telegram_result = None

        # Загрузка на YouTube
        if 'youtube' in platforms:
            if 'youtube_creds' not in session:
                return jsonify({'success': False, 'error': 'YouTube не авторизован'}), 400
            try:
                creds = session['youtube_creds']
                print(f"🔍 YouTube creds check:")
                print(f"   token: {creds.get('token', 'MISSING')[:30]}...")
                print(f"   refresh_token: {'YES' if creds.get('refresh_token') else 'MISSING'}")
                print(f"   expires_in: {creds.get('expiry', 'MISSING')}")
                youtube_uploader = YouTubeUploader(
                    title,
                    video_path,
                    description,
                    category,
                    image_path,
                    tags,
                    privacy,
                    session['youtube_creds']
                ) 
                youtube_result = youtube_uploader.upload_video()
            except Exception as e:
                print(f"Ошибка загрузки на YouTube: {e}")
                youtube_result = {'success': False, 'error': str(e)}
        
        # Загрузка на VK
        if 'vk' in platforms:
            if 'vk_token' not in session:
                return jsonify({'success': False, 'error': 'VK не авторизован'}), 400
            try:
                vk_uploader = VK.VideoUploader(session['vk_token'])
                vk_result = vk_uploader.upload_video(
                    video_path=video_path,
                    title=title,
                    description=description,
                    privacy_view=privacy,
                    group_id=user.vk_group_id
                )
            except Exception as e:
                print(f"Ошибка загрузки на VK: {e}")
                vk_result = {'success': False, 'error': str(e)}

        # Загрузка в Telegram
        if 'telegram' in platforms:
            try:
                telegram_result = Telegram.upload_video(
                    video_path=video_path,
                    name=title,
                    description=description,
                    chat_id=user.tg_chat_id
                )
            except Exception as e:
                print(f"Ошибка загрузки в Telegram: {e}")
                telegram_result = {'success': False, 'error': str(e)}

        # Проверяем, была ли хоть одна успешная загрузка
        all_results = [r for r in [youtube_result, vk_result, telegram_result] if r is not None]
        any_success = any(r.get('success', False) if isinstance(r, dict) else False for r in all_results)

        return jsonify({
            'success': any_success,
            'youtube_result': youtube_result,
            'vk_result': vk_result,
            'telegram_result': telegram_result,
            'message': 'Данные успешно обработаны' if any_success else 'Все загрузки завершились ошибкой'
        })
        
    except Exception as e:
        print(f"Ошибка при обработке формы: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500
    finally:
        # Закрываем соединение с БД, если оно было создано
        if db is not None:
            db.close()
        
        # Удаляем временные файлы
        for path in [video_path, image_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"🗑️ Удален временный файл: {path}")
                except Exception as e:
                    print(f"⚠️ Не удалось удалить {path}: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=80, host='localhost')