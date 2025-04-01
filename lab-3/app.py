from flask import Flask, request, jsonify  # Импортируем Flask и инструменты для работы с запросами и JSON
import random  # Модуль для генерации случайных чисел

app = Flask(__name__)  # Создаём экземпляр Flask-приложения

# Список возможных операций
operations = ['сумма', 'разность', 'умножение', 'деление']

# Функция, выполняющая нужную операцию
def operation(a, b, op):
    if op == 'сумма':
        return a + b
    elif op == 'разность':
        return a - b
    elif op == 'умножение':
        return a * b
    elif op == 'деление':
        return a / b

# Обработка GET-запроса: принимает параметр, возвращает результат умножения
@app.route('/number/', methods=['GET'])
def get_number():
    param = float(request.args.get('param'))  # Получаем параметр из строки запроса
    rand = random.randint(1, 10)  # Генерируем случайное число
    return jsonify({
        'result': rand * param,  # Умножаем и возвращаем
        'random_number': rand,
        'param': param,
    })

# Обработка POST-запроса: принимает JSON, выбирает случайную операцию
@app.route('/number/', methods=['POST'])
def post_number():
    param = float(request.get_json()['jsonParam'])  # Получаем число из JSON
    rand = random.randint(1, 10)  # Случайное число
    op = random.choice(operations)  # Случайная операция
    return jsonify({
        'result': operation(rand, param, op),  # Результат применения операции
        'jsonParam': param,
        'random_number': rand,
        'operation': op
    })

# Обработка DELETE-запроса: генерирует два числа и случайную операцию
@app.route('/number/', methods=['DELETE'])
def delete_number():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    op = random.choice(operations)
    return jsonify({
        'result': operation(a, b, op),  # Возвращаем результат
        'operation': op
    })
