import requests, random

base_url = "http://127.0.0.1:5000/number/"  # Базовый адрес API сервера

# 1. GET запрос
param = random.randint(1, 10)  # Генерируем случайное число от 1 до 10
get_response = requests.get(base_url, params={"param": param}).json()  # Отправляем GET-запрос с параметром и получаем JSON-ответ
get_result = get_response["result"]  # Извлекаем результат из ответа
get_op = "умножение"  # В GET запросе операция всегда "умножение"
print("GET:", get_result, get_op)  # Выводим результат GET-запроса

# 2. POST запрос
json_param = random.randint(1, 10)  # Случайное число для JSON-параметра
post_response = requests.post(base_url, json={"jsonParam": json_param}).json()  # POST-запрос с JSON-данными
post_result = post_response["result"]  # Извлекаем результат
post_op = post_response["operation"]  # Извлекаем операцию, выбранную сервером
print("POST:", post_result, post_op)  # Выводим результат POST-запроса

# 3. DELETE запрос
delete_response = requests.delete(base_url).json()  # Отправляем DELETE-запрос и получаем ответ
delete_result = delete_response["result"]  # Извлекаем результат
delete_op = delete_response["operation"]  # Извлекаем операцию
print("DELETE:", delete_result, delete_op)  # Выводим результат DELETE-запроса

# 4. Последовательное выполнение операций
def apply(a, b, op):  # Функция для выполнения математической операции по строке
    if op == "сумма":
        return a + b
    elif op == "разность":
        return a - b
    elif op == "умножение":
        return a * b
    elif op == "деление":
        return a / b

step1 = apply(get_result, post_result, get_op)  # Применяем первую операцию: GET с POST
final_result = apply(step1, delete_result, post_op)  # Применяем вторую операцию: результат с DELETE

print("Итоговое значение:", int(final_result))  # Выводим финальный результат, приведённый к целому числу