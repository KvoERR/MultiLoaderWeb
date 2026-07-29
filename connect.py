from flask import request, jsonify, session, redirect, current_app, Blueprint
import requests
import jwt
from models import User, SessionLocal

connect_bp = Blueprint('connect', __name__)

@connect_bp.route('/connect/vk', methods=['POST'])
def vk_connect():
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

@connect_bp.route('/connect/tg', methods=['POST'])
def tg_connect():
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