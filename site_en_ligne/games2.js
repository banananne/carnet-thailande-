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

  /* ───────────── les secrets cachés du site (mascottes, décors du jour, mot caché) et le tampon « Curieux·se » ───────────── */
  /* seuls les quatre voyageurs comptent ici (un autre fichier collé dans le même bloc redéfinit me() : il renvoie aussi « Invité ») */
  function trav() { var w = LS.get("carnet.who", ""); return PEOPLE.indexOf(w) >= 0 ? w : ""; }
  var Secrets = (function () {
    var KEY = "carnet.secrets", found = jlist(KEY), NEED = 3, TOTAL = 7; /*@NEW3@*/ TOTAL = 10; /*@/NEW3@*/
    function save() { jset(KEY, found); }
    function paint() {
      var p = $("#pp-sec"); if (!p) return;
      p.hidden = !found.length;
      p.textContent = found.length ? "Secrets trouvés : " + found.length + " sur " + TOTAL + (found.length >= NEED ? "" : ". Il y en a d’autres, cachés un peu partout.") : "";
    }
    function find(id) {
      if (!trav() || found.indexOf(id) >= 0) return false;      /* les secrets sont réservés aux voyageurs */
      found.push(id); save(); paint();
      if (found.length >= NEED) Stamps.bonus("curieux", true);
      return true;
    }
    function reset() { found = []; save(); paint(); }
    paint();
    return { find: find, paint: paint, reset: reset, count: function () { return found.length; } };
  })();

  /* touche 5 fois de suite une mascotte : confettis et petit mot (images qui ne sont pas des liens) */
  (function () {
    var SAY = {
      aftonsparv: "Aftonsparv : « Sur ma planète aussi, on adore qu’on nous tapote cinq fois. »",
      boop: "Boop : « Psst. Le mot caché du voyage veut dire « s’amuser » en thaï et commence par S. Tape-le tout en bas de Jeux. »",
      minou: "Minou : « Je ne dis rien, mais je note ta curiosité. »",
      moomoo: "Moomoo : « Encore ! Encore ! Encore ! »"
    };
    var cnt = {}, last = {};
    document.addEventListener("click", function (e) {
      var im = e.target.closest ? e.target.closest("img[data-dd]") : null;
      if (!im || !trav() || (im.closest && im.closest("a[href]"))) return;
      var k = im.getAttribute("data-dd"), now = Date.now();
      cnt[k] = now - (last[k] || 0) < 1300 ? (cnt[k] || 0) + 1 : 1; last[k] = now;
      if (!reduce) { im.classList.remove("boing"); void im.offsetWidth; im.classList.add("boing"); }
      buzz(8);
      if (cnt[k] >= 5) {
        cnt[k] = 0;
        var c = centerOf(im); Confetti.burst(c.x, c.y, 80); buzz(30);
        Secrets.find("m-" + k);
        toast(nb(SAY[k] || "Bravo !"), k === "boop" ? 7000 : 4200);
      }
    });
  })();

  /* décors du jour : neige les 24 et 25 décembre, feux d'artifice le soir du 31 et le 1er janvier */
  var Decor = (function () {
    var cv = null, ctx = null, raf = 0, stop = 0;
    function clear() { if (raf) cancelAnimationFrame(raf); raf = 0; if (cv && cv.parentNode) cv.parentNode.removeChild(cv); cv = null; ctx = null; }
    function mk() {
      clear();
      cv = document.createElement("canvas"); cv.setAttribute("aria-hidden", "true");
      cv.style.cssText = "position:fixed;left:0;top:0;width:100%;height:100%;z-index:40;pointer-events:none";
      document.body.appendChild(cv); ctx = cv.getContext("2d");
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      cv.width = Math.round(innerWidth * dpr); cv.height = Math.round(innerHeight * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function snow() {
      mk(); var fl = [], t0 = Date.now(), DUR = 13000, i;
      for (i = 0; i < 110; i++) fl.push({ x: Math.random() * innerWidth, y: -Math.random() * innerHeight, r: 1.6 + Math.random() * 3.2, v: 0.7 + Math.random() * 1.4, p: Math.random() * 6, a: 0.5 + Math.random() * 0.5 });
      (function step() {
        var t = Date.now() - t0; if (!cv || t > DUR) { clear(); return; }
        var fade = t < 1500 ? t / 1500 : t > DUR - 2500 ? (DUR - t) / 2500 : 1;
        ctx.clearRect(0, 0, innerWidth, innerHeight);
        ctx.globalAlpha = 0.16 * fade; ctx.fillStyle = "#1B2557"; ctx.fillRect(0, 0, innerWidth, innerHeight);
        fl.forEach(function (f) {
          f.y += f.v; f.p += 0.02; f.x += Math.sin(f.p) * 0.6;
          if (f.y > innerHeight + 6) { f.y = -6; f.x = Math.random() * innerWidth; }
          ctx.globalAlpha = f.a * fade; ctx.beginPath(); ctx.arc(f.x, f.y, f.r, 0, 6.3);
          ctx.fillStyle = "#FFFFFF"; ctx.shadowColor = "rgba(27,37,87,.8)"; ctx.shadowBlur = 5; ctx.fill(); ctx.shadowBlur = 0; ctx.lineWidth = 1; ctx.strokeStyle = "rgba(143,176,238,.9)"; ctx.stroke();
        });
        raf = requestAnimationFrame(step);
      })();
    }
    function fireworks() {
      mk(); var ps = [], t0 = Date.now(), DUR = 9500, next = 0, COL = ["#F2A71B", "#A51C36", "#8FB0EE", "#E9A9B8", "#FFFFFF", "#F7D294"];
      function burst() {
        var x = innerWidth * (0.15 + Math.random() * 0.7), y = innerHeight * (0.15 + Math.random() * 0.35), c = COL[Math.floor(Math.random() * COL.length)], n = 46, i;
        for (i = 0; i < n; i++) { var a = i / n * 6.283, sp = 2.2 + Math.random() * 2.6; ps.push({ x: x, y: y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, c: c, life: 60 + Math.random() * 25 }); }
      }
      (function step() {
        var t = Date.now() - t0; if (!cv || (t > DUR && !ps.length)) { clear(); return; }
        if (t < DUR - 1500 && t >= next) { burst(); next = t + 500 + Math.random() * 450; }
        ctx.clearRect(0, 0, innerWidth, innerHeight);
        ctx.globalAlpha = 0.6 * (t < 1200 ? t / 1200 : t > DUR - 1500 ? Math.max(0, (DUR - t) / 1500) : 1); ctx.shadowBlur = 0; ctx.fillStyle = "#141B45"; ctx.fillRect(0, 0, innerWidth, innerHeight);
        ps = ps.filter(function (p) {
          p.vy += 0.045; p.vx *= 0.985; p.vy *= 0.985; p.x += p.vx; p.y += p.vy; p.life--;
          if (p.life <= 0) return false;
          ctx.globalAlpha = Math.min(1, p.life / 30); ctx.fillStyle = p.c; ctx.shadowColor = p.c; ctx.shadowBlur = 8;
          ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, 6.3); ctx.fill(); return true;
        });
        raf = requestAnimationFrame(step);
      })();
    }
/*@NEW3@*/
    /* remerciements des quatre mascottes, le 3 janvier */
    var merci = $("#merci");
    function showMerci(test) {
      if (!merci) return;
      merci.hidden = false; merci.scrollTop = 0;
      var b = $('[data-merci="close"]', merci); if (b) { try { b.focus({ preventScroll: true }); } catch (e) {} }
      Confetti.burst(null, null, 100); buzz(30);
      if (!test) Secrets.find("merci");
    }
    document.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest('[data-merci="close"]') : null;
      if (b && merci) merci.hidden = true;
    });
/*@/NEW3@*/
    function show(kind, test) {
/*@NEW3@*/      if (kind === "merci") { showMerci(test); return; }
/*@/NEW3@*/      if (reduce) { toast(kind === "neige" ? "Il neige (sur ton téléphone, en mode calme)." : "Feux d’artifice (en mode calme)."); }
      else if (kind === "neige") snow(); else fireworks();
      toast(kind === "neige" ? "Joyeux Noël, de la part des mascottes !" : "Bonne année, de la part des mascottes !");
      if (!test) Secrets.find(kind === "neige" ? "d-neige" : "d-feux");
    }
    function kindOf() {
      var t = Cal.today(), h = new Date().getHours();
      if (t === "2026-12-24" || t === "2026-12-25") return "neige";
      if ((t === "2026-12-31" && h >= 17) || t === "2027-01-01") return "feux";
      return "";
    }
    /* une seule fois par jour de décor et par téléphone, à l'ouverture de l'accueil (neige et feux : tout le monde ; remerciements : voyageurs) */
    function auto() {
      var k = kindOf(), seen = jlist("carnet.decor"), id;
      if (k) {
        id = k + Cal.today();
        if (seen.indexOf(id) < 0) { seen.push(id); jset("carnet.decor", seen); setTimeout(function () { show(k, false); }, 700); return; }
      }
/*@NEW3@*/
      if (trav() && Cal.today() >= "2027-01-03" && seen.indexOf("merci") < 0) {
        seen.push("merci"); jset("carnet.decor", seen); setTimeout(function () { show("merci", false); }, 700);
      }
/*@/NEW3@*/
    }
    document.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("[data-decor],[data-secrets-reset]") : null; if (!b) return;
      if (b.hasAttribute("data-decor")) show(b.getAttribute("data-decor"), true);
      else { Secrets.reset(); jset("carnet.decor", []); toast("Secrets remis à zéro"); }
    });
    return { auto: auto, show: show };
  })();


