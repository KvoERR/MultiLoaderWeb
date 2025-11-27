import tempfile
from flask import Flask, render_template, request, jsonify
from utils import VK, YouTube



app = Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html')


'''@app.route('/autotag', methods=['GET'])
def   tags_generation():
    try:
        print("Получен запрос на /autotag")
'''

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

        ''' Тест POST запроса
        print(f"Данные от клиента: title={title}, category={category}, video={video_file}, image={image_file}, tags={tags}, privacy={privacy}, platforms={platforms}")
        '''
        
        
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
        # Обрабатываем данные (ваша бизнес-логика)
        result = YouTube.VideoUploader.upload_video(
            title=title,
            description=description,
            video=video_path,
            image=image_path,
            tags=tags,
            privacy=privacy,
            category=category
        ) 
        return jsonify({
            'success': True,
            'result': result,
            'message': 'Данные успешно получены и обработаны'
        }) 
    except Exception as e:
        print(f"Ошибка при обработке формы: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True)