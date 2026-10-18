# theshivamiq – SCRIPT + voice timing se cases\<NN Title>.csv ka DRAFT
#
#   py auto_csv.py "<story folder>" "<NN Title>"
#   py auto_csv.py "<story folder>" "<NN Title>" --times "cases\<NN Title>.voice_times.txt"
#   py auto_csv.py ... --names "cases\<NN Title>.prep.txt"   (prep_story ka print, "CSV mein ye naam lagao")
#   py auto_csv.py ... --print        (sirf dikhao, file mat likho)
#   py auto_csv.py ... --style pop    (STYLE row: pop / rise / slide, default rise)
#
# Timing kahan se:
#   --times   = build_voice.py ka print (har shabd "start end shabd" + "THINK pause a -> b" + "total")  <- SAHI
#   warna     = story ka VO_MAIN_timing.json, aur tighten + soch-pause ka ANDAZA (sirf draft, voice ke baad dobara banao)
#
# Structure CLAUDE.md "Reel ka structure" wala: hook (nopop, KILLER KAUN?) -> S01 clue -> kahani -> crime (night+heartbeat)
#   -> SUSPECT 1/N -> clue line -> S02 soch (tick_fast + 2 music_off rows) -> S06 (flash+music_off, whoosh) + boom
#   -> options card (ding) + "Sahi answer kal pin hoga" -> S16 noout end.
# Captions SCRIPT ke CAPTION (Roman) section se. ANSWER section kabhi screen par nahi jaata.

import csv, difflib, io, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(BASE, "cases")

THINK_TEXT = "डिटेक्टिव शिवम"
THINK = 3.0
LINE_CHARS = 20          # ek caption line mein itne akshar (Arial Black 72 ~ 940px)
MAX_LINES = 2            # ek row mein itni line (3 sirf "Clue isi video" wali fixed line mein)
MIN_ROW = 0.5            # isse chhoti row pichhli mein mila do
CTA_GAP, CTA_LEN, SIG_LEN = 0.1, 2.9, 2.7      # CTA = "लिया" + 0.1s, Signature = CTA + 2.9s

# tighten_voice.py jaisa andaza (sirf JSON fallback ke liye)
GAP, MIN_SILENCE, PAD, SPEED = 0.28, 0.30, 0.06, 1.07

SIZES = {"prop": 30, "victim": 40, "person": 45, "shivam": 55, "end": 60, "options": 38}
DEATH_HI = r"मरा|मरी|मरे|मृत|लाश|हत्या|क़त्ल|कत्ल|ख़ून|खून|मौत|मार दिया|ज़हर|जहर"
DEATH_RO = r"\b(mara|mari|maut|laash|lash|hatya|khoon|qatl|murder|dead|zeher|zahar)\b"
THEFT_HI = r"गायब|ग़ायब|चोरी|चुरा|चोर"
THEFT_RO = r"\b(gayab|ghayab|chori|chura\w*|chor)\b"
SAY_HI = r"बोला|बोली|बोले|ने कहा|कहता|कहती"
SAY_RO = r"\b(bolaa|bola|bolee|boli|bole|ne kaha|kehta|kehti)\b"
STRESS_HI = r"लेकिन|मगर|ध्यान|सिर्फ़|सिर्फ|तक नहीं"
SHIVAM = re.compile(r"^S\d{2}$", re.I)
TAG = re.compile(r"\[[^\]]*\]")


# ---------------- SCRIPT padhna ----------------
def sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^=+\s*(.+?)\s*=+\s*$", line.strip())
        if m:
            cur = m.group(1).split("(")[0].strip().upper()
            out[cur] = []
        elif cur:
            out[cur].append(line.rstrip())
    return out


def find_script(story):
    for f in sorted(os.listdir(story)):
        if f.upper().startswith("SCRIPT_") and f.lower().endswith(".txt"):
            return os.path.join(story, f)
    sys.exit(f"SCRIPT_*.txt nahi mila: {story}")


def is_pause(line):
    return re.fullmatch(r"[.\s…]*", TAG.sub("", line)) is not None


