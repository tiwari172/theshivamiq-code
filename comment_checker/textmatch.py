"""Comment ko samajhna: Hindi->Roman, spelling ki galti, number (3 / no. 03 / teen / third)."""
import re, unicodedata

# ---------- Devanagari -> Roman (seedha, naam milane layak) ----------
_V = {"अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo", "ए": "e", "ऐ": "ai",
      "ओ": "o", "औ": "au", "ऋ": "ri", "ऑ": "o"}
_M = {"ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo", "े": "e", "ै": "ai", "ो": "o",
      "ौ": "au", "ृ": "ri", "ॉ": "o", "ॅ": "e"}
_C = {"क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n", "च": "ch", "छ": "chh", "ज": "j",
      "झ": "jh", "ञ": "n", "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n", "त": "t",
      "थ": "th", "द": "d", "ध": "dh", "न": "n", "प": "p", "फ": "ph", "ब": "b", "भ": "bh",
      "म": "m", "य": "y", "र": "r", "ल": "l", "व": "v", "श": "sh", "ष": "sh", "स": "s",
      "ह": "h", "ळ": "l", "क़": "k", "ख़": "kh", "ग़": "g", "ज़": "z", "ड़": "r", "ढ़": "rh",
      "फ़": "f", "य़": "y"}
_DIG = {"०": "0", "१": "1", "२": "2", "३": "3", "४": "4", "५": "5", "६": "6", "७": "7", "८": "8", "९": "9"}
_HAL, _NUKTA = "्", "़"


def translit(s):
    s = unicodedata.normalize("NFC", s)
    out, i = [], 0
    while i < len(s):
        ch = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if nxt == _NUKTA and ch + _NUKTA in _C:
            ch, i = ch + _NUKTA, i + 1
            nxt = s[i + 1] if i + 1 < len(s) else ""
        if ch in _C:
            out.append(_C[ch])
            if nxt == _HAL:
                i += 1
            elif nxt in _M:
                out.append(_M[nxt]); i += 1
            elif nxt and (nxt in _C or nxt in "ंँ"):
                out.append("a")
            elif nxt and nxt not in "ःऽ":
                pass  # shabd ka aakhri akshar: halka 'a' chhod do (कल्लू, राम)
        elif ch in _V:
            out.append(_V[ch])
        elif ch in "ंँ":
            out.append("n")
        elif ch in _DIG:
            out.append(_DIG[ch])
        elif ch in _M or ch in (_HAL, _NUKTA, "ः", "ऽ"):
            pass
        else:
            out.append(ch)
        i += 1
    return "".join(out)


# ---------- shabd todna + phonetic key ----------
STOP = set("""
a aa an the is am are was it to of in on and or no yes ok okay hai he hain hu hoon tha thi the ho
ka ki ke ko ne se me mein main mai par pe bhi to toh hi ye yeh wo woh vo voh is us un isne usne
ek do teen char kal aaj abhi sab sabse sir bhai bro sahab saab ji jii mr mrs ms miss dada didi
answer ans killer kaatil katil qatil chor chori culprit criminal guilty right correct sahi galat
wrong pakka pakad pakda pakdi liya lia mara maara maar kiya kia hua tha nahi nhi nahin na mat
kaun kon koun kaun hai mujhe lagta laga lgta mere mera hamara apna case video reel clue shivam
detective option opt number num ji bilkul obviously definitely confirm sure 100 percent
bola boli bole bolo bolin bolta kaha kehta kyunki kyuki kyuke kyoki kyu kyon because bcz bcoz bcs coz
isliye usne uske uski unke unki jab tab tak kaise kese kaisa kya kuch koi wala wali wale raha rahi rahe
tha thi the gaya gayi gye aaya aayi ata aata aati dekha dekho dekh pata sach jhooth jhoot jhuth
""".split())

_NUMWORD = {"ek": 1, "one": 1, "first": 1, "pehla": 1, "pehle": 1, "pahla": 1, "1st": 1,
            "do": 2, "two": 2, "second": 2, "doosra": 2, "dusra": 2, "dusre": 2, "2nd": 2,
            "teen": 3, "tin": 3, "three": 3, "third": 3, "teesra": 3, "tisra": 3, "teesre": 3, "3rd": 3,
            "char": 4, "chaar": 4, "four": 4, "fourth": 4, "chautha": 4, "chotha": 4, "4th": 4,
            "paanch": 5, "panch": 5, "five": 5, "fifth": 5, "5th": 5}
