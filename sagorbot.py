# -*- coding: utf-8 -*-
import asyncio
import re
import httpx
from bs4 import BeautifulSoup
import json
import os
import traceback
import pickle
from flask import Flask
import threading
from datetime import datetime, timezone
import socketio
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

# ================= KEEP ALIVE =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive 😁"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

# --- Configuration ---
YOUR_BOT_TOKEN = "8393297595:AAEksSfupLmn5qeBxjoGT3c9IzaJaLI6mck"
ADMIN_CHAT_IDS = ["7095358778"]
INITIAL_CHAT_IDS = ["-1003007557624"]

LOGIN_URL = "https://ivas.tempnum.qzz.io/login"
BASE_URL = "https://ivas.tempnum.qzz.io"
LIVE_SMS_URL = "https://ivas.tempnum.qzz.io/portal/live/my_sms"
SOCKET_SERVER = "https://ivas.tempnum.qzz.io"  # ⚡ Socket.IO server — subdomain

USERNAME = "sagorsakh8@gmail.com"
PASSWORD = "61453812Sa@"

STATE_FILE = "processed_sms_ids.json"
CHAT_IDS_FILE = "chat_ids.json"
SESSION_FILE = "session_cookies.pkl"

# ✅ পৃথিবীর সকল দেশের কোড
COUNTRY_CODES = {
    '20': ('Egypt', '🇪🇬'), '212': ('Morocco', '🇲🇦'), '213': ('Algeria', '🇩🇿'),
    '216': ('Tunisia', '🇹🇳'), '218': ('Libya', '🇱🇾'), '220': ('Gambia', '🇬🇲'),
    '221': ('Senegal', '🇸🇳'), '222': ('Mauritania', '🇲🇷'), '223': ('Mali', '🇲🇱'),
    '224': ('Guinea', '🇬🇳'), '225': ("Côte d'Ivoire", '🇨🇮'), '226': ('Burkina Faso', '🇧🇫'),
    '227': ('Niger', '🇳🇪'), '228': ('Togo', '🇹🇬'), '229': ('Benin', '🇧🇯'),
    '230': ('Mauritius', '🇲🇺'), '231': ('Liberia', '🇱🇷'), '232': ('Sierra Leone', '🇸🇱'),
    '233': ('Ghana', '🇬🇭'), '234': ('Nigeria', '🇳🇬'), '235': ('Chad', '🇹🇩'),
    '236': ('Central African Republic', '🇨🇫'), '237': ('Cameroon', '🇨🇲'),
    '238': ('Cape Verde', '🇨🇻'), '239': ('São Tomé and Príncipe', '🇸🇹'),
    '240': ('Equatorial Guinea', '🇬🇶'), '241': ('Gabon', '🇬🇦'),
    '242': ('Republic of the Congo', '🇨🇬'), '243': ('DR Congo', '🇨🇩'),
    '244': ('Angola', '🇦🇴'), '245': ('Guinea-Bissau', '🇬🇼'),
    '248': ('Seychelles', '🇸🇨'), '249': ('Sudan', '🇸🇩'), '250': ('Rwanda', '🇷🇼'),
    '251': ('Ethiopia', '🇪🇹'), '252': ('Somalia', '🇸🇴'), '253': ('Djibouti', '🇩🇯'),
    '254': ('Kenya', '🇰🇪'), '255': ('Tanzania', '🇹🇿'), '256': ('Uganda', '🇺🇬'),
    '257': ('Burundi', '🇧🇮'), '258': ('Mozambique', '🇲🇿'), '260': ('Zambia', '🇿🇲'),
    '261': ('Madagascar', '🇲🇬'), '263': ('Zimbabwe', '🇿🇼'), '264': ('Namibia', '🇳🇦'),
    '265': ('Malawi', '🇲🇼'), '266': ('Lesotho', '🇱🇸'), '267': ('Botswana', '🇧🇼'),
    '268': ('Eswatini', '🇸🇿'), '269': ('Comoros', '🇰🇲'), '27': ('South Africa', '🇿🇦'),
    '291': ('Eritrea', '🇪🇷'), '30': ('Greece', '🇬🇷'), '31': ('Netherlands', '🇳🇱'),
    '32': ('Belgium', '🇧🇪'), '33': ('France', '🇫🇷'), '34': ('Spain', '🇪🇸'),
    '350': ('Gibraltar', '🇬🇮'), '351': ('Portugal', '🇵🇹'), '352': ('Luxembourg', '🇱🇺'),
    '353': ('Ireland', '🇮🇪'), '354': ('Iceland', '🇮🇸'), '355': ('Albania', '🇦🇱'),
    '356': ('Malta', '🇲🇹'), '357': ('Cyprus', '🇨🇾'), '358': ('Finland', '🇫🇮'),
    '359': ('Bulgaria', '🇧🇬'), '36': ('Hungary', '🇭🇺'), '370': ('Lithuania', '🇱🇹'),
    '371': ('Latvia', '🇱🇻'), '372': ('Estonia', '🇪🇪'), '373': ('Moldova', '🇲🇩'),
    '374': ('Armenia', '🇦🇲'), '375': ('Belarus', '🇧🇾'), '376': ('Andorra', '🇦🇩'),
    '377': ('Monaco', '🇲🇨'), '380': ('Ukraine', '🇺🇦'), '381': ('Serbia', '🇷🇸'),
    '382': ('Montenegro', '🇲🇪'), '383': ('Kosovo', '🇽🇰'), '385': ('Croatia', '🇭🇷'),
    '386': ('Slovenia', '🇸🇮'), '387': ('Bosnia and Herzegovina', '🇧🇦'),
    '389': ('North Macedonia', '🇲🇰'), '39': ('Italy', '🇮🇹'), '40': ('Romania', '🇷🇴'),
    '41': ('Switzerland', '🇨🇭'), '420': ('Czech Republic', '🇨🇿'), '421': ('Slovakia', '🇸🇰'),
    '423': ('Liechtenstein', '🇱🇮'), '43': ('Austria', '🇦🇹'), '44': ('United Kingdom', '🇬🇧'),
    '45': ('Denmark', '🇩🇰'), '46': ('Sweden', '🇸🇪'), '47': ('Norway', '🇳🇴'),
    '48': ('Poland', '🇵🇱'), '49': ('Germany', '🇩🇪'),
    '1': ('USA/Canada', '🇺🇸'), '52': ('Mexico', '🇲🇽'), '53': ('Cuba', '🇨🇺'),
    '54': ('Argentina', '🇦🇷'), '55': ('Brazil', '🇧🇷'), '56': ('Chile', '🇨🇱'),
    '57': ('Colombia', '🇨🇴'), '58': ('Venezuela', '🇻🇪'), '591': ('Bolivia', '🇧🇴'),
    '592': ('Guyana', '🇬🇾'), '593': ('Ecuador', '🇪🇨'), '595': ('Paraguay', '🇵🇾'),
    '597': ('Suriname', '🇸🇷'), '598': ('Uruguay', '🇺🇾'), '501': ('Belize', '🇧🇿'),
    '502': ('Guatemala', '🇬🇹'), '503': ('El Salvador', '🇸🇻'), '504': ('Honduras', '🇭🇳'),
    '505': ('Nicaragua', '🇳🇮'), '506': ('Costa Rica', '🇨🇷'), '507': ('Panama', '🇵🇦'),
    '509': ('Haiti', '🇭🇹'), '1242': ('Bahamas', '🇧🇸'), '1246': ('Barbados', '🇧🇧'),
    '1345': ('Cayman Islands', '🇰🇾'), '1441': ('Bermuda', '🇧🇲'),
    '1473': ('Grenada', '🇬🇩'), '1758': ('Saint Lucia', '🇱🇨'),
    '1767': ('Dominica', '🇩🇲'), '1784': ('Saint Vincent', '🇻🇨'),
    '1787': ('Puerto Rico', '🇵🇷'), '1809': ('Dominican Republic', '🇩🇴'),
    '1868': ('Trinidad and Tobago', '🇹🇹'), '1876': ('Jamaica', '🇯🇲'),
    '7': ('Russia', '🇷🇺'), '77': ('Kazakhstan', '🇰🇿'), '81': ('Japan', '🇯🇵'),
    '82': ('South Korea', '🇰🇷'), '84': ('Vietnam', '🇻🇳'), '850': ('North Korea', '🇰🇵'),
    '852': ('Hong Kong', '🇭🇰'), '853': ('Macau', '🇲🇴'), '855': ('Cambodia', '🇰🇭'),
    '856': ('Laos', '🇱🇦'), '86': ('China', '🇨🇳'), '880': ('Bangladesh', '🇧🇩'),
    '886': ('Taiwan', '🇹🇼'), '90': ('Turkey', '🇹🇷'), '91': ('India', '🇮🇳'),
    '92': ('Pakistan', '🇵🇰'), '93': ('Afghanistan', '🇦🇫'), '94': ('Sri Lanka', '🇱🇰'),
    '95': ('Myanmar', '🇲🇲'), '960': ('Maldives', '🇲🇻'), '961': ('Lebanon', '🇱🇧'),
    '962': ('Jordan', '🇯🇴'), '963': ('Syria', '🇸🇾'), '964': ('Iraq', '🇮🇶'),
    '965': ('Kuwait', '🇰🇼'), '966': ('Saudi Arabia', '🇸🇦'), '967': ('Yemen', '🇾🇪'),
    '968': ('Oman', '🇴🇲'), '970': ('Palestine', '🇵🇸'), '971': ('UAE', '🇦🇪'),
    '972': ('Israel', '🇮🇱'), '973': ('Bahrain', '🇧🇭'), '974': ('Qatar', '🇶🇦'),
    '975': ('Bhutan', '🇧🇹'), '976': ('Mongolia', '🇲🇳'), '977': ('Nepal', '🇳🇵'),
    '98': ('Iran', '🇮🇷'), '992': ('Tajikistan', '🇹🇯'), '993': ('Turkmenistan', '🇹🇲'),
    '994': ('Azerbaijan', '🇦🇿'), '995': ('Georgia', '🇬🇪'), '996': ('Kyrgyzstan', '🇰🇬'),
    '998': ('Uzbekistan', '🇺🇿'), '60': ('Malaysia', '🇲🇾'), '61': ('Australia', '🇦🇺'),
    '62': ('Indonesia', '🇮🇩'), '63': ('Philippines', '🇵🇭'), '64': ('New Zealand', '🇳🇿'),
    '65': ('Singapore', '🇸🇬'), '66': ('Thailand', '🇹🇭'), '670': ('East Timor', '🇹🇱'),
    '673': ('Brunei', '🇧🇳'), '675': ('Papua New Guinea', '🇵🇬'), '679': ('Fiji', '🇫🇯'),
    '685': ('Samoa', '🇼🇸'), '686': ('Kiribati', '🇰🇮'), '691': ('Micronesia', '🇫🇲'),
}

