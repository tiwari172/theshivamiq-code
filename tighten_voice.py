# theshivamiq – Voice tight karo
# Lambe pause chhote karta hai aur thodi speed badhata hai (awaaz patli nahi hoti).
#
#   python tighten_voice.py "voice\purani.m4a" "voice\nayi.m4a"
#   python tighten_voice.py "voice\purani.m4a" "voice\nayi.m4a" --end 46.3-49.6
#        --end A-B  -> purani voice ka A se B second wala hissa sabse aakhir mein le jao
#                      (jaise signature ko CTA ke baad)
#
# Neeche har tukde ka purana aur naya time print hota hai -> CSV banane mein kaam aata hai.

import os, re, subprocess, sys
from make_reel import FFMPEG, audio_duration
from voice_queue import safe_replace

GAP = 0.28          # do tukdon ke beech ka pause (seconds)
MIN_SILENCE = 0.30  # isse lamba chup -> kaat kar GAP kar do
SILENCE_DB = -35    # isse dheemi awaaz = chup
PAD = 0.06          # awaaz ke dono taraf thoda sa chhodo
SPEED = 1.07        # 1.0 = normal, 1.07 = 7% tez


def speech_chunks(path):
    out = subprocess.run([FFMPEG, "-hide_banner", "-i", path, "-af",
                          f"silencedetect=noise={SILENCE_DB}dB:d={MIN_SILENCE}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return chunks_from_log(out, audio_duration(path))


def chunks_from_log(out, total):
    """silencedetect ke log se bolne wale tukde. FFmpeg kabhi 'silence_start: -0.002' (minus) deta hai."""
    starts = [max(0.0, float(x)) for x in re.findall(r"silence_start: (-?[\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", out)]
    chunks, cur = [], 0.0
    for s, e in zip(starts, ends + [total] * (len(starts) - len(ends))):
        if s > cur:
            chunks.append((max(0, cur - PAD), min(total, s + PAD)))
        cur = e
    if cur < total - 0.05:
        chunks.append((max(0, cur - PAD), total))
    return chunks


def main():
    if len(sys.argv) < 3:
        sys.exit('Aise chalao: py tighten_voice.py "voice\\purani.m4a" "voice\\nayi.m4a" [--end A-B]')
    src, dst = sys.argv[1], sys.argv[2]
    chunks = speech_chunks(src)
    if not chunks:
        sys.exit(f"Voice mein koi awaaz nahi mili (poori chup?): {src}")
    if "--end" in sys.argv:
        a, b = map(float, sys.argv[sys.argv.index("--end") + 1].split("-"))
        for cut in (a, b):   # jo tukda A ya B ke aar-paar hai use wahin todo
            chunks = [p for c in chunks for p in
                      ([(c[0], cut), (cut, c[1])] if c[0] < cut < c[1] else [c])]
        tail = [c for c in chunks if a <= (c[0] + c[1]) / 2 <= b]
        chunks = [c for c in chunks if c not in tail] + tail
    parts, labels, t, table = [], "", 0.0, []
    for i, (a, b) in enumerate(chunks):
        parts.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,"
                     f"aformat=sample_rates=44100:channel_layouts=mono[s{i}];")
        labels += f"[s{i}]"
        table.append((a, b, t / SPEED, (t + b - a) / SPEED))
        t += b - a
        if i < len(chunks) - 1:
            parts.append(f"aevalsrc=0:d={GAP}:s=44100,aformat=channel_layouts=mono[g{i}];")
            labels += f"[g{i}]"
            t += GAP
    n = len(chunks) * 2 - 1
    fc = "".join(parts) + f"{labels}concat=n={n}:v=0:a=1,atempo={SPEED}[o]"
    root, ext = os.path.splitext(dst)
    part = f"{root}.part{os.getpid()}{ext}"   # poori bane tab hi final naam (dusri chat aadhi file na padhe)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-filter_complex", fc,
                    "-map", "[o]", "-c:a", "aac", "-b:a", "192k", part], check=True)
    safe_replace(part, dst)
    print("  purana time      ->  naya time")
    for a, b, na, nb in table:
        print(f"  {a:6.2f} - {b:6.2f}  ->  {na:6.2f} - {nb:6.2f}")
    print(f"Pehle: {audio_duration(src):.1f}s   Ab: {audio_duration(dst):.1f}s")


if __name__ == "__main__":
    main()
