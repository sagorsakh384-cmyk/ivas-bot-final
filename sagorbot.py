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

# ==================== Multiple Admin IDs ====================
ADMIN_CHAT_IDS = ["7095358778"]

# ==================== JavaScript Bot's Files ====================
JS_ACTIVE_NUMBERS_FILE = "active_numbers.json"  # JavaScript বটের active_numbers.json ফাইল
# ===============================================================

# Old chat IDs kept for the first run
INITIAL_CHAT_IDS = ["1003007557624"] 

LOGIN_URL = "https://ivas.tempnum.qzz.io/login"
BASE_URL = "https://ivas.tempnum.qzz.io"
SMS_API_ENDPOINT = "https://ivas.tempnum.qzz.io/portal/sms/received/getsms"

USERNAME = "sagorsakh8@gmail.com"
PASSWORD = "61453812Sa@"

# Fast polling interval
POLLING_INTERVAL_SECONDS = 10 
STATE_FILE = "processed_sms_ids.json" 
CHAT_IDS_FILE = "chat_ids.json"
SESSION_FILE = "session_cookies.pkl"
COUNTRIES_FILE = "countries.json"  # আলাদা কান্ট্রি ফাইল

# ==================== লিংক কনফিগারেশন (আপনার দেওয়া লিংক) ====================
NUMBER_BOT_LINK = "https://t.me/Ah_method_number_bot"
NUMBER_CHANNEL_LINK = "https://t.me/blackotpnum"
DEVELOPER_LINK = "https://t.me/sadhin8miya"
# ============================================================================

# Service Keywords
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

