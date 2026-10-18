import os, subprocess

import pytest

import code_sync as CS


def g(cwd, *a):
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True).stdout


@pytest.fixture
def repos(tmp_path, monkeypatch):
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"),
                 ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@t")):
        monkeypatch.setenv(k, v)
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    laptop = tmp_path / "theshivamiq code"
    subprocess.run(["git", "clone", "-q", str(remote), str(laptop)], check=True)
    (laptop / ".gitignore").write_text("elevenlabs_key.txt\n.env\noutput/\n")
    (laptop / "make_reel.py").write_text("print('v1')\n")
    g(laptop, "checkout", "-q", "-b", "main")
    g(laptop, "add", "-A")
    g(laptop, "commit", "-q", "-m", "init")
    g(laptop, "push", "-q", "-u", "origin", "main")
    cloud = tmp_path / "cloud"
    subprocess.run(["git", "clone", "-q", str(remote), str(cloud)], check=True)
    return laptop, cloud, remote


def run(laptop, **kw):
    log = []
    res = CS.sync(str(laptop), message=kw.pop("message", "test"), out=log.append, **kw)
    return res, "\n".join(str(x) for x in log)


def test_normal_sync_commits_pulls_and_pushes(repos):
    laptop, cloud, remote = repos
    (cloud / "naya_cloud.py").write_text("x = 1\n")
    g(cloud, "add", "-A"); g(cloud, "commit", "-q", "-m", "cloud kaam"); g(cloud, "push", "-q")
    (laptop / "make_reel.py").write_text("print('v2')\n")
    (laptop / "elevenlabs_key.txt").write_text("sk_" + "ab" * 25)      # ignored -> theek
    res, log = run(laptop)
    assert res == "synced" and "SYNC POORA" in log
    assert (laptop / "naya_cloud.py").exists()
    files = g(remote, "ls-tree", "-r", "--name-only", "main")
    assert "make_reel.py" in files and "elevenlabs_key.txt" not in files
    assert "v2" in g(remote, "show", "main:make_reel.py")


def test_secret_file_not_ignored_stops(repos):
    laptop, _, remote = repos
    (laptop / ".gitignore").write_text("output/\n")                     # kisi ne ignore hata diya
    (laptop / "elevenlabs_key.txt").write_text("abc")
    with pytest.raises(CS.Stop) as e:
        run(laptop)
    assert "elevenlabs_key.txt" in str(e.value) and "abc" not in str(e.value)
    assert g(laptop, "log", "--oneline").count("\n") == 1                # koi commit nahi


def test_secret_inside_code_stops_without_printing_it(repos):
    laptop, _, _ = repos
    key = "sk_" + "0f" * 24
    (laptop / "helper.py").write_text(f"x = 1\nKEY = '{key}'\n")
    with pytest.raises(CS.Stop) as e:
        run(laptop)
    assert "helper.py" in str(e.value) and "line 2" in str(e.value) and key not in str(e.value)


def test_env_and_big_file_stop(repos):
    laptop, _, _ = repos
    (laptop / ".gitignore").write_text("")
    (laptop / "sub").mkdir()
    (laptop / "sub" / ".env").write_text("A=1")
    with pytest.raises(CS.Stop):
        run(laptop)
    os.remove(laptop / "sub" / ".env")
    big = laptop / "reel.bin"
    with open(big, "wb") as f:
        f.seek(CS.MAX_MB * 1024 * 1024 + 10); f.write(b"\0")
    with pytest.raises(CS.Stop) as e:
        run(laptop)
    assert "reel.bin" in str(e.value)


def test_conflict_stops_and_aborts(repos):
    laptop, cloud, _ = repos
    (cloud / "make_reel.py").write_text("print('cloud')\n")
    g(cloud, "commit", "-qam", "cloud"); g(cloud, "push", "-q")
    (laptop / "make_reel.py").write_text("print('laptop')\n")
    with pytest.raises(CS.Stop) as e:
        run(laptop)
    assert "CONFLICT" in str(e.value) and "make_reel.py" in str(e.value)
    assert not (laptop / ".git" / "MERGE_HEAD").exists()               # merge cancel ho gaya
    assert (laptop / "make_reel.py").read_text() == "print('laptop')\n"  # laptop ka kaam safe
    assert g(laptop, "status", "--porcelain") == ""


def test_dry_run_changes_nothing(repos):
    laptop, _, remote = repos
    (laptop / "naya.py").write_text("y = 2\n")
    res, log = run(laptop, dry_run=True)
    assert res == "dry-run" and "naya.py" in log
    assert "?? naya.py" in g(laptop, "status", "--porcelain")


def test_lists_unmerged_cloud_branches(repos):
    laptop, cloud, _ = repos
    g(cloud, "checkout", "-q", "-b", "claude/naya-kaam")
    (cloud / "tool.py").write_text("z = 3\n")
    g(cloud, "add", "-A"); g(cloud, "commit", "-q", "-m", "naya tool"); g(cloud, "push", "-q", "-u", "origin", "claude/naya-kaam")
    res, log = run(laptop)
    assert "origin/claude/naya-kaam" in log and "naya tool" in log