/*@NEW3@*/
  /* toucher 3 fois « Thaïlande » sur l'accueil : un éléphant traverse l'écran */
  (function () {
    var w = $("#tl-word"), tpl = $("#tpl-eleph"); if (!w || !tpl) return;
    var n = 0, t0 = 0, last = null;
    function run() {
      if (reduce) { toast("Prrrrout ! (un éléphant est passé, en mode calme)"); return; }
      if (last && last.parentNode) last.parentNode.removeChild(last);
      var d = document.createElement("div"); d.className = "eleph"; d.setAttribute("aria-hidden", "true");
      d.appendChild(tpl.content.cloneNode(true)); document.body.appendChild(d); last = d;
      setTimeout(function () { if (d.parentNode) d.parentNode.removeChild(d); }, 5600);
      toast("Prrrrout !");
    }
    w.addEventListener("click", function () {
      if (!trav()) return;
      var now = Date.now(); n = now - t0 < 800 ? n + 1 : 1; t0 = now;
      if (n >= 3) { n = 0; run(); buzz(25); Secrets.find("eleph"); }
    });
  })();

  /* appui long sur un tampon du passeport : un petit mot de la mascotte du jour */
  (function () {
    var pp = $("#v-pass"); if (!pp) return;
    var SAY = {
      "2026-12-18": ["aftonsparv", "Décollage confirmé. Je n’ai pas peur de l’avion : je viens déjà de beaucoup plus loin."],
      "2026-12-19": ["boop", "Vous êtes arrivés ? Je sens déjà le piment d’ici."],
      "2026-12-20": ["minou", "Un bateau avec un moteur de camion. Je n’y monte pas. Je regarde. Je juge."],
      "2026-12-21": ["moomoo", "Meuh. (De vieilles pierres, c’est très beau. Mais est-ce qu’on peut les brouter ?)"],
      "2026-12-22": ["aftonsparv", "Sur ma planète, il n’y a pas de marché. Ici, il y en a partout. Je prends tout."],
      "2026-12-23": ["boop", "Un palais tout doré, c’est exactement ma taille de pince."],
      "2026-12-24": ["minou", "Des milliers de stands. Je n’achète rien. Je note tout."],
      "2026-12-25": ["moomoo", "Joyeux Noël ! J’ai demandé au Père Noël une botte de foin. Il a ri."],
      "2026-12-26": ["aftonsparv", "Re-décollage. J’ai l’habitude : je suis un extraterrestre expert en aéroports."],
      "2026-12-27": ["boop", "À vélo ? Moi, je me déplace en marchant de travers."],
      "2026-12-28": ["minou", "Un temple tout en haut d’une colline. J’approuve. En silence."],
      "2026-12-29": ["moomoo", "La mer ! Meuh… c’est de l’eau salée ? Je reste sur la serviette."],
      "2026-12-30": ["aftonsparv", "J’ai compris le principe de la plage : on s’allonge et on ne fait rien. Excellent système."],
      "2026-12-31": ["boop", "Je trinque à distance, avec ma pince. Santé !"],
      "2027-01-01": ["minou", "Bonne année. Voilà. Je l’ai dit. Ne me le redemande pas."],
      "2027-01-02": ["moomoo", "On rentre ? Déjà ? Encore cinq minutes !"],
      "2027-01-03": ["aftonsparv", "À bientôt, la Thaïlande. Je reviendrai, si on me laisse la place côté hublot."]
    };
    var NAME = { aftonsparv: "Aftonsparv", boop: "Boop", minou: "Minou", moomoo: "Moomoo" };
    var T = 0, fired = false;
    function stop() { clearTimeout(T); T = 0; }
    pp.addEventListener("pointerdown", function (e) {
      fired = false; stop();
      var s = e.target.closest ? e.target.closest('.slot[data-stamp="d"]') : null;
      if (!s || !trav() || !s.classList.contains("on")) return;
      var say = SAY[s.getAttribute("data-id")]; if (!say) return;
      T = setTimeout(function () {
        fired = true; buzz(20);
        var c = centerOf(s); Confetti.burst(c.x, c.y, 30);
        toast(nb(NAME[say[0]] + " : « " + say[1] + " »"), 5200);
        Secrets.find("press");
      }, 650);
    });
    ["pointerup", "pointercancel", "pointerleave"].forEach(function (t) { pp.addEventListener(t, stop); });
    pp.addEventListener("contextmenu", function (e) { if (e.target.closest && e.target.closest(".slot")) e.preventDefault(); });
    /* le toucher qui suit un appui long ne doit pas retamponner ni afficher « Déjà tamponné » */
    pp.addEventListener("click", function (e) {
      if (fired) { fired = false; e.stopImmediatePropagation(); e.preventDefault(); }
    }, true);
  })();

