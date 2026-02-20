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
# New library added
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

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
    
# --- Configuration (Fill in your details) ---
# Your Telegram Bot Token here. You can get it from BotFather.
# Example: YOUR_BOT_TOKEN = "1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
YOUR_BOT_TOKEN = "8393297595:AAEksSfupLmn5qeBxjoGT3c9IzaJaLI6mck" # <--- This line needs to be changed

# ==================== New Addition: Multiple Admin IDs ====================
# Add your and other admins' Telegram User IDs to the list below
ADMIN_CHAT_IDS = ["7095358778"] # Example: ["YOUR_ADMIN_USER_ID_1", "YOUR_ADMIN_USER_ID_2"]
# =================================================================

# Old chat IDs kept for the first run
INITIAL_CHAT_IDS = ["-1003007557624"] 

LOGIN_URL = "https://ivas.tempnum.qzz.io/login"
BASE_URL = "https://ivas.tempnum.qzz.io"
SMS_API_ENDPOINT = "https://ivas.tempnum.qzz.io/portal/sms/received/getsms"

USERNAME = "sagorsakh8@gmail.com"
PASSWORD = "61453812Sa@"

# Fast polling interval (10 seconds) with session caching for quick OTP delivery
POLLING_INTERVAL_SECONDS = 10 
# STATE_FILE name changed
STATE_FILE = "processed_sms_ids.json" 
CHAT_IDS_FILE = "chat_ids.json" # New file for saving chat IDs
SESSION_FILE = "session_cookies.pkl" # Session storage for faster login

