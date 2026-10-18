"""YouTube screenshot khud check: image ka text (OCR, tesseract) padh kar dekho
"Subscribed" (ya Hindi "सदस्यता ली गई") aur channel ka naam (Shivam) likha hai ya nahi.
Server par chahiye:  sudo apt-get install -y tesseract-ocr tesseract-ocr-hin
tesseract na ho to check() None deta hai -> bot purane tareeke se admin ko bhejta hai.
"""
import hashlib, os, re, shutil, subprocess, tempfile

# "Subscribed" button (English) / "सदस्यता ली गई" (Hindi). "Subscribe" (bina d) = abhi subscribe nahi kiya.
SUBSCRIBED_RE = re.compile(r"subscri\w{0,3}ed|subscribed|सदस्यता\s*ली|सदस्यता\s*लिया|सब्सक्राइब\s*किया", re.I)
CHANNEL_RE = re.compile(r"shivam|शिवम", re.I)


def has_tesseract():
    return shutil.which("tesseract") is not None


def _ocr(path, langs):
    try:
        r = subprocess.run(["tesseract", path, "stdout", "-l", langs], capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return r.stdout.decode("utf-8", "ignore")


def read_text(path):
    """Image ka saara text. Dark mode (kaale background par safed text) ke liye ulti image bhi padhte hain."""
    langs = "eng+hin"
    txt = _ocr(path, langs) or _ocr(path, "eng")
    langs = langs if txt else "eng"
    try:
        from PIL import Image, ImageOps
        im = Image.open(path).convert("L")
        if im.width < 1000:                       # chhoti image badi karo, OCR achha padhta hai
            im = im.resize((im.width * 2, im.height * 2))
        fd, inv = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        try:
            ImageOps.invert(im).save(inv)
            txt += "\n" + _ocr(inv, langs)
        finally:
            os.remove(inv)
    except Exception:
        pass                                      # PIL na ho to sirf normal image
    return txt


def judge(text):
    """(pass?, wajah) – text se faisla."""
    sub = bool(SUBSCRIBED_RE.search(text or ""))
    ch = bool(CHANNEL_RE.search(text or ""))
    if sub and ch:
        return True, "Subscribed + Shivam dono dikhe"
    if not sub:
        return False, "'Subscribed' nahi dikha"
    return False, "channel ka naam (Shivam) nahi dikha"


def check(path):
    """None = OCR nahi hai (admin dekhe). Warna (pass?, wajah)."""
    if not has_tesseract():
        return None
    return judge(read_text(path))


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
