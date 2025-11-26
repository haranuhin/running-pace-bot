import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['🎯 Раскладка по темпу', '⏱ Время на дистанцию'],
        ['📏 Темп по времени', '📊 Пройденная дистанция']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = """
🏃‍♂️ *Беговой калькулятор*

Выбери тип расчета:
• 🎯 Раскладка по темпу
• ⏱ Время на дистанцию  
• 📏 Темп по времени
• 📊 Пройденная дистанция

👉 https://t.me/run_xo
    """
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🎯 Раскладка по темпу':
        await update.message.reply_text("Введи темп (например: 4:30)")
    
    elif text == '⏱ Время на дистанцию':
        await update.message.reply_text("Введи: дистанция в км и темп (например: 10 4:30)")
    
    elif text == '📏 Темп по времени':
        await update.message.reply_text("Введи: дистанция и время (например: 10 60)")
    
    elif text == '📊 Пройденная дистанция':
        await update.message.reply_text("Введи: время и темп (например: 60 5:00)")
    
    else:
        # Простой расчет раскладки
        if ':' in text and len(text) <= 5:
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
                
                response = f"🎯 Темп {minutes}:{seconds:02d} мин/км\n\n" + "\n".join(results)
                await update.message.reply_text(response)
                
            except:
                await update.message.reply_text("❌ Ошибка. Пример: 4:30")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🏃‍♂️ Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
