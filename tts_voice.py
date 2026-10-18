# theshivamiq – Free voiceover (Microsoft Edge ki awaaz, internet chahiye, paisa nahi)
#
#   python tts_voice.py "03 29 February ki Shaadi"
#       -> voice_scripts\03 29 February ki Shaadi.txt padhta hai
#       -> voice\03 29 February ki Shaadi.m4a banata hai + har line ka time print karta hai
#
# Script file mein har line:   mood | pause | text
#   mood  = normal / serious / whisper / suspense / smug / shout / calm  (neeche MOODS mein)
#   pause = line ke baad kitne second chup
#   text  = Devanagari mein likho (Hindi awaaz sahi bolti hai)
# '#' se shuru line = comment

import asyncio, os, subprocess, sys, tempfile
import edge_tts
from make_reel import FFMPEG, audio_duration

BASE = os.path.dirname(os.path.abspath(__file__))
VOICE_NAME = "hi-IN-MadhurNeural"   # mard ki awaaz  (aurat: hi-IN-SwaraNeural)
BASE_RATE = 8                        # sab lines thodi tez (%)

# mood -> (speed %, pitch Hz, volume %)
MOODS = {
    "normal":   (0, 0, 0),
    "calm":     (-3, -2, 0),
    "serious":  (-6, -5, 0),
    "suspense": (-12, -6, -5),
    "whisper":  (-15, -8, -35),
    "smug":     (-2, 4, 0),
    "shout":    (12, 12, 25),
    "nervous":  (10, 3, 0),
    "sad":      (-10, -4, -10),
}


def sign(n):
    return f"+{n}" if n >= 0 else str(n)


async def speak(text, mood, path):
    rate, pitch, vol = MOODS[mood]
    await edge_tts.Communicate(text, VOICE_NAME, rate=sign(rate + BASE_RATE) + "%",
                               pitch=sign(pitch) + "Hz", volume=sign(vol) + "%").save(path)


def trim(src, dst):
    # shuru aur aakhir ki khamoshi hatao
    f = "silenceremove=start_periods=1:start_threshold=-45dB"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, "-af",
                    f"{f},areverse,{f},areverse,aformat=sample_rates=44100:channel_layouts=mono", dst],
                   check=True)


def main():
    case = sys.argv[1]
    lines = []
    with open(os.path.join(BASE, "voice_scripts", case + ".txt"), encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            mood, pause, text = [p.strip() for p in raw.split("|", 2)]
            if mood not in MOODS:
                sys.exit(f"line {n}: mood '{mood}' galat hai. {' / '.join(MOODS)} likho.")
            lines.append((mood, float(pause), text))

    tmp = tempfile.mkdtemp()
    parts, t = [], 0.0
    print("  time           mood      text")
    for i, (mood, pause, text) in enumerate(lines):
        mp3, wav = os.path.join(tmp, f"{i}.mp3"), os.path.join(tmp, f"{i}.wav")
        asyncio.run(speak(text, mood, mp3))
        trim(mp3, wav)
        d = audio_duration(wav)
        print(f"  {t:6.2f} - {t + d:6.2f}  {mood:9} {text}")
        parts.append((wav, pause))
        t += d + pause

    cmd, fc, labels = [FFMPEG, "-v", "error", "-y"], "", ""
    for i, (wav, pause) in enumerate(parts):
        cmd += ["-i", wav]
        fc += f"[{i}:a]apad=pad_dur={pause if i < len(parts) - 1 else 0.3}[p{i}];"
        labels += f"[p{i}]"
    fc += f"{labels}concat=n={len(parts)}:v=0:a=1[o]"
    out = os.path.join(BASE, "voice", case + ".m4a")
    cmd += ["-filter_complex", fc, "-map", "[o]", "-c:a", "aac", "-b:a", "192k", out]
    subprocess.run(cmd, check=True)
    print(f"BAN GAYI -> voice\\{case}.m4a  ({audio_duration(out):.1f}s)")


if __name__ == "__main__":
    main()
