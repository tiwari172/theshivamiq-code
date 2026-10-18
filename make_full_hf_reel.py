# theshivamiq – EK COMMAND mein poori HyperFrames (motion-graphics) reel
#
#   py make_full_hf_reel.py "<story folder>" "<NN Title>"
#   py make_full_hf_reel.py "<story folder>" "<NN Title>" --from 4     step 4 se dobara (pehle wale skip)
#   py make_full_hf_reel.py "<story folder>" "<NN Title>" --dry-run    sirf batao kya karega, kuch mat chalao
#   --tak 5      step 5 (render) ke baad ruk jao - story folder mein kuch copy nahi
#   --haan       purani MP4 / haath se badla DATA replace karne ka sawaal mat poocho, seedha "haan"
#   --force      DATA check mein PROBLEM ho tab bhi render (sirf user bole)
#
# Steps (purane scripts hi chalte hain, engine kabhi nahi badalta):
#   1 prep_story.py   2 build_voice.py (3.0s soch-pause)   3 story + shabd ka time -> HF DATA (hf_data.json, DRAFT)
#   4 project: hyperframes\<NN Title>\ (shivam_engine.html copy + DATA + images + mix.wav)
#   5 render (npx hyperframes) -> output\<NN Title> - HF.mp4 + CHECK grid
#   6 MP4 + timing.csv story folder mein (purani MP4 ho to poochta hai)   7 make_cover.py one
#
# Structure auto_csv.py wala hi (hook, crime, Shivam, suspects, soch + tick_fast, pakad liya + boom, CTA, end),
# bas DATA HyperFrames engine ka: har ~3 sec visual change (1.12x punch), shabd-shabd peela caption,
# safe zone (upar 15% / neeche 20% khaali), music -14 dB (bolte waqt -16 dB), SFX CSV ke time par.
# DATA haath se theek karna ho: hyperframes\<NN Title>\hf_data.json badlo, phir  --from 4

import glob, html, json, math, os, re, shutil, subprocess, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import auto_csv
from make_full_reel import Stop, ask, md5, py, read_json, run, say

CASES = os.path.join(BASE, "cases")
ASSETS = os.path.join(BASE, "assets")
VOICE = os.path.join(BASE, "voice")
MUSIC = os.path.join(BASE, "music")
OUTPUT = os.path.join(BASE, "output")
SFX = os.path.join(BASE, "sfx")
HF = os.path.join(BASE, "hyperframes")
ENGINE = os.path.join(HF, "_ENGINE")
STORY_ROOT = r"C:\Users\Hp\Desktop\reels story"
FONT_FILE = r"C:\Windows\Fonts\ariblk.ttf"         # hook reels wala font (Arial Black)
HF_VERSION = "0.8.144"
THINK_TEXT, THINK = "डिटेक्टिव शिवम", "3.0"
FPS = 30

W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = int(H * 0.15), int(H * 0.80)    # 288 / 1536: text sirf iske beech
# engine CFG: header 290-490, caption 490-790, naam patti 1400, stopwatch 300, soch text 600, CTA pill 1400
LAYOUT = {"hdrTop": 290, "capTop": 490, "capSize": 80, "stroke": 12, "nameTop": 1400, "watchTop": 300,
          "sochTop": 600, "ctaTop": 1400, "levelTop": 300, "punch": 1.06, "floatPx": 12, "zoom": 1.1,
          "activeWord": "#FFE600", "ctaText": "Sahi answer kal pin hoga"}
BOX_H = {"hdrTop": 200, "capTop": 300, "nameTop": 110, "watchTop": 290, "sochTop": 210, "ctaTop": 120}
MAX_GAP, PUNCH_EVERY = 3.5, 3.0        # itne sec se zyada bina visual change nahi
CAP_CHARS, CAP_WORDS = 18, 6           # ek caption tukda: max 2 line x 18 akshar, max 6 shabd
MUSIC_GAP_DB, MUSIC_TALK_DB = 14, 16   # music voice se itna neeche: chup mein / bolte waqt
SFX_VOLUME = 0.35

STEPS = {1: "Images (prep_story)", 2: "Voice (build_voice)", 3: "HF DATA draft (hf_data.json)",
         4: "Project (engine + assets + mix.wav)", 5: "Render (hyperframes)",
         6: "Copy MP4 + timing.csv story mein", 7: "Case File cover (make_cover)"}
DATA_STEPS = (4, 5, 6, 7)      # hf_data.json badle to ye dobara


# ============================== images ==============================
def asset_size(asset):
    """code assets\\ ki PNG ka asli size (transparent kinare hata kar). Na mile to None"""
    p = os.path.join(ASSETS, asset + ".png")
    if not os.path.exists(p):
        return None
    from PIL import Image
    im = Image.open(p).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    return (bb[2] - bb[0], bb[3] - bb[1]) if bb else im.size


def trim_png(src, dst, max_side=1500):
    from PIL import Image
    im = Image.open(src).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if bb:
        im = im.crop(bb)
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    im.save(dst)


def fit(size, bw, bh):
    w, h = size
    k = min(bw / w, bh / h)
    return round(w * k), round(h * k)


def place(asset, size):
    """engine SCENE ka size + jagah (HOOK_REEL_GUIDE wale naap): {h|w, bottom}"""
    a = asset.upper()
    if a.endswith("_OPTIONS"):                       # options card: caption ke neeche (800), CTA pill (1400) ke upar
        w, h = fit(size or (W, 780), 980, 580)       # make_cards card = 1080 x 780 (step 3 tak bana nahi hota)
        return {"w": w, "bottom": H - 800 - h}
    size = size or (500, 1000)
    ar = size[0] / size[1]
    if re.match(r"^S1[67](_|$)", a):                 # Shivam close-up
        w, h = fit(size, 1000, 1130)
        return {"h": h, "bottom": 0}
    if a.startswith("P_"):                           # prop: beech mein
        w, h = fit(size, 880, 620)
        return {"w": w, "bottom": round(H - 1160 - h / 2)}
    if ar > 1.15:                                    # leta hua / chauda
        w, h = fit(size, 980, 640)
        return {"w": w, "bottom": 300}
    w, h = fit(size, 980, 1000)                      # khada
    return {"h": h, "bottom": 140} if w < 980 else {"w": w, "bottom": 140}


