  /* ───────────── étape 5 : les enveloppes secrètes (code personnel, serment, mission, révélation) ─────────────
     Ce fichier est collé dans games.js (à la place de « @ENV@ ») : il partage ses outils ($, $$, LS, toast, jget, jset, buzz, nb, twoTap, Confetti).
     Les missions sont publiées CHIFFRÉES (une enveloppe par personne et par vague : PBKDF2-SHA256 puis AES-GCM). Sans le code de la carte glissée
     dans le carnet, le fichier du site ne contient rien de lisible. L'heure d'ouverture est celle du téléphone : c'est un jeu, pas un coffre-fort.
     Tout reste sur le téléphone ; ce que le jeu y garde (le score, ce qui a déjà été vu) est effacé à la fin de chaque vague.
     Le code, lui, n'est JAMAIS gardé : on le retape à chaque ouverture de l'enveloppe, au cas où quelqu'un attraperait le téléphone d'un autre.
     Le « mot secret » du mode essai (carnet.open) n'ouvre JAMAIS une enveloppe. */
  var Env = (function () {
    var nop = { paint: function () {}, enter: function () {} };
    var box = $("#env"), dataEl = $("#env-data");
    if (!box || !dataEl) return nop;
    var D = null;
    try { D = JSON.parse(dataEl.textContent); } catch (e) { return nop; }
    if (!D || !D.win) return nop;
    var WIN = D.win, ITER = D.it || 150000, WAVES = ["w1", "w2", "w3"];
    var MAS = { boop: "Boop", minou: "Minou", moomoo: "Moomoo", aftonsparv: "Aftonsparv" };
    var IDLE = 60000, HOLD = 1000;   /* la carte se cache toute seule après une minute sans toucher */
    function G(id) { return document.getElementById(id); }
    var el = {
      x: G("env-x"), scroll: G("env-scroll"), barI: G("env-bar-i"), bar: $(".env-bar", box),
      code: G("envp-code"), chut: G("envp-chut"), card: G("envp-card"), sealed: G("envp-sealed"), rev: G("envp-rev"), bad: G("envp-bad"),
      form: G("env-form"), inp: G("env-in"), err: G("env-err"), go: G("env-go"), simHint: G("env-simhint"), simCode: G("env-simcode"), fill: G("env-fill"),
      chutPics: G("chut-pics"), chutKick: G("chut-kick"), chutTxt: G("chut-txt"), hold: G("env-hold"),
      cardKick: G("card-kick"), cardCtx: G("card-ctx"), cardIntro: G("card-intro"), cardSay: G("card-say"), cardTitle: G("card-title"), cardItems: G("card-items"), cardFoot: G("card-foot"),
      cardFin: G("card-fin"), cardFinD: G("card-fin-d"), cardFinH: G("card-fin-h"), cardClose: G("card-close"),
      sealedP: G("sealed-p"), sealedOpen: G("sealed-open"), sealedRev: G("sealed-rev"),
      revSay: G("rev-say"), revTitle: G("rev-title"), revTbl: G("rev-tbl"), revScore: G("rev-score"), revClose: G("rev-close"),
      badP: G("bad-p"), badClose: G("bad-close"),
      dock: G("env-dock"), edWord: G("ed-word"), edOk: G("ed-ok"), edSkip: G("ed-skip"), edN: G("ed-n"), edNl: G("ed-nl"), edUndo: G("ed-undo"), edQ: G("ed-q"), edQb: G("ed-qb"), edQt: G("ed-qt")
    };
    var PANES = ["code", "chut", "card", "sealed", "rev", "bad"];

    /* ── petits outils ── */
    function mk(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = nb(text); return e; }
    function normCode(w) {   /* même règle que le build : sans accents ni majuscules, lettres et chiffres seulement */
      var t = String(w);
      try { t = t.normalize("NFD"); } catch (e) {}
      return t.replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");
    }
    function unb64(s) { var b = atob(s), u = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; }
    function nowKey() { var d = new Date(); return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate()) + "T" + pad2(d.getHours()) + ":" + pad2(d.getMinutes()); }
    function hhmm(w) { var t = (WIN[w] || ["", "", ""])[1]; var h = parseInt(t.slice(11, 13), 10), m = t.slice(14, 16); return h + " h" + (m === "00" ? "" : " " + m); }
    var DAYS = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
    var MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
    function finOf(w) {   /* « fin de la mission » = l'heure de la révélation du calendrier public : l'encadré ne peut pas le contredire */
      var t = (WIN[w] || [])[1]; if (!t) return null;
      var y = +t.slice(0, 4), mo = +t.slice(5, 7), d = +t.slice(8, 10), dt = new Date(y, mo - 1, d);
      if (!y || !mo || !d || isNaN(dt.getTime())) return null;
      return { day: DAYS[dt.getDay()] + " " + (d === 1 ? "1er" : d) + " " + MONTHS[mo - 1], hour: hhmm(w) };
    }
    function sweep(prefix) {
      try { for (var i = localStorage.length - 1; i >= 0; i--) { var k = localStorage.key(i); if (k && k.indexOf(prefix) === 0) localStorage.removeItem(k); } } catch (e) {}
    }

    /* ── chiffrement : tout se passe sur le téléphone, avec WebCrypto ── */
    var subtle = null, enc = null, dec = null;
    try { subtle = (window.crypto && window.crypto.subtle) || null; enc = new TextEncoder(); dec = new TextDecoder("utf-8"); } catch (e) { subtle = null; }
    var CAN = !!(subtle && enc && dec && window.Promise && window.Uint8Array);
    function derive(code, saltB64) {
      return Promise.resolve().then(function () {
        return subtle.importKey("raw", enc.encode(normCode(code)), "PBKDF2", false, ["deriveBits"]);
      }).then(function (k) {
        return subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt: unb64(saltB64), iterations: ITER }, k, 256);
      }).then(function (bits) { return new Uint8Array(bits); });
    }
    function openBlob(c, n, w, rawKey) {   /* → la mission en clair ; la promesse est refusée si le code est faux */
      return Promise.resolve().then(function () {
        var blob = blobOf(c, n, w);
        return subtle.importKey("raw", rawKey, "AES-GCM", false, ["decrypt"]).then(function (k) {
          return subtle.decrypt({ name: "AES-GCM", iv: unb64(blob.iv), additionalData: enc.encode(w + "|" + n), tagLength: 128 }, k, unb64(blob.ct));
        });
      }).then(function (pt) { return JSON.parse(dec.decode(pt)); });
    }

    /* ── deux contextes : le vrai jeu (prénom de l'accueil, heure du téléphone) et l'essai (Mangue, heure choisie sur la page d'essai) ── */
    var simSel = (function () {
      var s = String(LS.get("carnet.sim.sel", "1:1")).split(":"), w = +s[0], t = +s[1];
      return { w: w >= 1 && w <= 3 ? w : 1, t: t >= 0 && t <= 3 ? t : 1 };
    })();
    /* phase : 0 pas encore, 1 le jeu est ouvert, 2 l'heure de la révélation est passée, 3 c'est fini (tout est effacé) */
    var REAL = { sim: false, ns: "carnet.env", data: D.real, who: function () { return LS.get("carnet.who", ""); },
      phase: function (w) { var n = nowKey(), t = WIN[w]; return n < t[0] ? 0 : n < t[1] ? 1 : n < t[2] ? 2 : 3; } };
    var SIM = { sim: true, ns: "carnet.sim", data: D.sim || null, who: function () { return D.simWho; }, phase: function () { return simSel.t; } };
    function blobOf(c, n, w) { var d = c.data; return (d && d.b && d.b[n] && d.b[n][w]) || null; }
    function names(c) { return c.data && c.data.b ? Object.keys(c.data.b) : []; }
    function waveOf(c) {   /* le jeu dont l'enveloppe est à voir maintenant ("" : aucun) */
      if (!c.data) return "";
      var n = c.who(), list = c.sim ? ["w" + simSel.w] : WAVES;
      for (var i = 0; i < list.length; i++) { var p = c.phase(list[i]); if ((p === 1 || p === 2) && blobOf(c, n, list[i])) return list[i]; }
      return "";
    }
    function wipe(c) {   /* à la fin de chaque vague : le score et les traces s'effacent */
      if (!c.data) return;
      WAVES.forEach(function (w) {
        if (c.phase(w) === 3) names(c).forEach(function (n) { ["h", "o", "r"].forEach(function (k) { LS.del(c.ns + "." + k + "." + n + "." + w); }); });
      });
    }
    sweep("carnet.env.k."); sweep("carnet.sim.k.");   /* une ancienne version gardait la clé tirée du code : plus aucune clé ne reste sur le téléphone */

    /* ── l'enveloppe ouverte à l'écran ── */
    var sess = 0, ctx = null, nm = "", wave = "", ph = 0, cur = null, pn = "", idleT = 0, lastPoke = 0, lastFocus = null, lastQ = -1, holdT = 0;

    function dockSize() { try { box.style.setProperty("--dock-h", el.dock.offsetHeight + "px"); } catch (e) {} }   /* la mission défile au-dessus du tableau de bord */
    function pane(n) {
      pn = n;
      PANES.forEach(function (p) { el[p].hidden = p !== n; });
      var dock = n === "card" && !!(cur && cur.hunt);
      el.dock.hidden = !dock; box.classList.toggle("has-dock", dock);
      if (dock) dockSize();
      el.bar.hidden = !(n === "chut" || n === "card");
      el.scroll.scrollTop = 0;
      var f = n === "code" ? el.inp : n === "chut" ? el.chutTxt : n === "card" ? el.cardKick : $("h2", el[n]);
      try { if (f) f.focus({ preventScroll: true }); } catch (e) {}
    }
    function pics(root, keys) {
      root.textContent = "";
      keys.forEach(function (k) {
        if (!MAS[k]) return;      /* seules les quatre mascottes connues ont une image */
        var i = document.createElement("img"); i.className = "env-mas"; i.src = "img/doudou_" + k + ".webp"; i.alt = MAS[k]; i.decoding = "async";
        root.appendChild(i);
      });
    }
    function paintSay(root, say) {
      root.textContent = "";
      (say || []).forEach(function (s) {
        var keys = String(s[0]).split("+"), row = mk("div", "env-sp"), pc = mk("div", "env-pics"), bub = mk("div", "env-bub");
        pics(pc, keys);
        bub.appendChild(mk("b", "", keys.map(function (k) { return MAS[k] || k; }).join(" et "))); bub.appendChild(mk("p", "", s[1]));
        row.appendChild(pc); row.appendChild(bub); root.appendChild(row);
      });
    }
    function wipeDom() {   /* la mission ne reste jamais dans la page quand l'enveloppe est refermée */
      [el.cardSay, el.cardIntro, el.cardItems, el.revSay, el.revTbl, el.chutPics].forEach(function (e) { e.textContent = ""; });
      [el.cardKick, el.cardTitle, el.cardFoot, el.cardFinD, el.cardFinH, el.chutKick, el.chutTxt, el.revTitle, el.revScore, el.edWord, el.edQt].forEach(function (e) { e.textContent = ""; });
    }
    function bad(msg) { el.badP.textContent = nb(msg); pane("bad"); }

    function start(c) {
      var w = waveOf(c);
      if (!w) { paint(); return; }
      sess++; ctx = c; wave = w; nm = c.who(); ph = c.phase(w); cur = null;
      lastFocus = document.activeElement;
      box.hidden = false; document.documentElement.classList.add("env-open");
      if (!CAN) { bad("Cet appareil est trop ancien pour ouvrir les enveloppes. Pas de panique : tout se fera à l’oral, à table."); return; }
      showCode("");   /* toujours : le code se retape à chaque ouverture */
    }
    function showCode(msg) {
      el.err.textContent = msg ? nb(msg) : "";
      el.go.disabled = false; el.go.textContent = nb("Ouvrir");
      el.simHint.hidden = !ctx.sim; el.simCode.textContent = D.simCode || "";
      pane("code");
    }
    function sworn() { return LS.get(ctx.ns + ".o." + nm + "." + wave, "") === "1"; }
    function arrive(p) {   /* la mission est lue : serment (la 1re fois seulement) avant l'heure des aveux, révélation après */
      cur = p; ph = ctx.phase(wave);
      if (ph === 3) { close(); return; }
      if (ph === 2) showReveal(); else if (sworn()) showCard(); else showChut();
    }
    el.form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!ctx) return;
      if (!normCode(el.inp.value)) { el.err.textContent = nb("Écris le code de ta carte."); return; }
      var salt = ctx.data && ctx.data.s && ctx.data.s[nm];
      if (!salt) { bad("Je ne trouve pas ton enveloppe. Dis-le à Anne."); return; }
      var s = sess, c0 = ctx;
      el.go.disabled = true; el.go.textContent = nb("Je vérifie…"); el.err.textContent = "";
      derive(el.inp.value, salt).then(function (k) {
        return openBlob(c0, nm, wave, k);   /* la clé sert une fois, puis elle est oubliée : rien n'est gardé */
      }).then(function (p) {
        if (s !== sess || box.hidden) return;
        el.inp.value = "";
        arrive(p);
      }, function () {
        if (s !== sess || box.hidden) return;
        el.go.disabled = false; el.go.textContent = nb("Ouvrir");
        el.err.textContent = nb("Ce n’est pas le bon code. Vérifie la carte de ton carnet, et ton prénom sur l’accueil.");
        el.form.classList.remove("no"); void el.form.offsetWidth; el.form.classList.add("no");
        try { el.inp.focus(); el.inp.select(); } catch (x) {}
      });
    });
    el.fill.addEventListener("click", function () { el.inp.value = D.simCode || ""; try { el.inp.focus(); } catch (x) {} });
    el.form.addEventListener("animationend", function () { el.form.classList.remove("no"); });

    /* le serment : on maintient le doigt une seconde */
    function holdReset() { clearTimeout(holdT); holdT = 0; el.hold.classList.remove("on"); }
    function holdStart() {
      if (holdT) return;
      el.hold.classList.add("on");
      holdT = setTimeout(function () { holdT = 0; el.hold.classList.remove("on"); buzz(40); showCard(); }, HOLD);
    }
    el.hold.addEventListener("pointerdown", function (e) {
      if (e.button) return;
      try { el.hold.setPointerCapture(e.pointerId); } catch (x) {}
      holdStart();
    });
    ["pointerup", "pointercancel", "lostpointercapture"].forEach(function (t) { el.hold.addEventListener(t, holdReset); });
    el.hold.addEventListener("contextmenu", function (e) { e.preventDefault(); });
    el.hold.addEventListener("click", function (e) { if (e.detail === 0 && cur) { holdReset(); showCard(); } });   /* clavier ou lecteur d'écran : un appui suffit */
    function showChut() {
      pics(el.chutPics, cur.m || []);
      el.chutKick.textContent = nb(cur.kick || ""); el.chutTxt.textContent = nb(cur.chut || "");
      holdReset(); pane("chut"); armIdle();
    }

    /* la mission */
    function showCard() {
      var p = cur; if (!p) return;
      el.cardKick.textContent = nb(p.kick || "");
      el.cardIntro.textContent = "";
      (p.intro || []).forEach(function (t) { el.cardIntro.appendChild(mk("p", "", t)); });
      el.cardCtx.hidden = !(p.intro && p.intro.length);
      paintSay(el.cardSay, p.say); el.cardTitle.textContent = nb(p.title || "");
      el.cardItems.textContent = "";
      (p.items || []).forEach(function (t) { el.cardItems.appendChild(mk("li", "", t)); });
      el.cardFoot.textContent = nb(p.foot || ""); el.cardFoot.hidden = !p.foot;
      var fin = finOf(wave); el.cardFin.hidden = !fin;
      if (fin) { el.cardFinD.textContent = nb(fin.day); el.cardFinH.textContent = nb(fin.hour); }
      LS.set(ctx.ns + ".o." + nm + "." + wave, "1");
      if (p.hunt) dockPaint("");
      pane("card"); armIdle();
    }
    function showSealed() {
      ph = ctx.phase(wave);
      el.sealedP.textContent = nb(ph === 2 ? "L’heure de la révélation est arrivée." : "Elle se referme toute seule. La révélation aura lieu vers " + hhmm(wave) + ", à table.");
      el.sealedOpen.hidden = ph === 2; el.sealedRev.hidden = ph !== 2;
      pane("sealed");
    }
    function lock() {   /* la mission disparaît de l'écran ET de la mémoire de la page ; pour rouvrir, il faut retaper le code */
      clearTimeout(idleT); holdReset(); cur = null; wipeDom();
      if (!ctx || box.hidden) return;
      showSealed();
    }
    function reopen() { showCode(""); }
    function showReveal() {
      var r = cur.rev || {};
      paintSay(el.revSay, r.say); el.revTitle.textContent = nb(r.title || "");
      el.revTbl.textContent = "";
      var cols = r.cols || [], head = mk("tr"), me = nm;
      cols.forEach(function (t) { head.appendChild(mk("th", "", t)); });
      var th = mk("thead"); th.appendChild(head); el.revTbl.appendChild(th);
      var tb = mk("tbody");
      (r.rows || []).forEach(function (row) {
        var tr = mk("tr", row[0] === me ? "me" : "");
        row.forEach(function (t) { tr.appendChild(mk("td", "", t)); });
        tb.appendChild(tr);
      });
      el.revTbl.appendChild(tb);
      if (cur.hunt) { var s = hget(); el.revScore.textContent = nb("Ton score : " + s.n + (s.n > 1 ? " mots dits" : " mot dit") + ". À toi de l’annoncer à table !"); el.revScore.hidden = false; }
      else { el.revScore.hidden = true; el.revScore.textContent = ""; }
      LS.set(ctx.ns + ".r." + nm + "." + wave, "1");
      pane("rev"); clearTimeout(idleT);
      try { Confetti.burst(); } catch (e) {}
    }
    function close() {
      sess++; clearTimeout(idleT); holdReset(); cur = null; wipeDom();
      el.inp.value = ""; el.err.textContent = ""; el.edQt.textContent = "";
      box.hidden = true; document.documentElement.classList.remove("env-open"); box.classList.remove("has-dock");
      try { if (lastFocus && lastFocus.focus && document.body.contains(lastFocus)) lastFocus.focus({ preventScroll: true }); } catch (e) {}
      lastFocus = null;
      paint(); simPaint();
    }

    /* l'enveloppe se referme toute seule si on ne touche plus rien, et dès qu'on quitte l'appli */
    function armIdle() {
      clearTimeout(idleT); lastPoke = Date.now();
      var i = el.barI; i.style.transition = "none"; i.style.transform = "scaleX(1)"; void i.offsetWidth;
      i.style.transition = "transform " + IDLE + "ms linear"; i.style.transform = "scaleX(0)";
      idleT = setTimeout(lock, IDLE);
    }
    function poke() { if ((pn === "card" || pn === "chut") && Date.now() - lastPoke > 800) armIdle(); }
    box.addEventListener("pointerdown", poke, true);
    box.addEventListener("keydown", function (e) { if (e.key === "Escape") { close(); return; } poke(); }, true);
    el.scroll.addEventListener("scroll", poke, { passive: true });
    document.addEventListener("visibilitychange", function () { if (document.hidden && !box.hidden) close(); });
    window.addEventListener("pagehide", function () { if (!box.hidden) close(); });
    el.x.addEventListener("click", close);
    el.cardClose.addEventListener("click", lock);
    el.sealedOpen.addEventListener("click", reopen);
    el.sealedRev.addEventListener("click", reopen);
    el.revClose.addEventListener("click", close);
    el.badClose.addEventListener("click", close);

    /* ── la chasse aux mots (vague 2) : « Mot dit ! », « Passer ce mot », « Annuler le dernier » ── */
    function hkey() { return ctx.ns + ".h." + nm + "." + wave; }
    function hget() {
      var s = jget(hkey(), null);
      if (!s || typeof s.i !== "number" || typeof s.n !== "number" || !(s.h instanceof Array)) s = { i: 0, n: 0, h: [] };
      return s;
    }
    function quip(msg) { el.edQt.textContent = msg ? nb(msg) : ""; el.edQb.hidden = !msg; }
    function dockPaint(msg) {
      var H = cur && cur.hunt; if (!H) return;
      var s = hget(), words = H.words || [], over = s.i >= words.length;
      el.edWord.textContent = over ? "—" : words[s.i];
      el.edOk.disabled = over; el.edSkip.disabled = over; el.edUndo.disabled = !s.h.length;
      el.edN.textContent = s.n; el.edNl.textContent = s.n > 1 ? "mots dits" : "mot dit";
      quip(over ? H.end : msg); dockSize();
    }
    el.edOk.addEventListener("click", function () {
      var H = cur && cur.hunt; if (!H) return;
      var s = hget(); if (s.i >= (H.words || []).length) return;
      s.i++; s.n++; s.h.push("s"); jset(hkey(), s);
      var q = H.quips || [], k = 0;
      if (q.length) { do { k = Math.floor(Math.random() * q.length); } while (k === lastQ && q.length > 1); lastQ = k; }
      buzz(25); dockPaint(q[k] || "");
      if (s.n % 5 === 0) { try { Confetti.burst(null, null, 45); } catch (e) {} }
    });
    el.edSkip.addEventListener("click", function () {
      var H = cur && cur.hunt; if (!H) return;
      var s = hget(); if (s.i >= (H.words || []).length) return;
      s.i++; s.h.push("p"); jset(hkey(), s); dockPaint(H.pass || "");
    });
    el.edUndo.addEventListener("click", function () {
      var H = cur && cur.hunt; if (!H) return;
      var s = hget(), last = s.h.pop(); if (!last) return;
      s.i = Math.max(0, s.i - 1); if (last === "s") s.n = Math.max(0, s.n - 1);
      jset(hkey(), s); dockPaint(H.undo || "");
    });

    /* ── l'accueil : l'enveloppe n'apparaît que pendant le jeu ── */
    var BTN = {   /* le texte du bandeau change selon l'heure et ce qui a déjà été vu */
      fresh: ["Une enveloppe t’attend", "Secrète : pour toi, et seulement pour toi"],
      seen: ["Ton enveloppe secrète", "Touche pour la rouvrir"],
      rev: ["L’heure des aveux", "Touche pour voir la révélation"],
      revSeen: ["La révélation", "Touche pour la revoir"]
    };
    function paintBtn(b, c) {
      if (!b) return;
      var w = waveOf(c);
      b.hidden = !w;
      if (!w) return;
      var n = c.who(), p = c.phase(w), dot = $(".dot", b);
      var seen = LS.get(c.ns + "." + (p === 2 ? "r" : "o") + "." + n + "." + w, "") === "1";
      var t = p === 2 ? (seen ? BTN.revSeen : BTN.rev) : (seen ? BTN.seen : BTN.fresh);
      $("b", b).textContent = nb(t[0]); $("small", b).textContent = nb(t[1]);
      if (dot) dot.hidden = seen;
    }
    function paint() { wipe(REAL); paintBtn($("#env-btn"), REAL); }
    var homeBtn = $("#env-btn"), whoPick = $("#who");
    if (homeBtn) homeBtn.addEventListener("click", function () { start(REAL); });
    if (whoPick) whoPick.addEventListener("click", function () { setTimeout(paint, 0); });   /* un autre prénom : l'enveloppe change aussi */

    /* ── la page d'essai (#/essai) : faux prénom, faux mots, faux code, heure choisie ── */
    var sv = $("#v-essai"), simBtn = $("#sim-env-btn");
    var SIM_W = {
      1: "Tu es Mangue, le gorille de Litchi : trois petites attentions à lui glisser sans te faire repérer. À l’heure des aveux, Boop dévoile tous les gorilles.",
      2: "Tu dois faire dire un mot à Litchi sans que la personne s’en doute. Chaque fois que c’est fait, touche « Mot dit ! » : un autre mot arrive. Essaie aussi « Passer ce mot » et « Annuler le dernier ». Qui en fait dire le plus gagne.",
      3: "Tu joues un rôle toute la journée sans jamais le dire (ici, le ventilateur : on est au chaud, après tout). Au dîner du réveillon, tout le monde devine qui jouait quoi."
    };
    function simTime() {
      var h = hhmm("w" + simSel.w);
      return ["Rien n’apparaît sur l’accueil : personne ne sait que le jeu existe.",
              "Une enveloppe apparaît à côté du prénom, avec un point qui clignote. Touche-la.",
              "À partir de " + h + ", l’enveloppe donne la révélation : qui était qui. Touche-la.",
              "Le lendemain, tout a disparu : plus d’enveloppe, et le téléphone a oublié la mission et le score."][simSel.t];
    }
    function simPaint() {
      if (!sv) return;
      $$("[data-sw]", sv).forEach(function (b) { b.setAttribute("aria-pressed", +b.getAttribute("data-sw") === simSel.w ? "true" : "false"); });
      $$("[data-st]", sv).forEach(function (b) { b.setAttribute("aria-pressed", +b.getAttribute("data-st") === simSel.t ? "true" : "false"); });
      wipe(SIM); paintBtn(simBtn, SIM);
      $("#sim-w-desc").textContent = nb(SIM_W[simSel.w]);
      $("#sim-t-desc").textContent = nb(simTime());
      $("#sim-h-desc").textContent = nb(simBtn.hidden ? "Pas d’enveloppe à cet instant." : "Voici l’accueil de Mangue : l’enveloppe est là. Touche-la.");
    }
    if (sv) {
      sv.addEventListener("click", function (e) {
        var b = e.target.closest ? e.target.closest("[data-sw],[data-st]") : null; if (!b) return;
        if (b.hasAttribute("data-sw")) simSel.w = +b.getAttribute("data-sw"); else simSel.t = +b.getAttribute("data-st");
        LS.set("carnet.sim.sel", simSel.w + ":" + simSel.t); simPaint();
      });
      simBtn.addEventListener("click", function () { start(SIM); });
      twoTap($("#sim-reset"), "Touche encore pour tout effacer", function () {
        sweep("carnet.sim."); simSel.w = 1; simSel.t = 1; LS.set("carnet.sim.sel", "1:1"); simPaint(); toast("Essai remis à zéro");
      });
    }

    /* l'heure avance, même quand l'appli reste ouverte (révélation, fin du jeu) */
    setInterval(function () {
      if (document.hidden) return;
      paint();
      if (box.hidden || !ctx) return;
      var p = ctx.phase(wave);
      if (p === ph) return;
      if (p === 3) { close(); return; }
      ph = p;
      if (pn === "chut" || pn === "card") lock(); else if (pn === "sealed") showSealed();
    }, 20000);

    return {
      paint: function () { paint(); },
      enter: function (name) { if (!box.hidden) close(); paint(); if (name === "essai") simPaint(); }
    };
  })();
