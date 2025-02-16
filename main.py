import os
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import re

# Environment Variables se API Config Load Karna
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

app = Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# URL Pattern Detection (Bio aur Messages me)
url_pattern = re.compile(r'(https?://|www\.)[a-zA-Z0-9.\-]+(\.[a-zA-Z]{2,})+(/[a-zA-Z0-9._%+-]*)*')

# Warnings System
warnings = {}
punishment = {}

# Default Punishment Settings
DEFAULT_WARNING_LIMIT = 3
DEFAULT_PUNISHMENT = "mute"
DEFAULT_PUNISHMENT_SET = ("warn", DEFAULT_WARNING_LIMIT, DEFAULT_PUNISHMENT)

# ✅ **Admin Check Function**
async def is_admin(client, chat_id, user_id):
    async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False

# ✅ **Punishment Selection Command**
@app.on_message(filters.group & filters.command("config"))
async def configure(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("<b>❌ You are not an administrator!</b>", parse_mode=enums.ParseMode.HTML)
        await message.delete()
        return

    current_punishment = punishment.get(chat_id, DEFAULT_PUNISHMENT_SET)[2]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Warn", callback_data="warn")],
        [InlineKeyboardButton("Mute ✅" if current_punishment == "mute" else "Mute", callback_data="mute"),
         InlineKeyboardButton("Ban ✅" if current_punishment == "ban" else "Ban", callback_data="ban")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    await message.reply_text("<b>⚙️ Select punishment for users who post links:</b>", reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    await message.delete()

# ✅ **Bio Check for Links**
@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    chat_id = message.chat.id
    for member in message.new_chat_members:
        try:
            bio = await client.get_users(member.id)
            bio_text = bio.bio if bio.bio else ""

            if url_pattern.search(bio_text):
                await message.chat.restrict_member(member.id, ChatPermissions())
                await message.reply_text(f"⚠️ User {member.mention} has links in their bio and has been muted!", parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            print(f"Error checking bio: {e}")

# ✅ **Message Link Detection**
@app.on_message(filters.text & filters.group)
async def check_links(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text

    if url_pattern.search(text):
        if chat_id not in warnings:
            warnings[chat_id] = {}

        if user_id not in warnings[chat_id]:
            warnings[chat_id][user_id] = 0

        warnings[chat_id][user_id] += 1

        if warnings[chat_id][user_id] >= DEFAULT_WARNING_LIMIT:
            punishment_action = punishment.get(chat_id, DEFAULT_PUNISHMENT_SET)[2]
            if punishment_action == "mute":
                await message.chat.restrict_member(user_id, ChatPermissions())
                await message.reply_text(f"🚫 {message.from_user.mention} has been muted for repeated link posting!", parse_mode=enums.ParseMode.HTML)
            elif punishment_action == "ban":
                await message.chat.ban_member(user_id)
                await message.reply_text(f"❌ {message.from_user.mention} has been banned for posting links!", parse_mode=enums.ParseMode.HTML)

        else:
            await message.reply_text(f"⚠️ {message.from_user.mention}, do not post links! ({warnings[chat_id][user_id]}/{DEFAULT_WARNING_LIMIT} warnings)", parse_mode=enums.ParseMode.HTML)

        await message.delete()

# ✅ **Bot Start Message**
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"👋 Hello {message.from_user.mention}, I am your bot!")

app.run()