# ============================== DATA ==============================
def r2(x):
    return round(float(x), 2)


def case_no(name):
    m = re.match(r"([A-Z]?\d{2}-\d{3})", name)
    return m.group(1) if m else name.split()[0]


def cap_fits(ws):
    return len(ws) <= CAP_WORDS and len(auto_csv.wrap([w[0] for w in ws], CAP_CHARS)) <= 2


def balanced(ws):
    """lamba phrase -> kam se kam barabar tukde (har tukda max 6 shabd / 2 line)"""
    for k in range(1, len(ws) + 1):
        size = sum(len(w[0]) + 1 for w in ws) / k
        parts, cur, c = [], [], 0
        for w in ws:
            if cur and c + (len(w[0]) + 1) / 2 > size * (len(parts) + 1) and len(parts) < k - 1:
                parts.append(cur)
                cur = []
            cur.append(w)
            c += len(w[0]) + 1
        parts.append(cur)
        if all(cap_fits(p) for p in parts):
            return parts
    return [[w] for w in ws]


def caption_chunks(words):
    """[(word, s, e)] -> screen ke tukde: , . ? ! par todo, lamba phrase barabar baanto, akela shabd jodo"""
    phrases, cur = [], []
    for w in words:
        cur.append(w)
        if auto_csv.ends_phrase(w[0]):
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    out = []
    for ph in phrases:
        for part in balanced(ph):
            if out and (len(part) == 1 or len(out[-1]) == 1) and cap_fits(out[-1] + part):
                out[-1] = out[-1] + part             # akela latka shabd padosi ke saath
            else:
                out.append(part)
    return out


def spread(roman, a, b):
    """Roman shabd [a, b] mein akshar ke hisaab se (CTA / signature: inka shabd-time voice print mein nahi)"""
    words = roman.split()
    total = sum(len(w) + 1 for w in words) or 1
    out, c = [], 0
    for w in words:
        s = a + (b - a) * c / total
        c += len(w) + 1
        out.append([w, r2(s), r2(a + (b - a) * c / total)])
    return out


def caps_words(words, caps):
    """naam CAPS (engine CAPS shabd ko peela dabba deta hai). Bayan ("...") ke andar kabhi CAPS nahi"""
    out, quote = [], False
    for w in words:
        if w.startswith(('"', "“")):
            quote = True
        core = re.sub(r"[^A-Za-z]", "", w)
        if not quote and core and any(core.lower() == c.lower() for c in caps):
            w = w.replace(core, core.upper())
        if quote and re.search(r'["”][.,!?…]*$', w[1:] if w.startswith(('"', "“")) else w):
            quote = False
        out.append(w)
    return out


