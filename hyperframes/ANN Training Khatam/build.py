# ANN Training Khatam: captions (P) + mix.wav + index.html (engine + DATA + extra.js)
# py build.py            -> sab banao
# py build.py --noaudio  -> sirf index.html
import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, CODE)
import make_reel as mr

VOICE = os.path.join(CODE, "voice", "ANN Training Khatam.m4a")
WORDS = json.load(open(os.path.join(CODE, "voice", "ANN Training Khatam - words.json"), encoding="utf-8"))
END = 62.7          # voice 61.7 + 1 sec CTA
lines = {}
for w, s, e, ln in WORDS:
    lines.setdefault(ln + 1, []).append((s, e))

# (line, Roman tukda, devanagari word index from-to)
CHUNKS = [
    (1, "Tumhe laga...", 0, 1), (1, "tumne case solve kar liye?", 2, 6),
    (2, "Pichhle kuch dino se", 0, 3), (2, "comment mein ek hi baat", 4, 8), (2, "aa rahi hai...", 9, 11),
    (3, '"Bhai, ye to bahut aasaan tha."', 0, 5),
    (4, '"Har baar wahi pattern...', 0, 3), (4, "ek bayan, ek galti,", 4, 7), (4, 'case khatam."', 8, 9),
    (5, "Shivam ne ye saare comment padhe...", 0, 5),
    (6, "Aur muskura diya.", 0, 2),
    (7, "Kyunki tumne ek cheez", 0, 3), (7, "kabhi dhyaan se nahi dekhi...", 4, 8),
    (8, "Har cover par likha...", 0, 3), (8, "CASE NUMBER.", 4, 5),
    (9, "Ye har category ke", 0, 3), (9, "sabse pehle case the...", 4, 7),
    (10, "Sabse seedhe... sabse aasaan.", 0, 3),
    (11, "Ye asli case nahi the...", 0, 4), (11, "ye tumhari TRAINING thi!", 5, 8),
    (12, "Shivam bas dekhna chahta tha...", 0, 4), (12, "kaun aakhir tak tikta hai.", 5, 9),
    (14, "Aur ab... TRAINING KHATAM!", 0, 3),
    (15, "SOMWAR se khulengi wo files...", 0, 4), (15, "jo Shivam ne ab tak", 5, 9), (15, "band rakhi thi.", 10, 12),
    (16, "Wahan har kisi par shak jaayega...", 0, 5), (16, "har koi jhootha lagega.", 6, 9),
    (17, "Aur clue itna chhota hoga...", 0, 4), (17, "ki do baar dekhne par bhi", 5, 10), (17, "shayad na dikhe.", 11, 13),
    (18, "Ek-ek karke sab begunaah niklenge...", 0, 4), (18, "aur jo aakhir mein bachega —", 5, 10), (18, "wahi KAATIL.", 11, 12),
    (19, "Agar lagta hai tum taiyaar ho...", 0, 5), (19, "to comment mein likho —", 6, 10), (19, "MAIN TAIYAAR HOON.", 11, 13),
    (20, "SOMWAR ko milte hain...", 0, 3), (20, "dekhte hain kitne tikte hain.", 4, 8),
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
SFX = [("pop", 1.75), ("whoosh", 15.87), ("hit", 29.16), ("riser", 32.6), ("hit", 35.64), ("lock_open", 40.2), ("pop", 57.9)]
MUTE = (33.45, 34.5)       # pause line par music band
DUCK = 54.26               # CTA par music 10% -> 6%
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
        "const CFG = { capTop: 1250, capSize: 70, stroke: 11, punch: 0, floatPx: 0 };\n"
        + open(os.path.join(HERE, "extra.js"), encoding="utf-8").read())
eng = open(os.path.join(CODE, "hyperframes", "_ENGINE", "shivam_engine.html"), encoding="utf-8").read()
html = (eng.replace("__TITLE__", "Training Khatam").replace("__DUR__", str(END))
        .replace("__MEDIA__", "").replace("__OVERLAYS__", "").replace("__DATA__", data))
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(html)
print("index.html ban gaya,", len(P), "caption tukde")
