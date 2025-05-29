import asyncio
import os
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties

# --- Настройка бота ---
API_TOKEN = "7897213396:AAHmjZijJzAIJNson9kGcsZ-zRRjahUqjy0"
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Клавиатуры ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/get_currencies"),
               KeyboardButton(text="/convert"),
               KeyboardButton(text="/manage_currency")]],
    resize_keyboard=True
)

manage_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Добавить валюту"),
               KeyboardButton(text="Удалить валюту"),
               KeyboardButton(text="Изменить курс валюты")]],
    resize_keyboard=True
)

# --- Состояния пользователя и список админов ---
user_states = {}
admins = ["626739484"]

# --- Работа с SQLite ---
DB_PATH = "currencies.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            currency_name TEXT PRIMARY KEY,
            rate REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_all_currencies():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT currency_name, rate FROM currencies")
    result = cursor.fetchall()
    conn.close()
    return result

def add_currency(name, rate):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO currencies (currency_name, rate) VALUES (?, ?)", (name, rate))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_currency(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM currencies WHERE currency_name = ?", (name,))
    rows_deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_deleted > 0

def update_currency(name, rate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE currencies SET rate = ? WHERE currency_name = ?", (rate, name))
    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_updated > 0

def convert_currency(name, amount):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rate FROM currencies WHERE currency_name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return amount * row[0]
    return None

# --- Команды ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_kb)

@dp.message(Command("manage_currency"))
async def cmd_manage_currency(message: Message):
    if str(message.from_user.id) not in admins:
        await message.answer("У вас нет доступа к этой функции.")
        return
    await message.answer("Выберите действие:", reply_markup=manage_kb)

@dp.message(Command("get_currencies"))
async def cmd_get_currencies(message: Message):
    data = get_all_currencies()
    if not data:
        await message.answer("Список валют пуст.")
    else:
        text = "<b>Список валют:</b>\n"
        for currency, rate in data:
            text += f"🔹 {currency}: {rate:.3f} RUB\n"
        await message.answer(text)

@dp.message(Command("convert"))
async def cmd_convert(message: Message):
    await message.answer("Введите название валюты:")
    user_states[message.from_user.id] = "waiting_for_currency_to_convert"

# --- Обработка пользовательского ввода ---
@dp.message()
async def handle_all(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "Добавить валюту":
        if str(user_id) not in admins:
            await message.answer("Нет доступа.")
            return
        await message.answer("Введите название валюты:")
        user_states[user_id] = "waiting_for_currency_name"
        return

    elif user_states.get(user_id) == "waiting_for_currency_name":
        user_states[user_id] = {"action": "add", "currency": text.upper()}
        await message.answer("Введите курс:")
        return

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("action") == "add":
        try:
            rate = float(text.replace(",", "."))
            currency = user_states[user_id]["currency"]
            if add_currency(currency, rate):
                await message.answer(f"Валюта {currency} добавлена.", reply_markup=main_kb)
            else:
                await message.answer("Валюта уже существует.", reply_markup=main_kb)
        except ValueError:
            await message.answer("Введите корректное число.")
        finally:
            user_states.pop(user_id)
        return

    elif text == "Удалить валюту":
        if str(user_id) not in admins:
            await message.answer("Нет доступа.")
            return
        await message.answer("Введите название валюты:")
        user_states[user_id] = "waiting_for_currency_to_delete"
        return

    elif user_states.get(user_id) == "waiting_for_currency_to_delete":
        currency = text.upper()
        if delete_currency(currency):
            await message.answer(f"Валюта {currency} удалена.", reply_markup=main_kb)
        else:
            await message.answer("Валюта не найдена.", reply_markup=main_kb)
        user_states.pop(user_id)
        return

    elif text == "Изменить курс валюты":
        if str(user_id) not in admins:
            await message.answer("Нет доступа.")
            return
        await message.answer("Введите название валюты:")
        user_states[user_id] = "waiting_for_currency_to_edit"
        return

    elif user_states.get(user_id) == "waiting_for_currency_to_edit":
        user_states[user_id] = {"action": "edit", "currency": text.upper()}
        await message.answer("Введите новый курс:")
        return

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("action") == "edit":
        try:
            rate = float(text.replace(",", "."))
            currency = user_states[user_id]["currency"]
            if update_currency(currency, rate):
                await message.answer(f"Курс обновлён для {currency}.", reply_markup=main_kb)
            else:
                await message.answer("Валюта не найдена.", reply_markup=main_kb)
        except ValueError:
            await message.answer("Введите корректное число.")
        finally:
            user_states.pop(user_id)
        return

    elif user_states.get(user_id) == "waiting_for_currency_to_convert":
        user_states[user_id] = {"action": "convert", "currency": text.upper()}
        await message.answer("Введите сумму:")
        return

    elif isinstance(user_states.get(user_id), dict) and user_states[user_id].get("action") == "convert":
        try:
            amount = float(text.replace(",", "."))
            currency = user_states[user_id]["currency"]
            result = convert_currency(currency, amount)
            if result is not None:
                await message.answer(f"{amount:.2f} {currency} = {result:.2f} RUB", reply_markup=main_kb)
            else:
                await message.answer("Валюта не найдена.", reply_markup=main_kb)
        except ValueError:
            await message.answer("Введите корректное число.")
        finally:
            user_states.pop(user_id)
        return

    else:
        await message.answer("Я вас не понял. Выберите команду из меню.", reply_markup=main_kb)

# --- Запуск ---
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
