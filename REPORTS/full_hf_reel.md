# make_full_hf_reel.py – ek command mein HyperFrames reel

## Ye kya karta hai
Normal story (SCRIPT + images + ElevenLabs VO_MAIN) se **HyperFrames wali motion-graphics reel** ek command mein banata hai –
wahi `shivam_engine.html` (bilkul nahi badla), bas DATA khud bharta hai. Reel ka structure CLAUDE.md wala hi hai:
hook (KILLER/CHOR KAUN?) → Shivam S01 + "CASE FILE #.." → kahani → crime scene (maut: khoon + raat, chori: "CHORI!" stamp)
→ SUSPECT 1/N + naam patti (left/right se) → clue line par "DHYAAN DO!" → S02 soch + stopwatch + tick_fast (music band 3 sec)
→ S06 + "CASE SOLVED" + boom + shake → options card "1, 2 ya 3?" + ding + peeli pill "Sahi answer kal pin hoga"
→ S16 close-up + logo + @theshivamiq.

## Kaise chalana hai
```
py make_full_hf_reel.py "C:\Users\Hp\Desktop\reels story\Category 9\Story 10" "09-010 Til Gud ki Dopahar"
```
- `--dry-run` = sirf batao kya chalega
- `--from N` = step N se dobara (jaise DATA haath se badla → `--from 4`)
- `--tak 5` = render ke baad ruko, story folder mein kuch copy nahi (pehle reel dekh lo)
- `--haan` = sawaal mat poocho; `--force` = DATA check PROBLEM ke bawajood render (sirf user bole)

Pehle se chahiye: story mein `SCRIPT_*.txt`, `images\`, `VO_MAIN.mp3` + `VO_MAIN_timing.json`; laptop par Node.js + internet
(render ke waqt engine gsap CDN se leta hai).

## Steps (kaise kaam karta hai)
| # | Step | Kya hota hai |
|---|------|--------------|
| 1 | Images | `prep_story.py` (same as purana) – `_CUT` / `_UP` naam yaad rakhta hai |
| 2 | Voice | `build_voice.py ... "डिटेक्टिव शिवम" 3.0`. **make_full_reel ne voice pehle bana di ho to wahi use** (skip). Nayi chahiye: `--from 2` |
| 3 | HF DATA | `auto_csv.build()` se reel ka structure + shabd ka time → `hyperframes\<naam>\hf_data.json` (DRAFT) + `timing.csv` |
| 4 | Project | DATA check → options card (`make_cards.py options`) → engine copy = `index.html`, images trim karke `assets\`, BG_MAIN, logo, font (ariblk), `mix.wav` |
| 5 | Render | `npx --yes hyperframes@0.8.144 render --fps 30 --quality high` → `output\<naam> - HF.mp4` + `output\<naam> - HF CHECK.png` (16 frame grid) |
| 6 | Copy | MP4 → `story\<naam>.mp4` + `timing.csv`. **Story mein pehle se koi MP4 ho to poochta hai** (render se pehle hi) |
| 7 | Cover | `make_cover.py one` → `<naam> - COVER.png` (purana ho to `- COVER NEW.png`, mitata nahi) |

Kahan tak pahunche: `cases\<naam>.hf.state.json`. Ruk jaaye to "!! RUK GAYA:" ke baad wajah – theek karo, wahi command dobara.

### DATA mein motion (Training Khatam jaisa)
- **Har ~3 sec visual change:** scene badalna, header graphics, aur lamba scene ho to beech mein **1.12x punch** (engine ka `punch`),
  bolte shabd par snap. Check: kahin bhi 3.5 sec se zyada bina change nahi (sample par max 3.4 sec).
- Har naye scene par camera punch (1.06), image halka float, background dheere zoom (engine ke apne).
- **Shabd-shabd caption:** Roman (CAPTION section se), ek tukda 1–6 shabd / max 2 line, bolta shabd peela (`activeWord #FFE600`).
  Naam CAPS = peela dabba; suspect ke bayan ke andar kabhi CAPS nahi. CTA + signature ke captions bhi (time andaze se, kyunki
  build_voice inka shabd-time nahi deta).
- **Safe zone:** header 290–490px, caption 490–790px, naam patti / CTA pill 1400px se – sab upar 15% (288px) aur neeche 20%
  (1536px) ke beech. Khade character h 1000 bottom 140, close-up h 1130, prop / leta hua chauda (HOOK_REEL_GUIDE ke naap).
- **Music:** `music\bg music.mp3`, voice se **-14 dB** (chup mein), **-16 dB** jab bol rahe (ducking), soch 3 sec + S06 1 sec band,
  shuru fade-in, end fade-out. Log mein `(music: bg music.mp3, -14/-16 dB, N sfx)` dikhta hai.
