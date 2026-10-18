"""Detective Shivam Rank Bot (Telegram)
Follower: /start -> Instagram username -> code reel par comment -> Telegram join -> YouTube screenshot
-> sab sahi to verified.txt mein naam + rank milta hai.  /rank se apna rank.
Chalao: run_bot.bat  (window khuli rakho)
"""
import os, re, sys, json, time, random, subprocess, html, shutil, tempfile
from datetime import datetime, timedelta, timezone
import requests
import ig_api
import yt_ocr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
STATE = os.path.join(DATA, "bot_state.json")
RANKS = os.path.join(DATA, "ranks.json")
VERIFIED = os.path.join(HERE, "verified.txt")
CHANNEL = "@theshivamiq"
TG_LINK = "https://t.me/theshivamiq"
YT_LINK = "https://www.youtube.com/@theshivamiq?sub_confirmation=1"
IG_LINK = "https://www.instagram.com/theshivamiq/"
CHECKER_HOUR = 9          # roz subah 9 baje (IST) leaderboard update
SHAK_PER_DAY = 15
CHECKER_TIMEOUT = 45 * 60   # checker isse zyada chale to roko (bot atka na rahe)
IG_CHECK = False          # Instagram code comment wala check (False = admin khud naam dekhta hai)
AUTO_YT = True            # YouTube screenshot bot khud padhe ("Subscribed" + "Shivam") – pass ho to admin ki zaroorat nahi
AUTO_YT_TRIES = 2         # itni baar fail ho to screenshot admin ke paas (shayad OCR theek se nahi padh paaya)
IST = timezone(timedelta(hours=5, minutes=30))


def log(*a):
    print(datetime.now().strftime("%H:%M:%S"), *a, flush=True)


