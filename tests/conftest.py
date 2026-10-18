# Test helpers: asli media cloud par nahi hai, isliye nakli (mock) PNG / awaaz yahan banti hai.
# Har test apne alag temp folder mein chalta hai -> laptop ki assets/voice/output kabhi nahi chhooti.
import os, subprocess, sys

import pytest
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
SAMPLE = os.path.join(ROOT, "samples", "09-010 Til Gud ki Dopahar")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"   # cloud (Linux) par ariblk.ttf nahi hota
if not os.path.exists(FONT):
    FONT = r"C:\Windows\Fonts\ariblk.ttf"                     # laptop

import make_reel as R          # noqa: E402
import voice_queue             # noqa: E402

FFMPEG = R.FFMPEG


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """ElevenLabs / internet ko kabhi call na ho (credits!)"""
    import urllib.request

    def blocked(*a, **k):
        raise AssertionError("test mein internet call nahi honi chahiye")
    monkeypatch.setattr(urllib.request, "urlopen", blocked)


@pytest.fixture
def box(tmp_path, monkeypatch):
    """make_reel ke saare folder temp mein + test font"""
    d = {k: tmp_path / k for k in ("assets", "voice", "music", "cases", "output", "sfx", "work")}
    for p in d.values():
        p.mkdir()
    for k in ("assets", "voice", "music", "cases", "output", "sfx"):
        monkeypatch.setattr(R, k.upper(), str(d[k]))
    monkeypatch.setattr(R, "BG_FILE", str(d["assets"] / "BG_MAIN.png"))
    monkeypatch.setattr(R, "FONT_FILE", FONT)
    monkeypatch.setattr(R, "COMMON_MUSIC", str(tmp_path / "Common" / "bg music.mp3"))
    monkeypatch.setattr(voice_queue, "WORK", str(d["work"]))
    R._img_cache.clear()
    R._text_cache.clear()
    R._bg_cache.clear()
    Image.new("RGBA", (540, 960), (250, 240, 220, 255)).save(d["assets"] / "BG_MAIN.png")
    d["root"] = tmp_path
    return d


# ---------- nakli images ----------
def character(path, w=300, h=600, gap=20, color=(200, 60, 60, 255)):
    """transparent background par ek aakriti, neeche thodi khaali jagah"""
    im = Image.new("RGBA", (w, h + gap), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((10, 0, w - 10, h), fill=color)
    im.save(path)


def white_bg(path, w=300, h=300):
    """safed dabbe wali image (bina transparency)"""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    ImageDraw.Draw(im).rectangle((60, 60, w - 60, h - 60), fill=(30, 30, 200, 255))
    im.save(path)


def bottom_prop(path, w=400, h=200):
    """neeche ke kinare se chipka prop (sofa jaisa)"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rectangle((40, 40, w - 40, h - 1), fill=(120, 80, 40, 255))
    im.save(path)


# ---------- nakli awaaz ----------
def tone(path, seconds=2.0, freq=440):
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i",
                    f"sine=frequency={freq}:duration={seconds}:sample_rate=44100", str(path)], check=True)


def silence(path, seconds=1.0):
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i",
                    "anullsrc=r=44100:cl=mono", "-t", str(seconds), str(path)], check=True)


def speech(path, pattern):
    """pattern = [(awaaz_sec, chup_sec), ...] -> bolne jaisi file (tone + chup)"""
    expr, t = [], 0.0
    for on, off in pattern:
        expr.append(f"between(t,{t},{t + on})")
        t += on + off
    cond = "+".join(expr)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i",
                    f"aevalsrc='if({cond},0.5*sin(2*PI*330*t),0)':s=44100:d={t}",
                    "-ac", "1", str(path)], check=True)


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write("asset_id,start,end,position,size,text,effect,sfx,color,focus\n")
        for r in rows:
            f.write(r + "\n")
