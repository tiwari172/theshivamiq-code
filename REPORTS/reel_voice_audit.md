# Reel + Voice scripts ki jaanch (audit) – seedhi bhasha mein

**Branch:** `audit-reel-voice` (main par kuch nahi gaya)
**Kya nahi badla:** reel ka look/sound (size, rang, music level, effects), command-line arguments,
output files ke naam aur jagah, aur wo lines jo dusre scripts padhte hain (build_voice ke shabd-times + THINK line,
prep_story ki "CSV mein ye naam lagao" list, check_reel ka PROBLEM output). ElevenLabs ko ek bhi asli call nahi hui.

Har badlav chhota hai. Zyaadatar fix ek hi tarah ke hain: **pehle script ek lamba English error (traceback) de kar
band ho jaata tha, ab saaf Hinglish message deta hai ki kya galat hai aur kya karna hai.**

---

## 1. make_reel.py – reel banane wala main script

**Kya karta hai:** `cases\<naam>.csv` padhta hai, har frame par background + images + text banata hai, aur
voice + music + sound effects jod kar 1080x1920 MP4 banata hai. Render se pehle `check_reel` chalata hai, baad mein
16 frames ki CHECK grid banata hai.

**Kya badla:**

| Pehle kya karta tha | Problem kya thi (kab dikhti) | Ab kaise kaam karega |
|---|---|---|
| Music sirf `music\` folder mein dhoondhta tha. | `music\` khaali ho to reel **bina music** ban jaati thi (CLAUDE.md: "Music har reel mein hona chahiye"). Ye galti pehle ho chuki hai. | `music\` khaali ho to apne aap `reels story\Common\bg music.mp3` le leta hai. Wo bhi na mile to bada "DHYAAN DO: music nahi mila!" likhta hai. Log mein "(music: ...)" pehle jaisa. Music ka level nahi badla. |
| Naam galat likhne par (`py make_reel.py "09-010 Til Gud"`) seedha CSV kholta tha. | Lamba English error, samajh nahi aata kya hua. | "CSV nahi mili: cases\\... (naam check karo)". |
| CSV mein sirf header / STYLE line ho to bhi aage badhta tha. | `max() arg is an empty sequence` crash. | "CSV mein koi row nahi hai". |
| `focus` column mein ek hi number (jaise `0.5`) ho to chal padta tha. | Render **beech mein** (minute bhar baad) crash. | CSV padhte hi bata deta hai: "CSV line 7 mein galti hai… focus 'x;y' (jaise 0.5;0.3)". |
| FFmpeg render ke beech band ho jaaye (galat filter, disk full). | `BrokenPipeError` ka lamba error. | Saaf "FFmpeg fail hua" + agli reel par chala jaata hai. |
| Audio file kharab ho to `could not convert string to float`. | Samajh nahi aata kaunsi file. | "Audio file ki length nahi padh paaya: <file ka naam>". |
| ffprobe hamesha `ffmpeg wale folder\ffprobe.exe` maanta tha. | Kisi aur jagah se install FFmpeg (ya cloud) par crash. | Wahan na mile to PATH wala ffprobe leta hai. Laptop par pehle jaisa. |
| `bg` effect wali poori-screen photo `.jpg` ho to "assets mein nahi hai" bolta tha (jabki render .jpg le leta hai). | Galat PROBLEM, reel ruk jaati. | `bg` wali image ke liye `.jpg` bhi maan leta hai. |

**Risk:** koi nahi dikha. Render ka tareeka (frames, animation, mixing) bilkul wahi hai.

---

## 2. check_reel.py – render se pehle galti pakadne wala

**Kya karta hai:** CSV ko bina video banaye check karta hai: text image ke upar to nahi, text 3 line se lamba to nahi,
screen par sirf text (khaali screen) to nahi, image ka safed dabba (`_CUT` chahiye) ya neeche se kati (`_UP` chahiye).

**Kya badla:**

| Pehle | Problem | Ab |
|---|---|---|
| Koi image `assets\` mein na ho to "nahi hai" likh kar aage check karta tha. | Aage wale check mein **crash** (`py check_reel.py` akele chalane par). PROBLEM list dikhti hi nahi thi. | Gayab image ki PROBLEM dikhata hai aur baaki check bhi poora karta hai, crash nahi. |
| "S" se shuru har naam ko Shivam maan kar neeche-kata check chhod deta tha. | `SOFA`, `SAFE`, `STOOL` jaise prop kabhi `_UP` nahi bante the → screen ke neeche kate dikhte (CLAUDE.md wali galti). | Sirf Shivam (`S01`, `S16`, `S2_17` … yaani S ke baad number) chhodta hai. Baaki "S" wale prop bhi check hote hain. |
| CSV na mile / khaali ho to crash. | Lamba error. | PROBLEM mein saaf likhta hai. |
| `bg` wali photo par bhi "safed background → _CUT banao" bolta tha. | Faltu DHYAAN DO. | Poori-screen photo par ye check nahi. |

PROBLEM / DHYAAN DO / "check OK" ka format **bilkul wahi** hai (make_full_reel isi ko padhega).

---

## 3. prep_story.py – story ki images taiyaar karna

**Kya karta hai:** story ke `images\` ki PNG `assets\` mein copy karta hai (same naam par alag image ho to `<ID>_<CCSS>`),
safed background wali ka `_CUT`, neeche chipke prop ka `_UP`, aur contact sheet banata hai. Aakhir mein
"CSV mein ye naam lagao" list.

**Kya badla:**

| Pehle | Problem | Ab |
|---|---|---|
| Path ke aakhir mein `\"` ho (`"...\Story 07\"`) to Windows aakhri `"` bhi naam mein de deta hai. | "images folder nahi mila" – jabki folder sahi tha. | Faltu `"` hata deta hai. |
| `images\` mein ek bhi PNG na ho to bhi contact sheet banane jaata tha. | 0-height image ka crash. | "images folder mein koi PNG nahi mili". |
| `.jpg` / `.webp` image chup-chaap chhod deta tha. | Image gayab, pata hi nahi chalta. | Note dikhata hai: "P_PHOTO.jpg: PNG nahi hai, chhod diya". |
| `assets\` folder na ho to copy fail. | Crash. | Folder khud bana leta hai. |
| `SOFA` jaise "S" wale prop ka `_UP` nahi banta tha (check_reel wali wajah). | Kati hui image. | Ab `_UP` banta hai – list mein `SOFA -> SOFA_UP` dikhega. |

"CSV mein ye naam lagao" list ka format wahi hai.
**Risk (badla nahi):** agar story ki image badal kar dobara chalao aur `<ID>_CCSS` / `_CUT` / `_UP` pehle se bane hon,
to purane hi rehte hain (naya nahi banta). Image badli ho to un purani files ko haath se hatana padega.

---

## 4. make_cards.py – options card (1-2-3-4) aur purana cover

**Kya karta hai:** suspects ki images ko number ke saath ek card (`C0NN_OPTIONS.png`) mein jodta hai; `cover` se purane style ka cover.

**Kya badla:**

| Pehle | Problem | Ab |
|---|---|---|
| `ID:Naam` mein `:` bhool jao ya naam mein `:` ho. | `ValueError` crash. | "'C001_ROHIT' galat hai -> ID:Naam likho". Naam mein `:` ho to bhi chalta hai. |
| Image ID galat ho. | `Image.open(None)` crash. | "image nahi mili: assets\\GAYAB.png". |
| Arguments kam ho. | `IndexError` / `TypeError`. | Sahi tareeka print karta hai. |

Card ka design bilkul nahi badla.

---

## 5. make_cover.py – naya "Case File" cover

**Kya karta hai:** reel ke naam se case number (`CASE #10-004`), CSV ki hook line se sawaal (KILLER KAUN?), aur
Shivam + logo + police tape wala cover. `all` = har story folder jisme MP4 hai.

