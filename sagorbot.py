# -*- coding: utf-8 -*-
import asyncio, re, httpx, json, os, traceback, pickle
from bs4 import BeautifulSoup
from flask import Flask
import threading
from datetime import datetime, timezone
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

flask_app = Flask(__name__)
@flask_app.route("/")
def home(): return "Bot is alive!"
def keep_alive():
    t = threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=8080))
    t.daemon = True; t.start()

BOT_TOKEN      = "8393297595:AAEksSfupLmn5qeBxjoGT3c9IzaJaLI6mck"
ADMIN_IDS      = ["7095358778"]
INITIAL_CHATS  = ["-1003719868322"]
BASE_URL       = "https://ivas.tempnum.qzz.io"
LOGIN_URL      = f"{BASE_URL}/login"
SMS_PAGE_URL   = f"{BASE_URL}/portal/sms/received"
GETSMS_URL     = f"{BASE_URL}/portal/sms/received/getsms"
GETNUM_URL     = f"{BASE_URL}/portal/sms/received/getsms/number"
GETSMS2_URL    = f"{BASE_URL}/portal/sms/received/getsms/number/sms"
USERNAME       = "sagorsakh384@gmail.com"
PASSWORD       = "61453812Sa@"
INTERVAL       = 12
STATE_FILE     = "processed.json"
CHATS_FILE     = "chats.json"
SESSION_FILE   = "session.pkl"

