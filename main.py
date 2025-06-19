from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

users_waiting = []
active_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши /search чтобы найти собеседника.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in active_chats:
        await update.message.reply_text("Ты уже в чате. Напиши /stop чтобы выйти.")
        return

    if users_waiting:
        partner_id = users_waiting.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        await context.bot.send_message(chat_id=user_id, text="✅ подписчик найден!")
        await context.bot.send_message(chat_id=partner_id, text="✅ подписчик найден!")
    else:
        users_waiting.append(user_id)
        await update.message.reply_text("⏳ ищем подписчика...")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        await context.bot.send_message(chat_id=partner_id, text="❗ пользователь покинул чат.")
        await update.message.reply_text("🔚 Ты покинул чат.")
    elif user_id in users_waiting:
        users_waiting.remove(user_id)
        await update.message.reply_text("❌ поиск остановлен.")
    else:
        await update.message.reply_text("Ты не в чате.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        await context.bot.send_message(chat_id=partner_id, text=update.message.text)
    else:
        await update.message.reply_text("🔍 Напиши /search чтобы начать поиск.")

app = Application.builder().token("AAGjDEiqkmh78wqeJrRJcG9T0_c6MwLfHQI").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

app.run_polling()