# দেশের ISO code থেকে পতাকা বের করা
ISO_TO_FLAG = {
    'af': '🇦🇫', 'al': '🇦🇱', 'dz': '🇩🇿', 'ad': '🇦🇩', 'ao': '🇦🇴', 'ag': '🇦🇬',
    'ar': '🇦🇷', 'am': '🇦🇲', 'au': '🇦🇺', 'at': '🇦🇹', 'az': '🇦🇿', 'bs': '🇧🇸',
    'bh': '🇧🇭', 'bd': '🇧🇩', 'bb': '🇧🇧', 'by': '🇧🇾', 'be': '🇧🇪', 'bz': '🇧🇿',
    'bj': '🇧🇯', 'bt': '🇧🇹', 'bo': '🇧🇴', 'ba': '🇧🇦', 'bw': '🇧🇼', 'br': '🇧🇷',
    'bn': '🇧🇳', 'bg': '🇧🇬', 'bf': '🇧🇫', 'bi': '🇧🇮', 'cv': '🇨🇻', 'kh': '🇰🇭',
    'cm': '🇨🇲', 'ca': '🇨🇦', 'cf': '🇨🇫', 'td': '🇹🇩', 'cl': '🇨🇱', 'cn': '🇨🇳',
    'co': '🇨🇴', 'km': '🇰🇲', 'cg': '🇨🇬', 'cd': '🇨🇩', 'cr': '🇨🇷', 'ci': '🇨🇮',
    'hr': '🇭🇷', 'cu': '🇨🇺', 'cy': '🇨🇾', 'cz': '🇨🇿', 'dk': '🇩🇰', 'dj': '🇩🇯',
    'dm': '🇩🇲', 'do': '🇩🇴', 'ec': '🇪🇨', 'eg': '🇪🇬', 'sv': '🇸🇻', 'gq': '🇬🇶',
    'er': '🇪🇷', 'ee': '🇪🇪', 'sz': '🇸🇿', 'et': '🇪🇹', 'fj': '🇫🇯', 'fi': '🇫🇮',
    'fr': '🇫🇷', 'ga': '🇬🇦', 'gm': '🇬🇲', 'ge': '🇬🇪', 'de': '🇩🇪', 'gh': '🇬🇭',
    'gr': '🇬🇷', 'gd': '🇬🇩', 'gt': '🇬🇹', 'gn': '🇬🇳', 'gw': '🇬🇼', 'gy': '🇬🇾',
    'ht': '🇭🇹', 'hn': '🇭🇳', 'hk': '🇭🇰', 'hu': '🇭🇺', 'is': '🇮🇸', 'in': '🇮🇳',
    'id': '🇮🇩', 'ir': '🇮🇷', 'iq': '🇮🇶', 'ie': '🇮🇪', 'il': '🇮🇱', 'it': '🇮🇹',
    'jm': '🇯🇲', 'jp': '🇯🇵', 'jo': '🇯🇴', 'kz': '🇰🇿', 'ke': '🇰🇪', 'ki': '🇰🇮',
    'kp': '🇰🇵', 'kr': '🇰🇷', 'kw': '🇰🇼', 'kg': '🇰🇬', 'la': '🇱🇦', 'lv': '🇱🇻',
    'lb': '🇱🇧', 'ls': '🇱🇸', 'lr': '🇱🇷', 'ly': '🇱🇾', 'li': '🇱🇮', 'lt': '🇱🇹',
    'lu': '🇱🇺', 'mo': '🇲🇴', 'mg': '🇲🇬', 'mw': '🇲🇼', 'my': '🇲🇾', 'mv': '🇲🇻',
    'ml': '🇲🇱', 'mt': '🇲🇹', 'mh': '🇲🇭', 'mr': '🇲🇷', 'mu': '🇲🇺', 'mx': '🇲🇽',
    'fm': '🇫🇲', 'md': '🇲🇩', 'mc': '🇲🇨', 'mn': '🇲🇳', 'me': '🇲🇪', 'ma': '🇲🇦',
    'mz': '🇲🇿', 'mm': '🇲🇲', 'na': '🇳🇦', 'nr': '🇳🇷', 'np': '🇳🇵', 'nl': '🇳🇱',
    'nz': '🇳🇿', 'ni': '🇳🇮', 'ne': '🇳🇪', 'ng': '🇳🇬', 'mk': '🇲🇰', 'no': '🇳🇴',
    'om': '🇴🇲', 'pk': '🇵🇰', 'pw': '🇵🇼', 'pa': '🇵🇦', 'pg': '🇵🇬', 'py': '🇵🇾',
    'pe': '🇵🇪', 'ph': '🇵🇭', 'pl': '🇵🇱', 'pt': '🇵🇹', 'qa': '🇶🇦', 'ro': '🇷🇴',
    'ru': '🇷🇺', 'rw': '🇷🇼', 'kn': '🇰🇳', 'lc': '🇱🇨', 'vc': '🇻🇨', 'ws': '🇼🇸',
    'sm': '🇸🇲', 'st': '🇸🇹', 'sa': '🇸🇦', 'sn': '🇸🇳', 'rs': '🇷🇸', 'sc': '🇸🇨',
    'sl': '🇸🇱', 'sg': '🇸🇬', 'sk': '🇸🇰', 'si': '🇸🇮', 'sb': '🇸🇧', 'so': '🇸🇴',
    'za': '🇿🇦', 'ss': '🇸🇸', 'es': '🇪🇸', 'lk': '🇱🇰', 'sd': '🇸🇩', 'sr': '🇸🇷',
    'se': '🇸🇪', 'ch': '🇨🇭', 'sy': '🇸🇾', 'tw': '🇹🇼', 'tj': '🇹🇯', 'tz': '🇹🇿',
    'th': '🇹🇭', 'tl': '🇹🇱', 'tg': '🇹🇬', 'to': '🇹🇴', 'tt': '🇹🇹', 'tn': '🇹🇳',
    'tr': '🇹🇷', 'tm': '🇹🇲', 'tv': '🇹🇻', 'ug': '🇺🇬', 'ua': '🇺🇦', 'ae': '🇦🇪',
    'gb': '🇬🇧', 'us': '🇺🇸', 'uy': '🇺🇾', 'uz': '🇺🇿', 'vu': '🇻🇺', 've': '🇻🇪',
    'vn': '🇻🇳', 'ye': '🇾🇪', 'zm': '🇿🇲', 'zw': '🇿🇼', 'ps': '🇵🇸', 'xk': '🇽🇰',
}

