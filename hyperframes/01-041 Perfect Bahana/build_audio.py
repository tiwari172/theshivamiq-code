# HyperFrames test reel ke liye poori awaaz ek file mein: voice + music (auto level + ducking + music_off) + sfx
# make_reel.py wali hi mixing. Use: py build_audio.py "<case>" [extra_sfx "naam@time" ...]
import os, sys, subprocess, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import make_reel as mr

case = sys.argv[1]
extra = [(a.split("@")[0], float(a.split("@")[1])) for a in sys.argv[2:]]
rows = mr.read_csv(os.path.join(mr.CASES, case + ".csv"))
voice = mr.find_file(mr.VOICE, case, [".mp3", ".m4a", ".wav"])
duration = max(mr.audio_duration(voice), max(r["end"] for r in rows))
music = sorted(f for f in os.listdir(mr.MUSIC) if f.endswith((".mp3", ".m4a")))[0]
music = os.path.join(mr.MUSIC, music)
mutes = [(r["start"], r["start"] + 1.0) for r in rows if "music_off" in r["effects"]]
sfx = [(r["sfx"], r["start"]) for r in rows if r["sfx"]] + extra

fmt = "aformat=sample_rates=44100:channel_layouts=stereo"
cmd = [mr.FFMPEG, "-y", "-loglevel", "error", "-i", voice, "-stream_loop", "-1", "-i", music]
gain = mr.mean_db(voice) - mr.MUSIC_BELOW_VOICE - mr.mean_db(music)
mute_f = "".join(f",volume=0:enable='between(t,{a:.2f},{b:.2f})'" for a, b in mutes)
fc = (f"[0:a]volume={mr.VOICE_VOLUME},{fmt},asplit=2[v][vsc];"
      f"[1:a]{fmt},volume={gain:.1f}dB{mute_f},afade=t=in:d=0.3,"
      f"afade=t=out:st={max(0, duration - mr.MUSIC_FADE_OUT):.2f}:d={mr.MUSIC_FADE_OUT}[mraw];"
      "[mraw][vsc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=400[m];")
mix, n = "[v][m]", 2
for name, t in sfx:
    cmd += ["-i", mr.find_file(mr.SFX, name, [".wav", ".mp3"])]
    ms = int(t * 1000)
    fc += f"[{n}:a]{fmt},volume={mr.SFX_VOLUME},adelay={ms}|{ms}[x{n}];"
    mix += f"[x{n}]"
    n += 1
fc += f"{mix}amix=inputs={n}:duration=first:normalize=0[a]"
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mix.wav")
cmd += ["-filter_complex", fc, "-map", "[a]", "-t", f"{duration:.3f}", out]
subprocess.run(cmd, check=True)
print(f"mix.wav {duration:.2f}s  (music: {os.path.basename(music)}, gain {gain:.1f}dB, {len(sfx)} sfx)")
