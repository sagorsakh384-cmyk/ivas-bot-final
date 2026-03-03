# -*- coding: utf-8 -*-
import asyncio, re, httpx, json, os, traceback, pickle
from bs4 import BeautifulSoup
from flask import Flask
import threading
from datetime import datetime, timezone
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

# ===== KEEP ALIVE =====
flask_app = Flask(__name__)
@flask_app.route("/")
def home(): return "Bot is alive!"
def keep_alive():
    t = threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=8080))
    t.daemon = True; t.start()

# ===== CONFIG =====
BOT_TOKEN      = "8393297595:AAEksSfupLmn5qeBxjoGT3c9IzaJaLI6mck"
ADMIN_IDS      = ["7095358778"]
INITIAL_CHATS  = ["-1003007557624"]
BASE_URL       = "https://ivas.tempnum.qzz.io"
LOGIN_URL      = f"{BASE_URL}/login"
SMS_PAGE_URL   = f"{BASE_URL}/portal/sms/received"
GETSMS_URL     = f"{BASE_URL}/portal/sms/received/getsms"
GETNUM_URL     = f"{BASE_URL}/portal/sms/received/getsms/number"
GETSMS2_URL    = f"{BASE_URL}/portal/sms/received/getsms/number/sms"
USERNAME       = "sagorsakh384@gmail.com"
PASSWORD       = "61453812Sa@"
INTERVAL       = 5
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
    "Instagram":["instagram"],"Twitter":["twitter"],"TikTok":["tiktok"],
    "Snapchat":["snapchat"],"Amazon":["amazon"],"Netflix":["netflix"],
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

def get_service(text):
    t = text.lower()
    for svc, keys in SERVICE_KEYS.items():
        if any(k in t for k in keys): return svc
    return "Unknown"

def get_code(text):
    m = re.search(r'(\d{3}-\d{3})',text) or re.search(r'\b(\d{4,8})\b',text)
    return m.group(1) if m else "N/A"

