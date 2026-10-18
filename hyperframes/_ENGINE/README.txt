SHIVAM HYPERFRAMES ENGINE  (pakka format – dobara mat likhna)
==============================================================
File: shivam_engine.html  = H02-001 Aakhri Mazaak / H01 v2 wala look, ek jagah par.
Nayi reel = is file ko project folder mein index.html bana kar copy karo, sirf 4 cheezein bharo:
  __TITLE__  -> reel ka naam
  __DUR__    -> poori video ki lambai (sec) = OFF + END
  __MEDIA__  -> hook clip ho to:  <video id="hook" class="clip" src="assets/hook.mp4" data-start="0" data-duration="10" data-track-index="1" muted playsinline></video>
                warna khaali
  __OVERLAYS__ -> story ke upar wali layer (warna khaali):
                night:  <img id="nightimg" src="assets/night.png" alt="" />
                fog:    <video id="fog0" class="fog clip" src="assets/fog.mp4" data-start=".." data-duration=".." data-track-index="2" muted playsinline></video>
                (phir T.overlays mein [id, s, e, opacity])
  __DATA__   -> JS: const OFF, END, CASE, SCENES, P, T, CFG (neeche)
Engine code (DATA ke neeche) KABHI mat badlo. Naya effect chahiye to yahin engine mein jodo (optional field), taaki sab reels ko mile.

Project folder chahiye: assets\BG_MAIN.png, assets\fonts\MAIN.ttf (hook reels: ariblk.ttf, Sab Pe Shak: Poppins-Bold.ttf),
assets\mix.wav (poori awaaz), assets\<img>.png (transparent padding trim), LOGO_ROUND.png (brand ho to), cover.png (CFG.cover>0 ho to),
hyperframes.json + package.json (template\ se).
Render: project folder mein  npx --yes hyperframes@0.8.144 render -o "<out>.mp4"

DATA
----
const OFF = 10.2;          // story kis second se shuru (hook clip ki lambai + 0.2 ; cover ho to cover sec ; kuch nahi to 0)
const END = 56.6;          // story ki lambai (OFF ke baad)
const CASE = "H02-001";
const SCENES = [           // images (story time, OFF ke baad)
  { img:"S12", s:5.07, e:7.61, h:1000, bottom:140, enter:"pop" },
  // h = oonchai px (khade) | w = chaudai px (leta hua / prop / card) ; bottom = neeche se px
  // enter: none / fade / pop / popin (0->108%->100%) / rise / drop / left / right
  // optional: x (center px, 1080 mein), mirror:true, push:1.06 (dheere zoom), zoom:[[s,e]] (100->110%),
  //           shake:[t], noexit:true, nopunch:true
];
const P = [ [["Raat",7.61,8.11],["do",8.19,8.34]], ... ];   // captions: phrase = [[shabd,start,end]...], CAPS shabd = peela
const T = {                // sab optional (null / na likho = nahi dikhega)
  hook: [0.1, 5.07, "KILLER KAUN?"],      caseChip: [5.15, 7.55],
  chips: [["clock","RAAT 2 BAJE",7.7,8.68]],  stamps: [["BATTI GUL!",8.68,9.9,-6]],
  crime: [12.5,16.26],                    // template B khoon ki boondein (SIRF murder)
  suspects: [["SUSPECT 1/3","AAKASH",17.82,24.07]],   // badge "" = sirf naam patti
  dhyaan: [s,e], soch: 43.73 (3 sec stopwatch), solved: [47.6,48.75],
  options: [48.75,53.79,"1, 2 ya 3?"], ctaPill: [50.03,53.79], brand: 53.9,
  night: [[7.61,16.26,0.85]], black: [[8.68,9.3]], relight: 9.3,
  texts: [["Kurte par<br>kaju katli!", s, e, "clue", 1150, 76]],   // kind: hook/clue/twist/cta/plain, y px, size px
  level: ["LEVEL 6/10", 0.2, 96],         overlays: [["nightimg",s,e,0.25]],  pauses: [[s,e]],
  phone: { s:22.69, e:27.91, name:"Priya ❤️", time:"9:00 PM", top:700,          // CSS phone (WhatsApp jaisa chat)
           msgs:[["out","Bunty ke ghar Ludo khel raha hoon!",25.11]] },        // "out" = hara (right), "in" = safed (left)
           // out msg se 0.9s pehle "typing..." dots; bubble pop + shabd ek-ek karke; phone halka float. top/status optional.
           // (01-041 Perfect Bahana mein joda gaya. Na likho to kuch nahi dikhega – purani reels same.)
};
const CFG = {              // optional – default = hook reels wala layout
  hdrTop:120, nameTop:1770, capTop:330, capSize:84, stroke:12, levelTop:300, cover:0, ctaText:"COMMENT + FOLLOW karo",
  punch:1.06, floatPx:14, pop:{t1:0.15,t2:0.25,peak:1.08}, zoom:1.1, fade:0.3, shake:0.3, shakePx:14,
  colors:{clue:"#FFD400", twist:"#E53935", normal:"#FFFFFF"}
};

  // T.glitch: [s, e, "CASE - 003", "assets/cover.png"(optional peeche image)] – kaala parda + RGB-split glitch text + scanlines, end par flash (SS-003, 2026-10-15)
  // CFG.activeWord: true (ya rang) = caption mein bolta hua shabd peela #FFE600 + 1.1x, phir safed (SS-004, 2026-10-15)
  // SCENES punch:[t,...] = us time par image 1.0 -> 1.12 punch-in (spring), scene end tak ruka (SS-004)
  // sps.py: Animation column = rise / left / right / drop / pop bhi chalte hain; "punch" = same image + punch-in;
  //         Part folder mein EXTRA_<case>_P<n>.json {"T":{chips, crime, soch, stamps, night, black, phone...}, "CFG":{}} = T mein jud jaata hai
const EXTRA = function (tl, H) { ... };   // optional: reel ke khaas scenes (announcement jaise) – apne layer/animation
           // tl = story timeline (OFF ke baad ka time), H = {el, $, C, stampIn, fadeOut, rnd, root}.
           // Math.random/Date.now kabhi nahi – random chahiye to H.rnd(). (ANN Training Khatam mein joda gaya)

Kaun use karta hai:
- Sab Pe Shak series: theshivamiq code\sab_pe_shak\sps.py (Excel se DATA khud bharta hai)
- Hook reels (H01–H12) ki purani projects apni index.html rakhti hain (unhe mat chhuo). Nayi hook reel = yahi engine.
