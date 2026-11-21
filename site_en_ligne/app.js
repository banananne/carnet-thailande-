/* Carnet de voyage Thaïlande 2026 : navigation, photo du jour, plan du métro zoomable.
   Tout reste sur le téléphone : aucune donnée n'est envoyée nulle part, SAUF dans le Traducteur (trans.js) : le texte qu'on y tape
   n'est envoyé à un service de traduction (Google Traduction, puis MyMemory) que lorsqu'on touche « Traduire », et seulement pour une phrase libre. */
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
    if (msg) toast(typeof msg === "function" ? msg() : msg);
  });
  e.addEventListener("animationend", function () { e.classList.remove(cls); });
}
bump("ele", "wig", function () { var p = POL.get(); return "Sawasdee " + (p || "khrap / kha") + " !"; });
bump("tuk", "drive", "Pouet pouet !");

/* ───────────── qui es-tu ───────────── */
var who = $("#who"), hello = $("#hello"), whoBox = $("#who-box"), whoBar = $("#who-bar"), whoHi = $("#who-hi"), whoAv = $("#who-av"), whoT = 0;
function hi(el, me) {   /* « Bonjour <b>Anne</b> ! » */
  var bn = document.createElement("b"); bn.textContent = me;
  el.textContent = ""; el.appendChild(document.createTextNode("Bonjour ")); el.appendChild(bn); el.appendChild(document.createTextNode(" !"));
}
function whoOpen(open) {
  whoBox.hidden = !open;
  whoBar.setAttribute("aria-expanded", open ? "true" : "false");
  whoBar.classList.toggle("open", open);
}
function paintWho() {
  var me = LS.get("carnet.who", ""), sel = null;
  $$("button", who).forEach(function (b) {
    var on = b.getAttribute("data-n") === me;
    b.setAttribute("aria-pressed", on ? "true" : "false");
    if (on) sel = b;
  });
  whoAv.textContent = "";
  document.documentElement.classList.toggle("is-guest", me === "Invité");   /* espace visiteur : pas d'enveloppes, d'horoscope du jour ni de rôles du jour */
  if (me === "Invité" && sel) {
    hello.textContent = "Bienvenue ! Tu visites le carnet en invité·e : les enveloppes secrètes et les rôles du jour sont réservés aux voyageurs.";
    whoHi.textContent = ""; var gb = document.createElement("b"); gb.textContent = "Bienvenue"; whoHi.appendChild(gb); whoHi.appendChild(document.createTextNode("\u00a0!"));
    var gi = $(".ini", sel); if (gi) whoAv.appendChild(gi.cloneNode(true));
  } else if (me && sel) {
    hi(hello, me); hi(whoHi, me);
    var ini = $(".ini", sel); if (ini) whoAv.appendChild(ini.cloneNode(true));
  } else { hello.textContent = "Appuie sur ton prénom."; whoBar.hidden = true; }
}
/* une fois le prénom choisi, le bloc se replie (la ligne « Bonjour … Changer » le rouvre) */
whoBar.addEventListener("click", function () { clearTimeout(whoT); whoOpen(whoBox.hidden); });
who.addEventListener("click", function (e) {
  var b = e.target.closest ? e.target.closest("button") : null; if (!b) return;
  LS.set("carnet.who", b.getAttribute("data-n")); paintWho();
  clearTimeout(whoT);
  /* l'invité·e a une phrase à lire : le bloc reste ouvert plus longtemps (8 s) ; ailleurs, une demi-seconde */
  whoT = setTimeout(function () { whoBar.hidden = false; whoOpen(false); try { whoBar.focus({ preventScroll: true }); } catch (x) {} }, b.getAttribute("data-n") === "Invité" ? 8000 : 550);
});
paintWho();
if ($('button[aria-pressed="true"]', who)) { whoBar.hidden = false; whoOpen(false); } else whoOpen(true);
document.documentElement.classList.remove("has-who");

/* ───────────── navigation ───────────── */
var NAMES = { "": "home", jours: "days", hotels: "hotels", utile: "utile", metro: "metro", lexique: "lexique", taxi: "taxi", convertisseur: "convert", "good-to-know": "gtk",
  jeux: "jeux", quiz: "quiz", "test-doudou": "test", personnalite: "test", doudous: "doudous", mascottes: "doudous", "blind-test": "blind", "mots-meles": "mots", horoscope: "horo", passeport: "pass",
  defi: "defi", "mot-du-jour": "mot", mot: "mot", bingo: "bingo", gourmand: "gourmand", prix: "prix",
  traduire: "trad", traducteur: "trad", essai: "essai" };
