# make_full_hf_reel.py ke test: samples/09-010 + nakli images / awaaz (bina ElevenLabs / internet / asli render)
import json, os, re, shutil, subprocess

import pytest

import auto_csv
import make_full_hf_reel as H
from conftest import FFMPEG, FONT, SAMPLE, character, silence, tone
from test_full_reel import IMAGES, NAME, FakeScripts, fake_build_voice_print

ANSWER = auto_csv.script_lines(auto_csv.find_script(SAMPLE))[2]


def sizes(a):
    return (1080, 780) if a.endswith("_OPTIONS") else (800, 400) if a.startswith("P_") else (500, 1000)


@pytest.fixture
def data():
    timing = auto_csv.parse_build_voice(fake_build_voice_print())
    return H.build_data(SAMPLE, NAME, timing, {"C003_BHATIJA": "C003_BHATIJA_CUT"}, sizes)


def words(d):
    return [w for ph in d["P"] for w in ph]


# ---------------- DATA ----------------
def test_structure_same_as_reel_format(data):
    d, rows = data
    order = [s["img"] for s in d["SCENES"]]
    assert order == ["C002_ARYAN", "S01", "P_PATANG", "C002_ARYAN", "C005_VICKY", "C004_AMIT", "C003_BHATIJA_CUT",
                     "S02", "S06", "C910_OPTIONS", "S16"]
    T = d["T"]
    assert T["hook"][2] == "KILLER KAUN?" and T["hook"][0] < 0.5
    assert [x[:2] for x in T["suspects"]] == [["SUSPECT 1/3", "VICKY"], ["SUSPECT 2/3", "AMIT"], ["SUSPECT 3/3", "SONU"]]
    s02 = d["SCENES"][order.index("S02")]
    assert T["soch"] == s02["s"] and abs(s02["e"] - s02["s"] - 3.0) < 0.02
    assert ["tick_fast", s02["s"]] in d["AUDIO"]["sfx"]
    assert "tick" not in [n for n, _ in d["AUDIO"]["sfx"]]
    s06 = d["SCENES"][order.index("S06")]
    assert s06["s"] == s02["e"] and s06["shake"] == [T["solved"][0]]
    assert ["boom", T["solved"][0]] in d["AUDIO"]["sfx"]
    assert T["crime"] and T["night"]                              # maut -> khoon + raat
    assert T["options"][2] == "1, 2 ya 3?" and ["ding", T["options"][0]] in d["AUDIO"]["sfx"]
    assert d["CFG"]["ctaText"] == "Sahi answer kal pin hoga"
    end = d["SCENES"][-1]
    assert end["enter"] == "rise" and end["noexit"] and end["e"] == d["END"] and T["brand"] > end["s"]
    assert d["CASE"] == "09-010" and d["OFF"] == 0
    # suspects alag-alag side se aate hain
    assert [s["enter"] for s in d["SCENES"][4:7]] == ["left", "right", "left"]


def test_music_off_soch_and_s06(data):
    d, _ = data
    soch, mutes = d["T"]["soch"], d["AUDIO"]["mutes"]
    assert [m[0] for m in mutes] == [soch, round(soch + 1, 2), round(soch + 2, 2), round(soch + 3, 2)]


def test_captions_word_level_roman_short(data):
    d, _ = data
    last = -1
    for ph in d["P"]:
        txt = [w for w, _, _ in ph]
        assert 1 <= len(txt) <= H.CAP_WORDS, txt
        assert len(auto_csv.wrap(txt, H.CAP_CHARS)) <= 2, txt
        assert ph[0][1] >= last
        last = ph[0][1]
        for w, s, e in ph:
            assert not re.search(r"[ऀ-ॿ]", w)
            assert 0 <= s <= e <= d["END"] + 0.01
    text = " ".join(w for w, _, _ in words(d)).lower()
    assert "hawa" not in text                                      # ANSWER ka clue kabhi nahi
    assert "kaatil" in text and "shivam ki nazar se" in text and "comment karo" in text
    assert len(d["P"]) > 25                                        # shabd-shabd caption poori reel mein
    assert d["CFG"]["activeWord"]                                  # bolta shabd peela


