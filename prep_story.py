# theshivamiq – Story ki images taiyaar karo (reel banane se pehle, ek baar)
#
#   py prep_story.py "C:\Users\Hp\Desktop\reels story\Category 11\Story 07"
#
# Kya karta hai:
#   1. story images\ ki PNG assets\ mein copy (naam pehle se hai par image alag -> naya naam <ID>_<NNNN>, overwrite nahi)
#   2. safed background wali image -> <ID>_CUT.png (background transparent)
#   3. neeche ka kinara chipka hua prop -> <ID>_UP.png (neeche 20px khali)
#   4. sab final images ki ek contact sheet -> output\<Story> - IMAGES.png
#   Aakhir mein batata hai CSV mein kaunsa naam use karna hai.

import hashlib, os, re, shutil, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
import make_reel as R
from check_reel import white_box, cut_bottom

WHITE = 235          # isse zyada safed pixel = background
PAD_BOTTOM = 20


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def remove_white(src, dst):
    """kinaron se jude safed hisse ko transparent karo (andar ka safed jaise aankh / kameez bacha rahe)"""
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    rgb = im.convert("RGB")
    mask = Image.new("L", (w + 2, h + 2), 255)                  # bahar 1px safed frame, taaki ek fill kaafi ho
    white = rgb.point(lambda v: 255 if v > WHITE else 0).split()
    white = Image.merge("RGB", white).convert("L").point(lambda v: 255 if v == 255 else 0)
    mask.paste(white, (1, 1))
    ImageDraw.floodfill(mask, (0, 0), 128)
    bg = mask.crop((1, 1, w + 1, h + 1)).point(lambda v: 255 if v == 128 else 0)
    alpha = Image.eval(bg, lambda v: 255 - v).filter(ImageFilter.MinFilter(3))   # 1px kinara bhi hatao (safed halo)
    im.putalpha(ImageChops.darker(alpha, im.getchannel("A")))
    im.save(dst)


def pad_bottom(src, dst):
    im = Image.open(src).convert("RGBA")
    out = Image.new("RGBA", (im.width, im.height + PAD_BOTTOM), (0, 0, 0, 0))
    out.paste(im, (0, 0))
    out.save(dst)


def contact_sheet(ids, path):
    cell, cols = 240, 6
    rows = (len(ids) + cols - 1) // cols
    sheet = Image.new("RGB", (cell * cols, (cell + 30) * rows), (250, 240, 220))   # reel jaisa cream bg
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(R.FONT_FILE, 15)
    for i, a in enumerate(ids):
        im = Image.open(R.find_file(R.ASSETS, a, [".png", ".PNG"])).convert("RGBA")
        im.thumbnail((cell - 10, cell - 10))
        x, y = (i % cols) * cell, (i // cols) * (cell + 30)
        sheet.paste(im, (x + (cell - im.width) // 2, y + 5 + (cell - 10 - im.height)), im)
        d.rectangle((x, y, x + cell - 1, y + cell + 29), outline=(200, 190, 170))
        d.text((x + cell // 2, y + cell + 6), a[:26], font=font, fill="black", anchor="ma")
    sheet.save(path)


def main():
    if len(sys.argv) < 2:
        sys.exit('Chalao: py prep_story.py "<story folder>"')
    # "...\Story 07\" likhne par Windows aakhri " ko bhi naam mein de deta hai -> hatao
    story = sys.argv[1].strip().strip('"').rstrip("\\/")
    img_dir = os.path.join(story, "images")
    if not os.path.isdir(img_dir):
        sys.exit(f"images folder nahi mila: {img_dir}")
    cat = re.search(r"Category (\d+)", story)
    num = re.search(r"Story (\d+)", story)
    tag = f"{int(cat.group(1)):02d}{int(num.group(1)):02d}" if cat and num else "NEW"

    final = {}          # story ka naam -> CSV mein lagane wala naam
    notes = []
    os.makedirs(R.ASSETS, exist_ok=True)
    for f in sorted(os.listdir(img_dir)):
        if not f.lower().endswith(".png"):
            if f.lower().endswith((".jpg", ".jpeg", ".webp")):
                notes.append(f"{f}: PNG nahi hai, chhod diya (PNG mein save karke dobara chalao)")
            continue
        src = os.path.join(img_dir, f)
        a = os.path.splitext(f)[0]
        dst = os.path.join(R.ASSETS, a + ".png")
        if os.path.exists(dst) and md5(dst) != md5(src):
            new = f"{a}_{tag}"
            new_dst = os.path.join(R.ASSETS, new + ".png")
            if not os.path.exists(new_dst):
                shutil.copy2(src, new_dst)
            notes.append(f"{a}: assets mein isi naam ki DUSRI image hai -> {new} naam se rakhi")
            a = new
        elif not os.path.exists(dst):
            shutil.copy2(src, dst)
        use = a
        p = R.find_file(R.ASSETS, use, [".png"])
        if white_box(p):
            cut = use + "_CUT"
            if not os.path.exists(os.path.join(R.ASSETS, cut + ".png")):
                remove_white(p, os.path.join(R.ASSETS, cut + ".png"))
                notes.append(f"{use}: safed background hataya -> {cut}")
            use = cut
            p = R.find_file(R.ASSETS, use, [".png"])
        if cut_bottom(p, use):
            up = use + "_UP"
            if not os.path.exists(os.path.join(R.ASSETS, up + ".png")):
                pad_bottom(p, os.path.join(R.ASSETS, up + ".png"))
                notes.append(f"{use}: neeche 20px khali joda -> {up}")
            use = up
        final[os.path.splitext(f)[0]] = use

    if not final:
        for n in notes:
            print("  *", n)
        sys.exit(f"images folder mein koi PNG nahi mili: {img_dir}")
    os.makedirs(R.OUTPUT, exist_ok=True)
    sheet = os.path.join(R.OUTPUT, f"{os.path.basename(story)} {tag} - IMAGES.png")
    contact_sheet(list(final.values()), sheet)
    for n in notes:
        print("  *", n)
    print("\nCSV mein ye naam lagao:")
    for k, v in final.items():
        print(f"   {k:28s} -> {v}" if k != v else f"   {k}")
    print(f"\nContact sheet -> {sheet}")


if __name__ == "__main__":
    main()
