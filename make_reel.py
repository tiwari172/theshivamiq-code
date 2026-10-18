# theshivamiq – Reel Maker
# CSV + PNG + voice  ->  1080x1920 30fps MP4
#
# Chalane ka tareeka:
#   python make_reel.py              -> cases\ folder ki har CSV ki reel (jo pehle se bani nahi)
#   python make_reel.py 01-001       -> sirf ek case
#   python make_reel.py --redo       -> sab dobara banao (purani MP4 overwrite)
#   --force                          -> check_reel ki PROBLEM ke bawajood render karo
# Render se pehle check_reel.py apne aap chalta hai; render ke baad output\<case> - CHECK.png grid banti hai.

import csv, glob, math, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

# ================== SETTINGS (yahan badal sakte ho) ==================
W, H, FPS = 1080, 1920, 30
BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
VOICE = os.path.join(BASE, "voice")
MUSIC = os.path.join(BASE, "music")
CASES = os.path.join(BASE, "cases")
OUTPUT = os.path.join(BASE, "output")
SFX = os.path.join(BASE, "sfx")
BG_FILE = os.path.join(ASSETS, "BG_MAIN.png")

FONT_FILE = r"C:\Windows\Fonts\ariblk.ttf"   # channel ka ek hi font
FONT_SIZE = 72
TEXT_STROKE = 8                               # black outline ki motai
TEXT_MAX_WIDTH = 940

SAFE_TOP = int(H * 0.15)       # upar 15% khali
SAFE_BOTTOM = int(H * 0.80)    # neeche 20% khali
TEXT_TOP = SAFE_TOP + 20       # text yahan se shuru
CHAR_TOP = 620                 # character ka sir isse upar nahi jayega (text ki jagah)

POP_TIME = 0.25                # pop-in: 0% -> 108% -> 100%
POP_PEAK = 1.08
# Popup style: CSV mein ek line  STYLE,0,1,,,rise  likho to us reel mein naya popup
#   pop  = beech se bada ho kar aata hai (story 1 wala)
#   rise = neeche se uchhal kar upar aata hai
#   slide = side se phisal kar aata hai (baari baari daayen / baayen se)
POP_STYLE = "pop"
POP_STYLES = ("pop", "rise", "slide")
SLIDE_TIME = 0.35
SLIDE_FROM = 700               # slide: itne pixel side se aata hai
RISE_TIME = 0.35
RISE_FROM = 0.6                # rise: 60% size se shuru
RISE_DROP = 180                # rise: itne pixel neeche se aata hai
OUT_TIME = 0.12                # jaate waqt chhota ho kar gayab
DEFAULT_SIZE = 55              # character ki height, screen height ka %
MAX_CHARS_ON_SCREEN = 3

MUSIC_BELOW_VOICE = 12         # music voice se itne dB dheema (kam number = music tez)
MUSIC_DUCK = True              # Shivam bolte waqt music apne aap thoda dab jaaye
VOICE_VOLUME = 1.0
SFX_VOLUME = 0.35              # sound effects ki awaaz
MUSIC_FADE_OUT = 0.3           # end par music kitni der mein band ho (chhota = loop achha lagta hai)
FOCUS_ZOOM = 3.0               # 'focus' effect: kitna paas jaana hai
FOCUS_TIME = 0.8               # 'focus' effect: kitni der mein paas pahunche
FOCUS_TARGET = (540, 1100)     # focus wali jagah screen par yahan aa jayegi
COLORS = {"white": "white", "yellow": (255, 214, 0), "red": (235, 40, 40)}
NIGHT_COLOR = (8, 20, 70)      # night overlay ka rang (neela)
NIGHT_STRENGTH = 0.40
WEATHER_COUNT = {"rain": 160, "snow": 110}   # 'rain' / 'snow' effect: kitni boondein / flakes
ZOOM_END = 1.12               # 'zoom' effect: shot ke end tak 112%
AUTO_PUNCH = True              # har naye scene par halka "camera punch" transition (False = band)
PUNCH_ZOOM = 1.07              # punch: shuru mein 107% se 100% par aata hai
PUNCH_TIME = 0.22
FLASH_TIME = 0.25             # 'flash' effect (transition): safed chamak kitni der
FLASH_STRENGTH = 0.85
BG_FADE = 0.3                  # 'bg' effect: poori screen wali image kitni der mein aaye / jaaye
BG_CROP_BOTTOM = 0.12          # 'bg' effect: neeche ka itna hissa kaat do (kone ka watermark hatane ke liye)
BG_ZOOM = 1.08                 # 'bg' effect: shot ke end tak dheere se 108%
POSITIONS = {"left": 0.28, "center": 0.50, "right": 0.72}
EDGE_MARGIN = 40               # image screen ke side kinaron se kam se kam itni door (chaudi image apne aap chhoti)
# ====================================================================


