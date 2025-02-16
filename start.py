import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Initialize Pyrogram Client
app = Client(
    "my_bot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

@app.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    await message.reply_video(
        video="https://envs.sh/RCD.mp4",  # Replace with actual video URL
        caption=(
            f"""**❖ нᴇʏ {message.from_user.first_name} !, ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ !
━━━━━━━━━━━━━━━━━━━━━━━━━━━

● ɪ ᴀᴍ {(await client.get_me()).mention} !

⦿━━━━━━━━━━━━━━━━━━━━━⦿
❍ • ɪ'ʟʟ ᴍᴜᴛᴇ ᴛʜᴇ ʙɪᴏ ʟɪɴᴋ ᴜsᴇʀ •
│❍ • ɴᴏ ʟᴀɢs + ɴᴏ ᴀᴅs •
│❍ • 24x7 ᴏɴʟɪɴᴇ sᴜᴘᴘᴏʀᴛ •
│❍ • ᴀ ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ •
❍ • ɪ ʜᴀᴠᴇ sᴘᴇᴄɪᴀʟ ғᴇᴀᴛᴜʀᴇs •
⦿━━━━━━━━━━━━━━━━━━━━━⦿

❖ ᴛʜɪs ɪs ᴘᴏᴡᴇʀғᴜʟ ʙᴏᴛ, ғᴏʀ ʏᴏᴜʀ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ  •\n\n❍ • ʏᴏᴜ ᴄᴀɴ ᴍᴀᴋᴇ ʏᴏᴜʀ ʙᴏᴛ ʙʏ /clone**"""
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("💠 ᴀᴅᴅ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ 💠", url="https://t.me/SWEETY9_REACTION_BOT?startgroup=true")],
                [
                    InlineKeyboardButton("🛠 sᴜᴘᴘᴏʀᴛ 🛠", url="https://t.me/APNA_CLUB_09"),
                    InlineKeyboardButton("🐰 ᴜᴘᴅᴀᴛᴇs 🐰", url="https://t.me/SWEETY_BOT_UPDATE")
                ],
                [
                    InlineKeyboardButton("🌀 ᴏᴡɴᴇʀ 🌀", url="https://t.me/PRINCE_WEBZ"),
                    InlineKeyboardButton("📜 ᴄᴏᴍᴍᴀɴᴅs 📜", callback_data="help")
                ]
            ]
        )
    )

# Handle "Commands" button to show help menu
@app.on_callback_query(filters.regex("help"))
async def help_callback(client: Client, query):
    help_text = "**📜 ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs 📜**\n\n"
    help_text += "/start - 𝚂𝚝𝚊𝚛𝚝 𝚝𝚑𝚎 𝙱𝚘𝚝\n"
    help_text += "/help - 𝙲𝚘𝚖𝚖𝚊𝚗𝚍 𝙻𝚒𝚜𝚝\n"
    help_text += "/mute - 𝙼𝚞𝚝𝚎 𝚄𝚜𝚎𝚛\n"
    help_text += "/unmute - 𝚄𝚗𝚖𝚞𝚝𝚎 𝚄𝚜𝚎𝚛\n"
    help_text += "/ban - 𝙱𝚊𝚗 𝚄𝚜𝚎𝚛\n"
    help_text += "/unban - 𝚄𝚗𝚋𝚊𝚗 𝚄𝚜𝚎𝚛\n"

    await query.message.edit_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start")]]
        )
    )

# Handle "Back" button to return to start message
@app.on_callback_query(filters.regex("start"))
async def start_callback(client: Client, query):
    await start_message(client, query.message)

# Run the bot
app.run()