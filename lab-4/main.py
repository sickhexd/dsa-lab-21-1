import asyncio
import logging  
from aiogram import Bot, Dispatcher 
from aiogram.enums import ParseMode 
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import Command 
from aiogram.client.default import DefaultBotProperties  

API_TOKEN = "7897213396:AAHmjZijJzAIJNson9kGcsZ-zRRjahUqjy0"  
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()  

currency_data = {} 
user_states = {}
menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/save_currency")],
        [KeyboardButton(text="/show_currencies")],
        [KeyboardButton(text="/convert")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))  
async def start(message: Message):
    await message.answer("Выберите действие из меню ниже:", reply_markup=menu_kb)

@dp.message(Command("save_currency"))  
async def save_currency(message: Message):
    await message.answer("Введите название валюты:") 
    user_states[message.from_user.id] = {"state": "waiting_for_currency_name"}

@dp.message(Command("show_currencies"))  
async def show_currencies(message: Message):  
    if not currency_data:  
        await message.answer("Пока что нет сохранённых валют.")  
    else:
        text = "<b>Сохранённые курсы валют:</b>\n" + "\n".join(f"{currency} = {rate} RUB" for currency, rate in currency_data.items())
        await message.answer(text)  

@dp.message(Command("convert"))  
async def convert(message: Message):  
    await message.answer("Введите название валюты, которую хотите конвертировать в рубли:")  
    user_states[message.from_user.id] = {"state": "waiting_for_convert_currency"}

@dp.message()  
async def handle_message(message: Message):
    user_id = message.from_user.id 
    if user_id not in user_states:
        return
    
    state_data = user_states[user_id]
    state = state_data.get("state")

    if state == "waiting_for_currency_name":  
        state_data["currency"] = message.text.upper().strip()
        state_data["state"] = "waiting_for_currency_rate"
        await message.answer("Введите курс к рублю:")  
    elif state == "waiting_for_currency_rate":  
        try:
            rate = float(message.text.strip().replace(',', '.'))  
            currency = state_data["currency"]
            currency_data[currency] = rate  
            await message.answer(f"Сохранено: {currency} = {rate} RUB")  
            user_states.pop(user_id)  
        except ValueError:  
            await message.answer("Введите числовое значение для курса.")  
    elif state == "waiting_for_convert_currency":  
        currency = message.text.upper().strip() 
        if currency not in currency_data:  
            await message.answer(f"Валюта {currency} не найдена. Сначала добавьте её через /save_currency.") 
        else:
            state_data["currency"] = currency
            state_data["state"] = "waiting_for_convert_amount"
            await message.answer(f"Введите сумму в {currency}, которую хотите перевести в рубли:")
    elif state == "waiting_for_convert_amount":
        try:
            amount = float(message.text.strip().replace(',', '.'))  
            currency = state_data["currency"]
            result = round(amount * currency_data[currency], 2)  
            await message.answer(f"{amount} {currency} = {result} RUB")  
            user_states.pop(user_id)  
        except ValueError:  
            await message.answer("Введите числовое значение для суммы.")  

async def main():  
    await dp.start_polling(bot)  

if __name__ == "__main__":  
    asyncio.run(main())