COUNTRY_CODES = {
    '20':('Egypt','🇪🇬'),'212':('Morocco','🇲🇦'),'213':('Algeria','🇩🇿'),
    '216':('Tunisia','🇹🇳'),'218':('Libya','🇱🇾'),'220':('Gambia','🇬🇲'),
    '221':('Senegal','🇸🇳'),'222':('Mauritania','🇲🇷'),'223':('Mali','🇲🇱'),
    '224':('Guinea','🇬🇳'),'225':("Cote d'Ivoire",'🇨🇮'),'226':('Burkina Faso','🇧🇫'),
    '227':('Niger','🇳🇪'),'228':('Togo','🇹🇬'),'229':('Benin','🇧🇯'),
    '230':('Mauritius','🇲🇺'),'231':('Liberia','🇱🇷'),'232':('Sierra Leone','🇸🇱'),
    '233':('Ghana','🇬🇭'),'234':('Nigeria','🇳🇬'),'235':('Chad','🇹🇩'),
    '236':('CAR','🇨🇫'),'237':('Cameroon','🇨🇲'),'238':('Cape Verde','🇨🇻'),
    '240':('Equatorial Guinea','🇬🇶'),'241':('Gabon','🇬🇦'),'242':('Congo','🇨🇬'),
    '243':('DR Congo','🇨🇩'),'244':('Angola','🇦🇴'),'245':('Guinea-Bissau','🇬🇼'),
    '248':('Seychelles','🇸🇨'),'249':('Sudan','🇸🇩'),'250':('Rwanda','🇷🇼'),
    '251':('Ethiopia','🇪🇹'),'252':('Somalia','🇸🇴'),'253':('Djibouti','🇩🇯'),
    '254':('Kenya','🇰🇪'),'255':('Tanzania','🇹🇿'),'256':('Uganda','🇺🇬'),
    '257':('Burundi','🇧🇮'),'258':('Mozambique','🇲🇿'),'260':('Zambia','🇿🇲'),
    '261':('Madagascar','🇲🇬'),'263':('Zimbabwe','🇿🇼'),'264':('Namibia','🇳🇦'),
    '265':('Malawi','🇲🇼'),'266':('Lesotho','🇱🇸'),'267':('Botswana','🇧🇼'),
    '268':('Eswatini','🇸🇿'),'269':('Comoros','🇰🇲'),'27':('South Africa','🇿🇦'),
    '291':('Eritrea','🇪🇷'),'30':('Greece','🇬🇷'),'31':('Netherlands','🇳🇱'),
    '32':('Belgium','🇧🇪'),'33':('France','🇫🇷'),'34':('Spain','🇪🇸'),
    '350':('Gibraltar','🇬🇮'),'351':('Portugal','🇵🇹'),'352':('Luxembourg','🇱🇺'),
    '353':('Ireland','🇮🇪'),'354':('Iceland','🇮🇸'),'355':('Albania','🇦🇱'),
    '356':('Malta','🇲🇹'),'357':('Cyprus','🇨🇾'),'358':('Finland','🇫🇮'),
    '359':('Bulgaria','🇧🇬'),'36':('Hungary','🇭🇺'),'370':('Lithuania','🇱🇹'),
    '371':('Latvia','🇱🇻'),'372':('Estonia','🇪🇪'),'373':('Moldova','🇲🇩'),
    '374':('Armenia','🇦🇲'),'375':('Belarus','🇧🇾'),'376':('Andorra','🇦🇩'),
    '377':('Monaco','🇲🇨'),'380':('Ukraine','🇺🇦'),'381':('Serbia','🇷🇸'),
    '382':('Montenegro','🇲🇪'),'383':('Kosovo','🇽🇰'),'385':('Croatia','🇭🇷'),
    '386':('Slovenia','🇸🇮'),'387':('Bosnia','🇧🇦'),'389':('N. Macedonia','🇲🇰'),
    '39':('Italy','🇮🇹'),'40':('Romania','🇷🇴'),'41':('Switzerland','🇨🇭'),
    '420':('Czech Republic','🇨🇿'),'421':('Slovakia','🇸🇰'),'423':('Liechtenstein','🇱🇮'),
    '43':('Austria','🇦🇹'),'44':('UK','🇬🇧'),'45':('Denmark','🇩🇰'),
    '46':('Sweden','🇸🇪'),'47':('Norway','🇳🇴'),'48':('Poland','🇵🇱'),
    '49':('Germany','🇩🇪'),'1':('USA/Canada','🇺🇸'),'52':('Mexico','🇲🇽'),
    '53':('Cuba','🇨🇺'),'54':('Argentina','🇦🇷'),'55':('Brazil','🇧🇷'),
    '56':('Chile','🇨🇱'),'57':('Colombia','🇨🇴'),'58':('Venezuela','🇻🇪'),
    '591':('Bolivia','🇧🇴'),'592':('Guyana','🇬🇾'),'593':('Ecuador','🇪🇨'),
    '595':('Paraguay','🇵🇾'),'597':('Suriname','🇸🇷'),'598':('Uruguay','🇺🇾'),
    '501':('Belize','🇧🇿'),'502':('Guatemala','🇬🇹'),'503':('El Salvador','🇸🇻'),
    '504':('Honduras','🇭🇳'),'505':('Nicaragua','🇳🇮'),'506':('Costa Rica','🇨🇷'),
    '507':('Panama','🇵🇦'),'509':('Haiti','🇭🇹'),'1242':('Bahamas','🇧🇸'),
    '1246':('Barbados','🇧🇧'),'1345':('Cayman Islands','🇰🇾'),'1441':('Bermuda','🇧🇲'),
    '1473':('Grenada','🇬🇩'),'1758':('Saint Lucia','🇱🇨'),'1767':('Dominica','🇩🇲'),
    '1784':('Saint Vincent','🇻🇨'),'1787':('Puerto Rico','🇵🇷'),'1809':('Dominican Rep.','🇩🇴'),
    '1868':('Trinidad & Tobago','🇹🇹'),'1876':('Jamaica','🇯🇲'),'7':('Russia','🇷🇺'),
    '77':('Kazakhstan','🇰🇿'),'81':('Japan','🇯🇵'),'82':('South Korea','🇰🇷'),
    '84':('Vietnam','🇻🇳'),'86':('China','🇨🇳'),'880':('Bangladesh','🇧🇩'),
    '886':('Taiwan','🇹🇼'),'90':('Turkey','🇹🇷'),'91':('India','🇮🇳'),
    '92':('Pakistan','🇵🇰'),'93':('Afghanistan','🇦🇫'),'94':('Sri Lanka','🇱🇰'),
    '95':('Myanmar','🇲🇲'),'960':('Maldives','🇲🇻'),'961':('Lebanon','🇱🇧'),
    '962':('Jordan','🇯🇴'),'963':('Syria','🇸🇾'),'964':('Iraq','🇮🇶'),
    '965':('Kuwait','🇰🇼'),'966':('Saudi Arabia','🇸🇦'),'967':('Yemen','🇾🇪'),
    '968':('Oman','🇴🇲'),'970':('Palestine','🇵🇸'),'971':('UAE','🇦🇪'),
    '972':('Israel','🇮🇱'),'973':('Bahrain','🇧🇭'),'974':('Qatar','🇶🇦'),
    '975':('Bhutan','🇧🇹'),'976':('Mongolia','🇲🇳'),'977':('Nepal','🇳🇵'),
    '98':('Iran','🇮🇷'),'992':('Tajikistan','🇹🇯'),'993':('Turkmenistan','🇹🇲'),
    '994':('Azerbaijan','🇦🇿'),'995':('Georgia','🇬🇪'),'996':('Kyrgyzstan','🇰🇬'),
    '998':('Uzbekistan','🇺🇿'),'60':('Malaysia','🇲🇾'),'61':('Australia','🇦🇺'),
    '62':('Indonesia','🇮🇩'),'63':('Philippines','🇵🇭'),'64':('New Zealand','🇳🇿'),
    '65':('Singapore','🇸🇬'),'66':('Thailand','🇹🇭'),'670':('East Timor','🇹🇱'),
    '673':('Brunei','🇧🇳'),'675':('Papua New Guinea','🇵🇬'),'679':('Fiji','🇫🇯'),
    '850':('North Korea','🇰🇵'),'852':('Hong Kong','🇭🇰'),'853':('Macau','🇲🇴'),
    '855':('Cambodia','🇰🇭'),'856':('Laos','🇱🇦'),
}
SERVICE_KEYS = {
    "WhatsApp":["whatsapp","واتساب"],"Telegram":["telegram","تيليجرام"],
    "Facebook":["facebook"],"Google":["google","gmail"],
    "Instagram":["instagram"],"Twitter":["twitter"],
    "TikTok":["tiktok"],"Snapchat":["snapchat"],
    "Amazon":["amazon"],"Netflix":["netflix"],
    "LinkedIn":["linkedin"],"Microsoft":["microsoft","outlook"],
    "Apple":["apple","icloud"],"Discord":["discord"],"Signal":["signal"],
    "Viber":["viber"],"PayPal":["paypal"],"Binance":["binance"],
    "Uber":["uber"],"Spotify":["spotify"],"Coinbase":["coinbase"],
    "Steam":["steam"],"Reddit":["reddit"],"Tinder":["tinder"],
}
SERVICE_EMOJI = {
    "Telegram":"📩","WhatsApp":"🟢","Facebook":"📘","Instagram":"📸",
    "Google":"🔍","Twitter":"🐦","TikTok":"🎵","Snapchat":"👻",
    "Amazon":"🛒","Microsoft":"🪟","Netflix":"🎬","Spotify":"🎶",
    "Apple":"🍏","PayPal":"💰","Binance":"🪙","Discord":"🗨️",
    "Steam":"🎮","LinkedIn":"💼","Uber":"🚗","Tinder":"🔥",
    "Signal":"🔐","Viber":"📞","Reddit":"👽","Unknown":"❓",
}

