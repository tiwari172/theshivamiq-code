# theshivamiq – Reel Checker (render se PEHLE galtiyan pakdo, bina video banaye)
#
#   py check_reel.py "11-006 Bina Chaabi Ke"      -> ek case check
#   py check_reel.py                             -> cases\ ki saari CSV
#
# Kya check karta hai:
#   - text kisi image (character / prop) ke upar to nahi aa raha
#   - text 3 line se lamba to nahi
#   - koi waqt sirf text wala (khaali screen) to nahi
#   - image ka background safed dabba to nahi (_CUT chahiye)
#   - image screen ke neeche kat to nahi rahi (_UP chahiye)

import glob, os, sys
from PIL import Image, ImageChops, ImageDraw
import make_reel as R

STEP = 0.1                 # har itne second par check
MIN_OVERLAP_PX = 400       # isse kam pixel takraye to ignore (outline ka halka chhoona)
MIN_CHAR_SCALE = 0.75      # text ki wajah se character isse zyada chhota ho to galti


def text_lines(r):
    """caption kitni line mein wrap hoga"""
    R._text_cache.pop((r["text"], r["font"], r["color"]), None)
    R.text_image(r["text"], r["font"], r["color"])      # isse R._font sahi size par set hota hai
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    return len(R.wrap(r["text"], R._font, tmp))


def masks_at(rows, layers, t):
    """is waqt image aur text ka alpha mask (animation ke end wali position par)"""
    img = Image.new("RGBA", (R.W, R.H), (0, 0, 0, 0))
    limit = R.text_bottom(rows, t)
    for L in layers:
        if L.start <= t < L.end:
            R.draw_layer(img, L, t, limit)
    txt = Image.new("RGBA", (R.W, R.H), (0, 0, 0, 0))
    R.draw_texts(txt, rows, t)
    return img.getchannel("A"), txt.getchannel("A")


def white_box(path):
    """image ka background safed / bina transparency to nahi"""
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    corners = [im.getpixel(p) for p in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
    return sum(c[3] > 250 and min(c[:3]) > 230 for c in corners) >= 3   # kone safed aur bhare hue


def cut_bottom(path, asset_id):
    """image ka neeche wala kinara chipka hai aur ye character (S..) nahi -> screen ke neeche katega"""
    if asset_id.upper().startswith("S") or asset_id.upper().endswith("_UP"):
        return False
    a = Image.open(path).convert("RGBA").getchannel("A")
    box = a.getbbox()
    return bool(box) and box[3] >= a.height - 2 and (box[2] - box[0]) < a.width * 0.95 and \
        a.crop((0, a.height - 2, a.width, a.height)).getbbox() is not None


def check(case):
    rows = R.read_csv(os.path.join(R.CASES, case + ".csv"))
    layers = R.build_layers(rows)
    end = max(r["end"] for r in rows)
    problems = []          # ye hon to render mat karo
    warnings = []          # image wale: dekh lo, shayad theek ho (jaise bed ka neeche chipakna)

    # 1. lamba text
    for r in rows:
        if r["text"]:
            n = text_lines(r)
            if n > 3:
                problems.append(f"line {r['line']}: text {n} line ka hai (max 3) -> do time-rows mein todo: "
                                f"\"{r['text'][:40]}\"")

    # 2. images: safed dabba / neeche kati
    seen = set()
    for r in rows:
        a = r["asset"]
        if not a or a in seen:
            continue
        seen.add(a)
        p = R.find_file(R.ASSETS, a, [".png", ".PNG"])
        if not p:
            problems.append(f"line {r['line']}: image '{a}.png' assets mein nahi hai")
            continue
        if white_box(p):
            warnings.append(f"line {r['line']}: '{a}' ka background safed hai -> {a}_CUT banao")
        if cut_bottom(p, a):
            warnings.append(f"line {r['line']}: '{a}' ka neeche wala kinara chipka hai -> {a}_UP banao")

    # 3. har hisse (jab screen par kuch badle) ke beech mein: text image ke upar? khaali screen?
    cuts = sorted({0.0, end} | {r["start"] for r in rows} | {r["end"] for r in rows})
    shrunk = set()
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 0.05:
            continue
        # animation settle hone ke baad + end ke paas (zoom/focus sabse bada)
        for tt in {round(min(a + 0.4, (a + b) / 2), 2), round(b - 0.05, 2)}:
            img_a, txt_a = masks_at(rows, layers, tt)
            both = ImageChops.multiply(img_a.point(lambda v: 255 if v > 40 else 0),
                                       txt_a.point(lambda v: 255 if v > 40 else 0))
            limit = R.text_bottom(rows, tt)
            for L in layers:
                if L.start <= tt < L.end and limit and "focus" not in L.effects and L.asset not in shrunk:
                    base, bust = R.load_asset(L.asset, L.size)
                    room = (R.H if bust else R.SAFE_BOTTOM) - limit
                    if room < base.height * MIN_CHAR_SCALE:
                        shrunk.add(L.asset)
                        problems.append(f"{tt:.1f}s: text lamba hai, '{L.asset}' {int(100 * room / base.height)}% "
                                        f"size tak chhota ho gaya -> text chhota karo ya do time-rows mein todo")
                        break
            if both.histogram()[255] > MIN_OVERLAP_PX:
                txt_rows = [r["line"] for r in rows if r["text"] and r["start"] <= tt < r["end"]]
                img_rows = [L.asset for L in layers if L.start <= tt < L.end]
                problems.append(f"{tt:.1f}s: text (line {txt_rows}) image {img_rows} ke upar aa raha hai")
                break
            has_img = img_a.getbbox() is not None or any(
                r["asset"] and "bg" in r["effects"] and r["start"] <= tt < r["end"] for r in rows)
            if not has_img and txt_a.getbbox() is not None:
                problems.append(f"{a:.1f}-{b:.1f}s: screen par sirf text hai, koi image nahi (pichhli image aage badhao)")
                break
    return problems, warnings


def report(case):
    """print karo; True = render kar sakte ho"""
    p, w = check(case)
    for x in w:
        print(f"[{case}] DHYAAN DO: {x}")
    if p:
        print(f"\n[{case}] {len(p)} PROBLEM (render nahi hoga, CSV theek karo):")
        for x in p:
            print("   -", x)
        return False
    print(f"[{case}] check OK")
    return True


def main():
    cases = sys.argv[1:] or [os.path.splitext(os.path.basename(p))[0]
                             for p in sorted(glob.glob(os.path.join(R.CASES, "*.csv")))]
    return sum(not report(c) for c in cases)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
