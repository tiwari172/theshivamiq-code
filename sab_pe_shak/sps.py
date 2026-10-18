# SAB PE SHAK reel maker (HyperFrames style)
#   py sps.py SS-001 1      -> ek Part ki reel
#   py sps.py all           -> saare taiyaar Parts
#   py sps.py cover SS-001 1 -> sirf cover
# Saari settings: settings.txt (isi folder mein)
import os, sys, re, glob, json, math, shutil, subprocess, difflib, unicodedata, datetime, html
try:
    import winreg          # sirf Windows par hota hai
except ImportError:
    winreg = None

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECTS = os.path.join(HERE, "projects")
ENGINE_DIR = os.path.join(os.path.dirname(HERE), "hyperframes", "_ENGINE")   # pakka HF engine (README.txt)
HF_VERSION = "0.8.144"
W, H = 1080, 1920


# ============================== settings ==============================
def load_settings():
    S = {}
    with open(os.path.join(HERE, "settings.txt"), encoding="utf-8-sig") as f:
        for line in f:
            if line.lstrip().startswith("#") or "=" not in line:
                continue
            line = re.split(r"\s#\s", line, maxsplit=1)[0]
            k, v = line.split("=", 1)
            S[k.strip()] = v.strip()
    return S


S = load_settings()


def num(k):
    if k not in S:
        sys.exit(f"settings.txt mein '{k} = ...' wali line nahi mili (galti se mit gayi?). Wapas likho.")
    try:
        return float(S[k])
    except ValueError:
        sys.exit(f"settings.txt mein '{k} = {S[k]}' number nahi hai. Sirf number likho (jaise 0.5, comma nahi).")


def yes(k):
    return S.get(k, "").strip().lower() in ("haan", "han", "yes", "y", "1", "true")


for _k in ("series_folder", "excel_file"):
    if _k not in S:
        sys.exit(f"settings.txt mein '{_k} = ...' wali line nahi mili (galti se mit gayi?). Wapas likho.")
SERIES = os.environ.get("SPS_SERIES") or S["series_folder"]  # test ke liye env se badal sakte hain
EXCEL = os.path.join(SERIES, S["excel_file"])
STORY_ROOT = os.path.dirname(SERIES)          # ...\reels story
CODE_ROOT = os.path.dirname(HERE)              # ...\theshivamiq code


def log(*a):
    print(*a, flush=True)


# ============================== tools ==============================
def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    hits = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages",
                                  "Gyan.FFmpeg*", "*", "bin", "ffmpeg.exe"))
    if hits:
        return hits[0]
    return None


def find_ffprobe(ffmpeg):
    if not ffmpeg:
        return None
    for name in ("ffprobe.exe", "ffprobe"):   # Windows / Linux
        p = os.path.join(os.path.dirname(ffmpeg), name)
        if os.path.isfile(p):
            return p
    return shutil.which("ffprobe") or os.path.join(os.path.dirname(ffmpeg), "ffprobe.exe")


FFMPEG = find_ffmpeg()          # na mile to main() mein saaf message
FFPROBE = find_ffprobe(FFMPEG)


