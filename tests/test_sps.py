import os

import openpyxl
import pytest

import sps


def test_settings_parse_colors_and_comments():
    assert sps.S["color_clue"] == "#FFD400"          # rang ka '#' comment nahi samjha gaya
    assert sps.S["common_folder"] == "auto"
    assert ";" in sps.S["extra_png_folders"]
    assert sps.num("fps") == 30


def test_num_missing_or_bad_gives_clear_message(monkeypatch):
    monkeypatch.delitem(sps.S, "fps")
    with pytest.raises(SystemExit, match="fps"):
        sps.num("fps")
    monkeypatch.setitem(sps.S, "fps", "3o")
    with pytest.raises(SystemExit, match="number nahi"):
        sps.num("fps")


HDR = ["Case", "Part", "Shot", "Start", "End", "Cue", "PNG", "Position", "Size", "Animation", "Mirror",
       "On-screen Text", "Text Type", "Text Position", "SFX at", "SFX", "Music", "Overlay"]


def test_short_rows_and_blank_rows_dont_crash():
    rows = [("SS-001", 1, 1, 0, 2, "पहली", "S01", "C", "55"),     # chhoti row (baaki columns nahi)
            (None,) * len(HDR),                                   # khaali row
            ("SS-001", 1, 2, 2, 4, "दूसरी")]
    X = {"Edit Timeline": (HDR, rows), "Scripts": ([], []), "Cover Design": ([], []), "Tracker": ([], [])}
    assert sps.part_list(X) == [("SS-001", "1")]
    shots, level = sps.get_shots(X, "SS-001", 1)
    assert len(shots) == 2 and shots[0]["ids"] == ["S01"] and shots[1]["ids"] == []


def test_no_sfx_column_ok():
    hd = [h for h in HDR if h != "SFX"]
    X = {"Edit Timeline": (hd, [("SS-001", 1, 1, 0, 2, "x")])}
    shots, _ = sps.get_shots(X, "SS-001", "1")
    assert shots[0]["sfx"] == ""


def test_missing_sheets_or_columns_return_empty():
    X = {"Scripts": ([], []), "Cover Design": (["Case", "Part"], [("SS-001", 1)])}
    assert sps.get_script(X, "SS-001", 1) == ("", "", "")
    assert sps.get_cover_row(X, "SS-001", 1)["title"] == ""


def test_part_folder_exact_case(tmp_path, monkeypatch):
    (tmp_path / "SS-0010 Galat" / "Part 1").mkdir(parents=True)
    (tmp_path / "SS-001 Sahi" / "Part 1").mkdir(parents=True)
    monkeypatch.setattr(sps, "SERIES", str(tmp_path))
    story, part = sps.part_folder("SS-001", 1)
    assert os.path.basename(story) == "SS-001 Sahi"


def test_build_timing_only_tail_shots():
    shots = [{"cue": "(end)", "xs": 0, "xe": 2, "n": "1"}, {"cue": "(end2)", "xs": 2, "xe": 3, "n": "2"}]
    al = sps.Align(["कुछ"], [], 5.0)
    total, found, n = sps.build_timing(shots, al, 5.0, 1)
    assert total >= 5.0 and all("s" in s for s in shots)


def test_main_usage_and_default_part(monkeypatch):
    with pytest.raises(SystemExit):
        sps.main(["cover"])
    calls = []
    monkeypatch.setattr(sps, "load_excel", lambda: {})
    monkeypatch.setattr(sps, "make_part", lambda X, c, p, r, **k: calls.append((c, p, k)) or True)
    monkeypatch.setattr(sps, "write_report", lambda r: None)
    sps.main(["cover", "ss-001"])
    assert calls == [("SS-001", "1", {"cover_only": True})]


def test_all_mode_continues_after_error(monkeypatch):
    monkeypatch.setattr(sps, "load_excel", lambda: {})
    monkeypatch.setattr(sps, "part_list", lambda X: [("SS-001", "1"), ("SS-002", "1")])
    monkeypatch.setattr(sps, "part_folder", lambda c, p: (None, None))
    done = []

    def mp(X, case, part, report, **k):
        if case == "SS-001":
            raise ValueError("kharab row")
        done.append(case)
        return True
    monkeypatch.setattr(sps, "make_part", mp)
    reports = []
    monkeypatch.setattr(sps, "write_report", lambda r: reports.extend(r))
    sps.main(["all"])
    assert done == ["SS-002"] and "kharab row" in reports[0]


def test_missing_voice_with_skip_missing_nahi_does_not_crash(tmp_path, monkeypatch):
    (tmp_path / "SS-001 Test" / "Part 1").mkdir(parents=True)
    monkeypatch.setattr(sps, "SERIES", str(tmp_path))
    monkeypatch.setenv("SPS_COMMON", str(tmp_path / "nahi_hai"))
    monkeypatch.setitem(sps.S, "skip_missing", "Nahi")
    X = {"Edit Timeline": (HDR, [("SS-001", 1, 1, 0, 2, "x", "S01")]),
         "Scripts": (["Case", "Part", "Voiceover", "Caption", "Title"], [("SS-001", 1, "कुछ", "kuch", "T")]),
         "Cover Design": ([], []), "Tracker": ([], [])}
    report = []
    assert sps.make_part(X, "SS-001", "1", report) is False
    assert any("voice VO_SS-001_P1" in r for r in report)


def test_mark_excel_only_saves_when_changed(tmp_path, monkeypatch):
    x = tmp_path / "s.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Story Status"
    ws.append(["Case", "Part", "Video bani?"])
    ws.append(["SS-001", 1, "Haan"])
    wb.save(x)
    monkeypatch.setattr(sps, "EXCEL", str(x))
    monkeypatch.setattr(sps, "HERE", str(tmp_path))
    monkeypatch.setitem(sps.S, "update_excel", "Haan")
    sps.mark_excel("SS-001", 1)
    assert not (tmp_path / "excel_backup").exists()      # pehle se Haan: na save, na backup
    sps.mark_excel("SS-002", 1)
    assert not (tmp_path / "excel_backup").exists()


def test_ffprobe_found_next_to_ffmpeg(tmp_path):
    (tmp_path / "ffmpeg").write_text("")
    (tmp_path / "ffprobe").write_text("")
    assert sps.find_ffprobe(str(tmp_path / "ffmpeg")) == str(tmp_path / "ffprobe")
