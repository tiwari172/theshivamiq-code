import os, shutil, sys

import pytest
from PIL import Image

import make_reel as R
from conftest import FONT, bottom_prop, character, white_bg, write_csv


# ---------------- prep_story ----------------
@pytest.fixture
def story(box):
    folder = box["root"] / "reels story" / "Category 9" / "Story 10"
    (folder / "images").mkdir(parents=True)
    return folder


def run_prep(monkeypatch, capsys, arg):
    import prep_story
    monkeypatch.setattr(sys, "argv", ["prep_story.py", arg])
    prep_story.main()
    return capsys.readouterr().out


def test_prep_story_poora(box, story, monkeypatch, capsys):
    img = story / "images"
    character(img / "S01.png")
    white_bg(img / "P_GHADI.png")
    bottom_prop(img / "SOFA.png")
    Image.new("RGB", (50, 50)).save(img / "P_PHOTO.jpg")
    # Windows: "...\Story 10\"  ->  argv mein aakhir mein " aa jaata hai
    out = run_prep(monkeypatch, capsys, str(story) + os.sep + '"')
    assert "CSV mein ye naam lagao:" in out
    assert "P_GHADI                      -> P_GHADI_CUT" in out
    assert "SOFA                         -> SOFA_UP" in out      # pehle "S" ki wajah se chhoot jaata
    assert "\n   S01\n" in out
    assert "P_PHOTO.jpg: PNG nahi hai" in out
    for a in ("S01", "P_GHADI", "P_GHADI_CUT", "SOFA", "SOFA_UP"):
        assert os.path.exists(os.path.join(R.ASSETS, a + ".png"))
    cut = Image.open(os.path.join(R.ASSETS, "P_GHADI_CUT.png"))
    assert cut.getpixel((2, 2))[3] == 0          # safed kona ab transparent
    assert os.path.exists(os.path.join(R.OUTPUT, "Story 10 0910 - IMAGES.png"))


def test_prep_story_same_naam_alag_image(box, story, monkeypatch, capsys):
    character(os.path.join(R.ASSETS, "C002_ARYAN.png"), color=(0, 200, 0, 255))
    character(story / "images" / "C002_ARYAN.png", color=(200, 0, 0, 255))
    out = run_prep(monkeypatch, capsys, str(story))
    assert "C002_ARYAN                   -> C002_ARYAN_0910" in out
    # purani wali overwrite nahi hui
    assert Image.open(os.path.join(R.ASSETS, "C002_ARYAN.png")).getpixel((150, 300))[1] == 200


def test_prep_story_koi_png_nahi(box, story, monkeypatch, capsys):
    with pytest.raises(SystemExit) as e:
        run_prep(monkeypatch, capsys, str(story))
    assert "koi PNG nahi" in str(e.value)


# ---------------- make_cards ----------------
@pytest.fixture
def cards(box, monkeypatch):
    import make_cards
    for k in ("ASSETS", "OUTPUT", "BG_FILE"):
        monkeypatch.setattr(make_cards, k, getattr(R, k))
    monkeypatch.setattr(make_cards, "FONT_FILE", FONT)
    return make_cards


def test_options_card(cards):
    character(os.path.join(R.ASSETS, "C001_A.png"))
    character(os.path.join(R.ASSETS, "G_B.png"))
    cards.options("C001_OPTIONS", ["C001_A:Ramu", "G_B:Mr: Bhola"])   # naam mein ':' bhi chalega
    im = Image.open(os.path.join(R.ASSETS, "C001_OPTIONS.png"))
    assert im.size[0] == R.W


def test_options_galat_item(cards):
    with pytest.raises(SystemExit) as e:
        cards.options("X", ["C001_A"])
    assert "ID:Naam" in str(e.value)
    with pytest.raises(SystemExit) as e:
        cards.options("X", ["GAYAB:Koi"])
    assert "image nahi mili" in str(e.value)


def test_cards_cover(cards):
    character(os.path.join(R.ASSETS, "S16.png"))
    cards.cover("01 Test", "S16", "99% LOG FAIL!", "KILLER KAUN?")
    assert Image.open(os.path.join(R.OUTPUT, "01 Test - COVER.png")).size == (R.W, R.H)


