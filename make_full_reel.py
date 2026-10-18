# theshivamiq – EK COMMAND mein poori reel
#
#   py make_full_reel.py "<story folder>" "<NN Title>"
#   py make_full_reel.py "<story folder>" "<NN Title>" --from 5     step 5 se dobara (pehle wale skip)
#   py make_full_reel.py "<story folder>" "<NN Title>" --dry-run    sirf batao kya karega, kuch mat chalao
#   py make_full_reel.py "<story folder>" "<NN Title>" --force      check_reel PROBLEM ke bawajood render (sirf user bole)
#   --tak 6                    step 6 (render) ke baad ruk jao - story folder mein kuch copy nahi
#   --style pop|rise|slide     CSV ki STYLE row (default rise)
#   --haan                     purani MP4 / CSV replace karne ka sawaal mat poocho, seedha "haan"
#
# Steps (har step pehle se bane scripts ko hi chalata hai):
#   1 prep_story.py   2 build_voice.py (3.0s soch-pause)   3 auto_csv.py -> cases\<NN Title>.csv (DRAFT)
#   4 make_cards.py (options + cover)   5 check_reel.py   6 make_reel.py
#   7 MP4 + CSV (timing.csv) story folder mein   8 make_cover.py one
#
# Kaha tak pahunche: cases\<NN Title>.state.json  (story folder mein kuch extra nahi likhta)
# CSV haath se theek ki? Bas wahi command dobara chalao - CSV badli hai to check/render apne aap dobara.

import hashlib, json, os, re, shutil, subprocess, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import auto_csv

CASES = os.path.join(BASE, "cases")
ASSETS = os.path.join(BASE, "assets")
VOICE = os.path.join(BASE, "voice")
MUSIC = os.path.join(BASE, "music")
OUTPUT = os.path.join(BASE, "output")
STORY_ROOT = r"C:\Users\Hp\Desktop\reels story"
THINK_TEXT, THINK = "डिटेक्टिव शिवम", "3.0"
COVER_BIG = "99% LOG FAIL!"

STEPS = {1: "Images (prep_story)", 2: "Voice (build_voice)", 3: "CSV draft (auto_csv)",
         4: "Cards (options + cover)", 5: "Check (check_reel)", 6: "Render (make_reel)",
         7: "Copy MP4 + timing.csv story mein", 8: "Case File cover (make_cover)"}
CSV_STEPS = (4, 5, 6, 7, 8)       # CSV badle to ye dobara


class Stop(Exception):
    """pipeline yahin ruko (message user ke liye)"""


# ---------------- chhote helpers ----------------
def say(msg=""):
    print(msg, flush=True)


