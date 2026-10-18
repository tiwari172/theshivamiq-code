# theshivamiq YouTube Scheduler – Setup (Windows)

Folder: `C:\Users\Hp\Desktop\theshivamiq code\yt_scheduler\`
Har kaam ke liye is folder mein **double-click wali .bat file** hai. Command type karne ki zaroorat nahi.

| File | Kya karti hai |
|---|---|
| `0 INSTALL.bat` | Zaroori Python packages install (sirf ek baar) |
| `1 DRY RUN.bat` | Sirf dikhati hai kya upload hoga. Kuch upload nahi, Excel nahi badalti |
| `2 TEST 1 VIDEO.bat` | Sirf 1 video upload (`--max 1`) |
| `3 UPLOAD.bat` | Asli run – aaj ke quota tak (max 6) |
| `4 STATUS.bat` | Kitni PENDING / SCHEDULED / FAILED + agli 5 rows |
| `5 RETRY FAILED.bat` | FAILED rows ko wapas PENDING (upload nahi karti) |

> ⚠️ **Audit se pehle:** Google ka unverified project jo video upload karta hai wo **"Private (locked)"** rehti hai – schedule time par public NAHI hogi aur Studio mein bhi badal nahi sakte. Isliye audit pass hone tak sirf `1 DRY RUN` / `4 STATUS` chalao, upload haath se karo. Audit ke steps: `YOUTUBE AUDIT FORM - STEPS.txt`.

---

## 1. Python
Aapke laptop mein Python 3.14 pehle se hai – kuch karna nahi.
(Naye laptop par: python.org → Downloads → Windows installer → install screen par sabse neeche **"Add python.exe to PATH" ✅ tick zaroor karo** → Install Now.)

## 2. Packages install
`0 INSTALL.bat` par double-click. Aakhir mein "Successfully installed…" ya "Requirement already satisfied" aaye to sahi hai. (Ye ho chuka hai.)

## 3. Excel aur paths
- `.env` file (isi folder mein) mein saare paths hain. Notepad se kholo. Abhi:
  - Videos: `C:\Users\Hp\Desktop\theshivamiq code\output`
  - Excel: `C:\Users\Hp\Desktop\theshivamiq code\yt_scheduler\schedule.xlsx`
- Apni Excel ya to is folder mein `schedule.xlsx` naam se rakho, ya `.env` mein `EXCEL_PATH=` ke aage asli path likho (quotes mat lagana).
- (Optional) `.env` mein `YT_CONTAINS_SYNTHETIC_MEDIA=Haan` likhoge to YouTube ko bataya jaayega ki video mein AI (asli jaisi dikhne wali) cheez hai; `Nahi` = nahi hai; khaali/na likho = script kuch nahi bhejti (pehle jaisa).
- Excel ke `video_filename` column mein **exact file naam** likho, jaise `01 Ghup Andhera.mp4`.
- `schedule_datetime` = `2026-10-14 08:00:00` (India time).
- Script sirf "Post Schedule" sheet ke ye 4 columns badalti hai: `status, log_message, youtube_video_id, processed_at`.
- Har likhne se pehle Excel ki copy `backups\` folder mein ban jaati hai (last 20 rakhti hai).
- ⚠️ Excel mein **chart, picture ya shape** ho to openpyxl save karte waqt wo hat sakte hain (formulas, colors, baaki sheets theek rehti hain). Aisa ho to `backups\` se purani file wapas le lo, aur us cheez ko alag file mein rakho.

## 4. Google Cloud Console (ek baar)
1. https://console.cloud.google.com kholo, wahi Google account jiska YouTube channel hai.
2. Upar project dropdown → **New Project** → naam `theshivamiq-uploader` → Create. Phir upar se wahi project select karo.
3. Left menu ☰ → **APIs & Services → Library** → search "YouTube Data API v3" → kholo → **Enable**.
4. **APIs & Services → OAuth consent screen** (naye UI mein "Google Auth Platform"):
   - Get started → App name `theshivamiq uploader`, support email = aapka email → User type **External** → contact email → Create.
   - **Audience** tab → Test users mein apna email Add karo.
   - Phir isi Audience page par **Publish app** dabao → status **"In production"** ho jaayega.
     (Ye zaroori hai, warna login 7 din mein expire hota hai. "Verification needed" jaisi warning aaye to ignore karo – submit karne ki zaroorat nahi.)
5. **Clients** (ya Credentials → Create Credentials → OAuth client ID) → Application type **Desktop app** → naam `uploader` → Create.
6. **Download JSON** → file ka naam badal kar `client_secret.json` rakho → is folder (`yt_scheduler\`) mein daalo.
   ⚠️ Ye file aur `token.json` kisi ko mat bhejna.

## 5. Pehli baar login
`1 DRY RUN.bat` login nahi maangta. Pehli baar jab `2 TEST 1 VIDEO.bat` chalaoge:
1. Browser khulega → YouTube channel wala account chuno.
2. "Google hasn't verified this app" → **Advanced** → **Go to theshivamiq uploader (unsafe)** → Continue / Allow.
3. "The authentication flow has completed" dikhe to browser band karo. `token.json` apne aap ban jaayegi – agli baar login nahi maangega.

## 6. Pehle DRY RUN
`1 DRY RUN.bat` – kuch aisa dikhega:
```
===== DRY RUN (kuch upload nahi hoga, Excel nahi badlega) =====
Aaj ka quota bacha: 6/6
Ready rows: 2
  1. 2026-10-14 08:00 IST | 01 Ghup Andhera.mp4 | file mili | Ghup andhere mein khoon...  <- is run mein jayegi
  2. 2026-10-15 08:00 IST | 02 Saalgirah ki Raat.mp4 | file mili | Saalgirah ki raat...  <- is run mein jayegi