def build_data(story, name, timing, names=None, sizes=None):
    """story + build_voice timing -> HF engine DATA (dict). sizes(asset) -> (w, h) ya None"""
    sizes = sizes or asset_size
    rows, info = auto_csv.build(story, name, timing, names)
    pairs, scene_order, answer, _ = auto_csv.script_lines(auto_csv.find_script(story))
    lines, _ = auto_csv.align(pairs, timing)
    notes = list(info["notes"])
    R = [dict(zip(auto_csv.HEADER, r)) for r in rows[1:]]
    for r in R:
        r["s"], r["e"] = float(r["start"]), float(r["end"])
        r["fx"] = r["effect"].split("+") if r["effect"] else []
    END = r2(max(r["e"] for r in R))
    who = info["who"]

    # ---------- SCENES: lagatar same image = ek scene ----------
    scenes, sus_k = [], 0
    for r in R:
        a = r["asset_id"]
        if not a:
            continue
        if scenes and scenes[-1]["img"] == a and abs(scenes[-1]["e"] - r["s"]) < 0.05:
            scenes[-1]["e"] = r2(r["e"])
            continue
        sc = {"img": a, "s": r2(r["s"]), "e": r2(r["e"])}
        sc.update(place(a, sizes(a)))
        up = a.upper()
        if not scenes:
            sc["enter"] = "fade"
        elif r["text"].startswith("SUSPECT"):
            sc["enter"] = "left" if sus_k % 2 == 0 else "right"
            sus_k += 1
        elif re.match(r"^S1[67](_|$)", up):
            sc["enter"] = "rise"
        elif up.startswith("P_"):
            sc["enter"] = "drop"
        elif up.endswith("_OPTIONS") or auto_csv.SHIVAM.match(up):
            sc["enter"] = "pop"
        else:
            sc["enter"] = "popin"
        if up == "S02":
            sc["push"] = 1.14
        scenes.append(sc)
    scenes[-1]["noexit"] = True
    miss = sorted({s["img"] for s in scenes if sizes(s["img"]) is None and not s["img"].upper().endswith("_OPTIONS")})
    if miss:                # options card step 4 mein banta hai, uska size andaze se theek hai
        notes.append("assets\\ mein nahi mili (size andaze se): " + ", ".join(miss))

    # ---------- T (engine ke graphics) ----------
    T = {}
    by_text = lambda t: next((r for r in R if r["text"] == t), None)
    hook = by_text(info["hook"])
    if hook:
        T["hook"] = [0.1, r2(hook["e"]), info["hook"]]
    s01 = next((s for s in scenes if s["img"] == "S01"), None)
    if s01:
        T["caseChip"] = [r2(s01["s"] + 0.1), s01["e"]]
    crime = next((r for r in R if r["sfx"] == "heartbeat"), None)
    if crime:
        sc = next(s for s in scenes if s["s"] <= crime["s"] < s["e"])
        if "night" in crime["fx"]:
            T["crime"] = [r2(crime["s"]), sc["e"]]
        elif who == "CHOR":
            T["stamps"] = [["CHORI!", r2(crime["s"] + 0.1), r2(min(sc["e"], crime["s"] + 1.6)), -6]]
    night = []
    for r in R:
        if "night" in r["fx"]:
            if night and r["s"] - night[-1][1] < 0.05:
                night[-1][1] = r2(max(night[-1][1], r["e"]))
            else:
                night.append([r2(r["s"]), r2(r["e"]), 0.8])
    T["night"] = night
    sus = []
    for k, r in enumerate(R):
        if r["text"].startswith("SUSPECT"):
            sc = next(s for s in scenes if s["img"] == r["asset_id"] and s["s"] <= r["s"] < s["e"])
            nxt = R[k + 1] if k + 1 < len(R) else None
            nm = nxt["text"] if nxt and not nxt["asset_id"] and re.fullmatch(r"[A-Z .]+", nxt["text"] or "-") else ""
            if not nm:
                idx = len(sus)
                nm = info["suspects"][idx][1].upper() if idx < len(info["suspects"]) else ""
            sus.append([r["text"], html.escape(nm), sc["s"], sc["e"]])
    T["suspects"] = sus
    think = timing.get("think")
    s02 = next((s for s in scenes if s["img"] == "S02"), None)
    if sus:
        clue = next((s for s in scenes if s["s"] >= sus[-1][3] - 0.01 and s["img"] != "S02"
                     and (s02 is None or s["s"] < s02["s"])), None)
        if clue:
            T["dhyaan"] = [r2(clue["s"] + 0.1), r2(min(clue["e"], clue["s"] + 2.6))]
    if s02:
        T["soch"] = s02["s"]
    boom = next((r for r in R if r["sfx"] == "boom"), None)
    if boom:
        T["solved"] = [r2(boom["s"]), r2(boom["e"])]
        s06 = next((s for s in scenes if s["img"] == "S06"), None)
        if s06:
            s06["shake"] = [r2(boom["s"])]
    opt = next((r for r in R if r["sfx"] == "ding"), None)
    if opt:
        parts = opt["text"].split("\\n")
        title = next((p for p in parts if re.search(r"\d", p)), parts[0].upper())
        T["options"] = [r2(opt["s"]), r2(opt["e"]), title]
        T["ctaPill"] = [r2(opt["s"] + 0.6), r2(opt["e"])]
    end = scenes[-1]
    T["brand"] = r2(end["s"] + 0.3)

    # ---------- P: shabd-shabd caption (Roman) ----------
    real = [i for i, (d, _) in enumerate(pairs) if not auto_csv.is_pause(d)]
    pakad = next(i for i in reversed(real) if "पकड़" in pairs[i][0] or "pakad" in pairs[i][1].lower())
    caps = sorted({n for _, n in info["suspects"]} | {auto_csv.label(a) for a in scene_order
                                                      if auto_csv.kind(a) == "person"}, key=len, reverse=True)
    caps = [c for c in caps if len(c) > 2 and " " not in c and not c.upper().startswith("SUSPECT")]
    P = []
    for i in real:
        if i > pakad or not lines[i]:
            continue
        rw = pairs[i][1].split()
        rw = caps_words(rw, caps + ([who.lower(), "kaatil", "katil", "killer"] if i == pakad else []))
        st = auto_csv.roman_times(rw, lines[i])
        line_end = lines[i][-1][1]
        ws = [[w, r2(s), r2(st[k + 1] if k + 1 < len(st) else line_end)] for k, (w, s) in enumerate(zip(rw, st))]
        for ch in caption_chunks(ws):
            P.append(ch)
    after = [i for i in real if i > pakad]
    if opt and after:                                # CTA (options ke waqt) + signature (S16 ke waqt)
        cta_lines, sig_line = after[:-1] or after, after[-1] if len(after) > 1 else None
        a, b = opt["s"] + 0.15, end["s"] - 0.25
        txt = " ".join(pairs[i][1] for i in cta_lines)
        for ch in caption_chunks(spread(txt, a, b)):
            P.append(ch)
        if sig_line is not None:
            for ch in caption_chunks(spread(pairs[sig_line][1], end["s"] + 0.15, END - 0.4)):
                P.append(ch)
    # time chip (sirf suspects se pehle, 1.4 sec): "Teen baje..." -> TEEN BAJE
    first_sus = sus[0][2] if sus else END
    for ph in P:
        txt = " ".join(w for w, _, _ in ph)
        m = re.search(r"\b([A-Za-z]+\s+baje)\b", txt, re.I)
        if m and ph[0][1] < first_sus:
            T["chips"] = [["clock", m.group(1).upper(), ph[0][1], r2(min(ph[0][1] + 1.4, first_sus))]]
            break

    # ---------- har ~3 sec visual change: lambe scene mein 1.12x punch ----------
    events = sorted({s["s"] for s in scenes} | set(visual_events(T)))
    word_starts = [w[1] for ph in P for w in ph]
    for sc in scenes:
        if sc.get("push"):
            continue
        pts = [sc["s"]] + [t for t in events if sc["s"] + 0.01 < t < sc["e"] - 0.01] + [sc["e"]]
        add = []
        for a, b in zip(pts, pts[1:]):
            n = math.ceil((b - a) / PUNCH_EVERY - 1e-9)
            if b - a <= MAX_GAP or n < 2:
                continue
            for k in range(1, n):
                t = a + (b - a) * k / n
                near = [x for x in word_starts if abs(x - t) <= 0.3 and a + 0.8 < x < b - 0.8]
                add.append(r2(min(near, key=lambda x: abs(x - t)) if near else t))
        if add:
            sc["punch"] = add

    # ---------- awaaz: SFX / music band / bolne ka waqt ----------
    sfx = [[r["sfx"], r2(r["s"])] for r in R if r["sfx"]]
    mutes = [[r2(r["s"]), r2(min(r["s"] + 1.0, END))] for r in R if "music_off" in r["fx"]]
    speech = []
    for s, e, _ in timing["words"]:
        if e <= s or s >= END:
            continue
        if speech and s - speech[-1][1] < 0.35:
            speech[-1][1] = r2(max(speech[-1][1], e))
        else:
            speech.append([r2(s), r2(e)])
    if opt:
        speech.append([r2(opt["s"]), END])            # CTA + signature (voice mein, print mein nahi)

    CFG = dict(LAYOUT, cover=0)
    data = {"OFF": 0, "END": END, "CASE": case_no(name), "SCENES": scenes, "P": P, "T": T, "CFG": CFG,
            "AUDIO": {"sfx": sfx, "mutes": mutes, "speech": speech},
            "INFO": {"name": name, "hook": info["hook"], "who": who, "options": info["options"],
                     "suspects": info["suspects"], "notes": notes}}
    return data, rows