var NAV_OF = { home: "home", days: "days", hotels: "hotels", utile: "utile", metro: "utile", lexique: "utile", taxi: "utile", convert: "utile", gtk: "utile",
  jeux: "jeux", quiz: "jeux", test: "jeux", doudous: "jeux", blind: "jeux", mots: "jeux", horo: "jeux", pass: "jeux",
  defi: "jeux", mot: "jeux", bingo: "jeux", gourmand: "jeux", prix: "jeux", trad: "utile" };
var TITLES = { home: "Carnet Thaïlande 2026", days: "Jours · Carnet Thaïlande", hotels: "Hôtels · Carnet Thaïlande", utile: "Utile · Carnet Thaïlande", metro: "Plan du métro · Carnet Thaïlande",
  lexique: "Lexique · Carnet Thaïlande", taxi: "Cartes taxi · Carnet Thaïlande", convert: "Convertisseur · Carnet Thaïlande", gtk: "Good to know · Carnet Thaïlande",
  jeux: "Jeux · Carnet Thaïlande", quiz: "Quiz · Carnet Thaïlande", test: "Test de personnalité · Carnet Thaïlande", doudous: "Les mascottes · Carnet Thaïlande",
  blind: "Blind test · Carnet Thaïlande", mots: "Mots mêlés · Carnet Thaïlande", horo: "Horoscope · Carnet Thaïlande", pass: "Passeport · Carnet Thaïlande",
  defi: "Défi du jour · Carnet Thaïlande", mot: "Mot du jour · Carnet Thaïlande", bingo: "Bingo · Carnet Thaïlande", gourmand: "Carnet gourmand · Carnet Thaïlande", prix: "Prix du voyage · Carnet Thaïlande",
  trad: "Traducteur · Carnet Thaïlande", essai: "Essai des enveloppes · Carnet Thaïlande" };
var days = $$(".day").map(function (a) { return a.getAttribute("data-id"); });
var curDay = null, curName = "", fromDays = false;

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
  if (!document.getElementById("v-" + name)) name = "home";     /* une page absente (l'essai des enveloppes, une fois retiré) ramène à l'accueil */
  var target = null, first = curDay === null;
  if (name === "days") fromDays = false; else if (curName === "days") fromDays = true; else if (curName !== name) fromDays = false;
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
  } else if (name === "taxi") {
    var tid = showTaxi(parts[1]);
    if (parts[1] !== tid) { try { history.replaceState(null, "", "#/taxi/" + tid); } catch (e) {} }
  }
  Show.hide();
  clearTimeout(toastT); $("#toast").classList.remove("on");   /* un message ne suit pas d'une page à l'autre */
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
  if (window.CarnetGames) CarnetGames.enter(name);
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
/* « Retour » d'une page ouverte depuis un jour (le défi du jour, par exemple) : on revient à ce jour, pas à l'accueil des jeux */
document.addEventListener("click", function (e) {
  var b = e.target.closest ? e.target.closest(".vhead .back") : null;
  if (!b || !fromDays || history.length < 2) return;
  e.preventDefault(); fromDays = false;
  try { history.back(); } catch (x) { location.hash = "#/jours/" + (LS.get("carnet.day", "") || days[0]); }
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
    if (window.CarnetGames) CarnetGames.photo(id);
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
  var W0 = 490.392, H0 = 601.214;         /* taille du plan, en unités du SVG (relue dans le viewBox au chargement) */
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

/* ───────────── étape 2 : voix thaïe, « montrer en grand », cartes taxi, convertisseur ───────────── */

/* mon petit mot poli : kha (femme) ou khrap (homme), gardé sur ce téléphone */
var POL = {
  get: function () { var v = LS.get("carnet.pol", ""); return v === "kha" || v === "khrap" ? v : ""; },
  th: function (q) { var p = this.get(); return p === "khrap" ? "ครับ" : p === "kha" ? (q ? "คะ" : "ค่ะ") : ""; },
  rom: function () { var p = this.get(); return p ? " " + p : ""; }
};
function paintPol() {
  var cur = POL.get();
  $$("[data-pol]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-pol") === cur ? "true" : "false"); });
  Show.refresh();
}
document.addEventListener("click", function (e) {
  var b = e.target.closest ? e.target.closest("[data-pol]") : null; if (!b) return;
  var v = b.getAttribute("data-pol");
  if (POL.get() === v) LS.del("carnet.pol"); else LS.set("carnet.pol", v);
  paintPol();
});

