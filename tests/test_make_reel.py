import os, sys

import pytest

import make_reel as R
from conftest import SAMPLE, character, silence, tone, write_csv


def test_ffprobe_milta_hai():
    # pehle hamesha "<ffmpeg folder>\ffprobe.exe" maanta tha -> Linux / alag install par crash
    assert os.path.exists(R.FFPROBE)


def test_sample_csv_padh_leta_hai():
    rows = R.read_csv(os.path.join(SAMPLE, "timing.csv"))
    assert R.POP_STYLE == "rise"
    assert len(rows) == 29
    assert rows[0]["asset"] == "C002_ARYAN" and "night" in rows[0]["effects"]
    assert rows[1]["font"] == 90 and rows[1]["color"] == "yellow"


def test_khaali_rows_skip(box):
    p = os.path.join(R.CASES, "x.csv")
    write_csv(p, ["STYLE,0,1,,,pop,,,,", ",,,,,,,,,", "S01,0,2,center,55,,,,,", ",,,,,,,,,"])
    rows = R.read_csv(p)
    assert len(rows) == 1 and rows[0]["asset"] == "S01"


def test_focus_galat_to_saaf_message(box):
    # pehle "0.5" (sirf ek number) render ke beech crash karta tha (fx, fy = ...)
    p = os.path.join(R.CASES, "x.csv")
    write_csv(p, ["S01,0,2,center,55,,focus,,,0.5"])
    with pytest.raises(SystemExit) as e:
        R.read_csv(p)
    assert "line 2" in str(e.value)
    assert R.parse_focus("0.4;0.2") == (0.4, 0.2)
    assert R.parse_focus("") == (0.5, 0.3)


def test_csv_nahi_mili_to_crash_nahi(box, capsys):
    assert R.render("koi aur naam") is False
    assert "CSV nahi mili" in capsys.readouterr().out


def test_sirf_header_wali_csv(box, capsys):
    write_csv(os.path.join(R.CASES, "khaali.csv"), ["STYLE,0,1,,,rise,,,,"])
    silence(os.path.join(R.VOICE, "khaali.wav"), 1)
    assert R.render("khaali") is False
    assert "koi row nahi" in capsys.readouterr().out


def test_kharab_audio_par_saaf_message(box):
    bad = os.path.join(R.VOICE, "kharab.mp3")
    open(bad, "wb").write(b"ye mp3 nahi hai")
    with pytest.raises(SystemExit) as e:
        R.audio_duration(bad)
    assert "length nahi padh" in str(e.value)


def test_music_folder_khaali_to_common_music(box):
    assert R.find_music("x") is None
    os.makedirs(os.path.dirname(R.COMMON_MUSIC))
    tone(R.COMMON_MUSIC, 1)
    assert R.find_music("x") == R.COMMON_MUSIC
    tone(os.path.join(R.MUSIC, "bg music.mp3"), 1)
    assert R.find_music("x").endswith(os.path.join("music", "bg music.mp3"))


def test_bg_jpg_ko_gayab_nahi_maanta(box):
    from PIL import Image
    Image.new("RGB", (100, 200), (10, 10, 10)).save(os.path.join(R.ASSETS, "ROOM.jpg"))
    p = os.path.join(R.CASES, "bg.csv")
    write_csv(p, ["ROOM,0,1,center,55,,bg,,,"])
    rows = R.read_csv(p)
    assert R.check_case("bg", rows, R.build_layers(rows), 1.0) is True


def _chhoti_reel(box, name="02-001 Test Reel"):
    character(os.path.join(R.ASSETS, "S01.png"))
    character(os.path.join(R.ASSETS, "C001_A.png"), color=(60, 60, 200, 255))
    tone(os.path.join(R.SFX, "pop.wav"), 0.2, 900)
    tone(os.path.join(R.VOICE, name + ".wav"), 2.0)
    tone(os.path.join(R.MUSIC, "bg music.mp3"), 3.0, 220)
    write_csv(os.path.join(R.CASES, name + ".csv"), [
        "STYLE,0,1,,,rise,,,,",
        "S01,0,1,center,40,KILLER KAUN?,nopop,,yellow,",
        "C001_A,1,2,center,40,SUSPECT 1/1,,pop,yellow,",
    ])
    return name


def test_poori_reel_render(box, capsys):
    name = _chhoti_reel(box)
    assert R.render(name) is True
    out = capsys.readouterr().out
    assert "(music: bg music.mp3)" in out          # CLAUDE.md: log mein music dikhna chahiye
    assert "check OK" in out
    assert os.path.getsize(os.path.join(R.OUTPUT, name + ".mp4")) > 1000
    assert os.path.exists(os.path.join(R.OUTPUT, name + " - CHECK.png"))
    assert abs(R.audio_duration(os.path.join(R.OUTPUT, name + ".mp4")) - 2.0) < 0.2


def test_ffmpeg_beech_mein_band_to_crash_nahi(box, monkeypatch, capsys):
    # pehle BrokenPipeError ka lamba error aata tha; ab saaf "FFmpeg fail hua"
    if not os.path.exists("/bin/false"):
        pytest.skip("sirf Linux par")
    name = _chhoti_reel(box)
    monkeypatch.setattr(R, "FFMPEG", "/bin/false")
    assert R.render(name) is False
    assert "FFmpeg fail hua" in capsys.readouterr().out


def test_main_result_line(box, monkeypatch, capsys):
    name = _chhoti_reel(box)
    monkeypatch.setattr(R, "render", lambda c: True)
    monkeypatch.setattr(sys, "argv", ["make_reel.py", name])
    R.main()
    assert "Bani: 1" in capsys.readouterr().out
