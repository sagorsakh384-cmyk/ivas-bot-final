# -*- coding: utf-8 -*-
# Importing necessary libraries
import asyncio
import re
import httpx
from bs4 import BeautifulSoup
import time
import json
import os
import traceback
import pickle
from flask import Flask
import threading
from urllib.parse import urljoin
from datetime import datetime, timedelta, timezone
import pytz
# New library added
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# Import country data
from countries import get_country_flag, get_country_by_code, get_country_by_phone

# ================= KEEP ALIVE =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive ЁЯШБ"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

# --- Configuration (Fill in your details) ---
YOUR_BOT_TOKEN = "8393297595:AAEksSfupLmn5qeBxjoGT3c9IzaJaLI6mck"  # <--- Change this

# ==================== Super Admin (hardcoded, unchangeable) ====================
SUPER_ADMIN_ID = "7095358778"
# ==============================================================================

# Old chat IDs kept for the first run
INITIAL_CHAT_IDS = ["-1003007557624"]

# admins.json ржлрж╛ржЗрж▓рзЗ рж╕ржм admin рж╕рзЗржн рж╣ржмрзЗ
ADMINS_FILE = "admins.json"

LOGIN_URL = "https://ivas.tempnum.qzz.io/login"
BASE_URL = "https://ivas.tempnum.qzz.io"
SMS_API_ENDPOINT = "https://ivas.tempnum.qzz.io/portal/sms/received/getsms"

USERNAME = "allahorpriyobanda2023@gmail.com"
PASSWORD = "P@ssword"

# Bangladesh timezone (UTC+6)
BD_TIMEZONE = pytz.timezone('Asia/Dhaka')

# Polling interval in seconds
POLLING_INTERVAL_SECONDS = 10
STATE_FILE = "processed_sms_ids.json"
CHAT_IDS_FILE = "chat_ids.json"
SESSION_FILE = "session_cookies.pkl"
STATS_FILE = "bot_stats.json"  # for /stats command

# ===================== Bot Global State =====================
BOT_PAUSED = False  # /pause ржУ /resume ржжрж┐ржпрж╝рзЗ control рж╣ржмрзЗ

# Service Keywords (for identifying service from SMS text)
SERVICE_KEYWORDS = {
    "WhatsApp": ["whatsapp", "┘И╪з╪к╪│╪з╪и", "┘И╪з╪к╪│ ╪з╪и", "рж╣рзЛржпрж╝рж╛ржЯрж╕ржЕрзНржпрж╛ржк", "рд╡реНрд╣рд╛рдЯреНрд╕рдПрдк", "╨▓╨╛╤В╤Б╨░╨┐"],
    "Telegram": ["telegram", "╪к┘К┘Д┘К╪м╪▒╪з┘Е", "╪к┘Д╪║╪▒╪з┘Е", "ржЯрзЗрж▓рж┐ржЧрзНрж░рж╛ржо", "рдЯреЗрд▓реАрдЧреНрд░рд╛рдо", "╤В╨╡╨╗╨╡╨│╤А╨░╨╝"],
    "Facebook": ["facebook", "┘Б┘К╪│╪и┘И┘Г", "ржлрзЗрж╕ржмрзБржХ", "рдлреЗрд╕рдмреБрдХ"],
    "Instagram": ["instagram", "╪з┘Ж╪│╪к┘В╪▒╪з┘Е", "╪з┘Ж╪│╪к╪м╪▒╪з┘Е", "ржЗржирж╕рзНржЯрж╛ржЧрзНрж░рж╛ржо", "рдЗрдВрд╕реНрдЯрд╛рдЧреНрд░рд╛рдо"],
    "Messenger": ["messenger", "meta", "┘Е╪з╪│┘Ж╪м╪▒", "┘Е╪│┘Ж╪м╪▒", "ржорзЗрж╕рзЗржЮрзНржЬрж╛рж░"],
    "Gmail": ["gmail"],  # Gmail BEFORE Google to avoid wrong match
    "Google": ["google", "╪м┘И╪м┘Д", "ржЧрзБржЧрж▓", "рдЧреВрдЧрд▓"],
    "YouTube": ["youtube"],
    "Twitter": ["twitter", "╪к┘И┘К╪к╪▒", "ржЯрзБржЗржЯрж╛рж░", "рдЯреНрд╡рд┐рдЯрд░"],
    "X": ["x.com", "╪е┘Г╪│"],
    "TikTok": ["tiktok", "╪к┘К┘Г ╪к┘И┘Г", "ржЯрж┐ржХржЯржХ", "рдЯрд┐рдХрдЯреЙрдХ"],
    "Snapchat": ["snapchat", "╪│┘Ж╪з╪и ╪┤╪з╪к", "╪│┘Ж╪з╪и", "рж╕рзНржирзНржпрж╛ржкржЪрзНржпрж╛ржЯ"],
    "Amazon": ["amazon"],
    "eBay": ["ebay"],
    "AliExpress": ["aliexpress"],
    "Alibaba": ["alibaba"],
    "Flipkart": ["flipkart"],
    "Netflix": ["netflix"],
    "Spotify": ["spotify"],
    "LinkedIn": ["linkedin"],
    "Microsoft": ["microsoft", "live.com"],
    "Outlook": ["outlook"],
    "Skype": ["skype"],
    "Apple": ["apple", "icloud"],
    "iCloud": ["icloud"],
    "Discord": ["discord"],
    "Signal": ["signal"],
    "Viber": ["viber"],
    "IMO": ["imo"],
    "PayPal": ["paypal"],
    "Stripe": ["stripe"],
    "Cash App": ["cash app", "square cash"],
    "Venmo": ["venmo"],
    "Zelle": ["zelle"],
    "Wise": ["wise", "transferwise"],
    "Binance": ["binance"],
    "Coinbase": ["coinbase"],
    "KuCoin": ["kucoin"],
    "Bybit": ["bybit"],
    "OKX": ["okx"],
    "Huobi": ["huobi"],
    "Kraken": ["kraken"],
    "MetaMask": ["metamask"],
    "Epic Games": ["epic games", "epicgames"],
    "PlayStation": ["playstation", "psn"],
    "Xbox": ["xbox"],
    "Steam": ["steam"],
    "Blizzard": ["blizzard"],
    "Twitch": ["twitch"],
    "Reddit": ["reddit"],
    "Yahoo": ["yahoo"],
    "ProtonMail": ["protonmail", "proton"],
    "Zoho": ["zoho"],
    "Quora": ["quora"],
    "StackOverflow": ["stackoverflow"],
    "Indeed": ["indeed"],
    "Upwork": ["upwork"],
    "Fiverr": ["fiverr"],
    "Glassdoor": ["glassdoor"],
    "Booking.com": ["booking.com", "booking"],
    "Airbnb": ["airbnb"],
    "Uber": ["uber"],
    "Lyft": ["lyft"],
    "Bolt": ["bolt"],
    "Careem": ["careem"],
    "Swiggy": ["swiggy"],
    "Zomato": ["zomato"],
    "Foodpanda": ["foodpanda"],
    "Pathao": ["pathao"],
    "McDonald's": ["mcdonalds", "mcdonald's"],
    "KFC": ["kfc"],
    "Nike": ["nike"],
    "Adidas": ["adidas"],
    "Shein": ["shein"],
    "OnlyFans": ["onlyfans"],
    "Tinder": ["tinder"],
    "Bumble": ["bumble"],
    "Grindr": ["grindr"],
    "Line": ["line app", "line.me"],
    "WeChat": ["wechat"],
    "VK": ["vk.com", "vkontakte"],
    "Unknown": []
}

