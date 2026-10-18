# theshivamiq – Reel banane ka format

User non-coder hai. Hinglish mein, seedha aur chhota jawab do. Kaam khud karo, commands mat samjhao.
Memory (`reels-story-folder-layout`, `folder-access-scope`, `user-profile`) zaroor padho – wahan latest decisions hain.

## Folders
- Code: `C:\Users\Hp\Desktop\theshivamiq code\` (scripts, `assets\`, `voice\`, `cases\`, `sfx\`, `music\`, `output\`)
- Stories: `C:\Users\Hp\Desktop\reels story\Category N\Story NN\` → `SCRIPT_*.txt`, `images\`, voice mp3
- Common: `reels story\Common\` → `bg music.mp3`, `CTA_HI.mp3`, `SIGNATURE_HI.mp3`, G_ images
- Sirf in 2 folders ko chhuo. Excel kabhi edit mat karo. Story folder mein sirf MP4 + `timing.csv` likho.
- Purani MP4 overwrite karne se pehle user se poocho (jab tak user ne khud redo na bola ho).

## Ek reel ke steps
**Ek command (naya):** `py make_full_reel.py "<story folder>" "<NN Title>"` neeche ke saare steps (2-9) khud chalata hai,
CSV `auto_csv.py` se DRAFT banti hai. Ruk jaaye to wajah padho, theek karo, wahi command dobara (`--from N`, `--dry-run`).
Details: `REEL_EK_COMMAND.txt`. Draft CSV ke baad bhi frame grid zaroor dekho.
1. **Padho:** `SCRIPT_*.txt` (voiceover, SCENE ORDER, ANSWER). Answer-reveal wala section ignore karo (answer reel nahi banti).
2. **Images:** `py prep_story.py "<story folder>"` — ye khud: PNG `assets\` mein copy (same naam par alag image → `<ID>_<CCSS>`, overwrite nahi), safed background → `<ID>_CUT`, neeche chipka prop → `<ID>_UP`, aur `output\Story NN CCSS - IMAGES.png` contact sheet (cream bg par). Aakhir mein "CSV mein ye naam lagao" list deta hai — CSV mein wahi naam use karo. Contact sheet ek baar dekho (andar ghira safed jaise chain ka loop nahi hatta).
   - Chaudi image (leti hui body, sofa, options card) ka size ab tweak nahi karna: make_reel khud screen ke kinaron se 40px andar fit karta hai (`EDGE_MARGIN`).
3. **Voice:** ElevenLabs wali voice hi use karo (free TTS user ne reject kiya). Final voice =
   story VO → CTA_HI → SIGNATURE_HI, silence kaat kar thodi tez (`tighten_voice.py`) → `voice\<NN Title>.m4a`.
   Nayi voice `eleven_voice.py` se banti hai (header padho). CTA/Signature kabhi dobara generate mat karo.
   **Asaan tareeka (soch-pause ke saath):** `py -u build_voice.py "<story folder>" "<NN Title>" "डिटेक्टिव शिवम" 3.0`
   (build_voice ab AAKHRI match leta hai, kyunki "pakad liya" wali line end mein hoti hai. Print hua THINK time us line se theek pehle hai, ye zaroor dekho.)
   → VO_MAIN + CTA + Signature jodta hai, tighten karta hai, "डिटेक्टिव शिवम ने… पकड़ लिया" se pehle 3 sec chup daalta hai,
   aur har shabd ka naya time print karta hai (CSV isi se likho). CTA ≈ "लिया" khatam + 0.1s, Signature ≈ CTA + 2.9s.
   **Kai chats ek saath:** `voice_queue.py` khud sambhalta hai — build_voice 4 alag slot (`work\voice_slotN`), ElevenLabs 3 slot;
   saare busy hon to "[queue] ... line mein wait" dikhega, script ko band mat karo, apne aap chalegi.
   Voice haath se kaatni/jodni ho to `$env:TEMP` ya code folder mein temp file KABHI mat banao (dusri chat ki voice bigadti hai) —
   `py voice_queue.py <ffmpeg command>` chalao aur temp file ka path `SLOTDIR\naam.wav` do; final file seedha `voice\` mein.
4. **Timing:** `VO_MAIN_timing.json` ho to wahi use karo, warna tighten_voice ki chunk table + Whisper (faster-whisper small).
5. **CSV:** `cases\<NN Title>.csv` likho (format neeche). Scene order script ke hisaab se.
6. **Cards:** `make_cards.py options C0NN_OPTIONS <ID>:Naam ...` aur `make_cards.py cover "<NN Title>" S16 "99% LOG FAIL!" "KILLER KAUN?"`
7. **Render:** `py make_reel.py "<NN Title>"`. Render se pehle `check_reel.py` apne aap chalta hai: text image ke upar, 3+ line text, text ki wajah se character chhota, khaali screen → PROBLEM aaye to render nahi hota, CSV theek karo (`--force` sirf jab user bole). "DHYAAN DO" wale (safed background / neeche kati image) dekh kar `_CUT`/`_UP` banao. Sirf CSV check: `py check_reel.py "<NN Title>"` (2-3 sec, CSV likhte hi chalao).
8. **Check:** render ke baad `output\<NN Title> - CHECK.png` (16 frames ki grid) apne aap banti hai — sirf wahi ek image dekho: galat pose, khaali screen, kati hui image.
9. **Copy:** MP4 + CSV (as `timing.csv`) story folder mein. Phir `py make_cover.py all` → naya "Case File" cover (logo + @theshivamiq) `<reel naam> - COVER.png` story folder mein. Sirf ek reel: `py make_cover.py one "<reel naam>" "<story folder>\<reel naam> - COVER.png"` (`all` purana cover nahi mitata, "- COVER NEW.png" bana deta hai). User ko MP4 bhejo. Memory update karo.

## Reel ka structure (har reel same)
- Hook (0–4s): bada yellow sawaal (KILLER KAUN? / CHOR KAUN? / GALTI PAKDO!) + VO ki line, image `nopop`.
- Crime scene (maut par `night` + `heartbeat`) → Shivam (S01, `whoosh`) → suspects `SUSPECT 1/4` yellow + naam + quote.
- **Shivam soch + stopwatch tick (HAR reel mein, user ne approve kiya):** "killer pakad liya" se theek pehle 3 sec ka pause
  (build_voice.py daalta hai). Us 3 sec mein S02 (soch pose) + `zoom+music_off` + sfx `tick_fast` + yellow "Shivam SOCH\nraha hai...".
  `music_off` sirf 1 sec music band karta hai, isliye +1s aur +2s par do khaali rows `music_off` wali aur daalo. Example:
  ```
  S02,30.81,33.81,center,55,Shivam SOCH\nraha hai...,zoom+music_off,tick_fast,yellow,
  ,31.81,32.81,,,,music_off,,,
  ,32.81,33.81,,,,music_off,,,
  ```
  Tick = `sfx\tick_fast.wav` (lagatar stopwatch, 3s, 1 sec mein 5 tick). Purana dheema `tick` (1 sec mein 1) user ne REJECT kiya — use mat karna.
- Shivam ka reaction (S06, `flash+music_off` + `whoosh`), "…killer pakad liya!" par `boom`.
- Clue line ("dhyaan se dekho") ke saath clue wali image.
- CTA: options card (1-2-3-4) ya S17 + sawaal, "Comment karo!" + yellow "Sahi answer kal pin hoga" (`ding`).
- End: S16 "Shivam ki nazar se\nkoi nahi bachta." `noout` + `whoosh`.

## Rules (user ne bataye)
- Captions HAMESHA Roman Hinglish, chahe script Devanagari mein ho.
- Answer kabhi screen par seedha mat likho (clue dikhao, jawab nahi).
- Text character ke upar na aaye (make_reel khud handle karta hai, phir bhi frame check karo). Text 2–3 line se lamba mat karo.
- Popup style (`STYLE` row: pop / rise / slide, sfx pop / pop2 / swish) – jo story par achha lage wo rakho, alag hona zaroori nahi.
- Music har reel mein hona chahiye (`music\bg music.mp3`, make_reel khud voice ke hisaab se level set karta hai + bolte waqt dabata hai). Render log mein "(music: ...)" dikhna chahiye.
- Transition: make_reel har naye scene par apne aap halka "camera punch" lagata hai (AUTO_PUNCH). Bade moment par `flash` bhi laga sakte ho.
- Baarish / barf effect sirf tab jab story mein important ho (jaise toofan wali raat), aur sirf usi line/scene par — poori reel mein kabhi nahi.
- Cover hamesha "99% LOG FAIL!" (script mein alag % likha ho tab bhi).
- Shivam poses: S01 khada, S02 soch, S03 ishara, S05 notepad, S06 handcuff, **S07 muskurana**, S08 chaunkna, S09 phone, S11 kaagaz padhna, S15 jeb mein haath, S16/S17 chehra close-up.

## Ye galtiyan pehle ho chuki hain – dobara mat karna
- **Music nahi sunai diya:** har render ke log mein "(music: bg music.mp3)" check karo. `music\` folder khaali ho to `reels story\Common\bg music.mp3` copy karo. Music ka level khud se kam mat karo.
- **Galat Shivam pose:** "muskuraye" par S08 (chaunkna) laga diya tha. Voice ki line ke mood se pose milao (list upar hai).
- **Bina maange effect:** baarish poori reel mein laga di thi, user ko nahi chahiye tha. Rain/snow sirf zaroori scene par, poori reel mein nahi.
- **Khaali screen:** effect ya image hatane ke baad koi hissa sirf text wala na reh jaaye. Pichhli image ko aage badha do.
- **Safed dabba:** kuch PNG ka background safed hota hai. Contact sheet mein check karke `_CUT` banao.
- **Image screen ke neeche kati hui:** prop ka neeche wala kinara image ke end se chipka ho to `_UP` version banao.
- **Text character ke upar:** caption 3 line se lamba ho to character chhota ho jaata hai. Lambi line ko do time-rows mein tod do.
- **Do chats ek saath:** dusri chat jo reel ya script badal rahi ho, use mat chhuo.
- **Free TTS voice:** user ne reject kiya hai. Sirf ElevenLabs.
- **Answer screen par:** jaise "Feb 2023: 28 din" ya "No Signal" script mein likha ho, tab bhi seedha jawab mat dikhao.
- Render ke baad frame check zaroor karo, aur user ko bhejne se pehle MP4 + `timing.csv` story folder mein daalo.

## CSV format
`asset_id,start,end,position,size,text,effect,sfx,color,focus`
- Pehli line: `STYLE,0,1,,,rise,,,,`
- Image row: asset_id + time + position (left/center/right) + size (% height). Text us row mein bhi de sakte ho.
- Sirf text row: asset_id khaali, `size` = font size. `\n` = nayi line. color: white / yellow / red.
- Same image lagatar do rows mein → dobara pop nahi hoti (text badal sakte ho).
- effect (`+` se jodo): nopop, noout, zoom, focus (focus column `x;y`, 0–1), night, music_off, rain, snow, flash, punch, bg.
- sfx: `sfx\` folder ke naam (pop, pop2, swish, whoosh, boom, ding, heartbeat, tick_fast, + ElevenLabs wale).

## Tokens bachao
- Ek chat mein ~5 reels, phir nayi chat.
- Frame check ek grid image mein karo, alag alag nahi.
- Dusri chat jo files badal rahi ho unhe ek saath mat chhuo.

## HyperFrames (naya style) – PAKKA ENGINE, dobara mat likhna
- Engine: `hyperframes\_ENGINE\shivam_engine.html` + `README.txt` (DATA format). Har nayi HF reel = ye file copy karo, sirf DATA bharo.
  Naya effect chahiye to engine mein optional field jodo (README update), naya engine kabhi mat likho.
- Sab Pe Shak series (Excel se auto): `sab_pe_shak\` → `make_reel.bat SS-001 1`, `make_all.bat`, `make_cover.bat SS-001 1`,
  settings `sab_pe_shak\settings.txt` (user khud badalta hai). Code = `sab_pe_shak\sps.py`.
