import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Токен бота (будет установлен в переменных окружения Railway)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8303379555:AAF_koul86cJtzaiNOMSu7QvMinmhzihZVA')

# Состояния для ConversationHandler
CHOOSING, CALC_PACE, CALC_TIME, CALC_DISTANCE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение с клавиатурой"""
    keyboard = [
        ['🎯 Раскладка по темпу', '⏱ Время на дистанцию'],
        ['📏 Темп по времени', '📊 Пройденная дистанция']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = """
🏃‍♂️ *Беговой калькулятор PRO*

Выбери тип расчета:

*🎯 Раскладка по темпу* - узнай время для отрезков 200м-1000м
*⏱ Время на дистанцию* - рассчитай итоговое время по темпу  
*📏 Темп по времени* - определи нужный темп для цели
*📊 Пройденная дистанция* - сколько пробежишь за время

_Подписывайся на телеграм-канал_ 👉 https://t.me/run_xo
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
    return CHOOSING

async def calculate_pace_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Раскладка по темпу (основная функция)"""
    try:
        user_input = update.message.text.strip()
        
        # Проверяем формат ввода
        if ':' not in user_input:
            await update.message.reply_text("❌ Используй формат *4:30* или *5:45*", parse_mode='Markdown')
            return CHOOSING
        
        # Разбираем минуты и секунды
        parts = user_input.split(':')
        if len(parts) != 2:
            await update.message.reply_text("❌ Неверный формат. Пример: *5:20*", parse_mode='Markdown')
            return CHOOSING
        
        minutes = int(parts[0])
        seconds = int(parts[1])
        
        # Проверяем валидность темпа
        if minutes < 2 or seconds < 0 or seconds > 59:
            await update.message.reply_text("❌ Такой темп нереалистичен для бега")
            return CHOOSING
        
        # Рассчитываем время на 1 км в секундах
        total_seconds_per_km = minutes * 60 + seconds
        
        # Рассчитываем время для каждой дистанции
        distances = [200, 400, 600, 800, 1000]
        results = []
        
        for distance in distances:
            time_seconds = (total_seconds_per_km * distance) / 1000
            mins = int(time_seconds // 60)
            secs = int(time_seconds % 60)
            results.append(f"• *{distance} м* — {mins}:{secs:02d}")
        
        # Формируем ответ
        response = f"""
🎯 *Раскладка для темпа {minutes}:{seconds:02d} мин/км*

{chr(10).join(results)}

💡 *Подписывайся на телеграм-канал* 👉 https://t.me/run_xo
        """
        
        await update.message.reply_text(response, parse_mode='Markdown')
        return CHOOSING
        
    except ValueError:
        await update.message.reply_text("❌ Используй только цифры. Пример: *4:30*", parse_mode='Markdown')
        return CHOOSING
    except Exception as e:
        await update.message.reply_text("😬 Что-то пошло не так. Попробуй еще раз")
        return CHOOSING

async def calculate_time_for_distance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расчет времени на дистанцию по темпу"""
    try:
        # Ожидаем ввод в формате "дистанция темп", например "10 4:30"
        user_input = update.message.text.strip().split()
        
        if len(user_input) != 2:
            await update.message.reply_text("❌ Введи: *дистанция в км* и *темп*\nПример: *10 4:30*", parse_mode='Markdown')
            return CALC_TIME
        
        distance_km = float(user_input[0])
        pace_str = user_input[1]
        
        if ':' not in pace_str:
            await update.message.reply_text("❌ Темп в формате *минуты:секунды*\nПример: *5 4:30*", parse_mode='Markdown')
            return CALC_TIME
        
        # Разбираем темп
        pace_parts = pace_str.split(':')
        pace_min = int(pace_parts[0])
        pace_sec = int(pace_parts[1])
        
        # Расчет общего времени в секундах
        total_seconds = distance_km * (pace_min * 60 + pace_sec)
        
        # Конвертируем в часы:минуты:секунды
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        if hours > 0:
            time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes}:{seconds:02d}"
        
        response = f"""
⏱ *Результат на {distance_km} км*

Темп: *{pace_min}:{pace_sec:02d} мин/км*
Время: *{time_str}*

💡 *Подписывайся на телеграм-канал* 👉 https://t.me/run_xo
        """
        
        await update.message.reply_text(response, parse_mode='Markdown')
        return CHOOSING
        
    except ValueError:
        await update.message.reply_text("❌ Ошибка ввода. Пример: *10 4:30*", parse_mode='Markdown')
        return CALC_TIME

