# make_full_reel.py + auto_csv.py ke test (bina ffmpeg / images / ElevenLabs - nakli scripts)
#   py -m unittest discover tests

import csv, io, os, shutil, sys, tempfile, unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import auto_csv
import make_full_reel as M

SAMPLE = os.path.join(ROOT, "samples", "09-010 Til Gud ki Dopahar")
NAME = "09-010 Til Gud ki Dopahar"
IMAGES = ["C002_ARYAN", "C003_BHATIJA", "C004_AMIT", "C005_VICKY", "P_PATANG", "S04", "S06", "S12", "S17"]


THEFT_SCRIPT = """STORY 99 – Case 12-099: Nakli Test

========== VOICEOVER (Devanagari) ==========
क्या आप ये केस सॉल्व कर पाओगे?
क्लू इसी वीडियो में है। ध्यान से देखना।
शादी के घर में रात को हार गायब हो गया!
चार लोग घर में थे।
रमेश बोला... "मैं रसोई में था।"
सीमा बोली... "मैं सो रही थी।"
गोलू बोला... "मैं बाहर पटाखे जला रहा था, बहुत शोर था।"
काका बोले... "मैं मंदिर गया था।"
लेकिन एक बयान में छोटी सी गलती थी।
[dramatic] डिटेक्टिव शिवम ने चोर पकड़ लिया!
आंसर कमेंट करो।
शिवम की नज़र से कोई नहीं बचता।

========== SCENE ORDER ==========
P_HAAR → C001_RAMESH → C002_SEEMA → C003_GOLU → C004_KAKA → P_DIYA

========== ANSWER (sirf tumhare liye) ==========
Golu.
"""


def fake_build_voice_print():
    """build_voice.py jaisa print (sample ke JSON se andaza)"""
    t = auto_csv.estimate_from_json(os.path.join(SAMPLE, "VO_MAIN_timing.json"))
    lines = [f"THINK pause {t['think'][0]:.2f} -> {t['think'][1] - 3.0 + 3.0:.2f}"]
    lines += [f"{s:6.2f} {e:6.2f} {w}" for s, e, w in t["words"]]
    last = t["words"][-1][1]
    lines.append(f"last chunks start: {last - 3.0 + 0.1:.2f} {last - 3.0 + 3.0:.2f} (pre-think)  total {last + 5.7:.2f}")
    return "[queue] voice slot 1/4 mila\n" + "\n".join(lines) + "\n"


def read_rows(path_or_text):
    text = open(path_or_text, encoding="utf-8-sig").read() if os.path.exists(path_or_text) else path_or_text
    return list(csv.DictReader(io.StringIO(text)))


def image_order(rows):
    out = []
    for r in rows:
        a = r["asset_id"]
        if a and a != "STYLE" and (not out or out[-1] != a):
            out.append(a)
    return out