# ---------------- make_cover / make_cover2 ----------------
@pytest.fixture
def cov(box, monkeypatch):
    import make_cover
    character(box["assets"] / "S16.png")
    Image.new("RGBA", (200, 200), (255, 200, 0, 255)).save(box["assets"] / "LOGO_ROUND.png")
    monkeypatch.setattr(make_cover, "BASE", str(box["root"]))
    monkeypatch.setattr(make_cover, "STORY_ROOT", str(box["root"] / "reels story"))
    monkeypatch.setattr(make_cover, "FACE_FILE", str(box["assets"] / "S16.png"))
    monkeypatch.setattr(make_cover, "LOGO_FILE", str(box["assets"] / "LOGO_ROUND.png"))
    monkeypatch.setattr(make_cover, "IMPACT", FONT)
    monkeypatch.setattr(make_cover, "BLACK", FONT)
    make_cover._BG = None
    return make_cover


def test_cover_info(cov, box):
    assert cov.info("10-004 Joshi ji ki Angoothi") == ("CASE #10-004", "JOSHI JI KI ANGOOTHI", "KILLER KAUN?")
    assert cov.info("H01-002 Hook")[0] == "CASE #H01-002"
    assert cov.info("04 Raat Gyarah Baje", "1")[0] == "CASE #01-004"
    write_csv(box["cases"] / "02-003 Chor.csv", ["STYLE,0,1,,,rise,,,,", ",0,3,,90,CHOR KAUN?,nopop,,yellow,"])
    assert cov.info("02-003 Chor")[2] == "CHOR KAUN?"
    with pytest.raises(ValueError):         # pehle AttributeError crash (poora "all" ruk jaata)
        cov.info("final video")
    assert cov.category("x/Category Hooks/Story 01") is None
    assert cov.category("x/Category 12/Story 01") == "12"


def test_cover_all_ajeeb_naam_skip(cov, box, monkeypatch, capsys):
    root = box["root"] / "reels story"
    good = root / "Category 10" / "Story 04"
    bad = root / "Category Hooks" / "Story 01"
    for f in (good, bad):
        f.mkdir(parents=True)
    (good / "10-004 Joshi ji ki Angoothi.mp4").write_bytes(b"x")
    (bad / "final.mp4").write_bytes(b"x")
    monkeypatch.setattr(sys, "argv", ["make_cover.py", "all"])
    cov.main()
    out = capsys.readouterr().out
    assert "skip:" in out and "1 cover bane." in out
    assert (good / "10-004 Joshi ji ki Angoothi - COVER.png").exists()
    # dobara chalao -> purana nahi mitta, NEW banta hai (pehle jaisa)
    cov.main()
    assert (good / "10-004 Joshi ji ki Angoothi - COVER NEW.png").exists()


def test_cover_one_kam_argument(cov, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["make_cover.py", "one", "10-004 X"])
    with pytest.raises(SystemExit) as e:
        cov.main()
    assert "Aise likho" in str(e.value)


def test_cover2(cov, box, monkeypatch, capsys):
    import make_cover2 as c2
    assert c2.info is cov.info                       # ab ek hi jagah (duplicate hata)
    monkeypatch.setattr(c2, "BASE", str(box["root"]))
    monkeypatch.setattr(c2, "LOGO_FILE", cov.LOGO_FILE)
    monkeypatch.setattr(c2, "IMPACT", FONT)
    monkeypatch.setattr(c2, "BLACK", FONT)
    face = cov.FACE_FILE
    monkeypatch.setattr(sys, "argv", ["make_cover2.py", "one", "10-004 Test"])
    with pytest.raises(SystemExit):                  # out.png nahi diya -> saaf error (pehle save(None) crash)
        c2.main()
    shutil.rmtree(box["output"])                     # output folder na ho tab bhi chale
    monkeypatch.setattr(sys, "argv", ["make_cover2.py", "options", "10-004 Test", "--face", face])
    c2.main()
    for k in "ABC":
        assert (box["output"] / f"10-004 COVER {k}.png").exists()
    assert (box["output"] / "10-004 COVER OPTIONS.png").exists()


def test_cover2_green_screen_face(tmp_path):
    import make_cover2 as c2
    im = Image.new("RGBA", (200, 300), (0, 255, 0, 255))
    im.paste((90, 60, 40, 255), (50, 50, 150, 250))
    im.save(tmp_path / "g.png")
    out = c2.load_face(str(tmp_path / "g.png"))
    assert out.getpixel((5, 5))[3] == 0 and out.getpixel((100, 150))[3] > 200


# ---------------- make_sfx (badla nahi, bas chal ke dekha) ----------------
def test_make_sfx(tmp_path, monkeypatch):
    import wave
    import make_sfx
    monkeypatch.setattr(make_sfx, "OUT", str(tmp_path))
    for name in ("pop", "pop2", "swish", "whoosh", "boom", "heartbeat", "ding"):
        make_sfx.save(name, getattr(make_sfx, name)())
        with wave.open(str(tmp_path / (name + ".wav"))) as w:
            assert w.getframerate() == 44100 and w.getnframes() > 1000