# Service Emojis
SERVICE_EMOJIS = {
    "Telegram": "ЁЯУй", "WhatsApp": "ЁЯЯв", "Facebook": "ЁЯУШ", "Instagram": "ЁЯУ╕", "Messenger": "ЁЯТм",
    "Google": "ЁЯФН", "Gmail": "тЬЙя╕П", "YouTube": "тЦ╢я╕П", "Twitter": "ЁЯРж", "X": "тЭМ",
    "TikTok": "ЁЯО╡", "Snapchat": "ЁЯС╗", "Amazon": "ЁЯЫТ", "eBay": "ЁЯУж", "AliExpress": "ЁЯУж",
    "Alibaba": "ЁЯПн", "Flipkart": "ЁЯУж", "Microsoft": "ЁЯкЯ", "Outlook": "ЁЯУз", "Skype": "ЁЯУЮ",
    "Netflix": "ЁЯОм", "Spotify": "ЁЯО╢", "Apple": "ЁЯНП", "iCloud": "тШБя╕П", "PayPal": "ЁЯТ░",
    "Stripe": "ЁЯТ│", "Cash App": "ЁЯТ╡", "Venmo": "ЁЯТ╕", "Zelle": "ЁЯПж", "Wise": "ЁЯМР",
    "Binance": "ЁЯкЩ", "Coinbase": "ЁЯкЩ", "KuCoin": "ЁЯкЩ", "Bybit": "ЁЯУИ", "OKX": "ЁЯЯа",
    "Huobi": "ЁЯФе", "Kraken": "ЁЯРЩ", "MetaMask": "ЁЯжК", "Discord": "ЁЯЧия╕П", "Steam": "ЁЯОо",
    "Epic Games": "ЁЯХ╣я╕П", "PlayStation": "ЁЯОо", "Xbox": "ЁЯОо", "Twitch": "ЁЯУ║", "Reddit": "ЁЯС╜",
    "Yahoo": "ЁЯЯг", "ProtonMail": "ЁЯФР", "Zoho": "ЁЯУм", "Quora": "тЭУ", "StackOverflow": "ЁЯзСтАНЁЯТ╗",
    "LinkedIn": "ЁЯТ╝", "Indeed": "ЁЯУЛ", "Upwork": "ЁЯзСтАНЁЯТ╗", "Fiverr": "ЁЯТ╗", "Glassdoor": "ЁЯФО",
    "Airbnb": "ЁЯПа", "Booking.com": "ЁЯЫПя╕П", "Uber": "ЁЯЪЧ", "Lyft": "ЁЯЪХ", "Bolt": "ЁЯЪЦ",
    "Careem": "ЁЯЪЧ", "Swiggy": "ЁЯНФ", "Zomato": "ЁЯН╜я╕П", "Foodpanda": "ЁЯН▒",
    "McDonald's": "ЁЯНЯ", "KFC": "ЁЯНЧ", "Nike": "ЁЯСЯ", "Adidas": "ЁЯСЯ", "Shein": "ЁЯСЧ",
    "OnlyFans": "ЁЯФЮ", "Tinder": "ЁЯФе", "Bumble": "ЁЯРЭ", "Grindr": "ЁЯШИ", "Signal": "ЁЯФР",
    "Viber": "ЁЯУЮ", "Line": "ЁЯТм", "WeChat": "ЁЯТм", "VK": "ЁЯМР", "Unknown": "тЭУ"
}