# "do"/"ek" aam shabd bhi hain, isliye ye sirf akele ya "no./option" ke baad number maane jaate hain
_WEAK_NUMWORD = {"ek", "do", "char", "first", "second", "pehle", "dusre"}


def tokens(text):
    t = translit(text or "").lower()
    t = re.sub(r"[^\w#]+", " ", t)
    return [w for w in t.split() if w]


def key(w):
    """Spelling ki chhoti galti barabar karne ke liye shabd ka 'dhaancha'."""
    w = w.lower()
    w = re.sub(r"[^a-z]", "", w)
    w = re.sub(r"c(?!h)", "k", w)              # cook -> kook, clerk -> klerk
    for a, b in (("chh", "c"), ("ch", "c"), ("ph", "f"), ("sh", "s"), ("kh", "k"), ("gh", "g"),
                 ("bh", "b"), ("dh", "d"), ("th", "t"), ("jh", "j"), ("q", "k"),
                 ("w", "v"), ("z", "j"), ("x", "ks")):
        w = w.replace(a, b)
    w = re.sub(r"(?<=[^aeiou])h", "", w)
    w = w.replace("ee", "i").replace("oo", "u").replace("e", "i").replace("o", "u")
    w = re.sub(r"(?<=i)y(?=[aiu])", "", w)  # riya -> ria
    w = re.sub(r"(.)\1+", r"\1", w)           # kallu -> kalu, nikhill -> nikil
    return w


def _lev(a, b, cap=3):
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def similar(tok_key, alias_key):
    if not tok_key or not alias_key:
        return False
    if tok_key == alias_key:
        return True
    n = min(len(tok_key), len(alias_key))
    if n < 4 or tok_key[0] != alias_key[0]:
        return False
    d = _lev(tok_key, alias_key)
    return d <= (1 if n <= 6 else 2)


# ---------- number nikaalna ----------
_UNITS = set("baje baja bje bjey bajkar bajke min mins minute minutes ghante ghanta ghnte hrs hour hours saal sal din "
             "pm am rs log logo logon lakh lac hazar hajar crore percent bus gaadi gadi baar bar kg".split())


def numbers_detail(text, max_n):
    """-> (pakke number, kachche number).
    Pakka: shuru mein ho, 'no./suspect/option' ke saath, '3rd', ya chhota comment.
    Kachcha: lambi baat (reason) ke beech mein aaya number."""
    t = translit(text or "").lower()
    t = re.sub(r"\b\d{1,2}\s*[:.]\s*\d{2}\b", " ", t)                    # 7:00, 1:30, 1.30 (time)
    t = re.sub(r"\b\d{1,2}\s*[:.]\s*0\b", " ", t)                       # 9:0
    t = re.sub(r"\b\d+\s*(am|pm|bje|baje|%)", " ", t)                   # 10pm, 2 baje, 100%
    t = re.sub(r"\b(no|num|number|option|opt|suspect|nmbr|nbr)\s*[.:#-]*\s*0*(\d)\b", r" #\2 ", t)
    words = re.findall(r"#?\d+(?:st|nd|rd|th)?|[a-z]+", t)
    short = len([w for w in words if w not in STOP or re.match(r"#?\d", w) or w in _NUMWORD]) <= 3
    strong, weak = [], []
    for i, w in enumerate(words):
        n, pakka = None, short or i == 0
        if re.fullmatch(r"#?0*\d+(st|nd|rd|th)?", w):
            digits = re.sub(r"\D", "", w)
            if not digits:
                continue
            n = int(digits)
            pakka = pakka or w.startswith("#") or not w[-1].isdigit()
            if i + 1 < len(words) and words[i + 1] in _UNITS:
                continue
        elif w in _NUMWORD:
            prev = words[i - 1] if i else ""
            if w == "one" and re.match(r"#?\d", prev):     # "3rd one", "3 one"
                continue
            if (w in _WEAK_NUMWORD or w == "one") and len(words) > 2:
                continue
            n = _NUMWORD[w]
        if n and 1 <= n <= max_n:
            (strong if pakka else weak).append(n)
    dedup = lambda xs: list(dict.fromkeys(xs))
    return dedup(strong), [x for x in dedup(weak) if x not in strong]


def numbers(text, max_n):
    s, w = numbers_detail(text, max_n)
    return s + w


QUIZ_RE = re.compile(r"(\d)\s*[\.\)\-:]?\s*([a-dA-D])\b")


def quiz_answers(text):
    return {int(q): a.upper() for q, a in QUIZ_RE.findall(translit(text or ""))}