def script_lines(path):
    """[(devanagari, roman), ...] VO line + uska Roman caption, aur scene order / answer"""
    with open(path, encoding="utf-8-sig") as f:
        sec = sections(f.read())
    vo = [l.strip() for l in sec.get("VOICEOVER", []) if l.strip()]
    if not vo:
        sys.exit(f"SCRIPT mein VOICEOVER section nahi mila: {path}")
    cap = [l.strip() for l in sec.get("CAPTION", []) if l.strip() and not is_pause(l)]
    real = [l for l in vo if not is_pause(l)]
    notes = []
    if len(cap) != len(real):
        notes.append(f"CAPTION ki {len(cap)} line, VOICEOVER ki {len(real)} line - Roman caption apne aap "
                     f"(transliterate) bani, CSV mein padh kar theek karo")
        cap = [roman(l) for l in real]
    it = iter(cap)
    pairs = [(l, "" if is_pause(l) else next(it)) for l in vo]
    order = " ".join(sec.get("SCENE ORDER", []))
    scene = [a.strip() for a in re.split(r"→|->|,|\s+", order) if re.fullmatch(r"[A-Za-z0-9_]+", a.strip() or "-")]
    answer = " ".join(sec.get("ANSWER", []))
    return pairs, scene, answer, notes


# ---------------- Devanagari -> Roman (sirf jab CAPTION section na ho) ----------------
_C = dict(zip("कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह",
              "k kh g gh n ch chh j jh n t th d dh n t th d dh n p ph b bh m y r l v sh sh s h".split()))
_C.update({"क़": "q", "ख़": "kh", "ग़": "g", "ज़": "z", "फ़": "f", "ड़": "d", "ढ़": "dh", "ऱ": "r"})
_V = dict(zip("अआइईउऊऋएऐओऔ", "a aa i ee u oo ri e ai o au".split()))
_M = dict(zip("ािीुूृेैोौ", "aa i ee u oo ri e ai o au".split()))


_WORDS = {"में": "mein", "मैं": "main", "है": "hai", "हैं": "hain", "नहीं": "nahi", "और": "aur", "कि": "ki",
          "हम": "hum", "तुम": "tum", "यह": "yeh", "वह": "woh", "क्या": "kya", "भी": "bhi", "ही": "hi"}


def roman(text):
    """seedha andaza (Hinglish jaisa): mein, tha, thi ... CSV mein padh kar theek karna"""
    text = TAG.sub("", text).replace("।", ".").replace("ॉ", "ो").replace("ऑ", "ओ")
    out = []
    for word in re.split(r"(\s+)", text):
        core = word.strip("\"'.,!?…")
        if core in _WORDS:
            out.append(word.replace(core, _WORDS[core]))
            continue
        s, i = "", 0
        chars = list(word)
        while i < len(chars):
            ch = chars[i]
            if i + 1 < len(chars) and chars[i + 1] == "़" and ch + "़" in _C:
                ch, i = ch + "़", i + 1
            if ch in _C:
                s += _C[ch]
                nxt = chars[i + 1] if i + 1 < len(chars) else ""
                if nxt == "्":
                    i += 1
                elif nxt in _M:
                    s += _M[nxt]
                    i += 1
                elif nxt and (nxt in _C or nxt in "ंँ" or nxt in _V):
                    s += "a"
                elif i + 1 < len(chars) and nxt not in "ंँः":
                    pass
            elif ch in _V:
                s += _V[ch]
            elif ch in "ंँ":
                s += "n"
            elif ch != "ः":
                s += ch
            i += 1
        s = re.sub(r"(?<=[a-z])aa(?=[\"'.,!?…]*$)", "a", s)      # tha, raha, gaya
        s = re.sub(r"(?<=[a-z])ee(?=[\"'.,!?…]*$)", "i", s)      # thi, rahi
        s = re.sub(r"(?<=[a-z])oo(?=[\"'.,!?…]*$)", "u", s)      # Golu
        out.append(s)
    r = "".join(out).strip()
    return r[:1].upper() + r[1:]


# ---------------- timing ----------------
def vo_tokens(text):
    """build_voice.py jaisa: [^\\s]+ , sirf [tag] wale chhodo, tag hatao"""
    toks = []
    for m in re.finditer(r"[^\s]+", text):
        w = m.group()
        if re.fullmatch(r"\[[^\]]*\]", w):
            continue
        toks.append((TAG.sub("", w), m.start()))
    return toks


