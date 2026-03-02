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
LIVE_SMS_URL = "https://ivas.tempnum.qzz.io/portal/live/my_sms"  # ⚡ Live পেজ

USERNAME = "sagorsakh8@gmail.com"
PASSWORD = "61453812Sa@"

POLLING_INTERVAL_SECONDS = 3   # ⚡ প্রতি ৩ সেকেন্ডে Live পেজ চেক
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
    '291': ('Eritrea', '🇪🇷'), '297': ('Aruba', '🇦🇼'), '298': ('Faroe Islands', '🇫🇴'),
    '299': ('Greenland', '🇬🇱'), '30': ('Greece', '🇬🇷'), '31': ('Netherlands', '🇳🇱'),
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
    '1': ('USA/Canada', '🇺🇸'), '1242': ('Bahamas', '🇧🇸'), '1246': ('Barbados', '🇧🇧'),
    '1264': ('Anguilla', '🇦🇮'), '1268': ('Antigua and Barbuda', '🇦🇬'),
    '1345': ('Cayman Islands', '🇰🇾'), '1441': ('Bermuda', '🇧🇲'),
    '1473': ('Grenada', '🇬🇩'), '1649': ('Turks and Caicos', '🇹🇨'),
    '1664': ('Montserrat', '🇲🇸'), '1671': ('Guam', '🇬🇺'),
    '1758': ('Saint Lucia', '🇱🇨'), '1767': ('Dominica', '🇩🇲'),
    '1784': ('Saint Vincent', '🇻🇨'), '1787': ('Puerto Rico', '🇵🇷'),
    '1809': ('Dominican Republic', '🇩🇴'), '1868': ('Trinidad and Tobago', '🇹🇹'),
    '1869': ('Saint Kitts and Nevis', '🇰🇳'), '1876': ('Jamaica', '🇯🇲'),
    '52': ('Mexico', '🇲🇽'), '53': ('Cuba', '🇨🇺'), '54': ('Argentina', '🇦🇷'),
    '55': ('Brazil', '🇧🇷'), '56': ('Chile', '🇨🇱'), '57': ('Colombia', '🇨🇴'),
    '58': ('Venezuela', '🇻🇪'), '591': ('Bolivia', '🇧🇴'), '592': ('Guyana', '🇬🇾'),
    '593': ('Ecuador', '🇪🇨'), '595': ('Paraguay', '🇵🇾'), '597': ('Suriname', '🇸🇷'),
    '598': ('Uruguay', '🇺🇾'), '501': ('Belize', '🇧🇿'), '502': ('Guatemala', '🇬🇹'),
    '503': ('El Salvador', '🇸🇻'), '504': ('Honduras', '🇭🇳'), '505': ('Nicaragua', '🇳🇮'),
    '506': ('Costa Rica', '🇨🇷'), '507': ('Panama', '🇵🇦'), '509': ('Haiti', '🇭🇹'),
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
    '673': ('Brunei', '🇧🇳'), '675': ('Papua New Guinea', '🇵🇬'), '676': ('Tonga', '🇹🇴'),
    '677': ('Solomon Islands', '🇸🇧'), '678': ('Vanuatu', '🇻🇺'), '679': ('Fiji', '🇫🇯'),
    '685': ('Samoa', '🇼🇸'), '686': ('Kiribati', '🇰🇮'), '688': ('Tuvalu', '🇹🇻'),
    '689': ('French Polynesia', '🇵🇫'), '691': ('Micronesia', '🇫🇲'),
    '692': ('Marshall Islands', '🇲🇭'),
}

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
    "Amazon": ["amazon"], "Netflix": ["netflix"], "LinkedIn": ["linkedin"],
    "Microsoft": ["microsoft", "outlook", "live.com"], "Apple": ["apple", "icloud"],
    "Discord": ["discord"], "Signal": ["signal"], "Viber": ["viber"], "IMO": ["imo"],
    "PayPal": ["paypal"], "Binance": ["binance"], "Uber": ["uber"], "Bolt": ["bolt"],
    "Airbnb": ["airbnb"], "Yahoo": ["yahoo"], "Steam": ["steam"], "Blizzard": ["blizzard"],
    "Foodpanda": ["foodpanda"], "Pathao": ["pathao"], "Gmail": ["gmail"],
    "YouTube": ["youtube"], "eBay": ["ebay"], "AliExpress": ["aliexpress"],
    "Alibaba": ["alibaba"], "Flipkart": ["flipkart"], "Outlook": ["outlook"],
    "Skype": ["skype"], "Spotify": ["spotify"], "iCloud": ["icloud"], "Stripe": ["stripe"],
    "Cash App": ["cash app", "square cash"], "Venmo": ["venmo"], "Zelle": ["zelle"],
    "Wise": ["wise", "transferwise"], "Coinbase": ["coinbase"], "KuCoin": ["kucoin"],
    "Bybit": ["bybit"], "OKX": ["okx"], "Huobi": ["huobi"], "Kraken": ["kraken"],
    "MetaMask": ["metamask"], "Epic Games": ["epic games", "epicgames"],
    "PlayStation": ["playstation", "psn"], "Xbox": ["xbox"], "Twitch": ["twitch"],
    "Reddit": ["reddit"], "ProtonMail": ["protonmail", "proton"], "Zoho": ["zoho"],
    "Quora": ["quora"], "StackOverflow": ["stackoverflow"], "Indeed": ["indeed"],
    "Upwork": ["upwork"], "Fiverr": ["fiverr"], "Glassdoor": ["glassdoor"],
    "Booking.com": ["booking.com", "booking"], "Careem": ["careem"], "Swiggy": ["swiggy"],
    "Zomato": ["zomato"], "McDonald's": ["mcdonalds", "mcdonald's"], "KFC": ["kfc"],
    "Nike": ["nike"], "Adidas": ["adidas"], "Shein": ["shein"], "OnlyFans": ["onlyfans"],
    "Tinder": ["tinder"], "Bumble": ["bumble"], "Grindr": ["grindr"], "Line": ["line"],
    "WeChat": ["wechat"], "VK": ["vk", "vkontakte"], "Unknown": ["unknown"]
}

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

