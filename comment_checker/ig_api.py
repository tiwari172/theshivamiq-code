"""Instagram API (Instagram Login) helper. Token .env se padhta hai, kabhi print nahi karta."""
import os, sys, time, json
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.join(HERE, ".env")
BASE = "https://graph.instagram.com/v23.0"


class IGError(Exception):
    pass


def load_token():
    if not os.path.exists(ENV):
        raise IGError(".env file nahi mili: " + ENV)
    with open(ENV, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line.startswith("IG_TOKEN="):
                tok = line.split("=", 1)[1].strip().strip('"').strip("'")
                if tok:
                    return tok
    raise IGError(".env mein IG_TOKEN khaali hai")


def save_token(tok):
    lines = []
    if os.path.exists(ENV):
        with open(ENV, encoding="utf-8-sig") as f:
            lines = [l.rstrip("\r\n") for l in f if not l.startswith("IG_TOKEN=")]
    lines.insert(0, "IG_TOKEN=" + tok)
    tmp = ENV + ".new"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    os.replace(tmp, ENV)


def _get(url, params, token):
    params = dict(params or {})
    params["access_token"] = token
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, timeout=30)
        except requests.RequestException as e:
            # error message mein URL (token ke saath) ho sakta hai, isliye sirf type dikhao
            if attempt == 3:
                raise IGError("Internet/connection problem: " + type(e).__name__)
            time.sleep(3 * (attempt + 1))
            continue
        try:
            data = r.json()
        except ValueError:
            data = {}
        if r.status_code == 200 and "error" not in data:
            return data
        err = data.get("error", {}) if isinstance(data, dict) else {}
        msg = err.get("message", "HTTP %s" % r.status_code)
        code = err.get("code")
        if code in (4, 17, 32, 613) and attempt < 3:  # rate limit
            time.sleep(60)
            continue
        if r.status_code >= 500 and attempt < 3:
            time.sleep(5)
            continue
        raise IGError("Instagram error (%s): %s" % (code, msg))
    raise IGError("Instagram se jawab nahi aaya")


def get(path, params=None, token=None):
    return _get(BASE + "/" + path.lstrip("/"), params, token or load_token())


def get_all(path, params=None, token=None, limit_pages=200):
    """Pagination ke saath saare items."""
    token = token or load_token()
    data = _get(BASE + "/" + path.lstrip("/"), params, token)
    items = list(data.get("data", []))
    pages = 1
    nxt = data.get("paging", {}).get("next")
    while nxt and pages < limit_pages:
        # next URL mein token pehle se hota hai; hum params se dobara dete hain
        base, _, q = nxt.partition("?")
        qp = dict(p.split("=", 1) for p in q.split("&") if "=" in p)
        qp.pop("access_token", None)
        from urllib.parse import unquote
        qp = {k: unquote(v) for k, v in qp.items()}
        data = _get(base, qp, token)
        items.extend(data.get("data", []))
        nxt = data.get("paging", {}).get("next")
        pages += 1
    return items


def refresh_token():
    """Long-lived token ko 60 din aage badhata hai aur .env mein save karta hai."""
    tok = load_token()
    data = _get("https://graph.instagram.com/refresh_access_token",
                {"grant_type": "ig_refresh_token"}, tok)
    new = data.get("access_token")
    if new:
        save_token(new)
        return int(data.get("expires_in", 0)) // 86400
    return None
