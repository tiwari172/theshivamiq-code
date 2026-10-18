import base64, json, os, subprocess, sys, threading, time, unicodedata

import pytest

import make_reel as R
import voice_queue as Q
from conftest import ROOT, SAMPLE, silence, speech, tone


# ---------------- voice_queue ----------------
def test_slot_alag_folder_aur_saaf(box):
    with Q.slot("voice") as a:
        with Q.slot("voice") as b:
            assert a != b and os.path.isdir(a) and os.path.isdir(b)
    assert not os.path.exists(a) and not os.path.exists(b)


def test_slot_busy_to_line_mein_wait(box, monkeypatch, capsys):
    monkeypatch.setitem(Q.SLOTS, "test", 1)
    monkeypatch.setattr(Q, "WAIT", 0.05)
    order = []

    def second():
        with Q.slot("test"):
            order.append("dusra")

    with Q.slot("test"):
        t = threading.Thread(target=second)
        t.start()
        time.sleep(0.3)
        order.append("pehla khatam")
    t.join(5)
    assert order == ["pehla khatam", "dusra"]
    assert "line mein wait" in capsys.readouterr().err


def test_safe_replace(tmp_path):
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text("naya")
    b.write_text("purana")
    Q.safe_replace(str(a), str(b))
    assert b.read_text() == "naya" and not a.exists()


def test_voice_queue_bina_command():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "voice_queue.py")], capture_output=True, text=True)
    assert r.returncode != 0 and "Aise chalao" in r.stderr


# ---------------- tighten_voice ----------------
def test_minus_silence_start_se_faltu_tukda_nahi():
    import tighten_voice as T
    log = ("[silencedetect] silence_start: -0.00133\n[silencedetect] silence_end: 0.8 | silence_duration: 0.8\n"
           "[silencedetect] silence_start: 2.5\n[silencedetect] silence_end: 3.4 | silence_duration: 0.9\n")
    chunks = T.chunks_from_log(log, 5.0)
    # pehle "-0.00133" ko "0.00133" padhta tha -> shuru mein ek faltu chhota tukda + 0.28s chup
    assert len(chunks) == 2
    assert chunks[0][0] == pytest.approx(0.74)


def test_tighten_voice_chalta_hai(tmp_path):
    src, dst = tmp_path / "in.wav", tmp_path / "out.wav"
    speech(src, [(1.0, 1.5), (1.0, 1.5), (1.0, 0)])
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tighten_voice.py"), str(src), str(dst)],
                       capture_output=True, text=True, check=True)
    lines = [l for l in r.stdout.splitlines() if "->" in l]
    assert lines[0].strip().startswith("purana time")   # header wahi
    assert len(lines) == 4                               # 3 tukde
    assert R.audio_duration(str(dst)) < R.audio_duration(str(src)) - 2
    assert not [f for f in os.listdir(tmp_path) if ".part" in f]


def test_tighten_chup_file(tmp_path):
    src = tmp_path / "chup.wav"
    silence(src, 2)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tighten_voice.py"), str(src), str(tmp_path / "o.m4a")],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "koi awaaz nahi" in r.stderr


# ---------------- build_voice ----------------
def test_find_think_nukta_dono_roop():
    import build_voice as B
    text = unicodedata.normalize("NFC", "क़ातिल भागा... डिटेक्टिव शिवम ने क़ातिल पकड़ लिया!")
    assert B.find_think(text, "डिटेक्टिव शिवम") == text.index("डिटेक्टिव")
    assert B.find_think(text, "क़ातिल पकड़") > 0                 # क़ ek akshar wala roop
    assert B.find_think(text, "क़ातिल") == text.rfind("क़ातिल")       # aakhri match
    assert B.find_think(text, "inspector") == -1


def test_remap():
    import build_voice as B
    table = [(0.0, 1.0, 0.0, 0.9), (2.0, 3.0, 1.2, 2.1)]
    assert B.remap(0.5, table) == pytest.approx(0.45)
    assert B.remap(1.5, table) == pytest.approx(0.9)      # chup wale hisse mein -> pichhle tukde ka end


def _timing_json(path, phrases):
    """phrases = [(text, start, end)] -> ElevenLabs jaisa character timing"""
    chars, st, en = [], [], []
    for i, (txt, a, b) in enumerate(phrases):
        if i:
            chars.append(" "); st.append(a); en.append(a)
        step = (b - a) / len(txt)
        for k, c in enumerate(txt):
            chars.append(c); st.append(a + k * step); en.append(a + (k + 1) * step)
    json.dump({"characters": chars, "character_start_times_seconds": st,
               "character_end_times_seconds": en}, open(path, "w", encoding="utf8"), ensure_ascii=False)


