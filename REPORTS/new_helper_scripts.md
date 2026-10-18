# Naye helper scripts – roz ke kaam ke liye

Ye sab **naye** files hain. Purane scripts (make_reel, build_voice, prep_story, make_cover...) mein kuch nahi badla.
Koi bhi script ElevenLabs ya internet ki API call nahi karta (sirf CODE SYNC GitHub se baat karta hai).

| Double-click karo | Kya karta hai | Kab chalao |
|---|---|---|
| `SETUP CHECK.bat` | Laptop ka setup check (ffmpeg, packages, music, sfx, key...) | Naya laptop / Windows update ke baad / kuch ajeeb error aaye tab |
| `REEL STATUS.bat` | Saari stories ki table: kya bana, kya baaki | Roz subah, kaam shuru karne se pehle |
| `CODE SYNC.bat` | Laptop ka code GitHub par, cloud ka kaam laptop par | Din mein 1 baar (ya cloud par Claude ne kuch banaya ho tab) |
| `CLEANUP.bat` | Purani CHECK / contact-sheet / temp files ki list, chaho to Recycle Bin | Hafte mein 1 baar, ya disk bhar jaaye tab |

Sabhi `.bat` khud `py` (ya `python`) dhoondh lete hain, Devanagari / space wale raaste theek chalte hain (UTF-8 on).
Saath mein ek chhoti file `tools_common.py` hai – chaaron scripts folder ke raaste yahin se lete hain
(code folder = jahan script rakhi hai, stories = `C:\Users\Hp\Desktop\reels story`).

---

## 1. SETUP CHECK (`doctor.py` + `SETUP CHECK.bat`)

**Ye kya karta hai:** reel banane ke liye jo kuch chahiye wo laptop par hai ya nahi, ek baar mein dekhta hai.
Har kami ke saath **"KYA KARO"** line deta hai.

**Kaise kaam karta hai – ye sab check hota hai:**
- Python version, `py` launcher
- `ffmpeg` aur `ffprobe` (PATH par, ya WinGet wali jagah – bilkul make_reel jaisa)
- Python packages: pillow, numpy, faster-whisper (zaroori), openpyxl, requests (sab_pe_shak / comment_checker ke liye)
- Folders: `assets\ voice\ cases\ sfx\ music\ output\` + `reels story` folder (kitni stories mili)
- `music\bg music.mp3` – na ho aur `reels story\Common` mein ho to bolega "fix likho", phir copy kar deta hai
- `sfx\` mein CLAUDE.md wale saare sfx: pop, pop2, swish, whoosh, boom, ding, heartbeat, tick_fast
- Bonus: `cases\*.csv` mein jo sfx use hue (thunder, paper, ...) par `sfx\` mein nahi hain – unki list (DHYAAN)
- `reels story\Common` mein `CTA_HI.mp3`, `SIGNATURE_HI.mp3`, `bg music.mp3` (CTA/Signature dobara generate na karne ki yaad dilata hai)
- `assets\` mein BG_MAIN, LOGO_ROUND aur Shivam ke main poses (S01, S02, S06, S16, S17)
- Fonts: ariblk.ttf, impact.ttf
- `elevenlabs_key.txt` hai aur khaali nahi – **key kabhi screen par print nahi hoti**. Saath mein check: key galti se git mein to nahi gayi / .gitignore use rok raha hai
- Disk mein 5 GB se kam jagah ho to warning

**Kya badalta hai:** kuch nahi. Sirf jab aap "fix" likho tab `bg music.mp3` Common se `music\` mein copy hoti hai (CLAUDE.md wala rule).

**Kaise chalana hai:** `SETUP CHECK.bat` double-click → list aayegi → music copy karni ho to `fix` likho, warna Enter.

**Example output:**
```
== Packages ==
  [OK]    pillow installed
  [KAMI]  faster-whisper nahi hai (timing (Whisper) / sab_pe_shak)
           KYA KARO: PowerShell mein chalao: py -m pip install faster-whisper
== Music ==
  [KAMI]  music\bg music.mp3 nahi hai (reel bina music ke banegi!)
           KYA KARO: SETUP CHECK.bat mein 'fix' likho (ya: py doctor.py --fix) -> Common se copy ho jaayegi.
== SFX ==
  [KAMI]  ye sfx nahi mile: tick_fast
== ElevenLabs ==
  [OK]    elevenlabs_key.txt hai (key chhupi rakhi gayi)