def get_country(number):
    n = number.lstrip("+0")
    for l in [4,3,2,1]:
        if n[:l] in COUNTRY_CODES: return COUNTRY_CODES[n[:l]]
    return ("Unknown","🏴‍☠️")

def get_service(sender, msg_text):
    combined = (sender + " " + msg_text).lower()
    for svc, keys in SERVICE_KEYS.items():
        if any(k in combined for k in keys): return svc
    return "Unknown"

def get_code(text):
    m = (re.search(r'\b([A-Z0-9]{4,8}\+[A-Za-z0-9]{3,8})\b', text) or
         re.search(r'(\d{3}-\d{3})', text) or
         re.search(r'\b(\d{4,8})\b', text))
    return m.group(1) if m else "N/A"

def mask_number(phone):
    if len(phone) <= 9: return phone
    start, end = phone[:6], phone[-3:]
    mid_len = len(phone) - 9
    mask_chars = ['Ⓨ','Ⓞ','Ⓤ','Ⓐ','Ⓑ','Ⓒ','Ⓓ']
    mask = ''.join(mask_chars[:mid_len]) if mid_len <= 7 else '●' * mid_len
    return f"{start}{mask}{end}"

def esc(text):
    return re.sub(r'([\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])', r'\\\1', str(text))

def load_ids():
    try: return set(json.load(open(STATE_FILE))) if os.path.exists(STATE_FILE) else set()
    except: return set()

