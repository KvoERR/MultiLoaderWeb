import tempfile
import hashlib
import base64
import flask
import secrets
from flask import Flask, render_template, request, jsonify, session, redirect
import jwt
import datetime
import bcrypt
import os
from flask_cors import CORS
from utils import VK, YouTube, Telegram
from dotenv import load_dotenv
from auth import auth_bp
from models import User, init_db, SessionLocal


load_dotenv()

app = Flask(__name__)
app.register_blueprint(auth_bp)
CORS(app)
app.secret_key = secrets.token_hex(32)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app_id = "54311529" #TODO вроде небезопасно
bot_token=os.getenv('TG_BOT_TOKEN')

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
    extension = mime_to_text.get(file_storage.content_type, '.bin')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
        file_storage.save(temp_file.name)
        return temp_file.name

def generate_code_challenge(verifier):
    # SHA-256 хеширование
    sha256_hash = hashlib.sha256(verifier.encode('utf-8')).digest()
    # Base64url кодирование
    challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=')
    return challenge.decode('utf-8')

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
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
                'token': token,
                'tg_auth': user.tg_chat_id is not None,
                'yt_auth': user.yt_auth
        }), 201

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
                'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'token': token,
                'tg_auth': user.tg_chat_id is not None,
                'yt_auth': user.yt_auth
            })
            
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
            'tg_auth': user.tg_chat_id is not None
        }), 200

    except Exception as e:
        print(f"Ошибка в /authz: {e}")
        return jsonify({'success': False, 'error': 'Ошибка сервера'}), 500
    finally:
        db.close()

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

        youtube_result = 'None'
        vk_result = 'None'
        if 'youtube' in platforms:
            youtube_uploader = YouTube.VideoUploader(flask.session['youtube_creds'])
            youtube_result = youtube_uploader.upload_video(
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
            'youtube_result': youtube_result,
            'vk_result': vk_result,
            'message': 'Данные успешно получены и обработаны'
        }) 
    except Exception as e:
        print(f"Ошибка при обработке формы: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=80, host='localhost')