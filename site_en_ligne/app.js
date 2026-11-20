/* Carnet de voyage Thaïlande 2026 : navigation, photo du jour, plan du métro zoomable.
   Tout reste sur le téléphone : aucune donnée n'est envoyée nulle part. */
(function () {
"use strict";

var $ = function (s, r) { return (r || document).querySelector(s); };
var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
var pad2 = function (n) { return (n < 10 ? "0" : "") + n; };

/* ───────────── mémoire du téléphone ───────────── */
var LS = {
  get: function (k, d) { try { var v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } },
  set: function (k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } },
  del: function (k) { try { localStorage.removeItem(k); } catch (e) {} }
};
/* Photos : une par jour, rangée sous la date « AAAA-MM-JJ », en ArrayBuffer (le plus fiable sur iPhone). */
var DB = {
  p: null,
  open: function () {
    if (!this.p) {
      this.p = new Promise(function (res, rej) {
        try {
          var r = indexedDB.open("carnet-thailande", 1);
          r.onupgradeneeded = function () { if (!r.result.objectStoreNames.contains("photos")) r.result.createObjectStore("photos"); };
          r.onsuccess = function () { res(r.result); };
          r.onerror = function () { rej(r.error); };
          r.onblocked = function () { rej(new Error("bloquée")); };
        } catch (e) { rej(e); }
      });
    }
    return this.p;
  },
  run: function (mode, fn) {
    return this.open().then(function (db) {
      return new Promise(function (res, rej) {
        var t = db.transaction("photos", mode), out = fn(t.objectStore("photos"));
        t.oncomplete = function () { res(out && typeof out === "object" && "result" in out ? out.result : out); };
        t.onerror = t.onabort = function () { rej(t.error || new Error("échec")); };
      });
    });
  },
  put: function (k, v) { return this.run("readwrite", function (s) { s.put(v, k); }); },
  get: function (k) { return this.run("readonly", function (s) { return s.get(k); }); },
  del: function (k) { return this.run("readwrite", function (s) { s["delete"](k); }); },
  keys: function () { return this.run("readonly", function (s) { return s.getAllKeys(); }); }
};

/* ───────────── petits outils ───────────── */
var toastT;
function toast(m) {
  var t = $("#toast");
  t.textContent = m; t.classList.add("on");
  clearTimeout(toastT);
  toastT = setTimeout(function () { t.classList.remove("on"); }, 2400);
}
function fmtSize(n) { return n >= 1048576 ? (n / 1048576).toFixed(1).replace(".", ",") + " Mo" : Math.max(1, Math.round(n / 1024)) + " Ko"; }
function blobToBuf(b) {
  if (b.arrayBuffer) return b.arrayBuffer();
  return new Promise(function (res, rej) { var f = new FileReader(); f.onload = function () { res(f.result); }; f.onerror = function () { rej(f.error); }; f.readAsArrayBuffer(b); });
}
function setStatus(el, s, txt) { if (!el) return; el.setAttribute("data-s", s); el.textContent = txt; }
function copyText(txt, okMsg) {
  var ok = function () { toast(okMsg || "Copié"); };
  var ko = function () {
    var done = false;
    try {
      var ta = document.createElement("textarea");
      ta.value = txt; ta.setAttribute("readonly", "");
      ta.style.cssText = "position:fixed;top:0;left:0;opacity:0;font-size:16px";
      document.body.appendChild(ta); ta.select(); ta.setSelectionRange(0, txt.length);
      done = document.execCommand("copy"); ta.parentNode.removeChild(ta);
    } catch (e) {}
    if (done) ok(); else toast("Copie impossible : appuie longtemps sur le texte");
  };
  try { navigator.clipboard.writeText(txt).then(ok, ko); } catch (e) { ko(); }
}

/* ───────────── autocollants ───────────── */
function bump(id, cls, msg) {
  var e = $("#" + id); if (!e) return;
  e.addEventListener("click", function () {
    e.classList.remove("wig", "drive"); void e.offsetWidth; e.classList.add(cls);
    if (msg) toast(msg);
  });
  e.addEventListener("animationend", function () { e.classList.remove(cls); });
}
bump("ele", "wig", "Sawasdee khrap !");
bump("tuk", "drive", "Pouet pouet !");

/* ───────────── qui es-tu ───────────── */
var who = $("#who"), hello = $("#hello");
function paintWho() {
  var me = LS.get("carnet.who", "");
  $$("button", who).forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-n") === me ? "true" : "false"); });
  hello.textContent = "";
  if (me) {
    var bn = document.createElement("b"); bn.textContent = me;
    hello.appendChild(document.createTextNode("Bonjour ")); hello.appendChild(bn); hello.appendChild(document.createTextNode(" !"));
  } else hello.textContent = "Appuie sur ton prénom.";
}
who.addEventListener("click", function (e) {
  var b = e.target.closest ? e.target.closest("button") : null; if (!b) return;
  LS.set("carnet.who", b.getAttribute("data-n")); paintWho();
});
paintWho();

/* ───────────── navigation ───────────── */
var NAMES = { "": "home", jours: "days", hotels: "hotels", utile: "utile", metro: "metro" };
var NAV_OF = { home: "home", days: "days", hotels: "hotels", utile: "utile", metro: "utile" };
var TITLES = { home: "Carnet Thaïlande 2026", days: "Jours · Carnet Thaïlande", hotels: "Hôtels · Carnet Thaïlande", utile: "Utile · Carnet Thaïlande", metro: "Plan du métro · Carnet Thaïlande" };
var days = $$(".day").map(function (a) { return a.getAttribute("data-id"); });
var curDay = null, curName = "";

function centerChip(id, smooth) {
  var ol = $(".strip ol"), c = $('.chip[data-day="' + id + '"]');
  if (!ol || !c) return;
  var left = c.offsetLeft - (ol.clientWidth - c.offsetWidth) / 2;
  try { ol.scrollTo({ left: left, behavior: smooth ? "smooth" : "auto" }); } catch (e) { ol.scrollLeft = left; }
}
function showDay(id) {
  $$(".day").forEach(function (a) { a.hidden = a.getAttribute("data-id") !== id; });
  $$(".chip").forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-day") === id ? "true" : "false"); });
  LS.set("carnet.day", id);
  loadPhoto(id);
}
function route() {
  var h = (location.hash || "").replace(/^#\/?/, "");
  var parts = h.split("/");
  var name = NAMES[parts[0]] || "home";
  var target = null, first = curDay === null;
  if (name === "days") {
    var id = parts[1];
    if (days.indexOf(id) < 0) {
      id = LS.get("carnet.day", "");
      if (days.indexOf(id) < 0) id = days[0];
      try { history.replaceState(null, "", "#/jours/" + id); } catch (e) {}
    }
    showDay(id);
    if (parts[2] === "photo") target = $("#d-" + id + " .snap");
    curDay = id;
  } else if (name === "hotels" && parts[1]) {
    target = document.getElementById("h-" + parts[1]);
  }
  $$(".view").forEach(function (v) { v.hidden = v.id !== "v-" + name; });
  $$(".nav a").forEach(function (a) {
    if (a.getAttribute("data-nav") === NAV_OF[name]) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
  document.title = TITLES[name];
  curName = name;
  if (target) {
    target.scrollIntoView({ block: "start" });
    if (target.classList.contains("hotel")) { target.classList.remove("flash"); void target.offsetWidth; target.classList.add("flash"); }
  } else window.scrollTo(0, 0);
  if (name === "days") centerChip(curDay, !first);
  if (name === "metro") Metro.enter(); else Metro.leave();
}
function goDay(id) {
  /* d'un jour à l'autre : on remplace l'adresse (le bouton Retour ne doit pas repasser par tous les jours) ;
     depuis un autre écran (l'accueil) : on ajoute une page à l'historique */
  if (curName !== "days") { location.hash = "#/jours/" + id; return; }
  try { history.replaceState(null, "", "#/jours/" + id); } catch (e) { location.hash = "#/jours/" + id; return; }
  route();
}
window.addEventListener("hashchange", route);
var photoTile = $("[data-photo-tile]");
if (photoTile) photoTile.addEventListener("click", function (e) {
  e.preventDefault();
  var id = LS.get("carnet.day", ""); if (days.indexOf(id) < 0) id = days[0];
  location.hash = "#/jours/" + id + "/photo";
});
document.addEventListener("click", function (e) {
  var t = e.target.closest ? e.target.closest("[data-go-day]") : null;
  if (!t) return;
  e.preventDefault(); goDay(t.getAttribute("data-go-day"));
});
try { if ("scrollRestoration" in history) history.scrollRestoration = "manual"; } catch (e) {}

/* ───────────── photo du jour ───────────── */
var photoUrl = {}, hasPhoto = {};
function dayIdOf(el) { var d = el.closest ? el.closest(".day") : null; return d ? d.getAttribute("data-id") : null; }
function snapOf(id) { return $("#d-" + id + " .snap"); }
function updateCount() {
  var n = Object.keys(hasPhoto).filter(function (k) { return hasPhoto[k] && days.indexOf(k) >= 0; }).length;
  $$("[data-photo-count]").forEach(function (e) { e.textContent = n ? n + " sur " + days.length + " jours" : "Un polaroïd par jour"; });
}
function paintChip(id) {
  var c = $('.chip[data-day="' + id + '"]');
  if (c) c.classList.toggle("has", !!hasPhoto[id]);
}
function setPhotoUI(id, blob, fresh) {
  var sn = snapOf(id); if (!sn) return;
  var img = $("img", sn), empty = $(".ph-empty", sn), pol = $(".polaroid", sn);
  if (photoUrl[id]) { try { URL.revokeObjectURL(photoUrl[id]); } catch (e) {} photoUrl[id] = null; }
  pol.classList.remove("dev");
  if (blob) {
    photoUrl[id] = URL.createObjectURL(blob);
    img.src = photoUrl[id]; img.hidden = false; empty.hidden = true;
    if (fresh) { void pol.offsetWidth; pol.classList.add("dev"); }
  } else {
    img.removeAttribute("src"); img.hidden = true; empty.hidden = false;
  }
  hasPhoto[id] = !!blob;
  $$("[data-need-photo]", sn).forEach(function (b) { b.hidden = !blob; });
  paintChip(id); updateCount();
}
var loaded = {};
function loadPhoto(id) {
  if (loaded[id]) return;
  loaded[id] = true;
  DB.get(id).then(function (rec) {
    if (rec && rec.buf) setPhotoUI(id, new Blob([rec.buf], { type: rec.type || "image/jpeg" }), false);
  }).catch(function () {
    loaded[id] = false;
    setStatus($(".status", snapOf(id)), "warn", "La mémoire des photos est indisponible sur ce téléphone.");
  });
}
function loadBitmap(file) {
  if (window.createImageBitmap) return createImageBitmap(file, { imageOrientation: "from-image" }).catch(function () { return viaImg(file); });
  return viaImg(file);
}
function viaImg(file) {
  return new Promise(function (res, rej) {
    var u = URL.createObjectURL(file), i = new Image();
    i.onload = function () { URL.revokeObjectURL(u); res(i); };
    i.onerror = function () { URL.revokeObjectURL(u); rej(new Error("image illisible")); };
    i.src = u;
  });
}
function toJpeg(file) {
  return loadBitmap(file).then(function (bm) {
    var w0 = bm.width || bm.naturalWidth, h0 = bm.height || bm.naturalHeight, k = Math.min(1, 1600 / Math.max(w0, h0));
    var w = Math.round(w0 * k), h = Math.round(h0 * k), c = document.createElement("canvas");
    c.width = w; c.height = h; c.getContext("2d").drawImage(bm, 0, 0, w, h);
    if (bm.close) { try { bm.close(); } catch (e) {} }
    return new Promise(function (res, rej) {
      c.toBlob(function (b) { b ? res({ blob: b, w: w, h: h }) : rej(new Error("compression impossible")); }, "image/jpeg", 0.82);
    });
  });
}
function handleFile(id, file) {
  var st = $(".status", snapOf(id));
  setStatus(st, "", "Lecture de la photo…");
  toJpeg(file).then(function (r) {
    setPhotoUI(id, r.blob, true);
    setStatus(st, "ok", "Photo gardée sur ce téléphone. Pense aussi à l’enregistrer dans tes Photos (bouton « Enregistrer »).");
    return blobToBuf(r.blob).then(function (buf) {
      return DB.put(id, { buf: buf, type: "image/jpeg", ts: Date.now() });
    }).then(function () {
      try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist(); } catch (e) {}
    }, function () {
      setStatus(st, "bad", "La photo s’affiche mais n’a pas pu être gardée en mémoire : enregistre-la dans tes Photos.");
    });
  }).catch(function (err) {
    setStatus(st, "bad", "Oups, cette photo n’a pas pu être lue (" + ((err && err.message) || "erreur") + ").");
  });
}
document.addEventListener("change", function (e) {
  var inp = e.target;
  if (!inp.matches || !inp.matches(".snap input[type=file]")) return;
  var f = inp.files && inp.files[0], id = dayIdOf(inp);
  if (f && id) handleFile(id, f);
  try { inp.value = ""; } catch (x) {}
});
$$(".snap input.cap").forEach(function (inp) {
  var id = dayIdOf(inp);
  inp.value = LS.get("carnet.cap." + id, "");
  inp.addEventListener("input", function () { if (inp.value) LS.set("carnet.cap." + id, inp.value); else LS.del("carnet.cap." + id); });
});

/* Enregistrer : partage (iPhone, Android), sinon téléchargement */
function canShareFile() {
  try {
    if (!navigator.share || !navigator.canShare) return false;
    var f = new File([new Blob(["x"], { type: "image/jpeg" })], "x.jpg", { type: "image/jpeg" });
    return !!navigator.canShare({ files: [f] });
  } catch (e) { return false; }
}
var shareOk = canShareFile();
$$("[data-save-lbl]").forEach(function (e) { e.textContent = shareOk ? "Enregistrer" : "Télécharger"; });
function savePhoto(id) {
  var rec = null, st = $(".status", snapOf(id));
  DB.get(id).then(function (r) { rec = r; }, function () {}).then(function () {
    if (!rec || !rec.buf) { setStatus(st, "warn", "Pas encore de photo à enregistrer."); return; }
    var file = new File([new Blob([rec.buf], { type: "image/jpeg" })], "photo-du-jour-" + id + ".jpg", { type: "image/jpeg" });
    if (shareOk) {
      navigator.share({ files: [file], title: "Photo du jour" }).then(function () {
        setStatus(st, "ok", "Choisis « Enregistrer l’image » pour la mettre dans tes Photos.");
      }, function (e) {
        if (e && e.name === "AbortError") { setStatus(st, "", "Annulé."); return; }
        download(file, st);
      });
    } else download(file, st);
  });
}
function download(file, st) {
  try {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(file); a.download = file.name; a.rel = "noopener";
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 5000);
    setStatus(st, "ok", "Téléchargement lancé : la photo est dans l’appli Fichiers.");
  } catch (e) { setStatus(st, "bad", "Téléchargement impossible : appuie longtemps sur la photo."); }
}
var delT = {};
function delPhoto(id, btn) {
  if (btn.getAttribute("data-armed") !== "1") {
    btn.setAttribute("data-armed", "1"); btn.textContent = "Sûr ? Touche encore pour enlever";
    clearTimeout(delT[id]);
    delT[id] = setTimeout(function () { btn.removeAttribute("data-armed"); btn.textContent = "Enlever la photo"; }, 3500);
    return;
  }
  clearTimeout(delT[id]); btn.removeAttribute("data-armed"); btn.textContent = "Enlever la photo";
  DB.del(id).then(function () {
    setPhotoUI(id, null, false);
    setStatus($(".status", snapOf(id)), "", "");
    toast("Photo enlevée");
  }, function () { toast("Impossible d’enlever la photo"); });
}

/* ───────────── boutons « copier » ───────────── */
document.addEventListener("click", function (e) {
  var t = e.target.closest ? e.target.closest("[data-act]") : null; if (!t) return;
  var act = t.getAttribute("data-act");
  if (act === "save") { var i = dayIdOf(t); if (i) savePhoto(i); }
  else if (act === "del") { var j = dayIdOf(t); if (j) delPhoto(j, t); }
  else if (act === "copy") copyText(t.getAttribute("data-copy"), t.getAttribute("data-ok"));
});

/* ───────────── écran d'accueil et hors réseau ───────────── */
var standalone = false;
try { standalone = (window.matchMedia && matchMedia("(display-mode: standalone)").matches) || !!navigator.standalone; } catch (e) {}
var ios = /iPad|iPhone|iPod/.test(navigator.userAgent || "") || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
var deferred = null;
function paintInstall() {
  var box = $("#install-box"); if (!box) return;
  if (standalone) { box.hidden = true; return; }
  box.hidden = false;
  $("#install-btn").hidden = !deferred;
  $("#install-hint").textContent = deferred
    ? "Appuie sur « Installer » : le carnet s’ouvrira en plein écran, comme une appli."
    : ios ? "Dans Safari : touche le bouton Partager (le carré avec une flèche), puis « Sur l’écran d’accueil »."
    : "Dans le menu du navigateur (les trois points) : « Installer l’appli » ou « Ajouter à l’écran d’accueil ».";
}
window.addEventListener("beforeinstallprompt", function (e) { e.preventDefault(); deferred = e; paintInstall(); });
window.addEventListener("appinstalled", function () { standalone = true; paintInstall(); });
$("#install-btn").addEventListener("click", function () {
  if (!deferred) return;
  deferred.prompt(); deferred.userChoice.then(function () { deferred = null; paintInstall(); });
});
paintInstall();

if ("serviceWorker" in navigator && (location.protocol === "https:" || /^(localhost|127\.0\.0\.1)$/.test(location.hostname))) {
  var had = !!navigator.serviceWorker.controller;
  navigator.serviceWorker.addEventListener("controllerchange", function () { if (had) $("#upd").hidden = false; had = true; });
  navigator.serviceWorker.register("sw.js", { scope: "./" }).then(function (reg) {
    document.addEventListener("visibilitychange", function () { if (!document.hidden) { try { reg.update(); } catch (e) {} } });
  }, function () {});
}
$("#upd-btn").addEventListener("click", function () { location.reload(); });

/* ───────────── plan du métro : glisser, pincer, double-toucher ─────────────
   Pendant un geste, seul le calque est déplacé et agrandi (fluide). Une fois le geste fini, le plan
   est redessiné net à la nouvelle échelle (changement du viewBox). */
var Metro = (function () {
  var box = $("#mv"), stage = $("#mv-stage"), msg = $("#mv-load");
  var svg = null, state = "idle", active = false;
  var W0 = 510.224, H0 = 396.85;          /* taille du plan, en unités du SVG */
  var M = 90;                              /* marge dessinée autour de l'écran, en pixels */
  var VW = 0, VH = 0, sMin = 1, sMax = 10;
  var s = 1, vx = 0, vy = 0;               /* vue voulue : pixels par unité, coin haut-gauche (unités) */
  var s0 = 1, x0 = 0, y0 = 0;              /* vue dessinée : échelle, coin haut-gauche de la scène (unités) */
  var ptrs = {}, g = null, ct = 0;
  var tapT = 0, tapX = 0, tapY = 0, downT = 0, downX = 0, downY = 0, moved = false;

  function measure() {
    var r = box.getBoundingClientRect();
    VW = Math.max(120, r.width); VH = Math.max(120, r.height);
    stage.style.width = (VW + 2 * M) + "px"; stage.style.height = (VH + 2 * M) + "px";
    sMin = Math.min(VW / W0, VH / H0); sMax = Math.max(sMin * 12, 6);
  }
  function clampS(v) { return Math.max(sMin, Math.min(sMax, v)); }
  function clampView() {
    var w = VW / s, h = VH / s;
    vx = w >= W0 ? (W0 - w) / 2 : Math.max(-w * 0.08, Math.min(W0 - w + w * 0.08, vx));
    vy = h >= H0 ? (H0 - h) / 2 : Math.max(-h * 0.08, Math.min(H0 - h + h * 0.08, vy));
  }
  function fit() { s = sMin; vx = (W0 - VW / s) / 2; vy = (H0 - VH / s) / 2; }
  function commit() {
    if (!svg) return;
    s0 = s; x0 = vx - M / s; y0 = vy - M / s;
    svg.setAttribute("viewBox", x0 + " " + y0 + " " + ((VW + 2 * M) / s) + " " + ((VH + 2 * M) / s));
    stage.style.transition = "none";
    stage.style.transform = "translate3d(" + (-M) + "px," + (-M) + "px,0)";
  }
  function paint(delay) {
    stage.style.transform = "translate3d(" + (s * (x0 - vx)) + "px," + (s * (y0 - vy)) + "px,0) scale(" + (s / s0) + ")";
    clearTimeout(ct);
    if (!g) ct = setTimeout(commit, delay || 170);
  }
  function zoomTo(px, py, ns, anim) {
    ns = clampS(ns);
    var mx = vx + px / s, my = vy + py / s;
    s = ns; vx = mx - px / s; vy = my - py / s; clampView();
    if (anim) stage.style.transition = "transform .22s ease-out";
    paint(anim ? 290 : 170);
  }
  function pos(e) { var r = box.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }
  function ids() { return Object.keys(ptrs); }
  function startG() {
    var k = ids(), a = ptrs[k[0]], b = ptrs[k[1]];
    g = { n: Math.min(k.length, 2), s: s, vx: vx, vy: vy };
    if (g.n === 2) { g.cx = (a.x + b.x) / 2; g.cy = (a.y + b.y) / 2; g.d = Math.max(12, Math.hypot(a.x - b.x, a.y - b.y)); }
    else { g.cx = a.x; g.cy = a.y; }
    clearTimeout(ct);
  }
  function moveG() {
    if (!g) return;
    var k = ids(), a = ptrs[k[0]], b = ptrs[k[1]], cx = a.x, cy = a.y, ns = g.s;
    if (g.n === 2 && b) { cx = (a.x + b.x) / 2; cy = (a.y + b.y) / 2; ns = clampS(g.s * Math.hypot(a.x - b.x, a.y - b.y) / g.d); }
    var mx = g.vx + g.cx / g.s, my = g.vy + g.cy / g.s;       /* point du plan qui était sous les doigts au départ */
    s = ns; vx = mx - cx / s; vy = my - cy / s; clampView(); paint();
  }
  function up(e) {
    var p = ptrs[e.pointerId]; if (!p) return;
    delete ptrs[e.pointerId];
    try { box.releasePointerCapture(e.pointerId); } catch (x) {}
    if (ids().length) { startG(); return; }
    g = null;
    if (e.type === "pointerup" && !moved && Date.now() - downT < 400) {
      var now = Date.now();
      if (now - tapT < 330 && Math.hypot(p.x - tapX, p.y - tapY) < 34) {
        tapT = 0; zoomTo(p.x, p.y, s < sMin * 2.2 ? s * 2.6 : sMin, true); return;
      }
      tapT = now; tapX = p.x; tapY = p.y;
    }
    paint();
  }
  box.addEventListener("pointerdown", function (e) {
    if (!svg || (e.target.closest && e.target.closest(".mctl"))) return;
    try { box.setPointerCapture(e.pointerId); } catch (x) {}
    ptrs[e.pointerId] = pos(e);
    stage.style.transition = "none";
    if (ids().length === 1) { downT = Date.now(); downX = ptrs[e.pointerId].x; downY = ptrs[e.pointerId].y; moved = false; }
    else moved = true;
    startG();
  });
  box.addEventListener("pointermove", function (e) {
    if (!ptrs[e.pointerId]) return;
    ptrs[e.pointerId] = pos(e);
    if (!moved && Math.hypot(ptrs[e.pointerId].x - downX, ptrs[e.pointerId].y - downY) > 9) moved = true;
    moveG();
  });
  box.addEventListener("pointerup", up);
  box.addEventListener("pointercancel", up);
  box.addEventListener("wheel", function (e) {
    if (!svg) return;
    e.preventDefault();
    var p = pos(e);
    zoomTo(p.x, p.y, s * Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.002)), false);
  }, { passive: false });
  $$(".mctl button").forEach(function (b) {
    b.addEventListener("click", function () {
      if (!svg) return;
      var z = b.getAttribute("data-z");
      zoomTo(VW / 2, VH / 2, z === "fit" ? sMin : s * (z === "in" ? 1.7 : 1 / 1.7), true);
    });
  });
  window.addEventListener("resize", function () {
    if (!active || state !== "ready") return;
    var cx = vx + VW / (2 * s), cy = vy + VH / (2 * s);
    measure(); s = clampS(s); vx = cx - VW / (2 * s); vy = cy - VH / (2 * s); clampView(); commit();
  });

  function load() {
    if (state === "loading" || state === "ready") return;
    state = "loading";
    msg.hidden = false; msg.textContent = "Chargement du plan…";
    fetch("assets/metro.svg").then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.text();
    }).then(function (t) {
      stage.innerHTML = t;
      svg = stage.querySelector("svg");
      if (!svg) throw new Error("plan illisible");
      var vb = (svg.getAttribute("viewBox") || "").split(/[\s,]+/).map(Number);
      if (vb.length === 4 && vb[2] > 0 && vb[3] > 0) { W0 = vb[2]; H0 = vb[3]; }
      svg.removeAttribute("width"); svg.removeAttribute("height");
      svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
      svg.setAttribute("focusable", "false");
      svg.style.cssText = "display:block;width:100%;height:100%";
      state = "ready"; msg.hidden = true;
      measure(); fit(); commit();
    }).catch(function () {
      state = "idle";
      msg.hidden = false;
      msg.innerHTML = "";
      var p = document.createElement("span"); p.textContent = "Le plan n’a pas pu se charger (pas de réseau ?).";
      var b = document.createElement("button"); b.type = "button"; b.className = "btn sm"; b.textContent = "Réessayer";
      b.addEventListener("click", load);
      msg.appendChild(p); msg.appendChild(b);
    });
  }
  return {
    enter: function () {
      active = true;
      if (state === "ready") { var cx = vx + VW / (2 * s), cy = vy + VH / (2 * s); measure(); s = clampS(s); vx = cx - VW / (2 * s); vy = cy - VH / (2 * s); clampView(); commit(); }
      else load();
    },
    leave: function () { active = false; }
  };
})();

/* ───────────── démarrage ───────────── */
DB.keys().then(function (keys) {
  keys.forEach(function (k) { hasPhoto[k] = true; paintChip(k); });
  updateCount();
}, function () {});
updateCount();
try { route(); } catch (e) { var hv = $("#v-home"); if (hv) hv.hidden = false; }
})();