# List of countries
COUNTRY_CODES = {
    '1': ('USA/Canada', '🇺🇸'), '7': ('Russia/Kazakhstan', '🇷🇺'), '20': ('Egypt', '🇪🇬'), '27': ('South Africa', '🇿🇦'),
    '30': ('Greece', '🇬🇷'), '31': ('Netherlands', '🇳🇱'), '32': ('Belgium', '🇧🇪'), '33': ('France', '🇫🇷'),
    '34': ('Spain', '🇪🇸'), '36': ('Hungary', '🇭🇺'), '39': ('Italy', '🇮🇹'), '40': ('Romania', '🇷🇴'),
    '41': ('Switzerland', '🇨🇭'), '43': ('Austria', '🇦🇹'), '44': ('United Kingdom', '🇬🇧'), '45': ('Denmark', '🇩🇰'),
    '46': ('Sweden', '🇸🇪'), '47': ('Norway', '🇳🇴'), '48': ('Poland', '🇵🇱'), '49': ('Germany', '🇩🇪'),
    '51': ('Peru', '🇵🇪'), '52': ('Mexico', '🇲🇽'), '53': ('Cuba', '🇨🇺'), '54': ('Argentina', '🇦🇷'),
    '55': ('Brazil', '🇧🇷'), '56': ('Chile', '🇨🇱'), '57': ('Colombia', '🇨🇴'), '58': ('Venezuela', '🇻🇪'),
    '60': ('Malaysia', '🇲🇾'), '61': ('Australia', '🇦🇺'), '62': ('Indonesia', '🇮🇩'), '63': ('Philippines', '🇵🇭'),
    '64': ('New Zealand', '🇳🇿'), '65': ('Singapore', '🇸🇬'), '66': ('Thailand', '🇹🇭'), '81': ('Japan', '🇯🇵'),
    '82': ('South Korea', '🇰🇷'), '84': ('Viet Nam', '🇻🇳'), '86': ('China', '🇨🇳'), '90': ('Turkey', '🇹🇷'),
    '91': ('India', '🇮🇳'), '92': ('Pakistan', '🇵🇰'), '93': ('Afghanistan', '🇦🇫'), '94': ('Sri Lanka', '🇱🇰'),
    '95': ('Myanmar', '🇲🇲'), '98': ('Iran', '🇮🇷'), '211': ('South Sudan', '🇸🇸'), '212': ('Morocco', '🇲🇦'),
    '213': ('Algeria', '🇩🇿'), '216': ('Tunisia', '🇹🇳'), '218': ('Libya', '🇱🇾'), '220': ('Gambia', '🇬🇲'),
    '221': ('Senegal', '🇸🇳'), '222': ('Mauritania', '🇲🇷'), '223': ('Mali', '🇲🇱'), '224': ('Guinea', '🇬🇳'),
    '225': ("Côte d'Ivoire", '🇨🇮'), '226': ('Burkina Faso', '🇧🇫'), '227': ('Niger', '🇳🇪'), '228': ('Togo', '🇹🇬'),
    '229': ('Benin', '🇧🇯'), '230': ('Mauritius', '🇲🇺'), '231': ('Liberia', '🇱🇷'), '232': ('Sierra Leone', '🇸🇱'),
    '233': ('Ghana', '🇬🇭'), '234': ('Nigeria', '🇳🇬'), '235': ('Chad', '🇹🇩'), '236': ('Central African Republic', '🇨🇫'),
    '237': ('Cameroon', '🇨🇲'), '238': ('Cape Verde', '🇨🇻'), '239': ('Sao Tome and Principe', '🇸🇹'),
    '240': ('Equatorial Guinea', '🇬🇶'), '241': ('Gabon', '🇬🇦'), '242': ('Congo', '🇨🇬'),
    '243': ('DR Congo', '🇨🇩'), '244': ('Angola', '🇦🇴'), '245': ('Guinea-Bissau', '🇬🇼'), '248': ('Seychelles', '🇸🇨'),
    '249': ('Sudan', '🇸🇩'), '250': ('Rwanda', '🇷🇼'), '251': ('Ethiopia', '🇪🇹'), '252': ('Somalia', '🇸🇴'),
    '253': ('Djibouti', '🇩🇯'), '254': ('Kenya', '🇰🇪'), '255': ('Tanzania', '🇹🇿'), '256': ('Uganda', '🇺🇬'),
    '257': ('Burundi', '🇧🇮'), '258': ('Mozambique', '🇲🇿'), '260': ('Zambia', '🇿🇲'), '261': ('Madagascar', '🇲🇬'),
    '263': ('Zimbabwe', '🇿🇼'), '264': ('Namibia', '🇳🇦'), '265': ('Malawi', '🇲🇼'), '266': ('Lesotho', '🇱🇸'),
    '267': ('Botswana', '🇧🇼'), '268': ('Eswatini', '🇸🇿'), '269': ('Comoros', '🇰🇲'), '290': ('Saint Helena', '🇸🇭'),
    '291': ('Eritrea', '🇪🇷'), '297': ('Aruba', '🇦🇼'), '298': ('Faroe Islands', '🇫🇴'), '299': ('Greenland', '🇬🇱'),
    '350': ('Gibraltar', '🇬🇮'), '351': ('Portugal', '🇵🇹'), '352': ('Luxembourg', '🇱🇺'), '353': ('Ireland', '🇮🇪'),
    '354': ('Iceland', '🇮🇸'), '355': ('Albania', '🇦🇱'), '356': ('Malta', '🇲🇹'), '357': ('Cyprus', '🇨🇾'),
    '358': ('Finland', '🇫🇮'), '359': ('Bulgaria', '🇧🇬'), '370': ('Lithuania', '🇱🇹'), '371': ('Latvia', '🇱🇻'),
    '372': ('Estonia', '🇪🇪'), '373': ('Moldova', '🇲🇩'), '374': ('Armenia', '🇦🇲'), '375': ('Belarus', '🇧🇾'),
    '376': ('Andorra', '🇦🇩'), '377': ('Monaco', '🇲🇨'), '378': ('San Marino', '🇸🇲'), '380': ('Ukraine', '🇺🇦'),
    '381': ('Serbia', '🇷🇸'), '382': ('Montenegro', '🇲🇪'), '385': ('Croatia', '🇭🇷'), '386': ('Slovenia', '🇸🇮'),
    '387': ('Bosnia and Herzegovina', '🇧🇦'), '389': ('North Macedonia', '🇲🇰'), '420': ('Czech Republic', '🇨🇿'),
    '421': ('Slovakia', '🇸🇰'), '423': ('Liechtenstein', '🇱🇮'), '501': ('Belize', '🇧🇿'), '502': ('Guatemala', '🇬🇹'),
    '503': ('El Salvador', '🇸🇻'), '504': ('Honduras', '🇭🇳'), '505': ('Nicaragua', '🇳🇮'), '506': ('Costa Rica', '🇨🇷'),
    '507': ('Panama', '🇵🇦'), '509': ('Haiti', '🇭🇹'), '590': ('Guadeloupe', '🇬🇵'), '591': ('Bolivia', '🇧🇴'),
    '592': ('Guyana', '🇬🇾'), '593': ('Ecuador', '🇪🇨'), '595': ('Paraguay', '🇵🇾'), '597': ('Suriname', '🇸🇷'),
    '598': ('Uruguay', '🇺🇾'), '673': ('Brunei', '🇧🇳'), '675': ('Papua New Guinea', '🇵🇬'), '676': ('Tonga', '🇹🇴'),
    '677': ('Solomon Islands', '🇸🇧'), '678': ('Vanuatu', '🇻🇺'), '679': ('Fiji', '🇫🇯'), '685': ('Samoa', '🇼🇸'),
    '689': ('French Polynesia', '🇵🇫'), '852': ('Hong Kong', '🇭🇰'), '853': ('Macau', '🇲🇴'), '855': ('Cambodia', '🇰🇭'),
    '856': ('Laos', '🇱🇦'), '880': ('Bangladesh', '🇧🇩'), '886': ('Taiwan', '🇹🇼'), '960': ('Maldives', '🇲🇻'),
    '961': ('Lebanon', '🇱🇧'), '962': ('Jordan', '🇮🇴'), '963': ('Syria', '🇸🇾'), '964': ('Iraq', '🇮🇶'),
    '965': ('Kuwait', '🇰🇼'), '966': ('Saudi Arabia', '🇸🇦'), '967': ('Yemen', '🇾🇪'), '968': ('Oman', '🇴🇲'),
    '970': ('Palestine', '🇵🇸'), '971': ('United Arab Emirates', '🇦🇪'), '972': ('Israel', '🇮🇱'),
    '973': ('Bahrain', '🇧🇭'), '974': ('Qatar', '🇶🇦'), '975': ('Bhutan', '🇧🇹'), '976': ('Mongolia', '🇲🇳'),
    '977': ('Nepal', '🇳🇵'), '992': ('Tajikistan', '🇹🇯'), '993': ('Turkmenistan', '🇹🇲'), '994': ('Azerbaijan', '🇦🇿'),
    '995': ('Georgia', '🇬🇪'), '996': ('Kyrgyzstan', '🇰🇬'), '998': ('Uzbekistan', '🇺🇿'),
}

