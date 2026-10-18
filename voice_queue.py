# theshivamiq – Voice queue (kai chats ek saath voice banayein to takkar na ho)
#
# SLOTS jitne kaam ek saath chal sakte hain. Har kaam ko apna alag folder milta hai
# (work\voice_slot1, slot2 ...). Slot khaali na ho to agla khaali slot try hota hai,
# saare busy hon to line mein wait. Chat band/crash ho jaaye to slot apne aap chhoot jaata hai.
#
#   from voice_queue import slot, safe_replace
#   with slot("voice") as folder:  ...   # folder = is kaam ka apna temp folder

import contextlib, msvcrt, os, shutil, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(BASE, "work")
SLOTS = {"voice": 4, "eleven": 3}   # voice jodna/tighten = 4 ek saath, ElevenLabs API = 3 ek saath
WAIT = 2                            # busy ho to kitne second baad dobara dekhe


def _log(msg):
    print(f"[queue] {msg}", file=sys.stderr, flush=True)   # stderr: CSV wale time print mein na mile


@contextlib.contextmanager
def slot(kind="voice"):
    os.makedirs(WORK, exist_ok=True)
    n, waited = SLOTS.get(kind, 2), False
    while True:
        for i in range(1, n + 1):
            f = open(os.path.join(WORK, f"{kind}_slot{i}.lock"), "a+")
            f.seek(0)
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                f.close()
                continue
            folder = os.path.join(WORK, f"{kind}_slot{i}")
            shutil.rmtree(folder, ignore_errors=True)
            os.makedirs(folder, exist_ok=True)
            _log(f"{kind} slot {i}/{n} mila" + (" (line khatam)" if waited else ""))
            try:
                yield folder
            finally:
                shutil.rmtree(folder, ignore_errors=True)
                f.seek(0)
                with contextlib.suppress(OSError):
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                f.close()
            return
        if not waited:
            _log(f"saare {n} {kind} slot busy, line mein wait kar raha hoon...")
            waited = True
        time.sleep(WAIT)


def safe_replace(src, dst, tries=30):
    # poori file ban jaane ke baad hi final naam par rakho (koi aadhi file na padhe)
    for _ in range(tries):
        try:
            os.replace(src, dst)
            return
        except PermissionError:   # koi aur (jaise render) abhi file padh raha hai
            time.sleep(1)
    os.replace(src, dst)


if __name__ == "__main__":
    # haath se audio kaatna/jodna bhi queue mein:  py voice_queue.py ffmpeg -i a.mp3 ... "SLOTDIR\x.wav"
    # SLOTDIR = is kaam ka apna alag folder (kaam khatam hote hi saaf; final file bahar likho)
    import subprocess
    with slot("voice") as folder:
        code = subprocess.run([a.replace("SLOTDIR", folder) for a in sys.argv[1:]]).returncode
    sys.exit(code)
