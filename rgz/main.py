import sqlite3
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
import asyncio
import aiohttp
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка базы данных
def setup_db():
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER UNIQUE,
        name TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        sum REAL,
        chat_id INTEGER,
        type_operation TEXT,
        FOREIGN KEY (chat_id) REFERENCES users (chat_id)
    )
    ''')
    
    conn.commit()
    conn.close()

setup_db()


API_TOKEN = '7897213396:AAHmjZijJzAIJNson9kGcsZ-zRRjahUqjy0'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class RegistrationStates(StatesGroup):
    waiting_for_name = State()

class AddOperationStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_amount = State()
    waiting_for_date = State()

class OperationsStates(StatesGroup):
    waiting_for_currency = State()


def get_main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/reg"), KeyboardButton(text="/add_operation")],
            [KeyboardButton(text="/operations"), KeyboardButton(text="/delaccount")],
            [KeyboardButton(text="/help")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def get_cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True
    )

def get_data_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Сегодня")],
                  [KeyboardButton(text='Отмена')]],
        resize_keyboard=True
    )

def get_operation_types_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="РАСХОД"), KeyboardButton(text="ДОХОД")],
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True
    )

def get_currencies_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="RUB"), KeyboardButton(text="USD"), KeyboardButton(text="EUR")],
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True
    )

def is_user_registered(chat_id):
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

@dp.message(lambda message: message.text == "Отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных действий для отмены.", reply_markup=get_main_menu_kb())
        return
    
    await state.clear()
    await message.answer(
        "Действие отменено.",
        reply_markup=get_main_menu_kb()
    )


@dp.message(Command("start", "help"))
async def cmd_start(message: types.Message):
    help_text = """
    <b>Финансовый бот</b>

    Доступные команды:
    /reg - Регистрация
    /add_operation - Добавить операцию
    /operations - Просмотр операций
    /delaccount - Удалить аккаунт

    Выберите действие:
    """
    await message.answer(help_text, reply_markup=get_main_menu_kb(), parse_mode="HTML")

@dp.message(Command("reg"))
async def cmd_reg(message: types.Message, state: FSMContext):
    if is_user_registered(message.chat.id):
        await message.answer("Вы уже зарегистрированы!", reply_markup=get_main_menu_kb())
        return
    
    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer("Введите ваше имя:", reply_markup=get_cancel_kb())

@dp.message(RegistrationStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await cmd_cancel(message, state)
        return
    
    name = message.text
    chat_id = message.chat.id
    
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (chat_id, name) VALUES (?, ?)', (chat_id, name))
    conn.commit()
    conn.close()
    
    await state.clear()
    await message.answer(f"Регистрация завершена, {name}!", reply_markup=get_main_menu_kb())

@dp.message(Command("add_operation"))
async def cmd_add_operation(message: types.Message, state: FSMContext):
    if not is_user_registered(message.chat.id):
        await message.answer("Сначала зарегистрируйтесь с помощью /reg", reply_markup=get_main_menu_kb())
        return
    
    await state.set_state(AddOperationStates.waiting_for_type)
    await message.answer("Выберите тип операции:", reply_markup=get_operation_types_kb())

@dp.message(AddOperationStates.waiting_for_type)
async def process_operation_type(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await cmd_cancel(message, state)
        return
    
    operation_type = message.text
    if operation_type not in ["РАСХОД", "ДОХОД"]:
        await message.answer("Пожалуйста, выберите тип операции с помощью кнопок.")
        return
    
    await state.update_data(type_operation=operation_type)
    await state.set_state(AddOperationStates.waiting_for_amount)
    await message.answer("Введите сумму операции в рублях:", reply_markup=get_cancel_kb())

@dp.message(AddOperationStates.waiting_for_amount)
async def process_operation_amount(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await cmd_cancel(message, state)
        return
    
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму (положительное число).")
        return
    
    await state.update_data(sum=amount)
    await state.set_state(AddOperationStates.waiting_for_date)
    await message.answer(
        "Введите дату операции в формате ДД.ММ.ГГГГ (или 'сегодня' для текущей даты):",
        reply_markup=get_data_kb()
    )

@dp.message(AddOperationStates.waiting_for_date)
async def process_operation_date(message: types.Message, state: FSMContext):
    if message.text == " Отмена":
        await cmd_cancel(message, state)
        return
    
    date_str = message.text
    if date_str.lower() == 'сегодня':
        operation_date = datetime.date.today().strftime("%d.%m.%Y")
    else:
        try:
            datetime.datetime.strptime(date_str, "%d.%m.%Y")
            operation_date = date_str
        except ValueError:
            await message.answer("Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ или 'сегодня'.")
            return
    
    data = await state.get_data()
    chat_id = message.chat.id
    
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (?, ?, ?, ?)',
        (operation_date, data['sum'], chat_id, data['type_operation'])
    )
    conn.commit()
    conn.close()
    
    await state.clear()
    await message.answer(
        f"Операция добавлена!\nТип: {data['type_operation']}\nСумма: {data['sum']} RUB\nДата: {operation_date}",
        reply_markup=get_main_menu_kb()
    )

async def get_exchange_rate(currency):
    async with aiohttp.ClientSession() as session:
        try:
            # Запрос к вашему серверу
            async with session.get('http://localhost:5000/rate', params={'currency': currency}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['rate']
                else:
                    logger.error(f"Ошибка сервера: {response.status}")
                    return 1
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка соединения с сервером: {e}")
            return 1
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return 1

@dp.message(Command("operations"))
async def cmd_operations(message: types.Message, state: FSMContext):
    if not is_user_registered(message.chat.id):
        await message.answer("Сначала зарегистрируйтесь с помощью /reg", reply_markup=get_main_menu_kb())
        return
    
    await state.set_state(OperationsStates.waiting_for_currency)
    await message.answer("Выберите валюту для отображения операций:", reply_markup=get_currencies_kb())

@dp.message(OperationsStates.waiting_for_currency)
async def process_operations_currency(message: types.Message, state: FSMContext):
    if message.text == " Отмена":
        await cmd_cancel(message, state)
        return
    
    currency = message.text
    if currency not in ["RUB", "USD", "EUR"]:
        await message.answer("Пожалуйста, выберите валюту с помощью кнопок.")
        return
    
    chat_id = message.chat.id
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT date, sum, type_operation FROM operations WHERE chat_id = ? ORDER BY date DESC', (chat_id,))
    operations = cursor.fetchall()
    conn.close()
    
    if not operations:
        await message.answer("У вас пока нет операций.", reply_markup=get_main_menu_kb())
        await state.clear()
        return
    
    rate = 1
    if currency != "RUB":
        rate = await get_exchange_rate(currency)
    
    response = f"Ваши операции в {currency}:\n\n"
    total = 0
    
    for op in operations:
        date, amount, op_type = op
        converted_amount = round(amount / rate, 2)
        response += f"{date} - {op_type}: {converted_amount} {currency}\n"
        
        if op_type == "ДОХОД":
            total += converted_amount
        else:
            total -= converted_amount
    
    response += f"\nИтоговый баланс: {round(total, 2)} {currency}"
    
    await message.answer(response, reply_markup=get_main_menu_kb())
    await state.clear()

@dp.message(Command("delaccount"))
async def cmd_delaccount(message: types.Message):
    if not is_user_registered(message.chat.id):
        await message.answer("Вы не зарегистрированы.", reply_markup=get_main_menu_kb())
        return
    
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM operations WHERE chat_id = ?', (message.chat.id,))
    cursor.execute('DELETE FROM users WHERE chat_id = ?', (message.chat.id,))
    
    conn.commit()
    conn.close()
    
    await message.answer("Ваш аккаунт и все связанные данные были удалены.", reply_markup=get_main_menu_kb())

# Запуск бота
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())