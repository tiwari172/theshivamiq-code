# VO_MAIN + CTA + SIGNATURE -> tighten -> (optional think pause) -> voice\<name>.m4a ; prints word times
# Kai chats ek saath chalayein to voice_queue alag slot deta hai / line mein rokta hai.
import json, re, subprocess, sys, os
os.chdir(r"C:\Users\Hp\Desktop\theshivamiq code")
sys.path.insert(0, os.getcwd())
from make_reel import FFMPEG, audio_duration
from voice_queue import slot, safe_replace

story, name = sys.argv[1], sys.argv[2]
think_before = sys.argv[3] if len(sys.argv) > 3 else None   # text jis line se pehle pause
THINK = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0
common = r"C:\Users\Hp\Desktop\reels story\Common"
# hook stories ka alag CTA: env CTA_FILE=...\CTA_HOOK_KATIL.mp3 (warna normal CTA_HI)
cta_file = os.environ.get("CTA_FILE") or os.path.join(common, "CTA_HI.mp3")


def remap(t, table):
    for a, b, na, nb in table:
        if a - 0.05 <= t <= b + 0.05:
            return na + (min(max(t, a), b) - a) * (nb - na) / (b - a)
    prev = [r for r in table if r[1] < t]
    return prev[-1][3] if prev else 0.0


with slot("voice") as work:
    cat = os.path.join(work, "cat_vo.wav")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", os.path.join(story, "VO_MAIN.mp3"),
                    "-i", cta_file, "-i", os.path.join(common, "SIGNATURE_HI.mp3"),
                    "-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1,aformat=sample_rates=44100:channel_layouts=mono[o]",
                    "-map", "[o]", cat], check=True)
    tight = os.path.join(work, "tight_vo.m4a")
    out = subprocess.run([sys.executable, "tighten_voice.py", cat, tight], capture_output=True, text=True, check=True).stdout
    table = [tuple(map(float, re.findall(r"[\d.]+", l)[:4])) for l in out.splitlines() if "->" in l and re.search(r"\d", l)]

    j = json.load(open(os.path.join(story, "VO_MAIN_timing.json"), encoding="utf8"))
    chars, st, en = j["characters"], j["character_start_times_seconds"], j["character_end_times_seconds"]
    text = "".join(chars)
    words = []
    for m in re.finditer(r"[^\s]+", text):
        w = m.group()
        if re.fullmatch(r"\[[^\]]*\]", w):
            continue
        words.append([re.sub(r"\[[^\]]*\]", "", w), remap(st[m.start()], table), remap(en[m.end() - 1], table), m.start()])

    final = os.path.join("voice", name + ".m4a")
    ready = os.path.join(work, "final.m4a")
    shift_at = None
    if think_before:
        pos = text.rfind(think_before)   # aakhri match: "pakad liya" wali line kahani ke end mein hoti hai
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
print(f"last chunks start: {table[-2][2]:.2f} {table[-1][2]:.2f} (pre-think)  total {audio_duration(final):.2f}")