# --- Helper Functions ---
def parse_country_from_number(phone_number):
    clean_num = phone_number.lstrip("+0")
    for length in [4, 3, 2, 1]:
        prefix = clean_num[:length]
        if prefix in COUNTRY_CODES:
            return COUNTRY_CODES[prefix]
    return ("Unknown", "🏴‍☠️")

def parse_service_from_sms(sms_text):
    lower_sms_text = sms_text.lower()
    for service_name, keywords in SERVICE_KEYWORDS.items():
        if any(keyword in lower_sms_text for keyword in keywords):
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
            pickle.dump(cookie_list, f)
        print("💾 Session saved!")
    except Exception as e:
        print(f"⚠️ Failed to save session: {e}")

def load_session():
    if not os.path.exists(SESSION_FILE): return None
    try:
        with open(SESSION_FILE, 'rb') as f:
            cookie_list = pickle.load(f)
        return {name: value for name, value, domain, path in cookie_list}
    except: return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("🗑️ Session cleared!")

# --- Login Function ---
async def do_login(client, headers):
    """Login করে CSRF token নেওয়া"""
    try:
        print("ℹ️ Logging in...")
        login_page_res = await client.get(LOGIN_URL, headers=headers)
        soup = BeautifulSoup(login_page_res.text, 'html.parser')
        token_input = soup.find('input', {'name': '_token'})
        login_data = {'email': USERNAME, 'password': PASSWORD}
        if token_input:
            login_data['_token'] = token_input['value']

        login_res = await client.post(LOGIN_URL, data=login_data, headers=headers)

        if "login" in str(login_res.url):
            print("❌ Login failed!")
            return False

        print("✅ Login successful!")
        save_session(client.cookies)
        return True
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

