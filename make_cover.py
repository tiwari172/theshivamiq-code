# theshivamiq – Naya "Case File" cover (Insta Reels / Shorts, 1080x1920)
#
#   py make_cover.py all                     har story folder jisme MP4 hai -> "<reel naam> - COVER.png" usi folder mein
#   py make_cover.py one "<reel naam>" "<out.png>"     sirf ek (case number + sawaal CSV se)
#
# Case number reel ke naam se (10-004 ... -> CASE #10-004, Cat 1 "04 ..." -> CASE #01-004),
# sawaal (KILLER / CHOR / ... KAUN?) cases\<reel naam>.csv ki hook line se. Purana cover overwrite nahi hota.

import csv, glob, os, random, re, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
STORY_ROOT = r"C:\Users\Hp\Desktop\reels story"
FACE_FILE = os.path.join(BASE, "assets", "S16.png")
LOGO_FILE = os.path.join(BASE, "assets", "LOGO_ROUND.png")   # naya channel logo (2026-10-10; pehle CHANNEL_LOGO.jpg)
HANDLE = "@theshivamiq"
IMPACT = r"C:\Windows\Fonts\impact.ttf"
BLACK = r"C:\Windows\Fonts\ariblk.ttf"
W, H = 1080, 1920
YEL, RED, WHITE = (255, 214, 10), (220, 20, 30), (255, 255, 255)


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(text, path, size, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while size > 30 and d.textlength(text, font=font(path, size)) > maxw:
        size -= 2
    return font(path, size)


def background():
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(12 - 8 * t), int(20 - 14 * t), int(38 - 30 * t)))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([90, 520, 990, 1480], fill=150)
    bg = Image.composite(Image.new("RGB", (W, H), (40, 90, 150)), bg, glow.filter(ImageFilter.GaussianBlur(160)))
    random.seed(7)
    fog = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fog)
    for _ in range(40):
        x, y, r = random.randint(0, W), random.randint(400, H), random.randint(80, 260)
        fd.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=random.randint(10, 35))
    bg = Image.composite(Image.new("RGB", (W, H), (120, 140, 170)), bg, fog.filter(ImageFilter.GaussianBlur(60)))
    return bg.convert("RGBA")


_BG = None