**Kya badla:**

| Pehle | Problem | Ab |
|---|---|---|
| Reel ka naam `10-004 Title` / `04 Title` jaisa na ho (jaise kisi folder mein `final.mp4`). | `all` **poora ruk jaata** tha (AttributeError), baaki covers bhi nahi bante. | Wo reel "skip: naam samajh nahi aaya" likh kar chhod deta hai, baaki sab bante hain. |
| Folder ka naam `Category Hooks` jaisa (bina number). | Crash. | Chal jaata hai. |
| Logo / S16 file na mile. | Pehle cover par crash. | Shuru mein hi bata deta hai kaunsi file nahi mili. |
| `one` mein argument kam. | IndexError. | Sahi tareeka print. |

Design, naam (`- COVER.png` / `- COVER NEW.png`) sab wahi.
**Risk (badla nahi, jaan-bujh kar):** `all` har baar chalane par jin reels ka cover pehle se hai unka `- COVER NEW.png`
dobara banata hai (purana kabhi nahi mitata). Isse ~200 reels mein thoda time lagta hai aur folders mein duplicate NEW
file aati hai. Ek reel ke liye CLAUDE.md wala `make_cover.py one ...` use karo – wo tez hai.

---

## 6. make_cover2.py – cover v2 (A/B/C rang)