SERVICE_KEYWORDS = {
    "WhatsApp": ["whatsapp", "واتساب", "হোয়াটসঅ্যাপ"],
    "Telegram": ["telegram", "تيليجرام", "টেলিগ্রাম"],
    "Facebook": ["facebook", "فيسبوك", "ফেসবুক"],
    "Google": ["google", "gmail", "গুগল"],
    "Instagram": ["instagram", "انستقرام", "ইনস্টাগ্রাম"],
    "Twitter": ["twitter", "تويتر", "টুইটার"],
    "TikTok": ["tiktok", "تيك توك", "টিকটক"],
    "Snapchat": ["snapchat", "سناب شات"],
    "Amazon": ["amazon"], "Netflix": ["netflix"], "LinkedIn": ["linkedin"],
    "Microsoft": ["microsoft", "outlook"], "Apple": ["apple", "icloud"],
    "Discord": ["discord"], "Signal": ["signal"], "Viber": ["viber"],
    "PayPal": ["paypal"], "Binance": ["binance"], "Uber": ["uber"],
    "Spotify": ["spotify"], "Stripe": ["stripe"], "Coinbase": ["coinbase"],
    "KuCoin": ["kucoin"], "Bybit": ["bybit"], "OKX": ["okx"],
    "Steam": ["steam"], "Epic Games": ["epicgames", "epic games"],
    "PlayStation": ["playstation"], "Xbox": ["xbox"], "Reddit": ["reddit"],
    "Tinder": ["tinder"], "Bumble": ["bumble"], "Line": ["line"],
    "WeChat": ["wechat"], "VK": ["vkontakte", " vk "],
}