def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    pattern = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet",
                           "Packages", "Gyan.FFmpeg*", "*", "bin", "ffmpeg.exe")
    hits = glob.glob(pattern)
    if hits:
        return hits[0]
    sys.exit("FFmpeg nahi mila. PowerShell mein chalao: winget install Gyan.FFmpeg")


FFMPEG = find_ffmpeg()
FFPROBE = os.path.join(os.path.dirname(FFMPEG), "ffprobe.exe")


def audio_duration(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(out.stdout.strip())


def mean_db(path):
    """file ki average awaaz (dB)"""
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path, "-vn", "-af", "volumedetect",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    for line in err.splitlines():
        if "mean_volume:" in line:
            return float(line.split("mean_volume:")[1].split()[0])
    return -20.0


def find_file(folder, name, exts):
    for e in exts:
        p = os.path.join(folder, name + e)
        if os.path.exists(p):
            return p
    return None


# ---------- animation curves ----------
def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_back(x):
    """thoda aage nikal kar wapas aata hai (uchhal)"""
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def pop_offset(t):
    """popup ke waqt kitna neeche hai (sirf 'rise' style mein)"""
    if POP_STYLE != "rise" or t >= RISE_TIME:
        return 0
    return int(RISE_DROP * (1 - ease_back(max(0.0, t) / RISE_TIME)))


def pop_shift(t, side=1):
    """popup ke waqt kitna side mein hai (sirf 'slide' style mein). side = 1 daayen, -1 baayen"""
    if POP_STYLE != "slide" or t >= SLIDE_TIME:
        return 0
    return int(side * SLIDE_FROM * (1 - ease_back(max(0.0, t) / SLIDE_TIME)))


def pop_scale(t):
    """t = shot shuru hone ke baad ka time"""
    if POP_STYLE == "slide":
        return 1.0 if t >= 0 else 0.0
    if POP_STYLE == "rise":
        if t >= RISE_TIME:
            return 1.0
        return RISE_FROM + (1 - RISE_FROM) * ease_back(max(0.0, t) / RISE_TIME)
    if t >= POP_TIME:
        return 1.0
    x = t / POP_TIME
    split = 0.65
    if x < split:
        return POP_PEAK * ease_out(x / split)
    return POP_PEAK + (1.0 - POP_PEAK) * ease_out((x - split) / (1 - split))


def out_scale(time_left):
    if OUT_TIME <= 0 or time_left >= OUT_TIME:
        return 1.0
    return max(0.0, time_left / OUT_TIME)


# ---------- CSV ----------
def read_csv(path):
    global POP_STYLE
    POP_STYLE = "pop"
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            r = {k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
            if not r.get("start") and not r.get("asset_id"):
                continue
            if r.get("asset_id", "").upper() == "STYLE":
                POP_STYLE = (r.get("text") or "pop").lower()
                if POP_STYLE not in POP_STYLES:
                    sys.exit(f"CSV line {i}: STYLE '{POP_STYLE}' galat hai. {' / '.join(POP_STYLES)} likho.")
                continue
            try:
                row = {
                    "line": i,
                    "asset": r.get("asset_id", ""),
                    "start": float(r["start"]),
                    "end": float(r["end"]),
                    "pos": (r.get("position") or "center").lower(),
                    "size": float(r.get("size") or DEFAULT_SIZE),
                    "text": r.get("text", "").replace("\\n", "\n"),
                    "effects": [e.strip().lower() for e in r.get("effect", "").split("+") if e.strip()],
                    # naye (optional) columns
                    "sfx": r.get("sfx", "").lower(),
                    "color": (r.get("color") or "white").lower(),
                    "focus": tuple(float(v) for v in r["focus"].split(";")) if r.get("focus") else (0.5, 0.3),
                    # sirf text wali line mein 'size' = font size
                    "font": float(r["size"]) if r.get("size") and not r.get("asset_id") else FONT_SIZE,
                }
            except (KeyError, ValueError) as e:
                sys.exit(f"CSV line {i} mein galti hai ({e}). start/end number hone chahiye.")
            if row["end"] <= row["start"]:
                sys.exit(f"CSV line {i}: end ({row['end']}) start ({row['start']}) se bada hona chahiye.")
            if row["pos"] not in POSITIONS:
                sys.exit(f"CSV line {i}: position '{row['pos']}' galat hai. left / center / right likho.")
            if row["color"] not in COLORS:
                sys.exit(f"CSV line {i}: color '{row['color']}' galat hai. {' / '.join(COLORS)} likho.")
            rows.append(row)
    return rows


# ---------- images ----------
_img_cache = {}


def load_asset(asset_id, size_pct):
    key = (asset_id, size_pct)
    if key in _img_cache:
        return _img_cache[key]
    path = find_file(ASSETS, asset_id, [".png", ".PNG"])
    im = Image.open(path).convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    touches_bottom = bbox and bbox[3] >= im.height - 2   # adha-cut (bust) image
    if bbox:
        im = im.crop(bbox)
    h = int(H * size_pct / 100)
    h = min(h, (H if touches_bottom else SAFE_BOTTOM) - CHAR_TOP)   # text se takraye nahi
    w = int(im.width * h / im.height)
    if w > W - 2 * EDGE_MARGIN:     # bahut chaudi image -> kinaron se thoda andar fit
        w = W - 2 * EDGE_MARGIN
        h = int(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    _img_cache[key] = (im, touches_bottom)
    return _img_cache[key]


class Layer:
    def __init__(self, row):
        self.asset = row["asset"]
        self.pos = row["pos"]
        self.size = row["size"]
        self.start = row["start"]
        self.end = row["end"]
        self.effects = set(row["effects"])
        self.focus = row["focus"]
        self.pop = "nopop" not in self.effects    # False agar pichhle shot ka continuation hai
        self.leave = "noout" not in self.effects  # False agar agla shot isi ka continuation hai


def build_layers(rows):
    layers = []
    for r in rows:
        if not r["asset"] or "bg" in r["effects"]:
            continue
        L = Layer(r)
        L.side = 1 if len(layers) % 2 == 0 else -1     # 'slide' mein baari baari daayen / baayen se
        for prev in layers:   # same image lagatar -> dobara pop mat karo
            if (prev.asset == L.asset and prev.pos == L.pos and prev.size == L.size
                    and abs(prev.end - L.start) < 0.01):
                prev.leave = False
                L.pop = False
        layers.append(L)
    return layers


def draw_layer(frame, L, t, top_limit=0):
    """top_limit = text ke neeche ki line; image isse upar nahi jayegi"""
    base, bust = load_asset(L.asset, L.size)
    s = pop_scale(t - L.start) if L.pop else 1.0
    if L.leave:
        s *= out_scale(L.end - t)
    if "zoom" in L.effects:
        prog = (t - L.start) / (L.end - L.start)
        s *= 1 + (ZOOM_END - 1) * min(1, max(0, prog))
    if s <= 0.01:
        return
    cx = int(W * POSITIONS[L.pos])
    half_w = base.width * s / 2           # left/right par chaudi image screen se bahar na jaaye
    cx = int(min(max(cx, EDGE_MARGIN + half_w), W - EDGE_MARGIN - half_w)) if half_w < W / 2 - EDGE_MARGIN else W // 2
    bottom = H if bust else SAFE_BOTTOM
    cy = bottom - base.height // 2          # image ka center (100% par)
    if L.pop:
        cy += pop_offset(t - L.start)
        cx += pop_shift(t - L.start, L.side)
    if "focus" in L.effects:                # image ki ek jagah (jaise chehra) par paas jao
        k = ease_out(min(1, max(0, (t - L.start) / FOCUS_TIME)))
        fx, fy = L.focus
        px0 = cx - base.width / 2 + fx * base.width
        py0 = cy - base.height / 2 + fy * base.height
        px = px0 + (FOCUS_TARGET[0] - px0) * k
        py = py0 + (FOCUS_TARGET[1] - py0) * k
        s *= 1 + (FOCUS_ZOOM - 1) * k
        im = base.resize((max(1, int(base.width * s)), max(1, int(base.height * s))), Image.BILINEAR)
        py = max(py, top_limit + fy * im.height)       # zoom mein bhi text ke neeche raho
        paste(frame, im, int(px - fx * im.width), int(py - fy * im.height))
        return
    half = base.height * s / 2
    if cy - half < top_limit:               # text se takra rahi hai -> neeche se chipka kar chhota karo
        bottom_now = cy + half
        s = max(0.05, (bottom_now - top_limit) / base.height)
        cy = int(bottom_now - base.height * s / 2)
    if abs(s - 1) > 0.001:
        im = base.resize((max(1, int(base.width * s)), max(1, int(base.height * s))), Image.BILINEAR)
    else:
        im = base
    paste(frame, im, cx - im.width // 2, cy - im.height // 2)


def paste(frame, im, x, y):
    # alpha_composite negative ya bahar ke coordinates nahi leta -> crop kar do
    l, t = max(0, -x), max(0, -y)
    r, b = min(im.width, W - x), min(im.height, H - y)
    if r > l and b > t:
        frame.alpha_composite(im.crop((l, t, r, b)), (x + l, y + t))


# ---------- text ----------
_font = None
_text_cache = {}


def wrap(text, font, draw):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            test = (cur + " " + w).strip()
            if draw.textlength(test, font=font) <= TEXT_MAX_WIDTH:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def text_image(text, font_size=FONT_SIZE, color="white"):
    global _font
    key = (text, font_size, color)
    if key in _text_cache:
        return _text_cache[key]
    size = int(font_size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    while True:
        _font = ImageFont.truetype(FONT_FILE, size)
        lines = wrap(text, _font, tmp)
        widest = max(tmp.textlength(l, font=_font) for l in lines)
        if widest <= TEXT_MAX_WIDTH or size <= 40:
            break
        size -= 4
    line_h = int(size * 1.25)
    pad = TEXT_STROKE + 6
    im = Image.new("RGBA", (W, line_h * len(lines) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((W // 2, pad + i * line_h), l, font=_font, fill=COLORS[color], anchor="ma",
               stroke_width=TEXT_STROKE, stroke_fill="black")
    im = im.crop(im.getchannel("A").getbbox())
    _text_cache[key] = im
    return im


TEXT_GAP_BELOW = 30            # text aur character ke beech kam se kam itni jagah


def text_bottom(rows, t):
    """is waqt ka saara text kahan tak neeche jaata hai (0 = koi text nahi)"""
    y, any_text = TEXT_TOP, False
    for r in rows:
        if r["text"] and r["start"] <= t < r["end"]:
            y += text_image(r["text"], r["font"], r["color"]).height + 20
            any_text = True
    return y - 20 + TEXT_GAP_BELOW if any_text else 0


def draw_texts(frame, rows, t):
    y = TEXT_TOP
    for r in rows:
        if not r["text"] or not (r["start"] <= t < r["end"]):
            continue
        im = text_image(r["text"], r["font"], r["color"])
        s = (pop_scale(t - r["start"]) if "nopop" not in r["effects"] else 1) * \
            (out_scale(r["end"] - t) if "noout" not in r["effects"] else 1)
        if s <= 0.01:
            y += im.height + 20
            continue
        if abs(s - 1) > 0.001:
            sim = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
        else:
            sim = im
        cx, cy = W // 2, y + im.height // 2
        if "nopop" not in r["effects"]:
            cy += pop_offset(t - r["start"]) // 3      # text thoda kam uchhalta hai
            cx -= pop_shift(t - r["start"])            # text ulti taraf se aata hai
        paste(frame, sim, cx - sim.width // 2, cy - sim.height // 2)
        y += im.height + 20


# ---------- poori screen wali background image ('bg' effect) ----------
_bg_cache = {}


def load_bg(asset_id):
    if asset_id not in _bg_cache:
        im = Image.open(find_file(ASSETS, asset_id, [".png", ".PNG", ".jpg"])).convert("RGBA")
        im = im.crop((0, 0, im.width, int(im.height * (1 - BG_CROP_BOTTOM))))
        s = max(W / im.width, H / im.height)
        im = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
        l, t = (im.width - W) // 2, (im.height - H) // 2
        _bg_cache[asset_id] = im.crop((l, t, l + W, t + H))
    return _bg_cache[asset_id]


def draw_bg(frame, r, t):
    im = load_bg(r["asset"])
    prog = min(1, max(0, (t - r["start"]) / (r["end"] - r["start"])))
    z = 1 + (BG_ZOOM - 1) * prog
    zw, zh = int(W / z), int(H / z)
    im = im.crop(((W - zw) // 2, (H - zh) // 2, (W - zw) // 2 + zw, (H - zh) // 2 + zh)).resize((W, H), Image.BILINEAR)
    a = min(1, (t - r["start"]) / BG_FADE, (r["end"] - t) / BG_FADE)
    return Image.blend(frame, im, max(0, a)) if a < 1 else im


# ---------- baarish / barf ----------
def draw_weather(frame, kind, t, strength):
    """kind = rain / snow, strength 0..1 (fade in/out ke liye)"""
    import random
    rnd = random.Random(7 if kind == "rain" else 11)   # har frame mein same boondein, bas aage badhti hain
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a = int(255 * strength)
    for _ in range(WEATHER_COUNT[kind]):
        x0, y0, speed = rnd.random() * W, rnd.random() * H, 0.7 + rnd.random() * 0.6
        if kind == "rain":
            y = (y0 + t * 2200 * speed) % (H + 80) - 40
            x = (x0 - t * 350 * speed) % W
            d.line((x, y, x + 12, y - 60), fill=(170, 200, 255, int(a * 0.7)), width=3)
        else:
            y = (y0 + t * 160 * speed) % (H + 20) - 10
            x = (x0 + 30 * math.sin(t * 1.5 + x0)) % W
            r = 3 + speed * 4
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(a * 0.95)),
                      outline=(150, 170, 200, int(a * 0.8)), width=2)   # halki border, cream BG par dikhe
    frame.alpha_composite(layer)


# ---------- checks ----------
def check_case(case, rows, layers, duration):
    problems = []
    for r in rows:
        if r["asset"] and not find_file(ASSETS, r["asset"], [".png", ".PNG"]):
            problems.append(f"line {r['line']}: image '{r['asset']}.png' assets folder mein nahi hai")
        if r["sfx"] and not find_file(SFX, r["sfx"], [".wav", ".mp3"]):
            problems.append(f"line {r['line']}: sound '{r['sfx']}' sfx folder mein nahi hai")
        if r["end"] > duration + 0.5:
            problems.append(f"line {r['line']}: end {r['end']}s voice ({duration:.1f}s) se lamba hai")
    t = 0.0
    while t < duration:
        on = [L.asset for L in layers if L.start <= t < L.end]
        if len(on) > MAX_CHARS_ON_SCREEN:
            problems.append(f"{t:.1f}s par {len(on)} images ek saath: {', '.join(on)} (max {MAX_CHARS_ON_SCREEN})")
            break
        t += 0.1
    if problems:
        print(f"\n[{case}] PROBLEMS:")
        for p in problems:
            print("   -", p)
        return False
    return True


# ---------- main render ----------
def render(case):
    csv_path = os.path.join(CASES, case + ".csv")
    voice = find_file(VOICE, case, [".mp3", ".m4a", ".wav"])
    if not voice:
        print(f"[{case}] voice file nahi mili: voice\\{case}.mp3 (ya .m4a/.wav) rakho")
        return False
    rows = read_csv(csv_path)
    layers = build_layers(rows)
    duration = max(audio_duration(voice), max(r["end"] for r in rows))
    if not check_case(case, rows, layers, duration):
        return False
    import check_reel                   # text image ke upar / lamba text / khaali screen -> pehle hi roko
    if not check_reel.report(case) and "--force" not in sys.argv:
        return False

    music = find_file(MUSIC, case, [".mp3", ".m4a", ".wav"]) or \
        next(iter(sorted(glob.glob(os.path.join(MUSIC, "*.mp3")) + glob.glob(os.path.join(MUSIC, "*.m4a")))), None)
    mutes = [(r["start"], r["start"] + 1.0) for r in rows if "music_off" in r["effects"]]
    nights = [(r["start"], r["end"]) for r in rows if "night" in r["effects"]]
    weathers = [(r["start"], r["end"], k) for r in rows for k in WEATHER_COUNT if k in r["effects"]]
    bgs = [r for r in rows if r["asset"] and "bg" in r["effects"]]
    flashes = [r["start"] for r in rows if "flash" in r["effects"]]
    # punch: CSV mein 'punch' likho, ya AUTO_PUNCH se har nayi pop hone wali image par
    punches = sorted({r["start"] for r in rows if "punch" in r["effects"]} |
                     ({L.start for L in layers if L.pop and L.start > 0} if AUTO_PUNCH else set()))

    os.makedirs(OUTPUT, exist_ok=True)
    out = os.path.join(OUTPUT, case + ".mp4")
    cmd = [FFMPEG, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", voice]
    fmt = "aformat=sample_rates=44100:channel_layouts=stereo"
    fc, mix = f"[1:a]volume={VOICE_VOLUME},{fmt},asplit=2[v][vsc];", "[v]"
    n_in = 2
    if music:
        cmd += ["-stream_loop", "-1", "-i", music]
        # music ko voice ke hisaab se set karo (har music file ki awaaz alag hoti hai)
        gain = mean_db(voice) - MUSIC_BELOW_VOICE - mean_db(music)
        mute_f = "".join(f",volume=0:enable='between(t,{a:.2f},{b:.2f})'" for a, b in mutes)
        fc += (f"[{n_in}:a]{fmt},volume={gain:.1f}dB{mute_f},afade=t=in:d=0.3,"
               f"afade=t=out:st={max(0, duration - MUSIC_FADE_OUT):.2f}:d={MUSIC_FADE_OUT}[mraw];")
        if MUSIC_DUCK:
            fc += "[mraw][vsc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=400[m];"
        else:
            fc += "[mraw]anull[m];[vsc]anullsink;"
        mix += "[m]"
        n_in += 1
    else:
        fc += "[vsc]anullsink;"
    for r in rows:                      # har sound effect apne time par
        if r["sfx"]:
            cmd += ["-i", find_file(SFX, r["sfx"], [".wav", ".mp3"])]
            ms = int(r["start"] * 1000)
            fc += (f"[{n_in}:a]{fmt},volume={SFX_VOLUME},"
                   f"adelay={ms}|{ms}[x{n_in}];")
            mix += f"[x{n_in}]"
            n_in += 1
    fc += f"{mix}amix=inputs={n_in - 1}:duration=first:normalize=0[a]"
    cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[a]"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-t", f"{duration:.3f}", "-movflags", "+faststart", out]

    bg = Image.open(BG_FILE).convert("RGBA").resize((W, H))
    night_full = Image.new("RGBA", (W, H), NIGHT_COLOR + (255,))
    white_full = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(math.ceil(duration * FPS))
    last_key, last_bytes = None, None
    print(f"[{case}] {duration:.1f}s, {total} frames"
          f"{'  (music: ' + os.path.basename(music) + ')' if music else '  (bina music)'}")
    for n in range(total):
        t = n / FPS
        active = [L for L in layers if L.start <= t < L.end]
        night = 0.0
        for a, b in nights:
            if a <= t < b:
                night = NIGHT_STRENGTH * min(1, (t - a) / 0.3, (b - t) / 0.3)
        weather = [(k, min(1, (t - a) / 0.4, (b - t) / 0.4)) for a, b, k in weathers if a <= t < b]
        bg_now = [r for r in bgs if r["start"] <= t < r["end"]]
        flash = max([FLASH_STRENGTH * (1 - (t - a) / FLASH_TIME) for a in flashes if 0 <= t - a < FLASH_TIME] or [0])
        punch = max([1 - ease_out((t - a) / PUNCH_TIME) for a in punches if 0 <= t - a < PUNCH_TIME] or [0])
        # jo frame pichhle jaisa hai use dobara mat banao (speed)
        key = (round(t, 3) if bg_now or flash or punch else 0, tuple((id(L), (round(pop_scale(t - L.start), 3), pop_shift(t - L.start, L.side)) if L.pop else 1,
                      round(out_scale(L.end - t), 3) if L.leave else 1,
                      round(t, 3) if L.effects & {"zoom", "focus"} else 0) for L in active),
               round(night, 3), round(t, 3) if weather else 0,
               tuple((i, round(pop_scale(t - r["start"]), 3), pop_shift(t - r["start"]),
                      round(out_scale(r["end"] - t), 3))
                     for i, r in enumerate(rows) if r["text"] and r["start"] <= t < r["end"]))
        if key != last_key:
            frame = bg.copy()
            for r in bg_now:
                frame = draw_bg(frame, r, t)
            limit = text_bottom(rows, t)
            for L in active:
                draw_layer(frame, L, t, limit)
            if night > 0:
                frame = Image.blend(frame, night_full, night)
            for kind, strength in weather:
                draw_weather(frame, kind, t, strength)
            if punch > 0.001:           # poori picture thodi paas se shuru ho kar set ho (text nahi hilta)
                z = 1 + (PUNCH_ZOOM - 1) * punch
                zw, zh = int(W * z), int(H * z)
                big = frame.resize((zw, zh), Image.BILINEAR)
                frame = big.crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H))
            draw_texts(frame, rows, t)
            if flash > 0:
                frame = Image.blend(frame, white_full, flash)
            last_bytes = frame.convert("RGB").tobytes()
            last_key = key
        proc.stdin.write(last_bytes)
        if n % (FPS * 5) == 0:
            print(f"   {int(100 * n / total)}%", flush=True)
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        print(f"[{case}] FFmpeg fail hua")
        return False
    print(f"[{case}] BAN GAYI -> output\\{case}.mp4")
    # frame check ke liye ek grid image (16 frames) apne aap
    grid = os.path.join(OUTPUT, case + " - CHECK.png")
    step = max(0.5, duration / 16)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", out, "-vf",
                    f"fps=1/{step:.2f},scale=270:-1,tile=8x2", "-frames:v", "1", grid])
    print(f"[{case}] frame grid -> output\\{case} - CHECK.png")
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    redo = "--redo" in sys.argv
    cases = args or [os.path.splitext(os.path.basename(p))[0]
                     for p in sorted(glob.glob(os.path.join(CASES, "*.csv")))]
    if not cases:
        sys.exit("cases\\ folder mein koi CSV nahi mili.")
    done, failed, skipped = [], [], []
    for c in cases:
        if not redo and not args and os.path.exists(os.path.join(OUTPUT, c + ".mp4")):
            skipped.append(c)
            continue
        (done if render(c) else failed).append(c)
    print("\n===== RESULT =====")
    print(f"Bani: {len(done)}  |  Fail: {len(failed)} {failed if failed else ''}  |  Pehle se bani (skip): {len(skipped)}")


if __name__ == "__main__":
    main()
