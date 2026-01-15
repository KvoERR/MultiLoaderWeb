import tempfile
import hashlib
import base64
import flask
import secrets
import requests
from flask import Flask, render_template, request, jsonify, g
import jwt
import datetime
import bcrypt
import os
from flask_cors import CORS
from utils import VK, YouTube, Telegram
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(32)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app_id = "54311529" #TODO вроде небезопасно
bot_token=os.getenv('TG_BOT_TOKEN')

DATABASE_URI = os.getenv('DATABASE_URI')
engine = create_engine(DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    tg_chat_id = Column(Integer)
    tg_chat_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_file_path(file_storage):
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
    extension = mime_to_text.get(file_storage, '.bin')
    
    # Создаем временный файл с правильным расширением
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
        file_storage.save(temp_file.name)
        return temp_file.name  # Возвращаем путь к файлу

def generate_code_challenge(verifier):
    # SHA-256 хеширование
    sha256_hash = hashlib.sha256(verifier.encode('utf-8')).digest()
    # Base64url кодирование
    challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=')
    return challenge.decode('utf-8')

# Хеширование пароля
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Проверка пароля
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

        return jsonify({'message': 'Пользователь успешно зарегистрирован'}), 201
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

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            token = jwt.encode({
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({'token': token})
        else:
            return jsonify({'error': 'Неверный логин или пароль'}), 401
    except Exception as e:
        return jsonify({'error': 'Ошибка сервера'}), 500
    finally:
        db.close()

@app.route('/upload', methods=['POST'])
def upload():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Требуется токен авторизации'}), 401

    try:
        if token.startswith('Bearer '):
            token = token[7:]
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({
            'message': f'Видео успешно загружено от имени {data["username"]}',
            'user_id': data['user_id']
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Срок действия токена истёк'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Неверный токен'}), 401


@app.route('/process', methods=['POST'])
def process_form():
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
            })
        if not video_file:
            return jsonify({
                'success': False,
                'error': 'Нужно загрузить видео'
            }) 
        if not platforms:
            return jsonify({
                'success': False,
                'error': 'Выберите хотя бы одну платформу'
            })
        
        video_path=get_file_path(video_file)
        image_path=get_file_path(image_file)

        yt_result = 'None'
        vk_result = 'None'
        if 'youtube' in platforms:
            yt_result = YouTube.VideoUploader.upload_video(
                title=title,
                description=description,
                video=video_path,
                image=image_path,
                tags=tags,
                privacy=privacy,
                category=category
            ) 
        
        if 'vk' in platforms:
            vk_uploader = VK.VideoUploader(flask.session['vk_token'])
            vk_result = vk_uploader.upload_video(
                video_path=video_path,
                title=title,
                description=description
            )

        if 'telegram' in platforms:
            telegram_result = Telegram.upload_video(
                video_path=video_path,
                name=title,
                description=description
            )       

        return jsonify({
            'success': True,
            'yt_result': yt_result,
            'vk_result': vk_result,
            'message': 'Данные успешно получены и обработаны'
        }) 
    except Exception as e:
        print(f"Ошибка при обработке формы: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        })
    
@app.route('/auth/tg', methods=['POST'])  # ← Убери слеш в конце
def tg_auth():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    channel_name = data.get('channel_name', '').strip()

    if not channel_name:
        return jsonify({'error': 'Channel name is required'}), 400
    
    request_result = requests.get(
        f'https://api.telegram.org/bot{bot_token}/getUpdates'
        ).json()

    for update in request_result.get('result', []):
        channel_post = update['channel_post']
        if 'text' in channel_post and channel_post.get('text', '')==channel_name:
            chat_id = channel_post['chat']['id']
            message_text = channel_post.get('text', '')

            print(f"ID чата: {chat_id}")


    return jsonify({
            'success': True, 
            'message': 'Authorized'
            }), 200
            
'''
    # Получаем текущего пользователя (по токену из заголовка)
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authentication required'}), 401

    try:
        if token.startswith('Bearer '):
            token = token[7:]
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid or expired token'}), 401

    # Сохраняем название канала в БД
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.tg_chat_name = channel_name
        # Пока tg_chat_id неизвестен — можно заполнить позже
        db.commit()

        return jsonify({
            'success': True,
            'message': f'Канал "{channel_name}" привязан к вашему аккаунту'
        }), 200
    except Exception as e:
        db.rollback()
        print("❌ Ошибка при привязке канала:", e)
        return jsonify({'error': 'Database error'}), 500
    finally:
        db.close()
        '''

@app.route('/auth/vk/callback', methods=['POST'])
def vk_callback():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        code = data.get('code')
        state = data.get('state')
        code_verifier = data.get('code_verifier')
        device_id = data.get('device_id')

        if not code or not state or not code_verifier or not device_id:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        request_result=requests.post(
            url='https://id.vk.ru/oauth2/auth',
            data = {
                'grant_type': 'authorization_code',
                'code_verifier': code_verifier,
                'redirect_uri': 'http://localhost:80/auth/vk/callback', 
                'code': code,
                'client_id': app_id,
                'device_id': device_id,
                'state': state
            },
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            } 
        )
        flask.session['vk_token'] = request_result.json()['access_token']
        return jsonify({
            'success': True, 
            'message': 'Authorized'
            })

    except Exception as e:
        print(f"Ошибка в /auth/vk/callback: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=80, host='localhost')