Problem wali rows (asli run mein FAILED hongi): 1
  - Row 7 (03 Test.mp4): video file nahi mili: C:\...\output\03 Test.mp4
```
Problem wali rows theek karo (file naam / date), phir dobara dry run.

## 7. Ek video se test
`2 TEST 1 VIDEO.bat` → `upload 12%… 100%` → `SCHEDULED - video id …`.
Phir **YouTube Studio → Content** mein dekho: video **Private** ho aur uske neeche **"Scheduled"** + aapka time dikhe.
Theek ho to aage se `3 UPLOAD.bat`.

## Rules jo script khud follow karti hai
- Sirf wo rows: status khaali/PENDING, target_platform YOUTUBE ya BOTH, time abhi se 30+ min aage. Sabse pehle wala time pehle.
- Roz max 6 upload (`quota_state.json`). YouTube ka quota **Pacific Time** ki aadhi raat par reset hota hai = India mein **dopahar ~12:30** (Mar–Nov) / **~1:30** (Nov–Mar). Script bhi ab isi hisaab se ginti hai. 6 ke baad: "Aaj ka quota khatam (6/6). Kal phir chalao."
- Ek saath do baar nahi chalti: chalte waqt `scheduler.lock` banti hai. Doosri window khologe to "Scheduler pehle se chal raha hai" aayega (warna same video 2 baar upload ho sakti thi). Koi window na chal rahi ho aur phir bhi ye aaye to `scheduler.lock` delete karo (6 ghante se purani lock khud hat jaati hai).
- Har upload ke turant baad Excel save. Excel khuli ho to shuru mein hi: "schedule.xlsx Excel me khuli hai, pehle band karo."
- Beech mein save fail ho to `pending_updates.json` mein data rakhti hai; agli baar chalane par khud Excel mein daal deti hai.
- Har cheez `scheduler.log` mein bhi likhi jaati hai.
- `ig_caption` ko chhoti bhi nahi.

## Common errors
| Error | Matlab / kya karein |
|---|---|
| `quotaExceeded` | Aaj ka YouTube quota khatam. Row PENDING rehti hai. Dopahar ~1:30 IST ke baad dobara chalao. |
| `Scheduler pehle se chal raha hai` | Doosri black window abhi upload kar rahi hai – usse khatam hone do. Koi window nahi to `scheduler.lock` delete karo. |
| `invalidPublishAt` / publishAt must be in the future | Schedule time nikal gaya ya bahut paas hai. Excel mein time aage karo → `5 RETRY FAILED.bat` → phir upload. |
| `Excel me khuli hai, pehle band karo` / PermissionError | Excel band karo (Task Manager mein bhi Excel na chal raha ho), phir chalao. |
| `invalid_grant` / token expired | `token.json` delete karo, dobara chalao → browser login. Har hafte aaye to step 4 ka "In production" check karo. |
| Video "Private (locked)", schedule nahi dikh raha | Project ka audit nahi hua. Video delete karo, haath se upload karo, audit form bharo (`YOUTUBE AUDIT FORM - STEPS.txt`). |
| `client_secret.json nahi mili` | Step 4.6 dobara – file is folder mein `client_secret.json` naam se ho. |
| `video file nahi mili` | Excel ka `video_filename` aur `output\` ki file ka naam bilkul same ho (.mp4 ke saath). |

## Commands (agar .bat ki jagah khud chalana ho)
```
py scheduler.py --dry-run
py scheduler.py
py scheduler.py --max 3
py scheduler.py --status
py scheduler.py --retry-failed
```
