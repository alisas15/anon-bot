from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading
import os

# Flask-сервер для Render
web_app = Flask("")

@web_app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()  # запускаем Flask отдельно

# Telegram бот
users_waiting = []
active_chats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши /search чтобы найти подписчиков.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id in active_chats:
        await update.message.reply_text("Ты уже в чате. Напиши /stop чтобы выйти.")
        return
    if users_waiting:
        partner_id = users_waiting.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        await context.bot.send_message(chat_id=user_id, text="✅ Подписчик найден!")
        await context.bot.send_message(chat_id=partner_id, text="✅ Подписчик найден!")
    else:
        users_waiting.append(user_id)
        await update.message.reply_text("⏳ Ищем новых подписчиков...")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        await context.bot.send_message(chat_id=partner_id, text="❗ Подписчик покинул чат.")
        await update.message.reply_text("🔚 Ты покинул чат.")
    elif user_id in users_waiting:
        users_waiting.remove(user_id)
        await update.message.reply_text("❌ Поиск остановлен.")
    else:
        await update.message.reply_text("Ты не в чате.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        await context.bot.send_message(chat_id=partner_id, text=update.message.text)
    else:
        await update.message.reply_text("🔍 Напиши /search чтобы начать поиск.")

# Создаём Telegram Application
app_bot = Application.builder().token("8145266061:AAGK1SJVbSJiK3HTXMIJBm1ZLEAJlbtQKGc").build()

# Обработчики
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("search", search))
app_bot.add_handler(CommandHandler("stop", stop))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# Запуск Telegram бота в отдельном потоке
def run_bot():
    app_bot.run_polling()

threading.Thread(target=run_bot).start()