def parse_build_voice(out):
    words, think, chunks, total = [], None, None, None
    for line in out.splitlines():
        m = re.match(r"^\s*(-?[\d.]+)\s+(-?[\d.]+)\s+(\S+)\s*$", line)
        if m:
            words.append((float(m.group(1)), float(m.group(2)), m.group(3)))
            continue
        m = re.search(r"THINK pause ([\d.]+) -> ([\d.]+)", line)
        if m:
            think = (float(m.group(1)), float(m.group(2)))
        m = re.search(r"last chunks start: ([\d.]+) ([\d.]+).*total ([\d.]+)", line)
        if m:
            chunks, total = (float(m.group(1)), float(m.group(2))), float(m.group(3))
    if not words:
        sys.exit("build_voice ke print mein shabdon ka time nahi mila.")
    return {"words": words, "think": think, "chunks": chunks, "total": total, "estimated": False}


def estimate_from_json(path, think_before=THINK_TEXT, think=THINK):
    """VO_MAIN_timing.json + tighten_voice jaisa andaza (pause chhote, 7% tez) + soch pause"""
    with open(path, encoding="utf8") as f:
        j = json.load(f)
    text = "".join(j["characters"])
    st, en = j["character_start_times_seconds"], j["character_end_times_seconds"]
    raw = []
    for m in re.finditer(r"[^\s]+", text):
        if re.fullmatch(r"\[[^\]]*\]", m.group()):
            continue
        raw.append([TAG.sub("", m.group()), st[m.start()], en[m.end() - 1], m.start()])
    chunks = []
    for w in raw:
        if chunks and w[1] - chunks[-1][1] < MIN_SILENCE:
            chunks[-1][1] = w[2]
        else:
            chunks.append([w[1], w[2]])
    table, t = [], 0.0
    for a, b in chunks:
        a, b = max(0.0, a - PAD), b + PAD
        table.append((a, b, t / SPEED, (t + b - a) / SPEED))
        t += b - a + GAP

    def remap(x):
        for a, b, na, nb in table:
            if a - 0.05 <= x <= b + 0.05:
                return na + (min(max(x, a), b) - a) * (nb - na) / max(b - a, 1e-6)
        prev = [r for r in table if r[1] < x]
        return prev[-1][3] if prev else 0.0

    words = [[remap(s), remap(e), w, p] for w, s, e, p in raw]
    th = None
    pos = text.rfind(think_before) if think_before else -1
    if pos >= 0:
        first = [w for w in words if w[3] >= pos][0]
        prev = [w for w in words if w[3] < pos][-1]
        shift = (prev[1] + first[0]) / 2
        for w in words:
            if w[0] >= shift:
                w[0] += think
                w[1] += think
        th = (shift, shift + think)
    return {"words": [(s, e, w) for s, e, w, _ in words], "think": th, "chunks": None, "total": None,
            "estimated": True}


def norm(w):
    return re.sub(r"[\"'“”‘’.,!?।…\-–—:;()]", "", w)


def align(pairs, timing):
    """har VO line ke har shabd ko build_voice wala time do -> [[(s, e, deva), ...] per line]"""
    toks, owner = [], []
    for i, (deva, _) in enumerate(pairs):
        for w, _ in vo_tokens(deva):
            toks.append(w)
            owner.append(i)
    printed = [w for _, _, w in timing["words"]]
    sm = difflib.SequenceMatcher(None, [norm(t) for t in toks], [norm(p) for p in printed], autojunk=False)
    idx = [None] * len(toks)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            idx[a + k] = b + k
    tw = timing["words"]
    times = [None] * len(toks)
    for k, j in enumerate(idx):
        if j is not None:
            times[k] = tw[j][:2]
    for k in range(len(times)):          # na mile shabd: padosi se bharo
        if times[k] is None:
            prev = next((times[q] for q in range(k - 1, -1, -1) if times[q]), None)
            nxt = next((times[q] for q in range(k + 1, len(times)) if times[q]), None)
            if prev and nxt:
                times[k] = (prev[1], max(prev[1], nxt[0]))
            elif prev:
                times[k] = (prev[1], prev[1])
    lines = [[] for _ in pairs]
    for k, t in enumerate(times):
        if t:
            lines[owner[k]].append((t[0], t[1], toks[k]))
    missing = [owner[k] for k, j in enumerate(idx) if j is None]
    return lines, missing


# ---------------- caption ko rows mein todna ----------------
def ends_phrase(w):
    return bool(re.search(r"([,.?!।…]|\.\.\.)[\"'”]*$", w))


