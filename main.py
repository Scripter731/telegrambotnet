import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from sessions import load_sessions, initialize_sessions
from functions import FunctionManager
from config import BOT_TOKEN, load_config, API_ID, API_HASH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

user_data = {}

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Join", callback_data="join"),
        InlineKeyboardButton("Report", callback_data="report"),
        InlineKeyboardButton("Reaction Flood", callback_data="reaction_flood"),
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    sessions = await load_sessions()
    session_count = len(sessions) if sessions else 0

    await message.reply(
        f"Привет! Я бот для управления функциями.\n"
        f"Активных сессий: {session_count}\n"
        "Выберите команду:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query_handler(lambda query: query.data == "join")
async def start_join(query: types.CallbackQuery):
    await query.message.edit_text("Введите ссылку на чат/канал:")
    user_data[query.from_user.id] = {"command": "join", "step": "link"}

@dp.callback_query_handler(lambda query: query.data == "report")
async def start_report(query: types.CallbackQuery):
    await query.message.edit_text("Введите username или user_id пользователя, на которого хотите отправить жалобу:")
    user_data[query.from_user.id] = {"command": "report", "step": "username"}

@dp.callback_query_handler(lambda query: query.data == "reaction_flood")
async def start_reaction_flood(query: types.CallbackQuery):
    await query.message.edit_text("Введите ссылку на сообщение (например, https://t.me/chat/123):")
    user_data[query.from_user.id] = {"command": "reaction_flood", "step": "link"}

@dp.message_handler(lambda message: user_data.get(message.from_user.id, {}).get("step") == "link")
async def get_link(message: types.Message):
    user_data[message.from_user.id]["link"] = message.text
    user_data[message.from_user.id]["step"] = "mode"

    await message.reply(
        "Выберите режим:\n"
        "1. Просто вступить в чат/канал\n"
        "2. Вступить в связанный чат"
    )

@dp.message_handler(lambda message: user_data.get(message.from_user.id, {}).get("step") == "mode")
async def get_mode(message: types.Message):
    user_data[message.from_user.id]["mode"] = message.text
    user_data[message.from_user.id]["step"] = "speed"

    await message.reply(
        "Выберите скорость:\n"
        "normal - с задержкой\n"
        "fast - без задержки"
    )

@dp.message_handler(lambda message: user_data.get(message.from_user.id, {}).get("step") == "speed")
async def get_speed(message: types.Message):
    user_data[message.from_user.id]["speed"] = message.text
    user_data[message.from_user.id]["step"] = None

    sessions = await load_sessions()
    config = load_config()
    proxies = config.get("proxies", [])

    await initialize_sessions(sessions, proxies)

    manager = FunctionManager(sessions, API_ID, API_HASH)

    await manager.execute(
        command=user_data[message.from_user.id]["command"],
        link=user_data[message.from_user.id]["link"],
        mode=user_data[message.from_user.id]["mode"],
        speed=user_data[message.from_user.id]["speed"]
    )

    await message.reply("Вступление завершено!")

@dp.message_handler(lambda message: user_data.get(message.from_user.id, {}).get("step") == "username")
async def get_username(message: types.Message):
    user_data[message.from_user.id]["username"] = message.text
    user_data[message.from_user.id]["step"] = "reason"

    reasons = [
        "1. Child abuse",
        "2. Copyright",
        "3. Fake",
        "4. Pornography",
        "5. Spam",
        "6. Violence",
        "7. Other"
    ]
    await message.reply("Выберите причину жалобы:\n" + "\n".join(reasons))

@dp.message_handler(lambda message: user_data.get(message.from_user.id, {}).get("step") == "reason")
async def get_reason(message: types.Message):
    try:
        choice = int(message.text)
        if choice < 1 or choice > 7:
            raise ValueError
    except ValueError:
        await message.reply("Неверный выбор. Введите число от 1 до 7.")
        return

    user_data[message.from_user.id]["reason_choice"] = choice
    user_data[message.from_user.id]["step"] = "comment"

    await message.reply("Введите комментарий к жалобе:")

@dp.message_handler(lambda message: user_data.get(message.from_user.id, {}).get("step") == "comment")
async def get_comment(message: types.Message):
    user_data[message.from_user.id]["comment"] = message.text
    user_data[message.from_user.id]["step"] = None

    sessions = await load_sessions()
    config = load_config()
    proxies = config.get("proxies", [])

    await initialize_sessions(sessions, proxies)

    manager = FunctionManager(sessions, API_ID, API_HASH)

    await manager.execute(
        command=user_data[message.from_user.id]["command"],
        username=user_data[message.from_user.id]["username"],
        reason_choice=user_data[message.from_user.id]["reason_choice"],
        comment=user_data[message.from_user.id]["comment"]
    )

    await message.reply("Жалобы отправлены!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)start_polling(dp, skip_updates=True)
