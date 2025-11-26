import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['🎯 Раскладка по темпу']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = """🏃‍♂️ Беговой калькулятор

Нажми кнопку или введи темп (например: 4:30)

👉 https://t.me/run_xo"""
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🎯 Раскладка по темпу':
        await update.message.reply_text("Введи темп в формате 4:30")
    
    elif ':' in text:
        try:
            parts = text.split(':')
            minutes = int(parts[0])
            seconds = int(parts[1])
            
            total_seconds_per_km = minutes * 60 + seconds
            distances = [200, 400, 600, 800, 1000]
            results = []
            
            for distance in distances:
                time_seconds = (total_seconds_per_km * distance) / 1000
                mins = int(time_seconds // 60)
                secs = int(time_seconds % 60)
                results.append(f"• {distance} м — {mins}:{secs:02d}")
            
            response = f"🎯 Раскладка для темпа {minutes}:{seconds:02d} мин/км\n\n" + "\n".join(results) + "\n\n💡 https://t.me/run_xo"
            await update.message.reply_text(response)
            
        except:
            await update.message.reply_text("❌ Ошибка. Используй формат 4:30")
    
    else:
        await update.message.reply_text("Используй кнопки или введи темп в формате 4:30")

def main():
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не установлен!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен и работает!")
    application.run_polling()

if __name__ == "__main__":
    main()
