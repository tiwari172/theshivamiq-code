# Viral-hook reel ki poori awaaz: hook clip (original audio, OFFSET tak) + voice/music/sfx mix (CSV voice-time ke hisaab se)
# Use: py build_audio_hook.py "<project folder>" "<case>" "<hook clip.mp4>" [offset=4.7]
import os, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import make_reel as mr

proj, case, clip = sys.argv[1], sys.argv[2], sys.argv[3]
OFF = float(sys.argv[4]) if len(sys.argv) > 4 else 4.7
rows = mr.read_csv(os.path.join(mr.CASES, case + ".csv"))
voice = mr.find_file(mr.VOICE, case, [".mp3", ".m4a", ".wav"])
duration = max(mr.audio_duration(voice), max(r["end"] for r in rows))
music = os.path.join(mr.MUSIC, sorted(f for f in os.listdir(mr.MUSIC) if f.endswith((".mp3", ".m4a")))[0])
mutes = [(r["start"], r["start"] + 1.0) for r in rows if "music_off" in r["effects"]]
sfx = [(r["sfx"], r["start"]) for r in rows if r["sfx"]]
clip_len = mr.audio_duration(clip)

fmt = "aformat=sample_rates=44100:channel_layouts=stereo"
cmd = [mr.FFMPEG, "-y", "-loglevel", "error", "-i", voice, "-stream_loop", "-1", "-i", music, "-i", clip]
gain = mr.mean_db(voice) - mr.MUSIC_BELOW_VOICE - mr.mean_db(music)
mute_f = "".join(f",volume=0:enable='between(t,{a:.2f},{b:.2f})'" for a, b in mutes)
fc = (f"[0:a]volume={mr.VOICE_VOLUME},{fmt},asplit=2[v][vsc];"
      f"[1:a]{fmt},volume={gain:.1f}dB{mute_f},afade=t=in:d=0.3,"
      f"afade=t=out:st={max(0, duration - mr.MUSIC_FADE_OUT):.2f}:d={mr.MUSIC_FADE_OUT}[mraw];"
      "[mraw][vsc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=400[m];")
mix, n = "[v][m]", 3
for name, t in sfx:
    cmd += ["-i", mr.find_file(mr.SFX, name, [".wav", ".mp3"])]
    ms = int(t * 1000)
    fc += f"[{n}:a]{fmt},volume={mr.SFX_VOLUME},adelay={ms}|{ms}[x{n}];"
    mix += f"[x{n}]"
    n += 1
fc += f"{mix}amix=inputs={n - 1}:duration=first:normalize=0,atrim=0:{duration:.3f}[body];"
# hook clip: original audio 100%, aakhri 0.2s fade, phir chup OFFSET tak
fc += (f"[2:a]{fmt},atrim=0:{clip_len:.3f},afade=t=out:st={clip_len - 0.2:.3f}:d=0.2,"
       f"apad=whole_dur={OFF:.3f}[hook];[hook][body]concat=n=2:v=0:a=1[a]")
out = os.path.join(proj, "assets", "mix.wav")
cmd += ["-filter_complex", fc, "-map", "[a]", out]
subprocess.run(cmd, check=True)
print(f"mix.wav {OFF + duration:.2f}s  (hook {clip_len:.2f}s + voice {duration:.2f}s; music: {os.path.basename(music)}, gain {gain:.1f}dB, {len(sfx)} sfx)")
