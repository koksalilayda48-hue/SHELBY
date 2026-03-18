import telebot
import json
import os
from flask import Flask
from threading import Thread

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

KANAL = "@bedavakampanyalarorg"
ADMIN_ID = 33397779

# Veri dosyası
def load_data():
    try:
        with open("security.json", "r") as f:
            return json.load(f)
    except:
        return {"banned": []}

def save_data():
    with open("security.json", "w") as f:
        json.dump(DATA, f)

DATA = load_data()

# Kanal kontrol
def kanalda_mi(user_id):
    try:
        uye = bot.get_chat_member(KANAL, user_id)
        return uye.status in ["member","administrator","creator"]
    except:
        return False

# /start
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    if not kanalda_mi(user_id):
        bot.reply_to(message,"Kullanmak için kanala katıl!")
        return
    bot.reply_to(message,"SHELBY BOT AKTİF ✅")

# Admin komutları
@bot.message_handler(commands=["ban"])
def ban(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id not in DATA["banned"]:
            DATA["banned"].append(user_id)
            save_data()
            bot.reply_to(message,f"{user_id} yasaklandı.")
    except:
        bot.reply_to(message,"Hatalı kullanım")

@bot.message_handler(commands=["unban"])
def unban(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in DATA["banned"]:
            DATA["banned"].remove(user_id)
            save_data()
            bot.reply_to(message,f"{user_id} yasaktan kaldırıldı.")
    except:
        bot.reply_to(message,"Hatalı kullanım")

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id,"🔧 SHELBY PANEL\n\n/ban USERID\n/unban USERID")

# Mesaj filtresi
@bot.message_handler(func=lambda m: True)
def check_message(message):
    if message.from_user.id in DATA["banned"]:
        bot.delete_message(message.chat.id, message.message_id)
        return
    yasakli = ["link","spam"]
    if any(word in message.text.lower() for word in yasakli):
        bot.reply_to(message,"⚠️ Yasaklı içerik tespit edildi!")

# Flask server (Render için)
app = Flask('')

@app.route('/')
def home():
    return "SHELBY BOT AKTİF"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",3000)))

Thread(target=run).start()

# Başlat
bot.infinity_polling()
