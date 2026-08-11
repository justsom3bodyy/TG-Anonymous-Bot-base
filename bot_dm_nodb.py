#!/usr/bin/env python3

# If you don't know what packages to install or how they are named, read README paragraph 1.1

import os
import sys
import asyncio
import logging
from html import escape

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReactionTypeEmoji
)

load_dotenv()

# === config ===
# if you don't know what is this or how to use it, read README paragraph 2 (2.1 for dotenv/getenv, 2.2 for IDs)

BOT_TOKEN = os.getenv("BOT_TOKEN")
HOST_USER_ID = int(os.getenv("HOST_USER_ID", 0)) if os.getenv("HOST_USER_ID") else None
YOUR_PERSONAL_USERNAME = os.getenv("YOUR_PERSONAL_USERNAME", "@username")

if not BOT_TOKEN or not HOST_USER_ID:
    print("[ERROR] BOT_TOKEN or HOST_USER_ID not found in .env file! Read README paragraph 2.1")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === in-memory storage ===
# If you don't know what a database is or how to work with that thing, read README paragraph 3
users_db = {}
message_map = {}

# === states ===

class UserState(StatesGroup):
    chatting = State()

# === messages & keyboards ===
# Check README paragraph 4.1 for customization presets

READY_TEXT = "Отлично! Напишите ваше анонимное сообщение или отправьте медиафайл. Я всё передам."
BANNED_TEXT = "🚫 Вы заблокированы администратором."
CONTACT_SENT_TEXT = f"🔓 Контакт владельца: {YOUR_PERSONAL_USERNAME}"

def get_admin_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚫 Ban", callback_data=f"admin_ban_{user_id}"),
            InlineKeyboardButton(text="🔓 Send My Contact", callback_data=f"admin_contact_{user_id}")
        ]
    ])

# === handlers ===

@dp.message(CommandStart(), F.chat.type == "private", F.from_user.id != HOST_USER_ID)
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in users_db and users_db[user_id].get('is_banned'):
        await message.answer(BANNED_TEXT)
        return

    users_db[user_id] = {
        'username': message.from_user.username or "NoUsername",
        'full_name': message.from_user.full_name,
        'is_banned': False
    }

    await message.answer(READY_TEXT)
    await state.set_state(UserState.chatting)

@dp.message(F.chat.type == "private", F.from_user.id != HOST_USER_ID)
async def forward_client_to_host(message: Message):
    user_id = message.from_user.id
    user = users_db.get(user_id)

    if not user or user.get('is_banned'):
        return

    username = message.from_user.username
    full_name_safe = escape(message.from_user.full_name)
    user_link = f"@{escape(username)}" if username else f'<a href="tg://user?id={user_id}">{full_name_safe}</a>'
    header = f"👤 <b>From:</b> {user_link}\n──────────────────\n"

    try:
        sent_msg = None
        if message.text:
            text_safe = escape(message.text)
            sent_msg = await bot.send_message(
                chat_id=HOST_USER_ID,
                text=header + text_safe,
                reply_markup=get_admin_keyboard(user_id),
                parse_mode="HTML"
            )
        else:
            caption_safe = escape(message.caption) if message.caption else ""
            sent_msg = await bot.copy_message(
                chat_id=HOST_USER_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                caption=header + caption_safe,
                reply_markup=get_admin_keyboard(user_id),
                parse_mode="HTML"
            )

        if sent_msg:
            message_map[sent_msg.message_id] = user_id

        await bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji="✍️")]
        )
    except Exception as e:
        logging.error(f"Error forwarding message to host PM: {e}")

@dp.message(F.chat.type == "private", F.from_user.id == HOST_USER_ID)
async def forward_host_reply_to_client(message: Message):
    if not message.reply_to_message:
        await message.reply("💡 To reply to a user, use Telegram's <b>Reply</b> feature on their message.", parse_mode="HTML")
        return

    client_id = message_map.get(message.reply_to_message.message_id)
    if not client_id:
        await message.reply("❌ Unable to find user associated with this message.")
        return

    try:
        await bot.copy_message(
            chat_id=client_id,
            from_chat_id=HOST_USER_ID,
            message_id=message.message_id
        )
        await bot.set_message_reaction(
            chat_id=HOST_USER_ID,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji="✍️")]
        )
    except Exception:
        await bot.set_message_reaction(
            chat_id=HOST_USER_ID,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji="🚫")]
        )
        await message.reply("⚠️ <b>Delivery Failed!</b> The user blocked the bot or deleted the chat.", parse_mode="HTML")

@dp.callback_query(F.data.startswith("admin_"), F.from_user.id == HOST_USER_ID)
async def admin_buttons(callback: CallbackQuery):
    action, user_id = callback.data.split("_")[1], int(callback.data.split("_")[2])
    user = users_db.get(user_id)
    if not user:
        return

    if action == "ban":
        users_db[user_id]['is_banned'] = True
        try:
            await bot.send_message(user_id, BANNED_TEXT)
        except Exception:
            pass
        await callback.message.answer("🚫 User banned.")

    elif action == "contact":
        try:
            await bot.send_message(user_id, CONTACT_SENT_TEXT)
            await callback.message.answer("🔓 Contact info sent.")
        except Exception:
            await callback.message.answer("❌ Delivery failed.")

    await callback.answer()

async def main():
    print("[INFO] Bot WITHOUT Database & Direct PM forwarding started.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