/* voix thaïe (même réglage que la page de test, validé sur iPhone) */
var voices = [];
function getVoices() {
  return new Promise(function (res) {
    if (!("speechSynthesis" in window)) { res([]); return; }
    var v = speechSynthesis.getVoices();
    if (v && v.length) { res(v); return; }
    var done = false, fin = function () { if (done) return; done = true; res(speechSynthesis.getVoices() || []); };
    try { speechSynthesis.addEventListener("voiceschanged", fin, { once: true }); } catch (e) {}
    setTimeout(fin, 1800);
  });
}
function thaiVoice() { for (var i = 0; i < voices.length; i++) { if (/^th/i.test(voices[i].lang)) return voices[i]; } return null; }
getVoices().then(function (v) { voices = v; });
var curU = null, speakingBtn = null;
function mark(btn, on) { if (speakingBtn && speakingBtn !== btn) speakingBtn.classList.remove("on"); if (btn) btn.classList.toggle("on", on); speakingBtn = on ? btn : null; }
function say(text, btn) {
  if (!("speechSynthesis" in window) || !window.SpeechSynthesisUtterance) { toast("Ce téléphone ne sait pas lire à voix haute : montre l’écran."); return; }
  try {
    var ss = window.speechSynthesis, busy = !!(ss.speaking || ss.pending);
    var u = new SpeechSynthesisUtterance(text), t = thaiVoice(), started = false;
    u.lang = "th-TH"; u.rate = 0.85; u.volume = 1;
    if (t) u.voice = t;
    u.onstart = function () { started = true; mark(btn, true); };
    u.onend = function () { if (curU === u) mark(btn, false); };
    u.onerror = function () { mark(btn, false); toast("La lecture a échoué : montre l’écran."); };
    curU = u;   /* garder une référence : sinon iOS peut couper la lecture */
    var go = function () { try { ss.resume(); } catch (e) {} ss.speak(u); };
    if (busy) { ss.cancel(); setTimeout(go, 150); } else go();
    if (voices.length && !t) toast("Pas de voix thaïe sur ce téléphone : montre l’écran.");
    else setTimeout(function () { if (!started && curU === u) toast("Rien entendu ? Vérifie le volume (et l’interrupteur de sonnerie).") }, 2800);
  } catch (e) { toast("La lecture a échoué : montre l’écran."); }
}

/* « montrer en grand » : une seule fenêtre pour le lexique, les prix et les cartes taxi */
var Show = (function () {
  var box = $("#show"), th = $("#show-th"), rom = $("#show-rom"), fr = $("#show-fr"), phrase = $("#show-phrase"), card = $("#show-card");
  var pol = $("#show-pol"), sayB = $("#show-say"), closeB = $(".show-x", box);
  var cur = null, pushed = false, lock = null, opener = null;
  function sizeTh() {
    var s = th.textContent, n = (s.match(/[ก-ะาำเ-ๆ]/g) || []).length || s.length;
    var rem = n <= 4 ? 6 : n <= 7 ? 4.6 : n <= 12 ? 3.4 : n <= 20 ? 2.6 : 2.1;
    th.style.fontSize = rem + "rem";
    for (var g = 0; g < 16 && th.scrollWidth > th.clientWidth + 1; g++) { rem *= 0.92; th.style.fontSize = rem + "rem"; }
  }
  function refresh() {
    if (!cur || box.hidden) return;
    if (cur.card) return;
    th.textContent = cur.th + (cur.np ? "" : POL.th(cur.q));
    rom.textContent = cur.rom + (cur.np ? "" : POL.rom());
    fr.textContent = cur.fr || "";
    fr.hidden = !cur.fr;
    sizeTh();
  }
  function wake() {
    try { if (navigator.wakeLock && navigator.wakeLock.request) navigator.wakeLock.request("screen").then(function (l) { lock = l; }, function () {}); } catch (e) {}
  }
  function unwake() { try { if (lock) lock.release(); } catch (e) {} lock = null; }
  function openBox(d, from) {
    cur = d; opener = from || document.activeElement;
    phrase.hidden = !!d.card; card.hidden = !d.card;
    pol.hidden = !!(d.card || d.np);   /* un chiffre ou un prix ne prend pas de petit mot poli : on cache les pastilles */
    if (d.card) { card.innerHTML = ""; var c = d.card.cloneNode(true); c.removeAttribute("id"); card.appendChild(c); }
    box.hidden = false;
    refresh();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(refresh);
    if (!pushed) { try { history.pushState({ show: 1 }, ""); pushed = true; } catch (e) {} }
    wake();
    try { closeB.focus({ preventScroll: true }); } catch (e) {}
  }
  function hideNow() {
    if (box.hidden) return;
    box.hidden = true; cur = null; unwake(); mark(null, false);
    try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e) {}
    if (opener && opener.focus && document.contains(opener)) { try { opener.focus({ preventScroll: true }); } catch (e) {} }
  }
  function close() {
    hideNow();
    if (pushed) { pushed = false; try { history.back(); } catch (e) {} }
  }
  window.addEventListener("popstate", function () { pushed = false; hideNow(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !box.hidden) close(); });
  document.addEventListener("visibilitychange", function () { if (!document.hidden && !box.hidden) wake(); });
  closeB.addEventListener("click", close);
  sayB.addEventListener("click", function () {
    if (!cur) return;
    if (cur.card) say(cur.sayTh + POL.th(0), sayB);
    else say(cur.th + (cur.np ? "" : POL.th(cur.q)), sayB);
  });
  return { open: openBox, close: close, hide: hideNow, refresh: refresh };
})();

