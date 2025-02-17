import os
from pyrogram import Client, filters, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import re

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
        "🛠 ᴀᴅᴍɪɴs ᴜsᴇ /unmute ᴛᴏ ᴇxᴄʟᴜᴅᴇ ᴀ ᴜsᴇʀ ғʀᴏᴍ ʀᴇsᴛʀɪᴄᴛɪᴏɴ.\n\n"
        "🔥 𝐀ᴅᴅ 𝐌ᴇ 𝐓ᴏ 𝐘ᴏᴜʀ 𝐆ʀᴏᴜᴘ ғᴏʀ 𝐏ʀᴏᴛᴇᴄᴛɪᴏɴ!",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

@app.on_message(filters.group)
async def check_bio(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    user_full = await client.get_chat(user_id)
    bio = user_full.bio
    user_name = f"@{user_full.username} [<code>{user_id}</code>]" if user_full.username else f"{user_full.first_name} [<code>{user_id}</code>]"

    if bio and re.search(url_pattern, bio):
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            await message.reply_text("Please grant me delete permission.")
            return

        action = punishment.get(chat_id, default_punishment_set)
        if action[0] == "warn":
            warnings[user_id] = warnings.get(user_id, 0) + 1
            sent_msg = await message.reply_text(f"{user_name} please remove any links from your bio. ⚠️ Warning {warnings[user_id]}/{action[1]}", parse_mode=enums.ParseMode.HTML)

            if warnings[user_id] >= action[1]:
                try:
                    if action[2] == "mute":
                        await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Unmute", callback_data=f"unmute_{user_id}")]])
                        await sent_msg.edit(f"{user_name} has been 🔇 muted for [ Link In Bio ].", reply_markup=keyboard)
                    elif action[2] == "ban":
                        await client.ban_chat_member(chat_id, user_id)
                        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Unban", callback_data=f"unban_{user_id}")]])
                        await sent_msg.edit(f"{user_name} has been 🔨 banned for [ Link In Bio ].", reply_markup=keyboard)
                except errors.ChatAdminRequired:
                    await sent_msg.edit(f"I don't have permission to {action[2]} users.")
        elif action[0] == "mute":
            try:
                await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Unmute", callback_data=f"unmute_{user_id}")]])
                await message.reply_text(f"{user_name} has been 🔇 muted for [ Link In Bio ].", reply_markup=keyboard)
            except errors.ChatAdminRequired:
                await message.reply_text("I don't have permission to mute users.")
        elif action[0] == "ban":
            try:
                await client.ban_chat_member(chat_id, user_id)
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Unban", callback_data=f"unban_{user_id}")]])
                await message.reply_text(f"{user_name} has been 🔨 banned for [ Link In Bio ].", reply_markup=keyboard)
            except errors.ChatAdminRequired:
                await message.reply_text("I don't have permission to ban users.")
    else:
        if user_id in warnings:
            del warnings[user_id]

@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await callback_query.answer("❌ You are not an administrator", show_alert=True)
        return

    if data.startswith("unmute_"):
        target_user_id = int(data.split("_")[1])
        try:
            await client.restrict_chat_member(chat_id, target_user_id, ChatPermissions(can_send_messages=True))
            await callback_query.message.edit(f"✅ <b>Unmuted</b> user <code>{target_user_id}</code>", parse_mode=enums.ParseMode.HTML)
        except errors.ChatAdminRequired:
            await callback_query.message.edit("❌ I don't have permission to unmute users.")
        await callback_query.answer()

    elif data.startswith("unban_"):
        target_user_id = int(data.split("_")[1])
        try:
            await client.unban_chat_member(chat_id, target_user_id)
            await callback_query.message.edit(f"✅ <b>Unbanned</b> user <code>{target_user_id}</code>", parse_mode=enums.ParseMode.HTML)
        except errors.ChatAdminRequired:
            await callback_query.message.edit("❌ I don't have permission to unban users.")
        await callback_query.answer()

@app.on_message(filters.group & filters.command("mute"))
async def mute_user(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("❌ You are not an administrator.", parse_mode=enums.ParseMode.HTML)
        return

    args = message.text.split(" ")
    if len(args) < 2:
        await message.reply_text("❌ Please provide a username or user ID to mute.", parse_mode=enums.ParseMode.HTML)
        return

    target_user = args[1]
    try:
        target_user_id = int(target_user)  # If it's a user ID
    except ValueError:
        target_user_id = (await client.get_users(target_user)).id  # If it's a username

    try:
        await client.restrict_chat_member(chat_id, target_user_id, ChatPermissions())
        await message.reply_text(f"✅ User <code>{target_user}</code> has been muted.", parse_mode=enums.ParseMode.HTML)
    except errors.ChatAdminRequired:
        await message.reply_text("❌ I don't have permission to mute this user.", parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.group & filters.command("unmute"))
async def unmute_user(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("❌ You are not an administrator.", parse_mode=enums.ParseMode.HTML)
        return

    args = message.text.split(" ")
    if len(args) < 2:
        await message.reply_text("❌ Please provide a username or user ID to unmute.", parse_mode=enums.ParseMode.HTML)
        return

    target_user = args[1]
    try:
        target_user_id = int(target_user)  # If it's a user ID
    except ValueError:
        target_user_id = (await client.get_users(target_user)).id  # If it's a username

    try:
        await client.restrict_chat_member(chat_id, target_user_id, ChatPermissions(can_send_messages=True))
        await message.reply_text(f"✅ User <code>{target_user}</code> has been unmuted.", parse_mode=enums.ParseMode.HTML)
    except errors.ChatAdminRequired:
        await message.reply_text("❌ I don't have permission to unmute this user.", parse_mode=enums.ParseMode.HTML)

app.run()
