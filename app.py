from flask import Flask, render_template, request, jsonify
import controller


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/process', methods=['POST'])
def process_form():
    try:
        print("Получен запрос на /process")
        
        # Получаем данные из формы
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '')
        platforms = request.form.getlist('platforms')
        timestamp = request.form.get('timestamp', '')
        
        print(f"Данные от клиента: title={title}, category={category}, platforms={platforms}")
        
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
        result = process_video_data(title, description, category, platforms)
        
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