def md5(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ask(question, auto_yes=False):
    if auto_yes:
        say(f"{question} -> haan (--haan)")
        return True
    if not sys.stdin or not sys.stdin.isatty():
        say(f"{question} -> jawab nahi mila, NAHI maana")
        return False
    while True:
        a = input(f"{question} (y/n): ").strip().lower()
        if a in ("y", "yes", "h", "haan", "ha"):
            return True
        if a in ("n", "no", "nahi", "na"):
            return False


def run(cmd, log=None):
    """script chalao, output saath saath dikhao, aur poora output wapas do"""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")   # Devanagari print par Windows crash na kare
    say("   > " + " ".join(f'"{c}"' if " " in c else c for c in cmd[1:]))
    p = subprocess.Popen(cmd, cwd=BASE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                         text=True, encoding="utf-8", errors="replace", bufsize=1)
    out = []
    for line in p.stdout:
        out.append(line)
        print("     " + line.rstrip("\n"), flush=True)
    p.wait()
    text = "".join(out)
    if log:
        with open(log, "w", encoding="utf-8") as f:
            f.write(text)
    return p.returncode, text


def py(script, *args):
    return [sys.executable, "-u", os.path.join(BASE, script), *args]


# ---------------- state ----------------
class State:
    def __init__(self, name, story, dry=False):
        self.path = os.path.join(CASES, name + ".state.json")
        self.dry = dry
        self.d = {}
        if os.path.exists(self.path):
            try:
                self.d = read_json(self.path)
            except ValueError:
                self.d = {}
        self.d.setdefault("done", {})
        self.d["story"], self.d["name"] = story, name

    def save(self):
        if not self.dry:
            os.makedirs(CASES, exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.d, f, ensure_ascii=False, indent=1)
            os.replace(tmp, self.path)

    def done(self, n, **extra):
        self.d["done"][str(n)] = dict(at=time.strftime("%Y-%m-%d %H:%M"), **extra)
        self.save()

    def undo_from(self, n):
        for k in list(self.d["done"]):
            if int(k) >= n:
                del self.d["done"][k]


class Reel:
    def __init__(self, story, name, opts):
        self.story, self.name, self.o = story, name, opts
        self.csv = os.path.join(CASES, name + ".csv")
        self.times = os.path.join(CASES, name + ".voice_times.txt")
        self.prep_log = os.path.join(CASES, name + ".prep.txt")
        self.voice = os.path.join(VOICE, name + ".m4a")
        self.mp4 = os.path.join(OUTPUT, name + ".mp4")
        self.story_mp4 = os.path.join(story, name + ".mp4")
        self.st = State(name, story, opts["dry"])
        self.copy_ok = None

    # ---- step pehle se ho chuka? (aur uski file abhi bhi hai?) ----
    def is_done(self, n):
        rec = self.st.d["done"].get(str(n))
        if not rec:
            return False
        if n in CSV_STEPS and rec.get("csv") != md5(self.csv):
            return False                        # CSV baad mein badli -> dobara
        need = {1: [], 2: [self.voice, self.times], 3: [self.csv], 6: [self.mp4], 7: [self.story_mp4],
                8: [rec.get("cover", "")]}.get(n, [])
        if n == 4:
            info = self.st.d.get("info", {})
            need = [os.path.join(OUTPUT, self.name + " - COVER.png")] + (
                [os.path.join(ASSETS, info["options"] + ".png")] if info.get("options") else [])
        if n == 1 and not self.st.d.get("names"):
            return False
        return all(p and os.path.exists(p) for p in need)

    # ---------- steps ----------
    def step1(self):
        if not os.path.isdir(os.path.join(self.story, "images")):
            raise Stop(f"Story mein images\\ folder nahi hai: {self.story}")
        rc, out = run(py("prep_story.py", self.story), self.prep_log)
        if rc:
            raise Stop("prep_story.py fail hua (upar error dekho). Images theek karke --from 1 se chalao.")
        names = auto_csv.parse_prep_names(out)
        if not names:
            raise Stop('prep_story ne "CSV mein ye naam lagao" list nahi di.')
        self.st.d["names"] = names
        sheet = re.search(r"Contact sheet -> (.+)", out)
        self.st.d["sheet"] = sheet.group(1).strip() if sheet else ""
        self.st.done(1)

    def step2(self):
        for f in ("VO_MAIN.mp3", "VO_MAIN_timing.json"):
            if not os.path.exists(os.path.join(self.story, f)):
                c, s = re.search(r"Category (\d+)", self.story), re.search(r"Story (\d+)", self.story)
                hint = f"py eleven_voice.py {c.group(1)} {int(s.group(1))}" if c and s else "py eleven_voice.py <cat> <story>"
                raise Stop(f"Story mein {f} nahi hai. Pehle ElevenLabs voice banao:  {hint}\n"
                           f"   (CTA / Signature dobara mat banana) - phir yahi command dobara chalao.")
        j = read_json(os.path.join(self.story, "VO_MAIN_timing.json"))
        if THINK_TEXT not in "".join(j["characters"]):
            raise Stop(f'VO mein "{THINK_TEXT}" nahi mila - soch-pause kahan daale? SCRIPT / VO check karo.')
        rc, out = run(py("build_voice.py", self.story, self.name, THINK_TEXT, THINK), self.times)
        if rc or not os.path.exists(self.voice):
            raise Stop("build_voice.py fail hua (upar error dekho). Theek karke --from 2 se chalao.")
        th = re.search(r"THINK pause .+", out)
        if th:
            say(f"   {th.group(0)}  <- ye 'डिटेक्टिव शिवम ने...pakad liya' se theek pehle hona chahiye")
        self.st.done(2)

    def step3(self):
        old = md5(self.csv)
        made = self.st.d.get("csv_made")
        if old and old != made:
            say(f"   cases\\{self.name}.csv pehle se hai (haath se banayi / badli hui).")
            if not ask("   Nayi DRAFT CSV se replace karun? (purani .csv.old ban jaayegi)", self.o["yes"]):
                say("   Purani CSV hi rakhi.")
                self.st.d["info"] = self.st.d.get("info") or self.info_only()
                self.st.done(3)
                return
            shutil.copy2(self.csv, self.csv + ".old")
        timing = auto_csv.load_timing(self.story, self.times)
        rows, info = auto_csv.build(self.story, self.name, timing, self.st.d.get("names"), self.o["style"])
        with open(self.csv, "w", encoding="utf-8", newline="") as f:
            f.write(auto_csv.to_text(rows))
        say(f"   CSV DRAFT -> cases\\{self.name}.csv  ({len(rows) - 1} rows, {info['total']}s)")
        say(f"   sawaal: {info['hook']}   suspects: " + ", ".join(f"{a}:{n}" for a, n in info["suspects"]))
        for n in info["notes"]:
            say("   * " + n)
        self.st.d["info"], self.st.d["csv_made"] = info, md5(self.csv)
        self.st.done(3)

    def info_only(self):
        timing = auto_csv.load_timing(self.story, self.times)
        return auto_csv.build(self.story, self.name, timing, self.st.d.get("names"), self.o["style"])[1]

    def hook_from_csv(self, default):
        if os.path.exists(self.csv):
            with open(self.csv, encoding="utf-8-sig") as f:
                head = f.read().splitlines()[:8]
            for line in head:
                m = re.search(r"([A-Z]+ KAUN\?|[A-Z]+ PAKDO!)", line)
                if m:
                    return m.group(1)
        return default

    def step4(self):
        info = self.st.d.get("info") or {}
        if info.get("options"):
            items = [f"{a}:{n}" for a, n in info["suspects"]]
            rc, _ = run(py("make_cards.py", "options", info["options"], *items))
            if rc:
                raise Stop("Options card nahi bana (upar error). Suspects ki image naam check karo.")
        hook = self.hook_from_csv(info.get("hook", "KILLER KAUN?"))
        rc, _ = run(py("make_cards.py", "cover", self.name, "S16", COVER_BIG, hook))
        if rc:
            raise Stop("Cover card nahi bana (upar error).")
        self.st.done(4, csv=md5(self.csv))

    def step5(self):
        rc, out = run(py("check_reel.py", self.name))
        if rc:
            if self.o["force"]:
                say("   !! check_reel ne PROBLEM batayi, par --force diya hai to aage badh rahe hain.")
            else:
                raise Stop(
                    "check_reel ne PROBLEM pakdi - render NAHI kiya.\n"
                    f"   Kya karo: cases\\{self.name}.csv kholo aur upar likhi line theek karo:\n"
                    "     - 'text image ke upar'   -> text chhota karo ya row ko do time-rows mein todo\n"
                    "     - 'text N line ka hai'   -> lambi line ko do rows mein todo (max 2-3 line)\n"
                    "     - 'sirf text hai'        -> pichhli image ki row ka end aage badhao\n"
                    "     - 'assets mein nahi hai' -> image ka sahi naam likho (prep_story wali list)\n"
                    "   Phir yahi command dobara chalao (CSV badli hai to check apne aap dobara hoga).")
        if "DHYAAN DO" in out:
            say("   (DHYAAN DO wali lines dekh lo - safed background ho to _CUT, neeche kati ho to _UP naam lagao)")
        self.st.done(5, csv=md5(self.csv))

    def ensure_music(self):
        os.makedirs(MUSIC, exist_ok=True)
        if any(f.lower().endswith((".mp3", ".m4a")) for f in os.listdir(MUSIC)):
            return
        root = os.path.dirname(os.path.dirname(self.story))
        for src in (os.path.join(root, "Common", "bg music.mp3"), os.path.join(STORY_ROOT, "Common", "bg music.mp3")):
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(MUSIC, "bg music.mp3"))
                say(f"   music\\ khaali tha -> {src} copy kiya")
                return
        raise Stop("music\\ folder khaali hai aur 'reels story\\Common\\bg music.mp3' bhi nahi mila. Music daalo.")

    def step6(self):
        self.ensure_music()
        started = time.time()
        args = [self.name] + (["--force"] if self.o["force"] else [])
        rc, out = run(py("make_reel.py", *args))
        if rc or not os.path.exists(self.mp4) or os.path.getmtime(self.mp4) < started - 1:
            raise Stop("make_reel ne MP4 nahi banayi (upar log dekho). Theek karke --from 6 se chalao.")
        if "(music:" not in out:
            raise Stop("Render log mein '(music: ...)' nahi dikha - music nahi laga! music\\ folder check karo, "
                       "phir --from 6.")
        grid = os.path.join(OUTPUT, self.name + " - CHECK.png")
        self.st.d["grid"] = grid
        self.st.done(6, csv=md5(self.csv))

    def step7(self):
        if self.copy_ok is None:
            self.copy_ok = self.ask_copy()
        if not self.copy_ok:
            raise Stop("Story folder ki purani MP4 nahi chhedi. Nayi reel output\\ mein hai: " + self.mp4)
        shutil.copy2(self.mp4, self.story_mp4)
        shutil.copy2(self.csv, os.path.join(self.story, "timing.csv"))
        say(f"   MP4 + timing.csv -> {self.story}")
        self.st.done(7, csv=md5(self.csv))

    def ask_copy(self):
        old = [f for f in os.listdir(self.story) if f.lower().endswith(".mp4")] if os.path.isdir(self.story) else []
        if not old:
            return True
        say(f"   Story folder mein pehle se MP4 hai: {', '.join(old)}")
        return ask("   Nayi reel story folder mein daal dun? (same naam wali + timing.csv replace hogi)", self.o["yes"])

    def step8(self):
        out = os.path.join(self.story, self.name + " - COVER.png")
        mine = (self.st.d["done"].get("8") or {}).get("cover")
        if os.path.exists(out) and mine != out:
            out = os.path.join(self.story, self.name + " - COVER NEW.png")   # purana cover mat mitao
        rc, _ = run(py("make_cover.py", "one", self.name, out))
        if rc or not os.path.exists(out):
            raise Stop("make_cover fail hua (upar error). --from 8 se dobara chalao.")
        self.st.done(8, csv=md5(self.csv), cover=out)

    # ---------- chalao ----------
    def plan(self):
        start = self.o["from"]
        if start:
            todo = [n for n in STEPS if n >= start or not self.is_done(n)]
        else:
            todo = [n for n in STEPS if not self.is_done(n)]
            if todo:                       # ek step dobara -> uske baad wale bhi dobara
                todo = [n for n in STEPS if n >= todo[0]]
        if self.o.get("tak"):              # --tak N: step N ke baad ruk jao
            todo = [n for n in todo if n <= self.o["tak"]]
        return todo

    def go(self):
        todo = self.plan()
        dry = self.o["dry"]
        say(f"\n=== {self.name} ===\nStory: {self.story}")
        for n, title in STEPS.items():
            later = self.o.get("tak") and n > self.o["tak"]
            say(f"  {n}. {title:36s} {'CHALEGA' if n in todo else 'nahi (--tak)' if later else 'skip (ho chuka)'}")
        if not todo:
            say("\nSab steps pehle se ho chuke. Dobara chahiye to --from <step number> lagao.")
            return True
        if dry:
            say("\n--dry-run: kuch nahi chalaya. Ye commands chalengi:")
            for n in todo:
                say(f"  {n}. " + self.describe(n))
            return True
        if 7 in todo and not dry:
            self.copy_ok = self.ask_copy()      # render se pehle hi pooch lo, baad mein wait na karna pade
        if self.o["from"]:
            self.st.undo_from(self.o["from"])
        for n in todo:
            say(f"\n--- STEP {n}: {STEPS[n]} ---")
            getattr(self, f"step{n}")()
        if self.o.get("tak") and self.o["tak"] < 8:
            say(f"\n--tak {self.o['tak']}: yahin ruk gaye. Aage ke liye:  --from {self.o['tak'] + 1}")
            return True
        self.summary()
        return True

    def describe(self, n):
        q = lambda s: f'"{s}"'
        info = self.st.d.get("info") or {}
        return {
            1: f"py prep_story.py {q(self.story)}",
            2: f"py -u build_voice.py {q(self.story)} {q(self.name)} {q(THINK_TEXT)} {THINK}  -> voice\\{self.name}.m4a",
            3: f"auto_csv -> cases\\{self.name}.csv (haath wali CSV ho to pehle poochega)",
            4: f"py make_cards.py options {info.get('options') or 'C<tag>_OPTIONS'} <suspects>  +  "
               f"py make_cards.py cover {q(self.name)} S16 {q(COVER_BIG)} <sawaal>",
            5: f"py check_reel.py {q(self.name)}  (PROBLEM -> yahin rukega)",
            6: f"py make_reel.py {q(self.name)}" + (" --force" if self.o["force"] else ""),
            7: f"copy output\\{self.name}.mp4 + CSV (timing.csv) -> story folder (purani MP4 ho to poochega)",
            8: f"py make_cover.py one {q(self.name)} {q(os.path.join(self.story, self.name + ' - COVER.png'))}",
        }[n]

    def summary(self):
        say("\n===== REEL TAIYAAR =====")
        say(f"MP4: {self.story_mp4}")
        if self.st.d.get("grid"):
            say(f"Frame check (ek baar dekho): {self.st.d['grid']}")
        if self.st.d.get("sheet"):
            say(f"Images contact sheet: {self.st.d['sheet']}")
        cover = (self.st.d["done"].get("8") or {}).get("cover")
        if cover:
            say(f"Cover: {cover}")
        say("Yaad rahe: CSV auto DRAFT thi - frame grid mein pose / text / khaali screen zaroor dekho.")