# Create COUNTRY_FLAGS dictionary from COUNTRY_CODES
COUNTRY_FLAGS = {name: flag for code, (name, flag) in COUNTRY_CODES.items()}

# Service Keywords (for identifying service from SMS text)
# Major services support multiple languages (Arabic, Bengali, Hindi, etc.)
SERVICE_KEYWORDS = {
    "WhatsApp": ["whatsapp", "واتساب", "واتس اب", "হোয়াটসঅ্যাপ", "व्हाट्सएप", "вотсап"],
    "Telegram": ["telegram", "تيليجرام", "تلغرام", "টেলিগ্রাম", "टेलीग्राम", "телеграм"],
    "Facebook": ["facebook", "فيسبوك", "ফেসবুক", "फेसबुक"],
    "Google": ["google", "gmail", "جوجل", "গুগল", "गूगल"],
    "Instagram": ["instagram", "انستقرام", "انستجرام", "ইনস্টাগ্রাম", "इंस्टाग्राम"],
    "Twitter": ["twitter", "تويتر", "টুইটার", "ट्विटर"],
    "X": ["x", "إكس"],
    "Messenger": ["messenger", "meta", "ماسنجر", "مسنجر", "মেসেঞ্জার"],
    "TikTok": ["tiktok", "تيك توك", "টিকটক", "टिकटॉक"],
    "Snapchat": ["snapchat", "سناب شات", "سناب", "স্ন্যাপচ্যাট"],
    "Amazon": ["amazon"],
    "Netflix": ["netflix"],
    "LinkedIn": ["linkedin"],
    "Microsoft": ["microsoft", "outlook", "live.com"],
    "Apple": ["apple", "icloud"],
    "Discord": ["discord"],
    "Signal": ["signal"],
    "Viber": ["viber"],
    "IMO": ["imo"],
    "PayPal": ["paypal"],
    "Binance": ["binance"],
    "Uber": ["uber"],
    "Bolt": ["bolt"],
    "Airbnb": ["airbnb"],
    "Yahoo": ["yahoo"],
    "Steam": ["steam"],
    "Blizzard": ["blizzard"],
    "Foodpanda": ["foodpanda"],
    "Pathao": ["pathao"],
    "Gmail": ["gmail"],
    "YouTube": ["youtube"],
    "eBay": ["ebay"],
    "AliExpress": ["aliexpress"],
    "Alibaba": ["alibaba"],
    "Flipkart": ["flipkart"],
    "Outlook": ["outlook"],
    "Skype": ["skype"],
    "Spotify": ["spotify"],
    "iCloud": ["icloud"],
    "Stripe": ["stripe"],
    "Cash App": ["cash app", "square cash"],
    "Venmo": ["venmo"],
    "Zelle": ["zelle"],
    "Wise": ["wise", "transferwise"],
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
    "Twitch": ["twitch"],
    "Reddit": ["reddit"],
    "ProtonMail": ["protonmail", "proton"],
    "Zoho": ["zoho"],
    "Quora": ["quora"],
    "StackOverflow": ["stackoverflow"],
    "Indeed": ["indeed"],
    "Upwork": ["upwork"],
    "Fiverr": ["fiverr"],
    "Glassdoor": ["glassdoor"],
    "Booking.com": ["booking.com", "booking"],
    "Careem": ["careem"],
    "Swiggy": ["swiggy"],
    "Zomato": ["zomato"],
    "McDonald's": ["mcdonalds", "mcdonald's"],
    "KFC": ["kfc"],
    "Nike": ["nike"],
    "Adidas": ["adidas"],
    "Shein": ["shein"],
    "OnlyFans": ["onlyfans"],
    "Tinder": ["tinder"],
    "Bumble": ["bumble"],
    "Grindr": ["grindr"],
    "Line": ["line"],
    "WeChat": ["wechat"],
    "VK": ["vk", "vkontakte"],
    "Unknown": ["unknown"]
}

