# ANN Detective Rank: ElevenLabs voice -> tighten (gap max 0.5s, 1.05x) -> + SIGNATURE_HI -> voice\ANN Detective Rank.m4a
# + voice\ANN Detective Rank - words.json  [[shabd, start, end, line], ...]
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, CODE)
import eleven_voice as ev
import make_reel as mr
from voice_queue import slot

STORY = r"C:\Users\Hp\Desktop\reels story\category\ANNOUNCEMENT Detective Rank"
TXT = os.path.join(STORY, "VO_DETECTIVE_RANK.txt")
MP3 = os.path.join(STORY, "VO_DETECTIVE_RANK.mp3")
SIG = r"C:\Users\Hp\Desktop\reels story\Common\SIGNATURE_HI.mp3"
OUT = os.path.join(CODE, "voice", "ANN Detective Rank.m4a")
WORDS = os.path.join(CODE, "voice", "ANN Detective Rank - words.json")
MAXGAP, SPEED, SIG_GAP = 0.5, 1.05, 0.35

# 1) ElevenLabs (pehle se bani ho to credits nahi khaata)
if not os.path.exists(MP3):
    key = ev.read_key()
    ev.speak(key, ev.voice_id(key), open(TXT, encoding="utf-8").read().strip(), MP3)
al = json.load(open(MP3[:-4] + "_timing.json", encoding="utf-8"))

# 2) char alignment -> shabd (line ke saath), [tags] chhod kar
words, cur, line, tag = [], None, 0, False
for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
    if ch == "[":
        tag = True
    if tag:
        if ch == "]":
            tag = False
        continue
    if ch in " \n":
        if cur:
            words.append(cur); cur = None
        if ch == "\n":
            line += 1
        continue
    if cur is None:
        cur = [ch, s, e, line]
    else:
        cur[0] += ch; cur[2] = e
if cur:
    words.append(cur)

# 3) lambe gap kaato
keep, removed = [], []   # keep = [(a, b)] audio ke hisse
a = max(0.0, words[0][1] - 0.08)
for w, nx in zip(words, words[1:]):
    gap = nx[1] - w[2]
    if gap > MAXGAP:
        cut_a, cut_b = w[2] + MAXGAP / 2, nx[1] - MAXGAP / 2
        keep.append((a, cut_a)); removed.append((cut_a, cut_b)); a = cut_b
keep.append((a, words[-1][2] + 0.25))
start0 = keep[0][0]


def newt(t):
    shift = start0 + sum(b - a for a, b in removed if b <= t)
    return round((t - shift) / SPEED, 3)


with slot("voice") as tmp:
    parts = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[p{i}];" for i, (a, b) in enumerate(keep))
    fc = (parts + "".join(f"[p{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1,atempo={SPEED}[v];"
          f"aevalsrc=0:d={SIG_GAP}:s=44100[z];[1:a]aresample=44100[sg];[v]aresample=44100[v2];"
          "[v2][z][sg]concat=n=3:v=0:a=1[out]")
    wav = os.path.join(tmp, "vo.wav")
    subprocess.run([mr.FFMPEG, "-y", "-loglevel", "error", "-i", MP3, "-i", SIG, "-filter_complex", fc,
                    "-map", "[out]", "-ac", "1", "-ar", "44100", wav], check=True)
    subprocess.run([mr.FFMPEG, "-y", "-loglevel", "error", "-i", wav, "-c:a", "aac", "-b:a", "192k", OUT], check=True)

out = [[w, newt(s), newt(e), ln] for w, s, e, ln in words]
vo_end = round(sum(b - a for a, b in keep) / SPEED, 3)
dur = float(subprocess.run([mr.FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT],
                           capture_output=True, text=True).stdout)
sig_w = "शिवम की नज़र से कोई नहीं बचता।".split()
s0, s1 = vo_end + SIG_GAP + 0.1, dur - 0.15
step = (s1 - s0) / len(sig_w)
out += [[w, round(s0 + i * step, 3), round(s0 + (i + 1) * step, 3), line + 1] for i, w in enumerate(sig_w)]
json.dump(out, open(WORDS, "w", encoding="utf-8"), ensure_ascii=False)
print(f"voice {dur:.2f}s (VO {vo_end:.2f}s + signature), {len(removed)} gap kate -> {OUT}")
ln_prev = -1
for w, s, e, ln in out:
    if ln != ln_prev:
        print(f"\nL{ln + 1:02d} {s:6.2f}", end=" ")
        ln_prev = ln
    print(w, end=" ")
print()