def phrases(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if ends_phrase(w):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def wrap(words, width=LINE_CHARS):
    """kam se kam line, aur lines barabar lambi (greedy jaisa aakhri line mein ek shabd na latke)"""
    greedy = [""]
    for w in words:
        if greedy[-1] and len(greedy[-1]) + 1 + len(w) > width:
            greedy.append(w)
        else:
            greedy[-1] = (greedy[-1] + " " + w).strip()
    if len(greedy) != 2:
        return greedy
    best = min(range(1, len(words)), key=lambda k: max(len(" ".join(words[:k])), len(" ".join(words[k:]))))
    a, b = " ".join(words[:best]), " ".join(words[best:])
    return [a, b] if max(len(a), len(b)) <= width else greedy


def roman_times(roman_words, vo_words):
    """har Roman shabd ka start time (phrase milte hon to phrase-wise, warna akshar ke hisaab se)"""
    if not vo_words:
        return [0.0] * len(roman_words)
    rp, vp = phrases(roman_words), phrases([w for _, _, w in vo_words])
    groups = []
    if len(rp) == len(vp):
        k = 0
        for r, v in zip(rp, vp):
            groups.append((r, vo_words[k:k + len(v)]))
            k += len(v)
    else:
        groups.append((roman_words, vo_words))
    starts = []
    for r, v in groups:
        a, b = v[0][0], v[-1][1]
        total = sum(len(w) + 1 for w in r) or 1
        c = 0
        for w in r:
            starts.append(a + (b - a) * c / total)
            c += len(w) + 1
    return starts


def caption_rows(roman_text, vo_words, start, end, caps=()):
    """Roman line -> [(start, end, text)] har row max 2 line"""
    words = [w for w in roman_text.split() if w]
    for c in caps:
        words = [re.sub(rf"(?i)\b{re.escape(c)}\b", c.upper(), w) for w in words]
    if not words:
        return []
    st = roman_times(words, vo_words)
    rows, cur, cur_st = [], [], None
    for ph in _phrase_idx(words):
        for idx_group in _fit(ph, words):     # har phrase (, . ? ! ...) apni row; chhoti row baad mein judti hai
            if cur:
                rows.append((cur_st, cur))
            cur, cur_st = list(idx_group), st[idx_group[0]]
    if cur:
        rows.append((cur_st, cur))
    out = []
    for n, (s, idx) in enumerate(rows):
        s = start if n == 0 else s
        e = rows[n + 1][0] if n + 1 < len(rows) else end
        out.append([s, e, "\\n".join(wrap([words[i] for i in idx]))])
    merged = []                          # bahut chhoti row -> pichhli mein (agar 2 line mein aaye)
    for r in out:
        if merged and r[1] - r[0] < MIN_ROW:
            joined = wrap((merged[-1][2].replace("\\n", " ") + " " + r[2].replace("\\n", " ")).split())
            if len(joined) <= MAX_LINES:
                merged[-1] = [merged[-1][0], r[1], "\\n".join(joined)]
                continue
        merged.append(r)
    return merged


def _phrase_idx(words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if ends_phrase(w):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def _fit(idx, words):
    """ek phrase 2 line se lamba ho to barabar tukdon mein todo (kam se kam tukde)"""
    fits = lambda part: len(wrap([words[i] for i in part])) <= MAX_LINES
    if fits(idx):
        return [idx]
    for k in range(2, len(idx) + 1):
        size = sum(len(words[i]) + 1 for i in idx) / k
        parts, cur, c = [], [], 0
        for i in idx:
            if cur and c + (len(words[i]) + 1) / 2 > size * (len(parts) + 1) and len(parts) < k - 1:
                parts.append(cur)
                cur = []
            cur.append(i)
            c += len(words[i]) + 1
        parts.append(cur)
        if all(fits(p) for p in parts):
            return parts
    return [[i] for i in idx]


# ---------------- images ----------------
def parse_prep_names(out):
    """prep_story.py ka 'CSV mein ye naam lagao' hissa -> {story naam: CSV naam}"""
    names, on = {}, False
    for line in out.splitlines():
        if "CSV mein ye naam lagao" in line:
            on = True
            continue
        if on:
            if not line.strip() or line.strip().startswith("Contact sheet"):
                if names:
                    break
                continue
            m = re.match(r"^\s*(\S+)\s*->\s*(\S+)\s*$", line) or re.match(r"^\s*(\S+)\s*$", line)
            if m:
                names[m.group(1)] = m.group(m.lastindex)
    return names


def guess_names(story):
    """prep_story ka print na ho: images\\ ke naam, assets\\ mein _CUT/_UP bana ho to wo"""
    names, assets = {}, os.path.join(BASE, "assets")
    img = os.path.join(story, "images")
    for f in sorted(os.listdir(img)) if os.path.isdir(img) else []:
        if f.lower().endswith(".png"):
            a = os.path.splitext(f)[0]
            use = a
            for v in (a + "_CUT_UP", a + "_CUT", a + "_UP"):
                if os.path.exists(os.path.join(assets, v + ".png")):
                    use = v
                    break
            names[a] = use
    return names


def kind(asset):
    a = asset.upper()
    return "shivam" if SHIVAM.match(a) else "prop" if a.startswith("P_") else "person"


def label(asset):
    """C005_VICKY -> VICKY, G_M_ARCHER_A -> ARCHER A"""
    a = re.sub(r"_(CUT|UP|\d{4})$", "", asset.upper())
    a = re.sub(r"_(CUT|UP|\d{4})$", "", a)
    parts = [p for p in a.split("_") if not re.fullmatch(r"[A-Z]?\d+|[A-Z]|G|P|C|H", p)]
    return " ".join(parts) or asset


def case_tag(name, story=""):
    m = re.match(r"[A-Z]?(\d{2})-(\d{3})", name)
    if m:
        return f"{int(m.group(1))}{int(m.group(2)):02d}"
    cat, num = re.search(r"Category (\d+)", story), re.search(r"Story (\d+)", story)
    return f"{int(cat.group(1))}{int(num.group(1)):02d}" if cat and num else "NEW"


# ---------------- main draft ----------------
def build(story, name, timing, names=None, style="rise"):
    """-> (csv rows list, info dict)"""
    pairs, scene, answer, notes = script_lines(find_script(story))
    names = names or {}
    use = lambda a: names.get(a, a)
    lines, missing = align(pairs, timing)
    pakad_guess = max((i for i, (d, r) in enumerate(pairs) if "पकड़" in d or "pakad" in r.lower()), default=len(pairs))
    missing = sum(1 for o in missing if o <= pakad_guess)     # CTA / signature VO_MAIN mein hote hi nahi
    if missing:
        notes.append(f"{missing} shabd voice timing se match nahi hue (andaza lagaya)")
    if timing.get("estimated"):
        notes.append("timing VO_MAIN_timing.json ka ANDAZA hai (build_voice ke baad dobara banao)")

    # line roles
    real = [i for i, (d, r) in enumerate(pairs) if not is_pause(d)]
    pakad = next((i for i in reversed(real) if "पकड़" in pairs[i][0] or "pakad" in pairs[i][1].lower()), None)
    if pakad is None:
        sys.exit('SCRIPT mein "...pakad liya" wali line nahi mili.')
    story_lines = [i for i in real if i < pakad]
    clue = next((i for i in story_lines[:4] if "क्लू" in pairs[i][0] or "clue" in pairs[i][1].lower()), None)
    suspects = [i for i in story_lines if '"' in pairs[i][0] + pairs[i][1] and
                (re.search(SAY_HI, pairs[i][0]) or re.search(SAY_RO, pairs[i][1], re.I))]
    hook_lines = [i for i in story_lines if i < clue] if clue is not None else story_lines[:1]
    if not hook_lines:                     # pehli line hi "clue isi video mein" -> wahi hook
        hook_lines, clue = [clue], None
        notes.append("hook line nahi mili (pehli line clue wali hai) - S01 nahi laga, CSV mein dekh lo")
    after_clue = [i for i in story_lines if i not in hook_lines and i != clue]
    first_sus = suspects[0] if suspects else pakad
    crime_re = lambda i, hi, ro: re.search(hi, pairs[i][0]) or re.search(ro, pairs[i][1], re.I)
    crime = next((i for i in after_clue if i < first_sus and crime_re(i, DEATH_HI + "|" + THEFT_HI,
                                                                     DEATH_RO + "|" + THEFT_RO)), None)
    if crime is None:
        before = [i for i in after_clue if i < first_sus]
        crime = before[-1] if before else None
        notes.append("crime (maut / chori) wali line nahi pehchani - suspects se pehle wali line li")
    death = bool(crime is not None and crime_re(crime, DEATH_HI, DEATH_RO))
    pk_d, pk_r = pairs[pakad]
    if re.search(r"चोर", pk_d) or re.search(r"\bchor\b", pk_r, re.I):
        who = "CHOR"
    elif death or re.search(r"कातिल|क़ातिल|हत्यारा|किलर", pk_d) or re.search(r"\b(kaatil|katil|killer)\b", pk_r, re.I):
        who = "KILLER"
    else:                                  # "galti pakad li" jaisi: kahani mein chori ho to CHOR
        who = "CHOR" if re.search(THEFT_HI, " ".join(d for d, _ in pairs)) else "KILLER"
    hook_q = f"{who} KAUN?"

    # suspects ke naam + image
    people = [a for a in scene if kind(a) != "shivam"]
    sus_names = []
    for i in suspects:
        m = re.match(rf"^(.+?)\s+{SAY_RO}", pairs[i][1], re.I)
        sus_names.append(m.group(1).strip(" .,…").split()[-1] if m else f"SUSPECT {len(sus_names) + 1}")
    flat = lambda x: re.sub(r"(.)\1+", r"\1", x.upper().replace("EE", "I").replace("OO", "U"))
    sus_assets, taken = [], set()
    for n in sus_names:
        hit = next((a for a in people if a not in taken and n.upper() in a.upper()), None) or \
            next((a for a in people if a not in taken and len(n) > 2 and flat(n) in flat(a)), None)
        sus_assets.append(hit)
        if hit:
            taken.add(hit)
    unmatched = [k for k, a in enumerate(sus_assets) if a is None]
    left = [a for a in people if a not in taken]
    free = [a for a in left if kind(a) == "person"] or left           # pehle insaan (C_ / G_), prop baad mein
    if taken and unmatched:                                            # mile hue suspects ke aas-paas wale
        last = max(people.index(a) for a in taken)
        near = [a for a in free if people.index(a) < last]
        free = (near + [a for a in free if a not in near])
    free = free[-len(unmatched):] if unmatched else []
    for k, pick in zip(unmatched, free + ["S05"] * len(unmatched)):   # naam se na mila: scene order mein jo bacha
        sus_assets[k] = pick
        taken.add(pick)
        notes.append(f"suspect '{sus_names[k]}' ki image naam se nahi mili -> {pick} li (check karo)")
    first_s = min((people.index(a) for a in sus_assets if a in people), default=len(people))
    before_s = [a for a in people[:first_s] if a not in taken]
    after_s = [a for a in people[first_s:] if a not in taken]
    victim = before_s[-1] if before_s else (people[0] if people else "S08")
    setup_img = next((a for a in before_s if a != victim), victim)
    witness = [a for a in before_s if a not in (victim, setup_img)]
    caps = sorted({n for n in sus_names} | {label(a) for a in people if kind(a) == "person"}, key=len, reverse=True)
    caps = [c for c in caps if len(c) > 2 and " " not in c]

    def size(a, role=None):
        if role:
            return SIZES[role]
        return SIZES["end"] if a.upper() == "S16" else SIZES[kind(a)]

    T = lambda x: f"{x:.2f}"
    rows = [["STYLE", "0", "1", "", "", style, "", "", "", ""]]
    think = timing.get("think")
    seg_start = lambda i: lines[i][0][0] if lines[i] else None
    starts = [i for i in story_lines if lines[i]]

    def nxt_start(i):
        later = [j for j in starts if j > i]
        return seg_start(later[0]) if later else (think[0] if think else seg_start(pakad))

    def add(a, s, e, pos, sz, text, eff, sfx, color):
        rows.append([use(a) if a else "", T(s), T(e), pos, str(sz) if sz != "" else "", text, eff, sfx, color, ""])

    def text_rows(i, s, e, color="", first_on_image=None):
        """line ke caption rows; first_on_image = (asset, size, eff, sfx) to pehli row image ke saath"""
        cr = caption_rows(pairs[i][1], lines[i], s, e, caps)
        for k, (a, b, txt) in enumerate(cr):
            if first_on_image:
                img, sz, eff, sfx = first_on_image
                add(img, a, b, "center", sz, txt, eff if k == 0 else eff.replace("heartbeat", ""),
                    sfx if k == 0 else "", color)
            else:
                add("", a, b, "", "", txt, "", "", color)
        return cr

    # 1. hook
    hook_end = seg_start(clue) if clue is not None else nxt_start(hook_lines[-1])
    vsize = SIZES["prop"] if kind(victim) == "prop" else SIZES["victim"]
    add(victim, 0, hook_end, "center", vsize, "", "nopop+night" if death else "nopop", "", "")
    add("", 0, hook_end, "", "90", hook_q, "nopop", "", "yellow")
    for n, i in enumerate(hook_lines):
        s = seg_start(i) if n else (lines[i][0][0] if lines[i] else 0)
        e = seg_start(hook_lines[n + 1]) if n + 1 < len(hook_lines) else hook_end
        text_rows(i, s, e, "red")

    # 2. Shivam S01 + clue
    if clue is not None:
        add("S01", hook_end, nxt_start(clue), "center", SIZES["shivam"],
            "Clue isi video\\nmein hai.\\nDhyaan se dekhna!", "", "whoosh", "yellow")

    # 3. kahani / crime / witness / suspects / clue line
    sus_idx = {i: k for k, i in enumerate(suspects)}
    first_clue_line = True
    for i in story_lines:
        if i in hook_lines or i == clue or not lines[i]:
            continue
        s, e = seg_start(i), nxt_start(i)
        stress = "yellow" if re.search(STRESS_HI, pairs[i][0]) else ""
        if i in sus_idx:
            k = sus_idx[i]
            a = sus_assets[k]
            add(a, s, e, "center", SIZES["person"], f"SUSPECT {k + 1}/{len(suspects)}", "", "swish", "yellow")
            rom = pairs[i][1]
            m = re.match(rf"^(.+?\s+{SAY_RO}[.…\s]*)(.*)$", rom, re.I)
            intro, quote = (m.group(1), m.group(3)) if m else ("", rom)
            n_intro = len(intro.split())
            dev = lines[i]
            cut = next((q for q, (_, _, w) in enumerate(dev) if re.search(SAY_HI, w)), -1) + 1
            q_start = dev[cut][0] if 0 < cut < len(dev) else s + (e - s) * 0.25
            if n_intro:
                add("", s, q_start, "", "", sus_names[k].upper(), "", "", "")
            quote = quote.strip().strip('"“”').strip()
            quote = quote[:1].upper() + quote[1:]
            cr = caption_rows(quote, dev[cut:] if cut > 0 else dev, q_start if n_intro else s, e, caps)
            for a2, b2, txt in cr:
                add("", a2, b2, "", "", f'"{txt}"', "", "", "")
        elif i == crime:
            text_rows(i, s, e, "red", (victim, vsize, "night" if death else "", "heartbeat"))
        elif suspects and i > suspects[-1]:
            img = after_s[0] if after_s else "S11"
            text_rows(i, s, e, stress or "yellow", (img, size(img), "", "whoosh" if first_clue_line else ""))
            first_clue_line = False
        elif crime is not None and i > crime:
            img = witness[0] if witness else "S05"
            text_rows(i, s, e, stress, (img, size(img), "", "swish"))
        else:
            img = setup_img
            sz = SIZES["prop"] if kind(img) == "prop" else SIZES["victim"]
            text_rows(i, s, e, stress, (img, sz, "", ""))

    # 4. soch pause
    pk_words = lines[pakad]
    if think:
        a, b = think
        add("S02", a, b, "center", SIZES["shivam"], "Shivam SOCH\\nraha hai...", "zoom+music_off", "tick_fast",
            "yellow")
        add("", a + 1, a + 2, "", "", "", "music_off", "", "")
        add("", a + 2, b, "", "", "", "music_off", "", "")
        s06 = b
    else:
        notes.append("THINK pause nahi mila (S02 soch row nahi bani)")
        s06 = pk_words[0][0] if pk_words else nxt_start(story_lines[-1])
    last_end = pk_words[-1][1] if pk_words else s06 + 2
    cta = last_end + CTA_GAP
    ch, total = timing.get("chunks"), timing.get("total")
    sig = cta + CTA_LEN
    if ch and think:
        guess = ch[1] + (think[1] - think[0])
        if cta + 1.5 < guess < (total or guess + 1) - 0.8:
            sig = guess
    total = total or sig + SIG_LEN

    # 5. S06 + boom
    add("S06", s06, cta, "center", SIZES["shivam"], "Detective Shivam ne...", "flash+music_off", "whoosh", "")
    boom_at = next((w[0] for w in pk_words if re.search(r"कातिल|क़ातिल|चोर|हत्यारे|हत्यारा|किलर|गलती|ग़लती", w[2])),
                   pk_words[-2][0] if len(pk_words) > 1 else s06 + 1)
    boom_at = min(max(boom_at, s06 + 0.3), cta - 0.3)
    add("", boom_at, cta, "", "", f"{who}\\npakad liya!", "", "boom", "yellow")

    # 6. CTA + end
    n = len(suspects)
    nums = "1 ya 2?" if n == 2 else (", ".join(str(x) for x in range(1, n)) + f" ya {n}?") if n > 1 else "Batao?"
    opt = f"C{case_tag(name, story)}_OPTIONS"
    if n > 1:
        rows.append([opt, T(cta), T(sig), "center", str(SIZES["options"]),
                     f"{who.title()} kaun?\\n{nums}\\nComment karo!", "", "ding", "", ""])
    else:
        add("S17", cta, sig, "center", SIZES["shivam"], f"{who.title()} kaun?\\nComment karo!", "", "ding", "")
    add("", cta, sig, "", "56", "Sahi answer kal pin hoga", "", "", "yellow")
    add("S16", sig, total, "center", SIZES["end"], "Shivam ki nazar se\\nkoi nahi bachta.", "noout", "whoosh", "")

    bad = [r for r in rows[1:] if float(r[2]) <= float(r[1]) + 0.01]
    for r in bad:
        notes.append(f"{r[1]}s: '{r[0] or r[5]}' row ka time 0 tha, hata di")
    rows = [rows[0]] + [r for r in rows[1:] if r not in bad]

    # answer screen par to nahi? (ANSWER ke number / quote captions mein)
    shown = " ".join(r[5] for r in rows).lower()
    for tok in set(re.findall(r"\d+[:/.]?\d*\s*\w+|\"[^\"]+\"", answer)):
        if tok.lower().strip('"') in shown:
            notes.append(f"DHYAAN: ANSWER wala '{tok}' screen par bhi hai - dekh lo jawab seedha na dikhe")
    for r in rows[1:]:
        if r[5] and r[5].count("\\n") >= 3:
            notes.append(f"{r[1]}s: text 3 line se lamba: {r[5]}")

    info = {"hook": hook_q, "who": who, "options": opt if n > 1 else None,
            "suspects": [[use(a), nm.title()] for a, nm in zip(sus_assets, sus_names)],
            "victim": use(victim), "total": round(total, 2), "notes": notes}
    return rows, info


HEADER = ["asset_id", "start", "end", "position", "size", "text", "effect", "sfx", "color", "focus"]


def to_text(rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(HEADER)
    w.writerows(rows)
    return buf.getvalue()


def load_timing(story, times=None):
    if times and os.path.exists(times):
        with open(times, encoding="utf-8") as f:
            return parse_build_voice(f.read())
    j = os.path.join(story, "VO_MAIN_timing.json")
    if os.path.exists(j):
        return estimate_from_json(j)
    sys.exit("Timing nahi mili: build_voice ka print (--times) ya story mein VO_MAIN_timing.json chahiye.")


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    argv = list(sys.argv[1:] if argv is None else argv)
    opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else d
    pos = [a for k, a in enumerate(argv) if not a.startswith("--") and (k == 0 or argv[k - 1] not in
                                                                        ("--times", "--names", "--style", "--out"))]
    if len(pos) < 2:
        sys.exit('Chalao: py auto_csv.py "<story folder>" "<NN Title>"')
    story, name = pos[0].rstrip("\\/"), pos[1]
    times = opt("--times") or os.path.join(CASES, name + ".voice_times.txt")
    nf = opt("--names")
    if nf:
        with open(nf, encoding="utf-8") as f:
            names = parse_prep_names(f.read())
    else:
        names = guess_names(story)
    rows, info = build(story, name, load_timing(story, times), names, opt("--style", "rise"))
    text = to_text(rows)
    if "--print" in argv:
        print(text)
    else:
        out = opt("--out", os.path.join(CASES, name + ".csv"))
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        print(f"CSV DRAFT bana -> {out}")
    print(f"  sawaal: {info['hook']}   suspects: " + ", ".join(f"{a}:{n}" for a, n in info["suspects"]))
    for n in info["notes"]:
        print("  * " + n)
    return info


if __name__ == "__main__":
    main()
