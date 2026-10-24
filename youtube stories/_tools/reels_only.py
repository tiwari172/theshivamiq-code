# Long-video wali Excel ko "sirf reels" Excel mein badalta hai.
# python reels_only.py "<build_batch se bani xlsx (SHORTS = 10)>" "<out xlsx>"
import re, sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1])
for n in ("Script + Timing", "MOTION PLAN"): del wb[n]

def keep_rows(ws, ok):
    for i in range(ws.max_row, 1, -1):
        if not ok([c.value for c in ws[i]]): ws.delete_rows(i)

def sub(ws, pairs):
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str):
                v = c.value
                for a, b in pairs: v = re.sub(a, b, v)
                c.value = v

# Reel motion plan: case background ki jagah plain dark bg (nayi image nahi)
sm = wb["SHORTS MOTION PLAN"]
used = set()
for row in sm.iter_rows(min_row=2):
    a = row[7]
    if isinstance(a.value, str) and a.value.startswith("BG_"): a.value = "- (plain dark bg, image nahi)"
    if isinstance(a.value, str):
        used |= {x.strip() for x in re.split(r"\s*(?:\.\.\.|,|\+)\s*", a.value)}
sub(sm, [(r"^bg drift left->right$", "static")])

ws = wb["Shorts + Reels"]
sub(ws, [(r"^Short (\d+)$", r"Reel \1"), (r"short wala", "reel wala"), (r"Jawab short mein", "Jawab reel mein")])
ws.cell(1, 1).value = "Reel"
sub(sm, [(r"^Short$", "Reel")])

ip = wb["Image Prompts"]
keep_rows(ip, lambda r: r[0] in used)
new = [r[0].value for r in ip.iter_rows(min_row=2) if r[0].value and "PEHLE SE HAI" not in str(r[4].value)]
old = ip.max_row - 1 - len(new)

pj = wb["Pinned + Jawab"]
keep_rows(pj, lambda r: r[0] != "LONG VIDEO")
sub(pj, [(r"^Agle hafte ki video \(jawab\)$", "Reel ke agle din"), (r"\nPoori explanation \+ winners: YouTube full video \(link bio mein\)", ""),
         (r"\(reveal ke BAAD shorts/reels par\)", "(agle din reel par pin karo)")])
pj.cell(1, 3).value = "Jawab VO (chaho to agli reel ki shuruaat mein)"

up = wb["Upload Details"]
keep_rows(up, lambda r: not str(r[0]).startswith("YouTube Long") and r[1] != "Related video")
sub(up, [(r"YouTube Short (\d+)", r"YouTube Short \1"), (r"Kaatil kaun\? Baaki suspects \+ POINTS sirf full video mein 👉 \[long video link\]", "Kaatil kaun? Comment karo, sahi jawab kal pin hoga 👇"),
         (r"Baaki suspects \+ POINTS wala muqabla YouTube full video mein \(link bio mein\)", "Sahi jawab kal pin hoga 📌"),
         (r"Kaatil ka naam comment karo! Jawab agle Sunday\. Points wala muqabla YouTube full video par \(link bio mein\)\.", "Kaatil ka naam comment karo! Sahi jawab kal pin hoga."),
         (r"Kaatil kaun\? Jawab agle Sunday\. POINTS sirf full video ke comments par 👉 \[long video link\]", "Kaatil kaun? Naam comment karo! Sahi jawab kal pin hoga."),
         (r"Reel share karo \+ YouTube link sticker: 'Full case \+ points yahan'", "Reel share karo + Quiz sticker: 'Kaatil kaun?' (5 suspect ke naam)"),
         (r"^Sunday: long video.*$", "Roz 1 reel (A-021 se A-030, 10 din). Har din: nayi reel + pichhli reel par jawab wala comment pin. Insta + YouTube Shorts dono par same reel.")])

cd = wb["Cover Design"]
keep_rows(cd, lambda r: str(r[0]).startswith("Short/Reel"))

sh = wb["Start Here"]
S = {
 "Ye kya hai": "Batch 3 ki SIRF 10 REELS (9:16) ki production file – A-021 se A-030, har case ki ek reel. Long video nahi banega.",
 "Video": "10 reels, har ek ~60 sec. Har reel mein 5 suspect (kaatil + galat-ishara wala hamesha).",
 "Sheets": "Shorts + Reels (reel ka VO + scene order) | SHORTS MOTION PLAN (9:16 sec-by-sec) | MOTION CODES | Image Prompts | Shivam Poses | SFX + Motion | Pinned + Jawab | Upload Details | Cover Design | Answer Key (sirf aapke liye)",
 "Voice": "Shorts + Reels sheet ka aakhri column 'Reel VO FINAL' ElevenLabs mein ek baar mein (Rudra). CTA/Signature purane hi.",
 "Timing": "Start/End abhi ANDAAZA hai. Voice banne ke baad build_voice se asli time aayega.",
 "Size": "Sirf 9:16 (1080x1920). Case background nahi chahiye – plain dark bg.",
 "Jawab": "Jawab reel mein KABHI nahi. Agle din usi reel par pinned comment (Pinned + Jawab sheet ka aakhri column).",
 "Comment format": "Comment mein sirf kaatil ka naam (jaise 'Naresh').",
 "PRIMARY": "Is batch mein sirf reels (Insta + YouTube Shorts dono par same).",
 "Shorts niyam": "10 reel, har case ki ek. Har reel mein 5 suspect – kaatil + galat-ishara wala hamesha. Baaki suspect wo liye jinki image pehle se hai. Jawab reel mein KABHI nahi.",
 "Folders": "youtube stories\\batch 3\\ : Excel + 'YouTube Reels Story'\\R1..R10 (har reel ka VO, csv, images, cover).",
 "Reel VO niyam": "Reel VO poori story EK BAAR mein (Rudra, eleven_v4, stability 0.45, speed 1.05 + purana tighten). EMOTION TAG KAM SE KAM: sirf hook par [whispers], baaki saadi line – suspect ke bayaan par koi tag nahi (killer alag na lage). VO mein NAHI: 'bole/boli', motive line, galat-ishara line, saboot ka naam, 'full video/link bio'. End: 3 sec chup -> PAKAD_LIYA_HI + CTA_HI + SIGNATURE_HI (purani files, dobara nahi banti).",
 "Images": f"Image Prompts sheet: HARA = purani image (nayi mat banao) – {old} purani. Sirf {len(new)} nayi banani hain: {', '.join(new)}.",
}
drop = {"Script chat ke liye", "Motion"}
for i in range(sh.max_row, 1, -1):
    k = sh.cell(i, 1).value
    if k in drop: sh.delete_rows(i)
    elif k in S: sh.cell(i, 2).value = S[k]
sub(sh, [(r"MOTION PLAN \+ ", "")])
wb.save(sys.argv[2])
print("purani", old, "| nayi", len(new), new)
