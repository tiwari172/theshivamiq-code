# theshivamiq – SETUP CHECK (doctor)
#
# Laptop par reel banane ke liye sab cheezein theek hain ya nahi, ek baar mein check karta hai:
#   ffmpeg/ffprobe, python packages, folders, bg music, sfx, Common ki CTA/Signature,
#   assets (BG, logo, Shivam poses), fonts, elevenlabs key (key kabhi print nahi hoti), disk space.
# Har kami ke saath "KYA KARO" likha aata hai. Kuch nahi badalta (sirf --fix par music copy).
#
#   py doctor.py           sirf check
#   py doctor.py --fix     music\bg music.mp3 na ho to reels story\Common se copy kar deta hai
#   (ya double-click: SETUP CHECK.bat)

import argparse, csv, glob, importlib.util, os, shutil, subprocess, sys

import tools_common as T

OK, WARN, FAIL = "OK", "DHYAAN", "KAMI"

# (import naam, pip naam, kaun use karta hai, zaroori?)
PACKAGES = [
    ("PIL", "pillow", "make_reel / prep_story / make_cards / make_cover", True),
    ("numpy", "numpy", "make_cover2 / make_sfx / sab_pe_shak", True),
    ("faster_whisper", "faster-whisper", "timing (Whisper) / sab_pe_shak", True),
    ("openpyxl", "openpyxl", "sab_pe_shak / yt_scheduler (Excel padhna)", False),
    ("requests", "requests", "comment_checker", False),
]
# CLAUDE.md mein jo sfx har reel mein lagte hain
SFX_NEEDED = ["pop", "pop2", "swish", "whoosh", "boom", "ding", "heartbeat", "tick_fast"]
COMMON_FILES = ["CTA_HI.mp3", "SIGNATURE_HI.mp3", "bg music.mp3"]
ASSETS_NEEDED = ["BG_MAIN.png", "LOGO_ROUND.png", "S01.png", "S02.png", "S06.png", "S16.png", "S17.png"]
FONTS = [r"C:\Windows\Fonts\ariblk.ttf", r"C:\Windows\Fonts\impact.ttf"]
FOLDERS = ["assets", "voice", "cases", "sfx", "music", "output"]
MIN_FREE_GB = 5


class Report:
    def __init__(self):
        self.items = []   # (status, section, msg, fix)

    def add(self, status, section, msg, fix=""):
        self.items.append((status, section, msg, fix))

    def count(self, status):
        return sum(1 for i in self.items if i[0] == status)


def sfx_file(sfx_dir, name):
    for ext in (".wav", ".mp3"):
        p = os.path.join(sfx_dir, name + ext)
        if os.path.exists(p):
            return p
    return None


def sfx_used_in_cases(cases_dir):
    """cases\\*.csv ke 'sfx' column mein jo naam aaye hain -> {naam: pehli csv}"""
    used = {}
    for path in sorted(glob.glob(os.path.join(cases_dir, "*.csv"))):
        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    name = (row.get("sfx") or "").strip().lower()
                    if name and all(c.isalnum() or c in "_-" for c in name):
                        used.setdefault(name, os.path.basename(path))
        except Exception:
            continue
    return used


def git_secret_status(base, filename):
    """'tracked' (git mein chala gaya!) / 'ignored' / 'not-ignored' / None (git nahi)"""
    if not shutil.which("git") or not os.path.isdir(os.path.join(base, ".git")):
        return None
    run = lambda *a: subprocess.run(["git", "-C", base, *a], capture_output=True, text=True)
    if run("ls-files", "--error-unmatch", filename).returncode == 0:
        return "tracked"
    return "ignored" if run("check-ignore", "-q", filename).returncode == 0 else "not-ignored"