**Kya karta hai:** make_cover jaisa hi cover, teen rang styles mein, aur green-screen wala naya Shivam face khud saaf karta hai.

**Kya badla:**

| Pehle | Problem | Ab |
|---|---|---|
| `info()` (naam → case number + sawaal) ki **copy** make_cover se alag rakhi thi. | Dono mein same crash bug, ek theek karo to dusra reh jaata. | Ab make_cover wala hi use karta hai (ek jagah). |
| `one` ke saath out.png na do. | `save(None)` crash. | Saaf error. |
| `output\` folder na ho. | Crash. | Folder bana leta hai. |
| Face / logo file na mile. | Beech mein crash. | Shuru mein bata deta hai. |

---

## 7. make_sfx.py – computer se banaye trial sound effects

**Kya karta hai:** pop, pop2, swish, whoosh, boom, heartbeat, ding `.wav` banata hai (sirf jo `sfx\` mein pehle se nahi).

**Theek hai, kuch nahi badla.** Test mein saare sounds ban kar check hue.
**Risk:** `tick_fast.wav` (soch wale 3 sec ka stopwatch) ye script nahi banata – wo laptop ke `sfx\` mein pehle se hai.
Wo file kabhi delete ho jaaye to check_case "sound 'tick_fast' sfx folder mein nahi hai" bolega.

---

## 8. build_voice.py – VO + CTA + Signature jod kar final voice

**Kya karta hai:** story ka `VO_MAIN.mp3` + `CTA_HI` + `SIGNATURE_HI` jodta hai, `tighten_voice` se chup kaat-kar thoda tez
karta hai, "डिटेक्टिव शिवम…" se pehle 3 sec ka THINK pause daalta hai, aur har shabd ka naya time print karta hai (CSV isi se).

**Kya badla:**

| Pehle | Problem | Ab |
|---|---|---|
| Pehli line mein `C:\Users\Hp\Desktop\theshivamiq code` **hardcoded** tha. | Folder ka naam/jagah badle to turant crash; cloud par test hi nahi ho sakta tha. | Script jahan rakha hai wahi folder use karta hai (laptop par wahi jagah). |
| THINK text (jaise "डिटेक्टिव शिवम") voice ke text mein na mile (spelling thodi alag). | Poora kaam (jodna + tighten) karke **aakhir mein IndexError crash**, voice nahi banti. | Shuru mein hi: "THINK text … nahi mila. Script se same shabd copy karke do." |
| Nukta wale akshar (ज़, ड़, क़) do tarah type hote hain (ek akshar ya akshar + bindi). | Dikhne mein same, par match nahi hota → upar wala crash. | Dono roop try karta hai. |
| VO_MAIN.mp3 / timing.json / CTA / Signature na ho. | FFmpeg ka lamba error. | "File nahi mili: <path>". |
| tighten_voice fail ho. | Error chhupa reh jaata. | Asli error dikhata hai. |
| Devanagari shabd print karte waqt (jab koi dusra script output padhe). | Kuch Windows settings par `UnicodeEncodeError`. | Output UTF-8 mein (eleven_voice jaisa). |

**Printed lines bilkul wahi:** `THINK pause X -> Y`, har shabd `  start    end shabd`, aur `last chunks start: …`.
Arguments wahi: `py -u build_voice.py "<story folder>" "<NN Title>" "डिटेक्टिव शिवम" 3.0`.

---

## 9. tighten_voice.py – lambi chup chhoti karna + 7% tez

**Kya karta hai:** FFmpeg se chup wali jagah dhoondhta hai, har chup ko 0.28 sec kar deta hai, poori voice 7% tez,
aur har tukde ka purana → naya time print karta hai.

**Kya badla:**

| Pehle | Problem | Ab |
|---|---|---|
| FFmpeg kabhi `silence_start: -0.002` (minus) deta hai; script minus chhod kar `0.002` padhta tha. | Voice ke shuru mein ek **faltu chhota tukda + 0.28 sec chup** jud jaata (kuch mp3 mein). Sab time thode aage khisak jaate. | Minus ko 0 maanta hai – shuru mein faltu chup nahi. |
| Poori chup file. | Ajeeb FFmpeg error. | "Voice mein koi awaaz nahi mili". |
| Temp file ka naam banane ke liye maanta tha extension 4 letter ka hai. | `.flac` jaise naam par fail. | Kisi bhi extension par chalta hai. |
| Arguments kam. | IndexError. | Sahi tareeka print. |

Print ki table (`purana time -> naya time`) bilkul wahi format.

---

## 10. eleven_voice.py – ElevenLabs se VO_MAIN.mp3

**Kya karta hai:** story ka `VO_*.txt` (ya SCRIPT ka MAIN VOICEOVER) padhta hai, CTA/Signature wali lines hata deta hai
(wo Common se judti hain), aur ElevenLabs (Rudra voice, v3) se `VO_MAIN.mp3` + `VO_MAIN_timing.json` banata hai.
Credits pehle check karta hai, bani hui file dobara nahi banata.

**Kya badla (API wala hissa bilkul nahi chhua, koi asli call nahi):**

| Pehle | Problem | Ab |
|---|---|---|
| Signature line ("…की नज़र से…") hatane ke liye exact akshar milata tha. | Agar VO file mein ज़ dusre tareeke se type ho to signature line **nahi hatti** → credits faltu kharch + final voice mein signature **do baar**. | Dono roop ek jaisa karke milata hai. |
| `elevenlabs_voice.txt` khaali ho. | IndexError crash. | Library se voice dobara dhoondh leta hai. |
| Category / story number galat (`abc`, `9-`). | ValueError crash. | "Aise likho: 9 ya 9-12". |
| Voice ka text khaali mile. | Chup-chaap kuch nahi banta. | "voice ka text khaali mila … skip" likhta hai. |

**Risk:** `VOICE BANAO.bat` mein `fixed` option CTA/Signature banata hai – lekin sirf tab jab file Common mein **na ho**
(pehle se hai to skip). Isliye safe hai; bas Common se CTA_HI.mp3 / SIGNATURE_HI.mp3 kabhi delete mat karna.

---

## 11. voice_queue.py – kai chats ek saath voice banayein to takkar na ho

**Kya karta hai:** har voice kaam ko alag folder (`work\voice_slotN`) deta hai; saare busy hon to line mein rokta hai.
`safe_replace` poori file banne ke baad hi final naam deta hai.

**Kya badla:**

| Pehle | Problem | Ab |
|---|---|---|
| Sirf Windows wala lock (`msvcrt`) use karta tha. | Windows ke bahar import hi nahi hota → build_voice / eleven_voice / tts ka koi test nahi ho sakta tha (cloud session make_full_reel ke liye bhi). | Windows par **bilkul wahi** lock; dusri jagah Linux wala lock. |
| `py voice_queue.py` bina command. | Crash. | Sahi tareeka print. |
| `ffmpeg` PATH mein na ho (sirf winget folder mein). | "file not found". | make_reel wala FFmpeg dhoondh leta hai. |

---

## 12. tts_voice.py – free Microsoft awaaz

**Kya karta hai:** `voice_scripts\<naam>.txt` (mood | pause | text) se free Edge awaaz banata hai.
**Yaad rahe: aapne ye awaaz reject ki hai – reel ke liye sirf ElevenLabs.**

**Kya badla:**

| Pehle | Problem | Ab |
|---|---|---|
| Temp files `%TEMP%` mein banata tha aur kabhi saaf nahi karta tha. | CLAUDE.md ka rule tootta tha ("TEMP mein temp file KABHI mat banao"), aur kachra jamta tha. | voice_queue ka apna slot folder, kaam ke baad saaf. |
| Chalate hi koi chetavni nahi. | Galti se reel ke liye use ho sakta tha. | Shuru mein likhta hai "ye free awaaz user ne reject ki hai -> eleven_voice.py use karo". |
| Line mein `|` kam ho ya pause number na ho. | ValueError crash. | "line 3: 'mood \| pause \| text' format nahi hai". |

---

## 13. REEL BANAO.bat

**Kya karta hai:** double-click par `cases\` ki saari nayi reels banata hai.

**Kya badla:** pehle `python` se chalta tha, jabki CLAUDE.md ke saare command `py` se chalte hain (aur wahi laptop par roz chalte hain).
Kuch Windows par `python` likhne se Microsoft Store khul jaata hai. **Ab `py` use karta hai, `py` na ho to `python`.**

## 14. VOICE BANAO.bat

**Kya karta hai:** ElevenLabs menu (test / fixed / sfx / category number).

**Kya badla:**
- `py` pehle (REEL BANAO jaisa).
- Kuch likhe bina Enter dabao to pehle ajeeb command chalti thi; ab `test` (key + credits check) chalta hai.
- Repo mein `.gitattributes` joda: `.bat` files laptop par hamesha Windows wali line-ending (CRLF) mein aayengi. LF wali .bat mein
  `goto` kabhi kabhi fail hota hai.

---

## Tests ka result

- `tests/` folder mein **55 tests** (pytest), nakli images + nakli awaaz (FFmpeg se tone/chup) ke saath.
  Ek chhoti asli reel bhi render hoti hai (MP4 + CHECK grid + "(music: bg music.mp3)" check).
- **Naye code par: 55 pass, 0 fail.**
- Yahi tests purane code par chalaye: Linux par import hi nahi hua (msvcrt). Naya voice_queue daal kar chalaye to
  **13 fail + 37 error** – yaani tests sach mein in bugs ko pakadte hain.
- ElevenLabs / internet ko test mein call karna block hai (galti se bhi credit nahi lagega).
- Chalane ka tareeka (laptop par bhi): `py -m pip install pytest` phir `py -m pytest tests`
  (tests apne temp folder mein chalte hain, laptop ki assets / voice / output ko nahi chhoote; laptop par ariblk font use hota hai).

## Laptop par kya asli test karna chahiye (pull ke baad)

1. **Ek purani reel dobara render** (`py make_reel.py "09-010 Til Gud ki Dopahar" --redo` jaisa, ya koi bhi):
   video purani jaisi dikhni/sunni chahiye, log mein "(music: bg music.mp3)" aaye.
2. **Music fallback:** `music\` folder ka naam thodi der badlo, render karo → log mein "(music: bg music.mp3)" (Common wala) aana chahiye. Phir naam wapas.
3. **build_voice** ek nayi story par CLAUDE.md wale command se: THINK line aur shabd-times pehle jaise print hon,
   `voice\<NN Title>.m4a` bane. Ek baar jaan-bujh kar galat THINK text do → turant saaf message aana chahiye.
4. **check_reel** ek CSV par jisme ek image ka naam galat ho → crash nahi, PROBLEM list aaye.
5. **prep_story** ek story par: list aur contact sheet pehle jaisi. Agar kisi story mein `SOFA`/`SAFE` jaisa prop hai to ab uska `_UP` banega – contact sheet mein dekh lo.
6. **REEL BANAO.bat** aur **VOICE BANAO.bat** double-click karke (VOICE mein sirf Enter dabao → credits check).
7. `py make_cover.py one "<reel naam>" "<story folder>\<reel naam> - COVER.png"` → cover purane jaisa.