def visual_events(T):
    """T ke graphics kab screen par badalte hain (visual change)"""
    ev = []
    for k in ("hook", "caseChip", "crime", "dhyaan", "solved", "options", "ctaPill"):
        if T.get(k):
            ev.append(T[k][0])
    for k in ("chips", "stamps"):
        ev += [x[2] if k == "chips" else x[1] for x in T.get(k) or []]
    ev += [x[2] for x in T.get("suspects") or []]
    ev += [x[0] for x in T.get("night") or []]
    if T.get("soch") is not None:
        ev += [T["soch"], T["soch"] + 1, T["soch"] + 2]
    if T.get("brand") is not None:
        ev.append(T["brand"])
    return ev


# ============================== check (render se pehle) ==============================
DEVA = re.compile(r"[\u0900-\u097f]")


def check_data(data, answer=""):
    """-> (problems, warnings). PROBLEM ho to render nahi"""
    probs, warns = [], []
    END, S, T, P, C = data["END"], data["SCENES"], data["T"], data["P"], data["CFG"]
    shown = []
    for ph in P:
        shown += [w for w, _, _ in ph]
    for x in T.get("suspects", []):
        shown += [x[0], x[1]]
    for k in ("hook", "options"):
        if T.get(k):
            shown.append(T[k][2])
    shown += [c[1] for c in T.get("chips", [])] + [s[0] for s in T.get("stamps", [])] + [C.get("ctaText", "")]
    for t in shown:
        if DEVA.search(str(t)):
            probs.append(f"screen par Devanagari: {t}")
    low = " ".join(map(str, shown)).lower()
    for tok in set(re.findall(r"\d+[:/.]?\d*\s*\w+|\"[^\"]+\"", answer or "")):
        if tok.lower().strip('"') in low:
            probs.append(f"ANSWER wala '{tok}' screen par hai - jawab seedha mat dikhao")
    for sc in S:
        if sc.get("zoom") or sc.get("focus"):
            warns.append(f"{sc['img']}: zoom laga hai - clue par zoom/highlight nahi hona chahiye")
        if not (0 <= sc["s"] < sc["e"] <= END + 0.01):
            probs.append(f"{sc['img']}: galat time {sc['s']}-{sc['e']}")
    last = -1
    for ph in P:
        if not ph:
            probs.append("khaali caption tukda")
            continue
        if ph[0][1] < last - 0.01:
            probs.append(f"caption ulta time: {ph[0][0]} {ph[0][1]}")
        last = ph[0][1]
        if len(auto_csv.wrap([w for w, _, _ in ph], CAP_CHARS)) > 2:
            warns.append(f"{ph[0][1]}s: caption 2 line se lamba: {' '.join(w for w, _, _ in ph)}")
        if ph[-1][2] > END + 0.01:
            probs.append(f"caption END ke baad: {ph[-1][0]}")
    for k, h in BOX_H.items():
        top = C.get(k)
        if top is not None and (top < SAFE_TOP or top + h > SAFE_BOTTOM):
            probs.append(f"CFG.{k}={top}: safe zone (upar {SAFE_TOP}px / neeche {SAFE_BOTTOM}px) ke bahar")
    # khaali screen: har waqt koi image
    t = 0.0
    for sc in sorted(S, key=lambda s: s["s"]):
        if sc["s"] > t + 0.05:
            probs.append(f"{t:.2f}-{sc['s']:.2f}s: khaali screen (koi image nahi)")
        t = max(t, sc["e"])
    if t < END - 0.05:
        probs.append(f"{t:.2f}-{END:.2f}s: khaali screen (end)")
    gap = max_visual_gap(data)
    if gap[0] > MAX_GAP + 0.01:
        warns.append(f"{gap[1]:.2f}s ke baad {gap[0]:.1f} sec tak koi visual change nahi")
    if T.get("soch") is None:
        warns.append("soch (stopwatch) nahi laga - THINK pause nahi mila")
    for name, at in data["AUDIO"]["sfx"]:
        if name == "tick":
            probs.append("purana dheema 'tick' laga hai - sirf tick_fast")
    return probs, warns