@pytest.fixture
def bv(box, monkeypatch):
    import build_voice as B
    story = box["root"] / "reels story" / "Category 9" / "Story 10"
    common = box["root"] / "reels story" / "Common"
    story.mkdir(parents=True)
    common.mkdir(parents=True, exist_ok=True)
    # 3 tukde: hook | kahani | "डिटेक्टिव शिवम ने पकड़ लिया!"
    speech(story / "VO_MAIN.mp3", [(1.0, 1.0), (1.0, 1.0), (1.2, 0.3)])
    _timing_json(story / "VO_MAIN_timing.json",
                 [("[whispers]", 0.0, 0.0), ("हिम्मत है?", 0.0, 1.0), ("तीन बजे...", 2.0, 3.0),
                  ("[dramatic]", 4.0, 4.0), ("डिटेक्टिव शिवम ने पकड़ लिया!", 4.0, 5.2)])
    speech(common / "CTA_HI.mp3", [(0.8, 0.4)])
    speech(common / "SIGNATURE_HI.mp3", [(0.8, 0.3)])
    monkeypatch.setattr(B, "COMMON", str(common))
    monkeypatch.setattr(B, "VOICE_DIR", str(box["voice"]))
    monkeypatch.delenv("CTA_FILE", raising=False)
    return B, story


def test_build_voice_poora(bv, box, capsys):
    B, story = bv
    B.main([str(story), "09-010 Test", "डिटेक्टिव शिवम", "3.0"])
    out = capsys.readouterr().out.splitlines()
    think = [l for l in out if l.startswith("THINK pause")]
    assert len(think) == 1
    a, b = map(float, think[0].split()[2::2])
    assert b - a == pytest.approx(3.0)
    words = [l for l in out if l[:7].strip().replace(".", "").isdigit()]
    names = [l.split()[2] for l in words]
    assert names == ["हिम्मत", "है?", "तीन", "बजे...", "डिटेक्टिव", "शिवम", "ने", "पकड़", "लिया!"]   # [tag] hata
    det = float(words[4].split()[0])
    assert a < det and det > 3.0                     # think ke baad wale shabd 3s aage
    assert out[-1].startswith("last chunks start:")
    final = box["voice"] / "09-010 Test.m4a"
    assert final.exists()
    assert R.audio_duration(str(final)) > 8.0


def test_build_voice_think_text_galat(bv, capsys):
    B, story = bv
    with pytest.raises(SystemExit) as e:   # pehle poora kaam karke IndexError crash
        B.main([str(story), "x", "इंस्पेक्टर", "3.0"])
    assert "nahi mila" in str(e.value)


def test_build_voice_file_gayab(bv):
    B, story = bv
    os.remove(story / "VO_MAIN.mp3")
    with pytest.raises(SystemExit) as e:
        B.main([str(story), "x"])
    assert "VO_MAIN.mp3" in str(e.value)


def test_build_voice_mein_hardcoded_path_nahi():
    src = open(os.path.join(ROOT, "build_voice.py"), encoding="utf8").read()
    assert 'os.chdir(r"C:' not in src


# ---------------- eleven_voice (API kabhi call nahi) ----------------
def test_strip_fixed_nukta_dono_roop():
    import eleven_voice as E
    precomposed = "शिवम की नज़र से कोई नहीं बचता।"     # ज़ = ek akshar (U+095B)
    text = "कहानी की line\n" + precomposed + "\nआंसर कमेंट करो\nCOMMENT karo"
    assert E.strip_fixed(text) == "कहानी की line"


def test_sample_vo_se_sirf_kahani(box, monkeypatch):
    import eleven_voice as E
    root = box["root"] / "reels story"
    folder = root / "Category 9" / "Story 10"
    folder.mkdir(parents=True)
    import shutil
    shutil.copy(os.path.join(SAMPLE, "VO_09-010.txt"), folder)
    got = {}
    monkeypatch.setattr(E, "STORY_ROOT", str(root))
    monkeypatch.setattr(E, "voice_id", lambda key: "VID")
    monkeypatch.setattr(E, "run", lambda key, vid, jobs: got.setdefault("jobs", jobs))
    E.do_stories("KEY", 9, "10", False)
    (label, text, out), = got["jobs"]
    assert out.endswith(os.path.join("Story 10", "VO_MAIN.mp3"))
    assert text.rstrip().endswith("पकड़ लिया!")          # CTA + signature nahi (wo Common se judte hain)
    assert "कमेंट" not in text and "नज़र" not in text


