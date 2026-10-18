# VO_MAIN + CTA + SIGNATURE -> tighten -> (optional think pause) -> voice\<name>.m4a ; prints word times
# Kai chats ek saath chalayein to voice_queue alag slot deta hai / line mein rokta hai.
import json, re, subprocess, sys, os, unicodedata
BASE = os.path.dirname(os.path.abspath(__file__))   # code folder (pehle yahan C:\Users\Hp\... hardcoded tha)
sys.path.insert(0, BASE)
from make_reel import FFMPEG, audio_duration
from voice_queue import slot, safe_replace

COMMON = r"C:\Users\Hp\Desktop\reels story\Common"
VOICE_DIR = os.path.join(BASE, "voice")


def remap(t, table):
    for a, b, na, nb in table:
        if a - 0.05 <= t <= b + 0.05:
            return na + (min(max(t, a), b) - a) * (nb - na) / (b - a)
    prev = [r for r in table if r[1] < t]
    return prev[-1][3] if prev else 0.0


def find_think(text, think_before):
    """think wali line ka AAKHRI match ("pakad liya" wali line kahani ke end mein hoti hai).
    Nukta (ज़ / ड़) do tarah se type hota hai -> dono roop try karo. Na mile to -1."""
    for form in (think_before, unicodedata.normalize("NFC", think_before), unicodedata.normalize("NFD", think_before)):
        pos = text.rfind(form)
        if pos >= 0:
            return pos
    return -1


def main(argv):
    if len(argv) < 2:
        sys.exit('Aise chalao: py -u build_voice.py "<story folder>" "<NN Title>" ["डिटेक्टिव शिवम" 3.0]')
    os.chdir(BASE)
    if hasattr(sys.stdout, "reconfigure"):   # Devanagari shabd print karte waqt crash na ho (pipe / dusra script padhe tab)
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    story, name = argv[0].strip().strip('"').rstrip("\\/"), argv[1]
    think_before = argv[2] if len(argv) > 2 else None   # text jis line se pehle pause
    THINK = float(argv[3]) if len(argv) > 3 else 3.0
    # hook stories ka alag CTA: env CTA_FILE=...\CTA_HOOK_KATIL.mp3 (warna normal CTA_HI)
    cta_file = os.environ.get("CTA_FILE") or os.path.join(COMMON, "CTA_HI.mp3")
    vo, timing = os.path.join(story, "VO_MAIN.mp3"), os.path.join(story, "VO_MAIN_timing.json")
    for p in (vo, timing, cta_file, os.path.join(COMMON, "SIGNATURE_HI.mp3")):
        if not os.path.exists(p):
            sys.exit(f"File nahi mili: {p}")

    j = json.load(open(timing, encoding="utf8"))
    chars, st, en = j["characters"], j["character_start_times_seconds"], j["character_end_times_seconds"]
    text = "".join(chars)
    pos = None
    if think_before:   # pehle hi check karo, warna poora kaam karke aakhir mein crash hota
        pos = find_think(text, think_before)
        if pos <= 0:
            sys.exit(f"THINK text '{think_before}' voice ke text (VO_MAIN_timing.json) mein nahi mila "
                     "(ya bilkul shuru mein hai). "
                     "Script se same shabd copy karke do.")

    with slot("voice") as work:
        cat = os.path.join(work, "cat_vo.wav")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-i", vo,
                        "-i", cta_file, "-i", os.path.join(COMMON, "SIGNATURE_HI.mp3"),
                        "-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1,aformat=sample_rates=44100:channel_layouts=mono[o]",
                        "-map", "[o]", cat], check=True)
        tight = os.path.join(work, "tight_vo.m4a")
        res = subprocess.run([sys.executable, os.path.join(BASE, "tighten_voice.py"), cat, tight],
                             capture_output=True, text=True)
        if res.returncode != 0:
            sys.exit("tighten_voice fail hua:\n" + res.stderr)
        out = res.stdout
        table = [tuple(map(float, re.findall(r"[\d.]+", l)[:4])) for l in out.splitlines() if "->" in l and re.search(r"\d", l)]

        words = []
        for m in re.finditer(r"[^\s]+", text):
            w = m.group()
            if re.fullmatch(r"\[[^\]]*\]", w):
                continue
            words.append([re.sub(r"\[[^\]]*\]", "", w), remap(st[m.start()], table), remap(en[m.end() - 1], table), m.start()])

        os.makedirs(VOICE_DIR, exist_ok=True)
        final = os.path.join(VOICE_DIR, name + ".m4a")
        ready = os.path.join(work, "final.m4a")
        shift_at = None
        if think_before:
            first = [w for w in words if w[3] >= pos][0]
            prev = [w for w in words if w[3] < pos][-1]
            shift_at = (prev[2] + first[1]) / 2
            subprocess.run([FFMPEG, "-v", "error", "-y", "-i", tight, "-filter_complex",
                            f"[0:a]atrim=0:{shift_at:.3f},asetpts=PTS-STARTPTS[a];"
                            f"aevalsrc=0:d={THINK}:s=44100,aformat=channel_layouts=mono[g];"
                            f"[0:a]atrim={shift_at:.3f},asetpts=PTS-STARTPTS[b];[a][g][b]concat=n=3:v=0:a=1[o]",
                            "-map", "[o]", "-c:a", "aac", "-b:a", "192k", ready], check=True)
            for w in words:
                if w[1] >= shift_at:
                    w[1] += THINK; w[2] += THINK
            print(f"THINK pause {shift_at:.2f} -> {shift_at + THINK:.2f}")
        else:
            ready = tight
        safe_replace(ready, final)

    for w in words:
        print(f"{w[1]:6.2f} {w[2]:6.2f} {w[0]}")
    last = table[-2:] if len(table) >= 2 else table * 2   # bahut chhoti voice mein ek hi tukda ho sakta hai
    print(f"last chunks start: {last[0][2]:.2f} {last[1][2]:.2f} (pre-think)  total {audio_duration(final):.2f}")


if __name__ == "__main__":
    main(sys.argv[1:])
