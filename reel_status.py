# theshivamiq – REEL STATUS
#
# Saari story folders (reels story\Category N\Story NN) scan karke batata hai har reel ka kya bana, kya baaki:
#   Script (SCRIPT_*.txt) | VO (VO_MAIN.mp3) | Voice (voice\<reel>.m4a) | CSV (cases\<reel>.csv)
#   | MP4 (story folder mein) | timing.csv | Cover (- COVER.png)  + "Agla kaam"
# Story folder mein KUCH NAHI likhta. --report par sirf code folder ke output\ mein HTML + CSV banta hai.
#
#   py reel_status.py                 poori table
#   py reel_status.py --baaki         sirf adhoori reels
#   py reel_status.py --category 9    sirf Category 9
#   py reel_status.py --report        output\REEL STATUS.html + output\REEL STATUS.csv bhi
#   (ya double-click: REEL STATUS.bat)

import argparse, csv, glob, html, os, re, sys
from datetime import datetime

import tools_common as T

COLS = ["Script", "VO", "Voice", "CSV", "MP4", "timing", "Cover"]
AUDIO_EXT = (".m4a", ".mp3", ".wav")


def read_title(script):
    """SCRIPT ki pehli line: 'STORY 10 – Case 09-010: Til Gud ki Dopahar   (Category 9...)' -> (id, title)"""
    try:
        with open(script, encoding="utf-8-sig", errors="replace") as f:
            first = f.readline()
    except OSError:
        return None, None
    m = re.search(r"Case\s+([\w-]+)\s*:\s*(.+?)(?:\s{2,}|\s*\(|$)", first.strip())
    return (m.group(1), m.group(2).strip()) if m else (None, None)


def match_file(folder, name, case_id, exts):
    """folder mein '<name>.<ext>' (pehle), warna '<id> ...' se shuru hone wali file. Na mile to None."""
    if not os.path.isdir(folder):
        return None
    for ext in exts:
        p = os.path.join(folder, name + ext)
        if os.path.exists(p):
            return p
    if case_id:
        for p in sorted(os.listdir(folder)):
            stem, ext = os.path.splitext(p)
            if ext.lower() in exts and (stem == case_id or stem.startswith(case_id + " ")):
                return os.path.join(folder, p)
    return None


def scan_story(folder, base=None):
    base = base or T.BASE
    cat, num = T.story_numbers(folder)
    scripts = sorted(glob.glob(os.path.join(folder, "SCRIPT_*.txt")))
    script = scripts[0] if scripts else None
    case_id, title = read_title(script) if script else (None, None)
    if not case_id and script:
        case_id = os.path.splitext(os.path.basename(script))[0][len("SCRIPT_"):] or None
    if not case_id and cat is not None and num is not None:
        case_id = f"{cat:02d}-{num:03d}"

    mp4s = sorted(p for p in glob.glob(os.path.join(folder, "*.mp4")) if "(v1)" not in p)
    if mp4s:
        name = os.path.splitext(os.path.basename(mp4s[0]))[0]
    else:
        name = f"{case_id} {title}" if case_id and title else (case_id or os.path.basename(folder))

    vo = os.path.exists(os.path.join(folder, "VO_MAIN.mp3")) or bool(glob.glob(os.path.join(folder, "VO_MAIN.*")))
    voice = match_file(os.path.join(base, "voice"), name, case_id, AUDIO_EXT)
    case_csv = match_file(os.path.join(base, "cases"), name, case_id, (".csv",))
    rendered = match_file(os.path.join(base, "output"), name, case_id, (".mp4",))
    timing = os.path.exists(os.path.join(folder, "timing.csv"))
    cover = bool(glob.glob(os.path.join(folder, "* - COVER*.png")))

    have = {"Script": bool(script), "VO": vo, "Voice": bool(voice), "CSV": bool(case_csv),
            "MP4": bool(mp4s), "timing": timing, "Cover": cover}

    if have["MP4"] and timing and cover:
        nxt = "PURI"
    elif not script:
        nxt = "Script nahi hai (SCRIPT_*.txt)"
    elif not have["Voice"] and not vo:
        nxt = "Voice banao (VOICE BANAO.bat)"
    elif not have["Voice"]:
        nxt = "build_voice.py chalao"
    elif not have["CSV"]:
        nxt = "CSV likho (cases\\)"
    elif not have["MP4"] and rendered:
        nxt = "MP4 output\\ mein hai -> story folder mein copy karo"
    elif not have["MP4"]:
        nxt = "Render karo (make_reel.py)"
    elif not timing:
        nxt = "CSV ko timing.csv naam se story folder mein copy karo"
    else:
        nxt = "Cover banao (make_cover.py)"

    return {"folder": folder, "category": cat, "story": num, "id": case_id or "", "name": name,
            "have": have, "next": nxt, "done": nxt == "PURI"}