def save_id(sid):
    ids = load_ids(); ids.add(sid)
    json.dump(list(ids), open(STATE_FILE,'w'))

def load_chats():
    if not os.path.exists(CHATS_FILE):
        json.dump(INITIAL_CHATS, open(CHATS_FILE,'w'))
        return INITIAL_CHATS
    try: return json.load(open(CHATS_FILE))
    except: return INITIAL_CHATS

def save_chats(c): json.dump(c, open(CHATS_FILE,'w'), indent=2)

def save_session(cookies):
    try: pickle.dump([(c.name,c.value,c.domain,c.path) for c in cookies.jar], open(SESSION_FILE,'wb'))
    except: pass

def load_session():
    if not os.path.exists(SESSION_FILE): return None
    try: return {n:v for n,v,d,p in pickle.load(open(SESSION_FILE,'rb'))}
    except: return None

def clear_session():
    if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    'X-Requested-With': 'XMLHttpRequest',
}

async def do_login(client):
    try:
        page = await client.get(LOGIN_URL, headers=HEADERS)
        soup = BeautifulSoup(page.text, 'html.parser')
        el = soup.find('input', {'name': '_token'})
        res = await client.post(LOGIN_URL, data={
            'email': USERNAME, 'password': PASSWORD,
            '_token': el['value'] if el else ''
        }, headers=HEADERS)
        if 'login' in str(res.url): print("❌ Login failed!"); return False
        print("✅ Login success!")
        save_session(client.cookies)
        return True
    except Exception as e:
        print(f"❌ Login error: {e}"); return False

async def get_csrf(client):
    try:
        page = await client.get(SMS_PAGE_URL, headers=HEADERS)
        if 'login' in str(page.url): return None
        soup = BeautifulSoup(page.text, 'html.parser')
        meta = soup.find('meta', {'name': 'csrf-token'})
        if meta: return meta.get('content')
        el = soup.find('input', {'name': '_token'})
        return el['value'] if el else None
    except: return None

# ===== Step 1: Range list থেকে id+safe বের করা =====
def parse_ranges(html):
    """
    onclick="toggleRange('CAMBODIA 893', 'CAMBODIA_893')"
    → [{"id": "CAMBODIA 893", "safe": "CAMBODIA_893"}, ...]
    """
    soup = BeautifulSoup(html, 'html.parser')
    ranges = []
    for el in soup.find_all(onclick=True):
        m = re.search(r"toggleRange\(['\"](.+?)['\"],\s*['\"](.+?)['\"]\)", el.get('onclick',''))
        if m:
            ranges.append({"id": m.group(1), "safe": m.group(2)})
    # Deduplicate
    seen = set()
    unique = []
    for r in ranges:
        if r['id'] not in seen:
            seen.add(r['id']); unique.append(r)
    return unique

# ===== Step 2: একটা range-এর numbers আনা =====
async def fetch_numbers(client, today, range_id, csrf):
    try:
        r = await client.post(GETNUM_URL,
            data={'start': today, 'end': today, 'range': range_id, '_token': csrf},
            headers=HEADERS, timeout=15.0)
        soup = BeautifulSoup(r.text, 'html.parser')

        phones = []
        # .nrow থেকে
        for el in soup.find_all(class_='nrow'):
            nnum = el.find(class_='nnum')
            if nnum:
                t = re.sub(r'\D', '', nnum.get_text(strip=True))
                if t: phones.append(t)

        # onclick থেকে
        if not phones:
            for el in soup.find_all(onclick=True):
                m = re.search(r"toggleNumber\(['\"](\d{7,15})['\"]", el.get('onclick',''))
                if m: phones.append(m.group(1))

        # সব standalone number
        if not phones:
            for s in soup.stripped_strings:
                s = s.strip()
                if re.match(r'^\+?\d{7,15}$', s):
                    phones.append(re.sub(r'\D','',s))

        print(f"   📱 Range '{range_id}': {len(set(phones))} numbers")
        return list(set(phones))
    except Exception as e:
        print(f"   ⚠️ Number fetch error '{range_id}': {e}")
        return []

