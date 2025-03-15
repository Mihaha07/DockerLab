from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import requests

API_TOKEN = '5151344733:AAGxw8dY91WaZQJk6puo6fgorrARiU3xh0o'
OPENROUTER_API_KEY = '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'
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

user_contexts = {}
# обработка команды старт
@dp.message(Command("start"))
async def command_start(message: Message):
    user_id = message.from_user.id
    user_contexts[user_id] = []
    await message.answer("Привет! Напиши что-нибудь!")
# обработка команды хелп
@dp.message(Command("help"))
async def command_help(message: Message):
    await message.answer("Просто напиши мне любое сообщение и с помощью искусственного интелекта я тебе на него отвечу, может даже получится выстроить диалог.")
# обработка запросов
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_message = message.text
    #ввод в контекст
    if user_id not in user_contexts:
        user_contexts[user_id] = []
    user_contexts[user_id].append({"role": "user", "content": user_message})
    #промежуточный ответ
    await message.answer("Ответ формируется. Придется немного подождать...")
    llm_response = await send_to_llm(user_contexts[user_id])
    user_contexts[user_id].append({"role": "assistant", "content": llm_response})
    #добавление ссылки на страницу AI
    await message.answer(
        llm_response,
        parse_mode=ParseMode.HTML,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Powered by Gimini",
                        url="https://openrouter.ai/google/gemini-2.0-pro-exp-02-05:free/api"
                    )
                ]
            ]
        )
    )
# Формирование запроса
async def send_to_llm(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "@stillbot1_bot",
        "X-Title": "Telegram Bot"
    }

    data = {
        "model": "google/gemini-2.0-pro-exp-02-05:free",
        "messages": messages
    }
#Отработка ошибок
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return "Произошла ошибка при обработке ответа. Отправьте запрос еще раз."
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"
#запуск бота
if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=True)
