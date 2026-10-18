# Part 1 / Part 2 (jawab wali reel) + naye case ID – 19 Oct 2026 se points ke niyam
import json
import os
import sys

from test_comment_checker import chk  # noqa: F401  (same temp folders wala fixture)


def T(s):
    import checker
    return checker.ts(s)


def test_case_of_purane_aur_naye_id():
    import checker
    assert checker.case_of("Case 22-001 | Killer kaun?") == "22-001"
    assert checker.case_of("Case #3-7") == "03-007"
    after = T("2026-10-20T03:00:00+0000")
    before = T("2026-10-10T03:00:00+0000")
    assert checker.case_of("Case NF-001 naya case", after) == "NF-001"
    assert checker.case_of("case s2p-4", after) == "S2P-004"
    # purani reels ki ginti waisi hi rahe (SS-003 jaise pehle gine nahi jaate the)
    assert checker.case_of("Case SS-003", before) is None
    assert checker.case_of("Koi case nahi") is None


def test_part2_sirf_case_ke_saath():
    import checker
    after = T("2026-10-20T03:00:00+0000")
    assert checker.is_part2("Case NF-001 Part 2 – jawab yahan", after)
    assert checker.is_part2("CASE 22-001 | PART-2", after)
    assert checker.is_part2("Case 22-001 (Part II)", after)
    assert checker.is_part2("Case 22-001 भाग 2", after)
    # Part 1 ke caption mein "Part 2 kal" likha ho to wo Part 2 NAHI
    assert not checker.is_part2("Case NF-001 Part 1 – Part 2 kal aayega!", after)
    assert not checker.is_part2("Case NF-001 Killer kaun? Part 2 kal", after)
    # 19 Oct se pehle ki reels par naya niyam nahi
    assert not checker.is_part2("Case 22-001 Part 2", T("2026-10-10T03:00:00+0000"))


def test_part2_ke_baad_ginti_band(chk, monkeypatch):  # noqa: F811
    media = [
        {"id": "p1", "caption": "Case NF-001 Part 1 – Killer kaun? Part 2 kal",
         "timestamp": "2026-10-20T02:30:00+0000", "permalink": "https://www.instagram.com/reel/A1/",
         "comments_count": 2, "like_count": 1},
        {"id": "p2", "caption": "Case NF-001 Part 2 – jawab",
         "timestamp": "2026-10-20T12:30:00+0000", "permalink": "https://www.instagram.com/reel/A2/",
         "comments_count": 1, "like_count": 1},
    ]
    asked = []

    def fetch(mid):
        asked.append(mid)
        return {
            # Part 2 aane se PEHLE sahi -> ginega
            "c1": {"u": "riya", "uid": "u1", "t": "1 Kallu", "ts": "2026-10-20T02:40:00+0000", "p": ""},
            # Part 2 (jawab) aane ke BAAD Part 1 par -> nahi ginega
            "c2": {"u": "aman", "uid": "u2", "t": "1 Kallu", "ts": "2026-10-20T13:00:00+0000", "p": ""},
        }
    monkeypatch.setattr(chk.ig_api, "refresh_token", lambda: 60)
    monkeypatch.setattr(chk.ig_api, "get_all", lambda path, params=None, **k: media)
    monkeypatch.setattr(chk, "fetch_comments", fetch)
    monkeypatch.setattr(chk, "fetch_insights", lambda mid: {})
    monkeypatch.setattr(chk.akey, "load", lambda: {"NF-001": {"Sahi Answer": "Kallu", "Sahi Number": 1,
                                                              "Suspects (number naam)": "1 Kallu | 2 Pintu"}})
    monkeypatch.setattr(sys, "argv", ["checker.py"])
    assert chk.main() == 0

    assert asked == ["p1"]                       # Part 2 ke comment laaye hi nahi
    store = json.load(open(chk.COMMENTS_FILE))
    assert store["p2"]["part2"] is True and store["p1"]["part2"] is False
    users = json.load(open(os.path.join(chk.DATA, "ranks.json")))["users"]
    assert users["riya"]["sahi"] == 1
    assert "aman" not in users or users["aman"]["sahi"] == 0