def scan_all(story_root=None, base=None, category=None):
    rows = [scan_story(f, base) for f in T.story_folders(story_root)]
    if category is not None:
        rows = [r for r in rows if r["category"] == category]
    return rows


def label(r):
    c = f"{r['category']}" if r["category"] is not None else "?"
    s = f"{r['story']:02d}" if r["story"] is not None else "?"
    return f"C{c} S{s}"


def print_table(rows, only_pending=False):
    show = [r for r in rows if not (only_pending and r["done"])]
    nw = min(max([len(r["name"]) for r in show] + [4]), 34)
    head = f"{'Story':<8} {'Reel':<{nw}} " + " ".join(f"{c:^6}" for c in COLS) + "  Agla kaam"
    print(head)
    print("-" * len(head))
    for r in show:
        marks = " ".join(f"{('✓' if r['have'][c] else '-'):^6}" for c in COLS)
        name = r["name"] if len(r["name"]) <= nw else r["name"][:nw - 1] + "…"
        nxt = "✓ puri" if r["done"] else r["next"]
        print(f"{label(r):<8} {name:<{nw}} {marks}  {nxt}")
    done = sum(r["done"] for r in rows)
    print(f"\nKul {len(rows)} stories: {done} puri, {len(rows) - done} baaki.")
    pending = [r for r in rows if not r["done"]]
    if pending:
        print("\nYe reels baaki hain:")
        for r in pending:
            print(f"  - {label(r)}  {r['name']}  ->  {r['next']}")


def write_reports(rows, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "REEL STATUS.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "story", "id", "reel"] + COLS + ["agla kaam", "folder"])
        for r in rows:
            w.writerow([r["category"], r["story"], r["id"], r["name"]] +
                       ["haan" if r["have"][c] else "nahi" for c in COLS] + [r["next"], r["folder"]])

    html_path = os.path.join(out_dir, "REEL STATUS.html")
    done = sum(r["done"] for r in rows)
    trs = []
    for r in rows:
        cells = "".join(f'<td class="{"y" if r["have"][c] else "n"}">{"✓" if r["have"][c] else "–"}</td>'
                        for c in COLS)
        trs.append(f'<tr class="{"done" if r["done"] else "todo"}"><td>{html.escape(label(r))}</td>'
                   f'<td>{html.escape(r["name"])}</td>{cells}<td>{html.escape(r["next"])}</td></tr>')
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>Reel Status</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#faf6ee;color:#222;margin:16px}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
th,td{{border:1px solid #ddd;padding:5px 8px;text-align:left}} th{{background:#222;color:#fff;position:sticky;top:0}}
td.y{{background:#d9f2d9;text-align:center}} td.n{{background:#f8dada;text-align:center}}
tr.done td:first-child{{border-left:5px solid #2a2}} tr.todo td:first-child{{border-left:5px solid #d33}}
label{{cursor:pointer}}
</style></head><body>
<h2>theshivamiq – Reel Status</h2>
<p>{datetime.now():%d %b %Y, %H:%M} &nbsp;|&nbsp; Kul {len(rows)} &nbsp;|&nbsp; Puri {done} &nbsp;|&nbsp; Baaki {len(rows) - done}
&nbsp; <label><input type="checkbox" onchange="document.querySelectorAll('tr.done').forEach(t=>t.style.display=this.checked?'none':'')"> sirf baaki dikhao</label></p>
<table><tr><th>Story</th><th>Reel</th>{"".join(f"<th>{c}</th>" for c in COLS)}<th>Agla kaam</th></tr>
{chr(10).join(trs)}
</table></body></html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)
    return html_path, csv_path


def main(argv=None):
    T.utf8_console()
    ap = argparse.ArgumentParser(description="theshivamiq reel status")
    ap.add_argument("--baaki", action="store_true", help="sirf adhoori reels dikhao")
    ap.add_argument("--category", type=int, help="sirf is category ki stories")
    ap.add_argument("--report", action="store_true", help="output\\ mein HTML + CSV report bhi banao")
    a = ap.parse_args(argv)
    if not os.path.isdir(T.STORY_ROOT):
        print(f"reels story folder nahi mila: {T.STORY_ROOT}")
        return 1
    rows = scan_all(category=a.category)
    if not rows:
        print("Koi 'Category N\\Story NN' folder nahi mila.")
        return 0
    print_table(rows, only_pending=a.baaki)
    if a.report:
        h, c = write_reports(rows, os.path.join(T.BASE, "output"))
        print(f"\nReport bani: {h}\n             {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