# Service Emojis (for display in Telegram messages)
SERVICE_EMOJIS = {
    "Telegram": "📩", "WhatsApp": "🟢", "Facebook": "📘", "Instagram": "📸", "Messenger": "💬",
    "Google": "🔍", "Gmail": "✉️", "YouTube": "▶️", "Twitter": "🐦", "X": "❌",
    "TikTok": "🎵", "Snapchat": "👻", "Amazon": "🛒", "eBay": "📦", "AliExpress": "📦",
    "Alibaba": "🏭", "Flipkart": "📦", "Microsoft": "🪟", "Outlook": "📧", "Skype": "📞",
    "Netflix": "🎬", "Spotify": "🎶", "Apple": "🍏", "iCloud": "☁️", "PayPal": "💰",
    "Stripe": "💳", "Cash App": "💵", "Venmo": "💸", "Zelle": "🏦", "Wise": "🌐",
    "Binance": "🪙", "Coinbase": "🪙", "KuCoin": "🪙", "Bybit": "📈", "OKX": "🟠",
    "Huobi": "🔥", "Kraken": "🐙", "MetaMask": "🦊", "Discord": "🗨️", "Steam": "🎮",
    "Epic Games": "🕹️", "PlayStation": "🎮", "Xbox": "🎮", "Twitch": "📺", "Reddit": "👽",
    "Yahoo": "🟣", "ProtonMail": "🔐", "Zoho": "📬", "Quora": "❓", "StackOverflow": "🧑‍💻",
    "LinkedIn": "💼", "Indeed": "📋", "Upwork": "🧑‍💻", "Fiverr": "💻", "Glassdoor": "🔎",
    "Airbnb": "🏠", "Booking.com": "🛏️", "Uber": "🚗", "Lyft": "🚕", "Bolt": "🚖",
    "Careem": "🚗", "Swiggy": "🍔", "Zomato": "🍽️", "Foodpanda": "🍱",
    "McDonald's": "🍟", "KFC": "🍗", "Nike": "👟", "Adidas": "👟", "Shein": "👗",
    "OnlyFans": "🔞", "Tinder": "🔥", "Bumble": "🐝", "Grindr": "😈", "Signal": "🔐",
    "Viber": "📞", "Line": "💬", "WeChat": "💬", "VK": "🌐", "Unknown": "❓"
}

# --- Chat ID Management Functions ---
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