class FakeScripts:
    """subprocess ki jagah: har purana script jo file banata hai wo nakli bana do"""

    def __init__(self, check_rc=0):
        self.calls, self.check_rc = [], check_rc

    def __call__(self, cmd, log=None):
        script, args = os.path.basename(cmd[2]), cmd[3:]
        self.calls.append((script, args))
        out, rc = "", 0
        if script == "prep_story.py":
            out = "  * C003_BHATIJA: safed background hataya -> C003_BHATIJA_CUT\n\nCSV mein ye naam lagao:\n"
            out += "".join(f"   {a:28s} -> {a}_CUT\n" if a == "C003_BHATIJA" else f"   {a}\n" for a in IMAGES)
            out += "\nContact sheet -> output\\Story 10 0910 - IMAGES.png\n"
        elif script == "build_voice.py":
            out = fake_build_voice_print()
            open(os.path.join(M.VOICE, args[1] + ".m4a"), "w").close()
        elif script == "make_cards.py":
            if args[0] == "options":
                open(os.path.join(M.ASSETS, args[1] + ".png"), "w").close()
            else:
                open(os.path.join(M.OUTPUT, args[1] + " - COVER.png"), "w").close()
        elif script == "check_reel.py":
            rc = self.check_rc
            out = "[x] 1 PROBLEM (render nahi hoga, CSV theek karo):\n   - 5.0s: text image ke upar\n" if rc else \
                "[x] check OK\n"
        elif script == "make_reel.py":
            open(os.path.join(M.OUTPUT, args[0] + ".mp4"), "w").write("new")
            out = f"[{args[0]}] render... (music: bg music.mp3)\n===== RESULT =====\nBani: 1\n"
        elif script == "make_cover.py":
            open(args[2], "w").close()
        if log:
            open(log, "w", encoding="utf-8").write(out)
        return rc, out

    def scripts(self):
        return [c[0] for c in self.calls]


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        code = os.path.join(self.tmp, "code")
        self.story = os.path.join(self.tmp, "reels story", "Category 9", "Story 10")
        os.makedirs(os.path.join(self.story, "images"))
        for f in ("SCRIPT_09-010.txt", "VO_MAIN_timing.json"):
            shutil.copy(os.path.join(SAMPLE, f), self.story)
        open(os.path.join(self.story, "VO_MAIN.mp3"), "w").close()
        for a in IMAGES:
            open(os.path.join(self.story, "images", a + ".png"), "w").close()
        os.makedirs(os.path.join(self.tmp, "reels story", "Common"))
        open(os.path.join(self.tmp, "reels story", "Common", "bg music.mp3"), "w").close()
        self.patches = []
        for k in ("CASES", "ASSETS", "VOICE", "MUSIC", "OUTPUT"):
            p = os.path.join(code, k.lower())
            os.makedirs(p)
            self.patches.append(mock.patch.object(M, k, p))
        for p in self.patches:
            p.start()
        self.out = io.StringIO()
        self.patches.append(mock.patch("sys.stdout", self.out))
        self.patches[-1].start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def go(self, fake, *extra, stdin_answer=None):
        with mock.patch.object(M, "run", fake), \
                mock.patch.object(M, "ask", lambda q, auto=False: auto or bool(stdin_answer)):
            return M.main([self.story, NAME, *extra])

    def test_full_run(self):
        fake = FakeScripts()
        self.assertEqual(self.go(fake), 0, self.out.getvalue())
        self.assertEqual(fake.scripts(), ["prep_story.py", "build_voice.py", "make_cards.py", "make_cards.py",
                                          "check_reel.py", "make_reel.py", "make_cover.py"])
        bv = fake.calls[1][1]
        self.assertEqual(bv[2:], ["डिटेक्टिव शिवम", "3.0"])
        self.assertTrue(os.path.exists(os.path.join(self.story, NAME + ".mp4")))
        self.assertTrue(os.path.exists(os.path.join(self.story, "timing.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.story, NAME + " - COVER.png")))
        self.assertTrue(os.path.exists(os.path.join(M.MUSIC, "bg music.mp3")))      # Common se copy
        rows = read_rows(os.path.join(M.CASES, NAME + ".csv"))
        self.assertIn("C003_BHATIJA_CUT", image_order(rows))                        # prep_story wala naam
        opts = fake.calls[2][1]
        self.assertEqual(opts[:2], ["options", "C910_OPTIONS"])
        self.assertEqual(opts[2:], ["C005_VICKY:Vicky", "C004_AMIT:Amit", "C003_BHATIJA_CUT:Sonu"])
        self.assertEqual(fake.calls[3][1], ["cover", NAME, "S16", "99% LOG FAIL!", "KILLER KAUN?"])
        # story folder mein sirf MP4 + timing.csv + cover (state cases\ mein)
        self.assertEqual(sorted(os.listdir(self.story)), sorted(
            ["SCRIPT_09-010.txt", "VO_MAIN_timing.json", "VO_MAIN.mp3", "images", NAME + ".mp4", "timing.csv",
             NAME + " - COVER.png"]))
        self.assertTrue(os.path.exists(os.path.join(M.CASES, NAME + ".state.json")))
        # dobara chalao -> kuch nahi chalta
        fake2 = FakeScripts()
        self.assertEqual(self.go(fake2), 0)
        self.assertEqual(fake2.calls, [])

    def test_check_problem_stops_then_resume(self):
        fake = FakeScripts(check_rc=1)
        self.assertEqual(self.go(fake), 1)
        self.assertNotIn("make_reel.py", fake.scripts())
        self.assertIn("render NAHI kiya", self.out.getvalue())
        self.assertFalse(os.path.exists(os.path.join(self.story, NAME + ".mp4")))
        fake2 = FakeScripts()                     # CSV theek ki, dobara chalaya
        self.assertEqual(self.go(fake2), 0)
        self.assertEqual(fake2.scripts(), ["check_reel.py", "make_reel.py", "make_cover.py"])

    def test_force_goes_on(self):
        fake = FakeScripts(check_rc=1)
        self.assertEqual(self.go(fake, "--force"), 0)
        self.assertIn(("make_reel.py", [NAME, "--force"]), fake.calls)

    def test_edited_csv_reruns_check_and_render(self):
        self.go(FakeScripts())
        p = os.path.join(M.CASES, NAME + ".csv")
        open(p, "a", encoding="utf-8").write(",40.00,41.00,,,extra,,,,\n")
        fake = FakeScripts()
        self.assertEqual(self.go(fake, stdin_answer=True), 0)
        self.assertEqual(fake.scripts()[0], "make_cards.py")       # step 3 (CSV) skip, 4 se aage
        self.assertIn("extra", open(p, encoding="utf-8").read())    # haath wali CSV bachi rahi

    def test_from_skips_earlier(self):
        self.go(FakeScripts())
        fake = FakeScripts()
        self.assertEqual(self.go(fake, "--from", "6", "--haan"), 0)
        self.assertEqual(fake.scripts(), ["make_reel.py", "make_cover.py"])
        self.assertTrue(os.path.exists(os.path.join(self.story, NAME + " - COVER.png")))

    def test_from_3_asks_before_replacing_hand_csv(self):
        self.go(FakeScripts())
        p = os.path.join(M.CASES, NAME + ".csv")
        open(p, "a", encoding="utf-8").write(",40.00,41.00,,,haath se,,,,\n")
        self.go(FakeScripts(), "--from", "3")                      # jawab NAHI
        self.assertIn("haath se", open(p, encoding="utf-8").read())
        self.go(FakeScripts(), "--from", "3", "--haan")            # jawab haan -> nayi draft, purani .old
        self.assertNotIn("haath se", open(p, encoding="utf-8").read())
        self.assertIn("haath se", open(p + ".old", encoding="utf-8").read())

    def test_dry_run_does_nothing(self):
        fake = FakeScripts()
        self.assertEqual(self.go(fake, "--dry-run"), 0)
        self.assertEqual(fake.calls, [])
        self.assertEqual(os.listdir(M.CASES), [])
        self.assertIn("--dry-run", self.out.getvalue())
        self.assertIn("py make_reel.py", self.out.getvalue())

    def test_old_mp4_not_overwritten_without_yes(self):
        mp4 = os.path.join(self.story, NAME + ".mp4")
        open(mp4, "w").write("old")
        fake = FakeScripts()
        self.assertEqual(self.go(fake, stdin_answer=False), 1)
        self.assertEqual(open(mp4).read(), "old")
        self.assertFalse(os.path.exists(os.path.join(self.story, "timing.csv")))
        fake = FakeScripts()
        self.assertEqual(self.go(fake, stdin_answer=True), 0)
        self.assertEqual(open(mp4).read(), "new")

    def test_old_cover_kept(self):
        cover = os.path.join(self.story, NAME + " - COVER.png")
        open(cover, "w").write("old")
        self.go(FakeScripts(), "--haan")
        self.assertEqual(open(cover).read(), "old")
        self.assertTrue(os.path.exists(os.path.join(self.story, NAME + " - COVER NEW.png")))

    def test_missing_voice_tells_eleven(self):
        os.remove(os.path.join(self.story, "VO_MAIN.mp3"))
        fake = FakeScripts()
        self.assertEqual(self.go(fake), 1)
        self.assertIn("py eleven_voice.py 9 10", self.out.getvalue())
        self.assertNotIn("build_voice.py", fake.scripts())

    def test_bad_from(self):
        self.assertEqual(self.go(FakeScripts(), "--from", "12"), 1)


class AutoCsvTest(unittest.TestCase):
    def draft(self, names=None):
        timing = auto_csv.parse_build_voice(fake_build_voice_print())
        return auto_csv.build(SAMPLE, NAME, timing, names)

    def test_structure_matches_sample(self):
        rows, info = self.draft()
        mine = read_rows(auto_csv.to_text(rows))
        sample = read_rows(os.path.join(SAMPLE, "timing.csv"))
        # sample purani reel hai: S04 (aaj S01) aur soch-pause (S02) nahi tha
        want = ["S01" if a == "S04" else a for a in image_order(sample)]
        want.insert(want.index("S06"), "S02")
        self.assertEqual(image_order(mine), want)
        sus = lambda rs: [(r["asset_id"], r["text"], r["sfx"], r["color"]) for r in rs if r["text"].startswith("SUSPECT")]
        self.assertEqual(sus(mine), sus(sample))
        names = lambda rs: [r["text"] for rs_ in [rs] for k, r in enumerate(rs_)
                            if k and rs_[k - 1]["text"].startswith("SUSPECT")]
        self.assertEqual(names(mine), ["VICKY", "AMIT", "SONU"])
        self.assertEqual(info["options"], "C910_OPTIONS")

    def test_structure_rules(self):
        rows = read_rows(auto_csv.to_text(self.draft()[0]))
        self.assertEqual(list(rows[0].values())[:6], ["STYLE", "0", "1", "", "", "rise"])
        hook = rows[1]
        self.assertIn("nopop", hook["effect"])
        self.assertEqual((rows[2]["text"], rows[2]["color"], rows[2]["size"]), ("KILLER KAUN?", "yellow", "90"))
        by = lambda a: [r for r in rows if r["asset_id"] == a]
        self.assertEqual(by("S01")[0]["sfx"], "whoosh")
        crime = [r for r in by("C002_ARYAN") if r["sfx"] == "heartbeat"]
        self.assertTrue(crime and "night" in crime[0]["effect"])
        s02 = by("S02")[0]
        self.assertEqual((s02["effect"], s02["sfx"], s02["color"]), ("zoom+music_off", "tick_fast", "yellow"))
        i = rows.index(s02)
        a = float(s02["start"])
        for k, off in ((1, 1), (2, 2)):
            r = rows[i + k]
            self.assertEqual((r["asset_id"], r["effect"]), ("", "music_off"))
            self.assertAlmostEqual(float(r["start"]), a + off, places=2)
        self.assertAlmostEqual(float(s02["end"]) - a, 3.0, places=2)
        s06 = by("S06")[0]
        self.assertEqual((s06["effect"], s06["sfx"]), ("flash+music_off", "whoosh"))
        self.assertEqual(s06["start"], s02["end"])
        self.assertTrue(any(r["sfx"] == "boom" for r in rows))
        opt = by("C910_OPTIONS")[0]
        self.assertEqual(opt["sfx"], "ding")
        self.assertTrue(any(r["text"] == "Sahi answer kal pin hoga" and r["color"] == "yellow" for r in rows))
        end = rows[-1]
        self.assertEqual((end["asset_id"], end["effect"], end["sfx"]), ("S16", "noout", "whoosh"))
        # sab time aage badhte hain, end > start
        for r in rows[1:]:
            self.assertGreater(float(r["end"]), float(r["start"]), r)
        imgs = [r for r in rows[1:] if r["asset_id"] and r["asset_id"] not in ("S02",)]
        for x, y in zip(imgs, imgs[1:]):
            self.assertLessEqual(float(x["end"]), float(y["start"]) + 0.01, (x, y))

    def test_captions_roman_short_no_answer(self):
        rows = read_rows(auto_csv.to_text(self.draft()[0]))
        for r in rows[1:]:
            t = r["text"]
            self.assertFalse(any("ऀ" <= ch <= "ॿ" for ch in t), t)      # Devanagari nahi
            self.assertLessEqual(t.count("\\n") + 1, 3, t)
            self.assertNotIn("hawa", t.lower())                                    # ANSWER ka clue nahi
            self.assertNotIn("\n", t)                                              # nayi line = \n likha hua

    def test_names_used(self):
        rows, info = self.draft({"C003_BHATIJA": "C003_BHATIJA_CUT", "P_PATANG": "P_PATANG_UP"})
        order = image_order(read_rows(auto_csv.to_text(rows)))
        self.assertIn("C003_BHATIJA_CUT", order)
        self.assertIn("P_PATANG_UP", order)
        self.assertNotIn("C003_BHATIJA", order)

    def test_json_fallback(self):
        rows, info = auto_csv.build(SAMPLE, NAME, auto_csv.load_timing(SAMPLE, None))
        self.assertTrue(any("ANDAZA" in n for n in info["notes"]))
        self.assertIn("S02", image_order(read_rows(auto_csv.to_text(rows))))

    def test_theft_story_without_caption(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        open(os.path.join(tmp, "SCRIPT_12-099.txt"), "w", encoding="utf-8").write(THEFT_SCRIPT)
        pairs, _, _, _ = auto_csv.script_lines(os.path.join(tmp, "SCRIPT_12-099.txt"))
        words, t = [], 0.0
        for d, _ in pairs[:10]:
            for w, _ in auto_csv.vo_tokens(d):
                if w == "डिटेक्टिव":
                    think, t = (t, t + 3.0), t + 3.0
                words.append(f"{t:6.2f} {t + 0.3:6.2f} {w}")
                t += 0.4
        timing = auto_csv.parse_build_voice(f"THINK pause {think[0]:.2f} -> {think[1]:.2f}\n" + "\n".join(words))
        rows, info = auto_csv.build(tmp, "12-099 Nakli Test", timing)
        rows = read_rows(auto_csv.to_text(rows))
        self.assertEqual(info["hook"], "CHOR KAUN?")
        self.assertEqual(info["options"], "C1299_OPTIONS")
        self.assertEqual([a for a, _ in info["suspects"]], ["C001_RAMESH", "C002_SEEMA", "C003_GOLU", "C004_KAKA"])
        self.assertEqual(rows[1]["asset_id"], "P_HAAR")                      # chori: hook par saamaan
        self.assertNotIn("night", rows[1]["effect"])                          # maut nahi -> night nahi
        self.assertIn("1, 2, 3 ya 4?", [r for r in rows if r["asset_id"] == "C1299_OPTIONS"][0]["text"])
        self.assertTrue(any(r["asset_id"] == "P_DIYA" and r["sfx"] == "whoosh" for r in rows))   # clue image
        self.assertIn("KAAKA", [r["text"] for r in rows])
        for r in rows[1:]:
            self.assertFalse(any("\u0900" <= ch <= "\u097f" for ch in r["text"]), r["text"])

    def test_parse_prep_names(self):
        out = "  * X\n\nCSV mein ye naam lagao:\n   P_A                          -> P_A_CUT\n   S04\n\n" \
              "Contact sheet -> output\\a.png\n"
        self.assertEqual(auto_csv.parse_prep_names(out), {"P_A": "P_A_CUT", "S04": "S04"})

    def test_parse_build_voice(self):
        t = auto_csv.parse_build_voice("[queue] x\nTHINK pause 30.81 -> 33.81\n  0.10   0.40 ये\n"
                                       "last chunks start: 31.00 34.00 (pre-think)  total 40.10\n")
        self.assertEqual(t["think"], (30.81, 33.81))
        self.assertEqual(t["words"], [(0.1, 0.4, "ये")])
        self.assertEqual(t["total"], 40.1)

    def test_roman_fallback(self):
        self.assertEqual(auto_csv.roman("मकर संक्रांति"), "Makar sankraanti")


if __name__ == "__main__":
    unittest.main()
