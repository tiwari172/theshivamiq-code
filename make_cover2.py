# theshivamiq – "Case File" cover v2 (rang ke presets A/B/C + naya dark Shivam), 1080x1920
# (purana make_cover.py waisa hi hai – 200 reels ke cover usi se bane. Ye alag file hai.)
#
#   py make_cover2.py one "<reel naam>" "<out.png>" --style A [--hook "GALTI PAKDO!"] [--face <png>]
#   py make_cover2.py options "<reel naam>" [--hook ...] [--face ...]
#        -> output\<case> COVER A/B/C.png + output\<case> COVER OPTIONS.png (teeno saath)
#
# Styles:  A = purana navy + yellow, stamp neon cyan     B = maroon/wine + hot pink, stamp peela
#          C = kaala + neon lime frame, stamp laal, hook safed + peela outline
# Face: green-screen PNG ho to khud hara hata deta hai (chroma key + Gemini sitara saaf).

import argparse, csv, os, random, re
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FACE_FILE = r"C:\Users\Hp\Desktop\reels story\sab pe shak\_common\S2_17.png"   # naya dark look
LOGO_FILE = os.path.join(BASE, "assets", "LOGO_ROUND.png")
HANDLE = "@theshivamiq"
IMPACT = r"C:\Windows\Fonts\impact.ttf"
BLACK = r"C:\Windows\Fonts\ariblk.ttf"
W, H = 1080, 1920
STAMP_TOP, STAMP_BOTTOM = "99%", "LOG FAIL!"   # hamesha 99%

STYLES = {
    "A": dict(  # purane jaisa, sirf stamp cyan
        bg_top=(12, 20, 38), bg_bot=(4, 6, 8), glow=(40, 90, 150), fog=(120, 140, 170),
        badge_fill=(10, 10, 14), badge_line=(220, 20, 30), badge_text=(255, 255, 255),
        hook=(255, 214, 10), hook_line=(0, 0, 0),
        frame=(255, 214, 10), frame_fill=(14, 28, 50),
        stamp_fill=(8, 14, 20, 235), stamp_line=(0, 235, 255), stamp_text=(0, 235, 255),
        tape=(255, 214, 10), tape_stripe=(15, 15, 15), title_box=(0, 0, 0), title=(255, 255, 255),
        ring=(255, 214, 10), line=(255, 255, 255)),
    "B": dict(  # Pyaar aur Dhokha – kaala-maroon bg, peela hook/tape, gulabi sirf frame + stamp
        bg_top=(42, 10, 16), bg_bot=(26, 5, 9), glow=(58, 14, 22), fog=(80, 36, 44),
        badge_fill=(14, 4, 7), badge_line=(255, 212, 0), badge_text=(255, 255, 255),
        hook=(255, 212, 0), hook_line=(0, 0, 0),
        frame=(255, 60, 170), frame_fill=(36, 8, 14),
        stamp_fill=(255, 40, 150, 245), stamp_line=(255, 255, 255), stamp_text=(255, 255, 255),
        tape=(255, 214, 10), tape_stripe=(15, 15, 15), title_box=(0, 0, 0), title=(255, 255, 255),
        ring=(255, 214, 10), line=(255, 255, 255)),
    "C": dict(  # kaala + neon lime, stamp laal, hook safed peela outline
        bg_top=(14, 16, 14), bg_bot=(2, 2, 2), glow=(40, 80, 30), fog=(110, 130, 100),
        badge_fill=(0, 0, 0), badge_line=(170, 255, 40), badge_text=(170, 255, 40),
        hook=(255, 255, 255), hook_line=(255, 214, 10), hook_line2=(0, 0, 0),
        frame=(170, 255, 40), frame_fill=(16, 24, 14),
        stamp_fill=(255, 255, 255, 240), stamp_line=(220, 20, 30), stamp_text=(220, 20, 30),
        tape=(170, 255, 40), tape_stripe=(10, 10, 10), title_box=(0, 0, 0), title=(255, 255, 255),
        ring=(170, 255, 40), line=(255, 255, 255)),
}


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(text, path, size, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while size > 30 and d.textlength(text, font=font(path, size)) > maxw:
        size -= 2
    return font(path, size)


def background(s):
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    (r0, g0, b0), (r1, g1, b1) = s["bg_top"], s["bg_bot"]
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(r0 + (r1 - r0) * t), int(g0 + (g1 - g0) * t), int(b0 + (b1 - b0) * t)))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([90, 520, 990, 1480], fill=150)
    bg = Image.composite(Image.new("RGB", (W, H), s["glow"]), bg, glow.filter(ImageFilter.GaussianBlur(160)))
    random.seed(7)
    fog = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fog)
    for _ in range(40):
        x, y, r = random.randint(0, W), random.randint(400, H), random.randint(80, 260)
        fd.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=random.randint(10, 35))
    bg = Image.composite(Image.new("RGB", (W, H), s["fog"]), bg, fog.filter(ImageFilter.GaussianBlur(60)))
    return bg.convert("RGBA")