def max_visual_gap(data):
    ev = sorted({0.0, data["END"]} | {s["s"] for s in data["SCENES"]} |
                {t for s in data["SCENES"] for t in s.get("punch", [])} | set(visual_events(data["T"])))
    best = (0.0, 0.0)
    for a, b in zip(ev, ev[1:]):
        if b - a > best[0]:
            best = (b - a, a)
    return best


# ============================== engine page ==============================
def data_js(d):
    js = lambda o: json.dumps(o, ensure_ascii=False)
    return (f"const OFF = {d['OFF']};\n      const END = {d['END']};\n      const CASE = {js(d['CASE'])};\n"
            f"      const SCENES = {js(d['SCENES'])};\n      const P = {js(d['P'])};\n"
            f"      const T = {js(d['T'])};\n      const CFG = {js(d['CFG'])};")


def page(d, title):
    with open(os.path.join(ENGINE, "shivam_engine.html"), encoding="utf-8") as f:
        eng = f.read()
    dur = f"{d['OFF'] + d['END']:.3f}"
    return (eng.replace("__TITLE__", html.escape(title)).replace("__DUR__", dur).replace("__MEDIA__", "")
            .replace("__OVERLAYS__", "").replace("__DATA__", data_js(d)))


# ============================== audio ==============================
def build_mix(voice, music, d, out, sfx_dir=None):
    """voice + music (-14 dB, bolte waqt -16 dB, music_off par band) + SFX -> mix.wav. -> (log, missing sfx)"""
    import make_reel as mr
    sfx_dir = sfx_dir or SFX
    A, END = d["AUDIO"], d["END"]
    fmt = "aformat=sample_rates=44100:channel_layouts=stereo"
    gain = mr.mean_db(voice) - MUSIC_GAP_DB - mr.mean_db(music)
    duck = 10 ** (-(MUSIC_TALK_DB - MUSIC_GAP_DB) / 20)
    talk = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in A["speech"]) or "0"
    mute = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in A["mutes"]) or "0"
    cmd = [mr.FFMPEG, "-y", "-loglevel", "error", "-i", voice, "-stream_loop", "-1", "-i", music]
    fc = (f"[0:a]{fmt},apad=whole_dur={END:.3f}[v];"
          f"[1:a]{fmt},volume={gain:.1f}dB,volume={duck:.3f}:enable='{talk}',volume=0:enable='{mute}',"
          f"afade=t=in:d=0.3,afade=t=out:st={max(0, END - 0.6):.2f}:d=0.6[m];")
    mix, n, missing = "[v][m]", 2, []
    for name, t in A["sfx"]:
        p = next((os.path.join(sfx_dir, name + e) for e in (".wav", ".mp3") if os.path.exists(os.path.join(sfx_dir, name + e))), None)
        if not p:
            missing.append(name)
            continue
        cmd += ["-i", p]
        ms = int(t * 1000)
        fc += f"[{n}:a]{fmt},volume={SFX_VOLUME},adelay={ms}|{ms}[x{n}];"
        mix += f"[x{n}]"
        n += 1
    fc += f"{mix}amix=inputs={n}:duration=first:normalize=0,alimiter=limit=0.95[a]"
    cmd += ["-filter_complex", fc, "-map", "[a]", "-t", f"{END:.3f}", out]
    subprocess.run(cmd, check=True)
    return (f"mix.wav {END:.1f}s (music: {os.path.basename(music)}, -{MUSIC_GAP_DB}/-{MUSIC_TALK_DB} dB, "
            f"{len(A['sfx']) - len(missing)} sfx)"), missing


# ============================== pipeline ==============================
def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def run_shell(cmd, cwd):
    """npx (Windows par npx.cmd) - shell se, output saath saath"""
    say("   > " + cmd)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                         text=True, encoding="utf-8", errors="replace", bufsize=1)
    out = []
    for line in p.stdout:
        out.append(line)
        print("     " + line.rstrip("\n"), flush=True)
    p.wait()
    return p.returncode, "".join(out)


class State:
    def __init__(self, name, story, dry=False):
        self.path = os.path.join(CASES, name + ".hf.state.json")
        self.dry = dry
        self.d = {}
        if os.path.exists(self.path):
            try:
                self.d = read_json(self.path)
            except ValueError:
                self.d = {}
        self.d.setdefault("done", {})
        self.d["story"], self.d["name"] = story, name

    def save(self):
        if not self.dry:
            os.makedirs(CASES, exist_ok=True)
            write_json(self.path, self.d)

    def done(self, n, **extra):
        self.d["done"][str(n)] = dict(at=time.strftime("%Y-%m-%d %H:%M"), **extra)
        self.save()

    def undo_from(self, n):
        for k in list(self.d["done"]):
            if int(k) >= n:
                del self.d["done"][k]


