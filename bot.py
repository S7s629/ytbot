import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 ابعتلي لينك يوتيوب وهقطعه ليك!\n\nالصيغة:\nرابط | 00:01:30 | 00:02:00"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if "|" not in text:
        await update.message.reply_text("❌ الصيغة: رابط | بداية | نهاية")
        return
    parts = text.split("|")
    if len(parts) != 3:
        await update.message.reply_text("❌ لازم 3 أجزاء")
        return
    url, start_time, end_time = parts[0].strip(), parts[1].strip(), parts[2].strip()
    await update.message.reply_text("⏳ جاري التحميل والتقطيع...")
    try:
        chat_id = update.message.chat_id
        ydl_opts = {
            'format': 'best[filesize<45M]/best',
            'outtmpl': f'full_{chat_id}.%(ext)s',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            input_file = f"full_{chat_id}.{info['ext']}"
        output_file = f"clip_{chat_id}.mp4"
        os.system(f'ffmpeg -i "{input_file}" -ss {start_time} -to {end_time} -c copy "{output_file}" -y')
        with open(output_file, 'rb') as f:
            await update.message.reply_video(f, caption="✅ الكليب جاهز!")
        os.remove(input_file)
        os.remove(output_file)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