# --- New Telegram Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) in ADMIN_CHAT_IDS:
        await update.message.reply_text(
            "Welcome Admin!\n"
            "You can use the following commands:\n"
            "/add_chat <chat_id> - Add a new chat ID\n"
            "/remove_chat <chat_id> - Remove a chat ID\n"
            "/list_chats - List all chat IDs"
        )
    else:
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")

async def add_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins can use this command.")
        return
    try:
        new_chat_id = context.args[0]
        chat_ids = load_chat_ids()
        if new_chat_id not in chat_ids:
            chat_ids.append(new_chat_id)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"✅ Chat ID {new_chat_id} successfully added.")
        else:
            await update.message.reply_text(f"⚠️ This chat ID ({new_chat_id}) is already in the list.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Invalid format. Use: /add_chat <chat_id>")

async def remove_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins can use this command.")
        return
    try:
        chat_id_to_remove = context.args[0]
        chat_ids = load_chat_ids()
        if chat_id_to_remove in chat_ids:
            chat_ids.remove(chat_id_to_remove)
            save_chat_ids(chat_ids)
            await update.message.reply_text(f"✅ Chat ID {chat_id_to_remove} successfully removed.")
        else:
            await update.message.reply_text(f"🤔 This chat ID ({chat_id_to_remove}) was not found in the list.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Invalid format. Use: /remove_chat <chat_id>")

async def list_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Sorry, only admins can use this command.")
        return
    
    chat_ids = load_chat_ids()
    if chat_ids:
        message = "📜 Currently registered chat IDs are:\n"
        for cid in chat_ids:
            message += f"- `{escape_markdown(str(cid))}`\n"
        try:
            await update.message.reply_text(message, parse_mode='MarkdownV2')
        except Exception as e:
            plain_message = "📜 Currently registered chat IDs are:\n" + "\n".join(map(str, chat_ids))
            await update.message.reply_text(plain_message)
    else:
        await update.message.reply_text("No chat IDs registered.")

# --- Core Functions ---
def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

def load_processed_ids():
    if not os.path.exists(STATE_FILE): return set()
    try:
        with open(STATE_FILE, 'r') as f: return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError): return set()

def save_processed_id(sms_id):
    processed_ids = load_processed_ids()
    processed_ids.add(sms_id)
    with open(STATE_FILE, 'w') as f: json.dump(list(processed_ids), f)

# --- Session Management Functions ---
def save_session(cookies):
    """Save session cookies to file for reuse"""
    try:
        # Convert httpx.Cookies to a list of tuples to avoid conflicts
        cookie_list = [(cookie.name, cookie.value, cookie.domain, cookie.path) 
                       for cookie in cookies.jar]
        with open(SESSION_FILE, 'wb') as f:
            pickle.dump(cookie_list, f)
        print("💾 Session saved successfully!")
    except Exception as e:
        print(f"⚠️ Failed to save session: {e}")

def load_session():
    """Load saved session cookies"""
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, 'rb') as f:
            cookie_list = pickle.load(f)
        print("🔓 Loaded saved session!")
        # Convert list back to dict format for httpx
        cookies_dict = {name: value for name, value, domain, path in cookie_list}
        return cookies_dict
    except Exception as e:
        print(f"⚠️ Failed to load session: {e}")
        return None

def clear_session():
    """Clear saved session"""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("🗑️ Session cleared!")