# ===================== Stats Functions =====================
def load_stats() -> dict:
    if not os.path.exists(STATS_FILE):
        return {"total_sent": 0, "start_time": datetime.now(timezone.utc).isoformat()}
    try:
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {"total_sent": 0, "start_time": datetime.now(timezone.utc).isoformat()}

def save_stats(stats: dict):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)

def increment_stats(count: int = 1):
    stats = load_stats()
    stats["total_sent"] = stats.get("total_sent", 0) + count
    save_stats(stats)


# ===================== Chat ID Functions =====================
def load_chat_ids():
    if not os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, 'w') as f:
            json.dump(INITIAL_CHAT_IDS, f)
        return INITIAL_CHAT_IDS
    try:
        with open(CHAT_IDS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return INITIAL_CHAT_IDS

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, 'w') as f:
        json.dump(chat_ids, f, indent=4)


# ===================== Admin Management Functions =====================
def load_admins() -> dict:
    """admins.json рж▓рзЛржб ржХрж░рзЗред ржирж╛ ржерж╛ржХрж▓рзЗ super admin ржжрж┐ржпрж╝рзЗ рждрзИрж░рж┐ ржХрж░рзЗред"""
    default = {"super_admin": SUPER_ADMIN_ID, "admins": [SUPER_ADMIN_ID]}
    if not os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'w') as f:
            json.dump(default, f, indent=4)
        return default
    try:
        with open(ADMINS_FILE, 'r') as f:
            data = json.load(f)
        # Super admin рж╕ржмрж╕ржоржпрж╝ admins list ржП ржерж╛ржХржмрзЗ
        if SUPER_ADMIN_ID not in data.get("admins", []):
            data["admins"].append(SUPER_ADMIN_ID)
        return data
    except Exception:
        return default

