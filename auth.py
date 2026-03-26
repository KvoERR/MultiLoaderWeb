from flask import Blueprint, request, jsonify, session, redirect
from google_auth_oauthlib.flow import Flow
import jwt
import os
import requests
from models import User, SessionLocal

auth_bp = Blueprint('auth', __name__)
bot_token = os.getenv('TG_BOT_TOKEN')
app_id = os.getenv('VK_APP_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
YOUTUBE_URI = os.getenv('GOOGLE_REDIRECT_URI')
VK_URI = os.getenv('VK_REDIRECT_URI')

@auth_bp.route('/auth/youtube/login')
def youtube_login():
    flow = Flow.from_client_secrets_file(
        'secrets/client_secret_web.json',
        scopes=['https://www.googleapis.com/auth/youtube.upload'],
        redirect_uri=YOUTUBE_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
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

    try:
        flow = Flow.from_client_secrets_file(
            'secrets/client_secret_web.json',
            scopes=['https://www.googleapis.com/auth/youtube.upload'],
            redirect_uri=YOUTUBE_URI,
            state=state
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        session['youtube_creds'] = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        session['yt_auth']=True
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
        response = requests.get(f'https://api.telegram.org/bot{bot_token}/getUpdates').json()
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
        payload = jwt.decode(token[7:], SECRET_KEY, algorithms=['HS256'])
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
        payload = jwt.decode(token[7:], SECRET_KEY, algorithms=['HS256'])
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
                'redirect_uri': VK_URI,
                'code': code,
                'client_id': app_id,
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
