from pyrogram import Client, filters
import config

app = Client(
    "my_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! I am your Telegram bot.")

app.run()