def save_admins(data: dict):
    with open(ADMINS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def is_super_admin(user_id: str) -> bool:
    return user_id == SUPER_ADMIN_ID

def is_admin(user_id: str) -> bool:
    """Super admin ржУ рж╕рж╛ржзрж╛рж░ржг admin ржЙржнржпрж╝ржХрзЗ ржЪрзЗржХ ржХрж░рзЗред"""
    data = load_admins()
    return user_id in data.get("admins", [])

def get_admins_list() -> list:
    return load_admins().get("admins", [])

def promote_admin(user_id: str) -> bool:
    """ржирждрзБржи admin ржпрзЛржЧ ржХрж░рзЗред ржЗрждрж┐ржоржзрзНржпрзЗ ржерж╛ржХрж▓рзЗ False рж░рж┐ржЯрж╛рж░рзНржи ржХрж░рзЗред"""
    data = load_admins()
    if user_id in data["admins"]:
        return False
    data["admins"].append(user_id)
    save_admins(data)
    return True

def demote_admin(user_id: str) -> str:
    """Admin рж░рж┐ржорзБржн ржХрж░рзЗред super admin ржХрзЗ remove ржХрж░рж╛ ржпрж╛ржмрзЗ ржирж╛ред"""
    if user_id == SUPER_ADMIN_ID:
        return "super"  # рж╕рзБржкрж╛рж░ ржПржбржорж┐ржи рж░рж┐ржорзБржн ржХрж░рж╛ ржпрж╛ржмрзЗ ржирж╛
    data = load_admins()
    if user_id not in data["admins"]:
        return "not_found"
    data["admins"].remove(user_id)
    save_admins(data)
    return "ok"


# ===================== Telegram Command Handlers =====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    keyboard = [[
        InlineKeyboardButton("ЁЯдЦ Number Bot", url="https://t.me/yusuf_number_bot"),
        InlineKeyboardButton("ЁЯТм Discussion Group", url="https://t.me/+n5LwmSZ7neA2OGE9"),
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_super_admin(user_id):
        await update.message.reply_text(
            "ЁЯСС *Welcome Super Admin!*\n\n"
            "*ЁЯСС Super Admin Commands:*\n"
            "/promote `<user_id>` тАФ ржирждрзБржи ржПржбржорж┐ржи ржпрзЛржЧ\n"
            "/demote `<user_id>` тАФ ржПржбржорж┐ржи рж░рж┐ржорзБржн\n"
            "/admins тАФ ржПржбржорж┐ржи рж▓рж┐рж╕рзНржЯ ржжрзЗржЦрзЛ\n\n"
            "*ЁЯСе Admin Commands:*\n"
            "/add\\_chat `<chat_id>` тАФ ржирждрзБржи ржЪрзНржпрж╛ржЯ ржпрзЛржЧ\n"
            "/remove\\_chat `<chat_id>` тАФ ржЪрзНржпрж╛ржЯ рж░рж┐ржорзБржн\n"
            "/list\\_chats тАФ ржЪрзНржпрж╛ржЯ рж▓рж┐рж╕рзНржЯ\n"
            "/status тАФ ржмржЯ рж╕рзНржЯрзНржпрж╛ржЯрж╛рж╕\n"
            "/stats тАФ ржкрж░рж┐рж╕ржВржЦрзНржпрж╛ржи\n"
            "/pause тАФ ржмржЯ ржмрж┐рж░рждрж┐\n"
            "/resume тАФ ржмржЯ ржЪрж╛рж▓рзБ\n"
            "/clear\\_session тАФ рж╕рзЗрж╢ржи рж░рж┐рж╕рзЗржЯ",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    elif is_admin(user_id):
        await update.message.reply_text(
            "ЁЯСе *Welcome Admin!*\n\n"
            "*Available Commands:*\n"
            "/add\\_chat `<chat_id>` тАФ ржирждрзБржи ржЪрзНржпрж╛ржЯ ржпрзЛржЧ\n"
            "/remove\\_chat `<chat_id>` тАФ ржЪрзНржпрж╛ржЯ рж░рж┐ржорзБржн\n"
            "/list\\_chats тАФ ржЪрзНржпрж╛ржЯ рж▓рж┐рж╕рзНржЯ\n"
            "/status тАФ ржмржЯ рж╕рзНржЯрзНржпрж╛ржЯрж╛рж╕\n"
            "/stats тАФ ржкрж░рж┐рж╕ржВржЦрзНржпрж╛ржи\n"
            "/pause тАФ ржмржЯ ржмрж┐рж░рждрж┐\n"
            "/resume тАФ ржмржЯ ржЪрж╛рж▓рзБ\n"
            "/clear\\_session тАФ рж╕рзЗрж╢ржи рж░рж┐рж╕рзЗржЯ",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "тЫФ Sorry, you are not authorized to use this bot.",
            reply_markup=reply_markup
        )

# ===================== Super Admin Only Commands =====================
async def promote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not is_super_admin(user_id):
        await update.message.reply_text("тЫФ рж╢рзБржзрзБ рж╕рзБржкрж╛рж░ ржПржбржорж┐ржи ржПржЗ ржХржорж╛ржирзНржб ржмрзНржпржмрж╣рж╛рж░ ржХрж░рждрзЗ ржкрж╛рж░ржмрзЗред")
        return
    try:
        target_id = context.args[0]
        result = promote_admin(target_id)
        if result:
            await update.message.reply_text(f"тЬЕ `{target_id}` ржХрзЗ рж╕ржлрж▓ржнрж╛ржмрзЗ ржПржбржорж┐ржи ржХрж░рж╛ рж╣ржпрж╝рзЗржЫрзЗред", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"тЪая╕П `{target_id}` ржЗрждрж┐ржоржзрзНржпрзЗ ржПржбржорж┐ржи ржЖржЫрзЗред", parse_mode='Markdown')
    except IndexError:
        await update.message.reply_text("тЭМ ржлрж░ржорзНржпрж╛ржЯ ржарж┐ржХ ржирзЗржЗред рж▓рзЗржЦрзЛ: /promote <user_id>")

async def demote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not is_super_admin(user_id):
        await update.message.reply_text("тЫФ рж╢рзБржзрзБ рж╕рзБржкрж╛рж░ ржПржбржорж┐ржи ржПржЗ ржХржорж╛ржирзНржб ржмрзНржпржмрж╣рж╛рж░ ржХрж░рждрзЗ ржкрж╛рж░ржмрзЗред")
        return
    try:
        target_id = context.args[0]
        result = demote_admin(target_id)
        if result == "super":
            await update.message.reply_text("тЫФ рж╕рзБржкрж╛рж░ ржПржбржорж┐ржиржХрзЗ рж░рж┐ржорзБржн ржХрж░рж╛ ржпрж╛ржмрзЗ ржирж╛!")
        elif result == "not_found":
            await update.message.reply_text(f"ЁЯдФ `{target_id}` ржПржбржорж┐ржи рж▓рж┐рж╕рзНржЯрзЗ ржирзЗржЗред", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"тЬЕ `{target_id}` ржХрзЗ ржПржбржорж┐ржи рж▓рж┐рж╕рзНржЯ ржерзЗржХрзЗ рж╕рж░рж╛ржирзЛ рж╣ржпрж╝рзЗржЫрзЗред", parse_mode='Markdown')
    except IndexError:
        await update.message.reply_text("тЭМ ржлрж░ржорзНржпрж╛ржЯ ржарж┐ржХ ржирзЗржЗред рж▓рзЗржЦрзЛ: /demote <user_id>")

async def admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not is_super_admin(user_id):
        await update.message.reply_text("тЫФ рж╢рзБржзрзБ рж╕рзБржкрж╛рж░ ржПржбржорж┐ржи ржПржЗ ржХржорж╛ржирзНржб ржмрзНржпржмрж╣рж╛рж░ ржХрж░рждрзЗ ржкрж╛рж░ржмрзЗред")
        return
    admins = get_admins_list()
    lines = []
    for aid in admins:
        if aid == SUPER_ADMIN_ID:
            lines.append(f"ЁЯСС `{aid}` тАФ Super Admin")
        else:
            lines.append(f"ЁЯСе `{aid}` тАФ Admin")
    msg = "ЁЯУЛ *ржПржбржорж┐ржи рж▓рж┐рж╕рзНржЯ:*\n\n" + "\n".join(lines)
    await update.message.reply_text(msg, parse_mode='Markdown')

# ===================== Regular Admin Commands =====================
async def add_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("тЫФ Only admins can use this command.")
        return
    try:
        new_chat_id = context.args[0]
        chat_ids = load_chat_ids()
        if new_chat_id not in chat_ids:
            chat_ids.append(new_chat_id)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"тЬЕ Chat ID `{new_chat_id}` successfully added.", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"тЪая╕П Chat ID `{new_chat_id}` is already in the list.", parse_mode='Markdown')
    except (IndexError, ValueError):
        await update.message.reply_text("тЭМ Invalid format. Use: /add_chat <chat_id>")

async def remove_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("тЫФ Only admins can use this command.")
        return
    try:
        chat_id_to_remove = context.args[0]
        chat_ids = load_chat_ids()
        if chat_id_to_remove in chat_ids:
            chat_ids.remove(chat_id_to_remove)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"тЬЕ Chat ID `{chat_id_to_remove}` successfully removed.", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"ЁЯдФ Chat ID `{chat_id_to_remove}` was not found.", parse_mode='Markdown')
    except (IndexError, ValueError):
        await update.message.reply_text("тЭМ Invalid format. Use: /remove_chat <chat_id>")