async def calculate_pace_from_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расчет темпа по времени и дистанции"""
    try:
        # Ожидаем ввод в формате "дистанция время", например "10 60" или "5 25:30"
        user_input = update.message.text.strip().split()
        
        if len(user_input) != 2:
            await update.message.reply_text("❌ Введи: *дистанция в км* и *время в минутах*\nПример: *10 60* или *5 25:30*", parse_mode='Markdown')
            return CALC_PACE
        
        distance_km = float(user_input[0])
        time_input = user_input[1]
        
        # Обрабатываем время (может быть в минутах или в формате мм:сс)
        if ':' in time_input:
            time_parts = time_input.split(':')
            total_minutes = int(time_parts[0]) + int(time_parts[1]) / 60
        else:
            total_minutes = float(time_input)
        
        # Расчет темпа в минутах на км
        pace_minutes_per_km = total_minutes / distance_km
        pace_min = int(pace_minutes_per_km)
        pace_sec = int((pace_minutes_per_km - pace_min) * 60)
        
        response = f"""
📏 *Необходимый темп на {distance_km} км*

Целевое время: *{time_input} мин*
Темп: *{pace_min}:{pace_sec:02d} мин/км*

💡 *Подписывайся на телеграм-канал* 👉 https://t.me/run_xo
        """
        
        await update.message.reply_text(response, parse_mode='Markdown')
        return CHOOSING
        
    except ValueError:
        await update.message.reply_text("❌ Ошибка ввода. Пример: *10 60* или *5 25:30*", parse_mode='Markdown')
        return CALC_PACE

async def calculate_distance_from_pace_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расчет дистанции по темпу и времени"""
    try:
        # Ожидаем ввод в формате "время темп", например "60 5:00"
        user_input = update.message.text.strip().split()
        
        if len(user_input) != 2:
            await update.message.reply_text("❌ Введи: *время в минутах* и *темп*\nПример: *60 5:00*", parse_mode='Markdown')
            return CALC_DISTANCE
        
        time_input = user_input[0]
        pace_str = user_input[1]
        
        # Обрабатываем время
        if ':' in time_input:
            time_parts = time_input.split(':')
            total_minutes = int(time_parts[0]) + int(time_parts[1]) / 60
        else:
            total_minutes = float(time_input)
        
        # Обрабатываем темп
        if ':' not in pace_str:
            await update.message.reply_text("❌ Темп в формате *минуты:секунды*\nПример: *60 5:00*", parse_mode='Markdown')
            return CALC_DISTANCE
        
        pace_parts = pace_str.split(':')
        pace_min = int(pace_parts[0])
        pace_sec = int(pace_parts[1])
        
        pace_minutes_per_km = pace_min + pace_sec / 60
        
        # Расчет дистанции
        distance_km = total_minutes / pace_minutes_per_km
        
        response = f"""
📊 *Пройденная дистанция*

Время: *{time_input} мин*
Темп: *{pace_min}:{pace_sec:02d} мин/км*
Дистанция: *{distance_km:.2f} км*

💡 *Подписывайся на телеграм-канал* 👉 https://t.me/run_xo
        """
        
        await update.message.reply_text(response, parse_mode='Markdown')
        return CALC_DISTANCE
        
    except ValueError:
        await update.message.reply_text("❌ Ошибка ввода. Пример: *60 5:00*", parse_mode='Markdown')
        return CALC_DISTANCE

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора из меню"""
    choice = update.message.text
    
    if choice == '🎯 Раскладка по темпу':
        await update.message.reply_text("Введи целевой темп (например: *4:30*):", parse_mode='Markdown')
        return CALC_PACE
    
    elif choice == '⏱ Время на дистанцию':
        await update.message.reply_text("Введи: *дистанция в км* и *темп*\nПример: *10 4:30*", parse_mode='Markdown')
        return CALC_TIME
    
    elif choice == '📏 Темп по времени':
        await update.message.reply_text("Введи: *дистанция в км* и *целевое время*\nПример: *10 60* или *5 25:30*", parse_mode='Markdown')
        return CALC_PACE
    
    elif choice == '📊 Пройденная дистанция':
        await update.message.reply_text("Введи: *время в минутах* и *темп*\nПример: *60 5:00*", parse_mode='Markdown')
        return CALC_DISTANCE
    
    else:
        await update.message.reply_text("Выбери вариант из меню ниже 👇")
        return CHOOSING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена операции"""
    await update.message.reply_text("Операция отменена. Используй меню для новых расчетов.")
    return CHOOSING

def main():
    """Запуск бота"""
    # Проверяем наличие токена
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ ОШИБКА: Установи переменную BOT_TOKEN в Render!")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)
            ],
            CALC_PACE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_pace_layout)
            ],
            CALC_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_time_for_distance)
            ],
            CALC_DISTANCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_distance_from_pace_time)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # Запускаем бота
    print("🏃‍♂️ Беговой бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