def check_all(base=None, story_root=None, fix=False, windows=None):
    base = base or T.BASE
    story_root = story_root or T.STORY_ROOT
    windows = (os.name == "nt") if windows is None else windows
    common = T.common_dir(story_root)
    r = Report()

    # --- Python ---
    v = sys.version_info
    if v < (3, 9):
        r.add(FAIL, "Python", f"Python {v.major}.{v.minor} purana hai",
              "python.org se Python 3.11+ install karo (Add to PATH tick karna).")
    else:
        r.add(OK, "Python", f"Python {v.major}.{v.minor}.{v.micro}")
    if windows and not shutil.which("py"):
        r.add(WARN, "Python", "'py' launcher nahi mila",
              "Python dobara install karo, 'py launcher' wala option tick rakho.")

    # --- ffmpeg ---
    ff = T.find_ffmpeg()
    if ff:
        r.add(OK, "FFmpeg", f"ffmpeg mila: {ff}")
    else:
        r.add(FAIL, "FFmpeg", "ffmpeg nahi mila (iske bina reel/voice nahi banegi)",
              "PowerShell mein chalao: winget install Gyan.FFmpeg  (phir laptop restart)")
    probe = T.find_ffprobe(ff)
    if probe:
        r.add(OK, "FFmpeg", "ffprobe mila")
    else:
        r.add(FAIL, "FFmpeg", "ffprobe nahi mila", "winget install Gyan.FFmpeg  (ffprobe saath aata hai)")

    # --- packages ---
    for mod, pip, who, needed in PACKAGES:
        if importlib.util.find_spec(mod):
            r.add(OK, "Packages", f"{pip} installed")
        else:
            r.add(FAIL if needed else WARN, "Packages", f"{pip} nahi hai ({who})",
                  f"PowerShell mein chalao: py -m pip install {pip}")

    # --- folders ---
    for name in FOLDERS:
        p = os.path.join(base, name)
        if os.path.isdir(p):
            r.add(OK, "Folders", f"{name}\\ hai")
        else:
            r.add(FAIL if name in ("assets", "sfx", "cases") else WARN, "Folders", f"{name}\\ folder nahi hai",
                  f"Code folder mein '{name}' naam ka folder banao.")
    if os.path.isdir(story_root):
        n = len(T.story_folders(story_root))
        r.add(OK, "Folders", f"reels story mili ({n} story folders)")
    else:
        r.add(FAIL, "Folders", f"reels story folder nahi mila: {story_root}",
              "Desktop par 'reels story' folder hona chahiye (naam check karo).")

    # --- music ---
    music = os.path.join(base, "music", "bg music.mp3")
    common_music = os.path.join(common, "bg music.mp3")
    if os.path.exists(music):
        r.add(OK, "Music", "music\\bg music.mp3 hai")
    elif os.path.exists(common_music) and fix:
        os.makedirs(os.path.dirname(music), exist_ok=True)
        shutil.copy2(common_music, music)
        r.add(OK, "Music", "music\\bg music.mp3 nahi thi -> reels story\\Common se copy kar di")
    elif os.path.exists(common_music):
        r.add(FAIL, "Music", "music\\bg music.mp3 nahi hai (reel bina music ke banegi!)",
              "SETUP CHECK.bat mein 'fix' likho (ya: py doctor.py --fix) -> Common se copy ho jaayegi.")
    else:
        r.add(FAIL, "Music", "bg music.mp3 na music\\ mein hai na reels story\\Common mein",
              "bg music.mp3 dhoondh kar code folder ke music\\ mein rakho.")

    # --- sfx ---
    sfx_dir = os.path.join(base, "sfx")
    missing = [s for s in SFX_NEEDED if not sfx_file(sfx_dir, s)]
    if missing:
        r.add(FAIL, "SFX", "ye sfx nahi mile: " + ", ".join(missing),
              "sfx\\ folder mein <naam>.wav ya .mp3 rakho (purane laptop/backup se). "
              "tick_fast dobara chahiye to Claude ko bolo.")
    else:
        r.add(OK, "SFX", f"zaroori {len(SFX_NEEDED)} sfx hain")
    extra = {k: v for k, v in sfx_used_in_cases(os.path.join(base, "cases")).items()
             if k not in SFX_NEEDED and not sfx_file(sfx_dir, k)}
    if extra:
        r.add(WARN, "SFX", "CSV mein use hue par sfx\\ mein nahi: " +
              ", ".join(f"{k} ({v})" for k, v in sorted(extra.items())),
              "Ye reel dobara render karni ho to ye sfx chahiye: VOICE BANAO.bat -> 'sfx' (sfx_list.txt se banti hain).")

    # --- Common ---
    for name in COMMON_FILES:
        if os.path.exists(os.path.join(common, name)):
            r.add(OK, "Common", f"Common\\{name} hai")
        else:
            fix_msg = ("CTA/Signature dobara generate MAT karo – purane backup se reels story\\Common mein rakho."
                       if name != "bg music.mp3" else "bg music.mp3 reels story\\Common mein rakho.")
            r.add(FAIL if name != "bg music.mp3" else WARN, "Common", f"Common\\{name} nahi mili", fix_msg)

    # --- assets ---
    miss = [a for a in ASSETS_NEEDED if not os.path.exists(os.path.join(base, "assets", a))]
    if miss:
        r.add(FAIL, "Assets", "assets\\ mein nahi: " + ", ".join(miss),
              "Ye images purane backup se assets\\ mein rakho (har reel mein lagti hain).")
    else:
        r.add(OK, "Assets", "BG, logo aur Shivam ke main poses hain")

    # --- fonts (sirf Windows) ---
    if windows:
        for font in FONTS:
            if os.path.exists(font):
                r.add(OK, "Fonts", os.path.basename(font) + " hai")
            else:
                r.add(FAIL, "Fonts", os.path.basename(font) + " nahi mila",
                      "Font file par right-click -> Install for all users.")

    # --- ElevenLabs key (kabhi print nahi) ---
    key = os.path.join(base, "elevenlabs_key.txt")
    if not os.path.exists(key):
        r.add(FAIL, "ElevenLabs", "elevenlabs_key.txt nahi mili (nayi voice nahi banegi)",
              "Code folder mein elevenlabs_key.txt banao, usme sirf API key paste karke save karo.")
    else:
        try:
            filled = bool(open(key, encoding="utf-8-sig").read().strip())
        except Exception:
            filled = False
        if filled:
            r.add(OK, "ElevenLabs", "elevenlabs_key.txt hai (key chhupi rakhi gayi)")
        else:
            r.add(FAIL, "ElevenLabs", "elevenlabs_key.txt khaali hai", "Usme API key paste karke save karo.")
        st = git_secret_status(base, "elevenlabs_key.txt")
        if st == "tracked":
            r.add(FAIL, "ElevenLabs", "KEY GIT MEIN CHALI GAYI HAI!",
                  "Turant Claude ko bolo. ElevenLabs website par key badal do (purani band karo).")
        elif st == "not-ignored":
            r.add(FAIL, "ElevenLabs", ".gitignore key ko nahi rok raha",
                  ".gitignore mein 'elevenlabs_key.txt' line honi chahiye – Claude ko bolo.")

    # --- disk ---
    try:
        free = shutil.disk_usage(base).free / 1024 ** 3
        if free < MIN_FREE_GB:
            r.add(WARN, "Disk", f"sirf {free:.1f} GB jagah bachi hai",
                  "CLEANUP.bat chala kar purani CHECK/contact sheet files Recycle Bin mein bhejo.")
        else:
            r.add(OK, "Disk", f"{free:.0f} GB jagah khaali")
    except Exception:
        pass
    return r