async def list_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("тЫФ Only admins can use this command.")
        return
    chat_ids = load_chat_ids()
    if chat_ids:
        lines = "\n".join(f"тАв `{cid}`" for cid in chat_ids)
        await update.message.reply_text(f"ЁЯУЬ Registered Chat IDs:\n{lines}", parse_mode='Markdown')
    else:
        await update.message.reply_text("No chat IDs registered.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("тЫФ Only admins can use this command.")
        return
    now_bd = datetime.now(BD_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
    session_active = os.path.exists(SESSION_FILE)
    chat_count = len(load_chat_ids())
    processed_count = len(load_processed_ids())
    admin_count = len(get_admins_list())
    pause_status = "тП╕ Paused" if BOT_PAUSED else "тЦ╢я╕П Running"
    msg = (
        f"ЁЯдЦ *Bot Status*\n\n"
        f"ЁЯХР *BD Time:* `{now_bd}`\n"
        f"ЁЯФЧ *Session:* {'тЬЕ Active' if session_active else 'тЭМ Not saved'}\n"
        f"ЁЯУв *Chats:* `{chat_count}`\n"
        f"ЁЯУи *Processed SMS:* `{processed_count}`\n"
        f"ЁЯСе *Total Admins:* `{admin_count}`\n"
        f"тП▒ *Poll Interval:* `{POLLING_INTERVAL_SECONDS}s`\n"
        f"ЁЯОЫ *Bot State:* {pause_status}"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("тЫФ Only admins can use this command.")
        return
    stats = load_stats()
    total = stats.get("total_sent", 0)
    start_iso = stats.get("start_time", "N/A")
    try:
        start_dt = datetime.fromisoformat(start_iso).astimezone(BD_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        start_dt = start_iso
    msg = (
        f"ЁЯУК *SMS Statistics*\n\n"
        f"ЁЯУи *Total SMS Forwarded:* `{total}`\n"
        f"ЁЯЪА *Bot Started:* `{start_dt}`"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_PAUSED
    user_id = str(update.message.from_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("тЫФ Only admins can use this command.")
        return
    if BOT_PAUSED:
        await update.message.reply_text("тЪая╕П Bot is already paused.\nUse /resume to start again.")
    else:
        BOT_PAUSED = True
        await update.message.reply_text("тП╕ Bot paused! SMS checking stopped.\nUse /resume to restart.")

async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_PAUSED
    user_id = str(update.message.from_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("тЫФ Only admins can use this command.")
        return
    if not BOT_PAUSED:
        await update.message.reply_text("тЬЕ Bot is already running!")
    else:
        BOT_PAUSED = False
        await update.message.reply_text("тЦ╢я╕П Bot resumed! SMS checking is active again.")

async def clear_session_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not is_admin(user_id):
        await update.message.reply_text("тЫФ Only admins can use this command.")
        return
    clear_session()
    await update.message.reply_text("ЁЯЧСя╕П Session cleared! Bot will re-login on next check.")


# ===================== Core Helper Functions =====================
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

# ===================== Number Masking (тУОтУДтУК style) =====================
def mask_phone_number(phone: str) -> str:
    """
    ржорж╛ржЭрзЗрж░ ржарж┐ржХ рзйржЯрж╛ digit hide ржХрж░рзЗ тУОтУДтУК ржжрж┐ржпрж╝рзЗ replace ржХрж░рзЗред
    Example: 9779817613  тЖТ 9779тУОтУДтУК613
             8801712345678 тЖТ 88017тУОтУДтУК5678
    Logic: ржкрзНрж░ржержо (total-6) digit + тУОтУДтУК + рж╢рзЗрж╖ рзй digit
    """
    digits_only = re.sub(r'\D', '', phone)
    total = len(digits_only)

    if total <= 7:
        return phone  # ржЦрзБржм ржЫрзЛржЯ, mask ржХрж░ржмрзЛ ржирж╛

    show_start = total - 6   # рж╢рзЗрж╖ рзм digit ржПрж░ ржЖржЧ ржкрж░рзНржпржирзНржд ржжрзЗржЦрж╛ржмрзЗ
    # ржХрж┐ржирзНрждрзБ minimum рзк digit рж╢рзБрж░рзБрждрзЗ ржжрзЗржЦрж╛рждрзЗ рж╣ржмрзЗ
    show_start = max(show_start, 4)

    start_part = digits_only[:show_start]
    end_part   = digits_only[show_start + 3:]  # рзйржЯрж╛ skip ржХрж░рзЗ ржмрж╛ржХрж┐ржЯрж╛

    return f"{start_part}тУОтУДтУК{end_part}"

def load_processed_ids() -> set:
    if not os.path.exists(STATE_FILE):
        return set()
    try:
        with open(STATE_FILE, 'r') as f:
            return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError):
        return set()

def save_processed_ids(processed_ids: set):
    """Save the full set at once (more efficient than one-by-one)."""
    with open(STATE_FILE, 'w') as f:
        json.dump(list(processed_ids), f)

def save_processed_id(sms_id: str):
    """Save a single new ID (backward compat)."""
    processed_ids = load_processed_ids()
    processed_ids.add(sms_id)
    save_processed_ids(processed_ids)

def detect_service(sms_text: str) -> str:
    """Detect service name from SMS text."""
    lower = sms_text.lower()
    for service_name, keywords in SERVICE_KEYWORDS.items():
        if service_name == "Unknown":
            continue
        if any(kw in lower for kw in keywords):
            return service_name
    return "Unknown"

def extract_otp(sms_text: str) -> str:
    """Extract OTP/verification code from SMS text."""
    # Try XXX-XXX format first (e.g. WhatsApp)
    match = re.search(r'\b(\d{3}[-\s]\d{3})\b', sms_text)
    if match:
        return match.group(1)
    # Try 4тАУ8 digit number
    match = re.search(r'\b(\d{4,8})\b', sms_text)
    if match:
        return match.group(1)
    return "N/A"


# ===================== Session Management =====================
def save_session(cookies):
    try:
        cookie_list = [(cookie.name, cookie.value, cookie.domain, cookie.path)
                       for cookie in cookies.jar]
        with open(SESSION_FILE, 'wb') as f:
            pickle.dump(cookie_list, f)
        print("ЁЯТ╛ Session saved successfully!")
    except Exception as e:
        print(f"тЪая╕П Failed to save session: {e}")

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, 'rb') as f:
            cookie_list = pickle.load(f)
        print("ЁЯФУ Loaded saved session!")
        return {name: value for name, value, domain, path in cookie_list}
    except Exception as e:
        print(f"тЪая╕П Failed to load session: {e}")
        return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("ЁЯЧСя╕П Session cleared!")


# ===================== SMS Fetching =====================
async def fetch_sms_from_api(client: httpx.AsyncClient, headers: dict, csrf_token: str):
    all_messages = []
    try:
        today = datetime.now(timezone.utc)
        start_date = today - timedelta(days=1)
        from_date_str = start_date.strftime('%m/%d/%Y')
        to_date_str = today.strftime('%m/%d/%Y')

        first_payload = {'from': from_date_str, 'to': to_date_str, '_token': csrf_token}
        summary_response = await client.post(SMS_API_ENDPOINT, headers=headers, data=first_payload)
        summary_response.raise_for_status()
        summary_soup = BeautifulSoup(summary_response.text, 'html.parser')
        group_divs = summary_soup.find_all('div', {'class': 'pointer'})
        if not group_divs:
            return []

        group_ids = [
            re.search(r"getDetials\('(.+?)'\)", div.get('onclick', '')).group(1)
            for div in group_divs
            if re.search(r"getDetials\('(.+?)'\)", div.get('onclick', ''))
        ]
        numbers_url = urljoin(BASE_URL, "portal/sms/received/getsms/number")
        sms_url = urljoin(BASE_URL, "portal/sms/received/getsms/number/sms")

        for group_id in group_ids:
            numbers_payload = {'start': from_date_str, 'end': to_date_str, 'range': group_id, '_token': csrf_token}
            numbers_response = await client.post(numbers_url, headers=headers, data=numbers_payload)
            numbers_soup = BeautifulSoup(numbers_response.text, 'html.parser')
            number_divs = numbers_soup.select("div[onclick*='getDetialsNumber']")
            if not number_divs:
                continue
            phone_numbers = [div.text.strip() for div in number_divs]

            for phone_number in phone_numbers:
                sms_payload = {
                    'start': from_date_str, 'end': to_date_str,
                    'Number': phone_number, 'Range': group_id, '_token': csrf_token
                }
                sms_response = await client.post(sms_url, headers=headers, data=sms_payload)
                sms_soup = BeautifulSoup(sms_response.text, 'html.parser')
                final_sms_cards = sms_soup.find_all('div', class_='card-body')

                for card in final_sms_cards:
                    sms_text_p = card.find('p', class_='mb-0')
                    if not sms_text_p:
                        continue
                    sms_text = sms_text_p.get_text(separator='\n').strip()

                    # Try to get actual SMS timestamp from card
                    date_str = None
                    time_tag = card.find('small') or card.find('span', class_=re.compile(r'time|date'))
                    if time_tag:
                        raw_time = time_tag.get_text(strip=True)
                        for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S'):
                            try:
                                parsed = datetime.strptime(raw_time, fmt).replace(tzinfo=timezone.utc)
                                bd_time = parsed.astimezone(BD_TIMEZONE)
                                date_str = bd_time.strftime('%Y-%m-%d %H:%M:%S')
                                break
                            except ValueError:
                                pass
                    if not date_str:
                        # Fallback: use current BD time
                        date_str = datetime.now(timezone.utc).astimezone(BD_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')

                    # Country detection тАФ try phone number first, then group_id
                    country_name, flag = get_country_by_phone(phone_number)
                    if country_name == 'Unknown':
                        # Try group_id as country name
                        country_name_raw = re.match(r'([a-zA-Z\s/]+)', group_id)
                        if country_name_raw:
                            country_name = country_name_raw.group(1).strip().upper()
                        else:
                            country_name = group_id.strip().upper()
                        flag = get_country_flag(country_name)

                    service = detect_service(sms_text)
                    code = extract_otp(sms_text)
                    unique_id = f"{phone_number}-{sms_text}"

                    all_messages.append({
                        "id": unique_id,
                        "time": date_str,
                        "number": phone_number,
                        "country": country_name,
                        "flag": flag,
                        "service": service,
                        "code": code,
                        "full_sms": sms_text
                    })

        return list(reversed(all_messages))

    except httpx.RequestError as e:
        print(f"тЭМ Network issue (httpx): {e}")
        return []
    except Exception as e:
        print(f"тЭМ Error fetching/processing API data: {e}")
        traceback.print_exc()
        return []


async def send_telegram_message(context: ContextTypes.DEFAULT_TYPE, chat_id: str, message_data: dict):
    try:
        time_str = message_data.get("time", "N/A")
        number_str = message_data.get("number", "N/A")
        masked_number = mask_phone_number(number_str)   # тУОтУДтУК masking
        country_name = message_data.get("country", "N/A")
        flag_emoji = message_data.get("flag", "ЁЯП┤тАНтШая╕П")
        service_name = message_data.get("service", "N/A")
        code_str = message_data.get("code", "N/A")
        full_sms_text = message_data.get("full_sms", "N/A")
        service_emoji = SERVICE_EMOJIS.get(service_name, "тЭУ")

        full_message = (
            f"ЁЯФФ *New OTP Received*\n\n"
            f"ЁЯУЮ *Number:* `{escape_markdown(masked_number)}`\n"
            f"ЁЯФС *Code:* `{escape_markdown(code_str)}`\n"
            f"ЁЯПЖ *Service:* {service_emoji} {escape_markdown(service_name)}\n"
            f"ЁЯМО *Country:* {escape_markdown(country_name)} {flag_emoji}\n"
            f"тП│ *Time:* `{escape_markdown(time_str)}`\n\n"
            f"ЁЯТм *Message:*\n"
            f"```\n{full_sms_text}\n```"
        )

        # OTP message ржПрж░ ржирж┐ржЪрзЗ buttons + developer рж▓рж┐ржЩрзНржХ
        keyboard = [
            [
                InlineKeyboardButton("ЁЯдЦ Number Bot", url="https://t.me/Ah_method_number_bot"),
                InlineKeyboardButton("ЁЯТм Number Channel", url="https://t.me/blackotpnum"),
            ],
            [
                InlineKeyboardButton("ЁЯЫа Developer", url="https://t.me/sadhin8miya"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=chat_id,
            text=full_message,
            parse_mode='MarkdownV2',
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"тЭМ Error sending message to chat ID {chat_id}: {e}")


async def notify_admins(context: ContextTypes.DEFAULT_TYPE, message: str):
    """рж╕ржм admin ржХрзЗ alert ржкрж╛ржарж╛ржпрж╝ред"""
    for admin_id in get_admins_list():
        try:
            await context.bot.send_message(chat_id=admin_id, text=message)
        except Exception as e:
            print(f"тЪая╕П Could not notify admin {admin_id}: {e}")


# ===================== Main Polling Job =====================
async def check_sms_job(context: ContextTypes.DEFAULT_TYPE):
    global BOT_PAUSED

    # Pause рж╣рж▓рзЗ ржХрж┐ржЫрзБ ржХрж░ржмрзЗ ржирж╛
    if BOT_PAUSED:
        print(f"[{datetime.now(BD_TIMEZONE).strftime('%H:%M:%S')}] тП╕ Bot is paused. Skipping check.")
        return

    print(f"\n--- [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] Checking for new messages ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'
    }

    saved_cookies = load_session()

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True, cookies=saved_cookies) as client:
        try:
            csrf_token = None

            if saved_cookies:
                print("ЁЯФУ Using saved session...")
                try:
                    sms_page = await client.get(BASE_URL + "/portal/sms/received", headers=headers)
                    if "login" not in str(sms_page.url):
                        print("тЬЕ Session still valid!")
                        soup = BeautifulSoup(sms_page.text, 'html.parser')
                        csrf_token_meta = soup.find('meta', {'name': 'csrf-token'})
                        if csrf_token_meta:
                            csrf_token = csrf_token_meta.get('content')
                            headers['Referer'] = str(sms_page.url)
                            print("ЁЯФС CSRF token obtained!")
                        else:
                            print("тЪая╕П CSRF token not found on page")
                            clear_session()
                    else:
                        print("тЪая╕П Session expired")
                        clear_session()
                except Exception as e:
                    print(f"тЪая╕П Session check failed: {e}")
                    clear_session()

            if not csrf_token:
                print("тД╣я╕П Logging in...")
                login_page_res = await client.get(LOGIN_URL, headers=headers)
                soup = BeautifulSoup(login_page_res.text, 'html.parser')
                token_input = soup.find('input', {'name': '_token'})
                login_data = {'email': USERNAME, 'password': PASSWORD}
                if token_input:
                    login_data['_token'] = token_input['value']

                login_res = await client.post(LOGIN_URL, data=login_data, headers=headers)

                if "login" in str(login_res.url):
                    print("тЭМ Login failed. Check username/password.")
                    await notify_admins(context, "тЭМ Bot login failed! Please check your username/password.")
                    clear_session()
                    return

                print("тЬЕ Login successful!")
                save_session(client.cookies)

                dashboard_soup = BeautifulSoup(login_res.text, 'html.parser')
                csrf_token_meta = dashboard_soup.find('meta', {'name': 'csrf-token'})
                if not csrf_token_meta:
                    print("тЭМ CSRF token not found after login.")
                    return
                csrf_token = csrf_token_meta.get('content')
                headers['Referer'] = str(login_res.url)

            messages = await fetch_sms_from_api(client, headers, csrf_token)
            if not messages:
                print("тЬФя╕П No new messages found.")
                return

            # Load once, save once тАФ efficient
            processed_ids = load_processed_ids()
            chat_ids_to_send = load_chat_ids()
            new_messages_found = 0
            newly_processed = set()

            for msg in messages:
                if msg["id"] not in processed_ids:
                    new_messages_found += 1
                    print(f"тЬФя╕П New message from: {msg['number']} [{msg['service']}]")
                    for chat_id in chat_ids_to_send:
                        await send_telegram_message(context, chat_id, msg)
                    newly_processed.add(msg["id"])

            if newly_processed:
                processed_ids.update(newly_processed)
                save_processed_ids(processed_ids)
                increment_stats(new_messages_found)
                print(f"тЬЕ Total {new_messages_found} new messages sent to Telegram.")

        except httpx.RequestError as e:
            print(f"тЭМ Network issue: {e}")
            clear_session()
        except Exception as e:
            print(f"тЭМ Error: {e}")
            traceback.print_exc()
            clear_session()


# ===================== Entry Point =====================
def main():
    keep_alive()
    print("ЁЯЪА iVasms to Telegram Bot is starting...")

    # admins.json initialize ржХрж░рзЛ (ржирж╛ ржерж╛ржХрж▓рзЗ рждрзИрж░рж┐ рж╣ржмрзЗ)
    load_admins()

    # Initialize stats if first run
    if not os.path.exists(STATS_FILE):
        save_stats({"total_sent": 0, "start_time": datetime.now(timezone.utc).isoformat()})

    application = Application.builder().token(YOUR_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))

    # Super Admin only
    application.add_handler(CommandHandler("promote", promote_command))
    application.add_handler(CommandHandler("demote", demote_command))
    application.add_handler(CommandHandler("admins", admins_command))

    # Regular Admin
    application.add_handler(CommandHandler("add_chat", add_chat_command))
    application.add_handler(CommandHandler("remove_chat", remove_chat_command))
    application.add_handler(CommandHandler("list_chats", list_chats_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("pause", pause_command))
    application.add_handler(CommandHandler("resume", resume_command))
    application.add_handler(CommandHandler("clear_session", clear_session_command))

    job_queue = application.job_queue
    job_queue.run_repeating(
        check_sms_job,
        interval=POLLING_INTERVAL_SECONDS,
        first=1,
    )

    print(f"ЁЯЪА Checking for new messages every {POLLING_INTERVAL_SECONDS} seconds.")
    print("ЁЯдЦ Bot is now online. Ready to listen for commands.")
    print("тЪая╕П Press Ctrl+C to stop the bot.")

    application.run_polling()


if __name__ == "__main__":
    main()