# ------------------------------------------------------------ token / telegram
def bot_token():
    try:
        with open(ig_api.ENV, encoding="utf-8-sig") as f:
            for line in f:
                if line.strip().startswith("TG_BOT_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        sys.exit(".env file nahi mili: " + ig_api.ENV)
    sys.exit(".env mein TG_BOT_TOKEN nahi mila")


TOKEN = bot_token()


def tg(method, _timeout=30, _files=None, **params):
    for k, v in list(params.items()):
        if isinstance(v, (dict, list)):
            params[k] = json.dumps(v)
    for attempt in range(2):
        try:
            r = requests.post("https://api.telegram.org/bot%s/%s" % (TOKEN, method), data=params, files=_files, timeout=_timeout)
            d = r.json()
        except Exception as e:      # message mein URL (token) ho sakta hai, isliye sirf type
            log("Telegram connection problem:", type(e).__name__)
            return None
        # 429 = bahut tez message: Telegram jitna kahe utna ruk kar ek baar dobara (file upload dobara nahi)
        retry = (d.get("parameters") or {}).get("retry_after") if d.get("error_code") == 429 else None
        if retry and attempt == 0 and not _files:
            time.sleep(min(int(retry), 60) + 1)
            continue
        break
    if not d.get("ok"):
        log("Telegram error (%s): %s" % (method, d.get("description")))
        return None
    return d.get("result")


def send(chat, text, buttons=None):
    p = {"chat_id": chat, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if buttons:
        p["reply_markup"] = {"inline_keyboard": buttons}
    return tg("sendMessage", **p)


# ------------------------------------------------------------ state
def load(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_state(st):
    os.makedirs(DATA, exist_ok=True)
    tmp = STATE + ".new"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def verified_set():
    out = set()
    try:
        for line in open(VERIFIED, encoding="utf-8-sig"):
            line = line.split("#")[0].strip().lstrip("@").lower()
            if line:
                out.add(line)
    except OSError:
        pass
    return out


def add_verified(ig):
    if ig.lower() in verified_set():
        return
    with open(VERIFIED, "a", encoding="utf-8") as f:
        f.write("\n" + ig.lower() + "   # bot " + datetime.now(IST).strftime("%Y-%m-%d"))


# ------------------------------------------------------------ checks
_scan_cache = {"t": 0, "since": None, "found": {}}


CODE_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"   # O/0, I/1/L jaise confuse karne wale nahi


def make_code():
    """6 akshar, bina dash/space: jaise K7M2QX (kam se kam 2 number + 2 letter)"""
    while True:
        c = "".join(random.choice(CODE_CHARS) for _ in range(6))
        if sum(ch.isdigit() for ch in c) >= 2 and sum(ch.isalpha() for ch in c) >= 2:
            return c


def codes_in(text):
    t = (text or "").upper()
    out = set(re.findall(r"(?<![A-Z0-9])[A-Z0-9]{6}(?![A-Z0-9])", t))
    out |= set(re.findall(r"SHIVAM\s*[-_ ]?\s*(\d{4})", t))      # purana format
    return out


def scan_codes(since):
    """Haal ki reels ke comments (aur replies) mein code dhoondo -> {code: set(usernames)}"""
    c = _scan_cache
    if time.time() - c["t"] < 60 and c["since"] and c["since"] <= since:
        return c["found"]
    found = {}
    fields = "id,text,timestamp,from{username},replies{id,text,timestamp,from{username}}"
    try:
        # saari reels (har reel ke sirf naye comments – purane aate hi ruk jaata hai)
        media = ig_api.get_all("me/media", {"fields": "id,timestamp", "limit": 50})
        tok = ig_api.load_token()
        for m in media:
            data = ig_api.get(m["id"] + "/comments", {"fields": fields, "limit": 50}, tok)
            pages = 0
            while True:
                old = False
                for cm in data.get("data", []):
                    for x in [cm] + (cm.get("replies") or {}).get("data", []):
                        t = datetime.strptime(x["timestamp"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                        if t < since:
                            if x is cm:
                                old = True
                            continue
                        u = ((x.get("from") or {}).get("username") or "").lower()
                        for code in codes_in(x.get("text")):
                            found.setdefault(code, set()).add(u)
                nxt = data.get("paging", {}).get("next")
                pages += 1
                if old or not nxt or pages >= 6:
                    break
                after = re.search(r"after=([^&]+)", nxt)
                if not after:
                    break
                data = ig_api.get(m["id"] + "/comments", {"fields": fields, "limit": 50,
                                                          "after": requests.utils.unquote(after.group(1))}, tok)
    except ig_api.IGError as e:
        log("Instagram check nahi hua:", e)
    c.update(t=time.time(), since=since, found=found)
    return found


def in_channel(user_id):
    r = tg("getChatMember", chat_id=CHANNEL, user_id=user_id)
    if not r:
        return False
    return r.get("status") in ("creator", "administrator", "member") or \
        (r.get("status") == "restricted" and r.get("is_member"))


# ------------------------------------------------------------ rank text
def rank_text(ig):
    ig = html.escape(ig or "")   # "/rank <kuch bhi>" se HTML toot kar jawab gayab na ho
    rk = load(RANKS, {})
    d = rk.get("users", {}).get(ig.lower())
    if not d:
        return ("🔍 <b>@%s</b> ka abhi koi sahi jawab nahi mila.\n"
                "Har case par comment karo: naam ya number (jaise <b>Kallu</b> ya <b>3</b>).\n"
                "<i>Data update: %s</i>") % (ig, rk.get("updated", "-"))
    ok = ig.lower() in verified_set()
    if ok:
        rank = html.escape(d["rank"]) or "Abhi koi rank nahi (3 sahi par Junior Detective)"
    else:
        rank = ("🔒 " + d["would"] + " (verify poora karo to milega)") if d["would"] else \
            "Abhi koi rank nahi (3 sahi par Junior Detective)"
    return ("🕵️ <b>@%s</b>\n\n"
            "🏅 Rank: <b>%s</b>\n"
            "⭐ Kul points: <b>%d</b>  (leaderboard #%d)\n"
            "📅 Is hafte points: <b>%d</b>  |  Pichhle hafte: <b>%d</b>\n"
            "✅ Kul sahi: <b>%d</b>\n"
            "🔥 Din streak: <b>%d</b> din (sabse lambi %d)  |  Reel streak: %d\n\n"
            "⚡ Jaldi jawab = zyada points: reel ke baad 30 sec mein sahi = +10, 1 min = +8 ... 1 ghante tak bonus.\n"
            "🥇 Reel par pehle 3 sahi = +10 / +7 / +5\n"
            "<i>Data update: %s</i>") % (
        html.escape(d["name"]), rank, d.get("pts", 0), d["pos"], d.get("pts_live", 0), d.get("pts_week", 0), d["sahi"],
        d.get("day_streak", 0), d.get("best_day_streak", 0), d["streak"], rk.get("updated", "-"))


# ------------------------------------------------------------ flow
def status_msg(st, uid):
    u = st["users"][uid]
    tick = lambda b: "✅" if b else "⬜"
    btn = [[{"text": "✈️ Telegram join", "url": TG_LINK}, {"text": "▶️ YouTube subscribe", "url": YT_LINK}],
           [{"text": "🔄 Check karo", "callback_data": "check"}]]
    if not IG_CHECK:
        text = ("🕵️ <b>Detective Verification</b> – @%s\n\n"
                "%s <b>1. Telegram:</b> channel join karo\n"
                "%s <b>2. YouTube:</b> subscribe karo aur uska <b>screenshot</b> yahan bhejo%s\n"
                "👤 <b>3. Instagram:</b> manual verification – admin khud tumhara account check karega "
                "(tumhe kuch nahi karna)\n\n"
                "Telegram + YouTube karke <b>Check karo</b> dabao.") % (
            u["ig"], tick(u.get("tg_ok")), tick(u.get("yt_ok")),
            " (check ho raha hai ⏳)" if u.get("yt_wait") and not u.get("yt_ok") else "")
        return text, btn
    text = ("🕵️ <b>Detective Verification</b> – @%s\n\n"
            "%s <b>1. Instagram:</b> ye code meri kisi bhi reel par comment karo:\n"
            "      <code>%s</code>  (sirf ye 6 akshar – tap karke copy karo)\n"
            "%s <b>2. Telegram:</b> channel join karo\n"
            "%s <b>3. YouTube:</b> subscribe karo aur uska <b>screenshot</b> yahan bhejo%s\n\n"
            "Teeno karke <b>Check karo</b> dabao.") % (
        u["ig"], tick(u.get("ig_ok")), u["code"], tick(u.get("tg_ok")), tick(u.get("yt_ok")),
        " (check ho raha hai ⏳)" if u.get("yt_wait") and not u.get("yt_ok") else "")
    btn = [[{"text": "📸 Instagram", "url": IG_LINK}, {"text": "✈️ Telegram join", "url": TG_LINK}],
           [{"text": "▶️ YouTube subscribe", "url": YT_LINK}],
           [{"text": "🔄 Check karo", "callback_data": "check"}]]
    return text, btn


def finish_if_done(st, uid, chat):
    u = st["users"][uid]
    if (u.get("ig_ok") or not IG_CHECK) and u.get("tg_ok") and u.get("yt_ok") and not u.get("done"):
        u["done"] = True
        add_verified(u["ig"])
        save_state(st)
        send(chat, "🎉 <b>Verified!</b> Ab tum officially Shivam ki team mein ho.\n\n" + rank_text(u["ig"]))
        log("VERIFIED:", u["ig"])


def do_check(st, uid, chat):
    u = st["users"][uid]
    if IG_CHECK and not u.get("ig_ok"):
        since = datetime.fromisoformat(u["code_at"]) - timedelta(minutes=5)
        users = scan_codes(since).get(u["code"], set())
        if u["ig"].lower() in users:
            u["ig_ok"] = True
    u["tg_ok"] = bool(in_channel(int(uid)))
    save_state(st)
    text, btn = status_msg(st, uid)
    miss = []
    if IG_CHECK and not u.get("ig_ok"):
        miss.append("Instagram code comment nahi mila. Dhyaan do: (1) usi account se comment karo jo username diya, (2) reply nahi, seedha comment karo, (3) account private hai to comment nahi dikhta – kuch der public karke comment karo. Comment ke 1-2 minute baad dobara Check karo.")
    if not u.get("tg_ok"):
        miss.append("Telegram channel join nahi dikha")
    if not u.get("yt_ok"):
        miss.append("YouTube screenshot bhejo" if not u.get("yt_wait") else "YouTube screenshot check ho raha hai")
    if miss:
        text += "\n\n❗ " + "\n❗ ".join(miss)
    send(chat, text, btn)
    finish_if_done(st, uid, chat)


_admin_fail = {}   # galat /admin PIN ki ginti (sirf memory mein, file format same)


def handle_message(st, msg):
    chat = msg["chat"]["id"]
    if msg["chat"].get("type") != "private":
        return
    uid = str(msg["from"]["id"])
    text = (msg.get("text") or "").strip()
    u = st["users"].get(uid)

    # ---- admin
    if text.startswith("/admin"):
        if _admin_fail.get(uid, 0) >= 5:      # PIN ka andaaza lagane wale ko roko
            return
        if text.split()[-1] == st["admin_pin"]:
            st["admin"] = chat
            save_state(st)
            send(chat, "✅ Aap admin ho. YouTube screenshots aur roz ka leaderboard yahin aayega.\n"
                       "/update – abhi leaderboard banao\n/shak – shak wale comments\n"
                       "/week – Somvaar wali report\n/month – mahine ki report\n"
                       "/pending – baaki YouTube screenshots\n/stats – ginti")
        else:
            _admin_fail[uid] = _admin_fail.get(uid, 0) + 1
            if _admin_fail[uid] >= 5:
                log("Galat /admin PIN 5 baar (user id %s) – ab ignore" % uid)
        return
    if chat == st.get("admin"):
        if text == "/stats":
            us = st["users"].values()
            send(chat, "Kul: %d | Verified: %d | YT pending: %d" % (
                len(st["users"]), sum(1 for x in us if x.get("done")), sum(1 for x in us if x.get("yt_wait") and not x.get("yt_ok"))))
            return
        if text == "/shak":
            send_shak(st, SHAK_PER_DAY)
            return
        if text in ("/week", "/month"):
            st.pop("week_report" if text == "/week" else "month_report", None)
            send_reports(st, datetime.now(IST), force_week=text == "/week", force_month=text == "/month")
            return
        if text == "/update":
            send(chat, "⏳ Leaderboard update ho raha hai (2-5 minute)...")
            maybe_run_checker(st, force=True)
            return
        if text == "/pending":
            n = 0
            for xid, x in st["users"].items():
                if x.get("yt_wait") and not x.get("yt_ok") and x.get("yt_photo"):
                    forward_yt(st, xid)
                    n += 1
            if not n:
                send(chat, "Koi screenshot baaki nahi.")
            return

    # ---- rank
    if text.startswith("/rank"):
        parts = text.split()
        ig = parts[1].lstrip("@") if len(parts) > 1 else (u or {}).get("ig")
        if not ig:
            send(chat, "Apna Instagram username likho, jaise:\n<code>/rank riya_123</code>")
        else:
            send(chat, rank_text(ig))
        return

    if text.startswith("/start") or text == "/help" or not u:
        if u and u.get("done"):
            send(chat, "Tum already verified ho ✅\n\n" + rank_text(u["ig"]))
            return
        st["users"][uid] = {"step": "ig", "name": msg["from"].get("first_name", "")}
        save_state(st)
        send(chat, "🕵️ <b>Detective Shivam ki team mein swagat hai!</b>\n\n"
                   "Rank (Junior / Senior / Detective of the Week / Shivam ka Partner) paane ke liye ye kaam:\n"
                   + ("1️⃣ Instagram par ek code comment\n2️⃣ Telegram channel join\n3️⃣ YouTube subscribe\n\n" if IG_CHECK
                      else "1️⃣ Telegram channel join\n2️⃣ YouTube subscribe (screenshot)\n"
                           "3️⃣ Instagram – manual verification (admin check karega)\n\n") +
                   "Shuru karo: apna <b>Instagram username</b> bhejo (bina @ ke).\n\n"
                   "Sirf rank dekhna hai? <code>/rank username</code>")
        return

    # ---- screenshot
    if msg.get("photo"):
        if not u or not u.get("ig"):
            send(chat, "Pehle apna Instagram username bhejo.")
            return
        if u.get("yt_ok"):
            send(chat, "YouTube pehle hi confirm ho chuka hai ✅", status_msg(st, uid)[1])
            return
        u["yt_photo"] = msg["photo"][-1]["file_id"]
        u["yt_wait"] = True
        save_state(st)
        if AUTO_YT and auto_yt(st, uid, chat):
            return
        send(chat, "📸 Screenshot mil gaya. Check hone ke baad bata denge ✅")
        forward_yt(st, uid)
        return

    # ---- instagram username (verified ho chuka ho to "ok" / "thanks" jaise message se naam na badle)
    if u.get("step") == "ig" or (not u.get("done") and not u.get("ig_ok")
                                 and re.fullmatch(r"@?[A-Za-z0-9._]{2,30}", text)):
        ig = text.lstrip("@").lower()
        if not re.fullmatch(r"[a-z0-9._]{2,30}", ig):
            send(chat, "Ye sahi Instagram username nahi lag raha. Sirf username bhejo, jaise <code>riya_123</code>")
            return
        for xid, x in st["users"].items():
            if xid != uid and x.get("ig") == ig and (x.get("ig_ok") or x.get("done")):
                send(chat, "@%s pehle se kisi aur ne verify kar liya hai. Galti lage to admin ko batao." % ig)
                return
        u.update(ig=ig, step="tasks", code=make_code(),
                 code_at=datetime.now(timezone.utc).isoformat(), ig_ok=False)
        save_state(st)
        text, btn = status_msg(st, uid)
        send(chat, text, btn)
        return

    send(chat, "Status dekhne ke liye <b>Check karo</b> dabao, ya /rank likho.", status_msg(st, uid)[1])


def download_photo(file_id):
    """Telegram se photo temp file mein. Fail = None."""
    info = tg("getFile", file_id=file_id)
    if not info or not info.get("file_path"):
        return None
    try:
        r = requests.get("https://api.telegram.org/file/bot%s/%s" % (TOKEN, info["file_path"]), timeout=30)
        r.raise_for_status()
    except Exception as e:      # URL mein token hai, isliye sirf type
        log("Photo download problem:", type(e).__name__)
        return None
    fd, path = tempfile.mkstemp(suffix=os.path.splitext(info["file_path"])[1] or ".jpg")
    with os.fdopen(fd, "wb") as f:
        f.write(r.content)
    return path


def auto_yt(st, uid, chat):
    """Screenshot khud padho. True = maamla khatam (pass ya follower ko dobara bhejne ko bola).
    False = admin ke paas bhejo (OCR nahi hai / download fail / baar baar fail / copy screenshot)."""
    u = st["users"][uid]
    path = download_photo(u["yt_photo"])
    if not path:
        return False
    try:
        h = yt_ocr.file_hash(path)
        used = st.setdefault("yt_hash", {})
        if used.get(h) and used[h] != uid:       # same screenshot kisi aur ne bheja tha = copy
            log("YouTube screenshot copy lagta hai (@%s) – admin ko" % u.get("ig"))
            return False
        res = yt_ocr.check(path)
    finally:
        os.remove(path)
    if res is None:
        log("tesseract nahi hai – screenshot admin ko (server par: sudo apt-get install tesseract-ocr tesseract-ocr-hin)")
        return False
    ok, why = res
    if ok:
        used[h] = uid
        u["yt_ok"] = True
        u["yt_auto"] = True
        save_state(st)
        log("YouTube AUTO pass: @%s (%s)" % (u.get("ig"), why))
        send(chat, "▶️ YouTube subscribe confirm ho gaya ✅ (bot ne screenshot check kiya)")
        if st.get("admin"):
            send(st["admin"], "🤖 Auto pass: @%s – YouTube screenshot mein %s" % (html.escape(u.get("ig") or ""), why))
        do_check(st, uid, chat)
        return True
    u["yt_tries"] = u.get("yt_tries", 0) + 1
    save_state(st)
    log("YouTube auto fail %d: @%s (%s)" % (u["yt_tries"], u.get("ig"), why))
    if u["yt_tries"] >= AUTO_YT_TRIES:
        send(chat, "📸 Screenshot admin ke paas bhej diya, check karke bata denge ✅")
        forward_yt(st, uid, note="Bot ko %s (%d baar)" % (why, u["yt_tries"]))
        return True
    u["yt_wait"] = False
    save_state(st)
    send(chat, "❌ Screenshot mein %s.\n\nYouTube par <b>theshivamiq</b> channel kholo, Subscribe dabao, "
               "phir aisa screenshot bhejo jisme channel ka naam aur <b>Subscribed</b> button saaf dikhe." % why,
         [[{"text": "▶️ YouTube subscribe", "url": YT_LINK}]])
    return True


def forward_yt(st, uid, note=""):
    adm = st.get("admin")
    u = st["users"][uid]
    if not adm:
        log("YouTube screenshot aaya (@%s) – admin set nahi hai, /admin PIN bhejo" % u.get("ig"))
        return
    tg("sendPhoto", chat_id=adm, photo=u["yt_photo"],
       caption="Naya detective: @%s\nInstagram: https://www.instagram.com/%s/\n"
               "Screenshot mein YouTube subscribed dikh raha hai, aur Instagram naam sahi lag raha hai?%s" % (
                   u.get("ig"), u.get("ig"), ("\n(" + note + ")") if note else ""),
       reply_markup={"inline_keyboard": [[{"text": "✅ Sahi", "callback_data": "yt_ok:" + uid},
                                          {"text": "❌ Galat", "callback_data": "yt_no:" + uid}]]})


def handle_callback(st, cb):
    data = cb.get("data", "")
    chat = cb["message"]["chat"]["id"]
    uid = str(cb["from"]["id"])
    tg("answerCallbackQuery", callback_query_id=cb["id"])
    if data == "check" and uid in st["users"] and st["users"][uid].get("ig"):
        do_check(st, uid, chat)
    elif data.startswith("sk:") and chat == st.get("admin"):
        _, cid, v = data.split(":")
        save_decision(cid, "SAHI" if v == "S" else "GALAT")
        tg("editMessageReplyMarkup", chat_id=chat, message_id=cb["message"]["message_id"],
           reply_markup={"inline_keyboard": [[{"text": "✔ " + ("Sahi" if v == "S" else "Galat") +
                                               " (agle update mein judega)", "callback_data": "x"}]]})
    elif data.startswith(("yt_ok:", "yt_no:")) and chat == st.get("admin"):
        xid = data.split(":", 1)[1]
        x = st["users"].get(xid)
        if not x:
            return
        if data.startswith("yt_ok"):
            x["yt_ok"] = True
            save_state(st)
            send(chat, "✅ @%s YouTube pass" % x.get("ig"))
            send(int(xid), "▶️ YouTube subscribe confirm ho gaya ✅")
            do_check(st, xid, int(xid))
        else:
            x["yt_wait"] = False
            x.pop("yt_photo", None)
            save_state(st)
            send(chat, "❌ @%s YouTube reject" % x.get("ig"))
            send(int(xid), "❌ Screenshot mein subscribe nahi dikha. Subscribe karke naya screenshot bhejo.",
                 [[{"text": "▶️ YouTube subscribe", "url": YT_LINK}]])


# ------------------------------------------------------------ checker roz
def maybe_run_checker(st, force=False):
    now = datetime.now(IST)
    today = now.strftime("%Y-%m-%d")
    if not force and (st.get("checker_day") == today or now.hour < CHECKER_HOUR):
        return
    log("Comment checker chala raha hoon (leaderboard update)...")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "checker.py")], cwd=HERE, env=env,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=CHECKER_TIMEOUT)
    except subprocess.TimeoutExpired:
        # atka hua checker bot ko hamesha ke liye na roke; aaj dobara nahi chalega
        log("Checker %d min mein khatam nahi hua – roka" % (CHECKER_TIMEOUT // 60))
        st["checker_day"] = today
        save_state(st)
        if st.get("admin"):
            send(st["admin"], "⚠️ Comment checker %d min mein khatam nahi hua, roka gaya. /update se dobara chalao."
                 % (CHECKER_TIMEOUT // 60))
        return
    out = (r.stdout or "").strip().splitlines()
    if r.returncode != 0 and r.stderr:
        out += r.stderr.strip().splitlines()[-3:]
    log("Checker khatam (code %s)\n%s" % (r.returncode, "\n".join(out[-4:])))
    st["checker_day"] = today
    save_state(st)
    adm = st.get("admin")
    if not adm:
        return
    if r.returncode != 0:
        send(adm, "⚠️ Comment checker mein problem:\n<code>%s</code>" % html.escape("\n".join(out[-6:])[-800:]))
        return
    res = [l.strip() for l in out if " : jawab" in l or "Partner:" in l or "Week:" in l or "shoutout" in l]
    send(adm, "📊 <b>Aaj ka leaderboard</b>\n<code>%s</code>" % html.escape("\n".join(res[:6] + res[-3:])))
    xl = os.path.join(HERE, "leaderboard.xlsx")
    try:
        with open(xl, "rb") as f:
            tg("sendDocument", _timeout=120, _files={"document": ("leaderboard_%s.xlsx" % today, f)}, chat_id=adm)
    except OSError:
        pass
    send_shak(st, SHAK_PER_DAY)
    if not force:
        send_reports(st, now)


# ------------------------------------------------------------ Somvaar / mahine ki report (reel banane ke liye)
def _rows(rows, unit):
    out = []
    for i, (nm, v, sahi, ok, dst) in enumerate(rows, 1):
        out.append("%d. @%s – <b>%d</b> points (%d sahi, 🔥%d din)%s" % (i, nm, v, sahi, dst, "" if ok else "  ⚠️ verify nahi"))
    return "\n".join(out) or "–"


def send_reports(st, now, force_week=False, force_month=False):
    adm = st.get("admin")
    rp = load(os.path.join(DATA, "report.json"), {})
    if not adm or not rp:
        return
    today = now.strftime("%Y-%m-%d")
    if (now.weekday() == 0 or force_week) and st.get("week_report") != today:
        dow = rp.get("dow_verified") or "(koi verified nahi)"
        txt = ("📅 <b>SOMVAAR REPORT</b> – hafta %s\n\n"
               "🔍 <b>Detective of the Week:</b> @%s\n"
               "%s"
               "\n<b>Hafte ke Top 10:</b>\n%s\n\n"
               "Is hafte %d jawab aaye • Seniors: %d • Juniors: %d • Verified: %d\n\n"
               "👉 Ye message Claude ko forward karo – aaj shaam ki reel ban jaayegi.") % (
            rp["week_label"], dow,
            ("(Sabse zyada sahi: @%s – abhi verified nahi)\n" % rp["dow_any"]) if rp.get("dow_any") and rp.get("dow_any") != rp.get("dow_verified") else "",
            _rows(rp.get("week_top", []), "sahi"), rp.get("week_jawab", 0), rp.get("seniors", 0), rp.get("juniors", 0), rp.get("verified", 0))
        send(adm, txt)
        st["week_report"] = today
    if (now.day == 1 or force_month) and st.get("month_report") != today:
        txt = ("🗓️ <b>MAHINE KI REPORT</b> – %s\n\n"
               "👑 <b>Shivam ka Partner:</b> @%s%s\n\n"
               "<b>Mahine ke Top 10:</b>\n%s\n\n"
               "<b>Ab tak ke Top 10 (kul):</b>\n%s\n\n"
               "👉 Ye message Claude ko forward karo – mahine ki badi reel ban jaayegi.") % (
            rp["month_label"], rp.get("partner_verified") or "(koi verified nahi)",
            ("\n(Sabse zyada kul sahi: @%s – abhi verified nahi)" % rp["partner_any"]) if rp.get("partner_any") and rp.get("partner_any") != rp.get("partner_verified") else "",
            _rows(rp.get("month_top", []), "sahi"), _rows(rp.get("all_top", []), "sahi"))
        send(adm, txt)
        st["month_report"] = today
    save_state(st)


# ------------------------------------------------------------ shak wale comments (admin faisla)
def send_shak(st, limit):
    adm = st.get("admin")
    pend = load(os.path.join(DATA, "shak_pending.json"), [])
    sent = set(st.setdefault("shak_sent", []))
    todo = [x for x in pend if x["cid"] not in sent][:limit]
    if not adm:
        return
    if not todo:
        send(adm, "🤔 Koi naya shak wala comment nahi.")
        return
    left = len([x for x in pend if x["cid"] not in sent]) - len(todo)
    send(adm, "🤔 <b>%d shak wale comments</b> – har ek par Sahi/Galat dabao.%s" % (
        len(todo), ("\n(%d aur baaki: /shak)" % left) if left > 0 else ""))
    for x in todo:
        ok = send(adm, "📁 Case <b>%s</b>  (sahi: %s / no. %s)\n👤 @%s\n💬 %s" % (
            x["case"], html.escape(str(x["answer"])), x["number"], x["u"], x["text"].replace("&", "&amp;").replace("<", "&lt;")),
            [[{"text": "✅ Sahi", "callback_data": "sk:%s:S" % x["cid"]},
              {"text": "❌ Galat", "callback_data": "sk:%s:G" % x["cid"]}]])
        if ok:     # message nahi gaya to "bhej diya" mat maano – agli baar dobara aayega
            st["shak_sent"].append(x["cid"])
    st["shak_sent"] = st["shak_sent"][-5000:]
    save_state(st)


def save_decision(cid, verdict):
    p = os.path.join(DATA, "state.json")
    cst = load(p, None)
    if cst is None:
        if os.path.exists(p):
            # state.json kharab hai: {} likh kar purani yaadein (memory, rank_history) mat mitao
            bad = p + ".kharab-" + datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(p, bad)
            log("[!] state.json kharab thi, copy:", os.path.basename(bad))
        cst = {}
    cst.setdefault("decisions", {})[cid] = verdict
    tmp = p + ".new"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cst, f, ensure_ascii=False)
    os.replace(tmp, p)


def main():
    st = load(STATE, {})
    st.setdefault("users", {})
    st.setdefault("offset", 0)
    if "admin_pin" not in st:
        st["admin_pin"] = "%06d" % random.randint(0, 999999)
    save_state(st)
    me = tg("getMe")
    if not me:
        sys.exit("Bot token kaam nahi kar raha.")
    tg("setMyCommands", commands=[{"command": "start", "description": "Verify karo aur rank pao"},
                                  {"command": "rank", "description": "Apna rank dekho"}])
    log("Bot chalu: @%s  (ye window khuli rakho)" % me["username"])
    if not st.get("admin"):
        log(">>> Admin banne ke liye apne Telegram se bot ko bhejo:  /admin %s" % st["admin_pin"])
    while True:
        try:
            maybe_run_checker(st)
        except Exception as e:
            log("Checker problem:", type(e).__name__, e)
        res = tg("getUpdates", _timeout=70, offset=st["offset"], timeout=50)
        ups = res or []
        for up in ups:
            st["offset"] = up["update_id"] + 1
            try:
                if "message" in up:
                    handle_message(st, up["message"])
                elif "callback_query" in up:
                    handle_callback(st, up["callback_query"])
            except Exception as e:
                log("Message handle nahi hua:", type(e).__name__, e)
            save_state(st)
        if res is None:
            time.sleep(5)


if __name__ == "__main__":
    main()
