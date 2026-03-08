# -*- coding: utf-8 -*-
# ডিবাগ বট — getsms response টেলিগ্রামে পাঠাবে
import asyncio, httpx
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL    = "https://ivas.tempnum.qzz.io"
LOGIN_URL   = f"{BASE_URL}/login"
SMS_PAGE    = f"{BASE_URL}/portal/sms/received"
GETSMS_URL  = f"{BASE_URL}/portal/sms/received/getsms"
BOT_TOKEN   = "8393297595:AAEksSfupLmn5qeBxjoGT3c9IzaJaLI6mck"
ADMIN_ID    = "7095358778"
USERNAME    = "sagorsakh384@gmail.com"
PASSWORD    = "61453812Sa@"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'X-Requested-With': 'XMLHttpRequest',
}

async def send_tg(text):
    async with httpx.AsyncClient() as c:
        await c.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_ID, "text": text}
        )

async def main():
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        # Login
        page = await client.get(LOGIN_URL, headers=HEADERS)
        soup = BeautifulSoup(page.text, 'html.parser')
        el = soup.find('input', {'name': '_token'})
        token = el['value'] if el else ''
        
        res = await client.post(LOGIN_URL, data={
            'email': USERNAME, 'password': PASSWORD, '_token': token
        }, headers=HEADERS)
        
        if 'login' in str(res.url):
            await send_tg("❌ Login failed!")
            return
        await send_tg("✅ Login OK!")

        # CSRF
        page2 = await client.get(SMS_PAGE, headers=HEADERS)
        soup2 = BeautifulSoup(page2.text, 'html.parser')
        meta = soup2.find('meta', {'name': 'csrf-token'})
        csrf = meta.get('content') if meta else ''
        if not csrf:
            el2 = soup2.find('input', {'name': '_token'})
            csrf = el2['value'] if el2 else ''
        
        await send_tg(f"🔑 CSRF: {csrf[:20]}...")

        # getsms call
        today = datetime.now().strftime('%Y-%m-%d')
        r = await client.post(GETSMS_URL,
            data={'from': today, 'to': today, '_token': csrf},
            headers=HEADERS)
        
        html = r.text
        await send_tg(f"📄 Response length: {len(html)} chars")
        
        # কী কী class আছে check
        soup3 = BeautifulSoup(html, 'html.parser')
        
        rngs  = soup3.find_all(class_='rng')
        subs  = soup3.find_all(class_='sub')
        nrows = soup3.find_all(class_='nrow')
        smsps = soup3.find_all(class_='smsp')
        clits = soup3.find_all(class_='cli-tag')
        msgs  = soup3.find_all(class_='msg-text')
        
        report = (
            f"🔍 Parser Debug:\n"
            f".rng: {len(rngs)}\n"
            f".sub: {len(subs)}\n"
            f".nrow: {len(nrows)}\n"
            f".smsp: {len(smsps)}\n"
            f".cli-tag: {len(clits)}\n"
            f".msg-text: {len(msgs)}\n\n"
        )
        
        if clits:
            report += f"CLI tags: {[c.get_text(strip=True) for c in clits]}\n"
        if msgs:
            report += f"Messages: {[m.get_text(strip=True)[:50] for m in msgs]}\n"
        
        await send_tg(report)
        
        # HTML এর প্রথম ৫০০ char পাঠানো
        preview = html[:500] if html else "EMPTY"
        await send_tg(f"📝 HTML preview:\n{preview}")

asyncio.run(main())