SERVICE_EMOJIS = {
    "Telegram": "📩", "WhatsApp": "🟢", "Facebook": "📘", "Instagram": "📸",
    "Google": "🔍", "Gmail": "✉️", "YouTube": "▶️", "Twitter": "🐦",
    "TikTok": "🎵", "Snapchat": "👻", "Amazon": "🛒", "Microsoft": "🪟",
    "Netflix": "🎬", "Spotify": "🎶", "Apple": "🍏", "PayPal": "💰",
    "Binance": "🪙", "Coinbase": "🪙", "Discord": "🗨️", "Steam": "🎮",
    "LinkedIn": "💼", "Uber": "🚗", "Tinder": "🔥", "Signal": "🔐",
    "Viber": "📞", "Reddit": "👽", "Unknown": "❓"
}

# --- Helper Functions ---
def get_flag_from_iso(iso_code):
    if not iso_code:
        return "🏴‍☠️"
    return ISO_TO_FLAG.get(iso_code.lower(), "🏴‍☠️")

def parse_country_from_number(phone_number):
    clean_num = phone_number.lstrip("+0")
    for length in [4, 3, 2, 1]:
        prefix = clean_num[:length]
        if prefix in COUNTRY_CODES:
            return COUNTRY_CODES[prefix]
    return ("Unknown", "🏴‍☠️")

