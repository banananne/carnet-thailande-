  /* Ce fichier est collé dans games.js (à la place de « @TRANS@ ») : il partage ses outils ($, $$, LS, toast, setStatus, copyText, jget, jset…).
     LE TRADUCTEUR EST LA SEULE PAGE QUI ENVOIE QUELQUE CHOSE SUR INTERNET : le texte tapé, uniquement quand on touche « Traduire » et que
     la phrase n'est pas déjà dans les phrases toutes prêtes. Il est d'abord envoyé à Google Traduction, puis à MyMemory si le premier ne répond pas.
     Rien d'autre n'est envoyé (pas de prénom, pas d'identifiant, pas d'adresse de page : referrerPolicy « no-referrer », pas de cookie).
     Les dernières traductions (8 au maximum) sont gardées sur le téléphone (clé « carnet.trad »). */
  var Trad = (function () {
    var v = $("#v-trad");
    if (!v) return { enter: function () {} };
    var KEY = "carnet.trad", DIRK = "carnet.trad.dir", RECENT_MAX = 8, TIMEOUT = 9000;
    var inp = $("#tr-in"), lab = $("#tr-lab"), go = $("#tr-go"), clr = $("#tr-clear"), st = $("#tr-st"), out = $("#tr-out");
    var q = $("#tr-q"), none = $("#tr-none"), recent = $("#tr-recent"), recentL = $("#tr-recent-l");
    var MAX = (v.getAttribute("data-max") || "200,120").split(",").map(Number);
    var TH_RE = /[฀-๿]/, LAT_RE = /[A-Za-zÀ-ÿ]/;
    var dir = LS.get(DIRK, "fr") === "th" ? "th" : "fr", token = 0, last = null;

    /* ── comparer sans se soucier des accents, des majuscules, de la ponctuation ni des petits mots polis ── */
    function norm(s) {
      return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/œ/g, "oe").replace(/æ/g, "ae")
        .replace(/[^a-z0-9฀-๿]+/g, " ").replace(/\s+/g, " ").trim();
    }
    function thKey(s) { return String(s || "").replace(/[\s.!?…]+/g, "").replace(/(นะคะ|นะครับ|ครับ|ค่ะ|คะ|นะ)+$/, ""); }

    /* ── l'index des phrases connues (le recueil de cette page + le lexique) ── */
    var idx = [];
    $$("#v-trad .lx-main, #v-lexique .lx-main").forEach(function (b) {
      var fr = (b.getAttribute("data-fr") || "").replace(/[«»]/g, "").trim(), th = b.getAttribute("data-th") || "";
      if (!fr || !th) return;
      var rec = { th: th, rom: b.getAttribute("data-rom") || "", fr: fr, np: b.hasAttribute("data-np"), q: b.getAttribute("data-q") === "1", t: thKey(th) };
      var seen = {};
      fr.split(/\s*,\s*|\s+\/\s+/).concat([fr]).forEach(function (alt) { var k = norm(alt); if (k && !seen[k]) { seen[k] = 1; idx.push({ k: k, rec: rec }); } });
    });
    function known(text, d) {
      if (d === "fr") { var k = norm(text); for (var i = 0; i < idx.length; i++) if (idx[i].k === k) return idx[i].rec; return null; }
      var t = thKey(text); if (!t) return null;
      for (var j = 0; j < idx.length; j++) if (idx[j].rec.t === t) return idx[j].rec;
      return null;
    }

    /* ── appels réseau (le texte part ici, et seulement ici) ── */
    function getJson(url) {
      return new Promise(function (resolve, reject) {
        var ctl = window.AbortController ? new AbortController() : null, done = false;
        var tm = setTimeout(function () { if (done) return; done = true; try { if (ctl) ctl.abort(); } catch (e) {} reject(new Error("délai dépassé")); }, TIMEOUT);
        var opts = { cache: "no-store", credentials: "omit", referrerPolicy: "no-referrer" };
        if (ctl) opts.signal = ctl.signal;
        fetch(url, opts).then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); })
          .then(function (j) { if (done) return; done = true; clearTimeout(tm); resolve(j); },
                function (e) { if (done) return; done = true; clearTimeout(tm); reject(e); });
      });
    }
    function unent(s) { var t = document.createElement("textarea"); t.innerHTML = String(s).replace(/</g, "&lt;"); return t.value; }
    function viaGoogle(text, d) {
      var url = "https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&dt=rm&sl=" + (d === "fr" ? "fr&tl=th" : "th&tl=fr") + "&q=" + encodeURIComponent(text);
      return getJson(url).then(function (j) {
        var segs = j && j[0] instanceof Array ? j[0] : [], t = "", rom = [];
        segs.forEach(function (s) {
          if (!(s instanceof Array)) return;
          if (typeof s[0] === "string") t += s[0];
          else { var r = d === "fr" ? s[2] : s[3]; if (typeof r === "string" && r.trim()) rom.push(r.trim()); }   /* la ligne de prononciation (écriture latine du thaï) */
        });
        return { text: t.trim(), rom: rom.join(" "), via: "Google Traduction" };
      });
    }
    function viaMyMemory(text, d) {
      var url = "https://api.mymemory.translated.net/get?langpair=" + (d === "fr" ? "fr%7Cth" : "th%7Cfr") + "&q=" + encodeURIComponent(text);
      return getJson(url).then(function (j) {
        var rd = j && j.responseData, t = rd && typeof rd.translatedText === "string" ? rd.translatedText : "", code = Number(j && j.responseStatus);
        if ((j && j.quotaFinished) || (code && code !== 200) || /MYMEMORY WARNING|INVALID LANGUAGE|PLEASE SELECT/i.test(t)) throw new Error("service refusé");
        return { text: unent(t).trim(), rom: "", via: "MyMemory" };
      });
    }
    function plausible(r, text, d) {
      if (!r || !r.text || norm(r.text) === norm(text)) return false;
      return d === "fr" ? TH_RE.test(r.text) : LAT_RE.test(r.text);
    }
    function utf8len(s) { try { return new TextEncoder().encode(s).length; } catch (e) { return s.length * 3; } }
    function online(text, d) {
      return viaGoogle(text, d).then(function (r) { if (!plausible(r, text, d)) throw new Error("réponse vide"); return r; })
        .catch(function () {
          if (utf8len(text) > 480) throw new Error("trop long");        /* MyMemory refuse plus de 500 octets */
          return viaMyMemory(text, d).then(function (r) { if (!plausible(r, text, d)) throw new Error("réponse vide"); return r; });
        });
    }

    /* ── l'écran ── */
    function paintDir() {
      $$("[data-tdir]", v).forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-tdir") === dir ? "true" : "false"); });
      lab.textContent = dir === "fr" ? "Ta phrase en français" : "La phrase en thaï (colle-la ou écris-la)";
      inp.lang = dir; inp.maxLength = dir === "fr" ? MAX[0] : MAX[1];
      inp.placeholder = dir === "fr" ? "Ex. : Où est la station de métro ?" : "Ex. : สถานีรถไฟฟ้าอยู่ที่ไหน";
      if (inp.value.length > inp.maxLength) inp.value = inp.value.slice(0, inp.maxLength);
    }
    function busy(on) { go.disabled = on; go.setAttribute("aria-busy", on ? "true" : "false"); }
    function show(o) {
      last = o;
      $("#tr-th").textContent = o.th; $("#tr-rom").textContent = o.rom || ""; $("#tr-rom").hidden = !o.rom; $("#tr-fr").textContent = o.fr;
      $("#tr-src").textContent = o.src;
      out.setAttribute("data-dir", o.dir);
      var sayB = $("#tr-say"), showB = $("#tr-show");
      [sayB, showB].forEach(function (b) {
        b.setAttribute("data-th", o.th); b.setAttribute("data-q", o.q ? "1" : "0");
        if (o.np) b.setAttribute("data-np", ""); else b.removeAttribute("data-np");
      });
      showB.setAttribute("data-rom", o.rom || ""); showB.setAttribute("data-fr", o.fr);
      $("#tr-warn").hidden = !o.mt;
      out.hidden = false;
      try { out.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }); } catch (e) {}
    }
    function hide() { out.hidden = true; last = null; }

    /* ── les dernières traductions ── */
    function loadRecent() {
      var a = jget(KEY, []);
      return (a instanceof Array ? a : []).filter(function (x) { return x && typeof x.th === "string" && typeof x.fr === "string"; }).slice(0, RECENT_MAX);
    }
    function paintRecent() {
      var a = loadRecent(); recent.hidden = !a.length; recentL.innerHTML = "";
      a.forEach(function (x) {
        var li = document.createElement("li"); li.className = "lx long";
        var b = document.createElement("button"); b.type = "button"; b.className = "lx-main";
        b.setAttribute("data-show", ""); b.setAttribute("data-th", x.th); b.setAttribute("data-rom", x.rom || ""); b.setAttribute("data-fr", x.fr);
        b.setAttribute("data-q", x.q ? "1" : "0"); if (x.np) b.setAttribute("data-np", ""); b.setAttribute("aria-label", "Montrer en grand : " + x.fr);
        [["fr", x.fr], ["rom", x.rom || ""], ["th", x.th]].forEach(function (p) { var s = document.createElement("span"); s.className = p[0]; s.textContent = p[1]; if (p[0] === "th") s.lang = "th"; b.appendChild(s); });
        var sb = document.createElement("button"); sb.type = "button"; sb.className = "lx-say"; sb.setAttribute("data-say", ""); sb.setAttribute("data-th", x.th);
        sb.setAttribute("data-q", x.q ? "1" : "0"); if (x.np) sb.setAttribute("data-np", ""); sb.setAttribute("aria-label", "Écouter : " + x.fr);
        sb.innerHTML = (document.querySelector("#tr-say svg") || { outerHTML: "" }).outerHTML;
        li.appendChild(b); li.appendChild(sb); recentL.appendChild(li);
      });
    }
    function remember(o) {
      var a = loadRecent().filter(function (x) { return !(x.th === o.th && x.fr === o.fr); });
      a.unshift({ fr: o.fr, th: o.th, rom: o.rom || "", q: !!o.q, np: !!o.np });
      jset(KEY, a.slice(0, RECENT_MAX)); paintRecent();
    }

    /* ── traduire ── */
    function run() {
      var text = inp.value.replace(/\s+/g, " ").trim();
      if (!text) { setStatus(st, "warn", "Écris d’abord quelques mots."); try { inp.focus(); } catch (e) {} return; }
      var my = ++token, d = dir, hit = known(text, d);
      if (hit) {        /* phrase déjà connue : réponse immédiate, sans réseau */
        busy(false); setStatus(st, "ok", "Phrase toute prête : elle marche sans réseau.");
        var o = { th: hit.th, rom: hit.rom, fr: hit.fr, np: hit.np, q: hit.q, src: "Phrase toute prête · sans réseau", mt: false, dir: d };
        show(o); remember(o); return;
      }
      if (navigator.onLine === false) {
        busy(false); hide();
        setStatus(st, "bad", "Pas de réseau pour l’instant. Les phrases toutes prêtes, plus bas, marchent sans réseau.");
        return;
      }
      hide(); busy(true); setStatus(st, "", "Traduction en cours…");
      online(text, d).then(function (r) {
        if (my !== token) return;
        busy(false); setStatus(st, "ok", "Traduit.");
        var th = d === "fr" ? r.text : text, fr = d === "fr" ? text : r.text;
        var o = { th: th, rom: r.rom, fr: fr, np: true, q: false, src: "Traduction en ligne · " + r.via, mt: true, dir: d };
        show(o); remember(o);
      }, function () {
        if (my !== token) return;
        busy(false);
        setStatus(st, "bad", navigator.onLine === false ? "Pas de réseau pour l’instant. Les phrases toutes prêtes, plus bas, marchent sans réseau."
          : "La traduction n’a pas répondu. Réessaie dans un instant, avec une phrase plus courte, ou choisis une phrase toute prête plus bas.");
      });
    }

    /* ── les boutons ── */
    go.addEventListener("click", run);
    inp.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); run(); } });
    inp.addEventListener("input", function () { setStatus(st, "", ""); });
    clr.addEventListener("click", function () { token++; busy(false); inp.value = ""; setStatus(st, "", ""); hide(); try { inp.focus(); } catch (e) {} });
    $$("[data-tdir]", v).forEach(function (b) {
      b.addEventListener("click", function () {
        var d = b.getAttribute("data-tdir"); if (d === dir) return;
        dir = d; LS.set(DIRK, d); token++; busy(false); hide(); setStatus(st, "", ""); paintDir();
      });
    });
    $("#tr-copy").addEventListener("click", function () {
      if (!last) return;
      copyText(last.dir === "fr" ? last.th : last.fr, "Copié");
    });
    twoTap($("#tr-recent-x"), "Sûr ? Touche encore pour vider la liste", function () { LS.del(KEY); paintRecent(); toast("Liste vidée"); });

    /* ── la recherche dans les phrases toutes prêtes ── */
    var rows = $$("#tr-book .lx", v).map(function (li) {
      var b = $(".lx-main", li);
      return { li: li, h: norm((b.getAttribute("data-fr") || "") + " " + (b.getAttribute("data-rom") || "")) + " " + thKey(b.getAttribute("data-th")) };
    });
    var groups = $$("#tr-book .trg", v);
    function filter() {
      var raw = q.value, k = norm(raw), tk = thKey(raw), toks = k ? k.split(" ") : [], n = 0;
      rows.forEach(function (r) {
        var ok = !toks.length || toks.every(function (t) { return r.h.indexOf(t) >= 0; }) || (tk && TH_RE.test(tk) && r.h.indexOf(tk) >= 0);
        r.li.hidden = !ok; if (ok) n++;
      });
      groups.forEach(function (g) {
        var all = $$(".lx", g), shown = all.filter(function (li) { return !li.hidden; }).length, nb = $(".trg-n", g);
        g.hidden = !shown;
        g.open = toks.length ? shown > 0 : false;
        if (nb) nb.textContent = String(toks.length ? shown : all.length);   /* pendant une recherche, le badge compte les phrases trouvées */
      });
      none.hidden = !(toks.length && !n);
    }
    q.addEventListener("input", filter);
    q.addEventListener("search", filter);

    paintDir(); paintRecent();
    return { enter: function () { dir = LS.get(DIRK, "fr") === "th" ? "th" : "fr"; paintDir(); paintRecent(); } };
  })();
