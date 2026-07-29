from flask import request, jsonify, session, redirect, current_app, Blueprint
import requests
import secrets
import urllib.parse
import jwt
from Platform import Platform, YouTube, VK
from models import User, SessionLocal

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/youtube/login')
def youtube_login():
    code_verifier = Platform.generate_code_verifier()
    session['youtube_code_verifier'] = code_verifier

    youtube = YouTube(code_verifier,
                      current_app.config["GOOGLE_CLIENT_ID"],
                      current_app.config["GOOGLE_CLIENT_SECRET"],
                      current_app.config["GOOGLE_REDIRECT_URI"])
    authorization_url, state = youtube.get_authorization_url()
    session['youtube_state'] = state
    return redirect(authorization_url)

@auth_bp.route('/auth/youtube/callback')
def youtube_callback():
    state = session.get('youtube_state')
    if not state or state != request.args.get('state'):
        return jsonify({'error': 'Invalid state'}), 400

    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Authorization code not found'}), 400

    code_verifier = session.get('youtube_code_verifier')
    if not code_verifier:
        return jsonify({'error': 'Missing code verifier in session'}), 400

    youtube = YouTube(code_verifier,
                      current_app.config["GOOGLE_CLIENT_ID"],
                      current_app.config["GOOGLE_CLIENT_SECRET"],
                      current_app.config["GOOGLE_REDIRECT_URI"])
    creds = youtube.get_creds(code)

    session['youtube_creds'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    session['yt_auth'] = True
    session.pop('youtube_code_verifier', None)

    return redirect('/')

@auth_bp.route('/auth/vk/login')
def vk_login():
    """Начало авторизации VK ID"""
    # Создаем экземпляр VK (он сам сгенерирует code_verifier и state)
    code_verifier = Platform.generate_code_verifier()
    vk = VK(code_verifier,
        current_app.config["VK_CLIENT_ID"],
        current_app.config["VK_CLIENT_SECRET"],
        current_app.config["VK_REDIRECT_URI"]
    )
    
    # Сохраняем параметры в сессии
    session['vk_code_verifier'] = vk.code_verifier
    session['vk_state'] = vk.state
    
    authorization_url = vk.get_authorization_url()
    return redirect(authorization_url)

@auth_bp.route('/auth/vk/callback')
def vk_callback():
    """Callback после авторизации VK ID"""
    # Проверяем state (защита от CSRF)
    state = session.get('vk_state')
    received_state = request.args.get('state')
    
    if not state or state != received_state:
        return jsonify({'error': 'Invalid state'}), 400
    
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Authorization code not found'}), 400
    
    # Получаем device_id из параметров (может быть не во всех случаях)
    device_id = request.args.get('device_id')
    
    # Восстанавливаем code_verifier из сессии
    code_verifier = session.get('vk_code_verifier')
    if not code_verifier:
        return jsonify({'error': 'Missing code verifier in session'}), 400

    # Создаем экземпляр VK с сохраненным code_verifier
    vk = VK(
        current_app.config["VK_CLIENT_ID"],
        current_app.config["VK_CLIENT_SECRET"],
        current_app.config["VK_REDIRECT_URI"],
        code_verifier
    )
    
    try:
        token_data = vk.get_token(code, device_id)
        
        # Сохраняем токены в сессии
        session['vk_token'] = token_data.get('access_token')
        session['vk_refresh_token'] = token_data.get('refresh_token')  # Если есть
        session['vk_user_id'] = token_data.get('user_id')
        session['vk_device_id'] = device_id  # Сохраняем для будущих обновлений
        session['vk_auth'] = True
        
        # Очищаем временные данные
        session.pop('vk_state', None)
        session.pop('vk_code_verifier', None)
        
        return redirect('/')
        
    except Exception as e:
        print(f"Ошибка в /auth/vk/callback: {e}")
        return jsonify({'error': str(e)}), 500

__all__ = ['auth_bp']