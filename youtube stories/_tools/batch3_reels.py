# Batch 3 se SIRF 10 reels (har case ki ek). Data batch3_data wala, bas SHORTS = saare 10 case.
# Har reel: 5 suspect = killer + galat-ishara wala + purani image wale (taaki nayi image kam bane).
from batch3_data import *
from batch3_data import CASES, REUSE, SHORTS as _OLD
_old = {s[0]: s for s in _OLD}
SHORTS = []
for _c in CASES:
    _n = _c["n"]
    if _n in _old: SHORTS.append(_old[_n]); continue
    _must = sorted({_c["killer"], _c["galat"][2]})
    _all = range(1, len(_c["suspects"]) + 1)
    _rest = [k for k in _all if k not in _must and ("S", _n, k) in REUSE] + [k for k in _all if k not in _must and ("S", _n, k) not in REUSE]
    SHORTS.append((_n, sorted(_must + _rest[:5 - len(_must)]), _c["hook"]))