============================================================
3 KAMI hai (upar [KAMI] wali lines) – 'KYA KARO' follow karo, phir dobara chalao.
```

---

## 2. REEL STATUS (`reel_status.py` + `REEL STATUS.bat`)

**Ye kya karta hai:** `reels story` ki har `Category N\Story NN` folder dekh kar table banata hai –
har reel ka kya bana aur **agla kaam kya hai**. Aakhir mein "Ye reels baaki hain" list.

**Kaise kaam karta hai:**
- Dono layout dhoondhta hai: `reels story\Category 9\Story 10` aur `reels story\category\Category 9\Story 10`
- Reel ka naam: story folder ki MP4 se; MP4 na ho to `SCRIPT_*.txt` ki pehli line se ("Case 09-010: Til Gud ki Dopahar")
- Columns:
  - **Script** = `SCRIPT_*.txt` · **VO** = story folder mein `VO_MAIN.mp3`
  - **Voice** = `voice\<reel>.m4a` (final voice) · **CSV** = `cases\<reel>.csv`
  - **MP4** = story folder mein MP4 · **timing** = `timing.csv` · **Cover** = `- COVER.png`
- Naam thoda alag ho (jaise "v2") to bhi ID (`09-010 ...`) se file mil jaati hai
- "Agla kaam" sahi kram mein: Voice banao → build_voice → CSV likho → Render → MP4 copy → timing.csv → Cover.
  Agar MP4 `output\` mein bani padi hai par story folder mein nahi gayi, ye bhi pakad leta hai.

**Kya badalta hai:** story folder mein **kuch nahi** likhta (test se pakka kiya). `.bat` se chalane par
`output\REEL STATUS.html` (browser mein khulta hai, "sirf baaki dikhao" checkbox) aur `output\REEL STATUS.csv` banti hai.

**Kaise chalana hai:** `REEL STATUS.bat` double-click. Report browser mein apne aap khul jaati hai.
Extra: `py reel_status.py --baaki` (sirf adhoori), `py reel_status.py --category 9`.

**Example output:**
```
Story    Reel                      Script   VO   Voice   CSV    MP4   timing Cover   Agla kaam
----------------------------------------------------------------------------------------------
C9 S10   09-010 Til Gud ki Dopahar   ✓      ✓      ✓      ✓      ✓      ✓      ✓     ✓ puri
C9 S11   09-011 Diwali ki Raat       ✓      ✓      -      -      -      -      -     build_voice.py chalao

Kul 2 stories: 1 puri, 1 baaki.

Ye reels baaki hain:
  - C9 S11  09-011 Diwali ki Raat  ->  build_voice.py chalao
```

---

## 3. CODE SYNC (`code_sync.py` + `CODE SYNC.bat`)

**Ye kya karta hai:** laptop ka code GitHub par bhejta hai aur cloud (Claude) ka kaam laptop par laata hai – ek click mein.

**Kaise kaam karta hai (isi kram mein):**
1. Laptop par kya badla – list dikhata hai (naya / badla / hataya)
2. **Secret check** – inme se kuch bhi jaa raha ho to **wahin ruk jaata hai, kuch commit/push nahi hota**:
   - naam se: `elevenlabs_key.txt`, `.env`, `*secret*`, `*credential*`, `token*.json`, `*.pem`, `*.key`...
     (sirf woh jo `.gitignore` ke bahar hain – ignore wali files waise bhi nahi jaati)
   - file ke andar: ElevenLabs `sk_...` key, Google/GitHub/Telegram/Instagram token, private key
     (key screen par nahi dikhti, sirf "helper.py line 2 par ElevenLabs key jaisa kuch hai")
   - 50 MB se badi file (galti se video/audio)
3. Commit – message poochta hai, Enter dabao to "laptop se update 18-10-2026 14:30"
4. GitHub se cloud ka kaam laata hai (merge, history kabhi rewrite nahi)
5. **Conflict** (laptop aur cloud dono ne same file badli): merge **cancel** karke sab pehle jaisa kar deta hai,
   files ki list dikhata hai aur bolta hai "Claude ko bolo". Aapka kaam commit mein safe rehta hai.
6. Push
7. Cloud par jo branches abhi aapke code mein merge nahi hui (jaise ye `repeat-task-tools`) – unki list, taaki pata rahe kya pending hai

Internet / login / git naam-email na ho to bhi Hinglish mein seedha bata deta hai kya karna hai.

**Kaise chalana hai:** `CODE SYNC.bat` double-click → list dekho → message likho ya Enter.
Sirf dekhna ho (kuch na bheje): `py code_sync.py --dry-run`.

**Example output:**
```
Branch: main

Laptop par 2 badlav:
  [badla     ] make_reel.py
  [naya      ] cases/09-011 Diwali ki Raat.csv
Secret check: theek (koi key/.env/badi media file nahi).

Commit ka message likho (Enter = 'laptop se update 18-10-2026 14:30'):
Commit ho gaya: laptop se update 18-10-2026 14:30
GitHub se naya kaam la rahe hain...
Cloud ka kaam aa gaya.
GitHub par bhej rahe hain...
Push ho gaya.

Cloud par in branches mein kaam hai jo abhi aapke code mein NAHI aaya (Claude se merge karwao):
  - origin/repeat-task-tools  (2026-10-18)  Naye helper scripts: doctor, reel_status, code_sync, cleanup

