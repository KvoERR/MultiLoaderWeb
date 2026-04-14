from flask import request, jsonify, session, redirect, current_app, Blueprint
from google_auth_oauthlib.flow import Flow
import hashlib
import base64
import secrets
import os
import requests
import jwt
from models import User, SessionLocal

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/youtube/login')
def youtube_login():
    code_verifier = secrets.token_urlsafe(64)
    session['code_verifier'] = code_verifier  # ← сохраняем в сессии

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config["GOOGLE_CLIENT_ID"],
                "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [current_app.config["GOOGLE_REDIRECT_URI"]]
            }
        },
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
        redirect_uri=current_app.config["GOOGLE_REDIRECT_URI"],
    )

    # Создаём code_challenge из code_verifier
    import hashlib
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').strip('=')

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        code_challenge=code_challenge,
        code_challenge_method='S256'
    )
    session['oauth_state'] = state
    return redirect(authorization_url)

@auth_bp.route('/auth/youtube/callback')
def youtube_callback():
    state = session.get('oauth_state')
    if not state or state != request.args.get('state'):
        return jsonify({'error': 'Invalid state'}), 400

    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Authorization code not found'}), 400

    code_verifier = session.get('code_verifier')
    if not code_verifier:
        return jsonify({'error': 'Missing code verifier in session'}), 400

    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": current_app.config["GOOGLE_CLIENT_ID"],
                    "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [current_app.config["GOOGLE_REDIRECT_URI"]]
                }
            },
            scopes=["https://www.googleapis.com/auth/youtube.upload"],
            redirect_uri=current_app.config["GOOGLE_REDIRECT_URI"],
            state=state
        )

        flow.fetch_token(code=code, code_verifier=code_verifier)

        creds = flow.credentials

        session['youtube_creds'] = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        session['yt_auth'] = True

        session.pop('code_verifier', None)

        return redirect('/')
    except Exception as e:
        print(f"Ошибка авторизации YouTube: {e}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/tg', methods=['POST'])
def tg_auth():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    channel_name = data.get('channel_name', '').strip()
    if not channel_name:
        return jsonify({'error': 'Channel name is required'}), 400

    # Получаем chat_id из Telegram
    try:
        response = requests.get(f"https://api.telegram.org/bot{current_app.config['TG_BOT_TOKEN']}/getUpdates").json()
        chat_id = None
        for update in response.get('result', []):
            if 'channel_post' in update and update['channel_post'].get('text') == channel_name:
                chat_id = update['channel_post']['chat']['id']
                break
        if not chat_id:
            return jsonify({'error': 'Channel not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to connect to Telegram'}), 500

    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'Authentication required'}), 401

    try:
        payload = jwt.decode(token[7:], current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid or expired token'}), 401

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user.tg_chat_id = chat_id
        db.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Database error'}), 500
    finally:
        db.close()

@auth_bp.route('/auth/vk', methods=['POST'])
def vk_auth():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    group_id = data.get('group_id', '').strip()
    if not group_id:
        return jsonify({'error': 'group_id is required'}), 400

    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'Authentication required'}), 401

    try:
        payload = jwt.decode(token[7:], current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid or expired token'}), 401

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user.vk_group_id = group_id
        db.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Database error'}), 500
    finally:
        db.close()

@auth_bp.route('/auth/vk/callback', methods=['POST'])
def vk_callback():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    state = data.get('state')
    code = data.get('code')
    code_verifier = data.get('code_verifier')
    device_id = data.get('device_id')

    if not code or not code_verifier or not device_id:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        response = requests.post(
            'https://id.vk.ru/oauth2/auth',
            data={
                'grant_type': 'authorization_code',
                'code_verifier': code_verifier,
                'redirect_uri': current_app.config['VK_REDIRECT_URI'],
                'code': code,
                'client_id': current_app.config['VK_APP_ID'],
                'device_id': device_id,
                'state': state
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        ).json()

        session['vk_token'] = response['access_token']
        return jsonify({'success': True, 'message': 'Authorized'})
    except Exception as e:
        print(f"Ошибка в /auth/vk/callback: {e}")
        return jsonify({'error': 'Internal server error'}), 500

__all__ = ['auth_bp']
