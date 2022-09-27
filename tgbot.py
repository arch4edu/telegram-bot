import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types

from config import Config
from repository import Repository

logging.basicConfig(level=logging.INFO)

config = Config()
repository = Repository()
bot = Bot(token=config.get("config", "token"))
dp = Dispatcher(bot)
last_run = {}


def cooldown(chat_id):
    now = datetime.now()
    if chat_id in last_run and now - last_run[chat_id] < timedelta(minutes=15):
        return True
    last_run[chat_id] = now
    return False


def get_chat(message):
    chat = message.chat.mention
    chat = chat if chat else str(message.chat.id)
    return chat


@dp.message_handler(commands=["start"])
async def send_start(message: types.Message):
    reply = []
    reply.append("Hi!")
    reply.append(
        "I'm the cactus bot from [arch4edu](https://github.com/arch4edu/arch4edu)!"
    )
    reply.append("I ping someone when there is message about arch4edu.")
    await message.reply("\n".join(reply), parse_mode="Markdown")


@dp.message_handler(commands=["help"])
async def send_help(message: types.Message):
    reply = []
    reply.append("/disable\t Disable ping in this chat.")
    reply.append("/enable\t Enable ping in this chat.")
    reply.append("/pingme\t Ping you in this chat.")
    reply.append("/arch4edu package\t Search for a package in arch4edu.")
    reply.append("/help\t Show this help.")
    await message.reply("\n".join(reply))


@dp.message_handler(commands=["disable"])
async def set_disable(message: types.Message):
    chat = get_chat(message)
    config.set(chat, "enable", False)
    await message.reply(f"I won't ping in {chat}.")


@dp.message_handler(commands=["enable"])
async def set_enable(message: types.Message):
    chat = get_chat(message)
    config.set(chat, "enable", True)
    await message.reply(f"I will ping in {chat}.")


@dp.message_handler(commands=["pingme"])
async def set_ping(message: types.Message):
    user = message.from_user.mention
    chat = get_chat(message)
    config.set(chat, "ping", user)
    await message.reply(f"I will ping {user} in {chat}.")


@dp.message_handler(commands=["arch4edu"])
async def search(message: types.Message):
    package = message.get_args()

    if package == "":
        await message.reply("Usage: /arch4edu package")

    result = repository.search(package)
    if len(result) > 0:
        await message.reply("\n".join(" ".join(i) for i in result))
    else:
        await message.reply(f"Cannot find {package} in arch4edu.")


@dp.message_handler()
async def ping(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    user = message.from_user.mention
    chat = get_chat(message)
    enable = config.get(chat, "enable")
    enable = True if enable is None else enable
    if enable and "arch4edu" in message.text and not cooldown(chat):
        _user = config.get(chat, "ping")
        if user == _user:
            return
        if _user:
            await message.reply(f"Ping {_user}.")
        else:
            await message.reply("I don't know who to ping. Please set it with /pingme.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
