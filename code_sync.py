# theshivamiq – CODE SYNC (laptop <-> GitHub)
#
# Ek baar mein:  1) laptop par kya badla wo dikhata hai
#                2) SECRET CHECK: key / .env / token / badi media file galti se jaa rahi ho to RUK jaata hai
#                3) commit (message poochta hai, Enter = date wala message)
#                4) GitHub se cloud ka kaam pull (merge, rebase nahi)  -> conflict ho to merge cancel karke rukta hai
#                5) push
#                6) cloud ki jo branches abhi merge nahi hui unki list (sirf dikhata hai)
#
#   py code_sync.py               poora sync
#   py code_sync.py --dry-run     sirf dikhao + secret check, kuch commit/push nahi
#   (ya double-click: CODE SYNC.bat)

import argparse, fnmatch, os, re, shutil, subprocess, sys
from datetime import datetime

import tools_common as T

# file ke naam jo kabhi GitHub par nahi jaane chahiye
SECRET_NAMES = [".env", "*.env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*", "*secret*",
                "*credential*", "token*.json", "*key*.txt", "elevenlabs_*.txt", "*.kdbx"]
# file ke andar ye dikhe to secret hai (match print NAHI hota, sirf file + line)
SECRET_PATTERNS = [
    ("ElevenLabs key", r"\bsk_[0-9a-f]{40,}\b"),
    ("OpenAI/Anthropic key", r"\bsk-(?:ant-)?[A-Za-z0-9_\-]{20,}"),
    ("Google API key", r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    ("Private key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    ("Slack token", r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"),
    ("Telegram bot token", r"\b\d{8,10}:AA[A-Za-z0-9_\-]{33}\b"),
    ("Facebook/Instagram token", r"\bEAA[A-Za-z0-9]{60,}"),
]
MAX_MB = 50                 # isse badi file = media galti se (GitHub 100 MB par mana karta hai)
SCAN_MAX_BYTES = 2 * 1024 * 1024


class Stop(Exception):
    """Sync rokna hai – message Hinglish mein."""


def git(base, *args, capture=True, check=False):
    cmd = ["git", "-c", "core.quotepath=false", "-C", base, *args]
    r = subprocess.run(cmd, capture_output=capture, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        raise Stop(f"git {' '.join(args)} fail hua:\n{(r.stderr or '').strip()}")
    return r


def changed_files(base):
    """[(code, path)] – git status (ignored files nahi aate)."""
    out = git(base, "status", "--porcelain=v1", "-z", "-uall", check=True).stdout
    parts, items, i = out.split("\0"), [], 0
    while i < len(parts):
        e = parts[i]
        i += 1
        if len(e) < 4:
            continue
        code, path = e[:2], e[3:]
        if code[0] in "RC":
            i += 1          # rename: agla hissa purana naam hai
        items.append((code, path))
    return items


def describe(code):
    if code == "??":
        return "naya"
    if "D" in code:
        return "hataya"
    if "R" in code:
        return "naam badla"
    if "U" in code or code in ("AA", "DD"):
        return "CONFLICT"
    return "badla"


def find_secrets(base, items):
    """[(path, wajah)] – jo files commit mein nahi jaani chahiye."""
    bad = []
    for code, path in items:
        if "D" in code:
            continue
        name = os.path.basename(path).lower()
        if any(fnmatch.fnmatch(name, p) for p in SECRET_NAMES):
            bad.append((path, "naam se secret/key file lagti hai"))
            continue
        full = os.path.join(base, path)
        if not os.path.isfile(full):
            continue
        size = os.path.getsize(full)
        if size > MAX_MB * 1024 * 1024:
            bad.append((path, f"{size / 1024 / 1024:.0f} MB ki badi file (media GitHub par nahi jaata)"))
            continue
        if size > SCAN_MAX_BYTES:
            continue
        try:
            with open(full, "rb") as f:
                data = f.read()
            if b"\0" in data[:4096]:
                continue        # binary
            text = data.decode("utf-8", errors="replace")
        except OSError:
            continue
        for label, pat in SECRET_PATTERNS:
            m = re.search(pat, text)
            if m:
                line = text.count("\n", 0, m.start()) + 1
                bad.append((path, f"line {line} par {label} jaisa kuch hai"))
                break
    return bad


def unmerged(base):
    out = git(base, "diff", "--name-only", "--diff-filter=U").stdout
    return [l for l in out.splitlines() if l.strip()]


def remote_branch_exists(base, branch):
    return git(base, "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{branch}").returncode == 0


def pending_cloud_branches(base):
    """origin ki branches jinka kaam abhi is branch mein nahi aaya (sirf dikhane ke liye)."""
    out = git(base, "branch", "-r", "--no-merged", "HEAD",
              "--format=%(refname:short)|%(committerdate:short)|%(subject)").stdout
    rows = []
    for line in out.splitlines():
        name, _, rest = line.partition("|")
        if not name or name.endswith("/HEAD") or name == "origin":
            continue
        date, _, subj = rest.partition("|")
        rows.append((name, date, subj))
    return rows


def sync(base=None, message=None, dry_run=False, ask=input, out=print):
    """Poora sync. Kuch galat ho to Stop raise. Return: 'synced' / 'dry-run' / 'nothing'."""
    base = base or T.BASE
    if not shutil.which("git"):
        raise Stop("git install nahi hai. PowerShell mein chalao: winget install Git.Git  (phir laptop restart)")
    if git(base, "rev-parse", "--is-inside-work-tree").returncode != 0:
        raise Stop(f"Ye folder git repo nahi hai: {base}\nClaude ko bolo, wo setup kar dega.")
    gitdir = git(base, "rev-parse", "--git-dir", check=True).stdout.strip()
    gitdir = gitdir if os.path.isabs(gitdir) else os.path.join(base, gitdir)
    if os.path.exists(os.path.join(gitdir, "MERGE_HEAD")) or unmerged(base):
        raise Stop("Pichla merge/conflict adhoora pada hai. Kuch mat chhuo – Claude ko bolo:\n"
                   "  'CODE SYNC mein conflict adhoora hai, theek karo'.")
    branch = git(base, "rev-parse", "--abbrev-ref", "HEAD", check=True).stdout.strip()
    if branch == "HEAD":
        raise Stop("Abhi koi branch nahi chuni hui (detached HEAD). Claude ko bolo.")
    out(f"Branch: {branch}")

    # 1) kya badla
    items = changed_files(base)
    if items:
        out(f"\nLaptop par {len(items)} badlav:")
        for code, path in items:
            out(f"  [{describe(code):<10}] {path}")
    else:
        out("\nLaptop par koi naya badlav nahi.")

    # 2) secret check
    bad = find_secrets(base, items)
    if bad:
        lines = "\n".join(f"  !! {p}  ({why})" for p, why in bad)
        raise Stop("RUK GAYE – ye files GitHub par nahi jaani chahiye:\n" + lines +
                   "\nKYA KARO: Claude ko bolo 'ye file .gitignore mein daalo' (key wali file kabhi upload nahi hoti)."
                   "\nKuch commit/push nahi hua.")
    if items:
        out("Secret check: theek (koi key/.env/badi media file nahi).")

    if dry_run:
        out("\n--dry-run: kuch commit / pull / push nahi kiya.")
        return "dry-run"

    # 3) commit
    if items:
        default = f"laptop se update {datetime.now():%d-%m-%Y %H:%M}"
        msg = message
        if msg is None:
            msg = ask(f"\nCommit ka message likho (Enter = '{default}'): ").strip()
        msg = msg or default
        git(base, "add", "-A", check=True)
        r = git(base, "commit", "-m", msg)
        if r.returncode != 0:
            err = (r.stderr or r.stdout or "").strip()
            if "user.email" in err or "user.name" in err or "identity" in err.lower():
                raise Stop("Git ko aapka naam/email nahi pata. PowerShell mein ek baar chalao:\n"
                           '  git config --global user.name "Shivam"\n'
                           '  git config --global user.email "aapki@email.com"')
            raise Stop("Commit nahi hua:\n" + err)
        out(f"Commit ho gaya: {msg}")

    # 4) pull (cloud ka kaam)
    has_origin = bool(git(base, "remote", "get-url", "origin").stdout.strip())
    if not has_origin:
        raise Stop("GitHub (origin) set nahi hai. Claude ko bolo.")
    out("\nGitHub se naya kaam la rahe hain...")
    r = git(base, "fetch", "origin", capture=False)
    if r.returncode != 0:
        raise Stop("GitHub se connect nahi hua (internet ya login). Internet check karke dobara chalao.\n"
                   "Aapka kaam laptop par commit mein safe hai.")
    if remote_branch_exists(base, branch):
        r = git(base, "merge", "--no-edit", f"origin/{branch}")
        if r.returncode != 0:
            conflicts = unmerged(base)
            if conflicts:
                git(base, "merge", "--abort")
                raise Stop("CONFLICT – laptop aur cloud dono ne same file badli hai:\n" +
                           "\n".join(f"  !! {c}" for c in conflicts) +
                           "\nMerge cancel kar diya, sab pehle jaisa hai. Aapka kaam commit mein safe hai."
                           "\nKYA KARO: Claude ko bolo 'CODE SYNC mein conflict aaya, in files ka theek karo'.")
            git(base, "merge", "--abort")
            raise Stop("Cloud ka kaam merge nahi hua:\n" + (r.stderr or r.stdout).strip() +
                       "\nClaude ko ye message dikhao.")
        out("Cloud ka kaam aa gaya." if "Already up to date" not in (r.stdout or "") else "Cloud par kuch naya nahi tha.")

    # 5) push
    ahead = git(base, "rev-list", "--count", f"origin/{branch}..HEAD").stdout.strip() \
        if remote_branch_exists(base, branch) else "1"
    if ahead and ahead != "0":
        out("\nGitHub par bhej rahe hain...")
        r = git(base, "push", "-u", "origin", branch, capture=False)
        if r.returncode != 0:
            raise Stop("Push nahi hua (internet / login / kisi ne beech mein naya kaam daala).\n"
                       "CODE SYNC dobara chalao. Phir bhi na ho to Claude ko bolo.")
        out("Push ho gaya.")
    else:
        out("\nGitHub par bhejne ko kuch naya nahi.")

    # 6) cloud branches jo abhi merge nahi hui
    pending = pending_cloud_branches(base)
    if pending:
        out("\nCloud par in branches mein kaam hai jo abhi aapke code mein NAHI aaya (Claude se merge karwao):")
        for name, date, subj in pending:
            out(f"  - {name}  ({date})  {subj}")
    out("\nSYNC POORA.")
    return "synced"


def main(argv=None):
    T.utf8_console()
    ap = argparse.ArgumentParser(description="theshivamiq code sync")
    ap.add_argument("--dry-run", action="store_true", help="sirf dikhao, kuch commit/push nahi")
    ap.add_argument("-m", "--message", help="commit message (na do to poochega)")
    a = ap.parse_args(argv)
    print("theshivamiq – CODE SYNC")
    try:
        sync(message=a.message, dry_run=a.dry_run)
    except Stop as e:
        print("\n" + "=" * 60 + f"\n{e}\n" + "=" * 60)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