def fresh_env():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if winreg is None:     # Linux / Mac: PATH jaisa hai waisa
        return env
    parts = []
    for hive, key in ((winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                      (winreg.HKEY_CURRENT_USER, "Environment")):
        try:
            with winreg.OpenKey(hive, key) as k:
                parts.append(os.path.expandvars(winreg.QueryValueEx(k, "Path")[0]))
        except OSError:
            pass
    env["Path"] = ";".join(parts + [os.path.dirname(FFMPEG), env.get("Path", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def duration_of(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        raise RuntimeError(f"file ki lambai nahi padh paaya (kharab / adhoori file?): {path}") from None


def find_common():
    c = os.environ.get("SPS_COMMON") or S.get("common_folder", "auto")
    if c and c.lower() != "auto":
        return c if os.path.isdir(c) else None
    for base in (SERIES, STORY_ROOT, CODE_ROOT):
        for depth in range(0, 4):
            for d in glob.glob(os.path.join(base, *(["*"] * depth), "_common")):
                if os.path.isdir(d):
                    return d
    return None


def find_file(folders, name, exts):
    for d in folders:
        if not d or not os.path.isdir(d):
            continue
        low = {f.lower(): f for f in os.listdir(d)}
        for e in exts:
            f = low.get((name + e).lower())
            if f:
                return os.path.join(d, f)
    return None


# ============================== excel ==============================
def cell(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def read_sheet(wb, name):
    if name not in wb.sheetnames:
        return [], []
    rows = list(wb[name].iter_rows(values_only=True))
    if not rows:
        return [], []
    return [cell(h) for h in rows[0]], rows[1:]


def col(headers, *starts):
    for st in starts:
        for i, h in enumerate(headers):
            if h.lower().startswith(st.lower()):
                return i
    return None


def at(row, i):
    """row[i], par column na ho ya row chhoti ho to "" (crash nahi)."""
    return cell(row[i]) if i is not None and i < len(row) else ""


def same_part(row, ci, pi, case, part):
    return at(row, ci).upper() == case.upper() and at(row, pi) == str(part)


def load_excel():
    if not os.path.isfile(EXCEL):
        sys.exit(f"Excel nahi mili: {EXCEL}\n(settings.txt mein series_folder / excel_file check karo)")
    try:
        wb = openpyxl.load_workbook(EXCEL, read_only=True, data_only=True)
    except PermissionError:
        sys.exit(f"Excel khul nahi rahi (shayad OneDrive sync / lock): {EXCEL}")
    data = {n: read_sheet(wb, n) for n in ("Edit Timeline", "Scripts", "Cover Design", "Tracker")}
    wb.close()
    return data


def part_list(X):
    hd, rows = X["Edit Timeline"]
    ci, pi = col(hd, "Case"), col(hd, "Part")
    seen = []
    if ci is None or pi is None:
        return seen
    for r in rows:
        k = (at(r, ci), at(r, pi))
        if k[0] and k[1] and k not in seen:
            seen.append(k)
    return seen


def get_shots(X, case, part):
    hd, rows = X["Edit Timeline"]
    c = {k: col(hd, *v) for k, v in {
        "case": ["Case"], "part": ["Part"], "shot": ["Shot"], "start": ["Start"], "end": ["End"], "cue": ["Cue"],
        "png": ["PNG"], "pos": ["Position"], "size": ["Size"], "anim": ["Animation"], "mirror": ["Mirror"],
        "text": ["On-screen"], "ttype": ["Text Type"], "tpos": ["Text Position"], "sfx": ["SFX at", "XXX"],
        "sfxname": ["SFX"], "music": ["Music"], "overlay": ["Overlay"]}.items()}
    c["sfxname"] = next((i for i, h in enumerate(hd) if h.upper() == "SFX"), None)
    shots, level = [], None
    for r in rows:
        if not same_part(r, c["case"], c["part"], case, part):
            continue
        g = lambda k: cell(r[c[k]]) if c[k] is not None and c[k] < len(r) else ""
        try:
            st, en = float(g("start") or 0), float(g("end") or 0)
        except ValueError:
            st, en = 0.0, 0.0
        if g("shot").upper() == "LVL":
            level = {"txt": g("text").upper(), "s": st, "e": en}
            continue
        ids = [a.strip() for a in g("png").split(",") if a.strip() and a.strip().lower() != "none"]
        shots.append({
            "n": g("shot"), "xs": st, "xe": en, "cue": g("cue"), "ids": ids,
            "pos": [p.strip() for p in g("pos").split(",") if p.strip()],
            "size": [p.strip() for p in g("size").split(",") if p.strip()],
            "anim": (g("anim") or "none").lower(), "mirror": [m.strip().lower() for m in g("mirror").split(",")],
            "text": g("text"), "ttype": g("ttype").upper(), "tpos": (g("tpos") or "center").lower(),
            "sfx": g("sfxname"), "sfx_at": g("sfx"), "music": (g("music") or "on").lower(),
            "overlay": (g("overlay") or "none").lower(),
        })
    return shots, level


def get_script(X, case, part):
    hd, rows = X["Scripts"]
    ci, pi = col(hd, "Case"), col(hd, "Part")
    vo, cap, title = col(hd, "Voiceover"), col(hd, "Caption"), col(hd, "Title")
    for r in rows:
        if ci is not None and same_part(r, ci, pi, case, part):
            return at(r, vo), at(r, cap), at(r, title)
    return "", "", ""


def get_cover_row(X, case, part):
    hd, rows = X["Cover Design"]
    ci, pi = col(hd, "Case"), col(hd, "Part")
    for r in rows:
        if ci is not None and same_part(r, ci, pi, case, part):
            return {"title": at(r, col(hd, "Cover Title")), "hook": at(r, col(hd, "Cover Hook")),
                    "badge": at(r, col(hd, "Badge")), "png": at(r, col(hd, "PNG"))}
    return None


# ============================== text helpers ==============================
TAG = re.compile(r"\[[^\]]*\]")


def norm_dev(s):
    s = unicodedata.normalize("NFC", s or "").lower()
    s = s.replace("\u093c", "").replace("\u0901", "\u0902")
    return "".join(ch for ch in s if ("\u0900" <= ch <= "\u097f" and ch not in "\u0964\u0965") or ch.isalnum())


def is_pause(line):
    return re.fullmatch(r"[.\u2026\s]*", line or "") is not None and bool((line or "").strip())


# ============================== whisper + alignment ==============================
def transcribe(voice, cache, prompt):
    key = f"{os.path.getsize(voice)}_{int(os.path.getmtime(voice))}_{S['whisper_model']}"
    if os.path.exists(cache):
        try:
            d = json.load(open(cache, encoding="utf-8"))
        except (OSError, ValueError):
            d = {}          # kharab cache: Whisper dobara chalega
        if d.get("key") == key:
            return d["words"]
    log(f"  Whisper ({S['whisper_model']}) voice sun raha hai... (1-3 min)")
    from faster_whisper import WhisperModel
    m = WhisperModel(S["whisper_model"], device="cpu", compute_type="int8")
    segs, _ = m.transcribe(voice, language="hi", word_timestamps=True, initial_prompt=prompt[:220],
                           condition_on_previous_text=False)
    words = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for sg in segs for w in (sg.words or [])]
    json.dump({"key": key, "words": words}, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    return words


class Align:
    """Script (Devanagari) ke har akshar ko voice ke time se jodta hai."""

    def __init__(self, lines, words, vlen):
        self.lines, self.vlen = lines, vlen
        self.stream, self.line_of, self.line_rng = [], [], []
        for i, ln in enumerate(lines):
            a = len(self.stream)
            t = norm_dev(TAG.sub("", ln))
            self.stream += list(t)
            self.line_of += [i] * len(t)
            self.line_rng.append((a, len(self.stream)))
        tr, ts, te = [], [], []
        for w, a, b in words:
            t = norm_dev(w)
            for k, ch in enumerate(t):
                tr.append(ch)
                ts.append(a + (b - a) * k / len(t))
                te.append(a + (b - a) * (k + 1) / len(t))
        n = len(self.stream)
        self.matched = np.zeros(n, bool)
        ms, me = np.zeros(n), np.zeros(n)
        if n and tr:
            sm = difflib.SequenceMatcher(None, self.stream, tr, autojunk=False)
            for blk in sm.get_matching_blocks():
                if blk.size < 2:
                    continue
                for k in range(blk.size):
                    self.matched[blk.a + k] = True
                    ms[blk.a + k], me[blk.a + k] = ts[blk.b + k], te[blk.b + k]
        self.quality = float(self.matched.mean()) if n else 0.0
        idx = np.nonzero(self.matched)[0]
        allx = np.arange(n)
        if len(idx) >= 2:
            self.ts = np.interp(allx, idx, ms[idx])
            self.te = np.interp(allx, idx, me[idx])
        else:  # alignment nahi hua: seedha lambai ke hisaab se
            self.ts = allx / max(n, 1) * vlen
            self.te = (allx + 1) / max(n, 1) * vlen
        # monotonic
        self.ts = np.maximum.accumulate(self.ts)
        self.te = np.maximum(np.maximum.accumulate(self.te), self.ts)

    def line_times(self, i):
        a, b = self.line_rng[i]
        if a == b:
            return None
        return float(self.ts[a]), float(self.te[b - 1])

    def find_cue(self, cue, start_char):
        t = norm_dev(TAG.sub("", cue))
        if not t:
            return None
        s = "".join(self.stream)
        for L in (len(t), int(len(t) * 0.7), int(len(t) * 0.5)):
            if L < 4:
                break
            k = s.find(t[:L], start_char)
            if k >= 0:
                ok = self.matched[k:k + L].mean() >= 0.4
                return k, ok
        return None

    def word_spans(self, i):
        """Devanagari line i ke shabd: [(start_frac, end_frac, t0, t1)]"""
        a, b = self.line_rng[i]
        raw = TAG.sub("", self.lines[i]).split()
        out, pos = [], a
        for w in raw:
            L = len(norm_dev(w))
            if L == 0:
                continue
            out.append((pos, pos + L))
            pos += L
        return [(float(self.ts[x]), float(self.te[y - 1])) for x, y in out]


# ============================== timing ==============================
def build_timing(shots, al, vlen, n_lines):
    voiced = [s for s in shots if not s["cue"].startswith("(")]
    tail = [s for s in shots if s["cue"].startswith("(")]
    if not voiced:   # saare shots "(...)" wale: pehla shot voice ke saath maan lo
        voiced, tail = tail[:1], tail[1:]
    early = num("cue_early")
    ptr, line_ptr, found = 0, 0, 0
    for k, sh in enumerate(voiced):
        sh["t"] = None
        if k == 0:
            sh["t"], sh["how"] = 0.0, "start"
            continue
        if is_pause(sh["cue"]):
            for j in range(line_ptr + 1, n_lines):
                if is_pause(al.lines[j]):
                    prev = next((al.line_times(q) for q in range(j - 1, -1, -1) if al.line_times(q)), None)
                    if prev:
                        sh["t"], sh["how"] = prev[1] + 0.05, "pause-line"
                        line_ptr = j
                        found += 1
                    break
            continue
        r = al.find_cue(sh["cue"], ptr)
        if not (r and r[1]) and "अमित" in sh["cue"]:   # VO mein "डॉक्टर अमित" ho sakta hai
            r = al.find_cue(sh["cue"].replace("डॉक्टर अमित", "अमित").replace("अमित", "डॉक्टर अमित"), ptr)
        if not (r and r[1]):   # cue ka pichhla hissa
            cw = sh["cue"].split()
            if len(cw) >= 3:
                r2 = al.find_cue(" ".join(cw[len(cw) // 2:]), ptr)
                if r2 and r2[1]:
                    k2 = r2[0]
                    a0 = al.line_rng[al.line_of[k2]][0]
                    r = (a0 if a0 >= ptr else k2, True)
        if r and r[1]:
            k0 = r[0]
            sh["t"], sh["how"] = max(0.0, float(al.ts[k0]) - early), "cue"
            ptr, line_ptr = k0 + 1, al.line_of[k0]
            found += 1
    # anchors se baaki shots ka andaza (Excel time stretch)
    x_end = min([s["xs"] for s in tail] or [max(s["xe"] for s in voiced)])
    ax, ay = [0.0], [0.0]
    for sh in voiced:
        if sh["t"] is not None and sh["t"] > ay[-1] and sh["xs"] > ax[-1]:
            ax.append(sh["xs"]); ay.append(sh["t"])
    ax.append(max(x_end, ax[-1] + 0.1)); ay.append(max(vlen, ay[-1] + 0.1))
    last = 0.0
    for sh in voiced:
        if sh["t"] is None or sh["t"] < last:
            sh["t"], sh["how"] = float(np.interp(sh["xs"], ax, ay)), "andaza (Excel stretch)"
        sh["t"] = max(sh["t"], last)
        last = sh["t"] + 0.2
    for a, b in zip(voiced, voiced[1:]):
        a["s"], a["e"] = a["t"], b["t"]
    voiced[-1]["s"], voiced[-1]["e"] = voiced[-1]["t"], vlen
    t = vlen
    for i, sh in enumerate(tail):
        d = max(0.5, sh["xe"] - sh["xs"]) + (num("tail_extra") if i == len(tail) - 1 else 0)
        sh["s"], sh["e"], sh["how"] = t, t + d, "voice ke baad"
        t += d
    return t, found, len(voiced) - 1


def build_caps(al, cap_lines, total):
    maxw = int(num("subtitle_max_words"))
    out = []
    for i, dev in enumerate(al.lines):
        rom = cap_lines[i].strip() if i < len(cap_lines) else ""
        lt = al.line_times(i)
        if not rom or not lt:
            continue
        rw = rom.split()
        dw = al.word_spans(i)
        if len(dw) == len(rw):
            times = [d[0] for d in dw]
        else:  # akshar ke hisaab se baanto
            cum = np.cumsum([0] + [len(w) + 1 for w in rw])
            frac = cum[:-1] / cum[-1]
            dcum = np.cumsum([0] + [len(norm_dev(x)) for x in TAG.sub("", dev).split() if norm_dev(x)])
            dfrac = dcum / max(dcum[-1], 1)
            dts = [d[0] for d in dw] + [lt[1]]
            times = [float(np.interp(f, dfrac, dts)) for f in frac]
        n = math.ceil(len(rw) / maxw)
        size = math.ceil(len(rw) / n)
        for c in range(n):
            ws = list(zip(rw[c * size:(c + 1) * size], times[c * size:(c + 1) * size]))
            if ws:
                out.append({"s": ws[0][1], "words": [[w, round(t, 3)] for w, t in ws], "line_end": lt[1]})
    for a, b in zip(out, out[1:]):
        a["e"] = min(b["s"], max(a["words"][-1][1] + 0.4, a["line_end"] + 0.35))
    if out:
        out[-1]["e"] = min(total, out[-1]["line_end"] + 0.6)
    for c in out:
        c["s"] = round(c["s"], 3)
        c["e"] = round(max(c["e"], c["s"] + 0.3), 3)
        c.pop("line_end")
    return out


# ============================== images ==============================
def clean_png(src, dst, max_side=1500):
    im = Image.open(src).convert("RGBA")
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    a = np.array(im)
    w_, h_ = im.size
    corners = [a[2, 2], a[2, -3], a[-3, 2], a[-3, -3]]
    is_green = lambda c: c[3] > 250 and int(c[1]) > 150 and int(c[1]) - max(int(c[0]), int(c[2])) > 70
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]).astype(int)
    green_border = ((border[:, 1] > 150) & (border[:, 1] - np.maximum(border[:, 0], border[:, 2]) > 70)).mean()
    if sum(is_green(c) for c in corners) >= 3 or green_border > 0.3:   # close-up mein neeche ke kone coat hote hain
        # hara (green screen) background: jitna zyada hara, utna transparent + kinaron se hari jhalak hatao
        f = a.astype(np.int32)
        spill = f[..., 1] - np.maximum(f[..., 0], f[..., 2])
        alpha = np.clip(255 - (spill - 40) * 255 // 60, 0, 255).astype(np.uint8)
        a[..., 3] = np.minimum(a[..., 3], alpha)
        g = np.where(spill > 0, np.maximum(f[..., 0], f[..., 2]), f[..., 1])
        a[..., 1] = np.clip(g, 0, 255).astype(np.uint8)
        a[..., 3] = np.array(Image.fromarray(a[..., 3]).filter(ImageFilter.MinFilter(3)))
        ch, cw = int(h_ * 0.12), int(w_ * 0.15)   # Gemini ka sitara (neeche right kone mein)
        corner = a[-ch:, -cw:, 3]
        if 0 < (corner > 0).mean() < 0.06:
            a[-ch:, -cw:, 3] = 0
        else:   # sitara kapde ke upar ho (close-up): halke dhabbe ko aas-paas ke rang se bhar do
            reg = a[-int(h_ * 0.2):, -int(w_ * 0.25):]
            rgb = reg[..., :3].astype(int)
            opaque = reg[..., 3] > 0
            ref = np.median(rgb[opaque], axis=0) if opaque.any() else np.zeros(3)
            star = (rgb.mean(-1) - ref.mean() > 30) & (rgb.max(-1) - rgb.min(-1) < 35) & opaque
            if 0 < star.mean() < 0.04:
                med = np.broadcast_to(ref.astype(np.uint8), reg[..., :3].shape)
                star = np.array(Image.fromarray((star * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
                reg[..., :3][star] = med[star]
    elif yes("remove_white_bg") and all(c[3] > 250 and min(c[:3]) > 225 for c in corners):
        rgb = im.convert("RGB")
        key = (1, 254, 3)
        pts = [(0, 0), (w_ - 1, 0), (0, h_ - 1), (w_ - 1, h_ - 1), (w_ // 2, 0), (w_ // 2, h_ - 1), (0, h_ // 2), (w_ - 1, h_ // 2)]
        for p in pts:
            if min(rgb.getpixel(p)) > 215:
                ImageDraw.floodfill(rgb, p, key, thresh=40)
        r = np.array(rgb)
        bgmask = (r[..., 0] == 1) & (r[..., 1] == 254) & (r[..., 2] == 3)
        alpha = np.where(bgmask, 0, 255).astype(np.uint8)
        alpha = np.array(Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)))
        a[..., 3] = np.minimum(a[..., 3], alpha)
        # Gemini ka chhota sitara (neeche right kone mein)
        ch, cw = int(h_ * 0.1), int(w_ * 0.1)
        corner = a[-ch:, -cw:, 3]
        if 0 < (corner > 0).mean() < 0.06:
            a[-ch:, -cw:, 3] = 0
    im = Image.fromarray(a)
    bb = Image.fromarray((a[..., 3] > 12).astype(np.uint8) * 255).getbbox()
    if bb:
        im = im.crop(bb)
    im.save(dst)
    return im.size


def place(img_size, posname, size_pct, is_prop):
    m = re.match(r"\s*([LCR])\s*(?:\(\s*(\d+)\s*%?\s*\))?", posname.upper())
    letter, pct = (m.group(1), m.group(2)) if m else ("C", None)
    x = float(pct) if pct else num("pos_" + letter)
    x = x / 100 * W
    h = size_pct / 100 * H
    w = h * img_size[0] / img_size[1]
    mg = num("edge_margin_px")
    if w > W - 2 * mg:
        w = W - 2 * mg
        h = w * img_size[1] / img_size[0]
    x = min(max(x, mg + w / 2), W - mg - w / 2)
    if is_prop:
        bottom = H - num("prop_center_y") / 100 * H - h / 2
    else:
        bottom = H - num("char_feet_y") / 100 * H
    return round(x), round(bottom), round(w), round(h)


def spread(placed):
    """Ek shot ki kai images ek-doosre ko na kaatein: zaroorat ho to chhota karo aur barabar gap se rakho."""
    if len(placed) < 2:
        return
    mg, gap = num("edge_margin_px"), num("image_gap_px") if "image_gap_px" in S else 30
    placed.sort(key=lambda p: p[1])
    want = sum(p[1] for p in placed) / len(placed)
    total = sum(p[3] for p in placed) + gap * (len(placed) - 1)
    avail = W - 2 * mg
    if total > avail:
        f = (avail - gap * (len(placed) - 1)) / sum(p[3] for p in placed)
        for p in placed:
            prop = is_prop(p[0])
            cy = H - p[2] - p[4] / 2
            p[3], p[4] = round(p[3] * f), round(p[4] * f)
            if prop:
                p[2] = round(H - cy - p[4] / 2)
    for i in range(1, len(placed)):   # baayein se daayein: overlap ho to aage khiskao
        a, b = placed[i - 1], placed[i]
        need = a[1] + a[3] / 2 + gap + b[3] / 2
        if b[1] < need:
            b[1] = need
    left = placed[0][1] - placed[0][3] / 2
    right = placed[-1][1] + placed[-1][3] / 2
    shift = want - (left + right) / 2
    shift = min(max(shift, mg - left), W - mg - right)
    for p in placed:
        p[1] = round(p[1] + shift)


def is_prop(aid):
    return aid.upper().startswith("P_")


# ============================== font / text image ==============================
def font_path(common):
    f = S.get("font_file", "Poppins-Bold.ttf")
    for p in (f, os.path.join(common or "", f), os.path.join(common or "", "fonts", f)):
        if p and os.path.isfile(p):
            return p, True
    return r"C:\Windows\Fonts\arialbd.ttf", False


def draw_text(img, xy, text, font, fill, stroke, stroke_fill, anchor="mm"):
    d = ImageDraw.Draw(img)
    d.text(xy, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill, anchor=anchor)


def fit_font(fp, text, size, maxw, stroke):
    while size > 20:
        f = ImageFont.truetype(fp, size)
        if f.getbbox(text, stroke_width=stroke)[2] <= maxw:
            return f
        size -= 4
    return ImageFont.truetype(fp, size)


def wrap2(fp, text, size, maxw, stroke):
    f = ImageFont.truetype(fp, size)
    if f.getbbox(text, stroke_width=stroke)[2] <= maxw:
        return [text], f
    words = text.split()
    best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        wmax = max(f.getbbox(a, stroke_width=stroke)[2], f.getbbox(b, stroke_width=stroke)[2])
        if best is None or wmax < best[0]:
            best = (wmax, [a, b])
    lines = best[1] if best else [text]
    widest = max(lines, key=lambda s: f.getbbox(s, stroke_width=stroke)[2])
    return lines, fit_font(fp, widest, size, maxw, stroke)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ============================== cover ==============================
ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:[_-][A-Z0-9]+)+\b")


def make_cover(row, part, png_paths, fp, bg_path, out):
    bg = Image.open(bg_path).convert("RGB")
    bg = bg.crop((0, 0, bg.width, int(bg.height * 0.95)))   # kone ka Gemini sitara kaato
    sc = max(W / bg.width, H / bg.height)
    bg = bg.resize((math.ceil(bg.width * sc), math.ceil(bg.height * sc)), Image.LANCZOS)
    l, t = (bg.width - W) // 2, (bg.height - H) // 2
    img = bg.crop((l, t, l + W, t + H)).convert("RGBA")
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shade).rectangle((0, int(H * 0.45), W, H), fill=(0, 0, 0, 70))
    img = Image.alpha_composite(img, shade)

    ids = ID_RE.findall(row["png"].split("(")[0])
    shivam = [i for i in ids if re.match(r"^S2?_?\d", i)]
    props = [i for i in ids if i.startswith("P_")]
    sus = [i for i in ids if i not in shivam and i not in props]

    def load(aid, hfrac):
        p = png_paths.get(aid)
        if not p:
            return None
        im = Image.open(p).convert("RGBA")
        hh = int(H * hfrac)
        return im.resize((max(1, int(im.width * hh / im.height)), hh), Image.LANCZOS)

    for aid in shivam[:1]:   # Shivam peeche, suspects aage
        im = load(aid, 0.60)
        if im is not None:
            if im.width > W * 0.46:   # close-up chehra bahut chauda -> suspects na dhake
                im = im.resize((int(W * 0.46), int(im.height * W * 0.46 / im.width)), Image.LANCZOS)
            img.alpha_composite(im, (min(W - im.width, int(W * 0.80 - im.width / 2)), H - im.height))
    qfont = ImageFont.truetype(fp, 150)
    n = len(sus)
    xs = [0.30] if n == 1 else [0.13 + k * (0.42 / (n - 1)) for k in range(n)]
    floor = int(H * 0.985)
    for aid, xf in zip(sus, xs):
        im = load(aid, 0.45)
        if im is None:
            continue
        maxw = int(W * 0.62 / max(n, 1) * 1.9)   # chaudi image (kutta, leta hua) baaki ko na dhake
        if im.width > maxw:
            im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
        x = int(W * xf - im.width / 2)
        x = min(max(x, -im.width // 4), W - im.width)
        img.alpha_composite(im, (x, floor - im.height))
        qy = min(floor - im.height - 70, int(H * 0.75) - 150)   # "?" peeli patti ke upar hi rahe
        draw_text(img, (x + im.width // 2, qy), "?", qfont, hexrgb("#E53935"), 8, (255, 255, 255))
    for aid in props[:1]:
        im = load(aid, 0.11)
        if im is not None:
            if im.width > W * 0.42:
                im = im.resize((int(W * 0.42), int(im.height * W * 0.42 / im.width)), Image.LANCZOS)
            img.alpha_composite(im, (int(W * 0.40 - im.width / 2), H - im.height - 6))

    stroke = int(num("text_outline_px"))
    f = fit_font(fp, "SAB PE SHAK", 150, W - 100, stroke)
    draw_text(img, (W // 2, int(H * 0.18)), "SAB PE SHAK", f, hexrgb("#E53935"), stroke, (255, 255, 255))
    lines, f = wrap2(fp, row["title"].upper(), 120, W - 120, stroke)
    lh = f.size * 1.08
    y0 = H * 0.30 - lh * (len(lines) - 1) / 2
    for k, ln in enumerate(lines):
        draw_text(img, (W // 2, int(y0 + k * lh)), ln, f, (255, 255, 255), stroke, (17, 17, 17))
    d = ImageDraw.Draw(img)
    hf = fit_font(fp, row["hook"], 66, W - 200, 0)
    tw = hf.getbbox(row["hook"])[2]
    cy = int(H * 0.40)
    d.rectangle((W // 2 - tw // 2 - 50, cy - 62, W // 2 + tw // 2 + 50, cy + 62), fill=hexrgb("#B71C1C"))
    draw_text(img, (W // 2, cy), row["hook"], hf, (255, 255, 255), 0, None)
    badge = row["badge"] or f"SAB PE SHAK \u2022 PART {part}"
    bf = fit_font(fp, badge, 58, W - 220, 0)
    bw = bf.getbbox(badge)[2]
    cy = int(H * 0.75)
    d.rounded_rectangle((W // 2 - bw // 2 - 44, cy - 54, W // 2 + bw // 2 + 44, cy + 54), radius=54,
                        fill=hexrgb("#FFD400"), outline=(17, 17, 17), width=6)
    draw_text(img, (W // 2, cy + 2), badge, bf, (17, 17, 17), 0, None)
    img.convert("RGB").save(out)


# ============================== audio ==============================
def build_audio(voice, music, sfx_list, segs, total, cover, out):
    fmt = "aformat=sample_rates=44100:channel_layouts=stereo"
    ms = int(cover * 1000)
    allt = total + cover
    vv, mv = num("voice_volume") / 100, num("music_volume") / 100
    expr = str(mv)
    for a, b, vol in reversed(segs):
        expr = f"if(between(t,{a + cover:.2f},{b + cover:.2f}),{vol:.3f},{expr})"
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-i", voice, "-stream_loop", "-1", "-i", music]
    fc = (f"[0:a]{fmt},volume={vv},adelay={ms}|{ms},apad[v];"
          f"[1:a]{fmt},atrim=0:{allt:.3f},volume='{expr}':eval=frame,afade=t=out:st={max(0, allt - 1.5):.2f}:d=1.5[m];")
    mix, n = "[v][m]", 2
    for path, t, mx in sfx_list:
        cmd += ["-i", path]
        d = int((t + cover) * 1000)
        cut = f"atrim=0:{mx:.2f},afade=t=out:st={max(0, mx - 0.2):.2f}:d=0.2," if mx else ""
        fc += f"[{n}:a]{fmt},{cut}volume={num('sfx_volume') / 100},adelay={d}|{d}[x{n}];"
        mix += f"[x{n}]"
        n += 1
    fc += f"{mix}amix=inputs={n}:duration=longest:normalize=0,alimiter=limit=0.95[a]"
    cmd += ["-filter_complex", fc, "-map", "[a]", "-t", f"{allt:.3f}", out]
    subprocess.run(cmd, check=True)


# ============================== excel status ==============================
def mark_excel(case, part):
    if not yes("update_excel"):
        return
    try:
        wb = openpyxl.load_workbook(EXCEL)
        if "Story Status" not in wb.sheetnames:
            return
        ws = wb["Story Status"]
        changed = 0
        hdr_row, cols = None, {}
        for r in range(1, 6):
            vals = [cell(c.value).lower() for c in ws[r]]
            if any("video bani" in v for v in vals):
                hdr_row = r
                cols = {v: i + 1 for i, v in enumerate(vals)}
                break
        if not hdr_row:
            return
        cv = next((i for v, i in cols.items() if "video bani" in v), None)
        cc = next((i for v, i in cols.items() if v.startswith("case")), None)
        cp = next((i for v, i in cols.items() if v.startswith("part")), None)
        if cc is None or cv is None:
            return
        for r in range(hdr_row + 1, ws.max_row + 1):
            if cell(ws.cell(r, cc).value).upper() == case.upper() and (cp is None or cell(ws.cell(r, cp).value) == str(part)):
                if cell(ws.cell(r, cv).value).lower() != "haan":
                    ws.cell(r, cv).value = "Haan"
                    changed += 1
        if not changed:     # kuch badla hi nahi to Excel dobara save mat karo
            return
        bk = os.path.join(HERE, "excel_backup")
        os.makedirs(bk, exist_ok=True)
        shutil.copy2(EXCEL, os.path.join(bk, datetime.datetime.now().strftime("%Y%m%d_%H%M%S_") + os.path.basename(EXCEL)))
        wb.save(EXCEL)
        log("  Excel 'Story Status' -> Video bani? = Haan")
    except PermissionError:
        log("  [!] Excel khula hai, 'Story Status' update nahi hua (Excel band karke dobara chalao)")
    except Exception as e:
        log(f"  [!] Excel update nahi hua: {e}")


# ============================== one part ==============================
def part_folder(case, part):
    # "SS-001 Title" mile, "SS-0010 ..." nahi
    hits = [d for d in glob.glob(os.path.join(glob.escape(SERIES), glob.escape(case) + "*")) if os.path.isdir(d)
            and not os.path.basename(d)[len(case):len(case) + 1].isalnum()]
    for d in hits:
        p = os.path.join(d, f"Part {part}")
        if os.path.isdir(p):
            return d, p
    return (hits[0] if hits else None), None


def make_part(X, case, part, report, cover_only=False, render=True):
    log(f"\n=== {case} Part {part} ===")
    miss = []
    common = find_common()
    if not common:   # baaki cheezein bhi check karo taaki poori list ek baar mein mile
        miss.append("_common folder (BG_MAIN, MUSIC_MAIN, Poppins-Bold.ttf, sfx\\) – settings.txt mein common_folder = poora path likho")
        common = os.path.join(SERIES, "_common")
    story_dir, pdir = part_folder(case, part)
    if not pdir:
        report.append(f"{case} P{part}: Part folder nahi mila ({SERIES}\\{case} <Title>\\Part {part})")
        log("  [X] Part folder nahi mila")
        return False
    imgdir, voicedir, viddir = (os.path.join(pdir, x) for x in ("images", "voice", "video"))
    shots, level = get_shots(X, case, part)
    # Part folder mein SHOTS_<case>_P<n>.csv ho to Excel ki Edit Timeline ki jagah wahi (Excel kabhi edit nahi)
    ov = os.path.join(pdir, f"SHOTS_{case}_P{part}.csv")
    if os.path.isfile(ov):
        import csv as _csv
        rows = [r for r in _csv.reader(open(ov, encoding="utf-8-sig")) if r] or [[]]
        shots, level = get_shots({"Edit Timeline": ([cell(h) for h in rows[0]], [tuple(r) for r in rows[1:]])}, case, part)
        log(f"  shots: {os.path.basename(ov)} (Excel ki jagah)")
    vo_text, cap_text, title = get_script(X, case, part)
    cov = get_cover_row(X, case, part)
    # Part folder mein badla hua text ho (jaise "Dr. Amit") to Excel ki jagah wahi
    for fname, which in ((f"VO_{case}_P{part}.txt", "vo"), (f"CAPTION_{case}_P{part}.txt", "cap")):
        fpath = os.path.join(pdir, fname)
        if os.path.isfile(fpath):
            txt = open(fpath, encoding="utf-8-sig").read().replace("\r\n", "\n").strip("\n")
            if which == "vo":
                vo_text = txt
            else:
                cap_text = txt
            log(f"  text: {fname} (Excel ki jagah)")
    if not shots or not vo_text:
        report.append(f"{case} P{part}: Excel mein Edit Timeline / Scripts row nahi mili")
        return False

    png_dirs = [pdir, imgdir, common, os.path.join(common, "images")] + \
        [p.strip() for p in S.get("extra_png_folders", "").split(";") if p.strip()]
    need = []
    for sh in shots:
        need += sh["ids"]
    cover_ids = ID_RE.findall(cov["png"].split("(")[0]) if cov else []
    pngs = {}
    need = [a for a in need if a.upper() != "COVER"]
    for aid in dict.fromkeys(need + cover_ids):
        p = find_file(png_dirs, aid, [".png"])
        if p:
            pngs[aid] = p
        else:
            miss.append(f"PNG {aid}.png")
    voice = find_file([voicedir, pdir], f"VO_{case}_P{part}", [".mp3", ".wav", ".m4a"])
    if not voice:
        miss.append(f"voice VO_{case}_P{part}.mp3 (Part folder mein rakho: {pdir})")
    sfxdir = os.path.join(common, "sfx")
    sfx_need = {}
    for sh in shots:
        if sh["sfx"] and sh["sfx"].lower() != "none":
            p = find_file([sfxdir, common], sh["sfx"].split(":")[0].strip(), [".mp3", ".wav"])
            if p:
                sfx_need[sh["sfx"]] = p
            else:
                miss.append(f"SFX {sh['sfx']} (folder: {sfxdir})")
    bgp = find_file([common], "BG_MAIN", [".png", ".jpg"])
    music = find_file([common, os.path.join(common, "music")], "MUSIC_MAIN", [".mp3", ".wav", ".m4a"])
    cover_bg = next((p for p in (os.path.join(SERIES, S["cover_bg"]), os.path.join(SERIES, "COVER_SS_BG.png"),
                                 os.path.join(SERIES, "_cover", "COVER_SS_BG.png")) if os.path.isfile(p)),
                    os.path.join(SERIES, S["cover_bg"]))
    if not bgp:
        miss.append("BG_MAIN.png (_common)")
    if not music:
        miss.append("MUSIC_MAIN.mp3 (_common)")
    if not os.path.isfile(cover_bg):
        miss.append(f"cover background {cover_bg}")
    fp, font_ok = font_path(common)
    if not font_ok:
        report.append(f"{case} P{part}: (sirf jaankari) Poppins-Bold.ttf nahi mila, Arial Bold lagaya")
    miss = list(dict.fromkeys(miss))
    if cover_only and not cov:
        report.append(f"{case} P{part}: Excel 'Cover Design' sheet mein is Part ki row nahi mili, cover nahi bana")
    if cover_only:
        miss = [m for m in miss if m.startswith("PNG") or m.startswith("cover")]
    if miss:
        report.append(f"{case} P{part}: NAHI BANI, ye nahi mila:\n    - " + "\n    - ".join(miss))
        log("  [X] ye files nahi mili:\n    - " + "\n    - ".join(miss))
        preview_ok = os.environ.get("SPS_PREVIEW") and all(m.startswith("PNG") for m in miss)
        if yes("skip_missing") and not preview_ok:
            return False
        fatal = [m for m in miss if not m.startswith("PNG") and not m.startswith("SFX") and not m.startswith("cover")]
        if fatal and not cover_only:   # voice / BG / music ke bina reel ban hi nahi sakti (crash se pehle ruko)
            return False
        if preview_ok:
            log("  PREVIEW: missing PNG ke bina bana raha hoon")

    if not os.path.isdir(viddir):
        viddir = pdir          # naya layout: reel + cover seedha Part folder mein
    proj = os.path.join(PROJECTS, f"{case}_P{part}")
    adir = os.path.join(proj, "assets")
    os.makedirs(os.path.join(adir, "fonts"), exist_ok=True)

    # ---- cover ----
    cover_out = os.path.join(viddir, f"COVER_{case}_P{part}.png")
    cpng = {}
    for aid in cover_ids:
        if aid in pngs:
            dst = os.path.join(adir, aid + ".png")
            clean_png(pngs[aid], dst)
            cpng[aid] = dst
    if cov and os.path.isfile(cover_bg):
        make_cover(cov, part, cpng, fp, cover_bg, cover_out)
        log(f"  cover: {cover_out}")
    if cover_only:
        return True

    # ---- timing ----
    vlen = duration_of(voice)
    lines = vo_text.split("\n")
    cap_lines = cap_text.split("\n")
    tj = os.path.splitext(voice)[0] + "_timing.json"
    if os.path.isfile(tj) and os.path.getmtime(tj) >= os.path.getmtime(voice) - 60:
        # ElevenLabs ne har akshar ka time diya hai -> Whisper se zyada sahi
        d = json.load(open(tj, encoding="utf-8"))
        words, cur = [], None
        for ch, a, b in zip(d["characters"], d["character_start_times_seconds"], d["character_end_times_seconds"]):
            if ch.isspace():
                if cur:
                    words.append(cur)
                cur = None
            elif cur is None:
                cur = [ch, a, b]
            else:
                cur[0] += ch
                cur[2] = b
        if cur:
            words.append(cur)
        words = [w for w in words if not TAG.fullmatch(w[0])]
        log("  timing: ElevenLabs timing.json")
    else:
        words = transcribe(voice, os.path.join(proj, "whisper.json"), TAG.sub("", vo_text))
    al = Align(lines, words, vlen)
    total, found, nvo = build_timing(shots, al, vlen, len(lines))
    log(f"  voice {vlen:.1f}s, reel {total:.1f}s (+{num('cover_seconds')}s cover) | timing match {al.quality:.0%} | cue mile {found}/{nvo}")
    for sh in shots:
        log(f"    shot {sh['n']:>3}: {sh['s']:6.2f}-{sh['e']:6.2f}  ({sh['how']})  {', '.join(sh['ids'])}")
    if al.quality < 0.35:
        report.append(f"{case} P{part}: Whisper match kam ({al.quality:.0%}) - timing andaze se, reel dhyaan se dekho")

    # ---- images ----
    sizes = {}
    for aid in dict.fromkeys(need):
        if aid in pngs:
            sizes[aid] = clean_png(pngs[aid], os.path.join(adir, aid + ".png"))
    items, prev = [], {}
    for sh in shots:
        cur = {}
        placed = []
        for k, aid in enumerate(sh["ids"]):
            if aid not in sizes:
                continue
            pos = sh["pos"][k] if k < len(sh["pos"]) else (sh["pos"][-1] if sh["pos"] else "C")
            try:
                sz = float(re.sub(r"[^\d.]", "", sh["size"][k] if k < len(sh["size"]) else sh["size"][-1]))
            except (ValueError, IndexError):
                sz = 35 if is_prop(aid) else 55
            mir = (sh["mirror"][k] if k < len(sh["mirror"]) else sh["mirror"][0]) in ("yes", "y", "haan")
            x, bottom, w, h = place(sizes[aid], pos, sz, is_prop(aid))
            pcap = W * (0.28 if len(sh["ids"]) >= 3 else 0.4)
            if is_prop(aid) and len(sh["ids"]) > 1 and w > pcap:   # saath mein character ho to prop chhota (log bade rahein)
                f = pcap / w
                w, h = round(w * f), round(h * f)
                bottom = round(H - num("prop_center_y") / 100 * H - h / 2)
            placed.append([aid, x, bottom, w, h, mir])
        spread(placed)
        for aid, x, bottom, w, h, mir in placed:
            key = (aid, x, bottom, w, mir)
            it = prev.get(key)
            if it and abs(it["e"] - sh["s"]) < 0.05:
                it["e"] = sh["e"]          # wahi image agle shot mein bhi: dobara pop nahi
            else:
                it = {"file": aid + ".png", "x": x, "bottom": bottom, "w": w, "h": h, "mirror": mir,
                      "prop": is_prop(aid), "s": sh["s"], "e": sh["e"],
                      "anim": sh["anim"] if sh["anim"] in ("pop-in", "fade", "none", "rise", "left", "right", "drop", "pop") else "pop-in",
                      "zooms": [], "shakes": [], "punches": []}
                if sh["anim"] in ("zoom-in", "shake"):
                    it["anim"] = "pop-in" if sh["anim"] == "shake" else "fade"
                items.append(it)
            if sh["anim"] == "zoom-in":
                it["zooms"].append([sh["s"], sh["e"]])
            if sh["anim"] == "shake":
                it["shakes"].append(sh["s"])
            if sh["anim"] == "punch":      # zaroori shabd par 1.0 -> 1.12 punch-in (same image chalti rahe)
                it["punches"].append(sh["s"])
            cur[key] = it
        prev = cur
    for it in items:
        it["s"], it["e"] = round(it["s"], 3), round(it["e"], 3)

    # ---- on-screen text + suspects (engine T) ----
    stroke = num("text_outline_px")
    colors = {"normal": S["color_normal"], "clue": S["color_clue"], "twist": S["color_twist"]}
    ypos = {"top": num("text_y_top"), "center": num("text_y_center"), "bottom": num("text_y_bottom")}
    texts, suspects, glitch = [], [], None
    for sh in shots:
        if not sh["text"]:
            continue
        tt = sh["ttype"]
        parts = [html.escape(p.strip()) for p in re.split(r"\s*\|\s*|\\n|\n", sh["text"]) if p.strip()]
        if tt == "NAME":
            suspects.append(["", "<br>".join(parts), round(sh["s"], 3), round(sh["e"], 3)])
            continue
        if tt == "GLITCH":   # kaala glitch screen + text (engine T.glitch)
            glitch = [round(sh["s"], 3), round(sh["e"], 3), " ".join(parts)]
            if "cover" in sh["ids"] or "COVER" in sh["ids"]:   # PNG column mein "COVER" likho to peeche cover image
                glitch.append("assets/cover.png")
            continue
        size = num("size_" + tt) if ("size_" + tt) in S else num("size_other")
        yf = min(max(ypos.get(sh["tpos"], ypos["center"]), num("safe_top") + 4), 100 - num("safe_bottom") - 4)
        kind = {"HOOK": "hook", "CLUE": "clue", "TWIST": "twist", "CTA": "cta", "SIGN": "cta"}.get(tt, "plain")
        t0 = sh["s"] + (0.05 if kind in ("hook", "twist") else 0.1)
        texts.append(["<br>".join(parts), round(t0, 3), round(sh["e"], 3), kind, round(yf / 100 * H), size])

    caps = build_caps(al, cap_lines, total) if yes("subtitle_on") else []
    P = []
    for c in caps:
        ws = c["words"]
        P.append([[w, t if yes("subtitle_word_pop") else c["s"],
                   round(ws[k + 1][1] if k + 1 < len(ws) else c["e"], 3)] for k, (w, t) in enumerate(ws)])

    # ---- music / sfx / overlay ----
    segs, pauses = [], []
    for sh in shots:
        if sh["music"] == "off":
            segs.append((sh["s"], sh["e"], 0.0))
            pauses.append([round(sh["s"], 3), round(sh["e"], 3)])
        elif sh["music"] == "duck":
            segs.append((sh["s"], sh["e"], num("music_duck") / 100))
    sfx_list = []
    for sh in shots:
        if sh["sfx"] in sfx_need:
            try:
                off = float(sh["sfx_at"]) - sh["xs"]
            except ValueError:
                off = 0.0
            mx = sh["sfx"].split(":")[1] if ":" in sh["sfx"] else ""   # "SFX_RISER:0.9" = sirf 0.9 sec bajao
            try:
                mx = float(mx) if mx.strip() else 0
            except ValueError:
                mx = 0
            sfx_list.append((sfx_need[sh["sfx"]], max(sh["s"], sh["s"] + off), mx))
    cover_sec = num("cover_seconds") if os.path.isfile(cover_out) else 0.0
    overlays, ov_html, ovdir = [], "", os.path.join(common, "overlays")
    op = num("overlay_opacity") / 100
    for sh in shots:
        kind = sh["overlay"]
        if kind not in ("night", "fog"):
            continue
        src = find_file([ovdir], kind, [".png"] if kind == "night" else [".mp4"])
        if not src:
            log(f"  (overlay {kind} file nahi mili, skip)")
            continue
        if kind == "night":
            if "nightimg" not in ov_html:
                shutil.copy2(src, os.path.join(adir, "night.png"))
                ov_html += '<img id="nightimg" src="assets/night.png" alt="" />\n'
            overlays.append(["nightimg", round(sh["s"], 3), round(sh["e"], 3), op])
        else:
            shutil.copy2(src, os.path.join(adir, "fog.mp4"))
            fid = f"fog{len(overlays)}"
            ov_html += (f'<video id="{fid}" class="fog clip" src="assets/fog.mp4" data-start="{sh["s"] + cover_sec:.3f}" '
                        f'data-duration="{sh["e"] - sh["s"]:.3f}" data-track-index="{2 + len(overlays)}" muted playsinline></video>\n')
            overlays.append([fid, round(sh["s"], 3), round(sh["e"], 3), op])

    # ---- assets ----
    shutil.copy2(bgp, os.path.join(adir, "BG_MAIN.png"))
    shutil.copy2(fp, os.path.join(adir, "fonts", "MAIN.ttf"))
    shutil.copy2(os.path.join(ENGINE_DIR, "template", "LOGO_ROUND.png"), os.path.join(adir, "LOGO_ROUND.png"))
    if cover_sec:
        shutil.copy2(cover_out, os.path.join(adir, "cover.png"))
    else:
        Image.new("RGB", (W, H), "black").save(os.path.join(adir, "cover.png"))
    log("  audio mix bana raha hoon...")
    build_audio(voice, music, sfx_list, segs, total, cover_sec, os.path.join(adir, "mix.wav"))

    # ---- engine DATA (hyperframes\_ENGINE\shivam_engine.html) ----
    scenes = []
    for it in sorted(items, key=lambda i: not i["prop"]):   # prop peeche, character aage
        sc = {"img": it["file"][:-4], "s": it["s"], "e": it["e"], "bottom": it["bottom"], "x": it["x"],
              "enter": {"pop-in": "popin"}.get(it["anim"], it["anim"])}
        if it["punches"]:
            sc["punch"] = [round(t, 3) for t in it["punches"]]
        if it["w"] >= W - 2 * num("edge_margin_px") - 1:
            sc["w"] = it["w"]
        else:
            sc["h"] = it["h"]
        if it["mirror"]:
            sc["mirror"] = True
        if it["zooms"]:
            sc["zoom"] = [[round(a, 3), round(b, 3)] for a, b in it["zooms"]]
        if it["shakes"]:
            sc["shake"] = [round(t, 3) for t in it["shakes"]]
        scenes.append(sc)
    T = {"texts": texts, "suspects": suspects, "pauses": pauses, "overlays": overlays,
         "level": [level["txt"] or "LEVEL", 0.2, round(total, 3)] if (level and yes("level_badge")) else None,
         "glitch": glitch}
    CFG = {"cover": cover_sec, "capTop": round(num("subtitle_y") / 100 * H - 150), "capSize": num("subtitle_size"),
           "stroke": stroke * 2, "levelTop": round(num("safe_top") / 100 * H + 8),
           "nameTop": round(num("name_y") / 100 * H) if "name_y" in S else round(num("text_y_top") / 100 * H - 45), "hdrTop": round(num("safe_top") / 100 * H + 90),
           "punch": 1.045 if yes("camera_punch") else 0, "floatPx": 12 if yes("float_idle") else 0,
           "pop": {"t1": num("pop_peak_time"), "t2": num("pop_end_time"), "peak": num("pop_peak_scale") / 100},
           "zoom": num("zoom_end") / 100, "fade": num("fade_time"), "shake": num("shake_time"), "shakePx": num("shake_px"),
           "colors": colors, "activeWord": yes("subtitle_active_word")}
    # Part folder mein EXTRA_<case>_P<n>.json ho to engine T/CFG mein jod do (chips, crime, soch, stamps, night, black, phone ...)
    xp = os.path.join(pdir, f"EXTRA_{case}_P{part}.json")
    if os.path.isfile(xp):
        xt = json.load(open(xp, encoding="utf-8-sig"))
        for k, v in xt.get("T", {}).items():
            T[k] = (T.get(k) or []) + v if isinstance(v, list) and isinstance(T.get(k), list) and k not in ("crime", "hook", "solved", "dhyaan", "caseChip", "options", "ctaPill") else v
        CFG.update(xt.get("CFG", {}))
        log(f"  extra: {os.path.basename(xp)}")
    js = lambda o: json.dumps(o, ensure_ascii=False)
    data = (f"const OFF = {cover_sec};\n      const END = {total:.3f};\n      const CASE = {js(case)};\n"
            f"      const SCENES = {js(scenes)};\n      const P = {js(P)};\n      const T = {js(T)};\n      const CFG = {js(CFG)};")
    eng = open(os.path.join(ENGINE_DIR, "shivam_engine.html"), encoding="utf-8").read()
    dur = f"{total + cover_sec:.3f}"
    page = (eng.replace("__TITLE__", f"{case} P{part} {title}").replace("__DUR__", dur)
            .replace("__MEDIA__", "").replace("__OVERLAYS__", ov_html).replace("__DATA__", data))
    open(os.path.join(proj, "index.html"), "w", encoding="utf-8").write(page)
    for f in ("hyperframes.json", "package.json"):
        if not os.path.exists(os.path.join(proj, f)):
            shutil.copy2(os.path.join(ENGINE_DIR, "template", f), os.path.join(proj, f))
    if not render:
        log(f"  project taiyaar: {proj}")
        return True

    # ---- render ----
    tmp_out = os.path.join(proj, "render.mp4")
    log(f"  render ho raha hai (~{(total + 1) / 10 * 1.0:.0f}-{(total + 1) / 10 * 1.5:.0f} min)...")
    r = subprocess.run(f'npx --yes hyperframes@{HF_VERSION} render -o "{tmp_out}" --fps {int(num("fps"))} --quality high',
                       cwd=proj, shell=True, env=fresh_env())
    if r.returncode != 0 or not os.path.isfile(tmp_out):
        report.append(f"{case} P{part}: render fail hua (upar ka error dekho)")
        return False
    final = os.path.join(viddir, f"REEL_{case}_P{part}{'_PREVIEW' if os.environ.get('SPS_PREVIEW') else ''}.mp4")
    br = num("bitrate_mbps")
    enc = os.path.join(proj, "final_tmp.mp4")   # pehle yahan banao; fail ho to purani reel jaisi thi waisi rahe
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp_out, "-c:v", "libx264", "-preset", "medium",
                    "-b:v", f"{br:g}M", "-maxrate", f"{br + 2:g}M", "-bufsize", f"{br * 2:g}M", "-pix_fmt", "yuv420p",
                    "-r", f"{int(num('fps'))}", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", enc], check=True)
    if os.path.exists(final):
        shutil.move(final, os.path.join(viddir, f"REEL_{case}_P{part}_purana.mp4"))
    shutil.move(enc, final)
    # check grid
    grid = os.path.join(proj, "CHECK.png")
    n_all = total + cover_sec
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", final, "-vf",
                    f"fps=20/{n_all:.2f},scale=216:384,tile=10x2", "-frames:v", "1", grid])
    log(f"  BAN GAYI: {final}  ({duration_of(final):.1f}s)")
    if not os.environ.get("SPS_PREVIEW"):
        mark_excel(case, part)
    return True


# ============================== main ==============================
def write_report(report):
    p = os.path.join(SERIES, "missing_report.txt")
    stamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    body = "\n".join(report) if report else "Sab theek – kuch missing nahi."
    try:
        open(p, "w", encoding="utf-8").write(f"MISSING REPORT ({stamp})\n{'=' * 40}\n{body}\n")
        log(f"\nreport: {p}")
    except OSError:
        p = os.path.join(HERE, "missing_report.txt")
        open(p, "w", encoding="utf-8").write(f"MISSING REPORT ({stamp})\n{body}\n")
        log(f"\nreport: {p}")


USAGE = "Use:  py sps.py SS-001 1   |   py sps.py all   |   py sps.py cover SS-001 1"


def main(argv):
    if not argv or (argv[0].lower() in ("cover", "project") and len(argv) < 2):
        sys.exit(USAGE)
    if not FFMPEG:
        sys.exit("FFmpeg nahi mila. PowerShell mein chalao:  winget install Gyan.FFmpeg")
    X = load_excel()
    report = []
    if argv[0].lower() == "all":
        done = 0
        for case, part in part_list(X):
            _, pdir = part_folder(case, part)
            fins = [os.path.join(pdir or "", sub, f"REEL_{case}_P{part}.mp4") for sub in ("video", "")]
            if pdir and yes("make_all_skip_done") and any(os.path.isfile(f) for f in fins):
                log(f"{case} P{part}: pehle se bani hai, skip")
                continue
            try:   # ek Part ki galti se baaki Parts na rukein
                done += make_part(X, case, part, report)
            except Exception as e:
                log(f"  [X] {case} P{part}: {type(e).__name__}: {e}")
                report.append(f"{case} P{part}: beech mein galti - {type(e).__name__}: {e}")
        log(f"\n{done} reel(s) bani.")
    elif argv[0].lower() == "cover":
        make_part(X, argv[1].upper(), argv[2] if len(argv) > 2 else "1", report, cover_only=True)
    elif argv[0].lower() == "project":
        make_part(X, argv[1].upper(), argv[2] if len(argv) > 2 else "1", report, render=False)
    else:
        make_part(X, argv[0].upper(), argv[1] if len(argv) > 1 else "1", report)
    write_report(report)


if __name__ == "__main__":
    main(sys.argv[1:])
