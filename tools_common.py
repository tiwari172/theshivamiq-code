# theshivamiq – naye helper scripts (doctor / reel_status / cleanup / code_sync) ka common hissa
#
# Purane scripts isko use NAHI karte, sirf naye helper. Yahan sirf folder ke raaste aur chhote kaam hain.
# Test ke liye raaste env se badal sakte ho:
#   THESHIVAMIQ_BASE        = code folder   (default: is file ka folder)
#   THESHIVAMIQ_STORY_ROOT  = reels story   (default: C:\Users\Hp\Desktop\reels story)

import glob, os, re, shutil, sys

BASE = os.environ.get("THESHIVAMIQ_BASE") or os.path.dirname(os.path.abspath(__file__))
STORY_ROOT = os.environ.get("THESHIVAMIQ_STORY_ROOT") or r"C:\Users\Hp\Desktop\reels story"


def utf8_console():
    """Windows console mein Devanagari / ✓ print karte waqt crash na ho."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def common_dir(story_root=None):
    return os.path.join(story_root or STORY_ROOT, "Common")


def story_folders(story_root=None):
    """Saari 'Category N\\Story NN' folders, dono layout mein:
    reels story\\Category N\\Story NN   aur   reels story\\<koi bhi>\\Category N\\Story NN"""
    root = story_root or STORY_ROOT
    hits = glob.glob(os.path.join(root, "Category *", "Story *")) + \
        glob.glob(os.path.join(root, "*", "Category *", "Story *"))
    out = {}
    for p in hits:
        if os.path.isdir(p):
            out[os.path.normcase(os.path.abspath(p))] = p
    return sorted(out.values(), key=story_sort_key)


def story_numbers(folder):
    """(category, story) number folder ke naam se, na mile to None."""
    cat = re.search(r"Category\s*(\d+)", os.path.basename(os.path.dirname(folder)), re.I)
    sto = re.search(r"Story\s*(\d+)", os.path.basename(folder), re.I)
    return (int(cat.group(1)) if cat else None, int(sto.group(1)) if sto else None)


def story_sort_key(folder):
    c, s = story_numbers(folder)
    return (c if c is not None else 9999, s if s is not None else 9999, folder.lower())


def find_ffmpeg():
    """make_reel.py jaisa hi: PATH par, warna WinGet wali jagah. Na mile to None (exit nahi)."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    pattern = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet",
                           "Packages", "Gyan.FFmpeg*", "*", "bin", "ffmpeg.exe")
    hits = glob.glob(pattern)
    return hits[0] if hits else None


def find_ffprobe(ffmpeg=None):
    exe = shutil.which("ffprobe")
    if exe:
        return exe
    if ffmpeg:
        for name in ("ffprobe.exe", "ffprobe"):
            p = os.path.join(os.path.dirname(ffmpeg), name)
            if os.path.exists(p):
                return p
    return None


def human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