- **SFX sync:** CSV draft wale time par – whoosh (S01/S06/S16), heartbeat (crime), swish (suspects), tick_fast (soch), boom
  (pakad liya), ding (options). `sfx\` mein na mile to batata hai, uske bina mix banata hai. Purana `tick` kabhi nahi.

### Render se pehle DATA check (PROBLEM = render nahi)
Devanagari screen par, ANSWER ka number / quote screen par, khaali screen (koi image nahi), galat time, caption END ke baad,
safe zone ke bahar CFG, purana `tick`. DHYAAN (sirf warning): 3.5 sec+ bina change, clue par zoom, 2 line se lamba caption.

## Purane make_full_reel se kya alag
| | make_full_reel.py | make_full_hf_reel.py |
|---|---|---|
| Engine | make_reel.py (Python/ffmpeg) | HyperFrames `shivam_engine.html` (Chrome + GSAP) |
| Draft | `cases\<naam>.csv` | `hyperframes\<naam>\hf_data.json` (+ timing.csv). **cases\ ki CSV nahi chhoota** |
| Text | 2–3 line caption rows | shabd-shabd peele caption + engine graphics (stamps, badges, stopwatch, khoon) |
| Check | check_reel.py | DATA check (upar) |
| MP4 | `output\<naam>.mp4` | `output\<naam> - HF.mp4` (purana output nahi mitta) |
| Voice | build_voice | same – pehle se bani ho to dobara nahi |
Dono ek hi story folder mein `<naam>.mp4` daalte hain, isliye doosra chalao to overwrite se pehle poochega.
make_full_reel.py, auto_csv.py, sps.py, engine – kisi ka behaviour nahi badla (sirf auto_csv ke functions import kiye).

## Render ka andaaza time
- Cloud (4 core, software GPU): 44.6 sec ki mock reel = **2 min** render.
- Laptop: sps.py jaisa andaaza **~1–1.5 min har 10 sec video** → 45 sec reel ≈ **5–7 min** (HOOK_REEL_GUIDE: ~6 min).
  Baaki steps (images, voice, DATA, mix) < 1 min.

## Cloud par kya test hua
- `py -m pytest tests` → **158 pass** (137 purane + 21 naye `tests/test_full_hf_reel.py`): samples/09-010 + chori wali nakli story,
  structure, captions (Roman, 2 line, answer "hawa" nahi), CAPS bayan mein nahi, 3.5 sec rule, safe zone, answer/Devanagari/khaali
  screen pakadna, engine code same rehna + `node --check`, music ducking (-2 dB bolte waqt) + soch par music band (asli ffmpeg),
  poori pipeline nakli scripts ke saath (dry-run, --tak, --from, purani MP4 par sawaal, haath wala DATA bachna, haath wala HF
  project na chhedna, voice reuse, render fail, missing image).
- **Mock render:** nakli rang-birangi images + tone awaaz se poora project bana aur `hyperframes render` se 44.6 sec MP4
  (video + audio) bani. Frame grid mein hook, case chip, crime scene, suspect badge + naam, stopwatch, options, CTA pill,
  brand – sab sahi jagah, safe zone ke andar.
  Note: cloud ka Chrome CDN (gsap) tak nahi pahunchta, isliye **sirf mock copy** mein gsap local rakha – engine nahi badla.

## Laptop par kya test karna hai
1. `py make_full_hf_reel.py "<Story 10 folder>" "09-010 Til Gud ki Dopahar" --dry-run` – steps theek dikhen.
2. Bina `--dry-run`, `--tak 5` ke saath chalao → `output\... - HF.mp4` + `HF CHECK.png` dekho:
   pose sahi, image kati nahi, text character ke chehre par nahi, options card + "Sahi answer kal pin hoga" pill aapas mein na takraayein,
   asli options card ka size (step 3 par andaze se hota hai), music sunai de (ducking theek lage), tick_fast + boom time par.
3. Theek lage to `--from 6` → story folder mein MP4 + timing.csv + cover.
4. Kuch badalna ho: `hyperframes\<naam>\hf_data.json` mein (SCENES / P / T / CFG – README.txt format), phir `--from 4`.

## Engine ke liye sujhaav (khud nahi joda – user/brain decide kare)
- **gsap local fallback** (optional): engine `<script src=cdn>` par chalta hai; internet na ho to render fail. Ek optional
  `assets/gsap.min.js` fallback se offline render ho sakta hai.
- **CFG.tapeTop** (optional): crime scene ki doosri tape 1690px par hai (neeche 20% zone mein). Abhi engine ka fixed hai.
- **Options card ka asli size**: step 3 par card bana nahi hota, size andaze (1080x780) se – mismatch ho to step 4 mein
  dobara naap sakte hain (abhi nahi kiya, DATA haath se badalna safe rahe).
