# theshivamiq – CLEANUP (purani kachra files ki list, chaho to Recycle Bin)
#
# Sirf code folder ke ye do folder dekhta hai:
#   output\  -> "<reel> - CHECK.png" (frame grid) aur "<story> - IMAGES.png" (contact sheet)
#   work\    -> voice ki temp files (.lock files kabhi nahi)
# Story folder, voice\, cases\, assets\, MP4 – KABHI nahi chhuta.
# Default sirf LIST dikhata hai. --delete par Recycle Bin mein bhejta hai (permanent delete nahi,
# galti ho to Recycle Bin se Restore kar lo). Naye files (--days se kam purani) chhod deta hai.
#
#   py cleanup.py                  list (3 din se purani)
#   py cleanup.py --days 10        10 din se purani
#   py cleanup.py --delete         list + poochh kar Recycle Bin
#   (ya double-click: CLEANUP.bat)

import argparse, fnmatch, os, sys, time
from datetime import datetime

import tools_common as T

OUTPUT_PATTERNS = ["* - CHECK.png", "* - IMAGES.png"]
NEVER_FOLDERS = ["voice", "cases", "assets", "music", "sfx"]


def _inside(path, folder):
    path, folder = os.path.normcase(os.path.realpath(path)), os.path.normcase(os.path.realpath(folder))
    return path == folder or path.startswith(folder.rstrip("\\/") + os.sep)


def is_safe(path, base, story_root):
    """Sirf output\\ ya work\\ ke andar, aur kabhi voice\\ / story folder / .lock nahi."""
    if path.lower().endswith(".lock"):
        return False
    if not (_inside(path, os.path.join(base, "output")) or _inside(path, os.path.join(base, "work"))):
        return False
    if any(_inside(path, os.path.join(base, f)) for f in NEVER_FOLDERS):
        return False
    if story_root and _inside(path, story_root):
        return False
    return True


def find_junk(base=None, days=3, now=None, story_root=None):
    """[(path, kind, size, mtime)] – jo days se purani hain."""
    base = base or T.BASE
    story_root = story_root if story_root is not None else T.STORY_ROOT
    now = now or time.time()
    cutoff = now - days * 86400
    found = []
    out = os.path.join(base, "output")
    if os.path.isdir(out):
        for name in sorted(os.listdir(out)):
            p = os.path.join(out, name)
            if os.path.isfile(p):
                for pat in OUTPUT_PATTERNS:
                    if fnmatch.fnmatch(name, pat):
                        found.append((p, "CHECK grid" if "CHECK" in pat else "contact sheet"))
    work = os.path.join(base, "work")
    if os.path.isdir(work):
        for root, dirs, files in os.walk(work):
            for name in sorted(files):
                found.append((os.path.join(root, name), "work temp"))
    result = []
    for p, kind in found:
        if not is_safe(p, base, story_root):
            continue
        st = os.stat(p)
        if st.st_mtime <= cutoff:
            result.append((p, kind, st.st_size, st.st_mtime))
    return result


def recycle_windows(path):
    """Windows Recycle Bin (SHFileOperation + FOF_ALLOWUNDO). True = gaya."""
    import ctypes
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND), ("wFunc", wintypes.UINT),
                    ("pFrom", wintypes.LPCWSTR), ("pTo", wintypes.LPCWSTR),
                    ("fFlags", ctypes.c_ushort), ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", ctypes.c_void_p), ("lpszProgressTitle", wintypes.LPCWSTR)]

    FO_DELETE, FOF_SILENT, FOF_NOCONFIRMATION, FOF_ALLOWUNDO, FOF_NOERRORUI = 3, 4, 16, 64, 1024
    op = SHFILEOPSTRUCTW(wFunc=FO_DELETE, pFrom=os.path.abspath(path) + "\0",
                         fFlags=FOF_SILENT | FOF_NOCONFIRMATION | FOF_ALLOWUNDO | FOF_NOERRORUI)
    return ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op)) == 0 and not os.path.exists(path)


def default_recycler():
    if os.name == "nt":
        return recycle_windows
    try:
        from send2trash import send2trash

        def _s2t(p):
            send2trash(p)
            return not os.path.exists(p)
        return _s2t
    except ImportError:
        return None


def send_to_recycle(items, base=None, story_root=None, recycler=None):
    """(gaye, nahi gaye) count. Recycle Bin na ho to kuch delete nahi hota."""
    base = base or T.BASE
    story_root = story_root if story_root is not None else T.STORY_ROOT
    recycler = recycler or default_recycler()
    if recycler is None:
        raise RuntimeError("Recycle Bin nahi mila – permanent delete nahi karenge, kuch nahi hata.")
    ok = bad = 0
    for p, *_ in items:
        if not is_safe(p, base, story_root) or not os.path.isfile(p):
            bad += 1
            continue
        try:
            recycler(p)
        except Exception:
            pass
        if os.path.exists(p):
            bad += 1
        else:
            ok += 1
    return ok, bad


def main(argv=None):
    T.utf8_console()
    ap = argparse.ArgumentParser(description="theshivamiq cleanup")
    ap.add_argument("--days", type=float, default=3, help="itne din se purani files (default 3)")
    ap.add_argument("--delete", action="store_true", help="Recycle Bin mein bhejo")
    ap.add_argument("--yes", action="store_true", help="--delete ke saath bina pooche")
    a = ap.parse_args(argv)

    items = find_junk(days=a.days)
    if not items:
        print(f"Saaf hai! output\\ / work\\ mein {a.days:g} din se purani koi kachra file nahi.")
        return 0
    total = 0
    print(f"{'Size':>9}  {'Date':<16}  {'Kya':<13}  File")
    for p, kind, size, mt in items:
        total += size
        print(f"{T.human_size(size):>9}  {datetime.fromtimestamp(mt):%d-%m-%Y %H:%M}  {kind:<13}  "
              f"{os.path.relpath(p, T.BASE)}")
    print(f"\n{len(items)} files, kul {T.human_size(total)} (sirf output\\ aur work\\ ki; MP4/voice/story nahi).")
    if not a.delete:
        print("Kuch delete nahi kiya. Hatana ho to: py cleanup.py --delete  (Recycle Bin mein jaayengi)")
        return 0
    if not a.yes:
        ans = input("\nIn sabko Recycle Bin mein bhejein? 'haan' likho: ").strip().lower()
        if ans not in ("haan", "ha", "han", "yes", "y"):
            print("Theek hai, kuch nahi hataya.")
            return 0
    try:
        ok, bad = send_to_recycle(items)
    except RuntimeError as e:
        print(e)
        return 1
    print(f"{ok} files Recycle Bin mein gayi." + (f" {bad} nahi gayi (khuli ho sakti hain)." if bad else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