def esc(text):
    return re.sub(r'([\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])',r'\\\1',str(text))

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
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept':'text/html,application/xhtml+xml,*/*;q=0.8',
    'Accept-Language':'en-US,en;q=0.5',
    'X-Requested-With':'XMLHttpRequest',
}

async def do_login(client):
    try:
        page = await client.get(LOGIN_URL, headers=HEADERS)
        soup = BeautifulSoup(page.text,'html.parser')
        el = soup.find('input',{'name':'_token'})
        res = await client.post(LOGIN_URL, data={
            'email':USERNAME,'password':PASSWORD,
            '_token':el['value'] if el else ''
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
        soup = BeautifulSoup(page.text,'html.parser')
        el = soup.find('input',{'name':'_token'})
        return el['value'] if el else None
    except: return None

# ===== ⚡ PARALLEL: একটা নম্বরের SMS =====
async def fetch_sms_for_number(client, today, phone, gid, csrf):
    try:
        r = await client.post(GETSMS2_URL,
            data={'start':today,'end':today,'Number':phone,'Range':gid,'_token':csrf},
            headers=HEADERS, timeout=15.0)
        soup = BeautifulSoup(r.text,'html.parser')
        results = []

        # CLI / service খোঁজা
        cli_el = soup.find(string=re.compile(
            r'WhatsApp|Telegram|Facebook|Google|Instagram|Signal|Viber|TikTok|Snapchat', re.I))

        # card-body থেকে SMS text
        cards = soup.find_all('div', class_='card-body')

        if not cards:
            # Fallback — full text থেকে
            full_text = soup.get_text(separator=' ', strip=True)
            mc_idx = full_text.find('Message Content')
            if mc_idx > 0:
                sms_part = full_text[mc_idx+14:mc_idx+400].strip()
                rev_idx = sms_part.find('Rev.')
                if rev_idx > 0: sms_part = sms_part[:rev_idx].strip()
                if len(sms_part) > 10 and not re.match(r'^[\d\s\.\,]+$', sms_part):
                    service = get_service((str(cli_el) if cli_el else '') + ' ' + sms_part)
                    country, flag = get_country(phone)
                    results.append({
                        "id": f"{phone}-{sms_part[:60]}",
                        "time": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                        "number": phone,"country": country,"flag": flag,
                        "service": service,"code": get_code(sms_part),"full_sms": sms_part
                    })
            return results

        for card in cards:
            sms_el = card.find('p', class_='mb-0') or card.find('p')
            sms_text = sms_el.get_text(separator=' ', strip=True) if sms_el else card.get_text(separator=' ', strip=True)
            if not sms_text or len(sms_text) < 10: continue
            if re.match(r'^[\d\s\.\,]+$', sms_text): continue

            service = get_service((str(cli_el) if cli_el else '') + ' ' + sms_text)
            country, flag = get_country(phone)
            results.append({
                "id": f"{phone}-{sms_text[:60]}",
                "time": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                "number": phone,"country": country,"flag": flag,
                "service": service,"code": get_code(sms_text),"full_sms": sms_text
            })
        return results
    except Exception as e:
        print(f"   ⚠️ SMS error {phone}: {e}")
        return []

# ===== ⚡ PARALLEL: একটা range-এর সব নম্বর =====
async def fetch_numbers_for_range(client, today, gid, csrf):
    try:
        r = await client.post(GETNUM_URL,
            data={'start':today,'end':today,'range':gid,'_token':csrf},
            headers=HEADERS, timeout=15.0)
        soup = BeautifulSoup(r.text,'html.parser')

        phones = []
        for el in soup.select("div[onclick*='getDetialsNumber']"):
            t = el.get_text(strip=True)
            if re.match(r'^\+?\d{7,15}$', t.replace(' ','')):
                phones.append(re.sub(r'\D','',t))

        if not phones:
            for s in soup.stripped_strings:
                s = s.strip()
                if re.match(r'^\+?\d{7,15}$', s.replace(' ','')):
                    phones.append(re.sub(r'\D','',s))

        phones = list(set(phones))
        print(f"   📱 Range {gid}: {len(phones)} numbers → fetching parallel...")

        if not phones: return []

        # ⚡ সব নম্বরের SMS একসাথে!
        tasks = [fetch_sms_for_number(client, today, p, gid, csrf) for p in phones]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_msgs = []
        for r in results:
            if isinstance(r, list): all_msgs.extend(r)
        return all_msgs
    except Exception as e:
        print(f"   ⚠️ Range {gid} error: {e}")
        return []

# ===== ⚡ MAIN FETCH =====
async def fetch_all_sms(client, csrf):
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        # Step 1: Range list
        r1 = await client.post(GETSMS_URL,
            data={'from':today,'to':today,'_token':csrf},
            headers=HEADERS, timeout=15.0)
        if 'login' in str(r1.url): return None

        soup1 = BeautifulSoup(r1.text,'html.parser')

        group_ids = []
        for el in soup1.find_all(onclick=True):
            m = re.search(r"getDetials\(['\"](.+?)['\"]\)", el.get('onclick',''))
            if m and m.group(1) not in group_ids:
                group_ids.append(m.group(1))
        if not group_ids:
            for el in soup1.find_all(attrs={'data-range':True}):
                if el['data-range'] not in group_ids:
                    group_ids.append(el['data-range'])
        if not group_ids:
            for el in soup1.find_all(class_=lambda c: c and 'pointer' in c):
                t = el.get_text(strip=True)
                if t and t not in group_ids: group_ids.append(t)

        print(f"   📦 Found {len(group_ids)} ranges: {group_ids}")
        if not group_ids: return []

        # ⚡ Step 2+3: সব range একসাথে parallel!
        tasks = [fetch_numbers_for_range(client, today, gid, csrf) for gid in group_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_msgs = []
        for r in results:
            if isinstance(r, list): all_msgs.extend(r)

        # Duplicate সরানো
        seen, unique = set(), []
        for m in all_msgs:
            if m['id'] not in seen:
                seen.add(m['id']); unique.append(m)

        print(f"   ✅ Total: {len(unique)} SMS fetched")
        return unique
    except Exception as e:
        print(f"❌ Fetch error: {e}"); traceback.print_exc(); return []

# ===== TELEGRAM =====
async def send_otp(bot, chat_id, msg):
    try:
        emoji = SERVICE_EMOJI.get(msg['service'],'❓')
        text = (
            f"🔔 *You have successfully received OTP*\n\n"
            f"📞 *Number:* `{esc(msg['number'])}`\n"
            f"🔑 *Code:* `{esc(msg['code'])}`\n"
            f"🏆 *Service:* {emoji} {esc(msg['service'])}\n"
            f"🌎 *Country:* {esc(msg['country'])} {msg['flag']}\n"
            f"⏳ *Time:* `{esc(msg['time'])}`\n\n"
            f"💬 *Message:*\n```\n{msg['full_sms']}\n```"
        )
        kb = [[
            InlineKeyboardButton("📢 CHANNEL",url="https://t.me/blackotpnum"),
            InlineKeyboardButton("💬 GROUP",url="https://t.me/EarningHub6112"),
            InlineKeyboardButton("🤖 BOT",url="https://t.me/ah_method_number_bot"),
        ]]
        await bot.send_message(chat_id=chat_id, text=text,
            parse_mode='MarkdownV2', reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        print(f"❌ Send error to {chat_id}: {e}")

# ===== COMMANDS =====
async def start_cmd(u:Update, c:ContextTypes.DEFAULT_TYPE):
    if str(u.message.from_user.id) in ADMIN_IDS:
        await u.message.reply_text("✅ Bot running!\n/add_chat <id>\n/remove_chat <id>\n/list_chats")
    else: await u.message.reply_text("❌ Not authorized.")

async def add_chat_cmd(u:Update, c:ContextTypes.DEFAULT_TYPE):
    if str(u.message.from_user.id) not in ADMIN_IDS: return
    try:
        cid=c.args[0]; chats=load_chats()
        if cid not in chats: chats.append(cid); save_chats(chats); await u.message.reply_text(f"✅ Added: {cid}")
        else: await u.message.reply_text("Already exists.")
    except: await u.message.reply_text("Usage: /add_chat <id>")

async def rm_chat_cmd(u:Update, c:ContextTypes.DEFAULT_TYPE):
    if str(u.message.from_user.id) not in ADMIN_IDS: return
    try:
        cid=c.args[0]; chats=load_chats()
        if cid in chats: chats.remove(cid); save_chats(chats); await u.message.reply_text(f"✅ Removed: {cid}")
        else: await u.message.reply_text("Not found.")
    except: await u.message.reply_text("Usage: /remove_chat <id>")

async def list_cmd(u:Update, c:ContextTypes.DEFAULT_TYPE):
    if str(u.message.from_user.id) not in ADMIN_IDS: return
    chats=load_chats()
    await u.message.reply_text("📋 Chats:\n"+"\n".join(chats) if chats else "Empty.")

# ===== MAIN JOB =====
async def check_sms(context:ContextTypes.DEFAULT_TYPE):
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

            done=load_ids(); chats=load_chats(); new=0
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

# ===== MAIN =====
def main():
    keep_alive()
    print("🚀 Bot starting — PARALLEL MODE")
    print(f"   4 ranges × 9 numbers = 36 requests")
    print(f"   Sequential ~90s ❌  →  Parallel ~6s ✅")
    print(f"   Interval: {INTERVAL}s")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("add_chat", add_chat_cmd))
    app.add_handler(CommandHandler("remove_chat", rm_chat_cmd))
    app.add_handler(CommandHandler("list_chats", list_cmd))
    app.job_queue.run_repeating(check_sms, interval=INTERVAL, first=2,
        job_kwargs={"max_instances":1})
    print("🤖 Bot is online!")
    app.run_polling()

if __name__ == "__main__":
    main()
