import os
import json
from datetime import datetime, date
import telebot
from telebot import types

TOKEN = "8721843596:AAFqQoGvBG-Bks_aCW-vbcFZHPLvhBHNkik"
ADMIN_ID = 8202893335
WEB_APP_URL = "https://usdtcash24.onrender.com"
DB_FILE = "users_db.json"

bot = telebot.TeleBot(TOKEN)

# Функции работы с базой пользователей
def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "orders_count": 0}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "orders_count": 0}

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Ошибка сохранения базы:", e)

def register_user(user):
    db = load_db()
    uid = str(user.id)
    today = date.today().isoformat()
    if uid not in db["users"]:
        db["users"][uid] = {
            "first_name": user.first_name,
            "username": user.username,
            "joined": today
        }
        save_db(db)

# Команда статистики (доступна только вам)
@bot.message_handler(commands=['stats'])
def admin_stats(message):
    if message.from_user.id != ADMIN_ID:
        return

    db = load_db()
    users = db.get("users", {})
    total_users = len(users)
    today_str = date.today().isoformat()
    today_new = sum(1 for u in users.values() if u.get("joined") == today_str)

    stats_text = (
        f"📊 <b>СТАТИСТИКА БОТА USDT CASH24</b>\n\n"
        f"👥 <b>Всего пользователей в базе:</b> {total_users}\n"
        f"🆕 <b>Новых за сегодня:</b> {today_new}\n"
        f"🟢 <b>Статус сервера:</b> Онлайн (24/7)\n"
        f"🌐 <b>Адрес WebApp:</b> <code>{WEB_APP_URL}</code>"
    )
    bot.send_message(message.chat.id, stats_text, parse_mode="HTML")

# Главная команда /start
@bot.message_handler(commands=['start'])
def start(message):
    register_user(message.from_user)

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_app = types.InlineKeyboardButton(
        text="⚡️ ОТКРЫТЬ КАССУ И ОБМЕНЯТЬ ⚡️",
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    btn_support = types.InlineKeyboardButton(
        text="💬 Связь с оператором",
        url="https://t.me/usdtcash24_support"
    )
    markup.add(btn_app, btn_support)

    welcome_text = (
        f"👋 <b>Добро пожаловать в сервис обмена USDT Cash24!</b>\n\n"
        f"Официальный обменный пункт РФ и зарубежных направлений.\n\n"
        f"💳 <b>До $5,000:</b> Мгновенные выплаты на Карты / СБП / IBAN\n"
        f"🏢 <b>От $5,000:</b> Выдача наличными (USD, EUR, RUB, AED) в кассах Москва-Сити и регионах РФ.\n\n"
        f"🎁 <b>Гранд-Сезон 2026:</b> Участвуйте в розыгрыше iPhone 18 Pro Max, MacBook Pro M5 и 15,000 USDT при обмене от $300.\n\n"
        f"Нажмите кнопку ниже, чтобы рассчитать курс и создать заявку:"
    )

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="HTML")

print("Бот USDT Cash24 со статистикой запущен...")
bot.infinity_polling()
