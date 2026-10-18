import importlib
import json
import os
import subprocess
import sys
from unittest import mock

import pytest

import ig_api


@pytest.fixture
def bot(tmp_path, monkeypatch):
    """tg_bot ko nakli .env aur temp data folder ke saath load karo (asli Telegram nahi)."""
    env = tmp_path / ".env"
    env.write_text('IG_TOKEN=igtok\nTG_BOT_TOKEN="123:abc"\n', encoding="utf-8")
    monkeypatch.setattr(ig_api, "ENV", str(env))
    sys.modules.pop("tg_bot", None)
    tb = importlib.import_module("tg_bot")
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(tb, "DATA", str(data))
    monkeypatch.setattr(tb, "STATE", str(data / "bot_state.json"))
    monkeypatch.setattr(tb, "RANKS", str(data / "ranks.json"))
    monkeypatch.setattr(tb, "VERIFIED", str(tmp_path / "verified.txt"))
    sent = []
    monkeypatch.setattr(tb, "tg", lambda method, **p: sent.append((method, p)) or {"message_id": 1})
    tb._admin_fail.clear()
    tb.sent = sent
    return tb


def msg(uid, text, **extra):
    return {"chat": {"id": uid, "type": "private"}, "from": {"id": uid, "first_name": "A"}, "text": text, **extra}


def test_token_quotes_stripped(bot):
    assert bot.TOKEN == "123:abc"


def test_verified_user_text_does_not_change_username(bot):
    st = {"users": {"5": {"ig": "riya_1", "step": "tasks", "done": True, "ig_ok": False}}, "admin_pin": "111111"}
    bot.handle_message(st, msg(5, "thanks"))
    assert st["users"]["5"]["ig"] == "riya_1"
    # jo abhi verify ho raha hai wo naam theek kar sakta hai (purana behaviour)
    st["users"]["6"] = {"ig": "galat", "step": "tasks"}
    bot.handle_message(st, msg(6, "sahi_naam"))
    assert st["users"]["6"]["ig"] == "sahi_naam"


def test_admin_pin_bruteforce_blocked(bot):
    st = {"users": {}, "admin_pin": "123456"}
    for k in range(5):
        bot.handle_message(st, msg(9, "/admin %06d" % k))
    bot.handle_message(st, msg(9, "/admin 123456"))        # 5 galat ke baad sahi PIN bhi nahi chalega
    assert "admin" not in st
    bot.handle_message(st, msg(10, "/admin 123456"))
    assert st["admin"] == 10


def test_rank_text_escapes_html(bot):
    t = bot.rank_text("<b>x")
    assert "&lt;b&gt;x" in t and "<b>x" not in t


def test_send_shak_marks_only_delivered(bot, monkeypatch):
    with open(os.path.join(bot.DATA, "shak_pending.json"), "w") as f:
        json.dump([{"cid": "c1", "case": "01-001", "u": "a", "text": "x", "link": "", "answer": "A", "number": 1},
                   {"cid": "c2", "case": "01-001", "u": "b", "text": "y", "link": "", "answer": "A", "number": 1}], f)
    results = iter([{"ok": 1}, {"ok": 1}, None])          # header, c1 gaya, c2 fail
    monkeypatch.setattr(bot, "send", lambda *a, **k: next(results))
    st = {"users": {}, "admin": 1}
    bot.send_shak(st, 15)
    assert st["shak_sent"] == ["c1"]


def test_save_decision_keeps_corrupt_state_copy(bot):
    p = os.path.join(bot.DATA, "state.json")
    with open(p, "w") as f:
        f.write("{kharab")
    bot.save_decision("c1", "SAHI")
    assert json.load(open(p))["decisions"] == {"c1": "SAHI"}
    assert any(n.startswith("state.json.kharab-") for n in os.listdir(bot.DATA))


def test_checker_timeout_does_not_block_bot(bot, monkeypatch):
    def slow(*a, **k):
        raise subprocess.TimeoutExpired("checker", k.get("timeout"))
    monkeypatch.setattr(bot.subprocess, "run", slow)
    st = {"users": {}, "admin": 1}
    bot.maybe_run_checker(st, force=True)
    assert st["checker_day"]
    assert any("khatam nahi hua" in p.get("text", "") for m, p in bot.sent)


def test_checker_error_message_escaped(bot, monkeypatch):
    monkeypatch.setattr(bot.subprocess, "run", lambda *a, **k: mock.Mock(returncode=1, stdout="PROBLEM: <html> & x",
                                                                          stderr=""))
    st = {"users": {}, "admin": 1}
    bot.maybe_run_checker(st, force=True)
    assert any("&lt;html&gt; &amp; x" in p.get("text", "") for m, p in bot.sent)


