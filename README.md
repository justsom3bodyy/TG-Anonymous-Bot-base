
#  Telegram Anonymous Bot Base

A modular, lightweight, and customizable base for building anonymous Telegram feedback and messaging bots using **Python 3** and **aiogram 3.x**.

This template allows users to send anonymous text messages, photos, videos, voice notes, and files to an admin or moderation team without revealing their personal Telegram details. Administrators can reply directly, share their personal contact handle, or ban abusive users with a single tap.

---

## 📂 Repository Structure & Variants

This repository contains **4 architecture variants** to fit different project scales. Choose the script that matches your workflow:

### 1. Forum Topics Mode (`bot_topics_*.py`)
Incoming anonymous messages are routed into a **Telegram Supergroup with Forum Topics enabled**. The bot automatically creates a dedicated, named topic thread for each user who messages the bot.

* **`bot_topics_nodb.py`**: Runs in RAM using Python dictionaries. Fast setup, no local database files created.
* **`bot_topics_db.py`**: Uses a local **SQLite database** (`bot_topics.db`). Thread mappings, user information, and ban states persist across bot restarts.

### 2. Direct PM Mode (`bot_dm_*.py`)
Incoming anonymous messages are forwarded straight to your **personal Telegram private chat (DMs)**. You reply to users using Telegram's native "Reply" function on the forwarded message.

* **`bot_dm_nodb.py`**: Operates in memory without a database file.
* **`bot_dm_db.py`**: Stores message reply mappings and ban lists in a local **SQLite database** (`bot_pm.db`).

---

## Paragraph 1: Installation & Dependencies

### Paragraph 1.1: Required Python Packages

Ensure you have **Python 3.10 or higher** installed.

Install the necessary libraries via `pip`:

For **NoDB** variants (`bot_topics_nodb.py`, `bot_dm_nodb.py`):
```bash
pip install aiogram python-dotenv
```

For **Database** variants (`bot_topics_db.py`, `bot_dm_db.py`):
```bash
pip install aiogram python-dotenv aiosqlite
```

---

## Paragraph 2: Configuration & Setup

### Paragraph 2.1: Environment File Setup (`.env`)

Create a `.env` file in the root directory of your project and configure your environment variables:

```env
# Required for all scripts
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Required for Direct PM bots (bot_dm_nodb.py and bot_dm_db.py)
HOST_USER_ID=987654321

# Required for Forum Topics bots (bot_topics_nodb.py and bot_topics_db.py)
ADMIN_GROUP_ID=-1001234567890

# Optional: Personal handle sent to users when clicking "Send My Contact"
YOUR_PERSONAL_USERNAME=@your_username
```

---

### Paragraph 2.2: How to Obtain Telegram Tokens and IDs

#### Obtaining `BOT_TOKEN`:
1. Search for `@BotFather` on Telegram.
2. Send `/newbot` and follow the setup instructions.
3. Copy the token string provided into `BOT_TOKEN`.

#### Obtaining `HOST_USER_ID` (For Direct PM Mode):
1. Search for `@userinfobot` or `@myidbot` on Telegram.
2. Send `/start`.
3. Copy your numeric user ID into `HOST_USER_ID`.

#### Obtaining `ADMIN_GROUP_ID` (For Forum Topics Mode):
1. Create a new Telegram Group.
2. Open Group Settings and turn on **Topics / Forum**.
3. Add your bot to the group and promote it to **Administrator** (grant permissions to manage topics and send messages).
4. Add `@myidbot` to the group to inspect the chat ID.
5. Copy the group ID (it **must** start with `-100`, e.g., `-1001234567890`) into `ADMIN_GROUP_ID`.

---

## Paragraph 3: Storage & Database Architecture

### In-Memory Storage (NoDB)
* **How it works**: State and message tracking are stored in standard Python dictionaries (`users_db`, `topics_db`, `message_map`).
* **Pros**: Simple, zero database file management, easy to test.
* **Cons**: Volatile. Restarting the script resets active message reply routes and ban lists.

### SQLite Database (DB)
* **How it works**: Data is asynchronously stored in a local SQLite database (`bot_topics.db` or `bot_pm.db`) powered by `aiosqlite`.
* **Pros**: Persistent. Banned users, topic links, and message history survive bot restarts and server reboots.
* **Cons**: Requires the `aiosqlite` package.

---

## Paragraph 4: Code Customization & Localization

### Paragraph 4.1: Customizing Texts, Keyboards, and Reactions

You can modify system responses, translate the interface, or change reaction emojis directly inside the script files.

#### 1. Customizing Bot Texts
Locate the message constants near the top of any script:

```python
READY_TEXT = "Great! Send your anonymous message or media file. I will pass it along."
BANNED_TEXT = "🚫 You have been blocked by the administrator."
CONTACT_SENT_TEXT = f"🔓 Owner's contact: {YOUR_PERSONAL_USERNAME}"
```

To translate the bot into another language (e.g., Spanish), simply modify the string constants:

```python
READY_TEXT = "¡Genial! Envía tu mensaje o archivo anónimo. Lo entregaré inmediatamente."
BANNED_TEXT = "🚫 Has sido bloqueado por el administrador."
CONTACT_SENT_TEXT = f"🔓 Contacto del propietario: {YOUR_PERSONAL_USERNAME}"
```

#### 2. Customizing Admin Inline Buttons
To change the action buttons attached to forwarded messages, update `get_admin_keyboard`:

```python
def get_admin_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⛔ Ban User", callback_data=f"admin_ban_{user_id}"),
            InlineKeyboardButton(text="💬 Share Contact", callback_data=f"admin_contact_{user_id}")
        ]
    ])
```

#### 3. Customizing Emoji Reactions
When a user sends a message, the bot acknowledges delivery by placing a reaction emoji on it. You can change `"✍️"` to any valid emoji like `"👍"`, `"❤️"`, or `"⚡"`:

```python
await bot.set_message_reaction(
    chat_id=message.chat.id,
    message_id=message.message_id,
    reaction=[ReactionTypeEmoji(emoji="👍")]
)
```

#### 4. Adding Auto-Reply Confirmations
If you want the bot to send an explicit text confirmation instead of (or alongside) an emoji reaction:

```python
await message.reply("✅ Your message has been delivered anonymously!")
```

---

## 🚀 Running the Bot

Run the script variant you prefer:

```bash
# Forum Topics mode with SQLite Database
python bot_topics_db.py

# Direct PM mode with SQLite Database
python bot_dm_db.py

# Direct PM mode without Database
python bot_dm_nodb.py

# Forum Topics mode without Database
python bot_topics_nodb.py
```