SYNC POORA.
```
Secret mila to:
```
============================================================
RUK GAYE – ye files GitHub par nahi jaani chahiye:
  !! elevenlabs_key.txt  (naam se secret/key file lagti hai)
KYA KARO: Claude ko bolo 'ye file .gitignore mein daalo' (key wali file kabhi upload nahi hoti).
Kuch commit/push nahi hua.
============================================================
```

---

## 4. CLEANUP (`cleanup.py` + `CLEANUP.bat`)

**Ye kya karta hai:** purani kachra files dhoondhta hai jo jagah kha rahi hain, size + date ke saath list deta hai.

**Kaise kaam karta hai:**
- Sirf code folder ke **`output\`** (`<reel> - CHECK.png` frame grid, `<story> - IMAGES.png` contact sheet)
  aur **`work\`** (voice ki temp files) dekhta hai
- **Kabhi nahi chhuta:** story folder, `voice\`, `cases\`, `assets\`, `music\`, `sfx\`, MP4, cover, `.lock` files
  (har file par dobara check hota hai, galti se list mein aa bhi jaaye to nahi hatti)
- Sirf 3 din se purani files (abhi chal rahi dusri chat ki temp file nahi hatti). `--days 10` se badal sakte ho
- Default **sirf list**. "haan" likhoge tabhi files **Recycle Bin** mein jaati hain (permanent delete nahi –
  galti ho to Recycle Bin se Restore). Recycle Bin na mile to kuch delete hi nahi karta.

**Kaise chalana hai:** `CLEANUP.bat` double-click → list dekho → hatana ho to `haan` likho, warna Enter.

**Example output:**
```
     Size  Date              Kya            File
   1.9 MB  01-10-2026 00:00  CHECK grid     output\09-010 Til Gud ki Dopahar - CHECK.png
 878.9 KB  01-10-2026 00:00  contact sheet  output\Story 10 0910 - IMAGES.png

2 files, kul 2.8 MB (sirf output\ aur work\ ki; MP4/voice/story nahi).
Kuch delete nahi kiya. Hatana ho to: py cleanup.py --delete  (Recycle Bin mein jaayengi)
Recycle Bin mein bhejna hai? haan likho (warna Enter): haan
2 files Recycle Bin mein gayi.
```

---

## Jo extra joda (aur kyun)

- **doctor mein "CSV mein use hue par sfx\ mein nahi" check** – purani CSVs mein thunder, paper, phone, hit jaise sfx hain.
  Kabhi purani reel dobara render karni pade to make_reel wahin ruk jaata hai; ye pehle se bata deta hai.
- **doctor mein "key git mein to nahi gayi" check** – key leak hona sabse mehenga nuksaan hai.
- **reel_status mein "MP4 output\ mein hai, story folder mein copy karo"** – step 9 (copy) bhoolna aam galti hai.
- **code_sync mein "cloud ki pending branches" list** – cloud par Claude jo kaam branch par chhodta hai, wo laptop par
  tabhi aata hai jab merge ho; ye list yaad dilati hai.
- Alag se "MP4 + timing.csv story folder mein copy" wala script **nahi** banaya – dusri session `make_full_reel.py`
  bana rahi hai jo ye step sambhalegi, dono takrayein nahi.

---

## Tests (cloud par, nakli folders ke saath – koi asli media / API nahi)

`tests\` folder mein 23 tests (pytest):
- **doctor** (6): sab theek, music missing + `--fix` se copy, sfx missing, CSV wala sfx missing, key khaali/missing aur key kabhi print nahi hoti, Common CTA missing
- **reel_status** (5): dono folder layout, Devanagari naam, sahi "agla kaam", category filter, story folder mein kuch nahi likha (pehle/baad snapshot same), HTML/CSV report, ID se file match (09-0101 galti se 09-010 nahi banta)
- **cleanup** (5): sirf purani CHECK/IMAGES/work files aati hain; voice\, story folder, .lock, MP4, cover kabhi nahi; nayi files chhod deta hai; delete sirf Recycle Bin se; Recycle Bin na ho to kuch nahi hatta
- **code_sync** (7, asli git repos ke saath): normal sync (cloud ka kaam aaya + push hua + ignored key nahi gayi), key file .gitignore ke bahar → ruka, code ke andar key → ruka aur key print nahi hui, .env / 50 MB+ file → ruka, conflict → merge cancel + laptop ka kaam safe, --dry-run kuch nahi badalta, pending cloud branch ki list

Result:
```
$ python -m pytest -q tests
.......................                                                  [100%]
23 passed in 2.42s
```

Note: Recycle Bin (Windows) aur fonts wala hissa cloud (Linux) par nahi chal sakta – unke liye test mein nakli Recycle Bin use hua.
Laptop par pehli baar `CLEANUP.bat` chalate waqt ek baar dekh lena ki file Recycle Bin mein dikhi.
