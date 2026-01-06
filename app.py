import tempfile
import hashlib
import base64
import flask
import secrets
import requests
from flask import Flask, render_template, request, jsonify, g
import pymysql
import jwt
import datetime
import bcrypt
import os
from flask_cors import CORS
from utils import VK, YouTube, Telegram

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(32)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app_id = "54311529"

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


# Подключение к MySQL
def get_db():
    return pymysql.connect(
        host='localhost',
        port=3306,
        user='admin',
        password='password',
        database='multiloader',
        cursorclass=pymysql.cursors.DictCursor  # Чтобы получать dict
    )

# Создание таблицы users
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Хеширование пароля
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Проверка пароля
def verify_password(password, hash):
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))

@app.route('/')
def home():
    return render_template('base.html')

# Регистрация
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Логин и пароль обязательны'}), 400

    conn = get_db()
    cur = conn.cursor()

    try:
        password_hash = hash_password(password)
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        return jsonify({'message': 'Пользователь успешно зарегистрирован'}), 201
    except pymysql.IntegrityError:
        return jsonify({'error': 'Пользователь с таким именем уже существует'}), 400
    finally:
        cur.close()
        conn.close()

# Логин и выдача JWT
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and verify_password(password, user['password_hash']):
        token = jwt.encode({
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Неверный логин или пароль'}), 401

# Защищённый маршрут
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
    app.run(debug=True, port=80, host='localhost')