def parse_service_from_text(text):
    if not text:
        return "Unknown"
    lower_text = text.lower()
    for service_name, keywords in SERVICE_KEYWORDS.items():
        if any(keyword in lower_text for keyword in keywords):
            return service_name
    return "Unknown"

def parse_code_from_sms(sms_text):
    code_match = re.search(r'(\d{3}-\d{3})', sms_text) or re.search(r'\b(\d{4,8})\b', sms_text)
    return code_match.group(1) if code_match else "N/A"

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

# --- State Management ---
def load_processed_ids():
    if not os.path.exists(STATE_FILE): return set()
    try:
        with open(STATE_FILE, 'r') as f: return set(json.load(f))
    except: return set()

def save_processed_id(sms_id):
    processed_ids = load_processed_ids()
    processed_ids.add(sms_id)
    with open(STATE_FILE, 'w') as f: json.dump(list(processed_ids), f)

def load_chat_ids():
    if not os.path.exists(CHAT_IDS_FILE):
        with open(CHAT_IDS_FILE, 'w') as f:
            json.dump(INITIAL_CHAT_IDS, f)
        return INITIAL_CHAT_IDS
    try:
        with open(CHAT_IDS_FILE, 'r') as f:
            return json.load(f)
    except: return INITIAL_CHAT_IDS

