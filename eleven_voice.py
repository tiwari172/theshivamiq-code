# ElevenLabs se voiceover banana (SCRIPT_NNN.txt -> VO_MAIN.mp3)
#
#   python eleven_voice.py test          key + credits + voice check
#   python eleven_voice.py 1 9           Category 1, Story 09 ka VO_MAIN.mp3
#   python eleven_voice.py 1 9-12        Story 09 se 12 tak
#   python eleven_voice.py fixed         Common mein CTA_HI + SIGNATURE_HI
#   python eleven_voice.py sfx           sfx_list.txt ke sound effects -> sfx\
#
# API key: isi folder mein elevenlabs_key.txt (sirf key, ek line)

import base64
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

from voice_queue import slot, safe_replace

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
STORY_ROOT = r"C:\Users\Hp\Desktop\reels story"
KEY_FILE = os.path.join(BASE, "elevenlabs_key.txt")
VOICE_FILE = os.path.join(BASE, "elevenlabs_voice.txt")

VOICE_NAME = "Rudra"          # voice ke naam ka hissa (library mein dhoondhega)
MODEL = "eleven_v3"
# purani Rudra files wali setting (sp105_s45_sb75); v3 na maane to SAFE_SETTINGS
SETTINGS = {"stability": 0.45, "similarity_boost": 0.75, "speed": 1.05}
SAFE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.75}
MAX_CHARS = 3000              # v3 ek baar mein itne hi letters leta hai
API = "https://api.elevenlabs.io/v1"


def read_key():
    if not os.path.exists(KEY_FILE):
        sys.exit("elevenlabs_key.txt nahi mili. Is folder mein file banao aur usme API key paste karo.")
    key = open(KEY_FILE, encoding="utf-8").read().strip()
    if not key:
        sys.exit("elevenlabs_key.txt khaali hai. Usme API key paste karke save karo.")
    return key


class BadSettings(Exception):
    pass


def call(path, key, body=None):
    for attempt in range(60):
        req = urllib.request.Request(API + path, method="POST" if body else "GET")
        req.add_header("xi-api-key", key)
        if body:
            req.add_header("Content-Type", "application/json")
            req.data = json.dumps(body).encode("utf-8")
        try:
            return _call(req, body)
        except Busy:   # ElevenLabs par dusri chat ki request chal rahi hai -> thoda ruk kar dobara
            if attempt == 0:
                print("  ElevenLabs busy (dusri chat), line mein wait...")
            time.sleep(5)
    sys.exit("ElevenLabs 5 minute tak busy raha, baad mein chalao.")


class Busy(Exception):
    pass


def _call(req, body):
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:400]
        if e.code == 429 and ("concurrent" in msg or "system_busy" in msg):
            raise Busy()
        if e.code == 401:
            if "missing_permissions" in msg:
                sys.exit("Key mein permission kam hai. ElevenLabs par key edit karke Text to Speech, Voices (read), User (read) ON karo.\n" + msg)
            sys.exit("API key galat hai (401). elevenlabs_key.txt dobara check karo.")
        if e.code in (402, 429) or "quota" in msg:
            sys.exit(f"Credits khatam / limit (code {e.code}).\n{msg}")
        if e.code in (400, 422) and body and body.get("voice_settings") != SAFE_SETTINGS \
                and re.search(r"stability|speed|voice_settings", msg):
            raise BadSettings(msg)
        sys.exit(f"ElevenLabs error {e.code}:\n{msg}")
    except urllib.error.URLError as e:
        sys.exit(f"Internet / connection problem: {e.reason}")


def credits(key):
    sub = json.loads(call("/user/subscription", key))
    left = sub["character_limit"] - sub["character_count"]
    return left, sub["character_limit"]


def voice_id(key, verbose=False):
    if os.path.exists(VOICE_FILE):
        vid = open(VOICE_FILE, encoding="utf-8").read().split()[0]
        if vid and not verbose:
            return vid
    voices = json.loads(call("/voices", key))["voices"]
    if verbose:
        print("\nAapki library ki voices:")
        for v in voices:
            print(f"  {v['name']}  ->  {v['voice_id']}")
    match = [v for v in voices if VOICE_NAME.lower() in v["name"].lower()]
    if not match:
        sys.exit(f"'{VOICE_NAME}' naam ki voice library mein nahi mili. ElevenLabs par voice ko 'Add to My Voices' karo.")
    v = match[0]
    with open(VOICE_FILE, "w", encoding="utf-8") as f:
        f.write(f"{v['voice_id']}  {v['name']}\n")
    print(f"\nVoice set: {v['name']}")
    return v["voice_id"]


def section(text, title):
    m = re.search(r"=+\s*" + title + r"[^\n]*=+\s*\n(.*?)(?=\n=+ |\Z)", text, re.S)
    if not m:
        return ""
    lines = [l for l in m.group(1).splitlines() if not l.strip().startswith("(")]
    return "\n".join(lines).strip()


def speak(key, vid, text, out_mp3):
    # voice_queue: kai chats ek saath -> har ek ko alag slot, saare busy to line mein wait
    with slot("eleven"):
        _speak(key, vid, text, out_mp3)


