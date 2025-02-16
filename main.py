import os
import re
import time
from pyrogram import Client, filters, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

app = Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

url_pattern = re.compile(r'(@[a-zA-Z0-9_]+|https?://[^\s]+|www\.[^\s]+|\.[a-zA-Z]{2,})')

approved_users = set()  
warnings = {}  
muted_users = {}  

async def is_admin(client, chat_id, user_id):
    async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False


@app.on_message(filters.group & filters.command("approve"))
async def approve_user(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("<b>❌ You are not an admin</b>", parse_mode=enums.ParseMode.HTML)
        return

    if not message.reply_to_message:
        await message.reply_text("<b>Reply to a user to approve them</b>", parse_mode=enums.ParseMode.HTML)
        return

    approved_users.add(message.reply_to_message.from_user.id)
    await message.reply_text(f"<b>✅ {message.reply_to_message.from_user.mention} has been approved.</b>", parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.group)
async def check_bio(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if await is_admin(client, chat_id, user_id) or user_id in approved_users:
        return  

    user_full = await client.get_chat(user_id)
    bio = user_full.bio
    user_name = f"@{user_full.username}" if user_full.username else f"{user_full.first_name}"

    if bio and re.search(url_pattern, bio):
        warnings.setdefault(chat_id, {}).setdefault(user_id, 0)
        warnings[chat_id][user_id] += 1

        if warnings[chat_id][user_id] < 3:
            await message.reply_text(f"⚠️ **Warning {warnings[chat_id][user_id]}/3**\n\n{user_name}, please remove the link from your bio. Otherwise, you will be muted!")
        else:
            try:
                await message.delete()
            except errors.MessageDeleteForbidden:
                await message.reply_text("❌ I need delete permissions!")
                return

            mute_duration = 3600  
            mute_time = int(time.time()) + mute_duration  
            muted_users[user_id] = mute_time  

            try:
                await client.restrict_chat_member(
                    chat_id, user_id,
                    ChatPermissions(),
                    until_date=mute_time
                )
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔓 Unmute", callback_data=f"unmute_{user_id}")]])
                await message.reply_text(
                    f"🔇 **{user_name} has been muted for 1 hour**\n"
                    f"⏳ **Mute Duration:** 1 hour",
                    reply_markup=keyboard
                )
            except errors.ChatAdminRequired:
                await message.reply_text("❌ I don't have permission to mute users.")

            warnings[chat_id][user_id] = 0


@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await callback_query.answer("❌ You are not an admin", show_alert=True)
        return

    if data.startswith("unmute_"):
        target_user_id = int(data.split("_")[1])
        try:
            await client.restrict_chat_member(chat_id, target_user_id, ChatPermissions(can_send_messages=True))
            del muted_users[target_user_id]
            await callback_query.message.edit_text(f"✅ {target_user_id} has been unmuted.")
        except errors.ChatAdminRequired:
            await callback_query.message.edit_text("❌ I don't have permission to unmute users.")


@app.on_message(filters.group & filters.command("unmute"))
async def manual_unmute(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("<b>❌ You are not an admin</b>", parse_mode=enums.ParseMode.HTML)
        return

    if not message.reply_to_message:
        await message.reply_text("<b>Reply to a user or mention them to unmute</b>", parse_mode=enums.ParseMode.HTML)
        return

    target_user = message.reply_to_message.from_user.id
    if target_user in muted_users:
        try:
            await client.restrict_chat_member(chat_id, target_user, ChatPermissions(can_send_messages=True))
            del muted_users[target_user]
            await message.reply_text(f"✅ {message.reply_to_message.from_user.mention} has been unmuted.")
        except errors.ChatAdminRequired:
            await message.reply_text("❌ I don't have permission to unmute users.")


@app.on_message(filters.group & filters.text)
async def detect_muted_user(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id in muted_users:
        user_full = await client.get_chat(user_id)
        user_name = f"@{user_full.username}" if user_full.username else f"{user_full.first_name}"

        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔓 Unmute", callback_data=f"unmute_{user_id}")]])

        await message.reply_text(
            f"🔇 **{user_name} is muted**\n"
            "❌ You cannot send messages until an admin unmutes you.",
            reply_markup=keyboard
        )


@app.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me In Your Group", url="https://t.me/bio_link_restriction_bot?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users")],
        [InlineKeyboardButton("🔔 Updates", url="https://t.me/SWEETY_BOT_UPDATE")]
    ])
    
    await message.reply_text(
        "**🔹 Bio Link Restriction Bot 🔹**\n\n"
        "🚫 This bot detects **links in user bios** and warns them.\n"
        "⚠️ After **3 warnings**, the user is **muted for 1 hour**.\n"
        "✅ Admins and approved users are ignored.\n"
        "🔓 Admins can **unmute users manually** using `/unmute @username`.\n"
        "🛠 Use `/approve` to exclude a user from restriction.\n\n"
        "🔥 Add this bot to your group for protection!",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )


app.run()
