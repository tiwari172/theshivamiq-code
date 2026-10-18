# Audit Report – Sab Pe Shak + YouTube Scheduler + Comment Bot

Date: 18 Oct 2026 · Branch: `audit-sps-yt-bot`

**Seedhi baat:** teeno folder padhe aur check kiye. Jo galtiyan crash karti thin, data mita sakti thin, ya duplicate upload kar sakti thin, unhe chhote-chhote fix se theek kiya. Commands, file ke naam, Excel/JSON ka format aur output ki jagah **wahi hain**. Kisi asli API (Instagram, Telegram, YouTube, ElevenLabs) ko call nahi kiya; sab nakli (mock) data par test kiya.

Jo cheezein nahi chhui: Excel, `.env`, keys, `comment_checker\data`, `sps.backup*.py`, `hyperframes\_ENGINE\shivam_engine.html`.

---

## 1. `sab_pe_shak\` – Sab Pe Shak reel maker

### `sps.py` – **BADLA**
**Ye kya karta hai:** Excel (Edit Timeline, Scripts, Cover Design) padh kar har Part ki HyperFrames reel banata hai. Voice ko Whisper/ElevenLabs timing se script ke shabdon se jodta hai, images saaf karta hai (green/safed background hatana), cover banata hai, music + SFX mix karta hai, phir pakke engine (`shivam_engine.html`) mein DATA bhar kar render karta hai.

| # | Pehle kya karta tha | Problem kya thi | Ab kaise kaam karega |
|---|---|---|---|
| 1 | Excel ki har row mein column seedha padhta tha | Row chhoti ho, ya Excel/CSV mein koi column (Case, Part, SFX, Title...) na ho to poora script crash | Column na mile ya row chhoti ho to wo khaana "khaali" maana jaata hai, crash nahi |
| 2 | "SFX" column dhoondhta tha | `SHOTS_...csv` ya Excel mein SFX column na ho to crash | SFX column na ho to bina SFX ke chalega |
| 3 | `settings.txt` se number padhta tha | Koi line mit jaaye ya `0,5` jaisa likha ho to samajh na aane wala error | Saaf message: "settings.txt mein 'fps = ...' wali line nahi mili" / "number nahi hai" |
| 4 | Excel na mile to Python ka lamba error | Samajh nahi aata tha | "Excel nahi mili: <path> (series_folder / excel_file check karo)" |
| 5 | `skip_missing = Nahi` par bhi aage badhta tha | Voice / BG / Music na ho to beech mein crash | PNG / SFX na ho to aage badhega (jaisa pehle), par voice / BG / music na ho to wahin ruk kar report mein likhega |
| 6 | `make_all` mein ek Part fail = sab ruk jaata | Ek kharab row se baaki saare Parts ki reel nahi banti thi | Wo Part report mein "beech mein galti" likh kar agle Part par chala jaata hai |
| 7 | Nayi reel banane se pehle purani ko `_purana.mp4` kar deta | Encode fail ho to purani hat chuki, nayi bani nahi | Pehle nayi reel project folder mein banti hai, safal ho tabhi purani `_purana` hoti hai |
| 8 | `SS-001*` naam ke folder dhoondhta tha | `SS-0010 ...` folder ko bhi `SS-001` samajh sakta tha | Sirf `SS-001` ya `SS-001 <Title>` wala folder |
| 9 | Excel "Story Status" mein har baar save karta tha | Bina badlaav ke bhi Excel dobara save + backup (Excel ki picture/chart hat sakte hain) | Sirf tab save jab sach mein "Haan" likhna ho |
| 10 | `make_cover SS-001` (bina Part) | Crash | Part na likho to Part 1 maana jaata hai (jaise `make_reel` mein pehle se tha) |
| 11 | `winreg` aur `ffprobe.exe` hamesha | Linux/cloud par import hi nahi hota tha (test nahi ho sakte the) | Windows par bilkul pehle jaisa; Linux par bhi chal jaata hai |
| 12 | Whisper cache / SFX ka `:0.9` time | Kharab cache file ya `SFX:abc` se crash | Kharab cache = Whisper dobara; galat time = poori SFX |
| 13 | Cover-only mode | Excel mein Cover row na ho to chupchap kuch nahi | Report mein likhta hai "Cover Design sheet mein row nahi mili" |

