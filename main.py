import os
from pyrogram import Client, filters, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import re

# Environment Variables se API Config Load Karna
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
mute_duration = 3 * 60 * 60  # 3 Hours Mute

async def is_admin(client, chat_id, user_id):
    async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        if member.user.id == user_id:
            return True
    return False

@app.on_message(filters.group)
async def check_bio(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Agar user admin hai toh ignore karo
    if await is_admin(client, chat_id, user_id):
        return  

    # User Bio Check
    user_full = await client.get_chat(user_id)
    bio = user_full.bio
    user_name = f"@{user_full.username}" if user_full.username else f"{user_full.first_name} {user_full.last_name or ''}".strip()

    if bio and re.search(url_pattern, bio):
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            await message.reply_text("Mujhe message delete karne ki permission nahi mili hai.")
            return

        action = punishment.get(chat_id, default_punishment_set)

        if action[0] == "warn":
            warnings[user_id] = warnings.get(user_id, 0) + 1
            sent_msg = await message.reply_text(f"{user_name}, apne bio se link hatao! ⚠️ Warning: {warnings[user_id]}/{action[1]}")

            if warnings[user_id] >= action[1]:
                try:
                    if action[2] == "mute":
                        await client.restrict_chat_member(chat_id, user_id, ChatPermissions(), until_date=int(time.time()) + mute_duration)
                        
                        # User ko message bhejna
                        user_msg = await client.send_message(
                            user_id, 
                            f"⛔ **Aapko group me mute kar diya gaya hai!**\n\n🔍 *Aapke bio me link paya gaya jo allow nahi hai.*\n\n🔓 *Agar aapne bio se link hata diya hai, to unmute request bheje!*",
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔓 Unmute Request", callback_data=f"unmute_request_{user_id}_{chat_id}")]])
                        )

                        # Admin ke paas approval request bhejna
                        keyboard = InlineKeyboardMarkup([
                            [InlineKeyboardButton("✅ Approve & Unmute", callback_data=f"approve_{user_id}_{chat_id}")],
                        ])
                        await client.send_message(chat_id, f"👮 **Admin:** {user_name} ko mute kiya gaya hai.", reply_markup=keyboard)

                except errors.ChatAdminRequired:
                    await sent_msg.edit(f"Bot ke pass mute karne ki permission nahi hai.")
        else:
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions(), until_date=int(time.time()) + mute_duration)
            await message.reply_text(f"{user_name} ko 🔇 3 ghante ke liye mute kar diya gaya hai.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔓 Unmute Request", callback_data=f"unmute_request_{user_id}_{chat_id}")]]))

@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # **Admin Approve & Unmute**  
    if data.startswith("approve_"):
        parts = data.split("_")
        target_user_id = int(parts[1])
        target_chat_id = int(parts[2])

        if not await is_admin(client, target_chat_id, user_id):
            await callback_query.answer("❌ Aap admin nahi hai.", show_alert=True)
            return

        try:
            await client.restrict_chat_member(target_chat_id, target_user_id, ChatPermissions(can_send_messages=True))
            await callback_query.message.edit_text(f"✅ {target_user_id} ko unmute kar diya gaya hai!")
        except errors.ChatAdminRequired:
            await callback_query.message.edit_text("❌ Bot ke pass permission nahi hai.")

    # **User Unmute Request Button**  
    elif data.startswith("unmute_request_"):
        parts = data.split("_")
        target_user_id = int(parts[2])
        target_chat_id = int(parts[3])

        # Admin ko notify karna
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve & Unmute", callback_data=f"approve_{target_user_id}_{target_chat_id}")]])
        await client.send_message(target_chat_id, f"⚠️ **Unmute Request:**\nUser: {target_user_id} ne unmute request bheji hai.", reply_markup=keyboard)

        await callback_query.answer("✅ Request admin ko bhej di gayi!", show_alert=True)