# ===== Step 3: একটা number-এর SMS আনা =====
async def fetch_sms(client, today, phone, range_id, csrf):
    try:
        r = await client.post(GETSMS2_URL,
            data={'start': today, 'end': today, 'Number': phone, 'Range': range_id, '_token': csrf},
            headers=HEADERS, timeout=15.0)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = []

        # নতুন UI: .cli-tag + .msg-text
        cli_tags = soup.find_all(class_='cli-tag')
        msg_texts = soup.find_all(class_='msg-text')

        for i, msg_el in enumerate(msg_texts):
            msg_text = msg_el.get_text(separator=' ', strip=True)
            if not msg_text or len(msg_text) < 5: continue

            sender = cli_tags[i].get_text(strip=True) if i < len(cli_tags) else ""

            country, flag = get_country(phone)
            service = get_service(sender, msg_text)
            results.append({
                "id": f"{phone}-{msg_text[:60]}",
                "time": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                "number": phone, "country": country, "flag": flag,
                "sender": sender, "service": service,
                "code": get_code(msg_text), "full_sms": msg_text,
            })

        # Fallback: card-body
        if not results:
            for card in soup.find_all('div', class_='card-body'):
                p = card.find('p', class_='mb-0') or card.find('p')
                if not p: continue
                msg_text = p.get_text(separator=' ', strip=True)
                if not msg_text or len(msg_text) < 5: continue
                if re.match(r'^[\d\s\.\,]+$', msg_text): continue
                cli_el = soup.find(string=re.compile(
                    r'WhatsApp|Telegram|Facebook|Google|Instagram|Signal', re.I))
                sender = str(cli_el).strip() if cli_el else ""
                country, flag = get_country(phone)
                results.append({
                    "id": f"{phone}-{msg_text[:60]}",
                    "time": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                    "number": phone, "country": country, "flag": flag,
                    "sender": sender, "service": get_service(sender, msg_text),
                    "code": get_code(msg_text), "full_sms": msg_text,
                })

        return results
    except Exception as e:
        print(f"   ⚠️ SMS error {phone}: {e}")
        return []

# ===== MAIN FETCH — Parallel =====
async def fetch_all_sms(client, csrf):
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        # Step 1: getsms → range list
        r1 = await client.post(GETSMS_URL,
            data={'from': today, 'to': today, '_token': csrf},
            headers=HEADERS, timeout=20.0)
        if 'login' in str(r1.url): return None

        ranges = parse_ranges(r1.text)
        print(f"   📦 Found {len(ranges)} ranges: {[r['id'] for r in ranges]}")
        if not ranges: return []

        # Step 2: সব range-এর numbers একসাথে (parallel)
        num_tasks = [fetch_numbers(client, today, r['id'], csrf) for r in ranges]
        num_results = await asyncio.gather(*num_tasks, return_exceptions=True)

        # Step 3: সব numbers-এর SMS একসাথে (parallel)
        sms_tasks = []
        for i, phones in enumerate(num_results):
            if isinstance(phones, list):
                rid = ranges[i]['id']
                for phone in phones:
                    sms_tasks.append(fetch_sms(client, today, phone, rid, csrf))

        if not sms_tasks:
            print("   ⚠️ No numbers found in any range")
            return []

        sms_results = await asyncio.gather(*sms_tasks, return_exceptions=True)

        all_msgs = []
        for r in sms_results:
            if isinstance(r, list): all_msgs.extend(r)

        # Duplicate সরানো
        seen, unique = set(), []
        for m in all_msgs:
            if m['id'] not in seen:
                seen.add(m['id']); unique.append(m)

        print(f"   ✅ Total: {len(unique)} SMS found")
        return unique

    except Exception as e:
        print(f"❌ Fetch error: {e}"); traceback.print_exc(); return []

