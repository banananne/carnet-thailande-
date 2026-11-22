/* ───────────── étape 3 : les jeux (quiz, test du doudou, blind test, mots mêlés, horoscope, passeport) ─────────────
   Ce fichier est collé dans app.js au moment du build (il partage ses outils : $, $$, LS, toast, say, hasPhoto…).
   Tout reste sur le téléphone : scores, mots trouvés, tampons et résultat du test sont gardés dans le navigateur. */
window.CarnetGames = (function () {
  var reduce = false;
  try { reduce = !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches); } catch (e) {}
  function jget(k, d) { try { var v = LS.get(k, null); return v === null ? d : JSON.parse(v); } catch (e) { return d; } }
  function jset(k, v) { LS.set(k, JSON.stringify(v)); }
  function buzz(ms) { try { if (navigator.vibrate) navigator.vibrate(ms); } catch (e) {} }
  /* sous-titre d'une tuile des Jeux : le texte du jeu, ou « À partir du … » tant que la tuile est fermée */
  var hubTxt = {};
  function hub(id, text) { hubTxt[id] = text || ""; hubPaint(id); }
  function hubPaint(id) {
    var e = $('[data-hub="' + id + '"]'); if (!e) return;
    var t = e.closest ? e.closest("[data-gate]") : null;
    if (t && !Cal.isOpen(t.getAttribute("data-gate"))) { e.textContent = "À partir du " + (t.getAttribute("data-opens") || ""); return; }
    e.textContent = hubTxt[id] || e.getAttribute("data-def");
  }
  function nb(s) { return String(s).replace(/ ([:;?!»])/g, "\u00a0$1").replace(/(«) /g, "$1\u00a0"); }
  /* bouton qui demande une deuxième touche avant d'effacer (le libellé est dans un <span>) */
  function twoTap(btn, armed, fn) {
    var lab = $("span", btn), base = lab.textContent, t = 0;
    function disarm() { btn.removeAttribute("data-armed"); lab.textContent = base; }
    btn.addEventListener("click", function () {
      if (btn.getAttribute("data-armed") !== "1") {
        btn.setAttribute("data-armed", "1"); lab.textContent = armed;
        clearTimeout(t); t = setTimeout(disarm, 3500); return;
      }
      clearTimeout(t); disarm(); fn();
    });
  }
  function centerOf(el) { var r = el.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }
  function focusTitle(root) { var h = $("h2", root); if (h) { h.setAttribute("tabindex", "-1"); try { h.focus({ preventScroll: true }); } catch (e) {} } }

  /* ───────────── confettis ───────────── */
  var Confetti = (function () {
    var cv = null, ctx = null, parts = [], raf = 0;
    var COLORS = ["#A51C36", "#F2A71B", "#283881", "#E9A9B8", "#F7D294", "#8FB0EE", "#1E7B4F"];
    function ensure() {
      if (cv) return;
      cv = document.createElement("canvas"); cv.setAttribute("aria-hidden", "true");
      cv.style.cssText = "position:fixed;left:0;top:0;width:100%;height:100%;z-index:90;pointer-events:none";
      document.body.appendChild(cv); ctx = cv.getContext("2d");
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      cv.width = Math.round(innerWidth * dpr); cv.height = Math.round(innerHeight * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function step() {
      ctx.clearRect(0, 0, innerWidth, innerHeight);
      var alive = [];
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        p.vy += 0.26; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.rot += p.vr; p.life--;
        if (p.life > 0 && p.y < innerHeight + 24) {
          alive.push(p);
          ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rot); ctx.globalAlpha = Math.min(1, p.life / 25);
          ctx.fillStyle = p.c; ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); ctx.restore();
        }
      }
      parts = alive;
      if (parts.length) raf = requestAnimationFrame(step);
      else { raf = 0; if (cv && cv.parentNode) cv.parentNode.removeChild(cv); cv = null; ctx = null; }
    }
    function burst(x, y, n) {
      if (reduce) return;
      try {
        ensure();
        if (x == null) { x = innerWidth / 2; y = innerHeight * 0.38; }
        n = n || 70;
        for (var i = 0; i < n; i++) {
          var a = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI * 1.15, sp = 4 + Math.random() * 8;
          parts.push({ x: x, y: y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, w: 6 + Math.random() * 6, h: 4 + Math.random() * 5,
                       rot: Math.random() * 6, vr: (Math.random() - 0.5) * 0.4, c: COLORS[i % COLORS.length], life: 80 + Math.random() * 50 });
        }
        if (!raf) raf = requestAnimationFrame(step);
      } catch (e) {}
    }
    return { burst: burst };
  })();

  /* ───────────── calendrier : la date du téléphone décide de ce qui est ouvert ─────────────
     Le mot secret (gardé sur ce téléphone) ouvre tout d'un coup : c'est le « mode essai » pour tester avant le départ. */
  var Cal = (function () {
    var KEY = "carnet.open", box = $("#v-jeux"), OPEN = {}, HASH = [];
    try { OPEN = JSON.parse(box.getAttribute("data-gates") || "{}"); } catch (e) {}
    HASH = (box.getAttribute("data-k") || "").split(",").map(Number);
    var FIRST = box.getAttribute("data-first") || "", LAST = box.getAttribute("data-last") || "";
    function today() { var d = new Date(); return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate()); }
    function master() { return LS.get(KEY, "") === "1"; }
    function setMaster(on) { if (on) LS.set(KEY, "1"); else LS.del(KEY); }
    function isOpen(key) { var o = OPEN[key]; return !o || master() || today() >= o; }
    function norm(w) {
      var t = String(w);
      try { t = t.normalize("NFD"); } catch (e) {}
      return t.replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");
    }
    function fnv(w) { var h = 0x811c9dc5; for (var i = 0; i < w.length; i++) h = Math.imul(h ^ w.charCodeAt(i), 16777619) >>> 0; return h; }
    function good(w) { var n = norm(w); return !!n && HASH.indexOf(fnv(n)) >= 0; }
    /* les 17 jours du voyage (mêmes identifiants que les pages de jour) */
    function inTrip() { var t = today(); return t >= FIRST && t <= LAST; }
    function idxToday() {
      var t = today(); if (t <= FIRST) return 0; if (t >= LAST) return days.length - 1;
      for (var i = days.length - 1; i >= 0; i--) if (days[i] <= t) return i;
      return 0;
    }
    function maxOpen() { return master() ? days.length - 1 : (today() < FIRST ? -1 : idxToday()); }
    function trying() { return master() && today() < LAST; }
    return { today: today, master: master, setMaster: setMaster, isOpen: isOpen, good: good, inTrip: inTrip, idxToday: idxToday, maxOpen: maxOpen, trying: trying };
  })();

  /* ───────────── cadenas : un écran « Pas encore ! » par jeu fermé, et les tuiles des Jeux ───────────── */
  var Gates = (function () {
    function paintView(name) {
      var v = $("#v-" + name);
      if (!v || !v.hasAttribute("data-gate")) return true;
      var p = $(".lkv", v), b = $(".gbody", v);
      if (!p || !b) return true;
      var lk = !Cal.isOpen(v.getAttribute("data-gate"));
      if (lk && p.hidden) {     /* vient de se fermer : le formulaire repart replié */
        var f = $(".lk-form", p); f.hidden = true; $('[data-lkv="ask"]', p).hidden = false; $(".lk-err", p).textContent = "";
      }
      p.hidden = !lk; b.hidden = lk;
      return !lk;
    }
    function paintHub() {
      $$("#v-jeux a.tile[data-gate]").forEach(function (t) { t.classList.toggle("is-locked", !Cal.isOpen(t.getAttribute("data-gate"))); });
      $$("#v-jeux [data-hub]").forEach(function (e) { hubPaint(e.getAttribute("data-hub")); });
      var tr = $("#hub-try"); if (tr) tr.hidden = !Cal.trying();
    }
    document.addEventListener("click", function (e) {
      var t = e.target.closest ? e.target.closest("[data-lkv],[data-relock]") : null; if (!t) return;
      if (t.hasAttribute("data-relock")) { Lock.close(); refreshAll(); toast("Cadenas remis"); return; }
      var p = t.closest(".lkv"), f = $(".lk-form", p);
      t.hidden = true; f.hidden = false; try { $("input", f).focus(); } catch (x) {}
    });
    document.addEventListener("submit", function (e) {
      var f = e.target; if (!f || !f.classList || !f.classList.contains("lkv-form")) return;
      e.preventDefault();
      var i = $("input", f), err = $(".lk-err", f), p = f.closest(".lkv");
      if (Cal.good(i.value)) { i.value = ""; err.textContent = ""; Lock.open(); refreshAll(); toast("Tout est ouvert sur ce téléphone"); Confetti.burst(null, null, 50); return; }
      err.textContent = "Ce n’est pas le bon mot."; buzz(40);
      p.classList.remove("no"); void p.offsetWidth; p.classList.add("no"); try { i.select(); } catch (x) {}
    });
    document.addEventListener("animationend", function (e) { if (e.target.classList && e.target.classList.contains("lkv")) e.target.classList.remove("no"); });
    return { paintView: paintView, paintHub: paintHub };
  })();

  /* ───────────── passeport : les tampons ───────────── */
  var Stamps = (function () {
    var KEY = "carnet.stamps";
    var data = jget(KEY, null) || {};
    if (!(data.d instanceof Array)) data.d = [];
    if (!(data.b instanceof Array)) data.b = [];
    var slots = $$("#v-pass .slot"), total = slots.length;
    var BONUS_TITLE = {};
    slots.forEach(function (s) { if (s.getAttribute("data-stamp") === "b") BONUS_TITLE[s.getAttribute("data-id")] = s.getAttribute("data-title"); });
    function has(kind, id) { return data[kind].indexOf(id) >= 0; }
    function count() { return data.d.length + data.b.length; }
    function save() { jset(KEY, data); }
    function slotOf(kind, id) { return $('#v-pass .slot[data-stamp="' + kind + '"][data-id="' + id + '"]'); }
    function pop(el) { if (!el) return; el.classList.remove("fresh"); void el.offsetWidth; el.classList.add("fresh"); }
    function paint() {
      var n = 0;
      slots.forEach(function (s) {
        var on = has(s.getAttribute("data-stamp"), s.getAttribute("data-id"));
        s.classList.toggle("on", on); s.setAttribute("aria-pressed", on ? "true" : "false");
        if (on) n++;
      });
      var c = $("#pp-count"); if (c) c.textContent = n;
      var f = $("#pp-fill"); if (f) f.style.width = (100 * n / total) + "%";
      var txt = n ? n + " sur " + total + " tampons" : "";
      $$("[data-pass-count]").forEach(function (e) { e.textContent = txt || "Un tampon par jour"; });
      hub("pass", txt);
      $$(".dstamp").forEach(function (b) {
        var id = b.getAttribute("data-day"), on = has("d", id), box = $(".dstamp-svg", b), btn = $("button", b);
        btn.hidden = on; box.hidden = !on;
        if (!on) box.textContent = "";
        var dh = $(".dstamp-hint", b); if (dh) dh.hidden = !on;
        box.setAttribute("role", on ? "button" : "presentation"); if (on) { box.setAttribute("tabindex", "0"); box.setAttribute("aria-label", "Retirer le tampon de ce jour"); } else { box.removeAttribute("tabindex"); box.removeAttribute("aria-label"); }
        if (on && !box.firstChild) {
          var src = slotOf("d", id), svg = src && $(".stamp", src);
          if (svg) {
            /* la copie garde ses propres identifiants : le texte courbé ne dépend pas du passeport (caché sur les pages de jour) */
            var cl = svg.cloneNode(true);
            $$("[id]", cl).forEach(function (n) {
              var o = n.id, u = "d" + o;
              n.id = u;
              $$('[href="#' + o + '"]', cl).forEach(function (m) { m.setAttribute("href", "#" + u); });
            });
            box.appendChild(cl);
          }
        }
      });
    }
    function earn(kind, id) {
      if (has(kind, id)) return false;
      data[kind].push(id); save(); paint();
      return true;
    }
    function done() {
      if (count() >= total) { setTimeout(function () { toast("Passeport complet : bravo, tout le monde a tout tamponné !"); Confetti.burst(null, null, 150); }, 600); }
    }
    function day(id, o) {
      o = o || {};
      var fresh = earn("d", id);
      if (!fresh) return false;
      pop(slotOf("d", id)); pop($('.dstamp[data-day="' + id + '"] .dstamp-svg'));
      if (o.from) { var c = centerOf(o.from); Confetti.burst(c.x, c.y, 50); }
      buzz(20);
      done();
      return true;
    }
    function unday(id) {
      var i = data.d.indexOf(id); if (i < 0) return false;
      data.d.splice(i, 1); save(); paint(); return true;
    }
    function bonus(key, quiet) {
      if (!earn("b", key)) return false;
      pop(slotOf("b", key));
      setTimeout(function () { toast("Tampon spécial gagné : " + (BONUS_TITLE[key] || key)); if (!quiet) Confetti.burst(null, null, 60); done(); }, 450);
      return true;
    }
    /* touche une case du passeport */
    var pp = $("#v-pass");
    pp.addEventListener("click", function (e) {
      var s = e.target.closest ? e.target.closest(".slot") : null; if (!s) return;
      var kind = s.getAttribute("data-stamp"), id = s.getAttribute("data-id");
      if (kind === "d") {
        if (has("d", id)) { toast("Déjà tamponné : " + s.getAttribute("data-word")); return; }
        day(id, { from: s }); toast("Tamponné : " + s.getAttribute("data-word"));
      } else {
        if (has("b", id)) toast("Tampon spécial : " + s.getAttribute("data-title"));
        else toast("À gagner : " + s.getAttribute("data-how"));
      }
    });
    twoTap($("#pp-reset"), "Sûr ? Touche encore pour tout effacer", function () {
      data = { d: [], b: [] }; save();
      $$(".dstamp-svg").forEach(function (b) { b.innerHTML = ""; });
      paint(); toast("Passeport remis à zéro");
    });
    /* bouton « Tamponner ce jour » de chaque page de jour */
    document.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("[data-stamp-day]") : null; if (!b) return;
      var id = b.getAttribute("data-stamp-day");
      if (day(id, { from: b })) toast("Tampon du jour ajouté au passeport");
    });
    /* retoucher le tampon d'une page de jour l'enlève */
    function unstamp(e) {
      var b = e.target.closest ? e.target.closest(".dstamp-svg") : null; if (!b || b.hidden) return;
      if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;
      e.preventDefault();
      var id = b.parentNode.getAttribute("data-day");
      if (unday(id)) { buzz(10); toast("Tampon retiré : tu peux retamponner ce jour"); }
    }
    document.addEventListener("click", unstamp);
    document.addEventListener("keydown", unstamp);
    paint();
    return { day: day, bonus: bonus, paint: paint, count: count, total: total };
  })();

  /* ───────────── quiz du 26 décembre ───────────── */
  var Quiz = (function () {
    var root = $("#qz"), intro = $("#qz-intro"), qs = $$(".qz-q", root), end = $("#qz-end");
    var msgs = {};
    var cur = 0, score = 0, locked = false;
    var best = parseInt(LS.get("carnet.quiz", ""), 10); if (isNaN(best)) best = -1;
    try { msgs = JSON.parse(root.getAttribute("data-msgs") || "{}"); } catch (e) {}
    function show(el) { [intro, end].concat(qs).forEach(function (x) { x.hidden = x !== el; }); }
    function paintBest() {
      var b = $("#qz-best");
      if (best >= 0) { b.hidden = false; b.textContent = "Ton meilleur score : " + best + " sur " + qs.length; } else b.hidden = true;
      hub("quiz", best >= 0 ? "Meilleur score : " + best + " sur " + qs.length : "");
    }
    function reset() { cur = 0; score = 0; locked = false; show(intro); paintBest(); }
    function start() {
      score = 0; cur = 0; locked = false;
      qs.forEach(function (q) {
        $$(".qz-o", q).forEach(function (o) { o.disabled = false; o.classList.remove("good", "bad"); });
        $(".qz-fb", q).hidden = true; $('[data-qz="next"]', q).hidden = true;
      });
      show(qs[0]); window.scrollTo(0, 0); focusTitle(qs[0]);
    }
    function answer(btn) {
      if (locked) return;
      locked = true;
      var q = qs[cur], good = parseInt(q.getAttribute("data-good"), 10), k = parseInt(btn.getAttribute("data-k"), 10), fb = $(".qz-fb", q);
      $$(".qz-o", q).forEach(function (o) {
        o.disabled = true;
        if (parseInt(o.getAttribute("data-k"), 10) === good) o.classList.add("good"); else if (o === btn) o.classList.add("bad");
      });
      var goodTxt = $(".qz-o.good span", q).textContent;
      if (k === good) { score++; fb.textContent = "Bonne réponse !"; fb.setAttribute("data-ok", "1"); buzz(20); }
      else { fb.textContent = nb("Raté… c’était : " + goodTxt); fb.setAttribute("data-ok", "0"); }
      fb.hidden = false;
      var nx = $('[data-qz="next"]', q); nx.hidden = false;
      try { nx.scrollIntoView({ block: "nearest", behavior: reduce ? "auto" : "smooth" }); } catch (e) {}
    }
    function next() {
      locked = false; cur++;
      if (cur >= qs.length) {
        if (score > best) best = score;
        LS.set("carnet.quiz", String(best)); paintBest();
        $("#qz-s").textContent = score; $("#qz-msg").textContent = msgs[score] || "";
        show(end); window.scrollTo(0, 0); focusTitle(end);
        Stamps.bonus("quiz", score >= qs.length - 1);
        if (score >= qs.length - 1) Confetti.burst(null, null, 90);
      } else { show(qs[cur]); window.scrollTo(0, 0); focusTitle(qs[cur]); }
    }
    root.addEventListener("click", function (e) {
      var t = e.target.closest ? e.target.closest("button, [data-qz]") : null; if (!t) return;
      var a = t.getAttribute("data-qz");
      if (a === "start" || a === "again") start();
      else if (a === "next") next();
      else if (t.classList.contains("qz-o")) answer(t);
    });
    paintBest();
    return { reset: reset };
  })();

  /* ───────────── cadenas : le test de personnalité s'ouvre le 29 décembre (heure du téléphone),
     ou plus tôt avec le mot secret d'Anne (gardé sur ce téléphone). La classe « tlock » de <html> allume les cadenas. ───────────── */
  var Lock = (function () {
    var root = $("#dt");
    var OPEN = root.getAttribute("data-open") || "";
    function byDate() { return !OPEN || Cal.today() >= OPEN; }
    function byWord() { return Cal.master(); }
    function locked() { return !byDate() && !byWord(); }
    function paint() {
      document.documentElement.classList.toggle("tlock", locked());
      var rl = $("#lk-relock"); if (rl) rl.hidden = !(byWord() && !byDate());   /* « remettre le cadenas » : seulement si ouvert avec le mot, avant la date */
    }
    function open() { Cal.setMaster(true); paint(); }
    function close() { Cal.setMaster(false); paint(); }
    document.addEventListener("visibilitychange", function () { if (!document.hidden) refreshAll(); });
    paint();
    return { locked: locked, paint: paint, good: Cal.good, open: open, close: close };
  })();

  /* ───────────── test de personnalité (mascottes) ───────────── */
  var Test = (function () {
    var root = $("#dt"), intro = $("#dt-intro"), qs = $$(".dt-q", root), tie = $("#dt-tie"), res = $("#dt-res"), lock = $("#dt-lock");
    var lkForm = $("#lk-form"), lkIn = $("#lk-in"), lkErr = $("#lk-err");
    var cur = 0, ans = [];
    var NAME = {}; $$("#v-doudous .dd-card").forEach(function (c) { NAME[c.getAttribute("data-who")] = $(".dd-kick", c).textContent; });
    var OPEN_TXT = ((lock.querySelector("b") || {}).textContent) || "";
    function show(el) { [lock, intro, tie, res].concat(qs).forEach(function (x) { x.hidden = x !== el; }); }
    function last() { var k = LS.get("carnet.doudou", ""); return NAME[k] ? k : ""; }
    function paintLast() {
      var k = last(), box = $("#dt-last");
      box.hidden = !k; if (k) $("#dt-lastn").textContent = NAME[k];
      hub("doudou", k ? "Ta mascotte : " + NAME[k] : "");
    }
    function reset() {
      cur = 0; ans = []; Lock.paint();
      if (Lock.locked()) { lkForm.hidden = true; $('[data-lk="ask"]', lock).hidden = false; lkErr.textContent = ""; lkIn.value = ""; show(lock); }
      else show(intro);
      paintLast();
    }
    function showQ(i) { cur = i; show(qs[i]); window.scrollTo(0, 0); focusTitle(qs[i]); }
    function lc(s) { return s.charAt(0).toLowerCase() + s.slice(1); }
    function result(key, again) {
      LS.set("carnet.doudou", key); paintLast();
      var c = $("#dd-" + key).cloneNode(true); c.removeAttribute("id");
      var kick = $(".dd-kick", c), h = $("h2", c);
      var name = kick.textContent, epi = h.textContent;
      kick.textContent = "Ta mascotte"; h.textContent = "Tu es " + name + ", " + lc(epi);
      res.innerHTML = ""; res.appendChild(c);
      var acts = document.createElement("div"); acts.className = "acts";
      acts.innerHTML = '<button class="btn" type="button" data-dt="start">Refaire le test</button><a class="btn alt" href="#/mascottes">Les quatre mascottes</a>';
      res.appendChild(acts);
      show(res); window.scrollTo(0, 0); focusTitle(res);
      if (!again) { Stamps.bonus("doudou", true); Confetti.burst(null, null, 70); }
    }
    function finish() {
      var n = {}, max = 0;
      ans.forEach(function (w) { n[w] = (n[w] || 0) + 1; if (n[w] > max) max = n[w]; });
      var win = Object.keys(n).filter(function (k) { return n[k] === max; });
      if (win.length === 1) { result(win[0]); return; }
      var names = win.map(function (k) { return NAME[k]; });
      $("#dt-tiep").textContent = "Égalité entre " + names.slice(0, -1).join(", ") + " et " + names[names.length - 1] + ". Comme dans le carnet : tes amis tranchent !";
      var box = $("#dt-ties"); box.innerHTML = "";
      win.forEach(function (k) {
        var b = document.createElement("button"); b.type = "button"; b.className = "dt-pick"; b.setAttribute("data-pick", k);
        var im = $("#dd-" + k + " .dd-img").cloneNode(true); im.className = "dd-mini"; im.removeAttribute("loading");
        b.appendChild(im); var sp = document.createElement("span"); sp.textContent = NAME[k]; b.appendChild(sp);
        box.appendChild(b);
      });
      show(tie); window.scrollTo(0, 0); focusTitle(tie);
    }
    root.addEventListener("click", function (e) {
      var t = e.target.closest ? e.target.closest("button, a") : null; if (!t) return;
      var lk = t.getAttribute("data-lk");
      if (lk === "ask") { t.hidden = true; lkForm.hidden = false; try { lkIn.focus(); } catch (x) {} return; }
      if (lk === "relock") { Lock.close(); reset(); toast("Cadenas remis"); return; }
      if (lock.contains(t)) return;                 /* le bouton « Ouvrir » du formulaire : c'est l'envoi du formulaire qui décide */
      if (Lock.locked()) { reset(); return; }       /* tout autre bouton tant que c'est fermé : retour à l'écran du cadenas */
      var a = t.getAttribute("data-dt");
      if (a === "start") { ans = []; showQ(0); }
      else if (a === "last") { var k = last(); if (k) result(k, true); }
      else if (a === "prev") { if (cur > 0) { ans.length = cur - 1; showQ(cur - 1); } }
      else if (t.classList.contains("qz-o")) {
        ans[cur] = t.getAttribute("data-who");
        if (cur + 1 < qs.length) showQ(cur + 1); else finish();
      } else if (t.getAttribute("data-pick")) result(t.getAttribute("data-pick"));
    });
    lkForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (Lock.good(lkIn.value)) { Lock.open(); lkIn.value = ""; lkErr.textContent = ""; reset(); toast("Test débloqué"); Confetti.burst(null, null, 50); return; }
      lkErr.textContent = "Ce n’est pas le bon mot."; buzz(40);
      lock.classList.remove("no"); void lock.offsetWidth; lock.classList.add("no");
      lkIn.select();
    });
    lock.addEventListener("animationend", function () { lock.classList.remove("no"); });
    paintLast();
    return { reset: reset };
  })();

  /* ───────────── blind test : le tableau des scores ───────────── */
  var Blind = (function () {
    var box = $("#bt"), lead = $("#bt-lead"), KEY = "carnet.blind";
    var ps = $$(".bt-p", box), sc = jget(KEY, {});
    function get(n) { var v = parseInt(sc[n], 10); return isNaN(v) || v < 0 ? 0 : v; }
    function paint() {
      var max = 0;
      ps.forEach(function (p) { var v = get(p.getAttribute("data-n")); if (v > max) max = v; });
      ps.forEach(function (p) {
        var n = p.getAttribute("data-n"), v = get(n);
        $("[data-score]", p).textContent = v;
        p.classList.toggle("lead", max > 0 && v === max);
        $(".bt-minus", p).disabled = v === 0;
      });
      var top = ps.filter(function (p) { return max > 0 && get(p.getAttribute("data-n")) === max; }).map(function (p) { return p.getAttribute("data-n"); });
      var pts = max + (max > 1 ? " points" : " point");
      lead.textContent = !max ? "Personne n’a encore marqué."
        : top.length === 1 ? top[0] + " mène avec " + pts + "."
        : "Égalité en tête : " + top.slice(0, -1).join(", ") + " et " + top[top.length - 1] + " (" + pts + ").";
    }
    function add(n, d, el) {
      var v = Math.max(0, get(n) + d); sc[n] = v; jset(KEY, sc); paint();
      if (el) { el.classList.remove("pop"); void el.offsetWidth; el.classList.add("pop"); }
      if (d > 0) { buzz(15); Stamps.bonus("blind"); }
    }
    box.addEventListener("click", function (e) {
      var t = e.target.closest ? e.target.closest("button") : null; if (!t) return;
      var p = t.closest(".bt-p"), n = p.getAttribute("data-n");
      if (t.classList.contains("bt-main")) add(n, 1, $("[data-score]", p));
      else if (t.classList.contains("bt-minus")) add(n, -1, $("[data-score]", p));
    });
    twoTap($("#bt-reset"), "Sûr ? Touche encore pour tout remettre à zéro", function () { sc = {}; jset(KEY, sc); paint(); toast("Scores remis à zéro"); });
    paint();
    return { paint: paint };
  })();

  /* ───────────── mots mêlés ───────────── */
  var Mots = (function () {
    var board = $("#mm-board"), N = parseInt(board.getAttribute("data-n"), 10), cells = $$(".c", board);
    var W = JSON.parse(board.getAttribute("data-words")).map(function (a) { return { k: a[0], r: a[1], c: a[2], dr: a[3], dc: a[4], n: a[0].length }; });
    var card = $("#mm-card"), live = $("#mm-live"), gFound = $("#mm-found"), gSel = $("#mm-sel"), gRef = $("#mm-ref");
    var NS = "http://www.w3.org/2000/svg", KEY = "carnet.mots";
    var DIRS = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]];   /* [dc, dr] */
    var found = (LS.get(KEY, "") || "").split(",").filter(function (k) { return k && W.some(function (w) { return w.k === k; }); });
    var zoom = false, drag = null, anchor = null, hintT = 0, liveT = 0, ptrId = null;
    function wordOf(k) { for (var i = 0; i < W.length; i++) if (W[i].k === k) return W[i]; return null; }
    function letter(r, c) { return cells[r * N + c].textContent; }
    function el(tag, attrs, parent) {
      var e = document.createElementNS(NS, tag);
      for (var k in attrs) e.setAttribute(k, attrs[k]);
      if (parent) parent.appendChild(e);
      return e;
    }
    function line(g, r0, c0, r1, c1, cls) {
      return el("line", { x1: c0 + 0.5, y1: r0 + 0.5, x2: c1 + 0.5 + (r0 === r1 && c0 === c1 ? 0.001 : 0), y2: r1 + 0.5, "class": cls, "stroke-linecap": "round" }, g);
    }
    function note(t, sticky) {
      live.textContent = t || " ";
      clearTimeout(liveT);
      if (t && !sticky) liveT = setTimeout(function () { live.textContent = " "; }, 2600);
    }
    function measure() { board.style.setProperty("--cell", (board.clientWidth / N) + "px"); }
    function paint() {
      $("#mm-count").textContent = found.length;
      $("#mm-fill").style.width = (100 * found.length / W.length) + "%";
      $$("#mm-words li").forEach(function (li) {
        var k = li.getAttribute("data-k"), i = found.indexOf(k);
        li.classList.toggle("found", i >= 0);
        li.style.setProperty("--f", i >= 0 ? "var(--f" + (i % 8) + ")" : "transparent");
      });
      hub("mots", found.length ? found.length + " sur " + W.length + " mots trouvés" : "");
    }
    function drawFound() {
      gFound.innerHTML = "";
      found.forEach(function (k, i) {
        var w = wordOf(k);
        line(gFound, w.r, w.c, w.r + (w.n - 1) * w.dr, w.c + (w.n - 1) * w.dc, "f" + (i % 8));
      });
    }
    function cellAt(e) {
      var rc = board.getBoundingClientRect(), cw = rc.width / N;
      var fx = (e.clientX - rc.left) / cw, fy = (e.clientY - rc.top) / cw;
      return { r: Math.max(0, Math.min(N - 1, Math.floor(fy))), c: Math.max(0, Math.min(N - 1, Math.floor(fx))), fx: fx, fy: fy };
    }
    function snap(a, fx, fy) {
      var dx = fx - (a.c + 0.5), dy = fy - (a.r + 0.5);
      if (Math.hypot(dx, dy) < 0.55) return { n: 0, dr: 0, dc: 0 };
      var i = (Math.round(Math.atan2(dy, dx) / (Math.PI / 4)) + 8) % 8, dc = DIRS[i][0], dr = DIRS[i][1];
      var t = Math.round((dx * dc + dy * dr) / (dc * dc + dr * dr));
      var mc = dc > 0 ? N - 1 - a.c : dc < 0 ? a.c : 99, mr = dr > 0 ? N - 1 - a.r : dr < 0 ? a.r : 99;
      return { n: Math.max(0, Math.min(t, mc, mr)), dr: dr, dc: dc };
    }
    function lettersOf(a, s) { var o = ""; for (var i = 0; i <= s.n; i++) o += letter(a.r + i * s.dr, a.c + i * s.dc); return o; }
    function clearSel() { gSel.innerHTML = ""; }
    function drawSel(a, s, cls) { clearSel(); line(gSel, a.r, a.c, a.r + s.n * s.dr, a.c + s.n * s.dc, cls || "sel"); }
    function rev(s) { return s.split("").reverse().join(""); }
    function check(a, s) {
      var str = lettersOf(a, s), w = null;
      if (s.n >= 1) for (var i = 0; i < W.length; i++) {
        if (found.indexOf(W[i].k) < 0 && (W[i].k === str || W[i].k === rev(str))) { w = W[i]; break; }
      }
      if (w) {
        found.push(w.k); LS.set(KEY, found.join(","));
        clearSel(); drawFound(); paint(); buzz(25);
        var li = $('#mm-words li[data-k="' + w.k + '"] span'), nm = li ? li.textContent : w.k;
        note(nm + " trouvé !");
        if (found.length === W.length) { toast("Bravo ! Les " + W.length + " mots sont trouvés"); Confetti.burst(null, null, 140); Stamps.bonus("mots"); }
        else if (found.length % 10 === 0) Confetti.burst(null, null, 40);
        return true;
      }
      if (s.n >= 1) {
        var bad = el("line", { x1: a.c + 0.5, y1: a.r + 0.5, x2: a.c + 0.5 + s.n * s.dc, y2: a.r + 0.5 + s.n * s.dr, "class": "sel bad", "stroke-linecap": "round" }, null);
        clearSel(); gSel.appendChild(bad); setTimeout(clearSel, 380);
        note(nb(str + " : ce n’est pas dans la liste"));
      }
      return false;
    }
    function down(e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      var a = cellAt(e);
      drag = { a: a, s: { n: 0, dr: 0, dc: 0 }, x: e.clientX, y: e.clientY, moved: false };
      ptrId = e.pointerId;
      try { board.setPointerCapture(e.pointerId); } catch (x) {}
      if (!zoom) { drawSel(a, drag.s); note(letter(a.r, a.c), true); }
    }
    function move(e) {
      if (!drag || e.pointerId !== ptrId) return;
      if (Math.hypot(e.clientX - drag.x, e.clientY - drag.y) > 6) drag.moved = true;
      if (zoom) return;
      var c = cellAt(e), s = snap(drag.a, c.fx, c.fy);
      drag.s = s; drawSel(drag.a, s); note(lettersOf(drag.a, s), true);
    }
    function aligned(a, b) { var dr = b.r - a.r, dc = b.c - a.c; return (dr === 0 || dc === 0 || Math.abs(dr) === Math.abs(dc)) && (dr !== 0 || dc !== 0); }
    function up(e) {
      if (!drag || e.pointerId !== ptrId) return;
      var d = drag; drag = null; ptrId = null;
      try { board.releasePointerCapture(e.pointerId); } catch (x) {}
      if (e.type === "pointercancel") { clearSel(); if (anchor) markAnchor(); return; }
      if (!zoom && d.s.n >= 1) { anchor = null; check(d.a, d.s); return; }
      if (d.moved && zoom) { clearSel(); if (anchor) markAnchor(); return; }
      /* simple touche : première lettre, puis dernière lettre */
      var c = cellAt(e);
      if (!anchor) { anchor = { r: c.r, c: c.c }; markAnchor(); note(letter(c.r, c.c) + " … touche la dernière lettre", false); return; }
      if (anchor.r === c.r && anchor.c === c.c) { anchor = null; clearSel(); note("Sélection annulée"); return; }
      if (aligned(anchor, c)) {
        var s = { n: Math.max(Math.abs(c.r - anchor.r), Math.abs(c.c - anchor.c)), dr: Math.sign(c.r - anchor.r), dc: Math.sign(c.c - anchor.c) };
        var a = anchor; anchor = null; check(a, s);
      } else { anchor = { r: c.r, c: c.c }; markAnchor(); note(letter(c.r, c.c) + " … touche la dernière lettre", false); }
    }
    function markAnchor() { clearSel(); if (anchor) line(gSel, anchor.r, anchor.c, anchor.r, anchor.c, "sel anchor"); }
    board.addEventListener("pointerdown", down);
    board.addEventListener("pointermove", move);
    board.addEventListener("pointerup", up);
    board.addEventListener("pointercancel", up);
    board.addEventListener("contextmenu", function (e) { e.preventDefault(); });

    $("#mm-zoom").addEventListener("click", function () {
      zoom = !zoom; card.setAttribute("data-zoom", zoom ? "1" : "0");
      this.setAttribute("aria-pressed", zoom ? "true" : "false"); $("span", this).textContent = zoom ? "Réduire" : "Agrandir";
      anchor = null; clearSel(); measure();
      note(zoom ? "Grille agrandie : fais-la défiler, puis touche la première et la dernière lettre." : "", false);
    });
    $("#mm-hint").addEventListener("click", function () {
      var left = W.filter(function (w) { return found.indexOf(w.k) < 0; });
      if (!left.length) { toast("Tous les mots sont trouvés !"); return; }
      var w = left[Math.floor(Math.random() * left.length)];
      gRef.innerHTML = ""; el("circle", { cx: w.c + 0.5, cy: w.r + 0.5, r: 0.78, "class": "hint" }, gRef);
      clearTimeout(hintT); hintT = setTimeout(function () { gRef.innerHTML = ""; }, 3200);
      note("Un mot de " + w.n + " lettres commence ici.");
      try { var rc = board.getBoundingClientRect(), y = rc.top + (w.r + 0.5) * rc.height / N; if (y < 80 || y > innerHeight - 90) window.scrollBy({ top: y - innerHeight / 2, behavior: reduce ? "auto" : "smooth" }); } catch (e) {}
    });
    twoTap($("#mm-reset"), "Sûr ? Touche encore pour tout effacer", function () {
      found = []; LS.del(KEY); anchor = null; clearSel(); gRef.innerHTML = ""; drawFound(); paint(); note("Grille remise à zéro");
    });
    window.addEventListener("resize", function () { if (!$("#v-mots").hidden) measure(); });
    paint(); drawFound(); measure();
    return { enter: function () { measure(); } };
  })();

  /* ───────────── horoscope ───────────── */
  var Horo = (function () {
    var seen = false, io = null;
    function grant() { if (seen) return; seen = true; if (io) io.disconnect(); Stamps.bonus("etoiles"); }
    return {
      enter: function () {
        if (seen) return;
        var last = $("#v-horo .hs:last-child");
        if (!last) return;
        if (!("IntersectionObserver" in window)) { setTimeout(grant, 4000); return; }
        if (io) io.disconnect();
        io = new IntersectionObserver(function (es) { es.forEach(function (x) { if (x.isIntersecting) grant(); }); }, { threshold: 0.6 });
        io.observe(last);
      },
      leave: function () { if (io) io.disconnect(); }
    };
  })();

  /* ───────────── le mot de la mascotte (accueil) ───────────── */
  (function () {
    var hq = $("#hq"); if (!hq) return;
    var list = [], imgs = {}, last = -1;
    try { list = JSON.parse(hq.getAttribute("data-q")); imgs = JSON.parse(hq.getAttribute("data-img")); } catch (e) { return; }
    var NAMES_ = { aftonsparv: "Aftonsparv", boop: "Boop", minou: "Minou", moomoo: "Moomoo" };
    var im = $("#hq-img"), who = $("#hq-who"), q = $("#hq-q"), btn = $("#hq-btn");
    function show(i) {
      last = i; var it = list[i];
      im.src = imgs[it[0]]; im.alt = NAMES_[it[0]] || ""; who.textContent = NAMES_[it[0]] || ""; q.textContent = nb("« " + it[1] + " »");
    }
    function pick() { var i; do { i = Math.floor(Math.random() * list.length); } while (i === last && list.length > 1); return i; }
    btn.addEventListener("click", function () {
      show(pick()); btn.classList.remove("wig"); void btn.offsetWidth; btn.classList.add("wig");
    });
    btn.addEventListener("animationend", function () { btn.classList.remove("wig"); });
    show(pick());
  })();

  /* ───────────── étape 4 : défi du jour, mot du jour, bingo, carnet gourmand, prix, horoscope de l'accueil ───────────── */
