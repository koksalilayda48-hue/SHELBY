import telebot
import json
import os
import time
import random
from flask import Flask
from threading import Thread

# ================= AYARLAR =================
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 33397779
LOG_KANAL = "@bedavakampanyalarorg"

# ================= DATA =================
def load_data():
    try:
        with open("security.json", "r") as f:
            return json.load(f)
    except:
        return {"banned": [], "flood": {}, "captcha": {}}

def save_data():
    with open("security.json", "w") as f:
        json.dump(DATA, f)

DATA = load_data()

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    code = str(random.randint(1000, 9999))
    DATA["captcha"][str(user_id)] = code
    save_data()

    bot.send_message(message.chat.id, f"🔐 Doğrulama kodu: {code}\nKodu yaz.")

# ================= ANA KONTROL =================
@bot.message_handler(func=lambda m: True)
def kontrol(message):
    user_id = message.from_user.id
    text = message.text or ""

    # BAN kontrol
    if user_id in DATA["banned"]:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        return

    # CAPTCHA kontrol
    if str(user_id) in DATA["captcha"]:
        if text == DATA["captcha"][str(user_id)]:
            del DATA["captcha"][str(user_id)]
            save_data()
            bot.reply_to(message, "✅ Doğrulama başarılı!")
        else:
            bot.reply_to(message, "❌ Kod yanlış")
        return

    # ANTI FLOOD
    now = time.time()
    uid = str(user_id)

    if uid not in DATA["flood"]:
        DATA["flood"][uid] = []

    DATA["flood"][uid].append(now)
    DATA["flood"][uid] = [t for t in DATA["flood"][uid] if now - t < 5]

    if len(DATA["flood"][uid]) > 5:
        if user_id not in DATA["banned"]:
            DATA["banned"].append(user_id)
            save_data()
            bot.send_message(message.chat.id, "🚫 Flood yaptığın için banlandın")
            bot.send_message(LOG_KANAL, f"🚨 Flood ban: {user_id}")
        return

    # LINK ENGEL
    if "http" in text or "t.me" in text:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        bot.send_message(message.chat.id, "⚠️ Link yasak!")
        bot.send_message(LOG_KANAL, f"🔗 Link silindi: {user_id}")

# ================= PANEL =================
@bot.message_handler(commands=["admin"])
def panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🔨 Ban", callback_data="ban"),
        telebot.types.InlineKeyboardButton("🔓 Unban", callback_data="unban")
    )
    markup.add(
        telebot.types.InlineKeyboardButton("📊 Durum", callback_data="durum")
    )

    bot.send_message(message.chat.id, "🔧 SHELBY PANEL", reply_markup=markup)

# ================= BUTON =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == "durum":
        bot.answer_callback_query(call.id, "Bot aktif ✅")

    elif call.data == "ban":
        bot.send_message(call.message.chat.id, "Banlamak için:\n/ban ID")

    elif call.data == "unban":
        bot.send_message(call.message.chat.id, "Ban kaldırmak için:\n/unban ID")

# ================= BAN =================
@bot.message_handler(commands=["ban"])
def ban(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        uid = int(message.text.split()[1])
        if uid not in DATA["banned"]:
            DATA["banned"].append(uid)
            save_data()
            bot.reply_to(message, "✅ Banlandı")
    except:
        bot.reply_to(message, "❌ Hatalı kullanım")

# ================= UNBAN =================
@bot.message_handler(commands=["unban"])
def unban(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        uid = int(message.text.split()[1])
        if uid in DATA["banned"]:
            DATA["banned"].remove(uid)
            save_data()
            bot.reply_to(message, "✅ Ban kaldırıldı")
    except:
        bot.reply_to(message, "❌ Hatalı kullanım")

# ================= FLASK =================
app = Flask(__name__)

@app.route('/')
def home():
    return "SHELBY BOT AKTİF"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))

Thread(target=run).start()

# ================= 7/24 ÇALIŞMA =================
while True:
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=30)
    except Exception as e:
        print("Hata:", e)
        time.sleep(5)