/*@/NEW3@*/
  /* mot caché, tout en bas des Jeux */
  (function () {
    var box = $(".hub-word"); if (!box) return;
    var f = $("#hw-form"), inp = $("#hw-in"), msg = $("#hw-msg"), ask = $('[data-word="ask"]', box);
    function norm(w) { var t = String(w); try { t = t.normalize("NFD"); } catch (e) {} return t.replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, ""); }
    ask.addEventListener("click", function () { f.hidden = false; ask.hidden = true; inp.focus(); });
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var w = norm(inp.value); if (!w || !trav()) return;
      if (w === "sanuk" || w === "sanook") {
        var c = centerOf(f); Confetti.burst(c.x, c.y, 120); buzz(40);
        msg.textContent = nb("Sanuk ! C’est le mot de tout ce voyage : s’amuser, sans se prendre au sérieux. Moomoo te félicite.");
        Secrets.find("mot"); inp.value = ""; f.hidden = true;
      } else {
        msg.textContent = "Ce n’est pas ça. Cherche encore : quelqu’un connaît un indice.";
        buzz(12);
      }
    });
  })();

  /* ───────────── carte à gratter du jour ───────────── */
  var Gratter = (function () {
    var v = $("#v-gratter"), KEY = "carnet.gratter", CFG = {};
    try { CFG = JSON.parse(v.getAttribute("data-cfg") || "{}"); } catch (e) {}
    var done = jobj(KEY), card = $("#grc"), ticket = $("#grc-ticket"), res = $("#grc-res"), foil = $("#grc-foil"), hint = $("#grc-hint"), allBtn = $("#grc-all");
    var nav = DayNav(v, "gratter", ".grd", function (i, blk) { paint(blk); });
    var cur = null, drawing = false, moves = 0, lastCheck = 0, revealed = false;
    function hash(s) { var h = 0x811c9dc5; for (var i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619) >>> 0; return h; }
    function key() { return trav() + "|" + (cur ? cur.getAttribute("data-id") : ""); }
    function weekday(id) { var p = id.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]).getDay(); }
    function html(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;"); }
    /* le contenu du jour : même carte chaque fois qu'on revient, différente selon la personne */
    function content(blk) {
      var who = trav(), id = blk.getAttribute("data-id"), i = parseInt(blk.getAttribute("data-i"), 10), rank = Math.max(0, PEOPLE.indexOf(who));
      var kind = (hash(who + "|" + id) >> 5) & 1 ? "loto" : "fort";
      var list = kind === "loto" ? CFG.loto : CFG.fort, n = list.length, text = list[(i + rank * 5) % n];
      var num = 1 + hash("n" + who + id) % 28, ticketNo = String(10000 + hash("t" + who + id) % 89999);
      return { kind: kind, text: text, num: num, no: ticketNo, col: (CFG.col || [])[weekday(id)] || "" };
    }
    function fill(c) {
      ticket.className = "grc-ticket " + c.kind;
      if (c.kind === "loto") {
        res.innerHTML = '<p class="grc-k">Loto thaï de Moomoo</p><p class="grc-big">Félicitations !</p><p class="grc-t">' + html(c.text) + '</p>'
          + '<p class="grc-s">Ticket n° ' + c.no + ' · aucun lot ne sera remis, Moomoo n’a même pas de poches</p>';
        $("#grc-kick").textContent = "Moomoo a un ticket pour toi"; $("#grc-h").textContent = "Le loto du jour";
      } else {
        res.innerHTML = '<p class="grc-k">Bâtonnet n° ' + c.num + '</p><p class="grc-t grc-fort">' + html(c.text) + '</p>'
          + '<p class="grc-s">Couleur du jour en Thaïlande : <b>' + html(c.col) + '</b></p>';
        $("#grc-kick").textContent = "Aftonsparv a secoué le pot"; $("#grc-h").textContent = "La fortune du jour";
      }
      $$(".grc-mas .df-img", card).forEach(function (im, k) { im.hidden = (k === 0) !== (c.kind === "loto"); });
    }
    /* la peau argentée */
    function drawFoil() {
      var w = ticket.clientWidth, h = ticket.clientHeight; if (!w || !h) return;
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      foil.width = Math.round(w * dpr); foil.height = Math.round(h * dpr);
      var g = foil.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.globalCompositeOperation = "source-over";
      var gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, "#B8BECE"); gr.addColorStop(0.35, "#E7EAF1"); gr.addColorStop(0.65, "#BFC5D4"); gr.addColorStop(1, "#DDE1EA");
      g.fillStyle = gr; g.fillRect(0, 0, w, h);
      g.strokeStyle = "rgba(255,255,255,.55)"; g.lineWidth = 2;
      for (var x = -h; x < w; x += 16) { g.beginPath(); g.moveTo(x, h); g.lineTo(x + h, 0); g.stroke(); }
      for (var k = 0; k < 140; k++) { g.fillStyle = "rgba(" + (k % 2 ? "255,255,255" : "90,100,130") + ",.28)"; g.fillRect(Math.random() * w, Math.random() * h, 1.6, 1.6); }
      g.fillStyle = "rgba(40,56,129,.78)"; g.textAlign = "center"; g.textBaseline = "middle";
      g.font = "800 " + Math.min(34, w / 9) + "px 'Barlow Condensed','Barlow',sans-serif"; g.fillText("GRATTE ICI", w / 2, h / 2 - 8);
      g.font = "600 " + Math.min(15, w / 24) + "px 'Barlow',sans-serif"; g.fillText("avec ton doigt", w / 2, h / 2 + 20);
      g.globalCompositeOperation = "destination-out";
    }
    function setRevealed(on) { foil.classList.toggle("gone", on); hint.hidden = on; allBtn.parentNode.hidden = on; revealed = on; }
    function paint(blk) {
      if (blk) cur = blk;
      paintWhoPick(v);
      var ok = !!trav() && !!cur; card.hidden = !ok;
      if (ok) {
        var c = content(cur); fill(c);
        var d = !!done[key()]; setRevealed(d);
        if (!d) { foil.hidden = false; setTimeout(drawFoil, 30); }
      }
      summary();
    }
    function summary() {
      var w = trav(), n = days.filter(function (id) { return done[w + "|" + id]; }).length;
      var t = n ? plural(n, "carte grattée", "cartes grattées") + " sur " + days.length : "";
      $("#gr-n").textContent = w ? (t || "Aucune carte grattée pour l’instant.") : "";
      $$("#gr-dots i").forEach(function (d, k) { d.classList.toggle("on", !!done[w + "|" + days[k]]); });
      $("#gr-reset-box").hidden = !Cal.trying();
      hub("gratter", t);
    }
    function reveal(auto) {
      if (revealed) return; setRevealed(true);
      done[key()] = 1; jset(KEY, done); summary(); buzz(25);
      var c = centerOf(ticket); Confetti.burst(c.x, c.y, content(cur).kind === "loto" ? 70 : 30);
    }
    /* quelle part de la peau est partie ? (on regarde un pixel sur dix) */
    function cleared() {
      try {
        var g = foil.getContext("2d"), d = g.getImageData(0, 0, foil.width, foil.height).data, n = 0, tot = 0;
        for (var y = 0; y < foil.height; y += 10) for (var x = 0; x < foil.width; x += 10) { tot++; if (d[(y * foil.width + x) * 4 + 3] < 40) n++; }
        return n / tot;
      } catch (e) { return 1; }
    }
    function pos(e) { var r = foil.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }
    var lp = null;
    foil.addEventListener("pointerdown", function (e) {
      if (revealed) return; drawing = true; lp = pos(e);
      try { foil.setPointerCapture(e.pointerId); } catch (x) {}
      scratch(lp, lp); e.preventDefault();
    });
    foil.addEventListener("pointermove", function (e) {
      if (!drawing || revealed) return; var p = pos(e); scratch(lp, p); lp = p; e.preventDefault();
      var t = Date.now(); if (t - lastCheck > 250) { lastCheck = t; if (cleared() > 0.5) reveal(true); }
    });
    function end() { if (!drawing) return; drawing = false; if (!revealed && cleared() > 0.5) reveal(true); }
    foil.addEventListener("pointerup", end); foil.addEventListener("pointercancel", end);
    function scratch(a, b) {
      var g = foil.getContext("2d"); g.lineCap = "round"; g.lineJoin = "round"; g.lineWidth = 34;
      g.beginPath(); g.moveTo(a.x, a.y); g.lineTo(b.x + 0.01, b.y + 0.01); g.stroke();
    }
    allBtn.addEventListener("click", function () { reveal(false); });
    twoTap($("#gr-reset"), "Sûr ? Touche encore pour tout remettre à zéro", function () {
      done = {}; jset(KEY, done); paint(); toast("Cartes remises à zéro");
    });
    window.addEventListener("resize", function () { if (!revealed && !card.hidden && !v.hidden) drawFoil(); });
    function enter() { var k = dayFromHash(); nav.set(k >= 0 ? k : Cal.idxToday()); }
    summary();
    return { enter: enter };
  })();