document.addEventListener("click", function (e) {
  var t = e.target.closest ? e.target.closest("[data-show],[data-say],[data-show-card]") : null; if (!t) return;
  if (t.hasAttribute("data-say")) { say(t.getAttribute("data-th") + (t.hasAttribute("data-np") ? "" : POL.th(t.getAttribute("data-q") === "1")), t); return; }
  if (t.hasAttribute("data-show-card")) {
    var art = t.closest(".taxi"), c = art && $(".tc", art), sayEl = art && $("[data-say]", art);
    if (c) Show.open({ card: c, sayTh: sayEl ? sayEl.getAttribute("data-th") : "" }, t);
    return;
  }
  Show.open({ th: t.getAttribute("data-th"), rom: t.getAttribute("data-rom") || "", fr: t.getAttribute("data-fr") || "",
              q: t.getAttribute("data-q") === "1", np: t.hasAttribute("data-np") }, t);
});

/* cartes taxi */
var taxiIds = $$(".taxi").map(function (a) { return a.getAttribute("data-id"); });
function showTaxi(id) {
  if (taxiIds.indexOf(id) < 0) id = LS.get("carnet.taxi", "");
  if (taxiIds.indexOf(id) < 0) id = taxiIds[0];
  $$(".taxi").forEach(function (a) { a.hidden = a.getAttribute("data-id") !== id; });
  $$(".tchip").forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-go-taxi") === id ? "true" : "false"); });
  LS.set("carnet.taxi", id);
  return id;
}
function goTaxi(id) {
  if (curName !== "taxi") { location.hash = "#/taxi/" + id; return; }
  try { history.replaceState(null, "", "#/taxi/" + id); } catch (e) { location.hash = "#/taxi/" + id; return; }
  route();
}
document.addEventListener("click", function (e) {
  var t = e.target.closest ? e.target.closest("[data-go-taxi]") : null; if (!t) return;
  e.preventDefault(); goTaxi(t.getAttribute("data-go-taxi"));
});

/* dire un nombre en thaï (jusqu'à 999 999) */
var D_TH = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"];
var D_RO = ["sun", "nueng", "song", "sam", "si", "ha", "hok", "chet", "paet", "kao"];
var U_TH = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน"];
var U_RO = ["", "sip", "roi", "phan", "muen", "saen"];
function thaiNum(n) {
  if (n !== Math.floor(n) || n < 0 || n > 999999) return null;
  if (n === 0) return { th: D_TH[0], rom: D_RO[0] };
  var ds = String(n).split("").map(Number), L = ds.length, th = "", ro = [];
  for (var i = 0; i < L; i++) {
    var d = ds[i], pos = L - 1 - i, w, r;
    if (d === 0) continue;
    if (pos === 1 && d === 1) { w = ""; r = ""; }
    else if (pos === 1 && d === 2) { w = "ยี่"; r = "yi"; }
    else if (pos === 0 && d === 1 && L > 1) { w = "เอ็ด"; r = "et"; }
    else { w = D_TH[d]; r = D_RO[d]; }
    th += w + U_TH[pos];
    if (r) ro.push(r);
    if (U_RO[pos]) ro.push(U_RO[pos]);
  }
  return { th: th, rom: ro.join(" ") };
}