def load_face(path):
    """Green-screen hatao: jitna hara utna transparent, kinare ki hari jhalak hatao, Gemini sitara saaf."""
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).astype(np.float32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    green = g - np.maximum(r, b)                      # kitna "hara"
    if (green > 120).mean() < 0.05:                   # green-screen nahi hai -> jaisa hai waisa
        return im
    alpha = np.clip(1.0 - (green - 30) / 90.0, 0, 1)  # 30 se kam = pakka body, 120+ = pakka hara
    a[..., 3] = al * alpha
    g2 = np.minimum(g, np.maximum(r, b) + 8)          # spill: kinare ka hara rang hatao
    a[..., 1] = np.where(green > 8, g2, g)
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    # alpha thoda andar khisko (1-2px hari line na bache)
    A = out.getchannel("A").filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1))
    out.putalpha(A)
    # Gemini ka sitara (neeche-right) – aas paas ke coat rang se dhak do
    w, h = out.size
    box = (int(w * 0.80), int(h * 0.84), int(w * 0.95), int(h * 0.97))
    crop = np.asarray(out.crop(box)).astype(np.int32)
    lum = crop[..., :3].mean(axis=2)
    base = np.median(crop[..., :3][(crop[..., 3] > 200) & (lum < 90)], axis=0) if ((crop[..., 3] > 200) & (lum < 90)).any() else None
    if base is not None:
        star = (lum > base.mean() + 25) & (crop[..., 3] > 200)
        star = np.asarray(Image.fromarray((star * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))) > 0
        crop[star, :3] = base.astype(np.int32)
        out.paste(Image.fromarray(crop.astype(np.uint8), "RGBA"), box[:2])
    return out


_FACE = {}