def test_caps_names_not_inside_quotes(data):
    d, _ = data
    ws = [w for w, _, _ in words(d)]
    assert "VICKY" in ws and "KAATIL" in ws
    quote, bad = False, []
    for w in ws:
        if w.startswith('"'):
            quote = True
        if quote and re.fullmatch(r"[^a-z]*[A-Z]{2,}[^a-z]*", w):
            bad.append(w)
        if quote and w.rstrip(".,!?…").endswith('"'):
            quote = False
    assert bad == []


def test_visual_change_every_3_sec(data):
    d, _ = data
    gap, at = H.max_visual_gap(d)
    assert gap <= H.MAX_GAP + 0.01, (gap, at)
    assert any(s.get("punch") for s in d["SCENES"])               # lambe scene mein punch
    for s in d["SCENES"]:
        for t in s.get("punch", []):
            assert s["s"] < t < s["e"]
        assert not s.get("zoom")                                    # clue par zoom nahi


def test_check_ok_and_safe_zone(data):
    d, _ = data
    probs, warns = H.check_data(d, ANSWER)
    assert probs == [], probs
    C = d["CFG"]
    for k, h in H.BOX_H.items():
        assert H.SAFE_TOP <= C[k] and C[k] + h <= H.SAFE_BOTTOM, k
    d["CFG"]["hdrTop"] = 120
    assert any("safe zone" in p for p in H.check_data(d, ANSWER)[0])


def test_check_catches_answer_devanagari_blank(data):
    d, _ = data
    d["P"].append([["\"28 din\"", d["END"] - 0.3, d["END"] - 0.1]])
    d["T"]["suspects"][0][1] = "विक्की"
    d["SCENES"][2]["s"] += 1.0
    probs = H.check_data(d, 'Feb 2023: 28 din tha. "28 din"')[0]
    assert any("ANSWER" in p for p in probs)
    assert any("Devanagari" in p for p in probs)
    assert any("khaali screen" in p for p in probs)


def test_layout_sizes():
    assert H.place("S01", (500, 1000)) == {"h": 1000, "bottom": 140}
    assert H.place("S16", (900, 1000))["bottom"] == 0
    opt = H.place("C910_OPTIONS", None)
    assert opt["w"] <= 980 and H.H - opt["bottom"] <= 1400             # CTA pill ke upar khatam
    lying = H.place("C002_ARYAN", (1200, 500))
    assert lying["w"] == 980 and lying["bottom"] == 300
    prop = H.place("P_PATANG", (800, 400))
    assert prop["w"] <= 880


def test_page_uses_engine_unchanged(data, tmp_path):
    d, _ = data
    eng = open(os.path.join(H.ENGINE, "shivam_engine.html"), encoding="utf-8").read()
    pg = H.page(d, NAME)
    assert "__DATA__" not in pg and "__DUR__" not in pg and "__TITLE__" not in pg
    tail = eng.split("// ===================== /DATA =====================")[1]
    assert pg.endswith(tail)                                       # engine code bilkul same
    assert f'data-duration="{d["END"]:.3f}"' in pg
    if shutil.which("node"):                                       # JS syntax sahi?
        js = pg.split("<script>")[-1].split("</script>")[0]
        p = tmp_path / "page.js"
        p.write_text(js, encoding="utf-8")
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr


