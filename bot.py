import os
import requests
from io import BytesIO
from telegram import InputFile, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# قراءة التوكنات من ملف .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if TELEGRAM_TOKEN is None or OPENAI_API_KEY is None:
    print("❌ الرجاء تعيين متغيرات البيئة TELEGRAM_BOT_TOKEN و OPENAI_API_KEY")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 مرحباً! أرسل لي وصف الصورة وسأحولها إلى صورة لك 🎨")

async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt_text = update.message.text
    await update.message.reply_text("⏳ جاري توليد الصورة...")

    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-image-1",
        "prompt": prompt_text,
        "size": "512x512"
    }

    try:
        r = requests.post(url, headers=headers, json=data)
        r.raise_for_status()
        image_url = r.json()["data"][0]["url"]
        img_bytes = BytesIO(requests.get(image_url).content)
        await update.message.reply_photo(photo=InputFile(img_bytes, filename="image.png"))
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ: " + str(e))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))
    print("🤖 Bot started...")
    app.run_polling()
