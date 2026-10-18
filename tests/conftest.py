"""Tests: koi asli API (Instagram / Telegram / YouTube / ElevenLabs) call nahi hoti - sab mock."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub in ("sab_pe_shak", "yt_scheduler", "comment_checker"):
    p = os.path.join(ROOT, sub)
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Galti se bhi internet par request na jaaye."""
    import socket

    def blocked(*a, **k):
        raise RuntimeError("test mein network band hai")
    monkeypatch.setattr(socket.socket, "connect", blocked)
