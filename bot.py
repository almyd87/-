import os
import requests
from io import BytesIO
from telegram import InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

API_URL = os.getenv('API_URL', 'http://localhost:8000/generate')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('مرحباً! أرسل لي وصف الصورة وسأرسلها لك.')

async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt_text = update.message.text
    payload = {
        "prompt": prompt_text,
        "width": 512,
        "height": 512,
        "steps": 25,
        "guidance": 7.5
    }
    try:
        r = requests.post(API_URL, json=payload, stream=True, timeout=60)
        if r.status_code == 200:
            bio = BytesIO(r.content)
            bio.seek(0)
            await update.message.reply_photo(photo=InputFile(bio, filename='image.png'))
        else:
            await update.message.reply_text('عذراً، حدث خطأ أثناء توليد الصورة.')
    except Exception as e:
        await update.message.reply_text('خطأ في الاتصال بالخادم: ' + str(e))

if __name__ == '__main__':
    if TELEGRAM_TOKEN is None:
        print('Please set TELEGRAM_BOT_TOKEN environment variable')
        exit(1)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))
    print('Bot started...')
    app.run_polling()