/*@GAMES2@*/
/*@TRANS@*/
/*@ENV@*/
/*@PHOTO@*/

  /* tout repeindre (mot secret saisi, retour dans l'appli un autre jour, cadenas remis) */
  function refreshAll() {
    Lock.paint(); Gates.paintHub(); HomeHoro.paint(); Env.paint();
    if (curName) api.enter(curName);
  }

  var api = {
    enter: function (name) {
      Lock.paint();
      Gates.paintHub();
      var open = Gates.paintView(name);
      HomeHoro.paint();
      Env.enter(name);
      if (name === "jeux") Test.reset();            /* met à jour la tuile du test (cadenas, ou « Ta mascotte : … ») */
      if (name === "quiz") Quiz.reset();
      else if (name === "test") Test.reset();
      else if (name === "blind") Blind.paint();
      else if (name === "mots") { if (open) Mots.enter(); }
      else if (name === "pass") Stamps.paint();
      else if (name === "defi") Defi.enter();
      else if (name === "mot") Mot.enter();
      else if (name === "bingo") Bingo.enter();
      else if (name === "gourmand") Gourmand.enter();
      else if (name === "prix") Prix.enter();
      else if (name === "trad") Trad.enter();
      else if (name === "photoinv") PhotoInv.enter();
      else if (name === "reportage") Rep.enter();
      if (name === "horo" && open) Horo.enter(); else Horo.leave();
    },
    photo: function (id) {
      if (Stamps.day(id)) toast("Photo gardée : le tampon du jour est dans ton passeport");
      var n = Object.keys(hasPhoto).filter(function (k) { return hasPhoto[k] && days.indexOf(k) >= 0; }).length;
      if (n >= 5) Stamps.bonus("photos");
    }
  };
  document.addEventListener("visibilitychange", function () { if (!document.hidden) refreshAll(); });
  Gates.paintHub();
  return api;
})();