def test_theft_story(tmp_path):
    from test_full_reel import THEFT_SCRIPT
    open(tmp_path / "SCRIPT_12-099.txt", "w", encoding="utf-8").write(THEFT_SCRIPT)
    pairs = auto_csv.script_lines(str(tmp_path / "SCRIPT_12-099.txt"))[0]
    lines, t, think = [], 0.0, None
    for dv, _ in pairs[:10]:
        for w, _ in auto_csv.vo_tokens(dv):
            if w == "डिटेक्टिव":
                think, t = (t, t + 3.0), t + 3.0
            lines.append(f"{t:6.2f} {t + 0.3:6.2f} {w}")
            t += 0.4
    timing = auto_csv.parse_build_voice(f"THINK pause {think[0]:.2f} -> {think[1]:.2f}\n" + "\n".join(lines))
    d, _ = H.build_data(str(tmp_path), "12-099 Nakli Test", timing, None, sizes)
    assert d["T"]["hook"][2] == "CHOR KAUN?"
    assert "crime" not in d["T"] and d["T"]["stamps"][0][0] == "CHORI!"
    assert d["T"]["night"] == []
    assert d["T"]["options"][2] == "1, 2, 3 ya 4?"
    assert H.check_data(d)[0] == []


# ---------------- pipeline (nakli scripts, asli mix.wav) ----------------
class FakeHF(FakeScripts):
    def __init__(self, render_rc=0):
        super().__init__()
        self.render_rc = render_rc

    def __call__(self, cmd, log=None):
        script, args = os.path.basename(cmd[2]), cmd[3:]
        if script == "build_voice.py":
            self.calls.append((script, args))
            out = fake_build_voice_print()
            t = auto_csv.parse_build_voice(out)
            tone(os.path.join(H.VOICE, args[1] + ".m4a"), seconds=round(t["total"], 2), freq=300)
            if log:
                open(log, "w", encoding="utf-8").write(out)
            return 0, out
        if script == "make_cards.py":
            self.calls.append((script, args))
            character(os.path.join(H.ASSETS, args[1] + ".png"), w=1000, h=700)
            return 0, "bana\n"
        return super().__call__(cmd, log)

    def shell(self, cmd, cwd):
        self.calls.append(("render", [cmd]))
        if not self.render_rc:
            open(os.path.join(cwd, "render.mp4"), "w").write("new")
        return self.render_rc, ""


@pytest.fixture
def hf(tmp_path, monkeypatch):
    code = tmp_path / "code"
    for k in ("CASES", "ASSETS", "VOICE", "MUSIC", "OUTPUT", "SFX", "HF"):
        p = code / k.lower()
        p.mkdir(parents=True)
        monkeypatch.setattr(H, k, str(p))
    monkeypatch.setattr(H, "FONT_FILE", FONT)
    story = tmp_path / "reels story" / "Category 9" / "Story 10"
    (story / "images").mkdir(parents=True)
    for f in ("SCRIPT_09-010.txt", "VO_MAIN_timing.json"):
        shutil.copy(os.path.join(SAMPLE, f), story)
    open(story / "VO_MAIN.mp3", "w").close()
    common = tmp_path / "reels story" / "Common"
    common.mkdir()
    tone(common / "bg music.mp3", seconds=5, freq=600)
    for a in IMAGES + ["C003_BHATIJA_CUT", "S01", "S02", "S16", "BG_MAIN", "LOGO_ROUND"]:
        character(os.path.join(H.ASSETS, a + ".png"))
    for a in IMAGES:
        open(story / "images" / (a + ".png"), "w").close()
    for s in ("whoosh", "boom", "ding", "tick_fast", "swish"):
        silence(os.path.join(H.SFX, s + ".wav"), 0.5)          # heartbeat jaan-bujh kar nahi (missing sfx)
    return {"story": str(story), "code": code}


def go(hf, fake, *extra, answer=None, monkeypatch=None):
    monkeypatch.setattr(H, "run", fake)
    monkeypatch.setattr(H, "run_shell", fake.shell)
    monkeypatch.setattr(H, "ask", lambda q, auto=False: auto or bool(answer))
    return H.main([hf["story"], NAME, *extra])


