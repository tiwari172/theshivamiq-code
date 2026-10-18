// ANN Detective Points – khaas scenes (engine ka optional EXTRA). Time = voice time (OFF 0).
const EXTRA = function (tl, H) {
  const { el, $, rnd } = H;
  const RED = "#E53935", YEL = "#FFD400", GOLD = "#F5C542", GREEN = "#2ecc71", TGBLUE = "#2AABEE";
  const SANS = "'Segoe UI', Arial, sans-serif";
  const A = el("div", "layer", null, null);
  A.id = "ann";
  $("cam").insertBefore(A, $("black"));
  const shake = (t, px) => {
    for (let k = 0; k < 6; k++)
      tl.to(A, { x: k === 5 ? 0 : (px || 14) * (1 - k / 6) * (k % 2 ? -1 : 1), duration: 0.035, ease: "none" }, t + k * 0.035);
  };
  const flash = (t, o) => tl.fromTo("#flash", { opacity: o || 0.7 }, { opacity: 0, duration: 0.35, ease: "power2.out" }, t);
  const redflash = (t) => tl.fromTo("#redflash", { opacity: 0.5 }, { opacity: 0, duration: 0.4, ease: "power2.out" }, t);
  const gone = (nodes, t, d) => tl.to(nodes, { opacity: 0, duration: d || 0.15 }, t);

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
  tl.fromTo(A, { scale: 1 }, { scale: 1.02, duration: 2, ease: "sine.inOut", yoyo: true, repeat: Math.floor(END / 2) }, 0);

  const big = (html, css, parent) => el("div", null, html, parent || A, Object.assign({
    position: "absolute", left: "40px", right: "40px", textAlign: "center", lineHeight: 1.05,
    WebkitTextStroke: "12px #111", paintOrder: "stroke fill", opacity: 0,
  }, css));
  const slam = (node, t, rot, from) => tl.fromTo(node, { opacity: 0, scale: from || 2.4, rotation: (rot || 0) - 5 },
    { opacity: 1, scale: 1, rotation: rot || 0, duration: 0.2, ease: "power4.in" }, t);
  const pulse = (node, t, n, s) => tl.to(node, { scale: s || 1.05, duration: 0.3, yoyo: true, repeat: n || 1, ease: "sine.inOut" }, t);
  const typeIn = (node, text, t, rate, css) => {
    const spans = [];
    Array.from(text).forEach((c, k) => {
      if (c === "|") { el("br", null, null, node); return; }
      const s = el("span", null, c === " " ? "&nbsp;" : c, node, Object.assign({ opacity: 0 }, css || {}));
      tl.set(s, { opacity: 1 }, t + k * (rate || 0.05));
      spans.push(s);
    });
    return spans;
  };
  // number counter: alag span har value ke liye (deterministic)
  const counter = (parent, vals, t0, t1, css, fmt) => {
    const box = el("div", null, null, parent, Object.assign({ position: "absolute", opacity: 0 }, css));
    const spans = vals.map((v) => el("span", null, fmt ? fmt(v) : String(v), box, { position: "absolute", left: 0, right: 0, opacity: 0 }));
    const step = (t1 - t0) / Math.max(1, vals.length - 1);
    spans.forEach((s, k) => {
      tl.set(s, { opacity: 1 }, t0 + k * step);
      if (k < spans.length - 1) tl.set(s, { opacity: 0 }, t0 + (k + 1) * step);
    });
    return box;
  };
  const range = (a, b) => Array.from({ length: b - a + 1 }, (_, k) => a + k);
  const black = el("div", "layer", null, A, { background: "#000", opacity: 0 });
  const bust = (src, css, fade) => {
    const w = el("div", null, null, A, Object.assign({ position: "absolute", opacity: 0 }, css));
    const im = el("img", null, null, w, { display: "block", height: "100%" });
    if (fade !== false) Object.assign(im.style, { WebkitMaskImage: "linear-gradient(180deg, #000 70%, rgba(0,0,0,0) 98%)",
      maskImage: "linear-gradient(180deg, #000 70%, rgba(0,0,0,0) 98%)" });
    im.src = "assets/" + src + ".png";
    return w;
  };
  const GRUNGE = "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='g'><feTurbulence baseFrequency='0.06' numOctaves='3' seed='4'/><feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -3.2 0 0 0 2.5'/></filter><rect width='100%' height='100%' filter='url(%23g)'/></svg>\")";
  const stampBox = (txt, size, top, color) => {
    const c = color || RED;
    const w = el("div", null, null, A, { position: "absolute", left: 0, right: 0, top: top + "px", display: "flex", justifyContent: "center", opacity: 0 });
    el("div", null, txt, w, { fontSize: size + "px", color: c, border: Math.round(size / 9) + "px solid " + c, borderRadius: "18px",
      padding: "6px 34px 12px", letterSpacing: "5px", background: "rgba(12,6,4,0.85)", WebkitMaskImage: GRUNGE, maskImage: GRUNGE,
      WebkitMaskSize: "240px 240px", textShadow: "0 0 2px " + c, textAlign: "center", lineHeight: 1.1 });
    return w;
  };
  const confetti = (t, n, cx, cy) => {
    const COLS = [GOLD, YEL, "#fff", RED, "#ffe9a8"];
    for (let k = 0; k < n; k++) {
      const p = el("div", null, null, A, { position: "absolute", left: cx + "px", top: cy + "px", width: 10 + Math.round(rnd() * 12) + "px",
        height: 18 + Math.round(rnd() * 16) + "px", background: COLS[k % COLS.length], borderRadius: "3px", opacity: 0 });
      const ang = rnd() * Math.PI * 2, sp = 260 + rnd() * 520;
      const dx = Math.cos(ang) * sp, dy = Math.sin(ang) * sp * 0.7 - 260;
      tl.set(p, { opacity: 1 }, t);
      tl.fromTo(p, { x: 0, y: 0, rotation: 0 }, { x: dx, y: dy, rotation: rnd() * 720 - 360, duration: 0.55, ease: "power3.out" }, t);
      tl.to(p, { y: dy + 700 + rnd() * 400, rotation: "+=" + Math.round(rnd() * 540), duration: 1.6, ease: "power1.in" }, t + 0.55);
      tl.to(p, { opacity: 0, duration: 0.3 }, t + 1.85);
    }
  };
  const avatarSvg = (fill) => `<svg width="100%" height="100%" viewBox="0 0 100 100"><circle cx="50" cy="38" r="20" fill="${fill}"/><path d="M14 96 C16 66, 84 66, 86 96 Z" fill="${fill}"/></svg>`;

  // ---------- common: gold score counter (upar right) ----------
  const ptsBox = el("div", null, null, A, { position: "absolute", right: "50px", top: "300px", width: "300px", height: "110px", borderRadius: "56px",
    background: "linear-gradient(180deg,#3a2c08,#1a1404)", border: "6px solid " + GOLD, boxShadow: "0 0 30px rgba(245,197,66,.5)", opacity: 0 });
  el("div", null, "⭐", ptsBox, { position: "absolute", left: "22px", top: "18px", fontSize: "56px", fontFamily: "'Segoe UI Emoji', " + SANS });
  const pspans = [0, 10, 11].map((v) => el("div", null, v + " <span style='font-size:36px'>PTS</span>", ptsBox, { position: "absolute", left: "90px",
    right: "16px", top: "16px", textAlign: "center", fontSize: "58px", whiteSpace: "nowrap", color: GOLD, WebkitTextStroke: "8px #111", paintOrder: "stroke fill", opacity: 0 }));
  const setPts = (k, t) => {
    pspans.forEach((s, j) => tl.set(s, { opacity: j === k ? 1 : 0 }, t));
    tl.fromTo(ptsBox, { scale: 1.25 }, { scale: 1, duration: 0.3, ease: "back.out(2.5)" }, t);
  };
  setPts(0, 0.02);
  tl.fromTo(ptsBox, { opacity: 0, x: 200 }, { opacity: 1, x: 0, duration: 0.3, ease: "back.out(2)" }, 1.2);

  // ================= L1 (0 – 3.35): Somvaar se... KEEMAT =================
  tl.set(black, { opacity: 1 }, 0);
  const flick = el("div", "layer", null, A, { background: "radial-gradient(ellipse at 50% 40%, rgba(255,214,120,0.30), rgba(0,0,0,0) 70%)", opacity: 0 });
  [[0.06, 0.6], [0.14, 0], [0.28, 0.75], [0.4, 0.1], [0.52, 0.45], [3.3, 0]].forEach(([t, o]) => tl.set(flick, { opacity: o }, t));
  const s1 = big("", { top: "620px", fontSize: "110px", color: "#fff", opacity: 1 });
  typeIn(s1, "SOMVAAR SE...", 0.08, 0.06);
  const s1b = big("HAR COMMENT KI<br><span style='color:" + GOLD + ";font-size:170px'>KEEMAT</span>", { top: "820px", fontSize: "90px", color: "#fff" });
  slam(s1b, 1.16, -2, 2);
  tl.to(s1b.querySelector("span"), { scale: 1.12, duration: 0.15, yoyo: true, repeat: 1 }, 2.23);
  shake(2.3, 16);
  gone([s1, s1b], 3.25);
  tl.to(black, { opacity: 0, duration: 0.2 }, 3.3);

  // ================= L2 (3.46 – 4.55): DETECTIVE POINTS + sikke =================
  const dp1 = big("DETECTIVE", { top: "620px", fontSize: "150px", color: "#fff", WebkitTextStroke: "16px #111" });
  const dp2 = big("POINTS", { top: "790px", fontSize: "250px", color: GOLD, WebkitTextStroke: "18px #111" });
  slam(dp1, 3.46, -2);
  slam(dp2, 3.79, -3, 2.8);
  shake(3.99, 24);
  flash(3.99, 0.6);
  for (let k = 0; k < 18; k++) {
    const c = el("div", null, "P", A, { position: "absolute", left: "500px", top: "900px", width: "80px", height: "80px", borderRadius: "50%",
      background: "radial-gradient(circle at 35% 30%, #fff3b0, " + GOLD + " 45%, #a67c00)", border: "4px solid #7a5a00", color: "#7a5a00",
      fontSize: "44px", textAlign: "center", lineHeight: "72px", opacity: 0 });
    const ang = (k / 18) * Math.PI * 2, r = 380 + rnd() * 160;
    tl.set(c, { opacity: 1 }, 3.99);
    tl.fromTo(c, { x: 0, y: 0, scale: 0.4, rotation: 0 }, { x: Math.cos(ang) * r, y: Math.sin(ang) * r * 0.9, scale: 1, rotation: rnd() * 360, duration: 0.45, ease: "power3.out" }, 3.99);
    tl.to(c, { opacity: 0, duration: 0.2 }, 4.45);
  }
  gone([dp1, dp2], 4.5);

  // ================= L3 (4.6 – 8.8): Sahi +10, Galat +1 =================
  const bub = (txt, top, t) => {
    const b = el("div", null, null, A, { position: "absolute", left: "60px", top: top + "px", width: "620px", height: "140px", opacity: 0,
      background: "rgba(22,22,28,0.96)", borderRadius: "26px", fontFamily: SANS, color: "#fff", boxShadow: "0 14px 30px rgba(0,0,0,0.5)" });
    el("div", null, null, b, { position: "absolute", left: "22px", top: "22px", width: "72px", height: "72px", borderRadius: "50%",
      background: "radial-gradient(circle at 50% 38%, #e0e0e6 0 15px, #6b6f7b 16px)" });
    el("div", null, 'user_<span style="filter:blur(6px)">k7x</span>', b, { position: "absolute", left: "112px", top: "14px", fontSize: "28px", fontWeight: 700, color: "#ccc" });
    el("div", null, txt, b, { position: "absolute", left: "112px", top: "54px", fontSize: "48px", fontWeight: 700 });
    tl.fromTo(b, { opacity: 0, x: -500 }, { opacity: 1, x: 0, duration: 0.3, ease: "power4.out" }, t);
    return b;
  };
  const tag = (txt, bg, left, top, t) => {
    const n = el("div", null, txt, A, { position: "absolute", left: left + "px", top: top + "px", fontSize: "56px", color: "#111", background: bg,
      padding: "4px 22px 10px", borderRadius: "16px", border: "5px solid #111", opacity: 0 });
    tl.fromTo(n, { opacity: 0, scale: 2.2, rotation: -10 }, { opacity: 1, scale: 1, rotation: -4, duration: 0.18, ease: "power4.in" }, t);
    return n;
  };
  const fly = (txt, x, y, t, size) => {
    const n = el("div", null, txt, A, { position: "absolute", left: x + "px", top: y + "px", fontSize: (size || 110) + "px", color: GOLD,
      WebkitTextStroke: "12px #111", paintOrder: "stroke fill", opacity: 0 });
    tl.fromTo(n, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1.2, duration: 0.2, ease: "back.out(2)" }, t);
    tl.to(n, { left: "830px", top: "290px", scale: 0.4, duration: 0.4, ease: "power2.in" }, t + 0.3);
    tl.set(n, { opacity: 0 }, t + 0.7);
    return n;
  };
  const b1 = bub("Kallu", 700, 4.6);
  const t1 = tag("✓ SAHI", GREEN, 720, 734, 5.0);
  fly("+10", 760, 560, 5.44);
  setPts(1, 6.14);
  const b2 = bub("Pintu", 900, 6.53);
  const t2 = tag("✗ GALAT", "#ff6b6b", 720, 934, 6.91);
  fly("+1", 790, 780, 7.37, 90);
  setPts(2, 8.07);
  gone([b1, b2, t1, t2], 8.75, 0.2);
  tl.to(ptsBox, { opacity: 0, x: 200, duration: 0.25, ease: "power2.in" }, 8.7);   // aage ke titles ke upar na aaye

  // ================= L4 + L5 (8.93 – 19.45): SPEED + stopwatch + seedhi =================
  const watch = el("div", null,
    `<svg width="420" height="480" viewBox="0 0 250 290"><rect x="105" y="0" width="40" height="30" rx="6" fill="#111"/><rect x="113" y="22" width="24" height="20" fill="#333"/>` +
    `<circle cx="125" cy="160" r="118" fill="#111"/><circle cx="125" cy="160" r="102" fill="#fff8e1"/>` +
    Array.from({ length: 12 }, (_, k) => `<line x1="125" y1="66" x2="125" y2="${k % 3 ? 76 : 84}" stroke="#111" stroke-width="${k % 3 ? 3 : 6}" transform="rotate(${k * 30} 125 160)"/>`).join("") +
    `<line class="hand" x1="125" y1="160" x2="125" y2="76" stroke="#e53935" stroke-width="8" stroke-linecap="round"/><circle cx="125" cy="160" r="11" fill="#111"/></svg>`,
    A, { position: "absolute", left: "330px", top: "470px", width: "420px", height: "480px", opacity: 0 });
  const hand = watch.querySelector(".hand");
  gsap.set(hand, { transformOrigin: "125px 160px" });
  gsap.set(watch, { transformOrigin: "50% 50%" });
  tl.fromTo(watch, { opacity: 0, scale: 0.3, rotation: -30 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2)" }, 8.93);
  tl.fromTo(hand, { rotation: 0 }, { rotation: 360 * 5, duration: 2.4, ease: "none" }, 8.95);
  const spd = big("SPEED", { top: "1010px", fontSize: "190px", color: RED, WebkitTextStroke: "18px #111" });
  slam(spd, 10.61, -4, 2.8);
  shake(10.81, 20);
  redflash(10.81);
  gone(spd, 11.4);
  // ghadi chhoti hokar upar-left
  tl.to(watch, { left: "40px", top: "290px", scale: 0.42, duration: 0.4, ease: "power3.inOut" }, 11.45);
  tl.fromTo(hand, { rotation: 0 }, { rotation: 360, duration: 6, ease: "none" }, 13.2);
  const chipA = el("div", null, "POST + 1 MIN = GHADI START", A, { position: "absolute", left: "300px", top: "380px", fontSize: "44px", color: "#111", background: YEL,
    padding: "8px 26px 12px", borderRadius: "40px", border: "5px solid #111", boxShadow: "0 7px 0 #111", whiteSpace: "nowrap", opacity: 0 });
  tl.fromTo(chipA, { opacity: 0, x: 300 }, { opacity: 1, x: 0, duration: 0.3, ease: "back.out(2)" }, 11.6);
  tl.to(chipA, { opacity: 0, duration: 0.15 }, 14.45);
  const chipB = el("div", null, "SPEED BONUS", A, { position: "absolute", left: "330px", top: "380px", fontSize: "60px", color: "#111", background: GOLD,
    padding: "6px 30px 12px", borderRadius: "40px", border: "5px solid #111", boxShadow: "0 7px 0 #111", whiteSpace: "nowrap", opacity: 0 });
  slam(chipB, 14.57, -2, 1.8);
  const BARS = [["30s", 10, 14.57], ["1m", 8, 16.67], ["5m", 6, 18.0], ["15m", 4, 18.15], ["30m", 2, 18.3], ["1hr", 1, 18.45]];
  const BASE = 1180;
  const bars = BARS.map(([lab, p, t], k) => {
    const x = 70 + k * 160, h = 60 + p * 46;
    const col = k === 0 ? GOLD : k === 1 ? "#ffd86b" : "#9aa3ad";
    const bar = el("div", null, null, A, { position: "absolute", left: x + "px", top: BASE - h + "px", width: "130px", height: h + "px",
      borderRadius: "16px 16px 6px 6px", background: "linear-gradient(180deg," + col + ", #4a3a10)", border: "5px solid #111",
      transformOrigin: "50% 100%", opacity: 0 });
    const v = el("div", null, "+" + p, A, { position: "absolute", left: x - 20 + "px", width: "170px", top: BASE - h - 90 + "px", textAlign: "center",
      fontSize: k < 2 ? "76px" : "60px", color: col, WebkitTextStroke: "9px #111", paintOrder: "stroke fill", opacity: 0 });
    const l = el("div", null, lab, A, { position: "absolute", left: x - 20 + "px", width: "170px", top: BASE + 10 + "px", textAlign: "center",
      fontSize: "44px", color: "#fff", WebkitTextStroke: "7px #111", paintOrder: "stroke fill", opacity: 0 });
    tl.fromTo(bar, { opacity: 1, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: 0.35, ease: "back.out(1.6)" }, t);
    tl.fromTo([v, l], { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.2 }, t + 0.2);
    return [bar, v, l];
  });
  tl.to(bars[0][0], { boxShadow: "0 0 50px " + GOLD, duration: 0.2, yoyo: true, repeat: 3 }, 15.8);
  pulse(bars[0][1], 15.8, 1, 1.2);
  gone([watch, chipB, ...bars.flat()], 19.4, 0.2);

  // ================= L6 (19.66 – 23.5): sirf PEHLA comment =================
  const lp = el("div", null, "PEHLA COMMENT", A, { position: "absolute", left: "60px", top: "620px", fontSize: "44px", color: YEL, WebkitTextStroke: "7px #111", paintOrder: "stroke fill", opacity: 0 });
  const w1 = bub("1", 680, 19.7);
  tl.to(lp, { opacity: 1, duration: 0.2 }, 19.75);
  const ld = el("div", null, "DOOSRA COMMENT", A, { position: "absolute", left: "60px", top: "860px", fontSize: "44px", color: "#aaa", WebkitTextStroke: "7px #111", paintOrder: "stroke fill", opacity: 0 });
  const w2 = bub("3", 920, 20.3);
  tl.to(ld, { opacity: 1, duration: 0.2 }, 20.35);
  tl.to(w2, { opacity: 0.45, filter: "grayscale(1)", duration: 0.2 }, 20.83);
  const ng = el("div", null, "NAHI GINA", A, { position: "absolute", left: "600px", top: "950px", fontSize: "56px", whiteSpace: "nowrap", color: RED, border: "7px solid " + RED,
    borderRadius: "14px", padding: "2px 18px 8px", background: "rgba(12,4,4,0.85)", WebkitMaskImage: GRUNGE, maskImage: GRUNGE, WebkitMaskSize: "240px 240px", opacity: 0 });
  tl.fromTo(ng, { opacity: 0, scale: 2.2, rotation: 0 }, { opacity: 1, scale: 1, rotation: -8, duration: 0.16, ease: "back.out(1.4)" }, 20.86);
  const x1 = tag("✗ GALAT", "#ff6b6b", 720, 714, 22.17);
  const slash = el("div", null, null, A, { position: "absolute", left: "50px", top: "742px", width: "650px", height: "14px", background: RED,
    borderRadius: "7px", transformOrigin: "0 50%", opacity: 0 });
  tl.fromTo(slash, { opacity: 1, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.2, ease: "power2.out" }, 22.47);
  const gaya = stampBox("GAYA!", 190, 1030);
  tl.fromTo(gaya, { opacity: 0, scale: 2.6, rotation: -3 }, { opacity: 1, scale: 1, rotation: -9, duration: 0.16, ease: "back.out(1.4)" }, 23.09);
  shake(23.25, 24);
  redflash(23.25);
  gone([lp, ld, w1, w2, ng, x1, slash, gaya], 23.5, 0.15);

  // ================= L7 (23.63 – 27.95): podium 1-2-3 =================
  const p3t = big("PEHLE 3 SAHI", { top: "320px", fontSize: "100px", color: "#fff" });
  tl.fromTo(p3t, { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, 23.7);
  const POD = [{ x: 380, h: 380, m: "🥇", p: "+10", c: GOLD, t: 26.29 }, { x: 80, h: 280, m: "🥈", p: "+7", c: "#C9D1DA", t: 26.78 },
    { x: 680, h: 200, m: "🥉", p: "+5", c: "#CD7F32", t: 27.27 }];
  const pods = POD.map((d, k) => {
    const b = el("div", null, String([1, 2, 3][k]), A, { position: "absolute", left: d.x + "px", top: 1200 - d.h + "px", width: "320px", height: d.h + "px",
      background: "linear-gradient(180deg," + d.c + ", #2a2410)", border: "6px solid #111", borderRadius: "16px 16px 0 0", textAlign: "center",
      fontSize: "140px", color: "#111", lineHeight: d.h > 250 ? "200px" : "180px", transformOrigin: "50% 100%", opacity: 0 });
    const m = el("div", null, d.m, A, { position: "absolute", left: d.x + 100 + "px", top: 1200 - d.h - 140 + "px", fontSize: "110px",
      fontFamily: "'Segoe UI Emoji', " + SANS, opacity: 0 });
    const p = el("div", null, d.p, A, { position: "absolute", left: d.x + "px", width: "320px", top: 1200 - d.h - 250 + "px", textAlign: "center",
      fontSize: "96px", color: d.c, WebkitTextStroke: "11px #111", paintOrder: "stroke fill", opacity: 0 });
    tl.fromTo(b, { opacity: 1, scaleY: 0 }, { opacity: 1, scaleY: 1, duration: 0.4, ease: "back.out(1.5)" }, 24.0 + [0.2, 0, 0.4][k]);
    tl.fromTo(m, { opacity: 0, y: -200, rotation: -30 }, { opacity: 1, y: 0, rotation: 0, duration: 0.35, ease: "bounce.out" }, 24.7 + k * 0.15);
    tl.fromTo(p, { opacity: 0, scale: 2 }, { opacity: 1, scale: 1, duration: 0.18, ease: "power4.in" }, d.t);
    return [b, m, p];
  });
  gone([p3t, ...pods.flat()], 27.85, 0.2);

  // ================= L8 (28.07 – 34.85): streak calendar -> 1000 =================
  const cal = el("div", null, null, A, { position: "absolute", left: "90px", top: "470px", width: "900px", height: "660px", opacity: 0,
    background: "rgba(20,20,26,0.95)", borderRadius: "26px", border: "5px solid #444", boxShadow: "0 16px 30px rgba(0,0,0,.55)" });
  el("div", null, "S&nbsp;&nbsp;&nbsp;M&nbsp;&nbsp;&nbsp;T&nbsp;&nbsp;&nbsp;W&nbsp;&nbsp;&nbsp;T&nbsp;&nbsp;&nbsp;F&nbsp;&nbsp;&nbsp;S", cal,
    { position: "absolute", left: 0, right: 0, top: "20px", textAlign: "center", fontSize: "40px", color: "#888" });
  const cells = [];
  for (let k = 0; k < 35; k++) {
    const c = el("div", null, "<span style='opacity:0'>🔥</span>", cal, { position: "absolute", left: 40 + (k % 7) * 118 + "px", top: 90 + Math.floor(k / 7) * 112 + "px", width: "100px",
      height: "96px", borderRadius: "14px", background: "#2c2c34", display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: "50px", fontFamily: "'Segoe UI Emoji', " + SANS });
    cells.push(c);
  }
  tl.fromTo(cal, { opacity: 0, y: 300 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }, 28.07);
  cells.forEach((c, k) => {
    const t = 28.4 + k * 0.075;
    tl.set(c.firstChild, { opacity: 1 }, t);
    tl.to(c, { backgroundColor: "#5a2a08", duration: 0.05 }, t);
    tl.fromTo(c, { scale: 1.4 }, { scale: 1, duration: 0.15 }, t);
  });
  const MIL = [["5 DIN", "+15", 30.66, 330], ["30 DIN", "+100", 31.81, 330]];
  const chips = MIL.map(([a, b, t, top], k) => {
    const n = el("div", null, a + " <span style='color:" + GOLD + "'>" + b + "</span>", A, { position: "absolute", left: k ? "560px" : "90px", top: top + "px",
      fontSize: "64px", color: "#fff", background: "#1b1408", border: "5px solid " + GOLD, borderRadius: "40px", padding: "6px 28px 12px",
      WebkitTextStroke: "7px #111", paintOrder: "stroke fill", whiteSpace: "nowrap", opacity: 0 });
    tl.fromTo(n, { opacity: 0, scale: 2 }, { opacity: 1, scale: 1, duration: 0.18, ease: "power4.in" }, t);
    return n;
  });
  gone([cal, ...chips], 33.0, 0.2);
  const y365 = big("365 DIN", { top: "420px", fontSize: "130px", color: "#fff" });
  slam(y365, 33.1, -2, 2);
  const k1000 = big("1000", { top: "580px", fontSize: "330px", color: GOLD, WebkitTextStroke: "22px #111" });
  const kpts = big("POINTS", { top: "930px", fontSize: "110px", color: GOLD });
  slam(k1000, 33.99, -3, 3);
  tl.fromTo(kpts, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.25 }, 34.2);
  shake(34.19, 28);
  flash(34.19, 0.8);
  confetti(34.19, 50, 540, 760);
  gone([y365, k1000, kpts], 34.85, 0.2);

  // ================= L9 (34.93 – 38.75): follow +50, story +15 =================
  const ICONS = [
    ["Telegram", TGBLUE, '<svg viewBox="0 0 24 24" width="130" height="130"><circle cx="12" cy="12" r="11" fill="#fff"/><path d="M5.5 11.6l11.4-4.4c.5-.2 1 .1.8.9l-1.9 9c-.1.6-.5.8-1 .5l-2.9-2.1-1.4 1.3c-.2.2-.3.3-.6.3l.2-3 5.4-4.9c.2-.2 0-.3-.3-.1l-6.7 4.2-2.9-.9c-.6-.2-.6-.6.1-.8z" fill="#2AABEE"/></svg>'],
    ["YouTube", "#E52D27", '<svg viewBox="0 0 24 24" width="130" height="130"><rect x="1" y="4" width="22" height="16" rx="5" fill="#fff"/><path d="M10 8.5v7l6-3.5z" fill="#E52D27"/></svg>'],
    ["Instagram", "#C13584", '<svg viewBox="0 0 24 24" width="130" height="130"><rect x="2" y="2" width="20" height="20" rx="6" fill="none" stroke="#fff" stroke-width="2.4"/><circle cx="12" cy="12" r="4.6" fill="none" stroke="#fff" stroke-width="2.4"/><circle cx="17.6" cy="6.4" r="1.4" fill="#fff"/></svg>'],
  ];
  const icons = ICONS.map(([nm, bg, svg], k) => {
    const n = el("div", null, svg, A, { position: "absolute", left: 90 + k * 320 + "px", top: "470px", width: "260px", height: "260px", borderRadius: "50px",
      background: bg, border: "7px solid #111", boxShadow: "0 12px 0 #111", display: "flex", alignItems: "center", justifyContent: "center", opacity: 0 });
    tl.fromTo(n, { opacity: 0, scale: 0.2, rotation: -20 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2.4)" }, 34.93 + k * 0.17);
    return n;
  });
  const p50 = big("+50", { top: "780px", fontSize: "220px", color: GOLD, WebkitTextStroke: "18px #111" });
  slam(p50, 35.96, -3, 2.5);
  shake(36.16, 16);
  tl.to([...icons, p50], { y: -900, opacity: 0, duration: 0.35, ease: "power3.in" }, 36.6);
  const sph = el("div", null, null, A, { position: "absolute", left: "290px", top: "400px", width: "500px", height: "820px", borderRadius: "54px",
    background: "#111", padding: "16px", boxSizing: "border-box", boxShadow: "0 30px 50px rgba(0,0,0,.5)", opacity: 0 });
  const sscr = el("div", null, null, sph, { position: "relative", width: "100%", height: "100%", borderRadius: "40px", overflow: "hidden",
    background: "linear-gradient(160deg,#6a3df0,#e0457b 60%,#f7a341)" });
  for (let k = 0; k < 4; k++) el("div", null, null, sscr, { position: "absolute", left: 14 + k * 113 + "px", top: "14px", width: "100px", height: "6px", borderRadius: "3px", background: k ? "rgba(255,255,255,.4)" : "#fff" });
  el("div", null, "Aaj ka case solve kiya 🕵️", sscr, { position: "absolute", left: 0, right: 0, top: "200px", textAlign: "center", fontSize: "40px", color: "#fff",
    fontFamily: "'Segoe UI Emoji', " + SANS, fontWeight: 800, textShadow: "0 3px 8px rgba(0,0,0,.4)" });
  const stk = el("div", null, "@THESHIVAMIQ", sscr, { position: "absolute", left: "34px", top: "420px", fontSize: "44px", color: "#e0457b", background: "#fff",
    padding: "8px 24px 12px", borderRadius: "16px", fontFamily: SANS, fontWeight: 900, opacity: 0 });
  tl.fromTo(sph, { opacity: 0, y: 700 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 36.72);
  tl.fromTo(stk, { opacity: 0, scale: 2.4, rotation: 12 }, { opacity: 1, scale: 1, rotation: -6, duration: 0.2, ease: "back.out(2)" }, 37.18);
  const p15 = el("div", null, "+15 ROZ", A, { position: "absolute", left: "600px", top: "330px", fontSize: "70px", color: "#111", background: GOLD,
    padding: "6px 28px 12px", borderRadius: "40px", border: "5px solid #111", boxShadow: "0 7px 0 #111", whiteSpace: "nowrap", opacity: 0 });
  slam(p15, 38.17, 4, 2);
  gone([sph, p15], 38.7, 0.2);

  // ================= L10 (38.87 – 45.6): naye case ka time-table =================
  const kab = big("NAYE CASE KAB?", { top: "350px", fontSize: "90px", color: YEL, WebkitTextStroke: "13px #111" });
  slam(kab, 38.87, -2, 2);
  const tt = el("div", null, null, A, { position: "absolute", left: "60px", top: "520px", width: "960px", height: "520px", borderRadius: "30px", opacity: 0,
    background: "rgba(20,20,26,0.96)", border: "6px solid #555", boxShadow: "0 16px 30px rgba(0,0,0,.55)" });
  const row = (lab, top) => el("div", null, lab, tt, { position: "absolute", left: "40px", top: top + "px", fontSize: "64px", color: "#fff", WebkitTextStroke: "8px #111", paintOrder: "stroke fill" });
  const pill = (txt, left, top, t, c) => {
    const p = el("div", null, "⏰ " + txt, tt, { position: "absolute", left: left + "px", top: top + "px", fontSize: "56px", color: "#111", background: c,
      padding: "8px 24px 12px", borderRadius: "40px", border: "5px solid #111", fontFamily: "'Segoe UI Emoji', ShivBlack", opacity: 0 });
    tl.fromTo(p, { opacity: 0, scale: 2, y: -30 }, { opacity: 1, scale: 1, y: 0, duration: 0.2, ease: "back.out(2)" }, t);
    return p;
  };
  const r1 = row("SOM – SHUKRA", 40), r2 = row("SHANI – RAVI", 290);
  tl.fromTo(tt, { opacity: 0, y: 400 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }, 39.6);
  tl.fromTo(r1, { opacity: 0, x: -200 }, { opacity: 1, x: 0, duration: 0.25 }, 40.76);
  pill("8:00 AM", 40, 140, 42.09, YEL);
  pill("8:00 PM", 470, 140, 42.66, YEL);
  tl.fromTo(r2, { opacity: 0, x: -200 }, { opacity: 1, x: 0, duration: 0.25 }, 43.81);
  pill("9:00 AM", 40, 390, 44.4, "#7fd3ff");
  pill("9:00 PM", 470, 390, 44.76, "#7fd3ff");
  const bell = el("div", null, "🔔 <span style='font-size:54px'>NOTIFICATION ON!</span>", A, { position: "absolute", left: 0, right: 0, top: "1090px", textAlign: "center",
    fontSize: "80px", color: "#fff", WebkitTextStroke: "8px #111", paintOrder: "stroke fill", fontFamily: "'Segoe UI Emoji', ShivBlack", opacity: 0 });
  tl.fromTo(bell, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.25 }, 44.99);
  [-12, 12, -8, 8, 0].forEach((r, k) => tl.to(bell, { rotation: r, duration: 0.05 }, 45.1 + k * 0.05));
  gone([kab, tt, bell], 45.6, 0.2);

  // ================= L11 (45.77 – 50.8): TOP 3 partner stories + TOP 10 =================
  const t3 = big("TOP 3", { top: "290px", fontSize: "150px", color: GOLD, WebkitTextStroke: "16px #111" });
  slam(t3, 46.29, -3, 2.6);
  shake(46.49, 16);
  const mock = (k, t) => {
    const ph = el("div", null, null, A, { position: "absolute", left: 50 + k * 330 + "px", top: "480px", width: "310px", height: "560px", borderRadius: "34px",
      background: "#111", padding: "10px", boxSizing: "border-box", boxShadow: "0 20px 40px rgba(0,0,0,.6)", opacity: 0 });
    const sc = el("div", null, null, ph, { position: "relative", width: "100%", height: "100%", borderRadius: "26px", overflow: "hidden",
      background: "radial-gradient(ellipse at 50% 45%, #6a5212, #1a1404 70%)" });
    el("div", null, "PARTNER", sc, { position: "absolute", left: 0, right: 0, top: "20px", textAlign: "center", fontSize: "42px", color: GOLD, WebkitTextStroke: "6px #111", paintOrder: "stroke fill" });
    const im = el("img", null, null, sc, { position: "absolute", left: "70px", top: "80px", height: "290px" });
    im.src = "assets/S2_07.png";
    el("div", null, "#" + (k + 1), sc, { position: "absolute", left: "14px", top: "300px", fontSize: "60px", color: "#fff", WebkitTextStroke: "7px #111", paintOrder: "stroke fill" });
    el("div", null, "@tumhara_naam", sc, { position: "absolute", left: "10px", right: "10px", top: "400px", textAlign: "center", fontSize: "30px", color: "#fff",
      background: "#111", border: "3px solid " + GOLD, borderRadius: "12px", padding: "6px 0 8px", fontFamily: SANS, fontWeight: 900 });
    tl.fromTo(ph, { opacity: 0, y: 500, rotation: [-8, 0, 8][k] }, { opacity: 1, y: 0, rotation: [-4, 0, 4][k], duration: 0.4, ease: "back.out(1.6)" }, t);
    return ph;
  };
  const mocks = [mock(0, 47.2), mock(1, 47.5), mock(2, 47.81)];
  flash(47.81, 0.4);
  tl.to([...mocks, t3], { y: -900, opacity: 0, duration: 0.35, ease: "power3.in" }, 49.15);
  const t10 = big("TOP 10", { top: "290px", fontSize: "140px", color: "#fff" });
  slam(t10, 49.45, -2, 2);
  const lst = el("div", null, null, A, { position: "absolute", left: "200px", top: "500px", width: "680px", opacity: 0 });
  for (let k = 4; k <= 10; k++)
    el("div", null, "#" + k + "&nbsp;&nbsp;@ ? ? ? ? ?", lst, { fontSize: "50px", color: k % 2 ? "#ddd" : "#fff", background: "rgba(22,22,28,.92)", border: "3px solid #555",
      borderRadius: "14px", padding: "4px 24px 8px", marginBottom: "12px", fontFamily: SANS, fontWeight: 800 });
  tl.fromTo(lst, { opacity: 0, y: 200 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, 49.6);
  const men = el("div", null, "STORY MENTION 📢", A, { position: "absolute", left: 0, right: 0, top: "430px", textAlign: "center", fontSize: "52px", color: GOLD,
    fontFamily: "'Segoe UI Emoji', ShivBlack", WebkitTextStroke: "7px #111", paintOrder: "stroke fill", opacity: 0 });
  tl.fromTo(men, { opacity: 0, scale: 1.8 }, { opacity: 1, scale: 1, duration: 0.2 }, 50.35);
  gone([t10, lst, men], 50.8, 0.2);

  // ================= L12 (50.9 – 53.5): Telegram bot phone =================
  const phn = el("div", null, null, A, { position: "absolute", left: "240px", top: "290px", width: "600px", height: "930px", background: "#111",
    borderRadius: "70px", padding: "20px", boxSizing: "border-box", boxShadow: "0 30px 50px rgba(0,0,0,0.5), inset 0 0 0 4px #3a3a3a", opacity: 0 });
  const scr = el("div", null, null, phn, { position: "relative", width: "100%", height: "100%", borderRadius: "52px", overflow: "hidden",
    background: "linear-gradient(180deg,#cfe3c5,#a9cfa0)", fontFamily: SANS });
  const tbar = el("div", null, null, scr, { position: "absolute", left: 0, right: 0, top: 0, height: "150px", background: "#517DA2", color: "#fff" });
  el("div", null, "🕵️", tbar, { position: "absolute", left: "28px", top: "52px", width: "78px", height: "78px", borderRadius: "50%", background: "#2b2b33",
    display: "flex", alignItems: "center", justifyContent: "center", fontSize: "44px", fontFamily: "'Segoe UI Emoji', " + SANS });
  el("div", null, "Shivam Rank Bot", tbar, { position: "absolute", left: "124px", top: "54px", fontSize: "38px", fontWeight: 700 });
  el("div", null, "bot", tbar, { position: "absolute", left: "124px", top: "100px", fontSize: "26px", opacity: 0.8 });
  const m1 = el("div", null, "/rank", scr, { position: "absolute", right: "22px", top: "320px", padding: "16px 26px", borderRadius: "24px 24px 6px 24px",
    background: "#effdde", fontSize: "44px", color: "#111", opacity: 0, transformOrigin: "100% 100%" });
  const m2 = el("div", null, "🕵️ <b>@tum</b><br>⭐ Kul points: <b>128</b><br>📅 Is hafte: <b>46</b><br>🔥 Din streak: <b>6 din</b>", scr,
    { position: "absolute", left: "22px", right: "60px", top: "430px", padding: "18px 24px", borderRadius: "24px 24px 24px 6px", background: "#fff",
      fontSize: "38px", lineHeight: 1.4, color: "#111", opacity: 0, transformOrigin: "0% 100%", fontFamily: "'Segoe UI Emoji', " + SANS });
  tl.fromTo(phn, { opacity: 0, y: 700 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 50.92);
  tl.fromTo(m1, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2.5)" }, 51.74);
  tl.fromTo(m2, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }, 52.3);
  tl.to(phn, { opacity: 0, y: 300, duration: 0.25, ease: "power2.in" }, 53.45);

  // ================= L13 (53.81 – 56.4): ghadi CHALU... TAIYAAR? =================
  const pt = bust("S2_03", { left: "30px", top: "430px", height: "960px" });
  tl.fromTo(pt, { opacity: 0, x: -500 }, { opacity: 1, x: 0, duration: 0.4, ease: "power4.out" }, 53.82);
  const w3 = el("div", null, watch.innerHTML, A, { position: "absolute", left: "600px", top: "440px", width: "420px", height: "480px", opacity: 0 });
  gsap.set(w3, { scale: 0.75, transformOrigin: "50% 50%" });
  const h3 = w3.querySelector(".hand");
  gsap.set(h3, { transformOrigin: "125px 160px" });
  tl.fromTo(w3, { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 0.75, duration: 0.35, ease: "back.out(2)" }, 53.9);
  tl.to(w3, { y: 12, duration: 0.06, yoyo: true, repeat: 1 }, 54.44);
  tl.fromTo(h3, { rotation: 0 }, { rotation: 300, duration: 1.9, ease: "none" }, 54.5);
  const chalu = big("CHALU!", { top: "330px", left: "460px", right: "20px", fontSize: "110px", color: GREEN, WebkitTextStroke: "13px #111" });
  slam(chalu, 54.71, -4, 2);
  const tai = big("TAIYAAR?", { top: "900px", left: "420px", right: "30px", fontSize: "96px", color: YEL, WebkitTextStroke: "14px #111" });
  slam(tai, 55.62, -6, 2.6);
  shake(55.82, 20);
  gone([pt, w3, chalu, tai], 56.4, 0.2);

  // ================= L14 (56.5 – 59.7) signature + END CTA (59.72 – 60.72) =================
  tl.set(ptsBox, { opacity: 0 }, 56.45);
  const eyes = bust("S2_16", { left: "233px", top: "380px", height: "760px" });
  tl.fromTo(eyes, { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.45, ease: "power2.out" }, 56.5);
  tl.fromTo(eyes, { y: 0 }, { y: -12, duration: 1.4, yoyo: true, repeat: 1, ease: "sine.inOut" }, 56.9);
  const dpn = big("DETECTIVE POINTS", { top: "290px", fontSize: "88px", color: GOLD, WebkitTextStroke: "12px #111" });
  slam(dpn, 56.55, -2, 2);
  const tg2 = big("Shivam ki nazar se<br>koi nahi bachta.", { top: "1180px", fontSize: "64px", color: "#fff", WebkitTextStroke: "9px #111" });
  tl.fromTo(tg2, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, 56.8);
  gone([eyes, dpn, tg2], 59.62, 0.2);
  const e1 = big("HAR COMMENT =<br><span style='color:" + GOLD + "'>POINTS</span>", { top: "460px", fontSize: "88px", color: "#fff" });
  const e2 = big("Telegram:<br><span style='color:" + TGBLUE + "'>@Theshivamiq_rank_bot</span>", { top: "740px", fontSize: "70px", color: "#fff", WebkitTextStroke: "10px #111" });
  const brand = el("div", null, '<img src="assets/LOGO_ROUND.png" style="width:120px;height:120px"/><span style="font-size:56px;color:#fff">@theshivamiq</span>', A,
    { position: "absolute", left: 0, right: 0, top: "1000px", display: "flex", justifyContent: "center", alignItems: "center", gap: "22px", opacity: 0 });
  tl.fromTo(e1, { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }, 59.72);
  slam(e2, 59.8, -2, 1.8);
  tl.to(brand, { opacity: 1, duration: 0.25 }, 59.9);
};
