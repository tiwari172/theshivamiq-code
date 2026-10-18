import os

import make_reel as R
import check_reel as C
from conftest import SAMPLE, bottom_prop, character, white_bg, write_csv


def test_csv_nahi_mili(box):
    p, w = C.check("nahi hai")
    assert p and "CSV nahi mili" in p[0]


def test_khaali_csv(box):
    write_csv(os.path.join(R.CASES, "k.csv"), ["STYLE,0,1,,,pop,,,,"])
    p, w = C.check("k")
    assert p and "koi row nahi" in p[0]


def test_gayab_image_problem_banta_hai_crash_nahi(box):
    # pehle: "image assets mein nahi hai" ke baad step 3 mein Image.open(None) crash
    character(os.path.join(R.ASSETS, "S01.png"))
    write_csv(os.path.join(R.CASES, "g.csv"), [
        "S01,0,2,center,50,Hello,,,,",
        "GAYAB,2,4,center,50,Duniya,,,,",
    ])
    p, w = C.check("g")
    assert any("'GAYAB.png' assets mein nahi hai" in x for x in p)


def test_problem_output_format_wahi_hai(box, capsys):
    write_csv(os.path.join(R.CASES, "g.csv"), ["GAYAB,0,2,center,50,Hi,,,,"])
    assert C.report("g") is False
    out = capsys.readouterr().out
    assert "[g] 1 PROBLEM (render nahi hoga, CSV theek karo):" in out
    assert "   - line 2: image 'GAYAB.png' assets mein nahi hai" in out


def test_s_wale_prop_bhi_check(box):
    # pehle har "S" se shuru naam (SOFA, SAFE ...) ko Shivam maan kar chhod deta tha
    p = os.path.join(R.ASSETS, "SOFA.png")
    bottom_prop(p)
    assert C.cut_bottom(p, "SOFA") is True
    assert C.cut_bottom(p, "P_SOFA") is True
    assert C.cut_bottom(p, "S01") is False
    assert C.cut_bottom(p, "S2_17") is False
    assert C.cut_bottom(p, "SOFA_UP") is False


def test_safed_dabba_warning(box):
    white_bg(os.path.join(R.ASSETS, "P_GHADI.png"))
    character(os.path.join(R.ASSETS, "S01.png"))
    write_csv(os.path.join(R.CASES, "w.csv"), [
        "S01,0,2,center,50,Hi,,,,",
        "P_GHADI,2,4,center,30,Ghadi,,,,",
    ])
    p, w = C.check("w")
    assert any("P_GHADI_CUT" in x for x in w)


def test_lamba_text_problem(box):
    character(os.path.join(R.ASSETS, "S01.png"))
    write_csv(os.path.join(R.CASES, "l.csv"), [
        "S01,0,3,center,50,ek do teen char paanch chhe saat aath nau das gyarah barah terah chaudah pandrah solah satrah atharah unnees bees,,,,",
    ])
    p, w = C.check("l")
    assert any("max 3" in x for x in p)


def test_sirf_text_khaali_screen(box):
    character(os.path.join(R.ASSETS, "S01.png"))
    write_csv(os.path.join(R.CASES, "t.csv"), [
        "S01,0,2,center,50,,,,,",
        ",2,4,,60,Sirf text,,,,",
    ])
    p, w = C.check("t")
    assert any("sirf text" in x for x in p)


def test_sample_reel_ki_csv_chalti_hai(box):
    # samples\09-010 ki asli CSV, nakli images ke saath: bina crash ke poora check
    import shutil
    for a in ("C002_ARYAN", "C003_BHATIJA", "C004_AMIT", "C005_VICKY", "S04", "S06", "S16"):
        character(os.path.join(R.ASSETS, a + ".png"))
    character(os.path.join(R.ASSETS, "P_PATANG.png"), 300, 300)
    character(os.path.join(R.ASSETS, "C910_OPTIONS.png"), 1000, 400)
    shutil.copy(os.path.join(SAMPLE, "timing.csv"), os.path.join(R.CASES, "09-010 Til Gud ki Dopahar.csv"))
    p, w = C.check("09-010 Til Gud ki Dopahar")
    assert isinstance(p, list) and isinstance(w, list)
