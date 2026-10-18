# YouTube screenshot ka auto check (OCR) – asli Telegram / internet nahi
import os
import shutil

import pytest

import yt_ocr
from test_comment_checker import bot, msg  # noqa: F401


def test_judge_text():
    assert yt_ocr.judge("Detective Shivam\n@theshivamiq · 2.1K subscribers\nSubscribed")[0]
    assert yt_ocr.judge("डिटेक्टिव शिवम\nसदस्यता ली गई")[0]
    # abhi subscribe NAHI kiya (button par sirf "Subscribe")
    ok, why = yt_ocr.judge("Detective Shivam @theshivamiq 2.1K subscribers Subscribe")
    assert not ok and "Subscribed" in why
    # kisi aur channel ka screenshot
    ok, why = yt_ocr.judge("Cooking with Riya\nSubscribed")
    assert not ok and "Shivam" in why


def _setup(bot, monkeypatch, tmp_path, result, img=b"photo-1"):
    def dl(file_id):
        p = tmp_path / ("dl_%s.jpg" % file_id)
        p.write_bytes(img)
        return str(p)
    monkeypatch.setattr(bot, "download_photo", dl)
    monkeypatch.setattr(bot.yt_ocr, "check", lambda path: result)
    monkeypatch.setattr(bot, "in_channel", lambda uid: True)
    return {"users": {"5": {"ig": "riya_1", "step": "tasks", "tg_ok": True}}, "admin": 1, "admin_pin": "1"}


def photo(uid, fid="F1"):
    return msg(uid, "", photo=[{"file_id": fid}])


def test_auto_pass_verifies_without_admin(bot, monkeypatch, tmp_path):
    st = _setup(bot, monkeypatch, tmp_path, (True, "Subscribed + Shivam dono dikhe"))
    bot.handle_message(st, photo(5))
    u = st["users"]["5"]
    assert u["yt_ok"] and u["yt_auto"] and u["done"]
    assert "riya_1" in open(bot.VERIFIED, encoding="utf-8").read()
    assert not any(m == "sendPhoto" for m, _ in bot.sent)         # admin ko photo nahi gayi
    assert not list(tmp_path.glob("dl_*.jpg"))                     # temp photo mit gayi


def test_fail_then_admin(bot, monkeypatch, tmp_path):
    st = _setup(bot, monkeypatch, tmp_path, (False, "'Subscribed' nahi dikha"))
    bot.handle_message(st, photo(5, "F1"))
    u = st["users"]["5"]
    assert not u.get("yt_ok") and u["yt_tries"] == 1 and not u["yt_wait"]
    assert not any(m == "sendPhoto" for m, _ in bot.sent)         # pehli baar follower ko hi bola
    bot.handle_message(st, photo(5, "F2"))
    assert u["yt_tries"] == 2 and u["yt_wait"]
    assert any(m == "sendPhoto" for m, _ in bot.sent)             # doosri baar admin ke paas


def test_no_tesseract_goes_to_admin(bot, monkeypatch, tmp_path):
    st = _setup(bot, monkeypatch, tmp_path, None)
    bot.handle_message(st, photo(5))
    assert any(m == "sendPhoto" for m, _ in bot.sent) and not st["users"]["5"].get("yt_ok")


def test_copied_screenshot_goes_to_admin(bot, monkeypatch, tmp_path):
    st = _setup(bot, monkeypatch, tmp_path, (True, "ok"), img=b"same-image")
    bot.handle_message(st, photo(5))
    assert st["users"]["5"]["yt_ok"]
    st["users"]["6"] = {"ig": "aman_2", "step": "tasks", "tg_ok": True}
    bot.sent.clear()
    bot.handle_message(st, photo(6))                                # wahi image dusre ne bheji
    assert not st["users"]["6"].get("yt_ok")
    assert any(m == "sendPhoto" for m, _ in bot.sent)


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract is machine par nahi hai")
def test_real_ocr_on_drawn_screenshot(tmp_path):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (900, 400), "white")
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
    except OSError:
        f = ImageFont.load_default()
    d.text((40, 60), "Detective Shivam", fill="black", font=f)
    d.text((40, 140), "@theshivamiq", fill="gray", font=f)
    d.rounded_rectangle((40, 240, 400, 320), 30, fill=(230, 230, 230))
    d.text((70, 252), "Subscribed", fill="black", font=f)
    p = tmp_path / "ss.png"
    im.save(p)
    assert yt_ocr.check(str(p))[0]
