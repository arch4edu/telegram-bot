import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types


class Config:
    def __init__(self, path="config.json"):
        self.path = Path(path)
        if self.path.exists():
            self.dict = json.load(open(self.path))
        else:
            self.dict = {}
            self.save()

    def get(self, chat, key):
        if not chat in self.dict:
            return None
        return None if not key in self.dict[chat] else self.dict[chat][key]

    def set(self, chat, key, value):
        if not chat in self.dict:
            self.dict[chat] = {}
        self.dict[chat][key] = value
        self.save()

    def save(self):
        json.dump(self.dict, open(self.path, "w"), sort_keys=True, indent=2)


logging.basicConfig(level=logging.INFO)

config = Config()
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


# @dp.message_handler(commands=["arch4edu"])
# async def set_ping(message: types.Message):
#    user = message.from_user.mention
#    await message.reply(f"I will ping {user} in {chat}.")


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
