# ANN Detective Points: captions (P) + mix.wav + index.html (engine + DATA + extra.js)
# py build.py            -> sab banao
# py build.py --noaudio  -> sirf index.html
import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, CODE)
import make_reel as mr

VOICE = os.path.join(CODE, "voice", "ANN Detective Points.m4a")
WORDS = json.load(open(os.path.join(CODE, "voice", "ANN Detective Points - words.json"), encoding="utf-8"))
END = 60.72         # voice 59.72 + 1 sec end card
lines = {}
for w, s, e, ln in WORDS:
    lines.setdefault(ln + 1, []).append((s, e))

# (line, Roman tukda, devanagari word index from-to)   CAPS shabd = peela
CHUNKS = [
    (1, "Somvaar se...", 0, 1), (1, "har comment ki KEEMAT hogi.", 2, 6),
    (2, "DETECTIVE POINTS!", 0, 1),
    (3, "Sahi jawab — 10 points.", 0, 4), (3, "Galat par bhi 1,", 5, 8), (3, "koshish ke liye.", 9, 11),
    (4, "Lekin asli khel hai...", 0, 3), (4, "SPEED ka.", 4, 5),
    (5, "Reel aane ke 1 minute baad", 0, 5), (5, "ghadi chalu...", 6, 7), (5, "30 second mein sahi —", 8, 12),
    (5, "10 aur,", 13, 14), (5, "1 minute mein 8...", 15, 18), (5, "1 ghante tak BONUS.", 19, 22),
    (6, "Par sirf PEHLA comment ginega...", 0, 5), (6, "jaldi mein galat likha,", 6, 9), (6, "to GAYA!", 10, 11),
    (7, "Har reel par pehle 3 sahi jawab —", 0, 7), (7, "10, 7 aur 5.", 8, 11),
    (8, "Roz aao, STREAK badhao...", 0, 3), (8, "5 din 15, 30 din 100...", 4, 9), (8, "aur poora saal — 1000!", 10, 15),
    (9, "Follow karo to 50,", 0, 3), (9, "story mein mention karo", 4, 7), (9, "to roz 15.", 8, 10),
    (10, "Naye case aate hain...", 0, 3), (10, "Somvaar se Shukravaar,", 4, 6), (10, "subah aur raat 8 baje...", 7, 11),
    (10, "Shanivaar-Ravivaar 9 baje.", 12, 14),
    (11, "Har hafte ke TOP 3...", 0, 4), (11, "Shivam ke saath PARTNER story mein!", 5, 10), (11, "Aur TOP 10 ko story mention.", 11, 16),
    (12, "Apne points dekho...", 0, 2), (12, "Telegram BOT par.", 3, 5),
    (13, "Somvaar se ghadi CHALU...", 0, 3), (13, "taiyaar ho?", 4, 5),
]
P = []
for ln, txt, a, b in CHUNKS:
    dv = lines[ln][a:b + 1]
    rw = txt.split(" ")
    if len(rw) == len(dv):
        times = dv
    else:  # Roman shabd dev range par barabar baanto
        s0, e0 = dv[0][0], dv[-1][1]
        step = (e0 - s0) / len(rw)
        times = [(s0 + i * step, s0 + (i + 1) * step) for i in range(len(rw))]
    P.append([[w, round(s, 2), round(e, 2)] for w, (s, e) in zip(rw, times)])

# ---------- audio ----------
SFX = [("heartbeat", 0.05), ("boom", 3.79), ("pop", 5.0), ("tick_fast", 8.93), ("swish", 14.57), ("hit", 23.09),
       ("ding", 26.29), ("boom", 34.14), ("pop", 37.18), ("whoosh", 47.2), ("ding", 52.3), ("whoosh", 53.82)]
MUTE = (0, 0)              # koi blackout nahi
DUCK = 56.5                # signature + end card par music 60%
if "--noaudio" not in sys.argv:
    music = os.path.join(mr.MUSIC, "bg music.mp3")
    fmt = "aformat=sample_rates=44100:channel_layouts=stereo"
    gain = mr.mean_db(VOICE) - mr.MUSIC_BELOW_VOICE - mr.mean_db(music)
    cmd = [mr.FFMPEG, "-y", "-loglevel", "error", "-i", VOICE, "-stream_loop", "-1", "-i", music]
    fc = (f"[0:a]{fmt},apad=whole_dur={END},asplit=2[v][vsc];"
          f"[1:a]{fmt},volume={gain:.1f}dB,volume=0:enable='between(t,{MUTE[0]},{MUTE[1]})',"
          f"volume=0.6:enable='gte(t,{DUCK})',afade=t=in:d=0.3,afade=t=out:st={END - 0.6:.2f}:d=0.6[mraw];"
          "[mraw][vsc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=400[m];")
    mix, n = "[v][m]", 2
    for name, t in SFX:
        cmd += ["-i", mr.find_file(mr.SFX, name, [".wav", ".mp3"])]
        ms = int(t * 1000)
        fc += f"[{n}:a]{fmt},volume={mr.SFX_VOLUME * 2:.2f},adelay={ms}|{ms}[x{n}];"
        mix += f"[x{n}]"
        n += 1
    fc += f"{mix}amix=inputs={n}:duration=first:normalize=0[a]"
    out = os.path.join(HERE, "assets", "mix.wav")
    cmd += ["-filter_complex", fc, "-map", "[a]", "-t", f"{END:.3f}", out]
    subprocess.run(cmd, check=True)
    print(f"mix.wav {END}s  (music: bg music.mp3, gain {gain:.1f}dB, {len(SFX)} sfx)")

# ---------- index.html ----------
data = (f"const OFF = 0;\nconst END = {END};\nconst CASE = \"ANN\";\nconst SCENES = [];\n"
        f"const P = {json.dumps(P, ensure_ascii=False)};\nconst T = {{}};\n"
        "const CFG = { capTop: 1250, capSize: 70, stroke: 11, punch: 0, floatPx: 0, activeWord: true };\n"
        + open(os.path.join(HERE, "extra.js"), encoding="utf-8").read())
eng = open(os.path.join(CODE, "hyperframes", "_ENGINE", "shivam_engine.html"), encoding="utf-8").read()
html = (eng.replace("__TITLE__", "Detective Points").replace("__DUR__", str(END))
        .replace("__MEDIA__", "").replace("__OVERLAYS__", "").replace("__DATA__", data))
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(html)
print("index.html ban gaya,", len(P), "caption tukde")
