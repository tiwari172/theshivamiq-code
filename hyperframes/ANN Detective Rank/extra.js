// ANN Detective Rank – khaas scenes (engine ka optional EXTRA). Time = voice time (OFF 0).
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

  // ================= L1 (0 – 4.15): RUKO + typewriter + REC =================
  tl.set(black, { opacity: 1 }, 0);
  const flick = el("div", "layer", null, A, { background: "radial-gradient(ellipse at 50% 40%, rgba(200,215,255,0.32), rgba(0,0,0,0) 70%)", opacity: 0 });
  [[0.06, 0.6], [0.14, 0], [0.28, 0.75], [0.4, 0.1], [0.52, 0.45], [4.0, 0]].forEach(([t, o]) => tl.set(flick, { opacity: o }, t));
  const rec = el("div", null, '<span style="display:inline-block;width:34px;height:34px;border-radius:50%;background:#e53935;margin-right:16px;vertical-align:-4px"></span>REC', A,
    { position: "absolute", left: "70px", top: "300px", fontSize: "48px", color: "#fff", fontFamily: SANS, fontWeight: 800, opacity: 0 });
  for (let t = 0.1; t < 4.0; t += 0.5) { tl.set(rec, { opacity: 1 }, t); tl.set(rec, { opacity: 0.25 }, t + 0.25); }
  tl.set(rec, { opacity: 0 }, 4.05);
  const ruko = big("RUKO!", { top: "620px", fontSize: "200px", color: RED, WebkitTextStroke: "16px #111" });
  slam(ruko, 0.07, -3);
  shake(0.27, 14);
  tl.to(ruko, { opacity: 0, scale: 0.8, duration: 0.15 }, 0.95);
  const q1 = big("", { top: "560px", fontSize: "108px", color: "#fff", opacity: 1 });
  typeIn(q1, "TUMHARA HAR|COMMENT...", 1.03, 0.045);
  const gin = big("KOI <span style='color:" + RED + "'>GIN</span><br>RAHA THA", { top: "840px", fontSize: "130px", color: YEL, WebkitTextStroke: "14px #111" });
  slam(gin, 2.74, -2);
  shake(2.94, 12);
  pulse(gin, 3.1, 1, 1.04);
  gone([q1, gin], 4.0);
  tl.to(black, { opacity: 0, duration: 0.2 }, 4.05);

  // ================= L2 (4.27 – 7.9): asli comments + counter =================
  const COMMENTS = ["3", "Kallu", "Clerk nikhil", "Suraj🔥🔥🔥", "3 kallu😂", "Nikhil kyuki canteen 10 baje band tha",
    "Bhola", "Mahesh 3rd one", "Sharma Aunty", "Ramu"];
  const AV = ["#6d6f78", "#7b6a5a", "#5a6b7b", "#6b5a7b", "#5a7b6a", "#7b5a5a", "#6a6a6a", "#5f6f5a", "#6b6b7b", "#7b6b5a"];
  const cwrap = el("div", "layer", null, A);
  const BOT = 1210, GAP = 16;
  const items = COMMENTS.map((txt, k) => {
    const h = txt.length > 24 ? 196 : 146;
    const b = el("div", null, null, cwrap, {
      position: "absolute", left: "60px", width: "960px", height: h + "px", top: BOT - h + "px", opacity: 0,
      background: "rgba(22,22,28,0.94)", borderRadius: "28px", border: "2px solid rgba(255,255,255,0.08)",
      boxShadow: "0 14px 30px rgba(0,0,0,0.5)", fontFamily: SANS, color: "#fff" });
    el("div", null, null, b, { position: "absolute", left: "24px", top: "22px", width: "78px", height: "78px", borderRadius: "50%",
      background: "radial-gradient(circle at 50% 38%, #c9c9cf 0 17px, " + AV[k] + " 18px)" });
    el("div", null, 'user_<span style="filter:blur(7px)">k' + (k * 7 + 3) + 'x</span> <span style="color:#8e8e96;font-weight:400;font-size:26px">&nbsp;' + (k + 2) + "m</span>", b,
      { position: "absolute", left: "124px", top: "18px", fontSize: "28px", fontWeight: 700, color: "#d8d8de" });
    el("div", null, txt, b, { position: "absolute", left: "124px", right: "40px", top: "58px", fontSize: "44px", fontWeight: 700, lineHeight: 1.18 });
    return { b, h, t: 4.3 + k * 0.31 };
  });
  items.forEach((it, k) => {
    tl.fromTo(it.b, { opacity: 0, y: 200, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.9)" }, it.t);
    let off = 0;
    for (let j = k - 1; j >= 0; j--) {
      off += items[j + 1].h + GAP;
      tl.to(items[j].b, { y: -off, duration: 0.25, ease: "power3.out" }, it.t);
      if (BOT - items[j].h - off < 560) tl.to(items[j].b, { opacity: 0, duration: 0.2 }, it.t);
    }
  });
  const chip39 = el("div", null, "39 CASES", A, { position: "absolute", left: "50%", top: "300px", fontSize: "64px", color: "#111", background: YEL,
    padding: "8px 34px 12px", borderRadius: "50px", border: "6px solid #111", boxShadow: "0 8px 0 #111", opacity: 0, whiteSpace: "nowrap" });
  gsap.set(chip39, { xPercent: -50 });
  slam(chip39, 4.27, -2, 2);
  const cnt = counter(A, [0, 120, 480, 1100, 1900, 2800, 3700, 4500, 5200, 5800, 6300, 6700, 7000, 7180, 7275], 6.02, 7.47,
    { left: 0, right: 0, top: "410px", height: "140px", textAlign: "center", fontSize: "120px", color: "#fff", WebkitTextStroke: "13px #111", paintOrder: "stroke fill" },
    (v) => v.toLocaleString("en-IN") + "<span style='font-size:70px;color:" + YEL + "'> JAWAB</span>");
  tl.set(cnt, { opacity: 1 }, 6.02);
  tl.to(cnt, { scale: 1.12, duration: 0.15, yoyo: true, repeat: 1, ease: "power2.out" }, 7.47);
  tl.to(cwrap, { filter: "blur(10px)", scale: 0.9, opacity: 0, duration: 0.45, ease: "power2.in" }, 7.8);
  gone([chip39, cnt], 7.85, 0.2);

  // ================= L3 (7.94 – 11.95): cabinet + taala + DETECTIVE RANK =================
  const cab = el("div", null, null, A, { position: "absolute", left: "270px", top: "520px", width: "540px", height: "700px", opacity: 0,
    background: "linear-gradient(90deg,#3a3f46 0%,#5b626b 18%,#474d55 50%,#5b626b 82%,#353a40 100%)", borderRadius: "14px",
    boxShadow: "0 40px 70px rgba(0,0,0,0.75), inset 0 0 0 6px #2a2e33" });
  const drawers = [];
  for (let k = 0; k < 3; k++) {
    const d = el("div", null, null, cab, { position: "absolute", left: "28px", right: "28px", top: 28 + k * 222 + "px", height: "200px", borderRadius: "8px",
      background: "linear-gradient(180deg,#6b737d 0%,#4d545c 100%)", boxShadow: "inset 0 3px 0 rgba(255,255,255,0.18), inset 0 -4px 0 rgba(0,0,0,0.35), 0 4px 8px rgba(0,0,0,0.4)" });
    el("div", null, null, d, { position: "absolute", left: "175px", width: "134px", bottom: "28px", height: "26px", borderRadius: "13px",
      background: "linear-gradient(180deg,#c5ccd4,#7d858e)", boxShadow: "0 3px 4px rgba(0,0,0,0.5)" });
    drawers.push(d);
  }
  const top = drawers[0];
  el("div", null, "DETECTIVE RANK", top, { position: "absolute", left: "30px", top: "26px", width: "290px", textAlign: "center", fontSize: "30px",
    color: "#111", background: YEL, padding: "6px 4px 10px", borderRadius: "6px", border: "3px solid #111" });
  const lock = el("div", null,
    `<svg width="130" height="170" viewBox="0 0 130 170"><path class="shk" d="M 30 80 L 30 48 C 30 14, 100 14, 100 48 L 100 80" fill="none" stroke="#b9c0c8" stroke-width="16" stroke-linecap="round"/><rect x="8" y="72" width="114" height="92" rx="16" fill="#d4a017" stroke="#6b4e00" stroke-width="5"/><circle cx="65" cy="110" r="12" fill="#3a2a00"/><rect x="59" y="114" width="12" height="28" rx="4" fill="#3a2a00"/></svg>`,
    top, { position: "absolute", right: "22px", top: "10px", width: "130px", height: "170px", transformOrigin: "50% 10%" });
  const shk = lock.querySelector(".shk");
  const glow = el("div", null, null, cab, { position: "absolute", left: "10px", right: "10px", top: "-50px", height: "160px",
    background: "radial-gradient(ellipse at 50% 70%, rgba(255,214,0,0.95), rgba(255,214,0,0) 70%)", filter: "blur(10px)", opacity: 0, mixBlendMode: "screen" });
  tl.fromTo(cab, { opacity: 0, y: 500 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, 7.95);
  [8.76, 8.98].forEach((t) => [-14, 14, -10, 8, 0].forEach((r, k) => tl.to(lock, { rotation: r, duration: 0.035 }, t + k * 0.035)));
  tl.to(shk, { y: -26, duration: 0.08, ease: "power4.out" }, 9.3);
  tl.to(lock, { y: 260, rotation: 35, opacity: 0, duration: 0.4, ease: "power2.in" }, 9.42);
  tl.to(top, { scale: 1.1, y: 26, duration: 0.3, ease: "back.out(1.6)" }, 9.35);
  tl.to(glow, { opacity: 1, duration: 0.25 }, 9.38);
  tl.to(cab, { scale: 0.6, y: 380, opacity: 0, duration: 0.3, ease: "power2.in" }, 10.0);
  const dt1 = big("DETECTIVE", { top: "560px", fontSize: "150px", color: YEL, WebkitTextStroke: "16px #111" });
  const dt2 = big("RANK", { top: "730px", fontSize: "250px", color: RED, WebkitTextStroke: "18px #111" });
  slam(dt1, 10.13, -2);
  slam(dt2, 10.86, -2, 2.8);
  shake(11.06, 24);
  flash(11.06, 0.6);
  pulse([dt1, dt2], 11.3, 1, 1.04);
  gone([dt1, dt2], 11.85);

  // ================= L4 + L5 (12.0 – 17.45): rank ki seedhi (4 cards) =================
  const LAD = [
    { t: "JUNIOR DETECTIVE", s: "3 SAHI", c: "#CD7F32", ic: "★" },
    { t: "SENIOR DETECTIVE", s: "10 SAHI", c: "#C9D1DA", ic: "★★" },
    { t: "DETECTIVE OF THE WEEK", s: "HAFTE KA TOP", c: GOLD, ic: "🔍" },
    { t: "SHIVAM KA PARTNER", s: "SABSE AAGE", c: RED, ic: "👑" },
  ];
  const TOPS = [1010, 790, 570, 350];
  const lad = el("div", "layer", null, A);
  const cards = LAD.map((r, k) => {
    const c = el("div", null, null, lad, { position: "absolute", left: "70px", width: "940px", height: "190px", top: TOPS[k] + "px",
      borderRadius: "26px", background: "rgba(20,20,26,0.95)", border: "6px solid #444", boxShadow: "0 16px 30px rgba(0,0,0,0.55)", opacity: 0 });
    const ic = el("div", null, r.ic, c, { position: "absolute", left: "26px", top: "26px", width: "126px", height: "126px", borderRadius: "50%",
      background: "#333", color: "#111", fontSize: r.ic.length > 1 && r.ic[0] === "★" ? "44px" : "66px", display: "flex", alignItems: "center",
      justifyContent: "center", fontFamily: "'Segoe UI Emoji', 'Segoe UI Symbol', " + SANS });
    const tt = el("div", null, r.t, c, { position: "absolute", left: "176px", top: "34px", fontSize: [58, 58, 45, 55][k] + "px", color: "#777", whiteSpace: "nowrap" });
    const ss = el("div", null, r.s, c, { position: "absolute", left: "178px", top: "112px", fontSize: "38px", color: "#666", fontFamily: SANS, fontWeight: 800, letterSpacing: "2px" });
    const lk = el("div", null, k < 2 ? "🔒" : "?", c, { position: "absolute", right: "34px", top: "40px", fontSize: k < 2 ? "78px" : "100px",
      color: RED, fontFamily: "'Segoe UI Emoji', " + SANS, WebkitTextStroke: k < 2 ? "0" : "8px #111", paintOrder: "stroke fill" });
    tl.fromTo(c, { opacity: 0, x: 700 }, { opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }, 12.0 + (3 - k) * 0.07);
    return { c, ic, tt, ss, lk, r };
  });
  const unlock = (k, t) => {
    const x = cards[k];
    tl.to(x.lk, { y: -60, rotation: 30, opacity: 0, duration: 0.3, ease: "power2.in" }, t);
    tl.to(x.c, { borderColor: x.r.c, boxShadow: "0 0 40px " + x.r.c + ", 0 16px 30px rgba(0,0,0,0.55)", duration: 0.2 }, t + 0.05);
    tl.to(x.ic, { backgroundColor: x.r.c, duration: 0.2 }, t + 0.05);
    tl.to(x.tt, { color: "#fff", duration: 0.2 }, t + 0.05);
    tl.to(x.ss, { color: x.r.c, duration: 0.2 }, t + 0.05);
    tl.fromTo(x.c, { scale: 1.12 }, { scale: 1, duration: 0.4, ease: "back.out(2)" }, t + 0.05);
  };
  unlock(0, 12.05);
  pulse(cards[0].c, 13.56, 1, 1.05);
  unlock(1, 14.72);
  pulse(cards[1].c, 16.38, 1, 1.05);
  [cards[2].lk, cards[3].lk].forEach((n) => tl.to(n, { scale: 1.25, duration: 0.35, yoyo: true, repeat: 7, ease: "sine.inOut" }, 12.6));
  tl.to(lad, { x: -1100, skewX: 10, duration: 0.35, ease: "power3.in" }, 17.2);

  // ================= L6 (17.54 – 21.6): 14 SENIOR DETECTIVES ki wall =================
  const SEN = [["__tejas__13", 16], ["akash.sachdeva.186", 15], ["fumakiya__zain___ali", 14], ["je_mappelle_mansi", 13],
    ["chaosskabeerr", 13], ["mishrakripanidhan", 11], ["anshsoni.5131754", 10], ["exotic_.harsh09", 10], ["its__nayem__king", 10],
    ["sidd7440", 10], ["__itz_me__0786", 10], ["its_himanshu_panday_07", 10], ["?", 0], ["?", 0]];
  const wall = el("div", "layer", null, A, { opacity: 0 });
  const n14 = big("14", { top: "290px", fontSize: "230px", color: YEL, WebkitTextStroke: "18px #111" }, wall);
  const n14b = big("SENIOR DETECTIVES", { top: "520px", fontSize: "70px", color: "#fff" }, wall);
  const tiles = SEN.map(([nm, s], k) => {
    const col = k % 2, row = Math.floor(k / 2);
    const lock = nm === "?";
    const t = el("div", null, null, wall, { position: "absolute", left: (col ? 552 : 48) + "px", top: 640 + row * 84 + "px", width: "480px", height: "70px",
      borderRadius: "16px", background: lock ? "rgba(60,46,8,0.95)" : "rgba(22,22,28,0.95)", border: "3px solid " + (lock ? GOLD : "#C9D1DA"),
      fontFamily: SANS, color: "#fff", display: "flex", alignItems: "center", padding: "0 16px", boxSizing: "border-box", opacity: 0,
      boxShadow: "0 8px 16px rgba(0,0,0,0.5)" });
    if (lock) {
      el("span", null, "@ ? ? ? ? ? ? ?", t, { fontSize: "32px", fontWeight: 800, color: GOLD, filter: "blur(1px)", flex: 1, textAlign: "center", letterSpacing: "4px" });
      el("span", null, "🔒", t, { fontSize: "34px", fontFamily: "'Segoe UI Emoji', " + SANS });
    } else {
      el("span", null, "@" + nm, t, { fontSize: nm.length > 18 ? "27px" : "31px", fontWeight: 800, flex: 1, whiteSpace: "nowrap", overflow: "hidden" });
      el("span", null, s + "✓", t, { fontSize: "30px", fontWeight: 800, color: GREEN, marginLeft: "8px" });
    }
    tl.fromTo(t, { opacity: 0, y: -120, rotation: col ? 4 : -4, scale: 1.2 }, { opacity: 1, y: 0, rotation: 0, scale: 1, duration: 0.3, ease: "back.out(1.7)" },
      18.55 + k * 0.1);
    return { t, lock };
  });
  tl.set(wall, { opacity: 1 }, 17.55);
  slam(n14, 18.21, -3, 2.6);
  shake(18.41, 14);
  tl.fromTo(n14b, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.25 }, 18.5);
  tl.fromTo(wall, { scale: 1 }, { scale: 1.06, duration: 4, ease: "sine.inOut", transformOrigin: "50% 60%" }, 17.6);
  tiles.filter((x) => x.lock).forEach(({ t }) => tl.to(t, { scale: 1.08, boxShadow: "0 0 30px " + GOLD, duration: 0.25, yoyo: true, repeat: 3 }, 20.6));
  tl.to(wall, { opacity: 0, duration: 0.2 }, 21.55);

  // ================= L7 (21.77 – 24.95): blackout + laal dot + EK NAAM =================
  tl.to(black, { opacity: 1, duration: 0.15 }, 21.6);
  const dot = el("div", null, null, A, { position: "absolute", left: "522px", top: "1000px", width: "36px", height: "36px", borderRadius: "50%",
    background: RED, boxShadow: "0 0 40px 12px rgba(229,57,53,0.55)", opacity: 0 });
  tl.fromTo(dot, { opacity: 0.4, scale: 0.8 }, { opacity: 1, scale: 1.5, duration: 0.35, ease: "sine.inOut", yoyo: true, repeat: 3 }, 21.75);
  tl.to(dot, { opacity: 0, duration: 0.1 }, 23.1);
  const ish = big("", { top: "560px", fontSize: "104px", color: "#fff", opacity: 1 });
  typeIn(ish, "IS HAFTE...", 21.98, 0.07);
  const ekn = big("EK NAAM", { top: "740px", fontSize: "200px", color: RED, WebkitTextStroke: "18px #111" });
  slam(ekn, 23.15, -3, 2.8);
  shake(23.35, 22);
  redflash(23.35);
  const aage = big("SABSE AAGE", { top: "960px", fontSize: "96px", color: YEL });
  tl.fromTo(aage, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }, 23.76);
  gone([ish, ekn, aage], 24.8);
  tl.to(black, { opacity: 0, duration: 0.2 }, 24.85);

  // ================= L8 (24.98 – 29.75): mystery avatar + stats =================
  const av = el("div", null, null, A, { position: "absolute", left: "390px", top: "300px", width: "300px", height: "300px", opacity: 0 });
  const ringEl = el("div", null, null, av, { position: "absolute", inset: "-14px", borderRadius: "50%",
    background: "conic-gradient(" + GOLD + " 0 25%, rgba(0,0,0,0) 25% 50%, " + GOLD + " 50% 75%, rgba(0,0,0,0) 75%)" });
  const face = el("div", null, null, av, { position: "absolute", inset: 0, borderRadius: "50%", background: "#1b1b22", border: "6px solid #111", overflow: "hidden" });
  const sil = el("div", null, avatarSvg("#000"), face, { position: "absolute", inset: "8%" });
  const qq = el("div", null, "?", face, { position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "180px", color: GOLD, WebkitTextStroke: "12px #111", paintOrder: "stroke fill" });
  const initial = el("div", null, "C", face, { position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "170px", color: "#111", background: GOLD, opacity: 0 });
  tl.fromTo(av, { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)" }, 24.98);
  tl.to(ringEl, { rotation: 360 * 4, duration: 8, ease: "none" }, 24.98);
  tl.to(qq, { scale: 1.15, duration: 0.3, yoyo: true, repeat: 7, ease: "sine.inOut" }, 25.4);
  const STATS = [
    { t: 24.98, lab: "CASE", vals: range(0, 16), fmt: (v) => String(v), col: "#fff", t1: 25.6 },
    { t: 26.70, lab: "SAHI", vals: range(0, 16), fmt: (v) => v + "<span style='font-size:60px;color:#888'>/16</span>", col: GREEN, t1: 27.3 },
    { t: 28.11, lab: "STREAK 🔥", vals: range(0, 15), fmt: (v) => v + "<span style='font-size:52px;color:#ffb36b'> REELS</span>", col: "#ff8a3d", t1: 28.9 },
  ];
  const statBoxes = STATS.map((s, k) => {
    const b = el("div", null, null, A, { position: "absolute", left: "110px", width: "860px", height: "160px", top: 680 + k * 185 + "px",
      borderRadius: "24px", background: "rgba(20,20,26,0.95)", border: "5px solid " + (k === 1 ? GREEN : k === 2 ? "#ff8a3d" : "#888"), opacity: 0,
      boxShadow: "0 14px 26px rgba(0,0,0,0.5)" });
    el("div", null, s.lab, b, { position: "absolute", left: "36px", top: "46px", fontSize: "58px", color: "#bbb", fontFamily: "'Segoe UI Emoji', ShivBlack" });
    const c = counter(b, s.vals, s.t + 0.1, s.t1, { right: "40px", width: "460px", top: "22px", height: "120px", textAlign: "right",
      fontSize: "104px", color: s.col, WebkitTextStroke: "10px #111", paintOrder: "stroke fill" }, s.fmt);
    tl.set(c, { opacity: 1 }, s.t + 0.1);
    tl.fromTo(b, { opacity: 0, x: -900, skewX: 12 }, { opacity: 1, x: 0, skewX: 0, duration: 0.3, ease: "power4.out" }, s.t);
    tl.fromTo(b, { scale: 1 }, { scale: 1.06, duration: 0.12, yoyo: true, repeat: 1 }, s.t1);
    return b;
  });
  // streak ki aag
  const fire = el("div", null, null, statBoxes[2], { position: "absolute", inset: "-6px", borderRadius: "26px", opacity: 0,
    boxShadow: "0 0 40px 10px rgba(255,120,30,0.8)" });
  tl.to(fire, { opacity: 1, duration: 0.1 }, 28.9);
  for (let t = 29.0; t < 29.7; t += 0.12) tl.to(fire, { opacity: 0.45 + rnd() * 0.55, duration: 0.06 }, t);
  tl.to(statBoxes, { opacity: 0, x: 900, duration: 0.25, ease: "power2.in", stagger: 0.05 }, 29.55);

  // ================= L9 (29.88 – 32.95): DETECTIVE OF THE WEEK reveal =================
  const dw = big("DETECTIVE OF<br>THE WEEK", { top: "290px", fontSize: "112px", color: GOLD, WebkitTextStroke: "14px #111" });
  slam(dw, 29.88, -2, 2.4);
  shake(30.08, 14);
  tl.to(av, { y: 300, scale: 1.25, duration: 0.45, ease: "power3.inOut" }, 29.9);
  // flip: ? -> naam ka akshar
  tl.to(face, { scaleX: 0, duration: 0.12, ease: "power2.in" }, 31.1);
  tl.set([qq, sil], { opacity: 0 }, 31.22);
  tl.set(initial, { opacity: 1 }, 31.22);
  tl.to(face, { scaleX: 1, duration: 0.15, ease: "power2.out" }, 31.22);
  const plate1 = el("div", null, "@classy.pran_krishna", A, { position: "absolute", left: "50%", top: "1030px", fontSize: "70px", fontFamily: SANS,
    fontWeight: 900, color: "#fff", background: "#111", border: "6px solid " + GOLD, borderRadius: "22px", padding: "10px 34px 16px",
    whiteSpace: "nowrap", boxShadow: "0 0 40px rgba(245,197,66,0.6)", opacity: 0 });
  gsap.set(plate1, { xPercent: -50 });
  tl.fromTo(plate1, { opacity: 0, scale: 2.2 }, { opacity: 1, scale: 1, duration: 0.2, ease: "power4.in" }, 31.15);
  flash(31.35, 0.8);
  shake(31.35, 24);
  confetti(31.35, 46, 540, 800);
  pulse(plate1, 31.7, 2, 1.05);
  gone([dw, av, plate1], 32.85, 0.2);

  // ================= L10 (32.99 – 35.5): evidence board -> beech ka frame =================
  const board = el("div", null, null, A, { position: "absolute", left: 0, top: 0, width: "1080px", height: "1920px", opacity: 0 });
  gsap.set(board, { transformOrigin: "540px 820px" });
  el("div", null, null, board, { position: "absolute", left: "16px", top: "280px", width: "1048px", height: "1240px", borderRadius: "18px",
    background: "radial-gradient(ellipse at 50% 45%, #5a3d27 0%, #3d2818 70%, #2a1b10 100%)",
    boxShadow: "inset 0 0 0 14px #2b1d12, inset 0 0 80px rgba(0,0,0,0.7), 0 20px 60px rgba(0,0,0,0.6)" });
  const POS = [[60, 330], [300, 310], [560, 330], [810, 320], [50, 620], [830, 610], [60, 930], [840, 930], [70, 1200], [300, 1230], [570, 1220], [820, 1210]];
  const TL2 = [-5, 3, -2, 4, 3, -4, -3, 5, 4, -3, 2, -5];
  const pins = [];
  POS.forEach(([x, y], k) => {
    const cv = el("div", null, null, board, { position: "absolute", left: x + "px", top: y + "px", width: "180px", height: "260px",
      background: "#f2efe6", padding: "5px", boxShadow: "0 12px 22px rgba(0,0,0,0.55)", opacity: 0 });
    gsap.set(cv, { rotation: TL2[k] });
    const im = el("img", null, null, cv, { display: "block", width: "100%", height: "100%", objectFit: "cover" });
    im.src = "assets/cover_" + String(k + 1).padStart(2, "0") + ".png";
    tl.fromTo(cv, { opacity: 0, y: -100, scale: 1.25 }, { opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.6)" }, 33.0 + k * 0.05);
    pins.push([x + 95, y + 18]);
  });
  const frame = el("div", null, null, board, { position: "absolute", left: "400px", top: "660px", width: "280px", height: "340px", background: "#f7f2e4",
    padding: "14px 14px 60px", boxShadow: "0 0 0 6px " + GOLD + ", 0 20px 40px rgba(0,0,0,0.6)", opacity: 0 });
  const fin = el("div", null, avatarSvg("#111"), frame, { width: "100%", height: "100%", background: "#2c2c34" });
  el("div", null, "?", frame, { position: "absolute", left: 0, right: 0, bottom: "4px", textAlign: "center", fontSize: "52px", color: RED });
  tl.fromTo(frame, { opacity: 0, scale: 1.6, rotation: 8 }, { opacity: 1, scale: 1, rotation: -2, duration: 0.35, ease: "back.out(1.8)" }, 33.5);
  let svg = '<svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0">';
  pins.forEach(([x, y]) => {
    svg += `<line class="str" x1="${x}" y1="${y}" x2="540" y2="670" stroke="#c62828" stroke-width="5" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`;
  });
  pins.concat([[540, 670]]).forEach(([x, y]) => {
    svg += `<circle cx="${x}" cy="${y + 3}" r="14" fill="rgba(0,0,0,0.35)"/><circle cx="${x}" cy="${y}" r="13" fill="#e53935" stroke="#7f0000" stroke-width="3"/><circle cx="${x - 4}" cy="${y - 4}" r="4" fill="#ffb3b3"/>`;
  });
  svg += "</svg>";
  const strings = el("div", null, svg, board, { position: "absolute", left: 0, top: 0, opacity: 0 });
  tl.to(strings, { opacity: 1, duration: 0.15 }, 33.6);
  strings.querySelectorAll(".str").forEach((s, k) => tl.to(s, { attr: { "stroke-dashoffset": 0 }, duration: 0.3, ease: "power1.inOut" }, 33.65 + k * 0.08));
  tl.set(board, { opacity: 1 }, 33.0);
  tl.fromTo(board, { scale: 1 }, { scale: 1.35, duration: 2.4, ease: "sine.in" }, 33.05);
  tl.to(board, { scale: 5, filter: "blur(14px)", opacity: 0, duration: 0.4, ease: "power3.in" }, 35.4);

  // ================= L11 (35.53 – 40.8): 17 SAHI -> SHIVAM KA PARTNER =================
  const c17 = counter(A, range(0, 17), 35.55, 36.2, { left: 0, right: 0, top: "380px", height: "300px", textAlign: "center",
    fontSize: "280px", color: GOLD, WebkitTextStroke: "20px #111", paintOrder: "stroke fill" });
  const c17b = big("SAHI JAWAB", { top: "690px", fontSize: "90px", color: "#fff" });
  tl.set(c17, { opacity: 1 }, 35.55);
  tl.fromTo(c17, { scale: 0.5 }, { scale: 1, duration: 0.6, ease: "power3.out" }, 35.55);
  tl.fromTo(c17b, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.25 }, 35.85);
  tl.to(c17, { scale: 1.12, duration: 0.12, yoyo: true, repeat: 1 }, 36.2);
  const aaj = big("AAJ SE...", { top: "860px", fontSize: "100px", color: YEL });
  tl.fromTo(aaj, { opacity: 0, x: -200 }, { opacity: 1, x: 0, duration: 0.3, ease: "power3.out" }, 36.77);
  gone([c17, c17b, aaj], 38.15);
  const partner = big("SHIVAM KA<br>PARTNER", { top: "290px", fontSize: "128px", color: GOLD, WebkitTextStroke: "15px #111" });
  slam(partner, 38.27, -3, 2.8);
  shake(38.47, 26);
  redflash(38.47);
  const sh = bust("S2_07", { left: "640px", top: "580px", height: "900px" });
  tl.fromTo(sh, { opacity: 0, x: 500 }, { opacity: 1, x: 0, duration: 0.4, ease: "power4.out" }, 38.35);
  const card = el("div", null, null, A, { position: "absolute", left: "36px", top: "760px", width: "640px", height: "380px", opacity: 0,
    borderRadius: "30px", background: "linear-gradient(160deg,#2b2210,#14110a)", border: "8px solid " + GOLD,
    boxShadow: "0 0 60px rgba(245,197,66,0.65), 0 24px 40px rgba(0,0,0,0.6)" });
  el("div", null, "👑", card, { position: "absolute", left: 0, right: 0, top: "18px", textAlign: "center", fontSize: "110px",
    fontFamily: "'Segoe UI Emoji', " + SANS });
  el("div", null, "@parchhaiboy143", card, { position: "absolute", left: 0, right: 0, top: "170px", textAlign: "center", fontSize: "66px",
    fontFamily: SANS, fontWeight: 900, color: "#fff" });
  el("div", null, "17 SAHI • #1", card, { position: "absolute", left: 0, right: 0, top: "270px", textAlign: "center", fontSize: "50px", color: GOLD });
  tl.fromTo(card, { opacity: 0, scale: 2.2, rotation: -6 }, { opacity: 1, scale: 1, rotation: -2, duration: 0.22, ease: "power4.in" }, 39.62);
  flash(39.84, 0.8);
  shake(39.84, 22);
  confetti(39.84, 54, 360, 900);
  pulse(card, 40.1, 1, 1.04);
  gone([partner, sh, card], 40.75, 0.2);

  // ================= L12 + L13 (40.88 – 48.95): comment box =================
  const hdr1 = el("div", null, "RANK CHAHIYE?", A, { position: "absolute", left: "50%", top: "320px", fontSize: "76px", color: "#111", background: YEL,
    padding: "8px 36px 14px", borderRadius: "20px", border: "6px solid #111", boxShadow: "0 9px 0 #111", whiteSpace: "nowrap", opacity: 0 });
  gsap.set(hdr1, { xPercent: -50 });
  slam(hdr1, 40.88, -2, 2);
  const box = el("div", null, null, A, { position: "absolute", left: "40px", top: "1040px", width: "1000px", height: "130px", opacity: 0,
    background: "#121218", borderRadius: "65px", border: "3px solid #3a3a44", fontFamily: SANS, boxShadow: "0 18px 40px rgba(0,0,0,0.6)" });
  el("div", null, null, box, { position: "absolute", left: "20px", top: "22px", width: "80px", height: "80px", borderRadius: "50%",
    background: "radial-gradient(circle at 50% 38%, #e0e0e6 0 16px, #4c6ef5 17px)" });
  const ph = el("div", null, "Add a comment...", box, { position: "absolute", left: "122px", top: "38px", fontSize: "40px", color: "#77777f" });
  const sendB = el("div", null, '<svg width="44" height="44" viewBox="0 0 24 24"><path d="M3 11.5 21 3l-8.5 18-2.2-7.3L3 11.5z" fill="#fff"/></svg>', box,
    { position: "absolute", right: "16px", top: "16px", width: "96px", height: "96px", borderRadius: "50%", background: "#3797f0",
      display: "flex", alignItems: "center", justifyContent: "center" });
  tl.fromTo(box, { opacity: 0, y: 120 }, { opacity: 1, y: 0, duration: 0.35, ease: "back.out(1.8)" }, 41.0);
  const typed = (txt, t, rate) => {
    const n = el("div", null, null, box, { position: "absolute", left: "122px", top: "36px", fontSize: "44px", color: "#fff", fontWeight: 700, whiteSpace: "nowrap" });
    tl.set(ph, { opacity: 0 }, t);
    const sp = typeIn(n, txt, t, rate);
    return { n, sp, end: t + txt.length * rate };
  };
  const send = (t, nodes) => {
    tl.to(sendB, { scale: 0.8, duration: 0.07 }, t);
    tl.to(sendB, { scale: 1, duration: 0.15, ease: "back.out(3)" }, t + 0.07);
    tl.set(nodes, { opacity: 0 }, t + 0.1);
    tl.set(ph, { opacity: 1 }, t + 0.1);
  };
  const posted = (txt, top, t, w) => {
    const p = el("div", null, null, A, { position: "absolute", left: "40px", top: top + "px", width: (w || 640) + "px", height: "140px", opacity: 0,
      background: "rgba(22,22,28,0.96)", borderRadius: "26px", fontFamily: SANS, color: "#fff", boxShadow: "0 14px 30px rgba(0,0,0,0.5)" });
    el("div", null, null, p, { position: "absolute", left: "22px", top: "22px", width: "72px", height: "72px", borderRadius: "50%",
      background: "radial-gradient(circle at 50% 38%, #e0e0e6 0 15px, #4c6ef5 16px)" });
    el("div", null, "tum <span style='color:#8e8e96;font-weight:400'>&nbsp;abhi</span>", p, { position: "absolute", left: "112px", top: "14px", fontSize: "28px", fontWeight: 700 });
    el("div", null, txt, p, { position: "absolute", left: "112px", top: "54px", fontSize: "46px", fontWeight: 700, whiteSpace: "nowrap" });
    const ok = el("div", null, "✓ SAHI", A, { position: "absolute", left: (w || 640) + 70 + "px", top: top + 34 + "px", fontSize: "56px", color: "#111",
      background: GREEN, padding: "4px 22px 10px", borderRadius: "16px", border: "5px solid #111", opacity: 0 });
    tl.fromTo(p, { opacity: 0, y: 160, scale: 0.8 }, { opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2)" }, t);
    tl.fromTo(ok, { opacity: 0, scale: 2.2, rotation: -10 }, { opacity: 1, scale: 1, rotation: -4, duration: 0.18, ease: "power4.in" }, t + 0.25);
    return [p, ok];
  };
  const k1 = typed("Kallu", 42.24, 0.07);
  send(42.75, k1.n);
  const p1 = posted("Kallu", 820, 42.8, 400);
  const k2 = typed("3", 43.78, 0.07);
  send(43.95, k2.n);
  tl.to(p1, { y: -170, duration: 0.3, ease: "power3.out" }, 44.0);
  const p2 = posted("3", 820, 44.0, 400);
  gone([...p1, ...p2, hdr1], 44.55, 0.2);
  // L13: naam - wajah
  const hdr2 = el("div", null, "WAJAH BATANI HAI?", A, { position: "absolute", left: "50%", top: "320px", fontSize: "72px", color: "#111", background: YEL,
    padding: "8px 36px 14px", borderRadius: "20px", border: "6px solid #111", boxShadow: "0 9px 0 #111", whiteSpace: "nowrap", opacity: 0 });
  gsap.set(hdr2, { xPercent: -50 });
  slam(hdr2, 44.62, -2, 2);
  const k3 = typed("Kallu - chaabi uski jeb mein thi", 46.22, 0.055);
  // NAAM / DASH / WAJAH labels (box ke upar)
  const LBL = [["NAAM", 46.6, 210, YEL, 640], ["DASH", 47.21, 312, RED, 830], ["WAJAH", 47.93, 600, "#7fd3ff", 830]];
  const lbls = LBL.map(([txt, t, x, c, top]) => {
    const ah = 1030 - top - 74;
    const w = el("div", null, null, A, { position: "absolute", left: x - 100 + "px", width: "200px", top: top + "px", textAlign: "center", opacity: 0 });
    el("div", null, txt, w, { fontSize: "58px", color: c, WebkitTextStroke: "9px #111", paintOrder: "stroke fill" });
    el("div", null, '<svg width="40" height="' + ah + '" viewBox="0 0 40 ' + ah + '"><path d="M20 0 L20 ' + (ah - 18) + ' M6 ' + (ah - 34) + ' L20 ' + (ah - 8) + ' L34 ' + (ah - 34) + '" stroke="' + c + '" stroke-width="8" fill="none" stroke-linecap="round"/></svg>', w,
      { marginTop: "2px" });
    tl.fromTo(w, { opacity: 0, y: -60 }, { opacity: 1, y: 0, duration: 0.25, ease: "back.out(2.2)" }, t);
    return w;
  });
  // dash ko laal + bada
  tl.to(k3.sp[6], { color: RED, scale: 1.6, duration: 0.15 }, 47.21);
  tl.to(k3.sp[6], { scale: 1, duration: 0.2 }, 47.4);
  send(48.45, k3.n);
  gone(lbls, 48.5);
  const p3 = posted("Kallu - chaabi uski jeb mein thi", 840, 48.5, 760);
  tl.to(p3[1], { left: "640px", top: "700px", duration: 0.01 }, 48.5);
  gone([...p3, hdr2, box], 48.95, 0.2);

  // ================= L14 (49.17 – 52.8): niyam stamps + 24 ghante ghadi =================
  const st1 = stampBox("SIRF PEHLA<br>COMMENT", 104, 400);
  tl.fromTo(st1, { opacity: 0, scale: 2.4, rotation: -3 }, { opacity: 1, scale: 1, rotation: -7, duration: 0.16, ease: "back.out(1.4)" }, 49.17);
  shake(49.33, 18);
  const clock = el("div", null,
    `<svg width="300" height="300" viewBox="0 0 300 300"><circle cx="150" cy="150" r="136" fill="#fff8e1" stroke="#111" stroke-width="16"/>` +
    Array.from({ length: 12 }, (_, k) => `<line x1="150" y1="30" x2="150" y2="${k % 3 ? 46 : 58}" stroke="#111" stroke-width="${k % 3 ? 5 : 9}" transform="rotate(${k * 30} 150 150)"/>`).join("") +
    `<line class="hh" x1="150" y1="150" x2="150" y2="88" stroke="#111" stroke-width="14" stroke-linecap="round"/><line class="mh" x1="150" y1="150" x2="150" y2="50" stroke="#e53935" stroke-width="9" stroke-linecap="round"/><circle cx="150" cy="150" r="13" fill="#111"/></svg>`,
    A, { position: "absolute", left: "390px", top: "760px", width: "300px", height: "300px", opacity: 0 });
  const mh = clock.querySelector(".mh"), hh = clock.querySelector(".hh");
  gsap.set([mh, hh], { transformOrigin: "150px 150px" });
  tl.fromTo(clock, { opacity: 0, scale: 0.3, rotation: -40 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2)" }, 51.24);
  tl.fromTo(mh, { rotation: 0 }, { rotation: 360 * 6, duration: 1.3, ease: "power2.inOut" }, 51.4);
  tl.fromTo(hh, { rotation: 0 }, { rotation: 360, duration: 1.3, ease: "power2.inOut" }, 51.4);
  const st2 = stampBox("24 GHANTE", 110, 1080, YEL);
  tl.fromTo(st2, { opacity: 0, scale: 2.4, rotation: 3 }, { opacity: 1, scale: 1, rotation: 5, duration: 0.16, ease: "back.out(1.4)" }, 51.85);
  shake(52.01, 14);
  gone([st1, clock, st2], 52.75, 0.2);

  // ================= L15 (52.91 – 57.95): YouTube SUBSCRIBE + Telegram JOIN =================
  const rs = big("RANK SIRF UNHE", { top: "330px", fontSize: "96px", color: "#fff" });
  tl.fromTo(rs, { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, 52.95);
  const btn = (top, bg, iconSvg, label, done) => {
    const b = el("div", null, null, A, { position: "absolute", left: "110px", width: "860px", height: "200px", top: top + "px", borderRadius: "40px",
      background: bg, border: "7px solid #111", boxShadow: "0 12px 0 #111", opacity: 0, overflow: "hidden" });
    el("div", null, iconSvg, b, { position: "absolute", left: "44px", top: "40px", width: "120px", height: "120px" });
    const l1 = el("div", null, label, b, { position: "absolute", left: "190px", top: "46px", fontSize: "92px", color: "#fff", WebkitTextStroke: "10px #111", paintOrder: "stroke fill" });
    const l2 = el("div", null, done, b, { position: "absolute", left: "190px", top: "52px", fontSize: "80px", color: "#fff", opacity: 0, WebkitTextStroke: "9px #111", paintOrder: "stroke fill" });
    return { b, l1, l2 };
  };
  const yt = btn(520, "#E52D27", '<svg viewBox="0 0 24 24" width="120" height="120"><rect x="1" y="4" width="22" height="16" rx="5" fill="#fff"/><path d="M10 8.5v7l6-3.5z" fill="#E52D27"/></svg>', "SUBSCRIBE", "SUBSCRIBED ✓");
  const tg = btn(790, TGBLUE, '<svg viewBox="0 0 24 24" width="120" height="120"><circle cx="12" cy="12" r="11" fill="#fff"/><path d="M5.5 11.6l11.4-4.4c.5-.2 1 .1.8.9l-1.9 9c-.1.6-.5.8-1 .5l-2.9-2.1-1.4 1.3c-.2.2-.3.3-.6.3l.2-3 5.4-4.9c.2-.2 0-.3-.3-.1l-6.7 4.2-2.9-.9c-.6-.2-.6-.6.1-.8z" fill="#2AABEE"/></svg>', "JOIN", "JOINED ✓");
  tl.fromTo(yt.b, { opacity: 0, x: -900 }, { opacity: 1, x: 0, duration: 0.35, ease: "power4.out" }, 55.43);
  tl.fromTo(tg.b, { opacity: 0, x: 900 }, { opacity: 1, x: 0, duration: 0.35, ease: "power4.out" }, 56.69);
  const cur = el("div", null, '<svg width="110" height="130" viewBox="0 0 24 28"><path d="M8 2.5c0-1 .8-1.8 1.8-1.8s1.8.8 1.8 1.8V11l5.6 1.3c1.2.3 1.9 1.4 1.7 2.6l-1.2 7.4c-.2 1.3-1.3 2.2-2.6 2.2H10c-.9 0-1.7-.4-2.2-1.1L3.1 17c-.6-.8-.4-1.9.4-2.5.7-.5 1.7-.4 2.3.2L8 17V2.5z" fill="#fff" stroke="#111" stroke-width="1.4"/></svg>', A,
    { position: "absolute", left: "700px", top: "1300px", width: "110px", height: "130px", opacity: 0 });
  tl.fromTo(cur, { opacity: 0, x: 200, y: 200 }, { opacity: 1, x: 0, y: 0, duration: 0.01 }, 55.6);
  tl.to(cur, { left: "640px", top: "600px", duration: 0.4, ease: "power2.inOut" }, 55.6);
  const click = (b, t) => {
    tl.to(cur, { scale: 0.85, duration: 0.07 }, t);
    tl.to(cur, { scale: 1, duration: 0.1 }, t + 0.07);
    tl.to(b.b, { scale: 0.94, duration: 0.07 }, t);
    tl.to(b.b, { scale: 1, duration: 0.18, ease: "back.out(3)" }, t + 0.07);
    tl.set(b.l1, { opacity: 0 }, t + 0.08);
    tl.set(b.l2, { opacity: 1 }, t + 0.08);
    tl.to(b.b, { backgroundColor: "#3a3a42", duration: 0.15 }, t + 0.08);
  };
  click(yt, 56.1);
  tl.to(cur, { left: "640px", top: "870px", duration: 0.3, ease: "power2.inOut" }, 56.95);
  click(tg, 57.3);
  gone([rs, yt.b, tg.b, cur], 57.9, 0.2);

  // ================= L16 (58.11 – 61.05): Telegram bot phone =================
  const phn = el("div", null, null, A, { position: "absolute", left: "240px", top: "290px", width: "600px", height: "930px", background: "#111",
    borderRadius: "70px", padding: "20px", boxSizing: "border-box", boxShadow: "0 30px 50px rgba(0,0,0,0.5), inset 0 0 0 4px #3a3a3a", opacity: 0 });
  const scr = el("div", null, null, phn, { position: "relative", width: "100%", height: "100%", borderRadius: "52px", overflow: "hidden",
    background: "linear-gradient(180deg,#cfe3c5,#a9cfa0)", fontFamily: SANS });
  const bar = el("div", null, null, scr, { position: "absolute", left: 0, right: 0, top: 0, height: "150px", background: "#517DA2", color: "#fff" });
  el("div", null, "🕵️", bar, { position: "absolute", left: "28px", top: "52px", width: "78px", height: "78px", borderRadius: "50%", background: "#2b2b33",
    display: "flex", alignItems: "center", justifyContent: "center", fontSize: "44px", fontFamily: "'Segoe UI Emoji', " + SANS });
  el("div", null, "Shivam Rank Bot", bar, { position: "absolute", left: "124px", top: "54px", fontSize: "38px", fontWeight: 700 });
  el("div", null, "bot", bar, { position: "absolute", left: "124px", top: "100px", fontSize: "26px", opacity: 0.8 });
  const m1 = el("div", null, "/rank", scr, { position: "absolute", right: "22px", top: "320px", padding: "16px 26px", borderRadius: "24px 24px 6px 24px",
    background: "#effdde", fontSize: "44px", color: "#111", opacity: 0, transformOrigin: "100% 100%" });
  const m2 = el("div", null, "🕵️ <b>@tum</b><br>🏅 Rank: <b>SENIOR DETECTIVE</b><br>✅ Kul sahi: <b>12</b><br>🔥 Streak: <b>5 reels</b>", scr,
    { position: "absolute", left: "22px", right: "60px", top: "430px", padding: "18px 24px", borderRadius: "24px 24px 24px 6px", background: "#fff",
      fontSize: "36px", lineHeight: 1.4, color: "#111", opacity: 0, transformOrigin: "0% 100%", fontFamily: "'Segoe UI Emoji', " + SANS });
  tl.fromTo(phn, { opacity: 0, y: 700 }, { opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }, 58.15);
  tl.fromTo(m1, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2.5)" }, 59.73);
  tl.fromTo(m2, { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }, 60.25);
  tl.fromTo(phn, { y: 0 }, { y: -14, duration: 1.2, yoyo: true, repeat: 1, ease: "sine.inOut" }, 58.6);
  tl.to(phn, { opacity: 0, y: 300, duration: 0.25, ease: "power2.in" }, 60.9);

  // ================= L17 (61.16 – 63.6): AGLA NAAM... TUMHARA? =================
  const pt = bust("S2_03", { left: "40px", top: "430px", height: "960px" });
  tl.fromTo(pt, { opacity: 0, x: -500 }, { opacity: 1, x: 0, duration: 0.4, ease: "power4.out" }, 61.18);
  const ag = big("AGLA NAAM...", { top: "330px", fontSize: "100px", color: "#fff" });
  tl.fromTo(ag, { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, 61.2);
  const tum = big("TUMHARA?", { top: "660px", left: "330px", right: "10px", fontSize: "106px", color: YEL, WebkitTextStroke: "14px #111" });
  slam(tum, 62.1, -6, 2.8);
  shake(62.3, 20);
  pulse(tum, 62.6, 1, 1.06);
  gone([pt, ag, tum], 63.5, 0.2);

  // ================= L18 (64.09 – 67.0): signature + END CTA (67.0 – 68.0) =================
  const eyes = bust("S2_16", { left: "233px", top: "380px", height: "760px" });
  tl.fromTo(eyes, { opacity: 0, scale: 1.15 }, { opacity: 1, scale: 1, duration: 0.45, ease: "power2.out" }, 63.6);
  tl.fromTo(eyes, { y: 0 }, { y: -12, duration: 1.5, yoyo: true, repeat: 1, ease: "sine.inOut" }, 64.0);
  const dr = big("DETECTIVE RANK", { top: "290px", fontSize: "92px", color: YEL, WebkitTextStroke: "12px #111" });
  slam(dr, 63.65, -2, 2);
  const tag = big("Shivam ki nazar se<br>koi nahi bachta.", { top: "1180px", fontSize: "64px", color: "#fff", WebkitTextStroke: "9px #111" });
  tl.fromTo(tag, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, 64.1);
  gone([eyes, dr, tag], 66.9, 0.2);
  const e1 = big("APNA RANK DEKHO", { top: "560px", fontSize: "86px", color: "#fff" });
  const e2 = big("Telegram:<br><span style='color:" + TGBLUE + "'>@Theshivamiq_rank_bot</span>", { top: "700px", fontSize: "70px", color: "#fff", WebkitTextStroke: "10px #111" });
  const brand = el("div", null, '<img src="assets/LOGO_ROUND.png" style="width:120px;height:120px"/><span style="font-size:56px;color:#fff">@theshivamiq</span>', A,
    { position: "absolute", left: 0, right: 0, top: "1000px", display: "flex", justifyContent: "center", alignItems: "center", gap: "22px", opacity: 0 });
  tl.fromTo(e1, { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.25, ease: "power3.out" }, 67.0);
  slam(e2, 67.08, -2, 1.8);
  tl.to(brand, { opacity: 1, duration: 0.25 }, 67.2);
};
