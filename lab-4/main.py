import asyncio
import logging  
from aiogram import Bot, Dispatcher 
from aiogram.enums import ParseMode 
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import Command 
from aiogram.client.default import DefaultBotProperties  

# Токен
API_TOKEN = "7897213396:AAHmjZijJzAIJNson9kGcsZ-zRRjahUqjy0"  # Устанавливает токен для бота, необходим для авторизации

#логирование
logging.basicConfig(level=logging.INFO)


bot = Bot(  # Создаёт объект бота с заданным токеном
    token=API_TOKEN,  # Используем токен API для авторизации бота
    default=DefaultBotProperties(parse_mode=ParseMode.HTML) 
)
dp = Dispatcher()  # диспетчер для управления обработкой сообщений

# Словарь для хранения валют
currency_data = {} 

# Состояния пользователя
user_states = {}

# Меню-клавиатура
menu_kb = ReplyKeyboardMarkup( 
    keyboard=[  # Описание клавиш
        [KeyboardButton(text="/save_currency")],  # Кнопка для сохранения валюты
        [KeyboardButton(text="/show_currencies")],  # Кнопка для показа сохранённых валют
        [KeyboardButton(text="/convert")]  # Кнопка для конвертации валют
    ],
    resize_keyboard=True
)

# Команда /start
@dp.message(Command("start"))  # Обработчик команды /start
async def start(message: Message):
    await message.answer(
        "Привет! Я бот для сохранения курсов валют.\nВыберите действие из меню ниже:",
        reply_markup=menu_kb
    )

# Команда /save_currency
@dp.message(Command("save_currency"))  
async def save_currency(message: Message):
    await message.answer("Введите название валюты (например, USD):") 
    user_states[message.from_user.id] = "waiting_for_currency_name"  # Сохраняем состояние пользователя, чтобы понять, что он ожидает ввод валюты

# Команда /show_currencies
@dp.message(Command("show_currencies"))  
async def show_currencies(message: Message):  
    if not currency_data:  
        await message.answer("Пока что нет сохранённых валют.")  
    else:
        text = "<b>Сохранённые курсы валют:</b>\n"  
        for currency, rate in currency_data.items():  # Перебираем все валюты в словаре
            text += f"{currency} = {rate} RUB\n"  # Добавляем каждую валюту и её курс в сообщение
        await message.answer(text)  # Отправляем сообщение с курсами валют

# Команда /convert
@dp.message(Command("convert"))  
async def convert(message: Message):  
    await message.answer("Введите название валюты, которую хотите конвертировать в рубли (например, USD):")  
    user_states[message.from_user.id] = "waiting_for_convert_currency"

# Обработка сообщений (ввод названия валюты, курса, суммы)
@dp.message()  
async def handle_message(message: Message):
    user_id = message.from_user.id 

    # Сохранение курса валюты
    if user_states.get(user_id) == "waiting_for_currency_name":  # Если пользователь ожидает ввода валюты
        user_states[user_id] = {  # Обновляем состояние пользователя для следующего шага
            "step": "waiting_for_currency_value",  # Теперь пользователь должен ввести курс
            "currency": message.text.upper().strip()  # Сохраняем введённую валюту (преобразуем в верхний регистр)
        }
        await message.answer("Введите курс к рублю (например, 94.5):")  # Запрашиваем курс для этой валюты

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("step") == "waiting_for_currency_value":  # Если пользователь на шаге ввода курса
        try:
            user_input = message.text.strip().replace(',', '.')  # Очищаем введённый текст и заменяем запятую на точку
            rate = float(user_input)  # Преобразуем введённый курс в число с плавающей точкой

            currency = user_states[user_id]["currency"]  # Получаем валюту из состояния
            currency_data[currency] = rate  # Сохраняем курс валюты в словарь

            await message.answer(f"Сохранено: {currency} = {rate} RUB")  # Подтверждаем сохранение курса
            user_states.pop(user_id)  # Убираем пользователя из состояния

        except ValueError:  # Если ввод некорректен (например, не число)
            await message.answer("Пожалуйста, введите числовое значение для курса (например, 94.5 или 94,5).")  # Просим ввести корректное значение

    # Конвертация валюты
    elif user_states.get(user_id) == "waiting_for_convert_currency":  # Если пользователь ожидает ввода валюты для конвертации
        currency = message.text.upper().strip()  # Получаем валюту из ввода и приводим к верхнему регистру
        if currency not in currency_data:  # Если валюта не найдена в словаре
            await message.answer(f"Валюта {currency} не найдена. Сначала добавьте её через /save_currency.")  # Просим добавить валюту
        else:
            user_states[user_id] = {  # Обновляем состояние пользователя для ввода суммы
                "step": "waiting_for_convert_amount",
                "currency": currency
            }
            await message.answer(f"Введите сумму в {currency}, которую хотите перевести в рубли:")  # Запрашиваем сумму для конвертации

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("step") == "waiting_for_convert_amount":  # Если пользователь на шаге ввода суммы
        try:
            amount_str = message.text.strip().replace(',', '.')  # Очищаем ввод и заменяем запятую на точку
            amount = float(amount_str)  # Преобразуем сумму в число

            currency = user_states[user_id]["currency"]  # Получаем валюту из состояния
            rate = currency_data[currency]  # Получаем курс этой валюты из словаря
            result = round(amount * rate, 2)  # Рассчитываем результат конвертации и округляем до двух знаков

            await message.answer(f"{amount} {currency} = {result} RUB")  # Отправляем результат конвертации
            user_states.pop(user_id)  # Убираем пользователя из состояния

        except ValueError:  # Если ввод некорректен (например, не число)
            await message.answer("Пожалуйста, введите корректное число (например, 10.5 или 10,5).")  # Просим ввести корректное число

    else:
        await message.answer("Выберите команду из меню или введите /start")  # Если пользователь ввёл что-то не так, просим выбрать команду из меню

# Запуск бота
async def main():  # Асинхронная функция для запуска бота
    await dp.start_polling(bot)  # Запуск бота с поллингом (ожиданием новых сообщений)

if __name__ == "__main__":  # Если этот файл запускается как основной
    asyncio.run(main())  # Запускаем асинхронную функцию main