class Reel:
    def __init__(self, story, name, opts):
        self.story, self.name, self.o = story, name, opts
        self.proj = os.path.join(HF, name)
        self.data = os.path.join(self.proj, "hf_data.json")
        self.timing_csv = os.path.join(self.proj, "timing.csv")
        self.times = os.path.join(CASES, name + ".voice_times.txt")      # make_full_reel wali hi file
        self.prep_log = os.path.join(CASES, name + ".prep.txt")
        self.voice = os.path.join(VOICE, name + ".m4a")
        self.mp4 = os.path.join(OUTPUT, name + " - HF.mp4")
        self.grid = os.path.join(OUTPUT, name + " - HF CHECK.png")
        self.story_mp4 = os.path.join(story, name + ".mp4")
        self.st = State(name, story, opts["dry"])
        self.copy_ok = None

    def is_done(self, n):
        rec = self.st.d["done"].get(str(n))
        if n == 2 and not rec and self.voice_ready():
            return True                                  # make_full_reel ne voice pehle hi bana di
        if not rec:
            return False
        if n in DATA_STEPS and rec.get("data") != md5(self.data):
            return False                                 # DATA baad mein badla -> dobara
        need = {2: [self.voice, self.times], 3: [self.data], 4: [os.path.join(self.proj, "index.html"),
                os.path.join(self.proj, "assets", "mix.wav")], 5: [self.mp4], 6: [self.story_mp4],
                7: [rec.get("cover", "")]}.get(n, [])
        if n == 1 and not self.st.d.get("names"):
            return False
        return all(p and os.path.exists(p) for p in need)

    def voice_ready(self):
        vo = os.path.join(self.story, "VO_MAIN.mp3")
        return all(os.path.exists(p) for p in (self.voice, self.times, vo)) and \
            os.path.getmtime(self.times) >= os.path.getmtime(vo) and "THINK pause" in open(self.times, encoding="utf-8").read()

    # ---------- steps ----------
    def step1(self):
        if not os.path.isdir(os.path.join(self.story, "images")):
            raise Stop(f"Story mein images\\ folder nahi hai: {self.story}")
        rc, out = run(py("prep_story.py", self.story), self.prep_log)
        if rc:
            raise Stop("prep_story.py fail hua (upar error dekho). Images theek karke --from 1 se chalao.")
        names = auto_csv.parse_prep_names(out)
        if not names:
            raise Stop('prep_story ne "CSV mein ye naam lagao" list nahi di.')
        self.st.d["names"] = names
        sheet = re.search(r"Contact sheet -> (.+)", out)
        self.st.d["sheet"] = sheet.group(1).strip() if sheet else ""
        self.st.done(1)

    def step2(self):
        if self.voice_ready() and self.o["from"] != 2:
            say(f"   voice\\{self.name}.m4a + shabd ka time pehle se hai (make_full_reel ne banaya) - wahi use kiya. "
                "Nayi chahiye to --from 2")
            self.st.done(2)
            return
        for f in ("VO_MAIN.mp3", "VO_MAIN_timing.json"):
            if not os.path.exists(os.path.join(self.story, f)):
                c, s = re.search(r"Category (\d+)", self.story), re.search(r"Story (\d+)", self.story)
                hint = f"py eleven_voice.py {c.group(1)} {int(s.group(1))}" if c and s else "py eleven_voice.py <cat> <story>"
                raise Stop(f"Story mein {f} nahi hai. Pehle ElevenLabs voice banao:  {hint}\n"
                           f"   (CTA / Signature dobara mat banana) - phir yahi command dobara chalao.")
        j = read_json(os.path.join(self.story, "VO_MAIN_timing.json"))
        if THINK_TEXT not in "".join(j["characters"]):
            raise Stop(f'VO mein "{THINK_TEXT}" nahi mila - soch-pause kahan daale? SCRIPT / VO check karo.')
        rc, out = run(py("build_voice.py", self.story, self.name, THINK_TEXT, THINK), self.times)
        if rc or not os.path.exists(self.voice):
            raise Stop("build_voice.py fail hua (upar error dekho). Theek karke --from 2 se chalao.")
        th = re.search(r"THINK pause .+", out)
        if th:
            say(f"   {th.group(0)}  <- ye 'डिटेक्टिव शिवम ने...pakad liya' se theek pehle hona chahiye")
        self.st.done(2)

    def step3(self):
        old, made = md5(self.data), self.st.d.get("data_made")
        if old and old != made:
            say(f"   {self.data} pehle se hai (haath se badla hua).")
            if not ask("   Nayi DRAFT DATA se replace karun? (purani hf_data.json.old ban jaayegi)", self.o["yes"]):
                say("   Purana DATA hi rakha.")
                self.st.done(3)
                return
            shutil.copy2(self.data, self.data + ".old")
        if os.path.isdir(self.proj) and not made and os.path.exists(os.path.join(self.proj, "index.html")) \
                and not os.path.exists(self.data):
            say(f"   hyperframes\\{self.name}\\ mein pehle se ek (haath wali?) HF project hai.")
            if not ask("   Isi folder mein naya project likh dun? (index.html replace hoga)", self.o["yes"]):
                raise Stop("Purana HF project nahi chheda. Reel ka naam badal kar chalao (jaise \"... v2\").")
        timing = auto_csv.load_timing(self.story, self.times)
        d, rows = build_data(self.story, self.name, timing, self.st.d.get("names"))
        os.makedirs(self.proj, exist_ok=True)
        write_json(self.data, d)
        with open(self.timing_csv, "w", encoding="utf-8", newline="") as f:
            f.write(auto_csv.to_text(rows))
        info = d["INFO"]
        say(f"   HF DATA DRAFT -> hyperframes\\{self.name}\\hf_data.json  ({len(d['SCENES'])} scenes, "
            f"{len(d['P'])} caption tukde, {d['END']}s)")
        say(f"   sawaal: {info['hook']}   suspects: " + ", ".join(f"{a}:{n}" for a, n in info["suspects"]))
        for n in info["notes"]:
            say("   * " + n)
        self.st.d["info"], self.st.d["data_made"] = {k: info[k] for k in ("hook", "options", "suspects")}, md5(self.data)
        self.st.done(3)

    def load_data(self):
        try:
            return read_json(self.data)
        except (OSError, ValueError) as e:
            raise Stop(f"hf_data.json padh nahi paaya ({e}). Galti theek karo ya --from 3 se nayi DATA banao.")

    def answer(self):
        try:
            return auto_csv.script_lines(auto_csv.find_script(self.story))[2]
        except SystemExit:
            return ""

    def step4(self):
        d = self.load_data()
        probs, warns = check_data(d, self.answer())
        for w in warns:
            say("   DHYAAN: " + w)
        if probs:
            say("   PROBLEM:\n     - " + "\n     - ".join(probs))
            if not self.o["force"]:
                raise Stop("DATA check mein PROBLEM - project/render NAHI banaya. hf_data.json theek karo, "
                           "phir yahi command dobara (ya --force sirf user bole).")
        info = d.get("INFO", {})
        if info.get("options") and any(s["img"] == info["options"] for s in d["SCENES"]):
            items = [f"{a}:{n}" for a, n in info["suspects"]]
            rc, _ = run(py("make_cards.py", "options", info["options"], *items))
            if rc:
                raise Stop("Options card nahi bana (upar error). Suspects ki image naam check karo.")
        adir = os.path.join(self.proj, "assets")
        os.makedirs(os.path.join(adir, "fonts"), exist_ok=True)
        miss = []
        for img in dict.fromkeys(s["img"] for s in d["SCENES"]):
            src = os.path.join(ASSETS, img + ".png")
            if os.path.exists(src):
                trim_png(src, os.path.join(adir, img + ".png"))
            else:
                miss.append(img + ".png")
        bg = os.path.join(ASSETS, "BG_MAIN.png")
        logo = next((p for p in (os.path.join(ENGINE, "template", "LOGO_ROUND.png"), os.path.join(ASSETS, "LOGO_ROUND.png"))
                     if os.path.exists(p)), None)
        font = next((p for p in (FONT_FILE, os.path.join(ASSETS, "fonts", "MAIN.ttf")) if os.path.exists(p)), None)
        for what, p in (("assets\\BG_MAIN.png", bg if os.path.exists(bg) else None), ("LOGO_ROUND.png", logo),
                        ("font ariblk.ttf", font)):
            if not p:
                miss.append(what)
        if miss:
            raise Stop("Ye files nahi mili (code assets\\ mein daalo, phir --from 4):\n     - " + "\n     - ".join(miss))
        shutil.copy2(bg, os.path.join(adir, "BG_MAIN.png"))
        shutil.copy2(logo, os.path.join(adir, "LOGO_ROUND.png"))
        shutil.copy2(font, os.path.join(adir, "fonts", "MAIN.ttf"))
        from PIL import Image
        Image.new("RGB", (W, H), "black").save(os.path.join(adir, "cover.png"))     # engine ko chahiye (dikhta nahi)
        for f in ("hyperframes.json", "package.json"):
            if not os.path.exists(os.path.join(self.proj, f)):
                shutil.copy2(os.path.join(ENGINE, "template", f), os.path.join(self.proj, f))
        music = self.ensure_music()
        log, missing = build_mix(self.voice, music, d, os.path.join(adir, "mix.wav"))
        say("   " + log)
        if missing:
            say("   DHYAAN: ye SFX sfx\\ mein nahi mile (bina inke mix bana): " + ", ".join(sorted(set(missing))))
        with open(os.path.join(self.proj, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(d, self.name))
        say(f"   project taiyaar -> {self.proj}")
        self.st.done(4, data=md5(self.data))

    def ensure_music(self):
        os.makedirs(MUSIC, exist_ok=True)
        have = sorted(f for f in os.listdir(MUSIC) if f.lower().endswith((".mp3", ".m4a")))
        if "bg music.mp3" in have:
            return os.path.join(MUSIC, "bg music.mp3")
        if have:
            return os.path.join(MUSIC, have[0])
        root = os.path.dirname(os.path.dirname(self.story))
        for src in (os.path.join(root, "Common", "bg music.mp3"), os.path.join(STORY_ROOT, "Common", "bg music.mp3")):
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(MUSIC, "bg music.mp3"))
                say(f"   music\\ khaali tha -> {src} copy kiya")
                return os.path.join(MUSIC, "bg music.mp3")
        raise Stop("music\\ folder khaali hai aur 'reels story\\Common\\bg music.mp3' bhi nahi mila. Music daalo.")

    def step5(self):
        tmp = os.path.join(self.proj, "render.mp4")
        if os.path.exists(tmp):
            os.remove(tmp)
        d = self.load_data()
        say(f"   render ho raha hai (~{render_minutes(d['END'])} min, laptop par)...")
        rc, _ = run_shell(f'npx --yes hyperframes@{HF_VERSION} render -o "render.mp4" --fps {FPS} --quality high',
                          self.proj)
        if rc or not os.path.exists(tmp):
            raise Stop("hyperframes render fail hua (upar log dekho). Node.js laga hai? Theek karke --from 5.")
        os.makedirs(OUTPUT, exist_ok=True)
        shutil.move(tmp, self.mp4)
        import make_reel as mr
        n_all = d["OFF"] + d["END"]
        subprocess.run([mr.FFMPEG, "-y", "-loglevel", "error", "-i", self.mp4, "-vf",
                        f"fps=16/{n_all:.2f},scale=216:384,tile=8x2", "-frames:v", "1", self.grid])
        self.st.d["grid"] = self.grid
        self.st.done(5, data=md5(self.data))

    def step6(self):
        if self.copy_ok is None:
            self.copy_ok = self.ask_copy()
        if not self.copy_ok:
            raise Stop("Story folder ki purani MP4 nahi chhedi. Nayi reel output\\ mein hai: " + self.mp4)
        shutil.copy2(self.mp4, self.story_mp4)
        shutil.copy2(self.timing_csv, os.path.join(self.story, "timing.csv"))
        say(f"   MP4 + timing.csv -> {self.story}")
        self.st.done(6, data=md5(self.data))

    def ask_copy(self):
        old = [f for f in os.listdir(self.story) if f.lower().endswith(".mp4")] if os.path.isdir(self.story) else []
        if not old:
            return True
        say(f"   Story folder mein pehle se MP4 hai: {', '.join(old)}")
        return ask("   Nayi HF reel story folder mein daal dun? (same naam wali + timing.csv replace hogi)", self.o["yes"])

    def step7(self):
        out = os.path.join(self.story, self.name + " - COVER.png")
        mine = (self.st.d["done"].get("7") or {}).get("cover")
        if os.path.exists(out) and mine != out:
            out = os.path.join(self.story, self.name + " - COVER NEW.png")   # purana cover mat mitao
        rc, _ = run(py("make_cover.py", "one", self.name, out))
        if rc or not os.path.exists(out):
            raise Stop("make_cover fail hua (upar error). --from 7 se dobara chalao.")
        self.st.done(7, data=md5(self.data), cover=out)

    # ---------- chalao ----------
    def plan(self):
        start = self.o["from"]
        if start:
            todo = [n for n in STEPS if n >= start or not self.is_done(n)]
        else:
            todo = [n for n in STEPS if not self.is_done(n)]
            if todo:
                todo = [n for n in STEPS if n >= todo[0]]
        if self.o.get("tak"):
            todo = [n for n in todo if n <= self.o["tak"]]
        return todo

    def go(self):
        todo = self.plan()
        say(f"\n=== {self.name} (HyperFrames) ===\nStory: {self.story}")
        for n, title in STEPS.items():
            later = self.o.get("tak") and n > self.o["tak"]
            say(f"  {n}. {title:38s} {'CHALEGA' if n in todo else 'nahi (--tak)' if later else 'skip (ho chuka)'}")
        if not todo:
            say("\nSab steps pehle se ho chuke. Dobara chahiye to --from <step number> lagao.")
            return True
        if self.o["dry"]:
            say("\n--dry-run: kuch nahi chalaya. Ye commands chalengi:")
            for n in todo:
                say(f"  {n}. " + self.describe(n))
            return True
        if 6 in todo:
            self.copy_ok = self.ask_copy()      # render se pehle hi pooch lo
        if self.o["from"]:
            self.st.undo_from(self.o["from"])
        for n in todo:
            say(f"\n--- STEP {n}: {STEPS[n]} ---")
            getattr(self, f"step{n}")()
        if self.o.get("tak") and self.o["tak"] < max(STEPS):
            say(f"\n--tak {self.o['tak']}: yahin ruk gaye. Aage ke liye:  --from {self.o['tak'] + 1}")
            return True
        self.summary()
        return True

    def describe(self, n):
        q = lambda s: f'"{s}"'
        return {
            1: f"py prep_story.py {q(self.story)}",
            2: f"py -u build_voice.py {q(self.story)} {q(self.name)} {q(THINK_TEXT)} {THINK}  -> voice\\{self.name}.m4a"
               "  (voice pehle se bani ho to skip)",
            3: f"story + shabd ka time -> hyperframes\\{self.name}\\hf_data.json + timing.csv (haath wala DATA ho to poochega)",
            4: f"make_cards options + engine copy -> hyperframes\\{self.name}\\index.html + assets\\ + mix.wav",
            5: f"npx --yes hyperframes@{HF_VERSION} render  -> output\\{self.name} - HF.mp4 + HF CHECK.png",
            6: f"copy output\\{self.name} - HF.mp4 -> story\\{self.name}.mp4 + timing.csv (purani MP4 ho to poochega)",
            7: f"py make_cover.py one {q(self.name)} {q(os.path.join(self.story, self.name + ' - COVER.png'))}",
        }[n]

    def summary(self):
        say("\n===== HF REEL TAIYAAR =====")
        say(f"MP4: {self.story_mp4}")
        if self.st.d.get("grid"):
            say(f"Frame check (ek baar dekho): {self.st.d['grid']}")
        if self.st.d.get("sheet"):
            say(f"Images contact sheet: {self.st.d['sheet']}")
        cover = (self.st.d["done"].get("7") or {}).get("cover")
        if cover:
            say(f"Cover: {cover}")
        say("Yaad rahe: DATA auto DRAFT tha - frame grid mein pose / text / khaali screen zaroor dekho.")


