from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading
import os

app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

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
        await context.bot.send_message(chat_id=partner_id, text="❗ Собеседник покинул чат.")
        await update.message.reply_text("🔚 ты покинул чат.")
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
        await update.message.reply_text("🔍 напиши /search чтобы начать поиск.")

app_bot = Application.builder().token("7959838571:AAFl1_RS9KUkSDWSIUhzjPFEXnalGGJR-u0").build()

app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("search", search))
app_bot.add_handler(CommandHandler("stop", stop))
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

app_bot.run_polling()