# ⚡ LIVE SMS FETCH — মূল ফাংশন
async def fetch_live_sms(client: httpx.AsyncClient, headers: dict):
    """
    Live SMS পেজ থেকে সরাসরি সব OTP আনে।
    আগের মতো ৫০০০ নম্বর check করতে হয় না।
    মাত্র ১টা request = অনেক দ্রুত!
    """
    try:
        response = await client.get(LIVE_SMS_URL, headers=headers)

        # Session expire হলে login করো
        if "login" in str(response.url):
            print("⚠️ Session expired, re-logging in...")
            clear_session()
            return None  # None মানে re-login দরকার

        soup = BeautifulSoup(response.text, 'html.parser')
        messages = []

        # Live SMS table থেকে data parse করা
        # প্রতিটা row-তে: নম্বর, service, SMS content আছে
        table_rows = soup.select('table tbody tr')

        if not table_rows:
            # Alternative: div-based layout check
            live_items = soup.select('.live-sms-item, [class*="sms"], [class*="message"]')

        for row in table_rows:
            try:
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue

                # ✅ Column 1: পতাকা + দেশ + নম্বর
                # cell[0] তে দেশের নাম এবং নম্বর আছে
                cell0_text = cells[0].get_text(separator=' ', strip=True)

                # নম্বর খোঁজা — ৭-১৫ ডিজিটের number
                number_match = re.search(r'\b(\d{7,15})\b', cell0_text)
                if not number_match:
                    continue
                phone_number = number_match.group(1)

                # ✅ Column 2: Service name (WhatsApp, Telegram ইত্যাদি)
                sid_text = cells[1].get_text(separator=' ', strip=True)

                # ✅ Column 5 (index 4): Message content
                sms_text = cells[4].get_text(separator=' ', strip=True)
                if not sms_text or len(sms_text) < 3:
                    continue

                date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                country_name, flag = parse_country_from_number(phone_number)

                # Service — প্রথমে SID column দেখো, তারপর SMS text
                service = sid_text if sid_text else parse_service_from_sms(sms_text)
                if not service or service == "Unknown":
                    service = parse_service_from_sms(sms_text)

                code = parse_code_from_sms(sms_text)
                unique_id = f"{phone_number}-{sms_text}"

                messages.append({
                    "id": unique_id,
                    "time": date_str,
                    "number": phone_number,
                    "country": country_name,
                    "flag": flag,
                    "service": service,
                    "code": code,
                    "full_sms": sms_text
                })

            except Exception as e:
                continue

        return messages

    except httpx.RequestError as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Error fetching live SMS: {e}")
        traceback.print_exc()
        return []

# --- Telegram Message Sender ---
async def send_telegram_message(context: ContextTypes.DEFAULT_TYPE, chat_id: str, message_data: dict):
    try:
        time_str = message_data.get("time", "N/A")
        number_str = message_data.get("number", "N/A")
        country_name = message_data.get("country", "N/A")
        flag_emoji = message_data.get("flag", "🏴‍☠️")
        service_name = message_data.get("service", "N/A")
        code_str = message_data.get("code", "N/A")
        full_sms_text = message_data.get("full_sms", "N/A")
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

        await context.bot.send_message(
            chat_id=chat_id,
            text=full_message,
            parse_mode='MarkdownV2',
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"❌ Error sending to {chat_id}: {e}")

# --- Command Handlers ---
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
            await update.message.reply_text(f"🤔 Chat ID ({chat_id_to_remove}) not found.")
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
        except:
            await update.message.reply_text("📜 Chat IDs:\n" + "\n".join(map(str, chat_ids)))
    else:
        await update.message.reply_text("No chat IDs registered.")

# --- Main Job ---
async def check_sms_job(context: ContextTypes.DEFAULT_TYPE):
    print(f"\n⚡ [{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Checking Live SMS...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    saved_cookies = load_session()

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True, cookies=saved_cookies) as client:
        try:
            # Session না থাকলে login করো
            if not saved_cookies:
                success = await do_login(client, headers)
                if not success:
                    return

            # ⚡ Live SMS পেজ থেকে সরাসরি OTP আনো
            messages = await fetch_live_sms(client, headers)

            # None মানে session expire — re-login করো
            if messages is None:
                clear_session()
                success = await do_login(client, headers)
                if not success:
                    return
                messages = await fetch_live_sms(client, headers) or []

            if not messages:
                print("✔️ No new messages.")
                return

            processed_ids = load_processed_ids()
            chat_ids_to_send = load_chat_ids()
            new_count = 0

            for msg in messages:
                if msg["id"] not in processed_ids:
                    new_count += 1
                    print(f"✅ New OTP from: {msg['number']} | {msg['service']}")
                    for chat_id in chat_ids_to_send:
                        await send_telegram_message(context, chat_id, msg)
                    save_processed_id(msg["id"])

            if new_count > 0:
                print(f"📨 Sent {new_count} new OTP(s) to Telegram!")

        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            clear_session()

# --- Main ---
def main():
    keep_alive()
    print("🚀 Bot starting...")
    print(f"⚡ Using LIVE SMS page — checking every {POLLING_INTERVAL_SECONDS} seconds")
    print(f"🔗 Live URL: {LIVE_SMS_URL}")

    if not ADMIN_CHAT_IDS:
        print("🔴 WARNING: No admin IDs set!")
        return

    application = Application.builder().token(YOUR_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("add_chat", add_chat_command))
    application.add_handler(CommandHandler("remove_chat", remove_chat_command))
    application.add_handler(CommandHandler("list_chats", list_chats_command))

    job_queue = application.job_queue
    job_queue.run_repeating(check_sms_job, interval=POLLING_INTERVAL_SECONDS, first=1)

    print("🤖 Bot is online!")
    application.run_polling()

if __name__ == "__main__":
    main()
