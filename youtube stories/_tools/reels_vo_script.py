# 10 reels ki VO script alag txt mein (local chat ko dene ke liye).
# python reels_vo_script.py "<10 Reels xlsx>" "<out txt>" <data module>
import sys, importlib, openpyxl
D = importlib.import_module(sys.argv[3])
wb = openpyxl.load_workbook(sys.argv[1])
rows = [r for r in wb["Shorts + Reels"].iter_rows(min_row=2, values_only=True) if r[0]]
cases = {c["n"]: c for c in D.CASES}
out = ["THESHIVAMIQ – BATCH 3: 10 REELS KI VO SCRIPT",
       "=" * 60,
       "Voice: ElevenLabs, Rudra, eleven_v4, stability 0.45, speed 1.05. Har reel ki VO EK BAAR mein banao, phir purana tighten.",
       "Emotion tag KAM SE KAM: sirf hook par [whispers]. Suspect ke bayaan par koi tag nahi (killer alag na lage).",
       "'⏸ 3 sec chup' = yahan voice mein 3 sec khaali (build_voice khud daalta hai). End wali 3 files purani hain – dobara MAT banao.",
       "Saboot kabhi bole nahi jaate (sirf tasveer). Jawab reel mein kabhi nahi.",
       "Images/motion/caption: 'Batch 3 - 10 Reels.xlsx' (Shorts + Reels, SHORTS MOTION PLAN, Image Prompts).", ""]
for (n, keep, hk), r in zip(D.SHORTS, rows):
    c = cases[n]
    out += ["-" * 60, f"{r[0].upper()} | {r[1]} | {r[6]}",
            "Suspect card: " + " | ".join(f"{j}/{len(keep)} {c['suspects'][k-1][3]}" for j, k in enumerate(keep, 1)),
            "Screen hook: " + hk[2], "", "VO (ElevenLabs mein ye paste karo, END line chhod kar):", r[8], ""]
out += ["=" * 60, "ANSWER KEY (SIRF AAPKE LIYE – screen par kabhi nahi, agle din pinned comment)"]
for (n, keep, hk) in D.SHORTS:
    c = cases[n]; s = c["suspects"][c["killer"] - 1]
    out.append(f"A-0{n}: {s[3]} (card par {keep.index(c['killer']) + 1}/{len(keep)}) – {c['answer']}")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
print("ok", len(rows))
