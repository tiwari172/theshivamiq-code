# Script dene se pehle khud check (user ka checklist, 2026-10-24).
# python check_batch.py <data module>   -> PROBLEM list (khaali = sab theek)
import sys, re, importlib, collections
D = importlib.import_module(sys.argv[1])
P = []
def w(t): return len(re.sub(r"[।,.?…]", " ", t).split())
cards, pats = collections.Counter(), collections.Counter()
for n, keep, hk in D.SHORTS:
    c = [x for x in D.CASES if x["n"] == n][0]; tag = f"A-0{n}"
    if c["killer"] not in keep: P.append(f"{tag}: kaatil reel mein nahi")
    if c["galat"][2] not in keep: P.append(f"{tag}: galat-ishara wala reel mein nahi")
    cards[keep.index(c["killer"]) + 1] += 1
    pats[c["pattern"].split("(")[0].strip()] += 1
    L = {k: w(c["suspects"][k - 1][2]) for k in keep}
    kl, others = L[c["killer"]], [v for k, v in L.items() if k != c["killer"]]
    if kl > max(others): P.append(f"{tag}: kaatil ki line sabse lambi ({kl} shabd, baaki max {max(others)})")
    if abs(kl - sorted(others)[len(others) // 2]) > 3: P.append(f"{tag}: kaatil ki line baaki se alag lambai ({kl} vs {sorted(others)})")
    for k in keep:
        s = c["suspects"][k - 1]
        if "!" in s[2]: P.append(f"{tag}: '!' bayaan mein ({s[3]})")
        if not 8 <= w(s[2]) <= 16: P.append(f"{tag}: {s[3]} ki line {w(s[2])} shabd (10-15 chahiye)")
    timed = [bool(re.search(r"बजे|बजकर|चालीस", c["suspects"][k - 1][2])) for k in keep]
    if any(timed) and not all(timed): P.append(f"{tag}: time kuch lines mein hai, kuch mein nahi")
    dev = " ".join([hk[0], c["setup"][0][0], c["setup"][1][0], c["entry"][0], c["jagah"][0]] + [c["suspects"][k - 1][2] for k in keep])
    if re.search(r"बोले|बोलीं|बोली", dev): P.append(f"{tag}: 'bole/boli' VO mein")
    if c["city"].lower() not in (c["setup"][0][1] + c["setup"][1][1]).lower(): P.append(f"{tag}: shehar ({c['city']}) VO mein nahi")
    for o in {x["city"] for x in D.CASES} - {c["city"]}:
        if o.lower() in c["title"].lower(): P.append(f"{tag}: title mein doosra shehar ({o})")
    for k in keep:
        r = getattr(D, "REUSE", {}).get(("S", n, k))
        if r and r[1]: P.append(f"{tag}: suspect {k} ka naam REUSE se badal raha ({r[2]}) – data mein hi sahi naam likho")
    for nm in [c["suspects"][k - 1][3].split()[-1] for k in keep]:
        pass
for k, v in cards.items():
    if v > 2: P.append(f"Kaatil card {k}/5 – {v} baar (max 2)")
miss = set(range(1, 6)) - set(cards)
if miss and len(D.SHORTS) >= 5: P.append(f"Kaatil card number kabhi nahi aaye: {sorted(miss)}")
for k, v in pats.items():
    if v > 3: P.append(f"Pattern '{k}' {v} baar (max 3)")
print("\n".join(P) if P else "SAB THEEK – checklist pass")
print("Kaatil card:", dict(sorted(cards.items())), "| Patterns:", dict(pats))