def print_report(r):
    mark = {OK: "  [OK]   ", WARN: "  [DHYAAN]", FAIL: "  [KAMI] "}
    section = None
    for status, sec, msg, fix in r.items:
        if sec != section:
            print(f"\n== {sec} ==")
            section = sec
        print(f"{mark[status]} {msg}")
        if fix and status != OK:
            print(f"           KYA KARO: {fix}")
    print("\n" + "=" * 60)
    k, w = r.count(FAIL), r.count(WARN)
    if not k and not w:
        print("Sab theek hai! Reel banane ke liye laptop taiyaar hai.")
    elif not k:
        print(f"Kaam chal jaayega, bas {w} cheezon par dhyaan do (upar [DHYAAN]).")
    else:
        print(f"{k} KAMI hai (upar [KAMI] wali lines) – 'KYA KARO' follow karo, phir dobara chalao.")


def main(argv=None):
    T.utf8_console()
    ap = argparse.ArgumentParser(description="theshivamiq setup check")
    ap.add_argument("--fix", action="store_true", help="music\\bg music.mp3 na ho to Common se copy karo")
    a = ap.parse_args(argv)
    print("theshivamiq – SETUP CHECK")
    print(f"Code folder : {T.BASE}\nreels story : {T.STORY_ROOT}")
    r = check_all(fix=a.fix)
    print_report(r)
    return 1 if r.count(FAIL) else 0


if __name__ == "__main__":
    sys.exit(main())