def save_chat_ids(chat_ids):
    with open(CHAT_IDS_FILE, 'w') as f:
        json.dump(chat_ids, f, indent=4)

# --- Session Management ---
def save_session(cookies):
    try:
        cookie_list = [(c.name, c.value, c.domain, c.path) for c in cookies.jar]
        with open(SESSION_FILE, 'wb') as f:
            import pickle; pickle.dump(cookie_list, f)
        print("💾 Session saved!")
    except Exception as e:
        print(f"⚠️ Failed to save session: {e}")

def load_session():
    if not os.path.exists(SESSION_FILE): return None
    try:
        import pickle
        with open(SESSION_FILE, 'rb') as f:
            cookie_list = pickle.load(f)
        return {name: value for name, value, domain, path in cookie_list}
    except: return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("🗑️ Session cleared!")

# --- Telegram Message Sender ---
async def send_telegram_message(bot, chat_id: str, message_data: dict):
    try:
        number_str = message_data.get("number", "N/A")
        country_name = message_data.get("country", "N/A")
        flag_emoji = message_data.get("flag", "🏴‍☠️")
        service_name = message_data.get("service", "Unknown")
        code_str = message_data.get("code", "N/A")
        full_sms_text = message_data.get("full_sms", "N/A")
        time_str = message_data.get("time", "N/A")
        service_emoji = SERVICE_EMOJIS.get(service_name, "❓")

        full_message = (
            f"🔔 *You have successfully received OTP*\n\n"
            f"📞 *Number:* `{escape_markdown(number_str)}`\n"
            f"🔑 *Code:* `{escape_markdown(code_str)}`\n"
            f"🏆 *Service:* {service_emoji} {escape_markdown(service_name)}\n"
            f"🌎 *Country:* {escape_markdown(country_name)} {flag_emoji}\n"
            f"⏳ *Time:* `{escape_markdown(time_str)}`\n\n"
            f"💬 *Message:*\n"
            f"```\n{full_sms_text}\n```"
        )

        keyboard = [[
            InlineKeyboardButton("📢 NUMBER CHANNEL", url="https://t.me/blackotpnum"),
            InlineKeyboardButton("💬 CHAT GROUP", url="https://t.me/EarningHub6112"),
            InlineKeyboardButton("🤖 NUMBER BOT", url="https://t.me/ah_method_number_bot"),
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await bot.send_message(
            chat_id=chat_id,
            text=full_message,
            parse_mode='MarkdownV2',
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"❌ Error sending to {chat_id}: {e}")

# --- Get Socket Token from Live Page ---
async def get_socket_credentials():
    """Login করে Live পেজ থেকে Socket token ও user নেওয়া"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    saved_cookies = load_session()

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True, cookies=saved_cookies) as client:
        try:
            # Session check অথবা login
            if not saved_cookies:
                print("ℹ️ Logging in...")
                login_page = await client.get(LOGIN_URL, headers=headers)
                soup = BeautifulSoup(login_page.text, 'html.parser')
                token_input = soup.find('input', {'name': '_token'})
                login_data = {'email': USERNAME, 'password': PASSWORD}
                if token_input:
                    login_data['_token'] = token_input['value']
                login_res = await client.post(LOGIN_URL, data=login_data, headers=headers)
                if "login" in str(login_res.url):
                    print("❌ Login failed!")
                    return None
                print("✅ Login successful!")
                save_session(client.cookies)
            else:
                print("🔓 Using saved session...")

            # Live পেজ থেকে token ও user নেওয়া
            live_page = await client.get(LIVE_SMS_URL, headers=headers)
            if "login" in str(live_page.url):
                print("⚠️ Session expired, re-logging in...")
                clear_session()
                return await get_socket_credentials()

            html = live_page.text

            # Token বের করা
            token_match = re.search(r"token:\s*['\"]([^'\"]+)['\"]", html)
            user_match = re.search(r"user:['\"]([a-f0-9]{32})['\"]", html)
            event_match = re.search(r'window\.liveSMSSocket\.on\(["\']([^"\']+)["\']', html)

            if not token_match or not user_match:
                print("❌ Could not find socket credentials in page!")
                return None

            creds = {
                'token': token_match.group(1),
                'user': user_match.group(1),
                'event': event_match.group(1) if event_match else None
            }
            print(f"✅ Socket credentials obtained!")
            print(f"   User: {creds['user'][:10]}...")
            return creds

        except Exception as e:
            print(f"❌ Error getting credentials: {e}")
            traceback.print_exc()
            return None

# --- Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) in ADMIN_CHAT_IDS:
        await update.message.reply_text(
            "Welcome Admin!\n"
            "/add_chat <chat_id> - Add chat\n"
            "/remove_chat <chat_id> - Remove chat\n"
            "/list_chats - List chats"
        )
    else:
        await update.message.reply_text("Sorry, not authorized.")

async def add_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins.")
        return
    try:
        new_chat_id = context.args[0]
        chat_ids = load_chat_ids()
        if new_chat_id not in chat_ids:
            chat_ids.append(new_chat_id)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"✅ Added: {new_chat_id}")
        else:
            await update.message.reply_text(f"⚠️ Already exists: {new_chat_id}")
    except:
        await update.message.reply_text("❌ Use: /add_chat <chat_id>")

async def remove_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins.")
        return
    try:
        chat_id_to_remove = context.args[0]
        chat_ids = load_chat_ids()
        if chat_id_to_remove in chat_ids:
            chat_ids.remove(chat_id_to_remove)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"✅ Removed: {chat_id_to_remove}")
        else:
            await update.message.reply_text(f"🤔 Not found: {chat_id_to_remove}")
    except:
        await update.message.reply_text("❌ Use: /remove_chat <chat_id>")

async def list_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins.")
        return
    chat_ids = load_chat_ids()
    if chat_ids:
        await update.message.reply_text("📜 Chat IDs:\n" + "\n".join(chat_ids))
    else:
        await update.message.reply_text("No chat IDs.")

# ⚡ SOCKET.IO BOT — মূল ফাংশন
async def run_socket_bot(bot):
    """
    Socket.IO দিয়ে সরাসরি iVAS সার্ভারের সাথে connect করে।
    OTP আসার সাথে সাথে instant Telegram-এ পাঠায়।
    কোনো polling নেই — push notification!
    """
    while True:
        try:
            print("🔑 Getting socket credentials...")
            creds = await get_socket_credentials()

            if not creds:
                print("⚠️ Failed to get credentials. Retrying in 30s...")
                await asyncio.sleep(30)
                continue

            token = creds['token']
            user = creds['user']
            event_name = creds['event']

            print(f"⚡ Connecting to Socket.IO server: {SOCKET_SERVER}/livesms")

            # Socket.IO client তৈরি
            sio = socketio.AsyncClient(
                ssl_verify=False,
                logger=False,
                engineio_logger=False,
                reconnection=False,
            )

            # ⚡ OTP আসলে এই function call হবে
            async def on_sms_received(data):
                try:
                    print(f"\n🔔 NEW OTP RECEIVED!")
                    print(f"   Data: {data}")

                    phone_number = str(data.get('recipient', '')).replace('+', '').strip()
                    sms_text = str(data.get('message', ''))
                    originator = str(data.get('originator', '')).replace('+', '').strip()
                    range_name = str(data.get('range', ''))
                    country_iso = str(data.get('country_iso', ''))

                    if not phone_number or not sms_text:
                        return

                    unique_id = f"{phone_number}-{sms_text}"
                    processed_ids = load_processed_ids()

                    if unique_id in processed_ids:
                        print(f"   ⏭️ Already sent, skipping.")
                        return

                    # দেশ ও পতাকা বের করা
                    flag = get_flag_from_iso(country_iso)
                    country_name, phone_flag = parse_country_from_number(phone_number)
                    if flag == "🏴‍☠️":
                        flag = phone_flag

                    # Service বের করা — originator থেকে
                    service = parse_service_from_text(originator)
                    if service == "Unknown":
                        service = parse_service_from_text(sms_text)

                    code = parse_code_from_sms(sms_text)
                    time_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

                    msg_data = {
                        "id": unique_id,
                        "time": time_str,
                        "number": phone_number,
                        "country": country_name,
                        "flag": flag,
                        "service": service,
                        "code": code,
                        "full_sms": sms_text
                    }

                    print(f"   📱 {phone_number} | {service} | {sms_text[:40]}...")

                    chat_ids = load_chat_ids()
                    for chat_id in chat_ids:
                        await send_telegram_message(bot, chat_id, msg_data)

                    save_processed_id(unique_id)
                    print(f"   ✅ Sent to {len(chat_ids)} chat(s)!")

                except Exception as e:
                    print(f"❌ Error processing SMS: {e}")
                    traceback.print_exc()

            @sio.event
            async def connect():
                print("✅ Connected to Socket.IO server!")

            @sio.event
            async def disconnect():
                print("⚠️ Disconnected from Socket.IO server!")

            @sio.event
            async def connect_error(data):
                print(f"❌ Connection error: {data}")

            # Event listener যোগ করা
            if event_name:
                sio.on(event_name, on_sms_received)
                print(f"👂 Listening to event: {event_name[:20]}...")
            else:
                # সব event শোনা
                @sio.on('*')
                async def catch_all(event, data):
                    print(f"📨 Event received: {event}")
                    await on_sms_received(data)

            # HTML-এর হুবহু format:
            # io.connect(url/namespace, { query: {token, user}, transports: ['websocket'] })
            import urllib.parse
            query_params = urllib.parse.urlencode({'token': token, 'user': user})
            full_url = f"https://ivas.tempnum.qzz.io/livesms?{query_params}"
            print(f"   🔗 Connecting to: https://ivas.tempnum.qzz.io/livesms")
            await sio.connect(
                full_url,
                transports=['websocket'],
                wait_timeout=30,
                headers={
                    'Origin': 'https://ivas.tempnum.qzz.io',
                    'Referer': 'https://ivas.tempnum.qzz.io/portal/live/my_sms',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }
            )

            print("🎯 Socket.IO bot is LIVE! Waiting for OTPs...")
            await sio.wait()

        except Exception as e:
            print(f"❌ Socket error: {e}")
            traceback.print_exc()
            print("🔄 Reconnecting in 15 seconds...")
            await asyncio.sleep(15)
            clear_session()

# --- Main ---
def main():
    keep_alive()
    print("🚀 iVAS Socket.IO Bot starting...")
    print(f"⚡ INSTANT mode — OTP arrives → Telegram in 1-2 seconds!")

    if not ADMIN_CHAT_IDS:
        print("🔴 WARNING: No admin IDs set!")
        return

    application = Application.builder().token(YOUR_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("add_chat", add_chat_command))
    application.add_handler(CommandHandler("remove_chat", remove_chat_command))
    application.add_handler(CommandHandler("list_chats", list_chats_command))

    async def post_init(app):
        asyncio.create_task(run_socket_bot(app.bot))

    application.post_init = post_init

    print("🤖 Bot is online!")
    application.run_polling()

if __name__ == "__main__":
    main()
