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

@app.route('/process', methods=['POST'])
def process_form():
    try:
        print("Получен запрос на /process")
        
        # Получаем данные из формы
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        video = request.files['video']
        image = request.files['image']
        tags = request.form.get('tags', '').strip()
        privacy = request.form.get('privacy', '')
        platforms = request.form.getlist('platforms')
        
        
        print(f"Данные от клиента: title={title}, category={category}, video={video}, image={image}, tags={tags}, privacy={privacy}, platforms={platforms}")
        
        # Валидация данных
        if not title:
            return jsonify({
                'success': False,
                'error': 'Название не может быть пустым'
            })
        
        if not platforms:
            return jsonify({
                'success': False,
                'error': 'Выберите хотя бы одну платформу'
            })
        
        # Обрабатываем данные (ваша бизнес-логика)
        result = YouTube.VideoUploader.upload_video(
            self=YouTube.VideoUploader,
            title=title,
            description=description,
            video=video,
            image=image,
            tags=tags,
            privacy=privacy,
            category=category
        )
        
        print("Данные успешно обработаны, отправляем ответ")
        
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