def test_tg_retries_once_on_429(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("TG_BOT_TOKEN=1:x\n")
    monkeypatch.setattr(ig_api, "ENV", str(env))
    sys.modules.pop("tg_bot", None)
    tb = importlib.import_module("tg_bot")
    answers = iter([{"ok": False, "error_code": 429, "parameters": {"retry_after": 1}}, {"ok": True, "result": 7}])
    post = mock.Mock(side_effect=lambda *a, **k: mock.Mock(json=lambda: next(answers)))
    monkeypatch.setattr(tb.requests, "post", post)
    monkeypatch.setattr(tb.time, "sleep", lambda s: None)
    assert tb.tg("sendMessage", chat_id=1, text="hi") == 7 and post.call_count == 2


# ---------------------------------------------------------------- checker.py
@pytest.fixture
def chk(tmp_path, monkeypatch):
    import checker
    import answer_key
    data = tmp_path / "data"
    monkeypatch.setattr(checker, "HERE", str(tmp_path))
    monkeypatch.setattr(checker, "DATA", str(data))
    monkeypatch.setattr(checker, "COMMENTS_FILE", str(data / "comments.json"))
    monkeypatch.setattr(checker, "STATE_FILE", str(data / "state.json"))
    monkeypatch.setattr(answer_key, "KEY_FILE", str(tmp_path / "answer_key.xlsx"))
    monkeypatch.setattr(answer_key, "STORY_ROOT", str(tmp_path / "scripts"))
    return checker


def test_jload_corrupt_file_is_backed_up(chk, tmp_path):
    os.makedirs(chk.DATA)
    p = os.path.join(chk.DATA, "comments.json")
    open(p, "w").write("{adhoori")
    assert chk.jload(p, {}) == {}
    assert any(n.startswith("comments.json.kharab-") for n in os.listdir(chk.DATA))
    assert chk.jload(os.path.join(chk.DATA, "nahi.json"), []) == []


def _media(n):
    return [{"id": "m%d" % i, "caption": "Case %d-001" % i, "timestamp": "2026-10-1%dT03:00:00+0000" % i,
             "permalink": "https://www.instagram.com/reel/C%d/" % i, "comments_count": 1, "like_count": 1}
            for i in range(1, n + 1)]


def _comments(mid):
    return {mid + "_c": {"u": "riya", "uid": "u1", "t": "1", "ts": "2026-10-1%sT03:05:00+0000" % mid[1:], "p": ""}}


def run_checker(chk, monkeypatch, fetch):
    monkeypatch.setattr(chk.ig_api, "refresh_token", lambda: 60)
    monkeypatch.setattr(chk.ig_api, "get_all", lambda path, params=None, **k: _media(3))
    monkeypatch.setattr(chk, "fetch_comments", fetch)
    monkeypatch.setattr(chk, "fetch_insights", lambda mid: {})
    monkeypatch.setattr(chk.akey, "load", lambda: {"01-001": {"Sahi Answer": "Kallu", "Sahi Number": 1,
                                                              "Suspects (number naam)": "1 Kallu | 2 Pintu"}})
    monkeypatch.setattr(sys, "argv", ["checker.py"])
    return chk.main()


def test_one_reel_fail_does_not_stop_leaderboard(chk, monkeypatch):
    def fetch(mid):
        if mid == "m2":
            raise chk.ig_api.IGError("Instagram error (4): limit")
        return _comments(mid)
    assert run_checker(chk, monkeypatch, fetch) == 0
    store = json.load(open(chk.COMMENTS_FILE))
    assert set(store["m1"]["comments"]) == {"m1_c"} and store["m2"]["comments"] == {}
    ranks = json.load(open(os.path.join(chk.DATA, "ranks.json")))
    # ranks.json ka format wahi (bot /rank isi par chalta hai)
    assert set(ranks) == {"updated", "total_cases", "users"}
    assert set(ranks["users"]["riya"]) == {"name", "sahi", "week", "live", "jawab", "pos", "rank", "would", "streak",
                                           "best_streak", "pts", "pts_week", "pts_live", "day_streak",
                                           "best_day_streak"}
    st = json.load(open(chk.STATE_FILE))
    assert {"decisions", "memory", "rank_history"} <= set(st)


def test_all_reels_fail_reports_problem(chk, monkeypatch):
    def fetch(mid):
        raise chk.ig_api.IGError("Instagram error (190): token expired")
    with pytest.raises(chk.ig_api.IGError):
        run_checker(chk, monkeypatch, fetch)


def test_ig_api_never_puts_token_in_error(monkeypatch):
    import requests

    def bad(url, params=None, timeout=None):
        raise requests.ConnectionError("https://graph.instagram.com/?access_token=SECRET123")
    monkeypatch.setattr(ig_api.requests, "get", bad)
    monkeypatch.setattr(ig_api.time, "sleep", lambda s: None)
    with pytest.raises(ig_api.IGError) as e:
        ig_api._get("https://graph.instagram.com/me", {}, "SECRET123")
    assert "SECRET123" not in str(e.value)


def test_ig_rate_limit_retries(monkeypatch):
    calls = []

    def fake(url, params=None, timeout=None):
        calls.append(1)
        if len(calls) == 1:
            return mock.Mock(status_code=400, json=lambda: {"error": {"code": 4, "message": "limit"}})
        return mock.Mock(status_code=200, json=lambda: {"data": [1]})
    monkeypatch.setattr(ig_api.requests, "get", fake)
    monkeypatch.setattr(ig_api.time, "sleep", lambda s: None)
    assert ig_api._get("u", {}, "t") == {"data": [1]}


def test_judge_basic():
    import checker
    c = checker.Case("01-001", {"Sahi Answer": "Kallu", "Sahi Number": 3,
                                "Suspects (number naam)": "1 Ramesh | 2 Pintu | 3 Kallu"})
    assert c.judge("Kallu")[0] == checker.SAHI
    assert c.judge("3")[0] == checker.SAHI
    assert c.judge("Pintu")[0] == checker.GALAT
    assert c.judge("nice reel")[0] == checker.NONE