def test_full_hf_run(hf, monkeypatch, capsys):
    fake = FakeHF()
    assert go(hf, fake, monkeypatch=monkeypatch) == 0, capsys.readouterr().out
    assert fake.scripts() == ["prep_story.py", "build_voice.py", "make_cards.py", "render", "make_cover.py"]
    assert fake.calls[1][1][2:] == ["डिटेक्टिव शिवम", "3.0"]
    assert fake.calls[2][1][:2] == ["options", "C910_OPTIONS"]
    proj = os.path.join(H.HF, NAME)
    for f in ("index.html", "hf_data.json", "timing.csv", "hyperframes.json", "package.json", "assets/mix.wav",
              "assets/BG_MAIN.png", "assets/LOGO_ROUND.png", "assets/fonts/MAIN.ttf", "assets/cover.png",
              "assets/C003_BHATIJA_CUT.png", "assets/C910_OPTIONS.png", "assets/S16.png"):
        assert os.path.exists(os.path.join(proj, f)), f
    d = json.load(open(os.path.join(proj, "hf_data.json"), encoding="utf-8"))
    # mix.wav ki lambai = reel ki lambai
    import make_reel as mr
    assert abs(mr.audio_duration(os.path.join(proj, "assets", "mix.wav")) - d["END"]) < 0.1
    out = capsys.readouterr().out
    assert "music: bg music.mp3" in out and "heartbeat" in out          # missing sfx bataya
    story = hf["story"]
    assert sorted(os.listdir(story)) == sorted(["SCRIPT_09-010.txt", "VO_MAIN_timing.json", "VO_MAIN.mp3", "images",
                                                NAME + ".mp4", "timing.csv", NAME + " - COVER.png"])
    assert open(os.path.join(story, NAME + ".mp4")).read() == "new"
    assert os.path.exists(os.path.join(H.CASES, NAME + ".hf.state.json"))
    assert not os.path.exists(os.path.join(H.CASES, NAME + ".csv"))       # purane engine ki CSV nahi chhedi
    fake2 = FakeHF()                                                       # dobara: kuch nahi chalta
    assert go(hf, fake2, monkeypatch=monkeypatch) == 0
    assert fake2.calls == []