async def fetch_sms_from_api(client: httpx.AsyncClient, headers: dict, csrf_token: str):
    all_messages = []
    try:
        today = datetime.now(timezone.utc)  # Using UTC time
        start_date = today - timedelta(days=1) # Data for the last 24 hours
        from_date_str, to_date_str = start_date.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y')
        first_payload = {'from': from_date_str, 'to': to_date_str, '_token': csrf_token}
        summary_response = await client.post(SMS_API_ENDPOINT, headers=headers, data=first_payload)
        summary_response.raise_for_status()
        summary_soup = BeautifulSoup(summary_response.text, 'html.parser')
        group_divs = summary_soup.find_all('div', {'class': 'pointer'})
        if not group_divs: return []
        
        group_ids = [re.search(r"getDetials\('(.+?)'\)", div.get('onclick', '')).group(1) for div in group_divs if re.search(r"getDetials\('(.+?)'\)", div.get('onclick', ''))]
        numbers_url = urljoin(BASE_URL, "portal/sms/received/getsms/number")
        sms_url = urljoin(BASE_URL, "portal/sms/received/getsms/number/sms")

        for group_id in group_ids:
            numbers_payload = {'start': from_date_str, 'end': to_date_str, 'range': group_id, '_token': csrf_token}
            numbers_response = await client.post(numbers_url, headers=headers, data=numbers_payload)
            numbers_soup = BeautifulSoup(numbers_response.text, 'html.parser')
            number_divs = numbers_soup.select("div[onclick*='getDetialsNumber']")
            if not number_divs: continue
            phone_numbers = [div.text.strip() for div in number_divs]
            
            for phone_number in phone_numbers:
                sms_payload = {'start': from_date_str, 'end': to_date_str, 'Number': phone_number, 'Range': group_id, '_token': csrf_token}
                sms_response = await client.post(sms_url, headers=headers, data=sms_payload)
                sms_soup = BeautifulSoup(sms_response.text, 'html.parser')
                final_sms_cards = sms_soup.find_all('div', class_='card-body')
                
                for card in final_sms_cards:
                    sms_text_p = card.find('p', class_='mb-0')
                    if sms_text_p:
                        sms_text = sms_text_p.get_text(separator='\n').strip()
                        date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')  # Using UTC time
                        
                        country_name_match = re.match(r'([a-zA-Z\s]+)', group_id)
                        if country_name_match: country_name = country_name_match.group(1).strip()
                        else: country_name = group_id.strip()
                        
                        service = "Unknown"
                        lower_sms_text = sms_text.lower()
                        for service_name, keywords in SERVICE_KEYWORDS.items():
                            if any(keyword in lower_sms_text for keyword in keywords):
                                service = service_name
                                break
                        code_match = re.search(r'(\d{3}-\d{3})', sms_text) or re.search(r'\b(\d{4,8})\b', sms_text)
                        code = code_match.group(1) if code_match else "N/A"
                        unique_id = f"{phone_number}-{sms_text}"
                        flag = COUNTRY_FLAGS.get(country_name, "🏴‍☠️")
                        
                        # Using 'sms_text' instead of 'full_sms_text'
                        all_messages.append({"id": unique_id, "time": date_str, "number": phone_number, "country": country_name, "flag": flag, "service": service, "code": code, "full_sms": sms_text}) 
        return all_messages
    except httpx.RequestError as e:
        print(f"❌ Network issue (httpx): {e}")
        return []
    except Exception as e:
        print(f"❌ Error fetching or processing API data: {e}")
        traceback.print_exc()
        return []

async def send_telegram_message(context: ContextTypes.DEFAULT_TYPE, chat_id: str, message_data: dict):
    try:
        time_str, number_str = message_data.get("time", "N/A"), message_data.get("number", "N/A")
        country_name, flag_emoji = message_data.get("country", "N/A"), message_data.get("flag", "🏴‍☠️")
        service_name, code_str = message_data.get("service", "N/A"), message_data.get("code", "N/A")
        full_sms_text = message_data.get("full_sms", "N/A")
        
        # Add service emoji
        service_emoji = SERVICE_EMOJIS.get(service_name, "❓") # If service not found, show '❓'

        # Message format reverted to previous state with extra spacing
        full_message = (f"🔔 *You have successfully received OTP*\n\n" 
                        f"📞 *Number:* `{escape_markdown(number_str)}`\n" 
                        f"🔑 *Code:* `{escape_markdown(code_str)}`\n" 
                        f"🏆 *Service:* {service_emoji} {escape_markdown(service_name)}\n" 
                        f"🌎 *Country:* {escape_markdown(country_name)} {flag_emoji}\n" 
                        f"⏳ *Time:* `{escape_markdown(time_str)}`\n\n" 
                        f"💬 *Message:*\n" 
                        f"```\n{full_sms_text}\n```")
        
        await context.bot.send_message(chat_id=chat_id, text=full_message, parse_mode='MarkdownV2')
    except Exception as e:
        print(f"❌ Error sending message to chat ID {chat_id}: {e}")

