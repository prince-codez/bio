import os
import re
from pyrogram import Client, filters, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

app = Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

url_pattern = re.compile(r'(https?://|www\.)[a-zA-Z0-9.\-]+(\.[a-zA-Z]{2,})+(/[a-zA-Z0-9._%+-]*)*')

warnings = {}
punishment = {}

default_warning_limit = 3  
default_punishment = "mute"
default_punishment_set = ("warn", default_warning_limit, default_punishment)

approved_users = {}

async def is_admin(client, chat_id, user_id):
    async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False

@app.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔮 𝐀ᴅᴅ 𝐌ᴇ 𝐈ɴ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ 🔮", url="https://t.me/bio_link_restriction_bot?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users")],
        [InlineKeyboardButton("☔ Uᴘᴅᴀᴛᴇs ☔", url="https://t.me/SWEETY_BOT_UPDATE")]
    ])
    
    await message.reply_text(
        "🐬 Bɪᴏ Lɪɴᴋ Rᴇsᴛʀɪᴄᴛɪᴏɴ Bᴏᴛ 🐬\n\n"
        "🚫 ᴛʜɪs ʙᴏᴛ ᴅᴇᴛᴇᴄᴛs ʟɪɴᴋs ɪɴ ᴜsᴇʀ ʙɪᴏs ᴀɴᴅ ʀᴇsᴛʀɪᴄᴛs ᴛʜᴇᴍ.\n"
        "⚠️ ᴀғᴛᴇʀ 𝟹 ᴡᴀʀɴɪɴɢs, ᴛʜᴇ ᴜsᴇʀ ɪs ʀᴇsᴛʀɪᴄᴛᴇᴅ ғʀᴏᴍ sᴇɴᴅɪɴɢ ᴍᴇssᴀɢᴇs.\n"
        "✅ ᴀᴅᴍɪɴs ᴀɴᴅ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜsᴇʀs ᴀʀᴇ ɪɢɴᴏʀᴇᴅ.\n"
        "🔓 ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs ᴍᴀɴᴜᴀʟʟʏ ᴜsɪɴɢ /unrestrict @username.\n"
        "🛠 ᴜsᴇ /approve @username ᴛᴏ ᴇxᴄʟᴜᴅᴇ ᴀ ᴜsᴇʀ ғʀᴏᴍ ʀᴇsᴛʀɪᴄᴛɪᴏɴ.\n"
        "🛠 ᴜsᴇ /unapprove @username ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ᴜsᴇʀ ғʀᴏᴍ ᴛʜᴇ ᴀᴘᴘʀᴏᴠᴇᴅ ʟɪsᴛ.\n\n"
        "🔥 𝐀ᴅᴅ 𝐌ᴇ 𝐓ᴏ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ ғᴏʀ 𝐏ʀᴏᴛᴇᴄᴛɪᴏɴ!",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

@app.on_message(filters.group)
async def check_bio(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id in approved_users.get(chat_id, []):
        return  

    user_full = await client.get_chat(user_id)
    bio = user_full.bio
    user_name = f"@{user_full.username} [<code>{user_id}</code>]" if user_full.username else f"{user_full.first_name} [<code>{user_id}</code>]"

    if bio and re.search(url_pattern, bio):
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            await message.reply_text("Please grant me delete permission.")
            return

        warnings[user_id] = warnings.get(user_id, 0) + 1
        if warnings[user_id] >= default_warning_limit:
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
            await message.reply_text(f"{user_name} has been 🔇 muted for link in bio.")
        else:
            await message.reply_text(f"{user_name} please remove any links from your bio. ⚠️ Warning {warnings[user_id]}/{default_warning_limit}", parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.command("approve") & filters.group)
async def approve_user(client, message):
    chat_id = message.chat.id
    user = message.reply_to_message.from_user if message.reply_to_message else message.command[1]

    if not await is_admin(client, chat_id, message.from_user.id):
        await message.reply_text("❌ Only admins can approve users!")
        return

    if isinstance(user, str):
        try:
            user = await client.get_users(user)
        except errors.UsernameNotOccupied:
            await message.reply_text("❌ User not found!")
            return

    approved_users.setdefault(chat_id, []).append(user.id)
    await message.reply_text(f"✅ {user.mention} has been approved and will not be restricted.")

@app.on_message(filters.command("unapprove") & filters.group)
async def unapprove_user(client, message):
    chat_id = message.chat.id
    user = message.reply_to_message.from_user if message.reply_to_message else message.command[1]

    if not await is_admin(client, chat_id, message.from_user.id):
        await message.reply_text("❌ Only admins can unapprove users!")
        return

    if isinstance(user, str):
        try:
            user = await client.get_users(user)
        except errors.UsernameNotOccupied:
            await message.reply_text("❌ User not found!")
            return

    approved_users.get(chat_id, []).remove(user.id)
    await message.reply_text(f"🚫 {user.mention} has been unapproved and will be monitored again.")

app.run()
