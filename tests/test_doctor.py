import os

import doctor

SECRET = "sk_" + "a1" * 25


def make_base(tmp_path, music=True, sfx=None, key=SECRET):
    base, story = tmp_path / "theshivamiq code", tmp_path / "reels story"
    for d in doctor.FOLDERS:
        (base / d).mkdir(parents=True)
    for a in doctor.ASSETS_NEEDED:
        (base / "assets" / a).write_bytes(b"x")
    for s in (doctor.SFX_NEEDED if sfx is None else sfx):
        (base / "sfx" / (s + ".wav")).write_bytes(b"x")
    if music:
        (base / "music" / "bg music.mp3").write_bytes(b"x")
    (story / "Common").mkdir(parents=True)
    for f in doctor.COMMON_FILES:
        (story / "Common" / f).write_bytes(b"common")
    (story / "Category 9" / "Story 10").mkdir(parents=True)
    if key is not None:
        (base / "elevenlabs_key.txt").write_text(key, encoding="utf-8")
    return str(base), str(story)


def by_section(r, sec):
    return [i for i in r.items if i[1] == sec]


def test_all_good_has_no_fail_in_our_sections(tmp_path):
    base, story = make_base(tmp_path)
    r = doctor.check_all(base, story, windows=False)
    for sec in ("Folders", "Music", "SFX", "Common", "Assets", "ElevenLabs"):
        assert all(i[0] == doctor.OK for i in by_section(r, sec)), by_section(r, sec)


def test_missing_music_suggests_fix_and_fix_copies(tmp_path):
    base, story = make_base(tmp_path, music=False)
    r = doctor.check_all(base, story, windows=False)
    music = by_section(r, "Music")[0]
    assert music[0] == doctor.FAIL and "--fix" in music[3]
    assert not os.path.exists(os.path.join(base, "music", "bg music.mp3"))   # bina --fix kuch nahi badla
    r = doctor.check_all(base, story, fix=True, windows=False)
    assert by_section(r, "Music")[0][0] == doctor.OK
    assert open(os.path.join(base, "music", "bg music.mp3"), "rb").read() == b"common"


def test_missing_sfx_listed(tmp_path):
    base, story = make_base(tmp_path, sfx=["pop", "boom"])
    r = doctor.check_all(base, story, windows=False)
    msg = by_section(r, "SFX")[0]
    assert msg[0] == doctor.FAIL and "tick_fast" in msg[2] and "whoosh" in msg[2]


def test_sfx_used_in_csv_but_missing_is_warning(tmp_path):
    base, story = make_base(tmp_path)
    with open(os.path.join(base, "cases", "09-010 Test.csv"), "w", encoding="utf-8") as f:
        f.write("asset_id,start,end,position,size,text,effect,sfx,color,focus\n"
                "S01,0,1,center,50,\"hi, there\",,thunder,,\n")
    r = doctor.check_all(base, story, windows=False)
    warn = [i for i in by_section(r, "SFX") if i[0] == doctor.WARN]
    assert warn and "thunder (09-010 Test.csv)" in warn[0][2]


def test_key_missing_empty_and_never_printed(tmp_path, capsys):
    base, story = make_base(tmp_path)
    r = doctor.check_all(base, story, windows=False)
    doctor.print_report(r)
    assert SECRET not in capsys.readouterr().out
    os.remove(os.path.join(base, "elevenlabs_key.txt"))
    assert by_section(doctor.check_all(base, story, windows=False), "ElevenLabs")[0][0] == doctor.FAIL
    open(os.path.join(base, "elevenlabs_key.txt"), "w").write("  \n")
    assert "khaali" in by_section(doctor.check_all(base, story, windows=False), "ElevenLabs")[0][2]


def test_missing_common_cta(tmp_path):
    base, story = make_base(tmp_path)
    os.remove(os.path.join(story, "Common", "CTA_HI.mp3"))
    bad = [i for i in by_section(doctor.check_all(base, story, windows=False), "Common") if i[0] != doctor.OK]
    assert bad[0][0] == doctor.FAIL and "MAT" in bad[0][3]