def cover(case_no, title, hook, out, style="A", face_file=FACE_FILE):
    s = STYLES[style.upper()]
    img = background(s)
    d = ImageDraw.Draw(img)

    # case badge (Insta grid safe zone 285..1635 ke andar)
    f = font(IMPACT, 64)
    tw = d.textlength(case_no, font=f)
    bx0, by0 = (W - tw) / 2 - 36, 292
    d.rounded_rectangle([bx0, by0, bx0 + tw + 72, by0 + 96], 14, fill=s["badge_fill"], outline=s["badge_line"], width=7)
    d.text((W / 2, by0 + 48), case_no, font=f, fill=s["badge_text"], anchor="mm")

    # sawaal / hook
    hf = fit(hook, IMPACT, 190, 960)
    if "hook_line2" in s:   # double outline: bahar kaala, andar rangeen
        d.text((W / 2, 505), hook, font=hf, fill=s["hook_line2"], anchor="mm", stroke_width=16, stroke_fill=s["hook_line2"])
    d.text((W / 2, 505), hook, font=hf, fill=s["hook"], anchor="mm", stroke_width=9, stroke_fill=s["hook_line"])

    # Shivam frame mein
    if face_file not in _FACE:
        _FACE[face_file] = load_face(face_file)
    face = _FACE[face_file]
    fh = 1000
    face = face.resize((int(face.width * fh / face.height), fh), Image.LANCZOS)
    fx0, fy0, fx1, fy1 = (W - face.width) // 2 + 20, 625, (W + face.width) // 2 - 20, 1450
    d.rounded_rectangle([fx0, fy0, fx1, fy1], 28, fill=s["frame_fill"], outline=s["frame"], width=8)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([fx0 + 8, fy0 + 8, fx1 - 8, fy1 - 8], 22, fill=255)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.alpha_composite(face, ((W - face.width) // 2, fy0 + 10))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    img.alpha_composite(layer)

    # 99% LOG FAIL! stamp (kandhe par, chehre se door)
    st = Image.new("RGBA", (360, 240), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rectangle([8, 8, 352, 232], fill=s["stamp_fill"], outline=s["stamp_line"], width=10)
    sd.text((180, 78), STAMP_TOP, font=font(IMPACT, 96), fill=s["stamp_text"], anchor="mm")
    sd.text((180, 172), STAMP_BOTTOM, font=fit(STAMP_BOTTOM, IMPACT, 78, 310), fill=s["stamp_text"], anchor="mm")
    st = st.resize((290, 193), Image.LANCZOS).rotate(14, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(st, (W - st.width - 14, 1150))

    # police tape + story naam
    tape = Image.new("RGBA", (W + 300, 170), s["tape"] + (255,))
    td = ImageDraw.Draw(tape)
    for x in range(-200, W + 400, 110):
        td.polygon([(x, 0), (x + 55, 0), (x - 5, 170), (x - 60, 170)], fill=s["tape_stripe"] + (255,))
    f = fit(title, IMPACT, 120, 820)
    tw = td.textlength(title, font=f)
    cx = tape.width / 2
    td.rectangle([cx - tw / 2 - 30, 18, cx + tw / 2 + 30, 152], fill=s["title_box"] + (255,))
    td.text((cx, 86), title, font=f, fill=s["title"], anchor="mm")
    tape = tape.rotate(-4, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(tape, ((W - tape.width) // 2, 1370))

    d = ImageDraw.Draw(img)
    d.text((W / 2, 1640), "Tum pakad paoge?", font=font(BLACK, 54), fill=s["line"], anchor="mm",
           stroke_width=4, stroke_fill=(0, 0, 0))

    # logo + handle
    ls = 120
    logo = Image.open(LOGO_FILE).convert("RGBA").resize((ls, ls), Image.LANCZOS)
    m = Image.new("L", (ls, ls), 0)
    ImageDraw.Draw(m).ellipse([0, 0, ls - 1, ls - 1], fill=255)
    logo.putalpha(m)
    f = font(BLACK, 50)
    tw = d.textlength(HANDLE, font=f)
    x0 = int((W - (ls + 24 + tw)) / 2)
    d.ellipse([x0 - 5, 1715 - 5, x0 + ls + 4, 1715 + ls + 4], fill=s["ring"])
    img.alpha_composite(logo, (x0, 1715))
    d.text((x0 + ls + 24, 1715 + ls / 2), HANDLE, font=f, fill=(255, 255, 255), anchor="lm",
           stroke_width=4, stroke_fill=(0, 0, 0))
    img.convert("RGB").save(out)
    return out


def info(name, cat=None):
    m = re.match(r"([A-Z]?\d{2})-(\d{3}) (.+)", name)
    if m:
        case_no, title = f"CASE #{m.group(1)}-{m.group(2)}", m.group(3)
    else:
        m = re.match(r"(\d{2}) (.+)", name)
        case_no, title = f"CASE #{int(cat or 1):02d}-0{m.group(1)}", m.group(2)
    hook = "KILLER KAUN?"
    path = os.path.join(BASE, "cases", name + ".csv")
    if os.path.exists(path):
        for r in list(csv.reader(open(path, encoding="utf-8-sig")))[:8]:
            txt = " ".join(r[5].split("\\n")).strip().upper() if len(r) > 5 else ""
            if re.search(r"KAUN\?|PAKDO!", txt):
                hook = txt
                break
    return case_no, title.upper(), hook


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["one", "options"])
    ap.add_argument("name")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--style", default="A", choices=list(STYLES) + [k.lower() for k in STYLES])
    ap.add_argument("--hook")
    ap.add_argument("--face", default=FACE_FILE)
    a = ap.parse_args()
    case_no, title, hook = info(a.name)
    hook = (a.hook or hook).upper()
    if a.cmd == "one":
        print("bana:", cover(case_no, title, hook, a.out, a.style, a.face))
        return
    code = a.name.split(" ")[0]
    outs = []
    for k in STYLES:
        p = os.path.join(BASE, "output", f"{code} COVER {k}.png")
        outs.append(cover(case_no, title, hook, p, k, a.face))
        print("bana:", p)
    # preview sheet (teeno chhote, saath mein)
    tw_, th_, gap = 360, 640, 30
    sheet = Image.new("RGB", (gap + 3 * (tw_ + gap), th_ + 2 * gap + 50), (40, 40, 40))
    sd = ImageDraw.Draw(sheet)
    for i, (k, p) in enumerate(zip(STYLES, outs)):
        x = gap + i * (tw_ + gap)
        sheet.paste(Image.open(p).resize((tw_, th_), Image.LANCZOS), (x, gap))
        sd.text((x + tw_ / 2, gap + th_ + 25), k, font=font(IMPACT, 40), fill=(255, 255, 255), anchor="mm")
    sp = os.path.join(BASE, "output", f"{code} COVER OPTIONS.png")
    sheet.save(sp)
    print("sheet:", sp)


if __name__ == "__main__":
    main()
