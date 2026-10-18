# answers_extra.txt (Sab Pe Shak jaise case, bina Excel) + "number nahi"
import answer_key
import checker


def test_extra_file_and_no_numbers(tmp_path, monkeypatch):
    f = tmp_path / "answers_extra.txt"
    f.write_text("# note\nSS-003 | Neha | Ramu, Riya, Rohit, Kunal, Bhola, Neha | number nahi\n"
                 "XX-001 | Pintu | Kallu, Pintu\nkhaali line |\n", encoding="utf-8")
    monkeypatch.setattr(answer_key, "EXTRA_FILE", str(f))
    monkeypatch.setattr(answer_key, "KEY_FILE", str(tmp_path / "nahi.xlsx"))
    rows = answer_key.load()
    assert set(rows) == {"SS-003", "XX-001"}
    ss = checker.Case("SS-003", rows["SS-003"])
    assert ss.judge("Neha")[0] == checker.SAHI
    assert ss.judge("नेहा")[0] == checker.SAHI
    assert ss.judge("Kunal")[0] == checker.GALAT
    assert ss.judge("6")[0] == checker.NONE          # screen par number nahi the -> "6" answer nahi
    xx = checker.Case("XX-001", rows["XX-001"])
    assert xx.judge("2")[0] == checker.SAHI          # "number nahi" na likha ho to number chalte hain


def test_ss_answer_from_part2_caption(tmp_path):
    d = tmp_path / "SS-009 Test"
    (d / "Part 1").mkdir(parents=True)
    (d / "Part 2").mkdir()
    (d / "Part 1" / "CAPTION_SS-009_P1.txt").write_text(
        'Dr. Amit bola... "case khatam!"\nRamu bola... "Main gate par tha."\nBhai Rohit bola... "Main gym mein tha."\n',
        encoding="utf-8")
    (d / "Part 2" / "CAPTION_SS-009_P2.txt").write_text("Detective Shivam ne chor pakad liya... bhai Rohit!\n",
                                                         encoding="utf-8")
    ans, sus = answer_key.ss_answer(str(d))
    assert ans == "Rohit"
    assert any("Rohit" in s for s in sus) and not any(s.lower().startswith("dr") for s in sus)