def render_minutes(seconds):
    """laptop andaza: ~10 sec video = 1-1.5 min render (sps.py jaisa)"""
    a, b = (seconds + 1) / 10 * 1.0, (seconds + 1) / 10 * 1.5
    return f"{a:.0f}-{b:.0f}"


def parse_args(argv):
    opts = {"from": None, "tak": None, "dry": "--dry-run" in argv, "force": "--force" in argv, "yes": "--haan" in argv}
    pos, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a in ("--from", "--tak"):
            if i + 1 >= len(argv):
                raise Stop(f"{a} ke baad number do")
            v = argv[i + 1]
            if not v.isdigit() or int(v) not in STEPS:
                raise Stop(f"{a} ke baad 1 se {max(STEPS)} ka number do (diya: {v})")
            opts[a[2:]] = int(v)
            i += 2
            continue
        if not a.startswith("--"):
            pos.append(a)
        i += 1
    if len(pos) < 2:
        raise Stop('Chalao:  py make_full_hf_reel.py "<story folder>" "<NN Title>"   (--dry-run / --from N / --tak N)')
    story = pos[0].strip().strip('"').rstrip("\\/")
    if not os.path.isdir(story) and not opts["dry"]:
        raise Stop(f"Story folder nahi mila: {story}")
    return story, pos[1].strip().strip('"'), opts


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    try:
        story, name, opts = parse_args(list(sys.argv[1:] if argv is None else argv))
        Reel(story, name, opts).go()
        return 0
    except Stop as e:
        say(f"\n!! RUK GAYA: {e}")
        return 1
    except KeyboardInterrupt:
        say("\n!! Band kar diya. Jo step ho chuke wo yaad hain - wahi command dobara chalao.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