# --- Main Job or Task (Optimized with Session Caching) ---
async def check_sms_job(context: ContextTypes.DEFAULT_TYPE):
    print(f"\n--- [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] Checking for new messages ---")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # Try to load saved session first
    saved_cookies = load_session()
    
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True, cookies=saved_cookies) as client:
        try:
            csrf_token = None
            
            # If we have saved session, try to get CSRF token directly from SMS page
            if saved_cookies:
                print("🔓 Using saved session...")
                try:
                    # Go directly to SMS page to get CSRF token
                    sms_page = await client.get(BASE_URL + "/portal/sms/received", headers=headers)
                    if "login" not in str(sms_page.url):
                        # Session is valid!
                        print("✅ Session still valid!")
                        soup = BeautifulSoup(sms_page.text, 'html.parser')
                        csrf_token_meta = soup.find('meta', {'name': 'csrf-token'})
                        if csrf_token_meta:
                            csrf_token = csrf_token_meta.get('content')
                            headers['Referer'] = str(sms_page.url)
                            print("🔑 CSRF token obtained!")
                        else:
                            print("⚠️ CSRF token not found on page")
                            clear_session()
                    else:
                        # Redirected to login, session expired
                        print("⚠️ Session expired")
                        clear_session()
                except Exception as e:
                    print(f"⚠️ Session check failed: {e}")
                    clear_session()
            
            # Login only if we don't have a valid csrf_token
            if not csrf_token:
                print("ℹ️ Logging in...")
                login_page_res = await client.get(LOGIN_URL, headers=headers)
                soup = BeautifulSoup(login_page_res.text, 'html.parser')
                token_input = soup.find('input', {'name': '_token'})
                login_data = {'email': USERNAME, 'password': PASSWORD}
                if token_input: 
                    login_data['_token'] = token_input['value']

                login_res = await client.post(LOGIN_URL, data=login_data, headers=headers)
                
                if "login" in str(login_res.url):
                    print("❌ Login failed. Check username/password.")
                    clear_session()
                    return

                print("✅ Login successful!")
                # Save session cookies
                save_session(client.cookies)
                
                dashboard_soup = BeautifulSoup(login_res.text, 'html.parser')
                csrf_token_meta = dashboard_soup.find('meta', {'name': 'csrf-token'})
                if not csrf_token_meta:
                    print("❌ CSRF token not found after login.")
                    return
                csrf_token = csrf_token_meta.get('content')
                headers['Referer'] = str(login_res.url)

            # Fetch SMS
            messages = await fetch_sms_from_api(client, headers, csrf_token)
            if not messages: 
                print("✔️ No new messages found.")
                return

            processed_ids = load_processed_ids()
            chat_ids_to_send = load_chat_ids()
            new_messages_found = 0
            
            for msg in reversed(messages):
                if msg["id"] not in processed_ids:
                    new_messages_found += 1
                    print(f"✔️ New message found from: {msg['number']}.")
                    for chat_id in chat_ids_to_send:
                        await send_telegram_message(context, chat_id, msg)
                    save_processed_id(msg["id"])
            
            if new_messages_found > 0:
                print(f"✅ Total {new_messages_found} new messages sent to Telegram.")

        except httpx.RequestError as e:
            print(f"❌ Network issue: {e}")
            clear_session()
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            clear_session()

# --- Main part to start the bot ---
def main():
    keep_alive()   # 👈 YE LINE ADD KARO (SABSE PEHLE)
    print("🚀 iVasms to Telegram Bot is starting...")

    # Not checking for 'YOUR_SECOND_ADMIN_ID_HERE' anymore,
    # as you have correctly provided the IDs in ADMIN_CHAT_IDS.
    # A warning will be shown if the ADMIN_CHAT_IDS list is empty.
    if not ADMIN_CHAT_IDS:
        print("\n!!! 🔴 WARNING: You have not correctly set admin IDs in your ADMIN_CHAT_IDS list. !!!\n")
        return

    # Create the bot application
    application = Application.builder().token(YOUR_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("add_chat", add_chat_command))
    application.add_handler(CommandHandler("remove_chat", remove_chat_command))
    application.add_handler(CommandHandler("list_chats", list_chats_command))

    # Set the main job to run repeatedly at a specific interval
    job_queue = application.job_queue
    job_queue.run_repeating(
        check_sms_job,
        interval=POLLING_INTERVAL_SECONDS,
        first=1,
    )

    print(f"🚀 Checking for new messages every {POLLING_INTERVAL_SECONDS} seconds.")
    print("🤖 Bot is now online. Ready to listen for commands.")
    print("⚠️ Press Ctrl+C to stop the bot.")
    
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
