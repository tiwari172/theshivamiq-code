import os, shutil

import reel_status as RS

SAMPLE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "samples", "09-010 Til Gud ki Dopahar")


def snapshot(root):
    out = []
    for r, ds, fs in os.walk(root):
        for f in fs:
            p = os.path.join(r, f)
            out.append((p, os.path.getsize(p), os.path.getmtime(p)))
    return sorted(out)


def setup(tmp_path):
    base, root = tmp_path / "theshivamiq code", tmp_path / "reels story"
    for d in ("voice", "cases", "output"):
        (base / d).mkdir(parents=True)
    # 1) puri reel (layout: reels story\category\Category 9\Story 10)
    done = root / "category" / "Category 9" / "Story 10"
    done.mkdir(parents=True)
    shutil.copy(os.path.join(SAMPLE, "SCRIPT_09-010.txt"), done)
    shutil.copy(os.path.join(SAMPLE, "timing.csv"), done)
    (done / "VO_MAIN.mp3").write_bytes(b"x")
    (done / "09-010 Til Gud ki Dopahar.mp4").write_bytes(b"x")
    (done / "09-010 Til Gud ki Dopahar - COVER.png").write_bytes(b"x")
    (base / "voice" / "09-010 Til Gud ki Dopahar.m4a").write_bytes(b"x")
    (base / "cases" / "09-010 Til Gud ki Dopahar.csv").write_bytes(b"x")
    # 2) voice + csv bane, render baaki (purana layout: reels story\Category 9\Story 11)
    mid = root / "Category 9" / "Story 11"
    mid.mkdir(parents=True)
    (mid / "SCRIPT_09-011.txt").write_text(
        "STORY 11 – Case 09-011: Diwali ki Raat   (Category 9: 09 – Tyohaar)\n", encoding="utf-8")
    (mid / "VO_MAIN.mp3").write_bytes(b"x")
    (base / "voice" / "09-011 Diwali ki Raat.m4a").write_bytes(b"x")
    (base / "cases" / "09-011 Diwali ki Raat.csv").write_bytes(b"x")
    # 3) sirf script, Devanagari wala naam
    new = root / "category" / "Category 10" / "Story 02"
    new.mkdir(parents=True)
    (new / "SCRIPT_10-002.txt").write_text(
        "STORY 02 – Case 10-002: सुबह की चोरी\n", encoding="utf-8")
    # 4) MP4 render ho gaya par output\ mein hi pada hai
    ren = root / "category" / "Category 10" / "Story 03"
    ren.mkdir(parents=True)
    (ren / "SCRIPT_10-003.txt").write_text("STORY 03 – Case 10-003: Seat\n", encoding="utf-8")
    for d, ext in (("voice", ".m4a"), ("cases", ".csv"), ("output", ".mp4")):
        (base / d / ("10-003 Seat" + ext)).write_bytes(b"x")
    # Common folder story nahi hai
    (root / "Common").mkdir()
    return str(base), str(root)


def test_scan_finds_both_layouts_and_status(tmp_path):
    base, root = setup(tmp_path)
    rows = RS.scan_all(root, base)
    assert [(r["category"], r["story"]) for r in rows] == [(9, 10), (9, 11), (10, 2), (10, 3)]
    a, b, c, d = rows
    assert a["done"] and a["name"] == "09-010 Til Gud ki Dopahar" and all(a["have"].values())
    assert b["name"] == "09-011 Diwali ki Raat" and b["have"]["Voice"] and b["have"]["CSV"]
    assert not b["have"]["MP4"] and "Render" in b["next"]
    assert c["name"] == "10-002 सुबह की चोरी" and "Voice banao" in c["next"]
    assert "copy" in d["next"] and "output" in d["next"]


def test_category_filter(tmp_path):
    base, root = setup(tmp_path)
    assert {r["story"] for r in RS.scan_all(root, base, category=10)} == {2, 3}


def test_read_only_story_folder_and_reports(tmp_path, capsys):
    base, root = setup(tmp_path)
    before = snapshot(root)
    rows = RS.scan_all(root, base)
    RS.print_table(rows)
    h, c = RS.write_reports(rows, os.path.join(base, "output"))
    assert snapshot(root) == before                     # story folder mein kuch nahi likha
    out = capsys.readouterr().out
    assert "Ye reels baaki hain" in out and "1 puri, 3 baaki" in out
    page = open(h, encoding="utf-8").read()
    assert "09-010 Til Gud ki Dopahar" in page and "सुबह की चोरी" in page
    assert open(c, encoding="utf-8-sig").read().count("\n") == 5


def test_only_pending(tmp_path, capsys):
    base, root = setup(tmp_path)
    RS.print_table(RS.scan_all(root, base), only_pending=True)
    table = capsys.readouterr().out.split("Kul")[0]
    assert "Til Gud" not in table and "Diwali" in table


def test_id_prefix_match_does_not_overmatch(tmp_path):
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "09-0101 Other.csv").write_bytes(b"x")
    assert RS.match_file(str(tmp_path / "x"), "09-010 Nahi", "09-010", (".csv",)) is None
    (tmp_path / "x" / "09-010 Purana Naam v2.csv").write_bytes(b"x")
    assert RS.match_file(str(tmp_path / "x"), "09-010 Nahi", "09-010", (".csv",)).endswith("v2.csv")