def _speak(key, vid, text, out_mp3):
    if os.path.exists(out_mp3):   # wait ke dauraan dusri chat ne bana di ho to credits mat khao
        print(f"  pehle se hai, skip: {out_mp3}")
        return
    if len(text) > MAX_CHARS:
        sys.exit(f"  text {len(text)} letters ka hai, v3 ki limit {MAX_CHARS}. Script chhota karo.")
    global SETTINGS
    path = f"/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128"
    body = {"text": text, "model_id": MODEL, "voice_settings": SETTINGS}
    try:
        data = json.loads(call(path, key, body))
    except BadSettings:
        print("  v3 ne 0.45 / 1.05 setting nahi maani, stability 0.5 (Natural) se bana raha hoon")
        SETTINGS = SAFE_SETTINGS
        body["voice_settings"] = SETTINGS
        data = json.loads(call(path, key, body))
    part = f"{out_mp3}.part{os.getpid()}"   # poori likh kar hi final naam
    align = data.get("alignment")
    if align:
        with open(part, "w", encoding="utf-8") as f:
            json.dump(align, f, ensure_ascii=False)
        safe_replace(part, out_mp3[:-4] + "_timing.json")
    with open(part, "wb") as f:
        f.write(base64.b64decode(data["audio_base64"]))
    safe_replace(part, out_mp3)
    print(f"  ban gaya: {out_mp3}")


# CTA + signature har baar credits na khaayein: Common\CTA_HI.mp3 + SIGNATURE_HI.mp3 jodte hain
FIXED_WORDS = ("कमेंट", "comment", "नज़र से", "नजर से", "nazar se")


def strip_fixed(text):
    lines = [l for l in text.splitlines() if not any(w in l.lower() for w in FIXED_WORDS)]
    return "\n".join(lines).strip()


def story_nums(arg):
    if "-" in arg:
        a, b = arg.split("-")
        return range(int(a), int(b) + 1)
    return [int(arg)]


def do_stories(key, cat, arg, reveal):
    vid = voice_id(key)
    jobs = []
    for n in story_nums(arg):
        folder = os.path.join(STORY_ROOT, f"Category {cat}", f"Story {n:02d}")
        # naya format (Category 2+): VO_02-001.txt = seedha voice ka text
        vo_txt = glob.glob(os.path.join(folder, "VO_*.txt"))
        script = os.path.join(folder, f"SCRIPT_{n:03d}.txt")
        if vo_txt:
            text, main = "", strip_fixed(open(vo_txt[0], encoding="utf-8").read())
        elif os.path.exists(script):
            text = open(script, encoding="utf-8").read()
            main = section(text, "MAIN VOICEOVER")
        else:
            print(f"Story {n:02d}: SCRIPT / VO text file nahi mili, skip")
            continue
        if main:
            jobs.append((f"Story {n:02d} main", main, os.path.join(folder, "VO_MAIN.mp3")))
        if reveal:
            rev = section(text, "ANSWER REVEAL")
            if rev:
                jobs.append((f"Story {n:02d} reveal", rev, os.path.join(folder, "VO_REVEAL.mp3")))
    run(key, vid, jobs)


def do_fixed(key):
    vid = voice_id(key)
    text = open(os.path.join(STORY_ROOT, "Common", "FIXED_LINES_v3.txt"), encoding="utf-8").read()
    jobs = []
    for name in ("CTA_HI", "SIGNATURE_HI"):
        m = re.search(name + r"\.mp3:\s*\n(.+)", text)
        if m:
            jobs.append((name, m.group(1).strip(), os.path.join(STORY_ROOT, "Common", name + ".mp3")))
    run(key, vid, jobs)


def do_sfx(key):
    folder = os.path.join(BASE, "sfx")
    os.makedirs(folder, exist_ok=True)
    jobs = []
    for line in open(os.path.join(BASE, "sfx_list.txt"), encoding="utf-8"):
        if line.strip().startswith("#") or line.count("|") < 2:
            continue
        name, secs, prompt = [p.strip() for p in line.split("|", 2)]
        if any(os.path.exists(os.path.join(folder, name + ext)) for ext in (".mp3", ".wav")):
            print(f"{name}: pehle se hai, skip")
            continue
        jobs.append((name, float(secs), prompt))
    if not jobs:
        print("Koi naya sound nahi banana.")
        return
    left, _ = credits(key)
    print(f"\n{len(jobs)} sound banenge. Abhi credits: {left}")
    for name, secs, prompt in jobs:
        print(f"{name} ({secs}s)...")
        audio = call("/sound-generation?output_format=mp3_44100_128", key,
                     {"text": prompt, "duration_seconds": secs, "prompt_influence": 0.5})
        with open(os.path.join(folder, name + ".mp3"), "wb") as f:
            f.write(audio)
    left, _ = credits(key)
    print(f"\nHo gaya, sfx folder mein save. Bache credits: {left}")


def run(key, vid, jobs):
    jobs = [j for j in jobs if not os.path.exists(j[2]) or print(f"{j[0]}: pehle se bani hai, skip")]
    if not jobs:
        print("Kuch naya banana nahi hai.")
        return
    need = sum(len(t) for _, t, _ in jobs)
    left, _ = credits(key)
    print(f"\n{len(jobs)} voice banegi, lagbhag {need} credits lagenge. Aapke paas {left} bache hain.")
    if need > left:
        sys.exit("Credits kam hain, ruk gaya.")
    for label, t, out in jobs:
        print(f"{label} ({len(t)} letters)...")
        speak(key, vid, t, out)
    left, _ = credits(key)
    print(f"\nHo gaya. Bache credits: {left}")


def main():
    args = [a.lower() for a in sys.argv[1:]]
    key = read_key()
    if not args or args[0] == "test":
        left, total = credits(key)
        print(f"Key sahi hai. Credits: {left} bache / {total}")
        voice_id(key, verbose=True)
        return
    if args[0] == "fixed":
        do_fixed(key)
        return
    if args[0] == "sfx":
        do_sfx(key)
        return
    if len(args) < 2:
        sys.exit("Aise likho:  python eleven_voice.py 1 9   (category, story)")
    do_stories(key, int(args[0]), args[1], False)   # reveal reels band (answer comment mein pin)


if __name__ == "__main__":
    main()