def parse_args(argv):
    opts = {"from": None, "tak": None, "dry": "--dry-run" in argv, "force": "--force" in argv, "yes": "--haan" in argv,
            "style": "rise"}
    pos, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a in ("--from", "--tak", "--style"):
            if i + 1 >= len(argv):
                raise Stop(f"{a} ke baad number / naam do")
            v = argv[i + 1]
            if a in ("--from", "--tak"):
                if not v.isdigit() or int(v) not in STEPS:
                    raise Stop(f"{a} ke baad 1 se 8 ka number do (diya: {v})")
                opts[a[2:]] = int(v)
            else:
                opts["style"] = v.lower()
            i += 2
            continue
        if not a.startswith("--"):
            pos.append(a)
        i += 1
    if len(pos) < 2:
        raise Stop('Chalao:  py make_full_reel.py "<story folder>" "<NN Title>"   (--dry-run / --from N / --force)')
    story = pos[0].strip().strip('"').rstrip("\\/")
    if not os.path.isdir(story) and not opts["dry"]:
        raise Stop(f"Story folder nahi mila: {story}")
    return story, pos[1].strip().strip('"'), opts


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    try:
        story, name, opts = parse_args(list(sys.argv[1:] if argv is None else argv))
        Reel(story, name, opts).go()
        return 0
    except Stop as e:
        say(f"\n!! RUK GAYA: {e}")
        return 1
    except KeyboardInterrupt:
        say("\n!! Band kar diya. Jo step ho chuke wo yaad hain - wahi command dobara chalao.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
