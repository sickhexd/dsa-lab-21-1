import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import sqlite3
from aiogram.client.default import DefaultBotProperties  

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token="7897213396:AAHmjZijJzAIJNson9kGcsZ-zRRjahUqjy0", default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('currency_bot.db')
    cursor = conn.cursor()
    
    # Создание таблицы валют
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS currencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        currency_name VARCHAR(3) UNIQUE,
        rate NUMERIC
    )
    ''')
    
    # Создание таблицы администраторов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id VARCHAR(50) UNIQUE
    )
    ''')
    
    
    try:
        cursor.execute("INSERT INTO admins (chat_id) VALUES (?)", ("6267394848",))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()

init_db()

# Проверка на администратора
async def is_admin(chat_id: str) -> bool:
    conn = sqlite3.connect('currency_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE chat_id=?", (str(chat_id),))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Состояния пользователей
user_states = {}

# Клавиатура для администраторов
def get_admin_keyboard():
    buttons = [
        [KeyboardButton(text="/manage_currency")],
        [KeyboardButton(text="/get_currencies")],
        [KeyboardButton(text="/convert")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

# Клавиатура для обычных пользователей
def get_user_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/get_currencies")],
            [KeyboardButton(text="/convert")]
        ],
        resize_keyboard=True
    )

# Клавиатура для управления валютами
def get_currency_management_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить валюту")],
            [KeyboardButton(text="Удалить валюту")],
            [KeyboardButton(text="Изменить курс валюты")],
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    if await is_admin(message.chat.id):
        await message.answer("Добро пожаловать, администратор!", reply_markup=get_admin_keyboard())
    else:
        await message.answer("Добро пожаловать в бота для работы с валютами!", reply_markup=get_user_keyboard())

@dp.message(Command("manage_currency"))
async def manage_currency(message: types.Message):
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде", reply_markup=get_user_keyboard())
        return
    
    await message.answer("Выберите действие:", reply_markup=get_currency_management_keyboard())

@dp.message(lambda message: message.text in ["Добавить валюту", "Удалить валюту", "Изменить курс валюты"])
async def currency_management_handler(message: types.Message):
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа", reply_markup=get_user_keyboard())
        return
    
    action = message.text
    user_states[message.from_user.id] = {"action": action}
    
    if action == "Добавить валюту":
        await message.answer("Введите название валюты (3 символа, например USD):", reply_markup=ReplyKeyboardRemove())
        user_states[message.from_user.id]["step"] = "enter_currency_name"
    elif action == "Удалить валюту":
        await message.answer("Введите название валюты для удаления:", reply_markup=ReplyKeyboardRemove())
        user_states[message.from_user.id]["step"] = "enter_currency_name"
    elif action == "Изменить курс валюты":
        await message.answer("Введите название валюты для изменения курса:", reply_markup=ReplyKeyboardRemove())
        user_states[message.from_user.id]["step"] = "enter_currency_name"

@dp.message(lambda message: message.from_user.id in user_states and 
                          user_states[message.from_user.id].get("step") == "enter_currency_name")
async def process_currency_name(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]
    currency_name = message.text.upper().strip()
    
    if len(currency_name) != 3 or not currency_name.isalpha():
        await message.answer("Название валюты должно состоять из 3 букв. Попробуйте еще раз:")
        return
    
    conn = sqlite3.connect('currency_bot.db')
    cursor = conn.cursor()
    
    if state["action"] == "Добавить валюту":
        cursor.execute("SELECT * FROM currencies WHERE currency_name=?", (currency_name,))
        if cursor.fetchone():
            await message.answer("Данная валюта уже существует", reply_markup=get_admin_keyboard())
            user_states.pop(user_id)
            conn.close()
            return
        
        state["currency_name"] = currency_name
        state["step"] = "enter_currency_rate"
        await message.answer("Введите курс к рублю:")
        
    elif state["action"] == "Удалить валюту":
        cursor.execute("DELETE FROM currencies WHERE currency_name=?", (currency_name,))
        if cursor.rowcount > 0:
            await message.answer(f"Валюта {currency_name} успешно удалена", reply_markup=get_admin_keyboard())
        else:
            await message.answer(f"Валюта {currency_name} не найдена", reply_markup=get_admin_keyboard())
        user_states.pop(user_id)
        conn.commit()
        
    elif state["action"] == "Изменить курс валюты":
        cursor.execute("SELECT * FROM currencies WHERE currency_name=?", (currency_name,))
        if not cursor.fetchone():
            await message.answer(f"Валюта {currency_name} не найдена", reply_markup=get_admin_keyboard())
            user_states.pop(user_id)
            conn.close()
            return
        
        state["currency_name"] = currency_name
        state["step"] = "enter_currency_rate"
        await message.answer("Введите новый курс к рублю:")
    
    conn.close()

@dp.message(lambda message: message.from_user.id in user_states and 
                          user_states[message.from_user.id].get("step") == "enter_currency_rate")
async def process_currency_rate(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]
    
    try:
        rate = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение для курса:")
        return
    
    conn = sqlite3.connect('currency_bot.db')
    cursor = conn.cursor()
    
    if state["action"] == "Добавить валюту":
        cursor.execute("INSERT INTO currencies (currency_name, rate) VALUES (?, ?)", 
                      (state["currency_name"], rate))
        await message.answer(f"Валюта: {state['currency_name']} успешно добавлена с курсом {rate}", 
                           reply_markup=get_admin_keyboard())
    elif state["action"] == "Изменить курс валюты":
        cursor.execute("UPDATE currencies SET rate=? WHERE currency_name=?", 
                      (rate, state["currency_name"]))
        await message.answer(f"Курс валюты {state['currency_name']} успешно изменен на {rate}", 
                           reply_markup=get_admin_keyboard())
    
    conn.commit()
    conn.close()
    user_states.pop(user_id)

@dp.message(Command("get_currencies"))
async def get_currencies(message: types.Message):
    conn = sqlite3.connect('currency_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT currency_name, rate FROM currencies")
    currencies = cursor.fetchall()
    conn.close()
    
    if not currencies:
        await message.answer("Нет сохраненных валют")
        return
    
    response = "Сохраненные валюты:\n" + "\n".join([f"{curr[0]} - {curr[1]} RUB" for curr in currencies])
    await message.answer(response)

@dp.message(Command("convert"))
async def convert(message: types.Message):
    user_states[message.from_user.id] = {"step": "enter_currency_for_conversion"}
    await message.answer("Введите название валюты:")

@dp.message(lambda message: message.from_user.id in user_states and 
                          user_states[message.from_user.id].get("step") == "enter_currency_for_conversion")
async def process_currency_for_conversion(message: types.Message):
    currency_name = message.text.upper().strip()
    
    conn = sqlite3.connect('currency_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT rate FROM currencies WHERE currency_name=?", (currency_name,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        await message.answer(f"Валюта {currency_name} не найдена")
        user_states.pop(message.from_user.id)
        return
    
    user_states[message.from_user.id] = {
        "step": "enter_amount_for_conversion",
        "currency_name": currency_name,
        "rate": result[0]
    }
    await message.answer("Введите сумму для конвертации:")

@dp.message(lambda message: message.from_user.id in user_states and 
                          user_states[message.from_user.id].get("step") == "enter_amount_for_conversion")
async def process_amount_for_conversion(message: types.Message):
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение для суммы:")
        return
    
    state = user_states[message.from_user.id]
    converted = amount * state["rate"]
    
    await message.answer(
        f"{amount} {state['currency_name']} = {converted:.2f} RUB\n"
        f"Курс: 1 {state['currency_name']} = {state['rate']} RUB"
    )
    user_states.pop(message.from_user.id)

@dp.message(lambda message: message.text == "Отмена")
async def cancel_handler(message: types.Message):
    if message.from_user.id in user_states:
        user_states.pop(message.from_user.id)
    
    if await is_admin(message.chat.id):
        await message.answer("Действие отменено", reply_markup=get_admin_keyboard())
    else:
        await message.answer("Действие отменено", reply_markup=get_user_keyboard())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())