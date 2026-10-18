# ANN Detective Rank: captions (P) + mix.wav + index.html (engine + DATA + extra.js)
# py build.py            -> sab banao
# py build.py --noaudio  -> sirf index.html
import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, CODE)
import make_reel as mr

VOICE = os.path.join(CODE, "voice", "ANN Detective Rank.m4a")
WORDS = json.load(open(os.path.join(CODE, "voice", "ANN Detective Rank - words.json"), encoding="utf-8"))
END = 68.0          # voice 67.0 + 1 sec end card
lines = {}
for w, s, e, ln in WORDS:
    lines.setdefault(ln + 1, []).append((s, e))

# (line, Roman tukda, devanagari word index from-to)   CAPS shabd = peela
CHUNKS = [
    (1, "Ruko...", 0, 0), (1, "tumhara har comment...", 1, 3), (1, "koi GIN raha tha.", 4, 7),
    (2, "39 case...", 0, 1), (2, "7000 se zyada JAWAB.", 2, 6),
    (3, "Aur aaj... khul rahi hai...", 0, 4), (3, "DETECTIVE RANK ki file!", 5, 8),
    (4, "3 case sahi...", 0, 2), (4, "JUNIOR DETECTIVE.", 3, 4),
    (5, "10 case sahi...", 0, 2), (5, "SENIOR DETECTIVE.", 3, 4),
    (6, "Aur 14 log...", 0, 2), (6, "pehle hi Senior ban chuke hain!", 3, 8),
    (7, "Lekin is hafte...", 0, 2), (7, "EK NAAM sabse aage tha.", 3, 7),
    (8, "16 case... 16 sahi...", 0, 3), (8, "aur lagatar 15 REELS.", 4, 7),
    (9, "Detective of the Week...", 0, 3), (9, "Classy Pran Krishna!", 4, 6),
    (10, "Aur jisne sabse zyada", 0, 3), (10, "case solve kiye...", 4, 6),
    (11, "17 sahi jawab...", 0, 2), (11, "aaj se wo hai...", 3, 6), (11, "Shivam ka Partner...", 7, 9), (11, "Parchhai Boy!", 10, 11),
    (12, "Rank chahiye?", 0, 1), (12, "Comment mein NAAM likho...", 2, 5), (12, "ya NUMBER.", 6, 7),
    (13, "Wajah batani hai?", 0, 2), (13, "To naam, phir DASH, phir wajah.", 3, 8),
    (14, "Sirf PEHLA comment ginega...", 0, 4), (14, "aur sirf 24 GHANTE ke andar.", 5, 10),
    (15, "Aur rank milegi use...", 0, 3), (15, "jisne YouTube SUBSCRIBE", 4, 6), (15, "aur Telegram JOIN kiya hai.", 7, 11),
    (16, "Apni rank dekho...", 0, 2), (16, "Telegram BOT par.", 3, 5),
    (17, "Agla naam...", 0, 1), (17, "TUMHARA ho sakta hai.", 2, 5),
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
SFX = [("heartbeat", 0.05), ("lock_open", 9.25), ("boom", 10.86), ("tick_fast", 24.98), ("boom", 31.15),
       ("riser", 33.0), ("boom", 38.27), ("reveal", 39.62), ("typing", 42.2), ("ding", 60.25), ("whoosh", 61.16)]
MUTE = (21.6, 23.1)        # blackout par music band
DUCK = 63.6                # signature + end card par music 60%
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
html = (eng.replace("__TITLE__", "Detective Rank").replace("__DUR__", str(END))
        .replace("__MEDIA__", "").replace("__OVERLAYS__", "").replace("__DATA__", data))
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(html)
print("index.html ban gaya,", len(P), "caption tukde")