async def send_otp(bot, chat_id, msg):
    try:
        emoji  = SERVICE_EMOJI.get(msg['service'], '❓')
        masked = mask_number(msg['number'])
        text = (
            f"🔔 *New OTP Received*\n\n"
            f"📞 *Number:* `{esc(masked)}`\n"
            f"🔑 *Code:* `{esc(msg['code'])}`\n"
            f"🏆 *Service:* {emoji} {esc(msg['service'])}\n"
            f"🌎 *Country:* {esc(msg['country'])} {msg['flag']}\n"
            f"⏳ *Time:* `{esc(msg['time'])}`\n\n"
            f"💬 *Message:*\n`{esc(msg['full_sms'])}`"
        )
        kb = [
            [InlineKeyboardButton("🤖 Number Bot", url="https://t.me/ah_method_number_bot"),
             InlineKeyboardButton("📢 Number Channel", url="https://t.me/blackotpnum")],
            [InlineKeyboardButton("🛠 Developer", url="https://t.me/EarningHub6112")]
        ]
        await bot.send_message(chat_id=chat_id, text=text,
            parse_mode='MarkdownV2', reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        print(f"❌ Send error {chat_id}: {e}")
        try:
            plain = (f"🔔 New OTP Received\n\n"
                     f"📞 Number: {mask_number(msg['number'])}\n"
                     f"🔑 Code: {msg['code']}\n"
                     f"🏆 Service: {msg['service']}\n"
                     f"🌎 Country: {msg['country']} {msg['flag']}\n"
                     f"⏳ Time: {msg['time']}\n\n"
                     f"💬 Message:\n{msg['full_sms']}")
            await bot.send_message(chat_id=chat_id, text=plain)
        except: pass

async def start_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if str(u.message.from_user.id) in ADMIN_IDS:
        await u.message.reply_text("✅ Bot running!\n/add_chat <id>\n/remove_chat <id>\n/list_chats")
    else: await u.message.reply_text("❌ Not authorized.")

async def add_chat_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if str(u.message.from_user.id) not in ADMIN_IDS: return
    try:
        cid = c.args[0]; chats = load_chats()
        if cid not in chats: chats.append(cid); save_chats(chats); await u.message.reply_text(f"✅ Added: {cid}")
        else: await u.message.reply_text("⚠️ Already exists.")
    except: await u.message.reply_text("Usage: /add_chat <chat_id>")

async def rm_chat_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if str(u.message.from_user.id) not in ADMIN_IDS: return
    try:
        cid = c.args[0]; chats = load_chats()
        if cid in chats: chats.remove(cid); save_chats(chats); await u.message.reply_text(f"✅ Removed: {cid}")
        else: await u.message.reply_text("❌ Not found.")
    except: await u.message.reply_text("Usage: /remove_chat <chat_id>")

async def list_cmd(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if str(u.message.from_user.id) not in ADMIN_IDS: return
    chats = load_chats()
    await u.message.reply_text("📋 Chats:\n" + "\n".join(chats) if chats else "Empty.")

async def check_sms(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(timezone.utc).strftime('%H:%M:%S')
    print(f"⚡ [{now}] Checking SMS...")
    cookies = load_session()
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, cookies=cookies) as client:
        try:
            if not cookies:
                if not await do_login(client): return
            csrf = await get_csrf(client)
            if not csrf:
                print("⚠️ Session expired, re-logging...")
                clear_session()
                if not await do_login(client): return
                csrf = await get_csrf(client)
                if not csrf: print("❌ CSRF failed!"); return

            messages = await fetch_all_sms(client, csrf)
            if messages is None: clear_session(); return
            if not messages: print("✔️ No SMS today."); return

            done = load_ids(); chats = load_chats(); new = 0
            for msg in messages:
                if msg['id'] not in done:
                    new += 1
                    print(f"✅ NEW: {msg['number']} | {msg['service']} | {msg['code']}")
                    for cid in chats: await send_otp(context.bot, cid, msg)
                    save_id(msg['id'])

            if new > 0: print(f"📨 Sent {new} new OTP(s)!")
            else: print("✔️ No new OTP.")
        except Exception as e:
            print(f"❌ Error: {e}"); traceback.print_exc(); clear_session()

def main():
    keep_alive()
    print("🚀 Bot v3.1 — Fixed toggleRange API")
    print(f"   Step 1: getsms → parse toggleRange('id','safe')")
    print(f"   Step 2: getsms/number?range=id → phone numbers")
    print(f"   Step 3: getsms/number/sms → .cli-tag + .msg-text")
    print(f"   Interval: {INTERVAL}s | Parallel: ✅")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",       start_cmd))
    app.add_handler(CommandHandler("add_chat",    add_chat_cmd))
    app.add_handler(CommandHandler("remove_chat", rm_chat_cmd))
    app.add_handler(CommandHandler("list_chats",  list_cmd))
    app.job_queue.run_repeating(check_sms, interval=INTERVAL, first=2,
        job_kwargs={"max_instances": 1})
    print("🤖 Bot is online!")
    app.run_polling()

if __name__ == "__main__":
    main()
