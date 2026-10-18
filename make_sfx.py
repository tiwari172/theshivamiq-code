# theshivamiq – Trial sound effects (computer se banaye hue)
#   python make_sfx.py   -> sfx\ folder mein pop, whoosh, boom, heartbeat, ding .wav
# Baad mein achhi SFX milein to same naam se sfx\ mein rakh do, ye wali replace ho jayengi.

import os, wave
import numpy as np

SR = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def pop():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 900 - 5000 * t                       # upar se neeche girti awaaz
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.03)


def pop2():
    # 'rise' popup ki awaaz: neeche se upar jaati bubble jaisi "bloop"
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = 300 + 9000 * t
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return tone * env(n, 0.004, 0.05)


def swish():
    # 'slide' popup ki awaaz: chhoti tez "swish"
    n = int(0.2 * SR)
    noise = np.random.default_rng(3).standard_normal(n)
    hp = np.append(noise[0], np.diff(noise))            # patli (high) awaaz
    return hp * np.sin(np.pi * np.arange(n) / n) ** 3


def whoosh():
    n = int(0.45 * SR)
    noise = np.random.default_rng(1).standard_normal(n)
    out, y = np.zeros(n), 0.0
    for i in range(n):                       # dheere-dheere khulta filter
        a = 0.02 + 0.25 * np.sin(np.pi * i / n)
        y += a * (noise[i] - y)
        out[i] = y
    return out * np.sin(np.pi * np.arange(n) / n) ** 2 * 3


def boom():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    f = 70 * np.exp(-t * 1.5) + 35
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.005, 0.35)
    hit = np.random.default_rng(2).standard_normal(n) * env(n, 0.001, 0.02) * 0.4
    return body + hit


def heartbeat():
    beat = int(0.75 * SR)
    one = np.zeros(beat)
    for off, amp in ((0, 1.0), (0.22, 0.7)):     # lub-dub
        s = int(off * SR)
        m = int(0.18 * SR)
        t = np.arange(m) / SR
        one[s:s + m] += amp * np.sin(2 * np.pi * 55 * t) * env(m, 0.004, 0.05)
    return np.tile(one, 4)


def ding():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    tone = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((1320, 1), (2640, 0.3), (3960, 0.1)))
    return tone * env(n, 0.002, 0.25)


def save(name, x):
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    data = (x * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("pop", pop), ("pop2", pop2), ("swish", swish),("whoosh", whoosh), ("boom", boom),
                     ("heartbeat", heartbeat), ("ding", ding)):
        path = os.path.join(OUT, name + ".wav")
        if os.path.exists(path):
            print("pehle se hai, chhod diya:", name)
            continue
        save(name, fn())
        print("bana:", name)