# Service Emojis
SERVICE_EMOJIS = {
    "Telegram": "✈️", "WhatsApp": "🟢", "Facebook": "📘", "Instagram": "📸", "Messenger": "💬",
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

# --- কান্ট্রি ডাটা লোড করার ফাংশন ---
def load_countries():
    """countries.json ফাইল থেকে কান্ট্রি ডাটা লোড করে"""
    if os.path.exists(COUNTRIES_FILE):
        try:
            with open(COUNTRIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# --- JavaScript বটের active_numbers লোড করার ফাংশন ---
def load_js_active_numbers():
    """JavaScript বটের active_numbers.json ফাইল লোড করে"""
    if os.path.exists(JS_ACTIVE_NUMBERS_FILE):
        try:
            with open(JS_ACTIVE_NUMBERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

# --- Telegram Command Handlers ---
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
    try:
        cookie_list = [(cookie.name, cookie.value, cookie.domain, cookie.path) 
                       for cookie in cookies.jar]
        with open(SESSION_FILE, 'wb') as f:
            pickle.dump(cookie_list, f)
        print("💾 Session saved successfully!")
    except Exception as e:
        print(f"⚠️ Failed to save session: {e}")

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, 'rb') as f:
            cookie_list = pickle.load(f)
        print("🔓 Loaded saved session!")
        cookies_dict = {name: value for name, value, domain, path in cookie_list}
        return cookies_dict
    except Exception as e:
        print(f"⚠️ Failed to load session: {e}")
        return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("🗑️ Session cleared!")

# --- Phone Number Cleaner Function ---
def clean_phone_number(phone_number):
    """ফোন নাম্বার থেকে শুধু ডিজিট বের করে"""
    if not phone_number:
        return None
    cleaned = re.sub(r'[^0-9]', '', str(phone_number))
    return cleaned if cleaned else None

# --- Extract Country from Number ---
def get_country_from_number(phone_number, countries_data):
    """ফোন নাম্বার থেকে কান্ট্রি কোড বের করে"""
    if not phone_number or not countries_data:
        return "Unknown", "🏴‍☠️"
    
    cleaned = clean_phone_number(phone_number)
    if not cleaned:
        return "Unknown", "🏴‍☠️"
    
    # 3 ডিজিটের কান্ট্রি কোড চেক
    if len(cleaned) >= 3:
        code3 = cleaned[:3]
        if code3 in countries_data:
            return countries_data[code3]["name"], countries_data[code3]["flag"]
    
    # 2 ডিজিটের কান্ট্রি কোড চেক
    if len(cleaned) >= 2:
        code2 = cleaned[:2]
        if code2 in countries_data:
            return countries_data[code2]["name"], countries_data[code2]["flag"]
    
    # 1 ডিজিটের কান্ট্রি কোড চেক
    if len(cleaned) >= 1:
        code1 = cleaned[:1]
        if code1 in countries_data:
            return countries_data[code1]["name"], countries_data[code1]["flag"]
    
    return "Unknown", "🏴‍☠️"

# --- Extract OTP Code from SMS ---
def extract_otp_code(sms_text):
    """SMS টেক্সট থেকে OTP কোড বের করে"""
    if not sms_text:
        return "N/A"
    
    patterns = [
        r'(\d{3}-\d{3})',
        r'(\d{4,8})',
        r'code[:\s]*(\d{4,8})',
        r'otp[:\s]*(\d{4,8})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, sms_text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return "N/A"

# --- Extract Service from SMS ---
def extract_service(sms_text):
    """SMS টেক্সট থেকে সার্ভিস নাম বের করে"""
    if not sms_text:
        return "Unknown"
    
    lower_text = sms_text.lower()
    for service_name, keywords in SERVICE_KEYWORDS.items():
        if any(keyword in lower_text for keyword in keywords):
            return service_name
    
    return "Unknown"

async def fetch_sms_from_api(client: httpx.AsyncClient, headers: dict, csrf_token: str, countries_data: dict):
    all_messages = []
    try:
        today = datetime.now(timezone.utc)
        start_date = today - timedelta(days=1)
        from_date_str, to_date_str = start_date.strftime('%m/%d/%Y'), today.strftime('%m/%d/%Y')
        first_payload = {'from': from_date_str, 'to': to_date_str, '_token': csrf_token}
        summary_response = await client.post(SMS_API_ENDPOINT, headers=headers, data=first_payload)
        summary_response.raise_for_status()
        summary_soup = BeautifulSoup(summary_response.text, 'html.parser')
        group_divs = summary_soup.find_all('div', {'class': 'pointer'})
        if not group_divs: return []
        
        group_ids = []
        for div in group_divs:
            onclick = div.get('onclick', '')
            match = re.search(r"getDetials\('(.+?)'\)", onclick)
            if match:
                group_ids.append(match.group(1))
        
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
                        date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                        
                        country_name_match = re.match(r'([a-zA-Z\s]+)', group_id)
                        if country_name_match:
                            country_name = country_name_match.group(1).strip()
                        else:
                            country_name = group_id.strip()
                        
                        service = extract_service(sms_text)
                        code = extract_otp_code(sms_text)
                        
                        clean_number = clean_phone_number(phone_number)
                        
                        detected_country, flag = get_country_from_number(clean_number, countries_data)
                        
                        if detected_country == "Unknown":
                            detected_country = country_name
                        
                        unique_id = f"{phone_number}-{sms_text[:50]}"
                        
                        all_messages.append({
                            "id": unique_id,
                            "time": date_str,
                            "number": phone_number,
                            "clean_number": clean_number,
                            "country": detected_country,
                            "flag": flag,
                            "service": service,
                            "code": code,
                            "full_sms": sms_text
                        })
        
        return all_messages
        
    except Exception as e:
        print(f"❌ Error fetching or processing API data: {e}")
        traceback.print_exc()
        return []

# ==================== ইউজারকে OTP পাঠানোর ফাংশন (বাটন সহ) ====================
async def send_otp_to_user(context: ContextTypes.DEFAULT_TYPE, message_data: dict):
    """OTP মেসেজ নির্দিষ্ট ইউজারকে পাঠায় (বাটন সহ)"""
    try:
        time_str = message_data.get("time", "N/A")
        number_str = message_data.get("number", "N/A")
        clean_number = message_data.get("clean_number", "")
        country_name = message_data.get("country", "N/A")
        flag_emoji = message_data.get("flag", "🏴‍☠️")
        service_name = message_data.get("service", "Unknown")
        code_str = message_data.get("code", "N/A")
        full_sms_text = message_data.get("full_sms", "N/A")
        
        # সার্ভিস ইমোজি
        service_emoji = SERVICE_EMOJIS.get(service_name, "❓")
        
        # মেসেজ ফরম্যাট (আপনার স্ক্রিনশটের মতো)
        full_message = (f"⚠️ *New OTP Received*\n\n"
                       f"📞 *Number:* `{escape_markdown(number_str)}`\n"
                       f"🔑 *Code:* `{escape_markdown(code_str)}`\n"
                       f"🏆 *Service:* {service_emoji} {escape_markdown(service_name)}\n"
                       f"🌎 *Country:* {escape_markdown(country_name)} {flag_emoji}\n"
                       f"⏳ *Time:* `{escape_markdown(time_str)}`\n\n"
                       f"💬 *Message:*\n"
                       f"{full_sms_text}")
        
        # ===== তিনটি বাটন (আপনার দেওয়া লিংক সহ) =====
        keyboard = [
            [
                InlineKeyboardButton("📞 Number Bot", url=NUMBER_BOT_LINK),
                InlineKeyboardButton("📢 Number Channel", url=NUMBER_CHANNEL_LINK)
            ],
            [
                InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_LINK)
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # JavaScript বটের active_numbers চেক
        active_numbers = load_js_active_numbers()
        
        user_info = None
        if clean_number and clean_number in active_numbers:
            user_info = active_numbers.get(clean_number)
        
        if user_info and user_info.get('userId'):
            # নির্দিষ্ট ইউজারকে পাঠান
            user_id = user_info.get('userId')
            print(f"📨 Sending OTP to user {user_id} for number {clean_number}")
            
            await context.bot.send_message(
                chat_id=user_id,
                text=full_message,
                parse_mode='MarkdownV2',
                reply_markup=reply_markup
            )
            return True
        else:
            # কোনো ইউজার না নিলে চ্যানেলে/গ্রুপে পাঠান
            print(f"ℹ️ Number {clean_number} is not active. Sending to channel/group.")
            chat_ids_to_send = load_chat_ids()
            for chat_id in chat_ids_to_send:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=full_message,
                        parse_mode='MarkdownV2',
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    print(f"❌ Error sending to chat {chat_id}: {e}")
            return True
            
    except Exception as e:
        print(f"❌ Error in send_otp_to_user: {e}")
        traceback.print_exc()
        return False

# --- Main Job ---
async def check_sms_job(context: ContextTypes.DEFAULT_TYPE):
    print(f"\n--- [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] Checking for new messages ---")
    
    # কান্ট্রি ডাটা লোড
    countries_data = load_countries()
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    saved_cookies = load_session()
    
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True, cookies=saved_cookies) as client:
        try:
            csrf_token = None
            
            if saved_cookies:
                print("🔓 Using saved session...")
                try:
                    sms_page = await client.get(BASE_URL + "/portal/sms/received", headers=headers)
                    if "login" not in str(sms_page.url):
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
                        print("⚠️ Session expired")
                        clear_session()
                except Exception as e:
                    print(f"⚠️ Session check failed: {e}")
                    clear_session()
            
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
                save_session(client.cookies)
                
                dashboard_soup = BeautifulSoup(login_res.text, 'html.parser')
                csrf_token_meta = dashboard_soup.find('meta', {'name': 'csrf-token'})
                if not csrf_token_meta:
                    print("❌ CSRF token not found after login.")
                    return
                csrf_token = csrf_token_meta.get('content')
                headers['Referer'] = str(login_res.url)

            # Fetch SMS
            messages = await fetch_sms_from_api(client, headers, csrf_token, countries_data)
            if not messages: 
                print("✔️ No new messages found.")
                return

            processed_ids = load_processed_ids()
            new_messages_found = 0
            
            for msg in reversed(messages):
                if msg["id"] not in processed_ids:
                    new_messages_found += 1
                    print(f"✔️ New message found from: {msg['number']} (Clean: {msg['clean_number']})")
                    
                    await send_otp_to_user(context, msg)
                    
                    save_processed_id(msg["id"])
                    await asyncio.sleep(1)
            
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
    keep_alive()
    print("🚀 iVasms to Telegram Bot is starting...")

    if not ADMIN_CHAT_IDS:
        print("\n!!! 🔴 WARNING: You have not correctly set admin IDs in your ADMIN_CHAT_IDS list. !!!\n")
        return

    application = Application.builder().token(YOUR_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("add_chat", add_chat_command))
    application.add_handler(CommandHandler("remove_chat", remove_chat_command))
    application.add_handler(CommandHandler("list_chats", list_chats_command))

    job_queue = application.job_queue
    job_queue.run_repeating(
        check_sms_job,
        interval=POLLING_INTERVAL_SECONDS,
        first=1,
    )

    print(f"🚀 Checking for new messages every {POLLING_INTERVAL_SECONDS} seconds.")
    print("🤖 Bot is now online. Ready to listen for commands.")
    print("⚠️ Press Ctrl+C to stop the bot.")
    
    application.run_polling()

if __name__ == "__main__":
    main()