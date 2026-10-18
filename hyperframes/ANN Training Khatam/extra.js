// ANN Training Khatam – khaas scenes (engine ka optional EXTRA). Time = voice time (OFF 0).
const EXTRA = function (tl, H) {
  const { el, $, rnd } = H;
  const RED = "#E53935", YEL = "#FFD400";
  const A = el("div", "layer", null, null);
  A.id = "ann";
  $("cam").insertBefore(A, $("black"));
  const hide = (n) => tl.set(n, { display: "none" }, 0);
  const show = (n, t) => tl.set(n, { display: "block" }, t);
  const shake = (t, px) => {
    for (let k = 0; k < 6; k++)
      tl.to(A, { x: k === 5 ? 0 : (px || 14) * (1 - k / 6) * (k % 2 ? -1 : 1), duration: 0.035, ease: "none" }, t + k * 0.035);
  };

  // ---------- dark case-file room look ----------
  const dark = el("div", "layer", null, null, {
    background: "radial-gradient(ellipse at 50% 42%, rgba(18,20,32,0.62) 0%, rgba(6,7,12,0.86) 58%, rgba(0,0,0,0.97) 100%)",
  });
  $("cam").insertBefore(dark, $("night"));
  const grain = el("div", "layer", null, null, {
    backgroundImage:
      "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='320'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0.55 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>\")",
    opacity: 0.08, mixBlendMode: "overlay", pointerEvents: "none",
  });
  $("story").insertBefore(grain, $("wipe"));
  for (let t = 0; t < END; t += 0.1)
    tl.set(grain, { backgroundPosition: Math.round(rnd() * 320) + "px " + Math.round(rnd() * 320) + "px" }, t);
  // camera saans
  tl.fromTo(A, { scale: 1 }, { scale: 1.02, duration: 2, ease: "sine.inOut", yoyo: true, repeat: Math.floor(END / 2) }, 0);

  const big = (html, css) => el("div", null, html, A, Object.assign({
    position: "absolute", left: "40px", right: "40px", textAlign: "center", lineHeight: 1.05,
    WebkitTextStroke: "12px #111", paintOrder: "stroke fill", opacity: 0,
  }, css));
  const black = el("div", "layer", null, A, { background: "#000", opacity: 0 });

  // ================= SHOT 1 (0 – 2.86): kaala + flicker + typewriter =================
  tl.set(black, { opacity: 1 }, 0);
  const flick = el("div", "layer", null, A, { background: "radial-gradient(ellipse at 50% 40%, rgba(200,215,255,0.35), rgba(0,0,0,0) 70%)", opacity: 0 });
  [[0.08, 0.6], [0.16, 0], [0.3, 0.8], [0.42, 0.1], [0.55, 0.45], [2.7, 0]].forEach(([t, o]) => tl.set(flick, { opacity: o }, t));
  const q1 = big("", { top: "660px", fontSize: "112px", color: "#fff", opacity: 1 });
  "TUMNE CASE|SOLVE KIYE".split("").forEach((c, k) => {
    if (c === "|") { el("br", null, null, q1); return; }
    const s = el("span", null, c === " " ? "&nbsp;" : c, q1, { opacity: 0 });
    tl.set(s, { opacity: 1 }, 0.3 + k * 0.065);
  });
  const qm = el("span", null, "?", q1, { color: RED, display: "inline-block", fontSize: "170px", opacity: 0 });
  tl.fromTo(qm, { opacity: 0, scale: 3, rotation: 20 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.25, ease: "back.out(2.5)" }, 1.75);
  tl.to(qm, { scale: 1.15, duration: 0.3, yoyo: true, repeat: 1, ease: "sine.inOut" }, 2.05);
  tl.to(q1, { opacity: 0, duration: 0.15 }, 2.72);
  tl.to(black, { opacity: 0, duration: 0.2 }, 2.75);

  // ================= SHOT 2 (2.86 – 12.46): comment bubbles =================
  const COMMENTS = [
    "Aap ki Har story mein 3 number wala hi katil hota hai",
    "Kuchh to change kiya karo",
    "Bhai aapki video mein sabse jyada Vikas hi mara hai",
    "Hard nhi hai bro",
    "Bhai kuch achha lao ye to bohot jaldi mil gaya",
    "Kuch bhi itna esey question kon puchta he",
    "bohot easy easy ha kuch hard bhi poso😂😂",
    "itna esey bhai",
  ];
  const AV = ["#6d6f78", "#7b6a5a", "#5a6b7b", "#6b5a7b", "#5a7b6a", "#7b5a5a", "#6a6a6a", "#5f6f5a"];
  const cwrap = el("div", "layer", null, A);
  const BOT = 1200, GAP = 22;
  const items = COMMENTS.map((txt, k) => {
    const lines = Math.ceil(txt.length / 30);
    const h = 104 + lines * 50;
    const b = el("div", null, null, cwrap, {
      position: "absolute", left: "50px", width: "980px", height: h + "px", top: BOT - h + "px", opacity: 0,
      background: "rgba(22,22,28,0.94)", borderRadius: "30px", border: "2px solid rgba(255,255,255,0.08)",
      boxShadow: "0 14px 30px rgba(0,0,0,0.5)", fontFamily: "'Segoe UI', Arial, sans-serif", color: "#fff",
    });
    el("div", null, null, b, { position: "absolute", left: "26px", top: "24px", width: "84px", height: "84px", borderRadius: "50%",
      background: "radial-gradient(circle at 50% 38%, #c9c9cf 0 18px, " + AV[k] + " 19px)" });
    el("div", null, 'user_<span style="filter:blur(7px)">a8k2</span> <span style="color:#8e8e96;font-weight:400;font-size:28px">&nbsp;' + (k + 1) + "h</span>", b,
      { position: "absolute", left: "134px", top: "20px", fontSize: "30px", fontWeight: 700, color: "#d8d8de" });
    el("div", null, txt, b, { position: "absolute", left: "134px", right: "96px", top: "62px", fontSize: "42px", fontWeight: 700, lineHeight: 1.18 });
    el("div", null, "Reply", b, { position: "absolute", left: "134px", bottom: "14px", fontSize: "26px", color: "#8e8e96", fontWeight: 600 });
    el("div", null, '<svg width="40" height="40" viewBox="0 0 24 24"><path d="M12 21s-7.5-4.6-9.6-9.2C.9 8.3 3 4.5 6.7 4.5c2.1 0 3.6 1.2 4.3 2.4.7-1.2 2.2-2.4 4.3-2.4 3.7 0 5.8 3.8 4.3 7.3C19.5 16.4 12 21 12 21z" fill="none" stroke="#a0a0a8" stroke-width="2"/></svg>', b,
      { position: "absolute", right: "30px", top: "34px" });
    return { b, h, t: 3.0 + k * 1.12 };
  });
  items.forEach((it, k) => {
    tl.fromTo(it.b, { opacity: 0, y: 220, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.9)" }, it.t);
    // purane upar khiskein
    let off = 0;
    for (let j = k - 1; j >= 0; j--) {
      off += items[j + 1].h + GAP;
      const o = BOT - items[j].h - off;   // top position
      tl.to(items[j].b, { y: -off, duration: 0.4, ease: "power3.out" }, it.t);
      if (o < 250) tl.to(items[j].b, { opacity: 0, duration: 0.3 }, it.t);
    }
  });
  const lol = items[6].b;
  tl.to(lol, { scale: 1.07, duration: 0.18, yoyo: true, repeat: 3, ease: "sine.inOut" }, items[6].t + 0.5);
  [-2, 2, -1.5, 1.5, 0].forEach((r, k) => tl.to(lol, { rotation: r, duration: 0.09 }, items[6].t + 0.5 + k * 0.09));

  // ================= SHOT 3 (12.46 – 15.87): blur + Shivam smirk =================
  tl.to(cwrap, { filter: "blur(10px)", scale: 0.9, opacity: 0.35, duration: 0.5, ease: "power2.out" }, 12.46);
  tl.to(cwrap, { opacity: 0, duration: 0.25 }, 15.6);
  const bust = (src, css) => {
    const w = el("div", null, null, A, Object.assign({ position: "absolute", opacity: 0 }, css));
    const im = el("img", null, null, w, { display: "block", height: "100%",
      WebkitMaskImage: "linear-gradient(180deg, #000 68%, rgba(0,0,0,0) 98%)", maskImage: "linear-gradient(180deg, #000 68%, rgba(0,0,0,0) 98%)" });
    im.src = "assets/" + src + ".png";
    return w;
  };
  const sm = bust("S2_17", { left: "300px", top: "250px", height: "960px" });
  tl.fromTo(sm, { opacity: 0, x: 800, skewX: -10 }, { opacity: 1, x: 0, skewX: 0, duration: 0.45, ease: "power4.out" }, 12.46);
  tl.to(sm, { scale: 1.05, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, 14.94);
  tl.to(sm, { opacity: 0, x: 700, duration: 0.25, ease: "power2.in" }, 15.62);

  // ================= SHOT 4 (15.87 – 21.6): evidence wall =================
  const wall = el("div", null, null, A, { position: "absolute", left: 0, top: 0, width: "1080px", height: "1920px", opacity: 0 });
  gsap.set(wall, { transformOrigin: "0 0" });
  el("div", null, null, wall, { position: "absolute", left: "16px", top: "170px", width: "1048px", height: "1370px", borderRadius: "18px",
    background: "radial-gradient(ellipse at 50% 45%, #5a3d27 0%, #3d2818 70%, #2a1b10 100%)",
    boxShadow: "inset 0 0 0 14px #2b1d12, inset 0 0 80px rgba(0,0,0,0.7), 0 20px 60px rgba(0,0,0,0.6)" });
  const TILT = [-3.5, 2.5, -1.5, 3.8, 2, -3, 1.2, -2.6, 3.2, -1.8, 2.8, -3.6];
  const CW = 225, CH = 400;
  const covers = [];
  for (let k = 0; k < 12; k++) {
    const c = k % 4, r = Math.floor(k / 4);
    const left = 52 + c * 250, top = 215 + r * 440;
    const cv = el("div", null, null, wall, { position: "absolute", left: left + "px", top: top + "px", width: CW + "px", height: CH + "px",
      background: "#f2efe6", padding: "6px", boxShadow: "0 12px 22px rgba(0,0,0,0.55)", opacity: 0 });
    gsap.set(cv, { rotation: TILT[k] });
    const im = el("img", null, null, cv, { display: "block", width: "100%", height: "100%" });
    im.src = "assets/cover_" + String(k + 1).padStart(2, "0") + ".png";
    const hl = el("div", null, null, cv, { position: "absolute", left: "30%", top: "13.4%", width: "40.5%", height: "5.6%",
      background: YEL, mixBlendMode: "screen", opacity: 0 });
    covers.push({ cv, hl, cx: left + CW / 2, cy: top + CH / 2, rot: TILT[k], top });
    tl.fromTo(cv, { opacity: 0, y: -120, scale: 1.25 }, { opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.6)" }, 15.9 + k * 0.06);
  }
  // pins + laal dhaage
  const pin = (k) => { const v = covers[k], a = (v.rot * Math.PI) / 180; return [v.cx + 185 * Math.sin(a), v.cy - 185 * Math.cos(a)]; };
  const PAIRS = [[0, 5], [5, 2], [2, 7], [1, 6], [6, 11], [4, 9], [9, 10], [3, 6], [8, 5], [10, 7], [4, 1]];
  let svg = '<svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">';
  PAIRS.forEach(([a, b]) => { const [x1, y1] = pin(a), [x2, y2] = pin(b);
    svg += `<line class="str" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#c62828" stroke-width="4" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`; });
  for (let k = 0; k < 12; k++) { const [x, y] = pin(k);
    svg += `<circle cx="${x}" cy="${y + 3}" r="15" fill="rgba(0,0,0,0.35)"/><circle cx="${x}" cy="${y}" r="14" fill="#e53935" stroke="#7f0000" stroke-width="3"/><circle cx="${x - 4}" cy="${y - 4}" r="4" fill="#ffb3b3"/>`; }
  svg += "</svg>";
  const strings = el("div", null, svg, wall, { position: "absolute", left: 0, top: 0, opacity: 0 });
  tl.to(strings, { opacity: 1, duration: 0.2 }, 16.5);
  strings.querySelectorAll(".str").forEach((s, k) => tl.to(s, { attr: { "stroke-dashoffset": 0 }, duration: 0.35, ease: "power1.inOut" }, 16.55 + k * 0.07));
  tl.set(wall, { opacity: 1 }, 15.87);
  tl.fromTo(wall, { scale: 1, x: 0, y: 0 }, { scale: 1.12, x: 540 * (1 - 1.12) + 24, y: 960 * (1 - 1.12), duration: 5.6, ease: "sine.inOut" }, 15.95);
  // "case number" par peela flash
  covers.forEach(({ hl }) => {
    tl.to(hl, { opacity: 0.85, duration: 0.1 }, 20.51);
    tl.to(hl, { opacity: 0, duration: 0.15 }, 20.66);
    tl.to(hl, { opacity: 0.85, duration: 0.1 }, 20.85);
    tl.to(hl, { opacity: 0, duration: 0.2 }, 21.0);
  });

  // ================= SHOT 5 (21.6 – 29.9): 3 DIVE =================
  const S = 6.2, NY = 800;
  const badge = (k) => { const v = covers[k], a = (v.rot * Math.PI) / 180, d = 0.338 * CH;
    return [v.cx + d * Math.sin(a), v.cy - d * Math.cos(a)]; };
  const at = (k, s) => { const [px, py] = badge(k); return { scale: s, x: 540 - px * s, y: NY - py * s }; };
  const ring = el("div", null,
    `<svg width="1080" height="420" viewBox="0 0 1080 420"><path class="rp" d="M 210 230 C 200 120, 420 80, 560 84 C 760 88, 900 130, 890 214 C 880 300, 700 336, 520 334 C 320 332, 170 300, 186 210 C 196 150, 300 110, 420 98" fill="none" stroke="${RED}" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>`,
    A, { position: "absolute", left: 0, top: NY - 210 + "px", width: "1080px", height: "420px", opacity: 0 });
  const rp = ring.querySelector(".rp");
  const GRUNGE = "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='g'><feTurbulence baseFrequency='0.06' numOctaves='3' seed='4'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -3.2 0 0 0 2.5'/></filter><rect width='100%' height='100%' filter='url(%23g)'/></svg>\")";
  const stampBox = (txt, size, top) => {
    const w = el("div", null, null, A, { position: "absolute", left: 0, right: 0, top: top + "px", display: "flex", justifyContent: "center", opacity: 0 });
    el("div", null, txt, w, { fontSize: size + "px", color: RED, border: Math.round(size / 9) + "px solid " + RED, borderRadius: "18px",
      padding: "6px 34px 12px", letterSpacing: "6px", background: "rgba(12,4,4,0.82)", WebkitMaskImage: GRUNGE, maskImage: GRUNGE,
      WebkitMaskSize: "240px 240px", textShadow: "0 0 2px " + RED });
    return w;
  };
  const DIVES = [
    { k: 0, t: 21.6, stamp: stampBox("LEVEL: EASY", 92, NY + 150), st: 22.85, out: 24.45 },
    { k: 6, t: 24.85, stamp: stampBox("LEVEL: EASY", 92, NY + 150), st: 26.05, out: 27.1 },
    { k: 8, t: 27.5, stamp: stampBox("TRAINING", 130, NY + 140), st: 29.16, out: 29.85 },
  ];
  DIVES.forEach((d, i) => {
    const tgt = at(d.k, S);
    if (i === 0) tl.to(wall, { ...tgt, duration: 0.6, ease: "power3.inOut" }, d.t);
    else {
      const p = DIVES[i - 1], a = at(p.k, 2.2), b = at(d.k, 2.2);
      tl.to(wall, { scale: 2.2, x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, filter: "blur(12px)", duration: 0.35, ease: "power2.in" }, d.t - 0.35);
      tl.to(wall, { ...tgt, duration: 0.5, ease: "power3.out" }, d.t);
    }
    tl.fromTo(wall, { filter: i === 0 ? "blur(4px)" : "blur(12px)" }, { filter: "blur(0px)", duration: i === 0 ? 0.6 : 0.5, ease: "power2.out" }, d.t);
    const rot = covers[d.k].rot - 6;
    tl.set(ring, { opacity: 1, rotation: rot }, d.t + 0.62);
    tl.fromTo(rp, { attr: { "stroke-dashoffset": 1 } }, { attr: { "stroke-dashoffset": 0 }, duration: 0.5, ease: "power1.inOut" }, d.t + 0.62);
    tl.fromTo(d.stamp, { opacity: 0, scale: 2.2, rotation: -2 }, { opacity: 1, scale: 1, rotation: -8, duration: 0.15, ease: "back.out(1.4)" }, d.st);
    shake(d.st + 0.15, i === 2 ? 22 : 12);
    tl.to([ring, d.stamp], { opacity: 0, duration: 0.12 }, d.out);
  });

  tl.to(strings, { opacity: 0, duration: 0.25 }, 21.6);
  tl.to(strings, { opacity: 1, duration: 0.3 }, 29.95);

  // ================= SHOT 6 (29.9 – 33.5): board + TRAINING stamp -> folder =================
  tl.to(wall, { scale: 1, x: 0, y: 0, duration: 0.5, ease: "power3.inOut" }, 29.9);
  const bigStamp = stampBox("TRAINING", 190, 760);
  tl.fromTo(bigStamp, { opacity: 0, scale: 2.4, rotation: -4 }, { opacity: 1, scale: 1, rotation: -14, duration: 0.18, ease: "back.out(1.4)" }, 30.45);
  shake(30.63, 16);
  // folder
  const fol = el("div", null, null, A, { position: "absolute", left: "160px", top: "640px", width: "760px", height: "560px", opacity: 0, perspective: "1400px" });
  el("div", null, null, fol, { position: "absolute", left: "30px", top: "-46px", width: "260px", height: "70px", background: "#c99a52", borderRadius: "16px 16px 0 0" });
  el("div", null, null, fol, { position: "absolute", inset: 0, background: "#c99a52", borderRadius: "0 14px 14px 14px", boxShadow: "0 30px 60px rgba(0,0,0,0.6)" });
  const flap = el("div", null, null, fol, { position: "absolute", inset: 0, background: "linear-gradient(180deg,#e2bb73,#d4a85e)", borderRadius: "14px",
    transformOrigin: "50% 100%", boxShadow: "0 -4px 14px rgba(0,0,0,0.25)", display: "flex", alignItems: "center", justifyContent: "center", backfaceVisibility: "hidden" });
  el("div", null, "TRAINING FILES<br><span style='font-size:64px'>– CLOSED –</span>", flap, { fontSize: "62px", color: "#2a1a08", textAlign: "center", lineHeight: 1.15,
    padding: "18px 30px", border: "6px solid #2a1a08", borderRadius: "10px", background: "rgba(255,255,255,0.18)" });
  tl.set(fol, { opacity: 1 }, 32.05);
  tl.fromTo(flap, { rotationX: -88 }, { rotationX: -88, duration: 0.01 }, 32.05);
  tl.to(wall, { scale: 0.42, x: 540 * (1 - 0.42), y: 920 * (1 - 0.42), opacity: 0, duration: 0.55, ease: "power3.in" }, 32.05);
  tl.to(bigStamp, { scale: 0.42, opacity: 0, duration: 0.55, ease: "power3.in" }, 32.05);
  tl.to(flap, { rotationX: 0, duration: 0.38, ease: "power2.in" }, 32.62);
  shake(33.0, 8);
  tl.to(fol, { y: 1300, rotation: 6, duration: 0.45, ease: "power3.in" }, 33.08);
  tl.set(fol, { opacity: 0 }, 33.55);

  // ================= SHOT 7 (33.5 – 35.1): kaala + laal dot =================
  tl.to(black, { opacity: 1, duration: 0.15 }, 33.45);
  const dot = el("div", null, null, A, { position: "absolute", left: "522px", top: "802px", width: "36px", height: "36px", borderRadius: "50%",
    background: RED, boxShadow: "0 0 40px 12px rgba(229,57,53,0.55)", opacity: 0 });
  tl.fromTo(dot, { opacity: 0.4, scale: 0.8 }, { opacity: 1, scale: 1.5, duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: 3 }, 33.55);
  tl.to(dot, { opacity: 0, duration: 0.1 }, 35.12);

  // ================= SHOT 8 (35.15 – 36.3): TRAINING KHATAM =================
  const tk1 = big("TRAINING", { top: "660px", fontSize: "150px", color: RED, WebkitTextStroke: "16px #111" });
  const tk2 = big("KHATAM!", { top: "830px", fontSize: "170px", color: RED, WebkitTextStroke: "16px #111" });
  tl.fromTo(tk1, { opacity: 0, scale: 2.6 }, { opacity: 1, scale: 1, duration: 0.18, ease: "power4.in" }, 35.15);
  tl.fromTo(tk2, { opacity: 0, scale: 2.8 }, { opacity: 1, scale: 1, duration: 0.18, ease: "power4.in" }, 35.5);
  shake(35.68, 26);
  tl.fromTo("#redflash", { opacity: 0.55 }, { opacity: 0, duration: 0.4, ease: "power2.out" }, 35.68);
  tl.to([tk1, tk2], { scale: 1.04, duration: 0.2, yoyo: true, repeat: 1 }, 35.9);
  tl.to([tk1, tk2], { opacity: 0, duration: 0.15 }, 36.2);
  tl.to(black, { opacity: 0, duration: 0.25 }, 36.2);

  // ================= SHOT 9 (36.31 – 40.78): SOMWAR + cabinet + taala =================
  const som = big("SOMWAR", { top: "300px", fontSize: "150px", color: YEL, WebkitTextStroke: "14px #111" });
  tl.fromTo(som, { opacity: 0, scale: 2.2, rotation: -6 }, { opacity: 1, scale: 1, rotation: -3, duration: 0.22, ease: "power4.in" }, 36.31);
  tl.to(som, { scale: 1.06, duration: 0.45, yoyo: true, repeat: 3, ease: "sine.inOut" }, 36.7);
  tl.to(som, { opacity: 0, duration: 0.15 }, 40.62);
  const cab = el("div", null, null, A, { position: "absolute", left: "270px", top: "500px", width: "540px", height: "780px", opacity: 0,
    background: "linear-gradient(90deg,#3a3f46 0%,#5b626b 18%,#474d55 50%,#5b626b 82%,#353a40 100%)", borderRadius: "14px",
    boxShadow: "0 40px 70px rgba(0,0,0,0.75), inset 0 0 0 6px #2a2e33" });
  const drawers = [];
  for (let k = 0; k < 3; k++) {
    const d = el("div", null, null, cab, { position: "absolute", left: "28px", right: "28px", top: 30 + k * 248 + "px", height: "226px", borderRadius: "8px",
      background: "linear-gradient(180deg,#6b737d 0%,#4d545c 100%)", boxShadow: "inset 0 3px 0 rgba(255,255,255,0.18), inset 0 -4px 0 rgba(0,0,0,0.35), 0 4px 8px rgba(0,0,0,0.4)" });
    el("div", null, null, d, { position: "absolute", left: "175px", width: "134px", bottom: "34px", height: "26px", borderRadius: "13px",
      background: "linear-gradient(180deg,#c5ccd4,#7d858e)", boxShadow: "0 3px 4px rgba(0,0,0,0.5)" });
    drawers.push(d);
  }
  const top = drawers[0];
  el("div", null, "HARD CASES", top, { position: "absolute", left: "36px", top: "30px", width: "276px", textAlign: "center", fontSize: "32px",
    color: "#fff", background: RED, padding: "6px 4px 10px", borderRadius: "6px", border: "3px solid #111" });
  const lock = el("div", null,
    `<svg width="130" height="170" viewBox="0 0 130 170"><path class="shk" d="M 30 80 L 30 48 C 30 14, 100 14, 100 48 L 100 80" fill="none" stroke="#b9c0c8" stroke-width="16" stroke-linecap="round"/><rect x="8" y="72" width="114" height="92" rx="16" fill="#d4a017" stroke="#6b4e00" stroke-width="5"/><circle cx="65" cy="110" r="12" fill="#3a2a00"/><rect x="59" y="114" width="12" height="28" rx="4" fill="#3a2a00"/></svg>`,
    top, { position: "absolute", right: "26px", top: "14px", width: "130px", height: "170px", transformOrigin: "50% 10%" });
  const shk = lock.querySelector(".shk");
  const glow = el("div", null, null, cab, { position: "absolute", left: "10px", right: "10px", top: "-40px", height: "150px",
    background: "radial-gradient(ellipse at 50% 70%, rgba(255,40,40,0.95), rgba(255,0,0,0) 70%)", filter: "blur(10px)", opacity: 0, mixBlendMode: "screen" });
  tl.fromTo(cab, { opacity: 0, y: 500 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, 36.45);
  [39.8, 40.0].forEach((t) => [-14, 14, -10, 8, 0].forEach((r, k) => tl.to(lock, { rotation: r, duration: 0.035 }, t + k * 0.035)));
  tl.to(shk, { y: -26, duration: 0.08, ease: "power4.out" }, 40.25);
  tl.to(lock, { y: 260, rotation: 35, opacity: 0, duration: 0.4, ease: "power2.in" }, 40.38);
  tl.to(top, { scale: 1.1, y: 26, duration: 0.3, ease: "back.out(1.6)" }, 40.3);
  tl.to(glow, { opacity: 1, duration: 0.25 }, 40.32);
  tl.to(cab, { opacity: 0, y: 120, duration: 0.2, ease: "power2.in" }, 40.6);

  // ================= SHOT 10 (40.78 – 54.2): 5 saaye =================
  const SUS = ["G_RAMU", "C001_ANJALI", "C007_VIKRAM", "C002_RIYA_CUT", "C010_MAHESH"];
  const XS = [120, 330, 540, 750, 960];
  const row = el("div", "layer", null, A, { opacity: 0 });
  el("div", null, null, row, { position: "absolute", left: 0, right: 0, top: "560px", height: "760px",
    background: "radial-gradient(ellipse at 50% 70%, rgba(170,180,210,0.20), rgba(0,0,0,0) 65%)" });
  const kglow = el("div", null, null, row, { position: "absolute", left: "290px", top: "520px", width: "500px", height: "760px",
    background: "radial-gradient(ellipse at 50% 55%, rgba(229,57,53,0.85), rgba(229,57,53,0) 65%)", opacity: 0 });
  const sil = SUS.map((id, k) => {
    const w = el("div", null, null, row, { position: "absolute", left: XS[k] - 150 + "px", width: "300px", top: "700px", height: "540px",
      display: "flex", justifyContent: "center", alignItems: "flex-end" });
    const im = el("img", null, null, w, { height: "520px", filter: "brightness(0) drop-shadow(0 0 5px rgba(229,57,53,0.55))" });
    im.src = "assets/" + id + ".png";
    const q = el("div", null, "?", row, { position: "absolute", left: XS[k] - 60 + "px", width: "120px", top: "560px", textAlign: "center",
      fontSize: "110px", color: RED, WebkitTextStroke: "10px #111", paintOrder: "stroke fill" });
    const tick = el("div", null, "&#10004;", row, { position: "absolute", left: XS[k] - 60 + "px", width: "120px", top: "578px", textAlign: "center",
      fontSize: "100px", color: "#2ecc40", opacity: 0, fontFamily: "'Segoe UI Symbol', Arial, sans-serif", textShadow: "0 0 8px #000" });
    return { w, q, tick };
  });
  tl.to(row, { opacity: 1, duration: 0.3 }, 40.8);
  sil.forEach(({ w, q }, k) => {
    tl.fromTo(w, { y: 140, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: "power3.out" }, 40.85 + k * 0.1);
    tl.fromTo(q, { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.5)" }, 41.2 + k * 0.1);
    tl.to(q, { scale: 1.18, duration: 0.5, yoyo: true, repeat: 1, ease: "sine.inOut" }, 41.6 + k * 0.08);
    tl.to(q, { scale: 1.35, duration: 0.1, yoyo: true, repeat: 7, ease: "sine.inOut" }, 43.46);
  });
  const glint = el("div", null, "&#10022;", A, { position: "absolute", left: "930px", top: "1160px", fontSize: "70px", color: YEL,
    textShadow: "0 0 20px " + YEL, opacity: 0 });
  tl.fromTo(glint, { opacity: 0, scale: 0.2, rotation: 0 }, { opacity: 1, scale: 1.1, rotation: 45, duration: 0.1 }, 45.42);
  tl.to(glint, { opacity: 0, scale: 0.3, duration: 0.1 }, 45.52);
  [[0, 48.85], [4, 49.45], [1, 49.96], [3, 50.38]].forEach(([k, t]) => {
    tl.to(sil[k].q, { opacity: 0, scale: 0.3, duration: 0.12 }, t);
    tl.fromTo(sil[k].tick, { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2.5)" }, t + 0.1);
    tl.to(sil[k].w, { opacity: 0, y: 40, duration: 0.45, ease: "power2.in" }, t + 0.25);
    tl.to(sil[k].tick, { opacity: 0, duration: 0.2 }, t + 0.6);
  });
  tl.to(sil[2].q, { scale: 1.7, duration: 0.4, ease: "back.out(2)" }, 51.36);
  tl.to(row, { scale: 1.22, transformOrigin: "50% 62%", duration: 1.8, ease: "power2.inOut" }, 51.36);
  tl.to(kglow, { opacity: 1, duration: 0.35 }, 53.25);
  tl.to(sil[2].q, { scale: 2.0, duration: 0.15, yoyo: true, repeat: 1 }, 53.25);
  tl.to(row, { opacity: 0, duration: 0.25 }, 54.0);

  // ================= SHOT 11 (54.26 – 58.5): arms crossed + comment box =================
  const arms = el("div", null, null, A, { position: "absolute", left: "690px", top: "330px", height: "920px", opacity: 0 });
  const aim = el("img", null, null, arms, { display: "block", height: "100%" });
  aim.src = "assets/S2_07.png";
  tl.fromTo(arms, { opacity: 0, x: 500 }, { opacity: 1, x: 0, duration: 0.45, ease: "power4.out" }, 54.3);
  const SANS = "'Segoe UI', Arial, sans-serif";
  const posted = el("div", null, null, A, { position: "absolute", left: "40px", top: "560px", width: "640px", height: "150px", opacity: 0,
    background: "rgba(22,22,28,0.95)", borderRadius: "26px", fontFamily: SANS, color: "#fff", boxShadow: "0 14px 30px rgba(0,0,0,0.5)" });
  el("div", null, null, posted, { position: "absolute", left: "22px", top: "22px", width: "72px", height: "72px", borderRadius: "50%",
    background: "radial-gradient(circle at 50% 38%, #e0e0e6 0 15px, #4c6ef5 16px)" });
  el("div", null, "tum <span style='color:#8e8e96;font-weight:400'>&nbsp;abhi</span>", posted, { position: "absolute", left: "112px", top: "16px", fontSize: "28px", fontWeight: 700 });
  el("div", null, "Main taiyaar hoon &#9995;", posted, { position: "absolute", left: "112px", top: "56px", fontSize: "44px", fontWeight: 700 });
  el("div", null, "&#10084;", posted, { position: "absolute", right: "26px", top: "40px", fontSize: "44px", color: "#ff3040" });
  const box = el("div", null, null, A, { position: "absolute", left: "40px", top: "760px", width: "640px", height: "130px", opacity: 0,
    background: "#121218", borderRadius: "65px", border: "3px solid #3a3a44", fontFamily: SANS, boxShadow: "0 18px 40px rgba(0,0,0,0.6)" });
  el("div", null, null, box, { position: "absolute", left: "20px", top: "22px", width: "80px", height: "80px", borderRadius: "50%",
    background: "radial-gradient(circle at 50% 38%, #e0e0e6 0 16px, #4c6ef5 17px)" });
  const ph = el("div", null, "Add a comment...", box, { position: "absolute", left: "122px", top: "38px", fontSize: "40px", color: "#77777f" });
  const typed = el("div", null, null, box, { position: "absolute", left: "122px", top: "36px", fontSize: "42px", color: "#fff", fontWeight: 700, whiteSpace: "nowrap" });
  const send = el("div", null, '<svg width="44" height="44" viewBox="0 0 24 24"><path d="M3 11.5 21 3l-8.5 18-2.2-7.3L3 11.5z" fill="#fff"/></svg>', box,
    { position: "absolute", right: "16px", top: "16px", width: "96px", height: "96px", borderRadius: "50%", background: "#3797f0",
      display: "flex", alignItems: "center", justifyContent: "center" });
  tl.fromTo(box, { opacity: 0, y: 120 }, { opacity: 1, y: 0, duration: 0.4, ease: "back.out(1.8)" }, 54.5);
  tl.set(ph, { opacity: 0 }, 56.4);
  const TYP = "Main taiyaar hoon ✋";
  Array.from(TYP).forEach((c, k) => {
    const s = el("span", null, c === " " ? "&nbsp;" : c, typed, { opacity: 0 });
    tl.set(s, { opacity: 1 }, 56.45 + k * 0.05);
  });
  const caret = el("span", null, "|", typed, { color: "#3797f0", fontWeight: 400 });
  for (let t = 54.9; t < 57.9; t += 0.5) { tl.set(caret, { opacity: 0 }, t + 0.25); tl.set(caret, { opacity: 1 }, t + 0.5); }
  tl.to(send, { scale: 0.8, duration: 0.08 }, 57.85);
  tl.to(send, { scale: 1, duration: 0.15, ease: "back.out(3)" }, 57.93);
  tl.set([typed], { opacity: 0 }, 58.0);
  tl.set(ph, { opacity: 1 }, 58.0);
  tl.fromTo(posted, { opacity: 0, y: 160, scale: 0.8 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(2)" }, 57.95);
  tl.to([arms, box, posted], { opacity: 0, duration: 0.2 }, 58.45);

  // ================= SHOT 12 (58.57 – 61.7) + END CTA (61.7 – 62.7) =================
  const eyes = bust("S2_16", { left: "233px", top: "400px", height: "760px" });
  tl.fromTo(eyes, { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.45, ease: "power2.out" }, 58.57);
  tl.fromTo(eyes, { y: 0 }, { y: -12, duration: 1.5, yoyo: true, repeat: 1, ease: "sine.inOut" }, 59.0);
  const hc = big("SOMWAR SE<br>HARD CASES", { top: "300px", fontSize: "92px", color: YEL, WebkitTextStroke: "12px #111" });
  tl.fromTo(hc, { opacity: 0, scale: 2, rotation: -4 }, { opacity: 1, scale: 1, rotation: -2, duration: 0.22, ease: "power4.in" }, 58.62);
  const tag = big("Shivam ki nazar se koi nahi bachta.", { top: "1170px", fontSize: "50px", color: "#fff", WebkitTextStroke: "8px #111" });
  tl.fromTo(tag, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, 59.3);
  tl.to([eyes, hc, tag], { opacity: 0, duration: 0.2 }, 61.62);
  const cta1 = big("Comment karo:", { top: "640px", fontSize: "96px", color: "#fff" });
  const cta2 = big("MAIN<br>TAIYAAR<br>HOON", { top: "780px", fontSize: "150px", color: YEL, WebkitTextStroke: "14px #111" });
  const brand = el("div", null, '<img src="assets/LOGO_ROUND.png" style="width:120px;height:120px"/><span style="font-size:56px;color:#fff">@theshivamiq</span>', A,
    { position: "absolute", left: 0, right: 0, top: "1300px", display: "flex", justifyContent: "center", alignItems: "center", gap: "22px", opacity: 0 });
  tl.fromTo(cta1, { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }, 61.72);
  tl.fromTo(cta2, { opacity: 0, scale: 1.8 }, { opacity: 1, scale: 1, duration: 0.22, ease: "power4.in" }, 61.8);
  tl.to(cta2, { scale: 1.05, duration: 0.3, yoyo: true, repeat: 1, ease: "sine.inOut" }, 62.05);
  tl.to(brand, { opacity: 1, duration: 0.25 }, 61.9);
};