def test_music_ducked_and_muted(hf, monkeypatch, tmp_path):
    """voice chup + music tone: soch (music_off) mein music band, baaki jagah music hai"""
    timing = auto_csv.parse_build_voice(fake_build_voice_print())
    d, _ = H.build_data(SAMPLE, NAME, timing, None, sizes)
    voice, music, out = tmp_path / "v.wav", tmp_path / "m.wav", tmp_path / "mix.wav"
    tone(voice, 2, 150)            # voice 2 sec ke baad chup -> neeche ke saare naap sirf music ke
    tone(music, 5, 500)
    d["AUDIO"]["sfx"] = []
    H.build_mix(str(voice), str(music), d, str(out))

    def level(a, b):
        err = subprocess.run([FFMPEG, "-hide_banner", "-ss", str(a), "-t", str(b - a), "-i", str(out), "-af",
                              "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
        return float(re.search(r"mean_volume: (-?[\d.]+|-inf)", err).group(1).replace("-inf", "-200"))

    soch = d["T"]["soch"]
    talk, gap = d["AUDIO"]["speech"][1], (d["AUDIO"]["speech"][0][1], d["AUDIO"]["speech"][1][0])
    assert level(soch + 0.2, soch + 2.8) < -80                           # soch: music band
    quiet, loud = level(talk[0] + 1, talk[0] + 3), level(gap[0] + 0.05, gap[1] - 0.05)
    assert loud > -80 and 1.0 < loud - quiet < 3.0                       # bolte waqt ~2 dB aur neeche


def test_dry_run_does_nothing(hf, monkeypatch, capsys):
    fake = FakeHF()
    assert go(hf, fake, "--dry-run", monkeypatch=monkeypatch) == 0
    assert fake.calls == [] and os.listdir(H.CASES) == [] and os.listdir(H.HF) == []
    assert "hyperframes@" in capsys.readouterr().out


def test_tak_5_stops_before_story(hf, monkeypatch):
    fake = FakeHF()
    assert go(hf, fake, "--tak", "5", monkeypatch=monkeypatch) == 0
    assert "make_cover.py" not in fake.scripts()
    assert not os.path.exists(os.path.join(hf["story"], NAME + ".mp4"))
    assert os.path.exists(os.path.join(H.OUTPUT, NAME + " - HF.mp4"))
    fake2 = FakeHF()
    assert go(hf, fake2, "--from", "6", monkeypatch=monkeypatch) == 0
    assert fake2.scripts() == ["make_cover.py"]


def test_old_mp4_needs_yes(hf, monkeypatch):
    mp4 = os.path.join(hf["story"], NAME + ".mp4")
    open(mp4, "w").write("old")
    assert go(hf, FakeHF(), answer=False, monkeypatch=monkeypatch) == 1
    assert open(mp4).read() == "old"
    assert not os.path.exists(os.path.join(hf["story"], "timing.csv"))
    assert go(hf, FakeHF(), answer=True, monkeypatch=monkeypatch) == 0
    assert open(mp4).read() == "new"


def test_hand_edited_data_kept_and_rebuilt(hf, monkeypatch):
    go(hf, FakeHF(), monkeypatch=monkeypatch)
    p = os.path.join(H.HF, NAME, "hf_data.json")
    d = json.load(open(p, encoding="utf-8"))
    d["T"]["hook"][2] = "CHOR KAUN?"
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    fake = FakeHF()
    assert go(hf, fake, "--haan", monkeypatch=monkeypatch) == 0
    assert fake.scripts()[:2] == ["make_cards.py", "render"]              # step 3 skip, 4 se dobara
    assert "CHOR KAUN?" in open(os.path.join(H.HF, NAME, "index.html"), encoding="utf-8").read()
    go(hf, FakeHF(), "--from", "3", monkeypatch=monkeypatch)              # jawab NAHI -> haath wala bacha
    assert "CHOR KAUN?" in open(p, encoding="utf-8").read()


def test_existing_hand_project_not_touched(hf, monkeypatch):
    proj = os.path.join(H.HF, NAME)
    os.makedirs(proj)
    open(os.path.join(proj, "index.html"), "w").write("haath ka")
    assert go(hf, FakeHF(), monkeypatch=monkeypatch) == 1
    assert open(os.path.join(proj, "index.html")).read() == "haath ka"


def test_voice_from_make_full_reel_reused(hf, monkeypatch):
    open(os.path.join(H.CASES, NAME + ".voice_times.txt"), "w", encoding="utf-8").write(fake_build_voice_print())
    t = auto_csv.parse_build_voice(fake_build_voice_print())
    tone(os.path.join(H.VOICE, NAME + ".m4a"), seconds=round(t["total"], 2))
    fake = FakeHF()
    assert go(hf, fake, "--tak", "4", monkeypatch=monkeypatch) == 0
    assert "build_voice.py" not in fake.scripts()


def test_render_fail_stops(hf, monkeypatch, capsys):
    assert go(hf, FakeHF(render_rc=1), monkeypatch=monkeypatch) == 1
    assert "render fail" in capsys.readouterr().out
    assert not os.path.exists(os.path.join(hf["story"], NAME + ".mp4"))


def test_missing_image_stops_before_render(hf, monkeypatch, capsys):
    os.remove(os.path.join(H.ASSETS, "S16.png"))
    fake = FakeHF()
    assert go(hf, fake, monkeypatch=monkeypatch) == 1
    assert "S16.png" in capsys.readouterr().out and "render" not in fake.scripts()


def test_bad_args(monkeypatch):
    assert H.main(["x"]) == 1
    assert H.main(["x", "y", "--from", "9", "--dry-run"]) == 1