def test_story_number_galat():
    import eleven_voice as E
    assert list(E.story_nums("9-11")) == [9, 10, 11]
    with pytest.raises(SystemExit):
        E.story_nums("9-")


def test_main_category_galat(tmp_path, monkeypatch):
    import eleven_voice as E
    (tmp_path / "k.txt").write_text("KEY")
    monkeypatch.setattr(E, "KEY_FILE", str(tmp_path / "k.txt"))
    monkeypatch.setattr(sys, "argv", ["eleven_voice.py", "abc", "9"])
    with pytest.raises(SystemExit) as e:
        E.main()
    assert "Aise likho" in str(e.value)


def test_voice_file_khaali(tmp_path, monkeypatch):
    import eleven_voice as E
    (tmp_path / "v.txt").write_text("")
    monkeypatch.setattr(E, "VOICE_FILE", str(tmp_path / "v.txt"))
    monkeypatch.setattr(E, "call", lambda path, key, body=None: json.dumps(
        {"voices": [{"name": "Rudra Hindi", "voice_id": "abc123"}]}).encode())
    assert E.voice_id("KEY") == "abc123"                  # pehle IndexError crash


def test_speak_files_likhta_hai_mock_api(box, tmp_path, monkeypatch):
    import eleven_voice as E
    fake = {"audio_base64": base64.b64encode(b"MP3DATA").decode(),
            "alignment": {"characters": ["a"], "character_start_times_seconds": [0],
                          "character_end_times_seconds": [0.1]}}
    calls = []
    monkeypatch.setattr(E, "call", lambda path, key, body=None: calls.append(path) or json.dumps(fake).encode())
    out = str(tmp_path / "VO_MAIN.mp3")
    E.speak("KEY", "VID", "नमस्ते", out)
    assert open(out, "rb").read() == b"MP3DATA"
    assert json.load(open(str(tmp_path / "VO_MAIN_timing.json")))["characters"] == ["a"]
    E.speak("KEY", "VID", "नमस्ते", out)                  # dobara -> skip, credit nahi
    assert len(calls) == 1


# ---------------- tts_voice ----------------
def test_tts_script_padhna(tmp_path):
    import tts_voice as V
    p = tmp_path / "s.txt"
    p.write_text("# comment\nnormal | 0.3 | नमस्ते\n\nserious|0.5|दूसरी लाइन\n", encoding="utf-8")
    assert V.read_script(str(p)) == [("normal", 0.3, "नमस्ते"), ("serious", 0.5, "दूसरी लाइन")]
    p.write_text("normal | नमस्ते\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        V.read_script(str(p))
    p.write_text("normal | aadha | नमस्ते\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        V.read_script(str(p))


def test_tts_temp_nahi_slot_folder(box, monkeypatch, tmp_path):
    import tts_voice as V
    used = []

    async def fake_speak(text, mood, path):     # internet nahi: nakli awaaz
        used.append(os.path.dirname(path))
        tone(path, 0.5)
    monkeypatch.setattr(V, "speak", fake_speak)
    monkeypatch.setattr(V, "BASE", str(tmp_path))
    (tmp_path / "voice_scripts").mkdir()
    (tmp_path / "voice_scripts" / "t.txt").write_text("normal | 0.2 | एक\ncalm | 0 | दो\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["tts_voice.py", "t"])
    V.main()
    assert (tmp_path / "voice" / "t.m4a").exists()
    assert used[0].startswith(Q.WORK)                     # $TEMP nahi
    assert not os.path.exists(used[0])                    # kaam ke baad saaf


# ---------------- .bat files ----------------
def test_bat_files():
    reel = open(os.path.join(ROOT, "REEL BANAO.bat"), encoding="utf8").read()
    voice = open(os.path.join(ROOT, "VOICE BANAO.bat"), encoding="utf8").read()
    assert 'cd /d "%~dp0"' in reel and "make_reel.py %*" in reel
    assert "eleven_voice.py %CAT% %STORY%" in voice and 'if "%CAT%"=="" goto run1' in voice
    attrs = open(os.path.join(ROOT, ".gitattributes"), encoding="utf8").read()
    assert "*.bat text eol=crlf" in attrs