/* convertisseur baht ↔ euro */
(function () {
  var root = $("#conv"); if (!root) return;
  var thb = $("#c-thb"), eur = $("#c-eur"), rateEl = $("#c-rate"), redit = $("#c-redit"), rin = $("#c-rin");
  var none = $("#c-none"), sayIn = $("#c-sayin"), thEl = $("#c-th"), roEl = $("#c-rom");
  var def = parseFloat(root.getAttribute("data-rate")), defLabel = root.getAttribute("data-label");
  var rate = def, label = "taux relevé le " + defLabel, last = "thb", price = null;
  var r0 = parseFloat(LS.get("carnet.rate", ""));
  if (r0 >= 10 && r0 <= 100) { rate = r0; label = LS.get("carnet.rate.d", "taux réglé à la main"); }
  function fmt(x, max) { try { return x.toLocaleString("fr-FR", { maximumFractionDigits: max }); } catch (e) { return String(Math.round(x * Math.pow(10, max)) / Math.pow(10, max)).replace(".", ","); } }
  function num(s) { var n = parseFloat(String(s).replace(/[\s  ]/g, "").replace(",", ".")); return isFinite(n) && n >= 0 ? n : NaN; }
  function paintRate() {
    rateEl.textContent = "";
    var b = document.createElement("b"), s = document.createElement("span");
    b.textContent = fmt(rate, 2) + " ฿"; s.textContent = " · " + label;
    rateEl.appendChild(document.createTextNode("1 € = ")); rateEl.appendChild(b); rateEl.appendChild(s);
    $$("#c-ref [data-b]").forEach(function (e) { e.textContent = fmt(parseFloat(e.getAttribute("data-b")) / rate, 2) + " €"; });
    $$("#c-ref [data-e]").forEach(function (e) { e.textContent = fmt(parseFloat(e.getAttribute("data-e")) * rate, 0) + " ฿"; });
  }
  function paintPrice() {
    var n = num(thb.value), t = isFinite(n) ? thaiNum(Math.round(n)) : null;
    if (!t) { price = null; none.hidden = false; sayIn.hidden = true; none.textContent = isFinite(n) && n > 999999 ? "C’est un très gros montant : essaie avec moins de 1 000 000 ฿." : "Tape un montant en baht, il s’écrira ici en thaï."; return; }
    price = { th: t.th + "บาท", rom: t.rom + " baht", n: Math.round(n) };
    none.hidden = true; sayIn.hidden = false; thEl.textContent = price.th; roEl.textContent = price.rom;
  }
  function recalc() {
    if (last === "thb") { var n = num(thb.value); eur.value = isFinite(n) ? fmt(n / rate, 2) : ""; }
    else { var m = num(eur.value); if (isFinite(m)) { var v = m * rate; thb.value = fmt(v, v >= 100 ? 0 : 1); } else thb.value = ""; }
    paintPrice();
  }
  thb.addEventListener("input", function () { last = "thb"; recalc(); });
  eur.addEventListener("input", function () { last = "eur"; recalc(); });
  $$("[data-quick]").forEach(function (b) { b.addEventListener("click", function () { last = "thb"; thb.value = fmt(parseFloat(b.getAttribute("data-quick")), 0); recalc(); }); });
  $("#c-edit").addEventListener("click", function () { redit.hidden = !redit.hidden; if (!redit.hidden) { rin.value = fmt(rate, 2); try { rin.focus(); rin.select(); } catch (e) {} } });
  $("#c-rok").addEventListener("click", function () {
    var r = num(rin.value);
    if (!(r >= 10 && r <= 100)) { toast("Choisis un taux entre 10 et 100 ฿ pour 1 €"); return; }
    rate = r; var d = ""; try { d = new Date().toLocaleDateString("fr-FR", { day: "numeric", month: "long" }); } catch (e) {}
    label = "taux réglé à la main" + (d ? " le " + d : "");
    LS.set("carnet.rate", String(r)); LS.set("carnet.rate.d", label);
    redit.hidden = true; paintRate(); recalc(); toast("Taux enregistré");
  });
  $("#c-rreset").addEventListener("click", function () {
    rate = def; label = "taux relevé le " + defLabel; LS.del("carnet.rate"); LS.del("carnet.rate.d");
    redit.hidden = true; paintRate(); recalc(); toast("Taux de départ remis");
  });
  $("#c-show").addEventListener("click", function () { if (price) Show.open({ th: price.th, rom: price.rom, fr: fmt(price.n, 0) + " ฿", np: true }, this); });
  $("#c-say-btn").addEventListener("click", function () { if (price) say(price.th, this); });
  paintRate(); paintPrice();
})();
paintPol();

/*@GAMES@*/

/* ───────────── démarrage ───────────── */
DB.keys().then(function (keys) {
  keys.forEach(function (k) { hasPhoto[k] = true; paintChip(k); });
  updateCount();
}, function () {});
updateCount();
try { route(); } catch (e) { var hv = $("#v-home"); if (hv) hv.hidden = false; }
})();
