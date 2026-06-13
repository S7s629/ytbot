import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 ابعتلي لينك يوتيوب وهقطعه ليك!\n\nالصيغة:\n`لينك | من | لحد`\n\nمثال:\nhttps://youtube.com/... | 00:01:30 | 00:02:00")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if "|" not in text:
        await update.message.reply_text("❌ ابعت اللينك بالصيغة دي:\nرابط | 00:01:30 | 00:02:00")
        return
    
    parts = text.split("|")
    if len(parts) != 3:
        await update.message.reply_text("❌ لازم 3 أجزاء: رابط | بداية | نهاية")
        return
    
    url = parts[0].strip()
    start_time = parts[1].strip()
    end_time = parts[2].strip()
    
    await update.message.reply_text("⏳ جاري التحميل والتقطيع...")
    
    try:
        output_file = f"clip_{update.message.chat_id}.mp4"
        
        ydl_opts = {
            'format': 'best[filesize<45M]/best',
            'outtmpl': f'full_{update.message.chat_id}.%(ext)s',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            input_file = f"full_{update.message.chat_id}.{info['ext']}"
        
        # تقطيع بـ ffmpeg
        os.system(f'ffmpeg -i "{input_file}" -ss {start_time} -to {end_time} -c copy "{output_file}" -y')
        
        # بعت الفيديو
        with open(output_file, 'rb') as f:
            await update.message.reply_video(f, caption="✅ الكليب جاهز!")
        
        # حذف الملفات
        os.remove(input_file)
        os.remove(output_file)
        
    except Exception as e:
        await update.message.reply_text(f"❌ حصل خطأ: {str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
