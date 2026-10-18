# theshivamiq – Options card + Cover
#
#   python make_cards.py options C001_OPTIONS G_RAMU:Ramu C001_ROHIT:Rohit G_BHOLA:Bhola C001_ANJALI:Anjali
#       -> assets\C001_OPTIONS.png  (suspects 1,2,3,4 number ke saath; CSV mein image ki tarah lagao)
#
#   python make_cards.py cover "01 Saalgirah ki Raat" S16 "99% LOG FAIL!" "KILLER KAUN?"
#       -> output\01 Saalgirah ki Raat - COVER.png  (reel upload karte waqt cover mein lagao)

import os, sys
from PIL import Image, ImageDraw, ImageFont
from make_reel import (ASSETS, OUTPUT, BG_FILE, FONT_FILE, W, H, COLORS, TEXT_STROKE,
                       find_file, text_image, paste)


def load(asset_id):
    path = find_file(ASSETS, asset_id, [".png", ".PNG"])
    if not path:
        sys.exit(f"image nahi mili: assets\\{asset_id}.png")
    im = Image.open(path).convert("RGBA")
    return im.crop(im.getchannel("A").getbbox())


def fit(im, max_w, max_h):
    s = min(max_w / im.width, max_h / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def options(name, items):
    if not items:
        sys.exit("options ke liye kam se kam ek  ID:Naam  do (jaise C001_ROHIT:Rohit)")
    for item in items:
        if ":" not in item:
            sys.exit(f"'{item}' galat hai -> ID:Naam likho (jaise C001_ROHIT:Rohit)")
    col, fig_h, badge = W // len(items), 560, 110
    card = Image.new("RGBA", (W, fig_h + badge + 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    num_font = ImageFont.truetype(FONT_FILE, 70)
    name_font = ImageFont.truetype(FONT_FILE, 46)
    for i, item in enumerate(items):
        asset, label = item.split(":", 1)
        fig = fit(load(asset), col - 20, fig_h)
        x = i * col + (col - fig.width) // 2
        card.alpha_composite(fig, (x, badge + fig_h - fig.height))
        cx = i * col + col // 2
        d.ellipse((cx - 50, 0, cx + 50, 100), fill=COLORS["yellow"], outline="black", width=6)
        d.text((cx, 52), str(i + 1), font=num_font, fill="black", anchor="mm")
        d.text((cx, badge + fig_h + 50), label.upper(), font=name_font, fill="white", anchor="mm",
               stroke_width=6, stroke_fill="black")
    out = os.path.join(ASSETS, name + ".png")
    card.save(out)
    print("bana:", out)


def cover(title, asset, big, small):
    im = Image.open(BG_FILE).convert("RGBA").resize((W, H))
    fig = fit(load(asset), W, int(H * 0.62))
    im.alpha_composite(fig, ((W - fig.width) // 2, H - fig.height))
    y = int(H * 0.12)
    for text, size, color in ((big, 130, "yellow"), (small, 96, "white"), (title, 60, "white")):
        t = text_image(text, size, color)
        paste(im, t, (W - t.width) // 2, y)
        y += t.height + 30
    out = os.path.join(OUTPUT, f"{title} - COVER.png")
    os.makedirs(OUTPUT, exist_ok=True)
    im.convert("RGB").save(out)
    print("bana:", out)


if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else ""
    if kind == "options":
        if len(sys.argv) < 4:
            sys.exit("Aise likho: make_cards.py options C0NN_OPTIONS ID:Naam ID:Naam ...")
        options(sys.argv[2], sys.argv[3:])
    elif kind == "cover":
        if len(sys.argv) < 6:
            sys.exit('Aise likho: make_cards.py cover "<NN Title>" S16 "99% LOG FAIL!" "KILLER KAUN?"')
        cover(*sys.argv[2:6])
    else:
        sys.exit(__doc__ or "make_cards.py options ... / cover ...")