**Baaki risk (nahi badla):**
- `update_excel = Haan` hai, to reel ke baad Excel save hoti hai (backup `sab_pe_shak\excel_backup\` mein). openpyxl save karte waqt Excel ki **picture / chart / shape hata sakta hai**. CLAUDE.md kehta hai "Excel kabhi edit mat karo" – chaho to `settings.txt` mein `update_excel = Nahi` kar do. `excel_backup\` folder kabhi khud saaf nahi hota, kabhi-kabhi purani files mita dena.
- Render ke liye internet chahiye (`npx hyperframes@0.8.144` pehli baar download hota hai).

### `make_reel.bat`, `make_all.bat`, `make_cover.bat` – **Theek hai**
Ye sirf `py sps.py ...` chalate hain. Koi problem nahi.

### `settings.txt` parsing – **Theek hai**
`naam = value   # note` format sahi padhta hai. Rang (`#FFD400`) ko comment nahi samajhta, kyunki comment ke liye `#` ke dono taraf space chahiye. **Risk:** note likhte waqt `#` se pehle aur baad mein space zaroor rakhna (`fps = 30 # note`), warna note value mein chala jaayega.

---

## 2. `yt_scheduler\` – YouTube Shorts scheduler

### `scheduler.py` – **BADLA**
**Ye kya karta hai:** Excel ki "Post Schedule" sheet se PENDING rows leta hai, video ko YouTube par *private + publishAt (schedule)* ke saath 4MB tukdon mein upload karta hai, net toote to retry karta hai, aur har upload ke turant baad Excel mein SCHEDULED + video id likhta hai. Roz max 6.

| # | Pehle kya karta tha | Problem kya thi | Ab kaise kaam karega |
|---|---|---|---|
| 1 | Roz ki ginti UTC date se (India mein subah 5:30 reset) | YouTube ka quota **Pacific Time** ki aadhi raat par reset hota hai (India mein dopahar ~12:30 / 1:30). Subah chalane par script "6 bacha" bolti thi jabki YouTube ka quota khatam tha | Ginti ab Pacific Time ki date se. `quota_state.json` ka format wahi (`date`, `uploads`). Pehli baar chalane par counter ek baar 0 ho sakta hai, quota khatam hua to YouTube ka "quotaExceeded" pehle jaisa sambhal liya jaata hai |
| 2 | Do baar double-click = do window ek saath upload | **Same video 2 baar upload** ho sakti thi | Chalte waqt `scheduler.lock` banti hai; doosri window bolegi "Scheduler pehle se chal raha hai". Crash ke baad 6 ghante purani lock khud hatti hai |
| 3 | `.env` mein `DAILY_UPLOAD_LIMIT=` (khaali) ya galat number | Python ka lamba error | Khaali = default value; galat = saaf message |
| 4 | — | YouTube ab "AI / synthetic content" batane ka option deta hai | Naya **optional** `.env` setting `YT_CONTAINS_SYNTHETIC_MEDIA=Haan/Nahi`. Na likho to pehle jaisa (kuch nahi bheja jaata) |

**Theek tha (nahi badla):** OAuth token sirf `token.json` mein, kabhi print/log nahi. Sirf `youtube.upload` permission. Retry 2s→4s→8s (max 60s). Excel save fail = `pending_updates.json`, agli baar khud Excel mein. Har likhne se pehle Excel backup (last 20).
**Baaki risk:** `scheduler.log` kabhi chhoti nahi hoti (saal mein kabhi delete kar dena). Fail hua upload bhi quota mein gina jaata hai (safe side).

### `.bat` files (0–5) – **Theek hai**
Sab sahi command chalati hain. `3 UPLOAD.bat` / `5 RETRY FAILED.bat` ab lock lagati hain.

### `SETUP.md` – **BADLA (sirf text)**
Quota reset ka time (dopahar ~12:30/1:30 IST), lock wali baat, aur naya optional setting likha.

### `requirements.txt` – **Theek hai** (`tzdata` pehle se hai – Pacific Time ke liye zaroori).

### YouTube Audit – code mein kya chahiye tha?
**Code audit ke liye taiyaar hai:** sirf ek permission (`youtube.upload`), sirf apne channel par, private + schedule, kisi aur ka data nahi. Code mein koi zaroori badlav nahi tha.

**Kami mili (code nahi, paperwork):** `YOUTUBE AUDIT FORM - STEPS.txt` ka privacy policy wala chhota text YouTube ki policy ki 3 zaroori baatein nahi rakhta tha: (1) "uses YouTube API Services", (2) Google Privacy Policy ka link, (3) access hatane ka link – aur Terms page mein YouTube Terms of Service ka link. Iske bina audit reject ho sakta hai.
→ Naya file **`yt_scheduler\PRIVACY_POLICY_YT.txt`** banaya (Privacy + Terms, copy-paste ready) aur STEPS.txt update kiya.

---

## 3. `comment_checker\` – Instagram comment checker + Telegram bot (server "shivambot")

**Data format bilkul same:** `comments.json`, `ranks.json`, `state.json`, `bot_state.json`, `report.json`, `shak_pending.json`, `verified.txt` – koi key nahi badli, koi naya file format nahi. Saare Telegram commands (`/start`, `/rank`, `/admin`, `/update`, `/shak`, `/week`, `/month`, `/pending`, `/stats`) wahi.

### `checker.py` – **BADLA**
**Ye kya karta hai:** Roz Instagram se reels + comments laata hai, har comment ko answer key se milata hai (naam / number / spelling galti), points + streak + rank ginta hai, `leaderboard.xlsx` aur bot ke liye `ranks.json` / `report.json` banata hai.

| # | Pehle kya karta tha | Problem kya thi | Ab kaise kaam karega |
|---|---|---|---|
| 1 | Ek bhi reel ke comment laane mein error = poora checker band | Ek reel par Instagram limit / net glitch se us din ka **poora leaderboard nahi banta** tha | Wo reel purane (saved) comments se chalti hai, log mein "[!] ... nahi aaye" likha aata hai. Lagatar 2 reel fail = baaki reels purane data se. Ek bhi reel na aaye (token/internet) = pehle jaisa PROBLEM, admin ko message |
| 2 | `comments.json` / `state.json` kharab ho to chupchap khaali maan leta | Agli save par **purana sab data mit jaata** (faisle, yaadein, rank history) | Kharab file ki copy `....kharab-<time>` naam se bacha leta hai, phir aage |
| 3 | Leaderboard ki "Shak" sheet padhte waqt | Chhoti row par crash ho sakta tha | Chhoti row chhod deta hai |

**Baaki risk:** comment ke replies sirf pehle page tak aate hain (bahut replies wale comment mein kuch chhoot sakte hain). Instagram par delete hua comment purane data mein gina rehta hai.

### `tg_bot.py` – **BADLA**
**Ye kya karta hai:** Telegram bot. Follower Instagram naam deta hai → Telegram join + YouTube screenshot → admin Sahi/Galat dabata hai → `verified.txt` mein naam. `/rank` se rank. Roz 9 baje checker chala kar admin ko leaderboard, shak wale comments aur Somvaar/mahine ki report bhejta hai.

| # | Pehle kya karta tha | Problem kya thi | Ab kaise kaam karega |
|---|---|---|---|
| 1 | Verified user koi bhi chhota message bheje ("ok", "thanks") | Uska **Instagram naam "ok" ho jaata** tha – `/rank` galat dikhata | Verified user ka naam message se nahi badalta. Jo abhi verify ho raha hai wo pehle jaisa naam theek kar sakta hai |
| 2 | `/admin <PIN>` ki koi limit nahi | Koi bhi PIN ka andaaza laga-laga kar **admin ban sakta** tha | 5 galat PIN ke baad us user ka `/admin` ignore (bot restart tak) |
| 3 | Checker atak jaaye | **Poora bot hamesha ke liye ruk** jaata | 45 min ke baad roka jaata hai, admin ko message, bot chalta rehta hai |
| 4 | Checker ka error admin ko `<code>` mein | Error mein `<` ya `&` ho to Telegram message hi nahi bhejta – **admin ko pata nahi chalta** | Text safe (escape) karke bhejta hai, + Python error ki aakhri lines bhi |
| 5 | Shak wale 15 comment ek saath | Telegram "too many requests" bole to message nahi gaya, phir bhi "bhej diya" maan leta – wo comment **dobara kabhi nahi aata** | Telegram jitna ruko bole utna ruk kar ek baar dobara; phir bhi na jaaye to agli baar dobara aayega |
| 6 | `/rank <kuch bhi>` | `<` jaise akshar se jawab hi nahi aata | Safe text |
| 7 | Sahi/Galat button ka faisla `state.json` mein | `state.json` kharab ho to purani saari yaadein mit jaati | Kharab file ki copy bachata hai |
| 8 | `.env` mein `TG_BOT_TOKEN="..."` (quotes) / `.env` na ho | Token galat / lamba error | Quotes hata deta hai; `.env` na ho to saaf message |

**Theek tha:** token kabhi log mein nahi (sirf error ka type). **Baaki risk:** checker chalte waqt (2-5 min) bot jawab nahi deta. `admin_pin` `bot_state.json` mein saaf likha hai – server ki file kisi ko mat dena.

### `ig_api.py` – **Theek hai**
Token `.env` se, kabhi print nahi; net error mein bhi token wala URL nahi dikhata (test se pakka kiya). Rate limit (code 4/17/32/613) par 60s ruk kar 3 baar retry, server error par retry. Token har 7 din checker refresh karta hai. **Risk:** bot/server 60 din band raha to token expire – naya token `.env` mein daalna padega.

### `textmatch.py` – **Theek hai**
Hindi→Roman, spelling ki galti (Kallu/Kalu), number (3 / no.3 / teen / third), time (7:00) ko answer na maanna – sab sahi. Koi crash point nahi mila.

### `answer_key.py` – **Theek hai**
Script se answer + suspects nikaal kar `answer_key.xlsx` mein sirf **nayi** case jodta hai, aapki likhi row kabhi overwrite nahi. **Risk:** `answer_key.xlsx` ke header (pehli line) ka naam badla to crash – header mat badalna.

### `server_sync.ps1` – **BADLA**
**Ye kya karta hai:** laptop ↔ server: scripts + answer_key upar bhejta hai, leaderboard / verified / answer_key neeche laata hai.

| # | Pehle | Problem | Ab |
|---|---|---|---|
| 1 | scp/ssh fail ho tab bhi aakhir mein "Ho gaya." | Lagta tha sync ho gaya, jabki nahi hua | Fail hone par laal "!! ... FAIL hua" aur wahin ruk jaata hai |
| 2 | `run_checker.bat` (both) laptop ki `answer_key.xlsx` ko server wali se overwrite karta | Laptop par kiye, bina bheje badlaav **mit jaate** | Overwrite se pehle `answer_key_backup\` mein copy (last 10) |
| 3 | Upload server ki answer_key seedha badal deta | Galti se purani file chali jaaye to wapas nahi | Server par pehle `answer_key.prev.xlsx` copy banti hai |

### `.bat` files
- `ANSWER_KEY_SERVER_PAR_BHEJO.bat`, `run_checker.bat`, `run_bot.bat` – **Theek hai.**
- **Naya `SERVER_SE_LAO.bat`** – `ANSWER_KEY...bat` mein likha tha "pehle SERVER_SE_LAO.bat chalao", par ye file repo mein nahi thi. Ab hai (sirf server se laata hai, kuch bhejta nahi). Laptop par pehle se ho to ye wali rakh lo.

---

## Tests ka result
`tests\` folder mein 39 tests (pytest), sab mock – koi asli API call nahi, network band rakh kar chalaye.

```
39 passed in 0.6s
```
- `test_sps.py` (12): settings parsing, khaali/chhoti Excel row, missing column, galat folder match, voice missing, make_all ek fail par na ruke, Excel bina badlaav save na ho.
- `test_scheduler.py` (12): Pacific quota date, lock (do run), `.env` khaali/galat, upload retry (503/network), quota khatam, poora run nakli YouTube ke saath (SCHEDULED/FAILED, `ig_caption` na chhuye), Excel save fail → pending → baad mein apply.
- `test_comment_checker.py` (15): ek reel fail par leaderboard bane, `ranks.json`/`state.json` ka format same, kharab JSON ka backup, token error mein na dikhe, IG rate-limit retry, bot: verified naam na badle, admin PIN limit, HTML escape, Telegram 429 retry, shak "bheja" sirf jab gaya, checker timeout.

Purane code par yahi tests chalaye to zyaadatar fail hue (sps wale to Linux par load hi nahi hue) → matlab tests sach mein ye galtiyan pakadte hain.

Khud chalane ke liye (code folder mein): `py -m pip install pytest` phir `py -m pytest tests`

---

## Server par update kaise karein (bot "shivambot")
Sirf **2 file** server par badalni hain: `checker.py` aur `tg_bot.py`. (`ig_api.py`, `textmatch.py`, `answer_key.py` same hain.)

1. Laptop par naya code lo (branch `audit-sps-yt-bot` merge karke ya GitHub se download).
2. PowerShell kholo, `theshivamiq code\comment_checker` folder mein jao.
3. Server par purani files ka backup:
   `ssh -i "$env:USERPROFILE\.ssh\shivam_gcp" shivam@35.222.83.100 "cd ~/bot && cp checker.py checker.py.old && cp tg_bot.py tg_bot.py.old"`
4. Nayi files bhejo:
   `scp -i "$env:USERPROFILE\.ssh\shivam_gcp" checker.py tg_bot.py shivam@35.222.83.100:bot/`
5. Bot restart:
   `ssh -i "$env:USERPROFILE\.ssh\shivam_gcp" shivam@35.222.83.100 "sudo systemctl restart shivambot && sleep 5 && sudo journalctl -u shivambot -n 15 --no-pager"`
   → aakhir mein **"Bot chalu: @..."** dikhna chahiye.
6. Telegram par bot ko `/stats` bhejo – jawab aaye to sab theek. (Admin pehle jaisa rahega, dobara `/admin` nahi karna.)
7. **Kuch gadbad ho to wapas purana:**
   `ssh -i "$env:USERPROFILE\.ssh\shivam_gcp" shivam@35.222.83.100 "cd ~/bot && cp checker.py.old checker.py && cp tg_bot.py.old tg_bot.py && sudo systemctl restart shivambot"`

Laptop par: `server_sync.ps1` aur `SERVER_SE_LAO.bat` bas `comment_checker\` folder mein replace/copy kar do. YT scheduler aur Sab Pe Shak ke liye bhi bas nayi files purani ki jagah copy karni hain – `.env`, Excel, `token.json` ko mat chhuna.

(Agar server par bot ka folder `~/bot` ke alawa kahin hai, to upar `~/bot` ki jagah wo naam likhna – `server_sync.ps1` `~/bot` hi use karta hai.)

---

## YouTube audit ke liye aapko kya karna baaki hai
1. **Privacy + Terms page:** sites.google.com par naya site → 2 page. Text `yt_scheduler\PRIVACY_POLICY_YT.txt` se copy karo, `<aapka email>` bharo → Publish → dono link copy.
2. **OAuth consent screen → Branding:** Privacy policy link + Terms link daalo, App home page = `https://www.youtube.com/@theshivamiq`.
3. **Project number** (12 digit) Google Cloud Dashboard se copy.
4. **Screenshots / 1-2 min recording:** `1 DRY RUN.bat` ka output, Excel "Post Schedule" (bina personal data), Studio mein video (Private + Scheduled), Google "Allow" screen.
5. **Form bharo:** https://support.google.com/youtube/contact/yt_api_form – jawab `YOUTUBE AUDIT FORM - STEPS.txt` STEP 2 mein copy-paste ready.
6. **AI content ka faisla:** voice ElevenLabs ki hai aur images AI ki. YouTube kehta hai *asli jaisi dikhne/sunne wali* AI cheez batani chahiye (saaf cartoon ho to zaroori nahi). Faisla karke `.env` mein `YT_CONTAINS_SYNTHETIC_MEDIA=Haan` ya `Nahi` likh sakte ho (na likho to pehle jaisa).
7. **Audit pass hone tak:** script se sirf `1 DRY RUN` / `4 STATUS`, video haath se upload. Approve email aaye to `2 TEST 1 VIDEO.bat` se ek video test karo.
