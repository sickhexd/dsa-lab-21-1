from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/number/', methods=['GET'])
def get_number():
    # Получаем параметр из запроса
    param = request.args.get('param', type=float)
    
    if param is None:
        return jsonify({'error': 'Параметр "param" обязателен и должен быть числом'}), 400

    # Генерируем случайное число
    random_number = random.uniform(1, 100)
    result = random_number * param

    return jsonify({
        'random_number': random_number,
        'param': param,
        'result': result
    })

