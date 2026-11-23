  /* Ce fichier est collé dans games.js (à la place de « @GAMES2@ ») : il partage ses outils (Cal, Gates, Stamps, Confetti, hub, jget, jset, buzz, twoTap…).
     Tout reste sur le téléphone : défis relevés, mots dits, cases du bingo, notes des plats et prix sont gardés dans le navigateur. */
  var PEOPLE = ["Arthur", "Daphne", "Flo", "Anne"];
  var PCOL = { Arthur: ["#283881", "#FFFFFF"], Daphne: ["#E9A9B8", "#5B1025"], Flo: ["#F2A71B", "#5B1025"], Anne: ["#A51C36", "#FFFFFF"] };
  function me() { var w = LS.get("carnet.who", ""); return PEOPLE.indexOf(w) >= 0 ? w : ""; }
  function jlist(k) { var v = jget(k, []); return v instanceof Array ? v : []; }
  function jobj(k) { var v = jget(k, {}); return v && typeof v === "object" && !(v instanceof Array) ? v : {}; }
  function toggleIn(list, id) { var i = list.indexOf(id); if (i >= 0) list.splice(i, 1); else list.push(id); return i < 0; }
  function plural(n, one, many) { return n + " " + (n > 1 ? many : one); }
  function paintWhoPick(root) { var wp = $(".whopick", root); if (wp) wp.hidden = !!me() || LS.get("carnet.who", "") === "Invité"; }
  /* pastilles « Qui es-tu ? » des jeux : même mémoire que l'accueil */
  document.addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("[data-wp]") : null; if (!b) return;
    LS.set("carnet.who", b.getAttribute("data-wp")); paintWho(); refreshAll();
  });

  /* choix du jour : flèches « avant / après », limité aux jours déjà ouverts */
  function DayNav(view, kind, blocksSel, onSet) {
    var root = $('.dn[data-dn="' + kind + '"]', view), blocks = $$(blocksSel, view);
    var prev = $('[data-step="-1"]', root), next = $('[data-step="1"]', root), bt = $("b", root), st = $("small", root), sel = -1;
    function set(i) {
      var m = Math.max(0, Cal.maxOpen());
      i = Math.max(0, Math.min(i, m, blocks.length - 1)); sel = i;
      blocks.forEach(function (b, k) { b.hidden = k !== i; });
      bt.textContent = blocks[i].getAttribute("data-title");
      st.textContent = "Jour " + (i + 1) + " sur " + blocks.length + (Cal.inTrip() && i === Cal.idxToday() ? " · aujourd’hui" : "");
      prev.disabled = i <= 0; next.disabled = i >= m;
      if (onSet) onSet(i, blocks[i]);
    }
    root.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("[data-step]") : null; if (!b || b.disabled) return;
      set(sel + parseInt(b.getAttribute("data-step"), 10));
    });
    return { set: set, cur: function () { return sel; } };
  }
  function dayFromHash() { var p = (location.hash || "").replace(/^#\/?/, "").split("/"); return days.indexOf(p[1]); }

  /* ───────────── horoscope du jour (accueil) : un seul signe par jour, selon le prénom ───────────── */
  var HomeHoro = (function () {
    var card = $("#hsd");
    if (!card) return { paint: function () {} };
    var SIGN = {}; try { SIGN = JSON.parse(card.getAttribute("data-signs") || "{}"); } catch (e) {}
    var items = $$(".hsd-i", card), skies = $$(".hsd-sky [data-sign]", card), sub = $("#hsd-sub"), wait = $("#hsd-wait"), nav = $("#hsd-nav"), navT = $("#hsd-nav-t");
    var essai = -1;                       /* jour regardé en mode essai (-1 : celui d'aujourd'hui) */
    function idx() { return Cal.master() && essai >= 0 ? essai : Math.max(0, Cal.idxToday()); }
    function paint() {
      var who = me(), sign = who ? SIGN[who] : "";
      card.hidden = !sign;
      if (!sign) return;
      skies.forEach(function (s) { s.hidden = s.getAttribute("data-sign") !== sign; });
      var open = Cal.isOpen("horo"), i = idx(), shown = null;
      items.forEach(function (it) {
        var on = open && it.getAttribute("data-sign") === sign && parseInt(it.getAttribute("data-i"), 10) === i;
        it.hidden = !on; if (on) shown = it;
      });
      wait.hidden = open; wait.textContent = open ? "" : card.getAttribute("data-wait");
      sub.textContent = shown ? shown.getAttribute("data-sub") : "";
      nav.hidden = !(Cal.trying() && open);
      if (shown) navT.textContent = shown.getAttribute("data-sub").split(" · ")[1] || "";
      card.classList.toggle("lucky", !!(shown && shown.hasAttribute("data-lucky")));
    }
    nav.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("[data-hs]") : null; if (!b) return;
      essai = Math.max(0, Math.min(days.length - 1, idx() + parseInt(b.getAttribute("data-hs"), 10))); paint();
    });
    who.addEventListener("click", function () { essai = -1; paint(); });
    paint();
    return { paint: paint };
  })();

  /* ───────────── défi du jour : la mission photo de Minou ───────────── */
  var Defi = (function () {
    var v = $("#v-defi"), KEY = "carnet.defi", done = jlist(KEY);
    var nav = DayNav(v, "defi", ".dfd", function (i, blk) { paintBlock(blk); });
    function paintBlock(blk) {
      var on = done.indexOf(blk.getAttribute("data-id")) >= 0, b = $('[data-df="done"]', blk);
      b.setAttribute("aria-pressed", on ? "true" : "false"); b.classList.toggle("on", on);
      $("span", b).textContent = on ? "Défi relevé !" : "Défi relevé";
      summary();
    }
    function summary() {
      var n = done.filter(function (id) { return days.indexOf(id) >= 0; }).length;
      var t = n ? plural(n, "défi relevé", "défis relevés") + " sur " + days.length : "";
      $("#mis-n").textContent = t || "Aucun défi relevé pour l’instant.";
      $$("#mis-dots i").forEach(function (d, k) { d.classList.toggle("on", done.indexOf(days[k]) >= 0); });
      hub("defi", t);
    }
    v.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest('[data-df="done"]') : null; if (!b) return;
      var blk = b.closest(".dfd"), on = toggleIn(done, blk.getAttribute("data-id"));
      jset(KEY, done); paintBlock(blk);
      if (on) { buzz(20); var c = centerOf(b); Confetti.burst(c.x, c.y, 40); if (done.length >= 5) Stamps.bonus("defi"); }
    });
    function enter() { var k = dayFromHash(); nav.set(k >= 0 ? k : Cal.idxToday()); }
    summary();
    return { enter: enter };
  })();

  /* ───────────── mot du jour (Boop) ───────────── */
  var Mot = (function () {
    var v = $("#v-mot"), KEY = "carnet.mj", said = jlist(KEY);
    var nav = DayNav(v, "mot", "article.mt", function (i, blk) { paintCard(blk); });
    function count() { return said.filter(function (id) { return days.indexOf(id) >= 0; }).length; }
    function summary() {
      var n = count(), t = n ? plural(n, "mot dit", "mots dits") + " sur " + days.length : "";
      $("#mt-n").textContent = t || "Aucun mot dit pour l’instant.";
      hub("mot", t);
    }
    function paintCard(blk) {
      var on = said.indexOf(blk.getAttribute("data-id")) >= 0, b = $('[data-mt="done"]', blk);
      b.setAttribute("aria-pressed", on ? "true" : "false"); b.classList.toggle("on", on);
      $("span", b).textContent = on ? "Dit !" : "Je l’ai dit !";
      summary();
    }
    function paintList() {
      var m = Cal.maxOpen();
      $$("#mtl .lx", v).forEach(function (li) { li.hidden = parseInt(li.getAttribute("data-i"), 10) > m; });
      var n = Math.max(0, m + 1);
      $("#mtl-n").textContent = n ? n + " sur " + days.length : "";
    }
    v.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest('[data-mt="done"]') : null; if (!b) return;
      var blk = b.closest("article.mt"), on = toggleIn(said, blk.getAttribute("data-id"));
      jset(KEY, said); paintCard(blk);
      if (on) { buzz(20); var c = centerOf(b); Confetti.burst(c.x, c.y, 40); if (said.length >= 5) Stamps.bonus("mot"); }
    });
    function enter() { var k = dayFromHash(); nav.set(k >= 0 ? k : Cal.idxToday()); paintList(); }
    summary();
    return { enter: enter };
  })();

  /* ───────────── bingo d'Aftonsparv : 9 cases tirées au sort pour chaque prénom (toujours les mêmes) ───────────── */
  var Bingo = (function () {
    var v = $("#v-bingo"), grid = $("#bg"), KEY = "carnet.bingo", N = 9, items = [], marks = jobj(KEY), cells = [], name = null;
    try { items = JSON.parse(grid.getAttribute("data-items") || "[]"); } catch (e) {}
    var LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]];
    function seed(s) { var h = 0x811c9dc5; for (var i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619) >>> 0; return h; }
    function rng(a) { return function () { a = (a + 0x6D2B79F5) | 0; var t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
    function pick(who) {
      var r = rng(seed("bingo:" + who)), a = items.slice();
      for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; }
      return a.slice(0, N);
    }
    function mine() { var w = me(); if (!(marks[w] instanceof Array)) marks[w] = []; return marks[w]; }
    function build() {
      var who = me();
      if (name === who && cells.length) return;
      name = who; grid.innerHTML = ""; cells = [];
      pick(who).forEach(function (it, i) {
        var b = document.createElement("button"); b.type = "button"; b.className = "bg-c"; b.setAttribute("data-k", it[0]); b.setAttribute("data-i", i);
        b.setAttribute("aria-pressed", "false");
        var s = document.createElement("span"); s.textContent = it[1]; b.appendChild(s); grid.appendChild(b); cells.push(b);
      });
      $("#bg-name").textContent = who ? "La grille de " + who : "Ta grille";
    }
    function done() { var m = mine(); return cells.map(function (c) { return m.indexOf(c.getAttribute("data-k")) >= 0; }); }
    function wins(d) { return LINES.filter(function (l) { return d[l[0]] && d[l[1]] && d[l[2]]; }); }
    function paint(quiet) {
      var d = done(), w = wins(d), inLine = {};
      w.forEach(function (l) { l.forEach(function (i) { inLine[i] = 1; }); });
      cells.forEach(function (c, i) {
        c.classList.toggle("on", d[i]); c.classList.toggle("win", !!inLine[i]); c.setAttribute("aria-pressed", d[i] ? "true" : "false");
      });
      var n = d.filter(Boolean).length;
      $("#bg-n").textContent = n === N ? "Grille complète : bravo !" : n ? plural(n, "case", "cases") + " sur " + N + (w.length ? " · " + plural(w.length, "ligne complète", "lignes complètes") : "") : "Aucune case pour l’instant. Ouvre l’œil !";
      hub("bingo", n ? (w.length ? "Bingo ! " : "") + n + " case" + (n > 1 ? "s" : "") + " sur " + N : "");
      return { n: n, lines: w.length };
    }
    grid.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest(".bg-c") : null; if (!b) return;
      var m = mine(), k = b.getAttribute("data-k"), before = wins(done()).length, on = toggleIn(m, k);
      jset(KEY, marks);
      var r = paint();
      if (!on) return;
      buzz(15);
      if (r.n === N) { toast("Grille complète !"); Confetti.burst(null, null, 120); Stamps.bonus("bingo", true); }
      else if (r.lines > before) { toast("BINGO ! Une ligne complète"); Confetti.burst(null, null, 80); Stamps.bonus("bingo", true); }
    });
    twoTap($("#bg-reset"), "Sûr ? Touche encore pour effacer ta grille", function () { marks[me()] = []; jset(KEY, marks); paint(); toast("Grille effacée"); });
    function enter() { paintWhoPick(v); build(); paint(); }
    return { enter: enter };
  })();

  /* ───────────── carnet gourmand (Moomoo) : une note de 1 à 5 cœurs par plat ───────────── */
  var Gourmand = (function () {
    var v = $("#v-gourmand"), KEY = "carnet.food", OWN = "carnet.food.own", notes = jobj(KEY), rows = $$(".fd", v), own = jget(OWN, []);
    if (!(own instanceof Array)) own = [];
    own = own.filter(function (o) { return o && typeof o.k === "string" && typeof o.n === "string" && o.n; }).slice(0, 40);
    var ownBox = $("#fd-own"), tpl = $(".fd-r", v), delT = 0, delK = "";
    function ownRow(o) {   /* un plat ajouté à la main : même cœurs, sans le thaï */
      var li = document.createElement("li"); li.className = "fd fd-u"; li.setAttribute("data-k", o.k);
      var h = document.createElement("div"); h.className = "fd-h";
      var nm = document.createElement("span"); nm.className = "fd-name"; var b = document.createElement("b"); b.textContent = o.n; nm.appendChild(b);
      var x = document.createElement("button"); x.type = "button"; x.className = "fd-del"; x.setAttribute("data-del", o.k); x.setAttribute("aria-label", "Retirer « " + o.n + " » de la liste"); x.textContent = "×";
      h.appendChild(nm); h.appendChild(x); li.appendChild(h);
      var r = tpl.cloneNode(true); r.setAttribute("aria-label", "Ma note pour " + o.n);
      $$("button", r).forEach(function (bt) { bt.classList.remove("on"); bt.setAttribute("aria-checked", "false"); });
      li.appendChild(r); return li;
    }
    function drawOwn() {
      ownBox.textContent = ""; own.forEach(function (o) { ownBox.appendChild(ownRow(o)); });
      ownBox.hidden = !own.length; rows = $$(".fd", v);
    }
    function rated() { return rows.filter(function (li) { return notes[li.getAttribute("data-k")] > 0; }); }
    function paint() {
      rows.forEach(function (li) {
        var r = notes[li.getAttribute("data-k")] || 0;
        li.classList.toggle("tasted", r > 0);
        $$(".fd-r button", li).forEach(function (b) {
          var k = parseInt(b.getAttribute("data-r"), 10);
          b.classList.toggle("on", k <= r); b.setAttribute("aria-checked", k === r ? "true" : "false");
        });
      });
      var n = rated().length;
      $("#fd-n").textContent = n ? plural(n, "plat goûté", "plats goûtés") + " sur " + rows.length : "Rien de goûté pour l’instant. À table !";
      $$("#fd-dots i").forEach(function (d, k) { d.classList.toggle("on", k < n); });
      var top = rated().sort(function (a, b) { return notes[b.getAttribute("data-k")] - notes[a.getAttribute("data-k")]; }).slice(0, 3);
      $("#fd-top").hidden = n < 3;
      var ol = $("#fd-top-l"); ol.innerHTML = "";
      if (n >= 3) top.forEach(function (li) {
        var o = document.createElement("li"), r = notes[li.getAttribute("data-k")];
        o.textContent = $(".fd-name b", li).textContent + " · " + r + " sur 5"; ol.appendChild(o);
      });
      hub("gourmand", n ? plural(n, "plat goûté", "plats goûtés") + " sur " + rows.length : "");
    }
    var form = $("#fd-form"), inp = $("#fd-in");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var n = inp.value.replace(/\s+/g, " ").trim();
      if (!n) { toast("Écris le nom du plat ou de la boisson"); inp.focus(); return; }
      var low = n.toLowerCase(), same = own.some(function (o) { return o.n.toLowerCase() === low; }) || rows.some(function (li) { var nb = $(".fd-name b", li); return nb && nb.textContent.trim().toLowerCase() === low; });
      if (same) { toast("Il est déjà dans la liste"); return; }
      if (own.length >= 40) { toast("Ça fait beaucoup de plats : retires-en un d’abord"); return; }
      var o = { k: "u" + Date.now().toString(36) + Math.floor(Math.random() * 1296).toString(36), n: n };
      own.push(o); jset(OWN, own); inp.value = ""; drawOwn(); paint(); toast("Ajouté : " + n); buzz(15);
    });
    v.addEventListener("click", function (e) {
      var d = e.target.closest ? e.target.closest(".fd-del") : null;
      if (d) {   /* deux touches pour retirer un plat ajouté (une seule risquerait de l'effacer par erreur) */
        var k = d.getAttribute("data-del");
        if (delK !== k) {
          clearTimeout(delT); $$(".fd-del.ask", v).forEach(function (z) { z.classList.remove("ask"); z.textContent = "×"; });
          delK = k; d.classList.add("ask"); d.textContent = "Retirer ?";
          delT = setTimeout(function () { delK = ""; d.classList.remove("ask"); d.textContent = "×"; }, 3000);
          return;
        }
        clearTimeout(delT); delK = "";
        own = own.filter(function (o) { return o.k !== k; }); delete notes[k]; jset(OWN, own); jset(KEY, notes); drawOwn(); paint(); return;
      }
      var b = e.target.closest ? e.target.closest(".fd-r button") : null; if (!b) return;
      var li = b.closest(".fd"), k = li.getAttribute("data-k"), r = parseInt(b.getAttribute("data-r"), 10);
      if (notes[k] === r) delete notes[k]; else notes[k] = r;
      jset(KEY, notes); paint();
      if (notes[k]) { buzz(15); if (rated().length >= 10) Stamps.bonus("gourmand"); }
    });
    drawOwn(); paint();
    return { enter: function () { paint(); } };
  })();

  /* ───────────── prix du voyage (3 janvier) : huit prix, un prénom chacun ───────────── */
  var Prix = (function () {
    var v = $("#v-prix"), KEY = "carnet.prix", votes = jobj(KEY), rows = $$(".aw", v), url = "";
    function titleOf(li) { return $(".aw-h b", li).textContent; }
    function tally() {
      var c = {}; PEOPLE.forEach(function (n) { c[n] = 0; });
      rows.forEach(function (li) { var w = votes[li.getAttribute("data-k")]; if (c[w] !== undefined) c[w]++; });
      return c;
    }
    function lines() {
      var c = tally();
      return PEOPLE.slice().sort(function (a, b) { return c[b] - c[a] || PEOPLE.indexOf(a) - PEOPLE.indexOf(b); }).map(function (n) { return [n, c[n]]; });
    }
    function paint() {
      var n = 0;
      rows.forEach(function (li) {
        var w = votes[li.getAttribute("data-k")] || "";
        if (w) n++;
        li.classList.toggle("set", !!w);
        $$(".aw-c button", li).forEach(function (b) { var on = b.getAttribute("data-n") === w; b.classList.toggle("on", on); b.setAttribute("aria-checked", on ? "true" : "false"); });
      });
      $("#aw-n").textContent = n ? plural(n, "prix décerné", "prix décernés") + " sur " + rows.length : "Aucun prix décerné pour l’instant.";
      var end = $("#aw-end"); end.hidden = n < rows.length;
      if (n === rows.length) {
        var ls = lines(), best = ls[0][1], champs = ls.filter(function (x) { return x[1] === best; }).map(function (x) { return x[0]; });
        $("#aw-tally").textContent = (champs.length === 1 ? "Le grand gagnant : " + champs[0] + " (" + plural(best, "prix", "prix") + "). " : "Égalité en tête : " + champs.join(", ") + " (" + plural(best, "prix", "prix") + " chacun). ")
          + ls.map(function (x) { return x[0] + " " + x[1]; }).join(" · ") + ".";
      }
      hub("prix", n ? plural(n, "prix décerné", "prix décernés") + " sur " + rows.length : "");
      return n;
    }
    v.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest(".aw-c button") : null; if (!b) return;
      var li = b.closest(".aw"), k = li.getAttribute("data-k"), who = b.getAttribute("data-n");
      if (votes[k] === who) delete votes[k]; else votes[k] = who;
      jset(KEY, votes); var before = $("#aw-end").hidden, n = paint();
      if (votes[k]) buzz(15);
      if (n === rows.length && before) { Confetti.burst(null, null, 120); Stamps.bonus("prix"); try { $("#aw-end").scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" }); } catch (x) {} }
    });
    /* l'image du palmarès (1080 × 1350), à garder dans les Photos ou à envoyer */
    function fit(g, text, maxW, px, weight, fam) {
      for (; px > 18; px -= 2) { g.font = weight + " " + px + "px " + fam; if (g.measureText(text).width <= maxW) break; }
      return px;
    }
    function draw() {
      var W = 1080, H = 1350, c = document.createElement("canvas"); c.width = W; c.height = H;
      var g = c.getContext("2d"), B = "'Barlow',system-ui,sans-serif", C = "'Barlow Condensed','Barlow',sans-serif";
      g.fillStyle = "#FFFCF6"; g.fillRect(0, 0, W, H);
      g.fillStyle = "#A51C36"; g.fillRect(0, 0, W, 250);
      g.textAlign = "center"; g.textBaseline = "alphabetic";
      g.fillStyle = "#F7D294"; g.font = "800 128px " + C; g.fillText("PRIX DU VOYAGE", W / 2, 148);
      g.fillStyle = "#FFFFFF"; g.font = "600 44px " + B; g.fillText("Thaïlande 2026 · 18.12 → 03.01", W / 2, 214);
      var y0 = 284, h = 112, gap = 8;
      rows.forEach(function (li, i) {
        var y = y0 + i * (h + gap), w = votes[li.getAttribute("data-k")] || "", col = PCOL[w] || ["#CCD9F4", "#1B2557"];
        g.fillStyle = i % 2 ? "#CCD9F4" : "#F7D294"; g.beginPath();
        if (g.roundRect) g.roundRect(48, y, W - 96, h, 28); else g.rect(48, y, W - 96, h);
        g.fill();
        g.textAlign = "left"; g.fillStyle = "#1B2557";
        var t = titleOf(li); fit(g, t, W - 96 - 64, 36, "600", B); g.fillText(t, 80, y + 44);
        g.fillStyle = col[0]; g.beginPath(); g.arc(104, y + 80, 22, 0, Math.PI * 2); g.fill();
        g.fillStyle = col[1]; g.textAlign = "center"; g.font = "800 30px " + C; g.fillText(w ? w.charAt(0) : "?", 104, y + 91);
        g.textAlign = "left"; g.fillStyle = "#A51C36"; g.font = "800 46px " + C; g.fillText(w || "…", 140, y + 95);
      });
      var ls = lines();
      g.textAlign = "center"; g.fillStyle = "#5B1025"; g.font = "600 34px " + B;
      var s = ls.map(function (x) { return x[0] + " : " + x[1]; }).join("   ·   "); fit(g, s, W - 120, 34, "600", B); g.fillText(s, W / 2, H - 50);
      return c;
    }
    function saveImg(blob) {
      var file = new File([blob], "palmares-thailande-2026.png", { type: "image/png" }), st = $("#aw-st"), can = false;
      try { can = !!(navigator.share && navigator.canShare && navigator.canShare({ files: [file] })); } catch (e) {}
      if (can) {
        navigator.share({ files: [file], title: "Prix du voyage" }).then(function () {
          setStatus(st, "ok", "Choisis « Enregistrer l’image » pour la mettre dans tes Photos.");
        }, function (e) { if (e && e.name === "AbortError") { setStatus(st, "", "Annulé."); return; } download(file, st); setStatus(st, "ok", "Téléchargement lancé : l’image est dans l’appli Fichiers."); });
      } else { download(file, st); setStatus(st, "ok", "Téléchargement lancé : l’image est dans l’appli Fichiers."); }
    }
    $("#aw-img").addEventListener("click", function () {
      var st = $("#aw-st"); setStatus(st, "", "Création de l’image…");
      var f = document.fonts && document.fonts.load ? Promise.all([document.fonts.load("800 40px 'Barlow Condensed'"), document.fonts.load("600 40px 'Barlow'")]) : Promise.resolve();
      f.catch(function () {}).then(function () {
        var c = draw();
        c.toBlob(function (b) {
          if (!b) { setStatus(st, "bad", "L’image n’a pas pu être créée."); return; }
          if (url) { try { URL.revokeObjectURL(url); } catch (e) {} }
          url = URL.createObjectURL(b);
          var pv = $("#aw-prev"); pv.hidden = false; pv.innerHTML = ""; var im = new Image(); im.src = url; im.alt = "Le palmarès du voyage"; pv.appendChild(im);
          saveImg(b);
        }, "image/png");
      });
    });
    return { enter: function () { paint(); } };
  })();