def cover(case_no, title, hook, out):
    global _BG
    if _BG is None:
        _BG = background()
    img = _BG.copy()
    d = ImageDraw.Draw(img)

    # case badge
    f = font(IMPACT, 64)
    tw = d.textlength(case_no, font=f)
    bx0, by0 = (W - tw) / 2 - 36, 262
    d.rounded_rectangle([bx0, by0, bx0 + tw + 72, by0 + 96], 14, fill=(10, 10, 14), outline=RED, width=7)
    d.text((W / 2, by0 + 48), case_no, font=f, fill=WHITE, anchor="mm")

    # sawaal
    d.text((W / 2, 490), hook, font=fit(hook, IMPACT, 190, 980), fill=YEL, anchor="mm",
           stroke_width=10, stroke_fill=(0, 0, 0))

    # Shivam peela frame mein (neeche ka hissa + watermark frame ke bahar kat jaata hai)
    face = Image.open(FACE_FILE).convert("RGBA")
    fh = 1000
    face = face.resize((int(face.width * fh / face.height), fh), Image.LANCZOS)
    fx0, fy0, fx1, fy1 = (W - face.width) // 2 + 20, 610, (W + face.width) // 2 - 20, 1450
    d.rounded_rectangle([fx0, fy0, fx1, fy1], 28, fill=(14, 28, 50), outline=YEL, width=8)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([fx0 + 8, fy0 + 8, fx1 - 8, fy1 - 8], 22, fill=255)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.alpha_composite(face, ((W - face.width) // 2, fy0 + 20))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    img.alpha_composite(layer)

    # 99% FAIL stamp (kaan ke neeche, kandhe par)
    st = Image.new("RGBA", (330, 230), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rectangle([8, 8, 322, 222], fill=(12, 12, 16, 235), outline=RED, width=10)
    sd.text((165, 80), "99%", font=font(IMPACT, 96), fill=RED, anchor="mm")
    sd.text((165, 168), "FAIL", font=font(IMPACT, 88), fill=RED, anchor="mm")
    st = st.resize((280, 195), Image.LANCZOS).rotate(14, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(st, (W - st.width - 20, 1130))

    # police tape + story naam
    tape = Image.new("RGBA", (W + 300, 170), YEL + (255,))
    td = ImageDraw.Draw(tape)
    for x in range(-200, W + 400, 110):
        td.polygon([(x, 0), (x + 55, 0), (x - 5, 170), (x - 60, 170)], fill=(15, 15, 15, 255))
    f = fit(title, IMPACT, 120, 820)
    tw = td.textlength(title, font=f)
    cx = tape.width / 2
    td.rectangle([cx - tw / 2 - 30, 18, cx + tw / 2 + 30, 152], fill=(0, 0, 0, 255))
    td.text((cx, 86), title, font=f, fill=WHITE, anchor="mm")
    tape = tape.rotate(-4, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(tape, ((W - tape.width) // 2, 1370))

    d = ImageDraw.Draw(img)
    d.text((W / 2, 1635), "Tum pakad paoge?", font=font(BLACK, 54), fill=WHITE, anchor="mm",
           stroke_width=4, stroke_fill=(0, 0, 0))

    # channel logo (gol) + insta handle
    ls = 120
    logo = Image.open(LOGO_FILE).convert("RGBA").resize((ls, ls), Image.LANCZOS)
    m = Image.new("L", (ls, ls), 0)
    ImageDraw.Draw(m).ellipse([0, 0, ls - 1, ls - 1], fill=255)
    logo.putalpha(m)
    f = font(BLACK, 50)
    tw = d.textlength(HANDLE, font=f)
    x0 = int((W - (ls + 24 + tw)) / 2)
    ring = [x0 - 5, 1715 - 5, x0 + ls + 4, 1715 + ls + 4]
    d.ellipse(ring, fill=YEL)
    img.alpha_composite(logo, (x0, 1715))
    d.text((x0 + ls + 24, 1715 + ls / 2), HANDLE, font=f, fill=WHITE, anchor="lm",
           stroke_width=4, stroke_fill=(0, 0, 0))
    img.convert("RGB").save(out)


def info(name, cat=None):
    # "10-004 Joshi ji ki Angoothi" / Cat 1: "04 Raat Gyarah Baje"
    m = re.match(r"([A-Z]?\d{2})-(\d{3}) (.+)", name)   # H01-001 (viral hook) bhi
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
    if len(sys.argv) > 1 and sys.argv[1] == "one":
        cover(*info(sys.argv[2]), sys.argv[3])
        print("bana:", sys.argv[3])
        return
    if len(sys.argv) > 1 and sys.argv[1] == "redo":
        # jo Case File cover pehle se bane hain unhe naye logo ke saath dobara (same naam par) banao
        n = 0
        for folder in sorted(glob.glob(os.path.join(STORY_ROOT, "Category *", "Story *"))):
            cat = re.search(r"Category (\d+)", folder).group(1)
            for p in glob.glob(os.path.join(folder, "* - COVER*.png")):
                name = re.sub(r" - COVER( NEW)?\.png$", "", os.path.basename(p))
                if cat == "1" and p.endswith(" - COVER.png") and os.path.exists(p[:-4] + " NEW.png"):
                    continue   # Cat 1 ka purana design wala cover, user ne rakhne ko kaha tha
                cover(*info(name, cat), p)
                n += 1
        print(f"{n} cover naye logo ke saath dobara bane.")
        return
    made, skipped = 0, []
    for folder in sorted(glob.glob(os.path.join(STORY_ROOT, "Category *", "Story *"))):
        mp4s = [p for p in glob.glob(os.path.join(folder, "*.mp4")) if "(v1)" not in p]
        if not mp4s:
            continue
        name = os.path.splitext(os.path.basename(mp4s[0]))[0]
        out = os.path.join(folder, name + " - COVER.png")
        if os.path.exists(out):   # purana cover mat mitao
            out = os.path.join(folder, name + " - COVER NEW.png")
            skipped.append(name)
        cat = re.search(r"Category (\d+)", folder).group(1)
        c = info(name, cat)
        cover(*c, out)
        made += 1
        print(f"{c[0]}  {c[2]:<16} {c[1]}")
    print(f"\n{made} cover bane.")
    if skipped:
        print("Inme purana cover pehle se tha, naya ' - COVER NEW.png' naam se bana:", ", ".join(skipped))


if __name__ == "__main__":
    main()
