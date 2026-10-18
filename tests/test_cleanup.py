import os, time

import cleanup as C

OLD = time.time() - 10 * 86400


def touch(p, old=True):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(b"x" * 100)
    if old:
        os.utime(p, (OLD, OLD))
    return p


def setup(tmp_path):
    base, story = str(tmp_path / "theshivamiq code"), str(tmp_path / "reels story")
    f = {
        "check": touch(os.path.join(base, "output", "09-010 Til Gud - CHECK.png")),
        "sheet": touch(os.path.join(base, "output", "Story 10 0910 - IMAGES.png")),
        "mp4": touch(os.path.join(base, "output", "09-010 Til Gud.mp4")),
        "cover": touch(os.path.join(base, "output", "09-010 Til Gud - COVER.png")),
        "newcheck": touch(os.path.join(base, "output", "Naya - CHECK.png"), old=False),
        "tmp": touch(os.path.join(base, "work", "voice_slot1", "tight_vo.m4a")),
        "lock": touch(os.path.join(base, "work", "voice_slot1.lock")),
        "voice": touch(os.path.join(base, "voice", "09-010 Til Gud.m4a")),
        "story": touch(os.path.join(story, "Category 9", "Story 10", "x - CHECK.png")),
    }
    return base, story, f


def test_lists_only_safe_old_junk(tmp_path):
    base, story, f = setup(tmp_path)
    found = {p for p, *_ in C.find_junk(base, days=3, story_root=story)}
    assert found == {f["check"], f["sheet"], f["tmp"]}


def test_days_zero_includes_new(tmp_path):
    base, story, f = setup(tmp_path)
    found = {p for p, *_ in C.find_junk(base, days=0, story_root=story)}
    assert f["newcheck"] in found and f["lock"] not in found


def test_is_safe_blocks_voice_story_lock(tmp_path):
    base, story, f = setup(tmp_path)
    for k in ("voice", "story", "lock"):
        assert not C.is_safe(f[k], base, story)
    assert C.is_safe(f["check"], base, story)


def test_delete_uses_recycler_and_never_touches_unsafe(tmp_path):
    base, story, f = setup(tmp_path)
    binned = []

    def fake_recycle(p):
        binned.append(p)
        os.remove(p)
        return True

    items = C.find_junk(base, days=3, story_root=story)
    items.append((f["voice"], "x", 1, OLD))            # koi galti se voice daal de, tab bhi nahi hatna chahiye
    ok, bad = C.send_to_recycle(items, base, story, recycler=fake_recycle)
    assert ok == 3 and bad == 1
    assert f["voice"] not in binned and os.path.exists(f["voice"]) and os.path.exists(f["mp4"])


def test_no_recycle_bin_means_no_delete(tmp_path, monkeypatch):
    base, story, f = setup(tmp_path)
    monkeypatch.setattr(C, "default_recycler", lambda: None)
    try:
        C.send_to_recycle(C.find_junk(base, days=3, story_root=story), base, story)
        assert False, "RuntimeError aana chahiye tha"
    except RuntimeError:
        pass
    assert os.path.exists(f["check"])
