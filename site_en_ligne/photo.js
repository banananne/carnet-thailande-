  /* ───────────── reportage photo : le polaroïd des voyageurs et le fil des invité·e·s ─────────────
     Ce fichier est collé dans games.js (à la place de « @PHOTO@ »). Les polaroïds des voyageurs ne partent nulle part tout seuls : on les partage à la main.
     Ceux du reportage sont publiés CHIFFRÉS (fichiers reportage/*.bin) : le code des invité·e·s les ouvre, sur le téléphone, avec WebCrypto. */
  var PhotoInv = (function () {
    var v = $("#v-photoinv"); if (!v) return { enter: function () {} };
    var DAYS_ = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
    var MONTHS_ = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
    function dayLabel(iso) {      /* « 2026-12-19 » → « samedi 19 décembre 2026 » */
      var y = +iso.slice(0, 4), m = +iso.slice(5, 7), d = +iso.slice(8, 10), dt = new Date(y, m - 1, d);
      if (!y || !m || !d || isNaN(dt.getTime())) return "";
      return DAYS_[dt.getDay()] + " " + (d === 1 ? "1er" : d) + " " + MONTHS_[m - 1] + " " + y;
    }
    var file = $("#pi-file"), form = $("#pi-form"), cap = $("#pi-cap"), dateIn = $("#pi-date"), cv = $("#pi-cv"), st = $("#pi-st"), send = $("#pi-send");
    var ctx = cv.getContext ? cv.getContext("2d") : null, img = null, imgUrl = "", name = "", fileName = "";
    var W = 1080, H = 1500, M = 60, PW = 960, PH = 1200;
    function todayIso() { var d = new Date(); return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate()); }
    function wrap(text, font, maxW) {      /* au plus deux lignes ; la taille de la police diminue si le texte est long */
      var size = 46, lines;
      for (; size >= 30; size -= 4) {
        ctx.font = "italic 400 " + size + "px \"Libre Baskerville\", Georgia, serif";
        var words = text.split(/\s+/), cur = ""; lines = [];
        for (var i = 0; i < words.length; i++) {
          var t = cur ? cur + " " + words[i] : words[i];
          if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = words[i]; } else cur = t;
        }
        if (cur) lines.push(cur);
        if (lines.length <= 2) break;
      }
      return { lines: lines.slice(0, 2), size: size };
    }
    function draw() {
      if (!ctx) return;
      ctx.fillStyle = "#FFFFFF"; ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = "#E7ECF8"; ctx.fillRect(M, M, PW, PH);
      if (img) {
        var iw = img.naturalWidth, ih = img.naturalHeight, sc = Math.max(PW / iw, PH / ih), sw = PW / sc, sh = PH / sc;
        ctx.drawImage(img, (iw - sw) / 2, (ih - sh) * 0.4, sw, sh, M, M, PW, PH);     /* recadrage en 4/5, un peu vers le haut (les visages) */
      }
      var text = cap.value.replace(/\s+/g, " ").trim();
      ctx.textBaseline = "alphabetic"; ctx.fillStyle = "#1F2548"; ctx.textAlign = "left";
      if (text) {
        var w = wrap(text, "", PW);
        ctx.font = "italic 400 " + w.size + "px \"Libre Baskerville\", Georgia, serif";
        var y0 = w.lines.length === 1 ? 1342 : 1328;
        for (var i = 0; i < w.lines.length; i++) ctx.fillText(w.lines[i], M, y0 + i * Math.round(w.size * 1.22));
      }
      ctx.fillStyle = "#566086";
      ctx.font = "500 30px Barlow, system-ui, sans-serif";
      try { ctx.letterSpacing = "3px"; } catch (e) {}
      ctx.textAlign = "left"; ctx.fillText(dayLabel(dateIn.value).toUpperCase(), M, 1446);
      ctx.textAlign = "right"; ctx.fillText(name.toUpperCase(), W - M, 1446);
      try { ctx.letterSpacing = "0px"; } catch (e) {}
    }
    var drawT = 0;
    function redraw() { clearTimeout(drawT); drawT = setTimeout(draw, 60); }
    function fonts() {
      try { if (document.fonts && document.fonts.load) return Promise.all([document.fonts.load("italic 400 40px \"Libre Baskerville\""), document.fonts.load("500 30px Barlow")]); } catch (e) {}
      return Promise.resolve();
    }
    function toBlob(cb) {
      draw();
      if (cv.toBlob) cv.toBlob(cb, "image/jpeg", 0.88);
      else { try { var u = cv.toDataURL("image/jpeg", 0.88), b = atob(u.split(",")[1]), a = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); cb(new Blob([a], { type: "image/jpeg" })); } catch (e) { cb(null); } }
    }
    function nameOut() { return "polaroid_" + (dateIn.value || todayIso()) + "_" + (name || "voyage") + ".jpg"; }
    function save(blob) {
      var a = document.createElement("a"), u = URL.createObjectURL(blob);
      a.href = u; a.download = nameOut(); document.body.appendChild(a); a.click();
      setTimeout(function () { document.body.removeChild(a); URL.revokeObjectURL(u); }, 4000);
    }
    function reset() {
      if (imgUrl) { try { URL.revokeObjectURL(imgUrl); } catch (e) {} }
      imgUrl = ""; img = null; file.value = ""; form.hidden = true; st.textContent = ""; cap.value = "";
    }
    file.addEventListener("change", function () {
      var f = file.files && file.files[0]; if (!f) return;
      if (imgUrl) { try { URL.revokeObjectURL(imgUrl); } catch (e) {} }
      st.textContent = "Je prépare ton polaroïd…"; fileName = f.name;
      var im = new Image();
      im.onload = function () {
        img = im; st.textContent = "";
        var d = f.lastModified ? new Date(f.lastModified) : new Date();
        dateIn.value = d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate());
        form.hidden = false;
        fonts().then(function () { draw(); try { cap.focus({ preventScroll: true }); } catch (e) {} });
      };
      im.onerror = function () { img = null; form.hidden = true; st.textContent = "Cette photo n’a pas pu être lue. Essaie avec une autre."; };
      imgUrl = URL.createObjectURL(f); im.src = imgUrl;
    });
    cap.addEventListener("input", redraw);
    dateIn.addEventListener("input", redraw); dateIn.addEventListener("change", redraw);
    $("#pi-again").addEventListener("click", function () { reset(); window.scrollTo(0, 0); });
    $("#pi-save").addEventListener("click", function () {
      toBlob(function (b) { if (!b) { st.textContent = "Impossible de fabriquer l’image sur ce téléphone."; return; } save(b); toast("Polaroïd enregistré"); });
    });
    $("#pi-share").addEventListener("click", function () {
      toBlob(function (b) {
        if (!b) { st.textContent = "Impossible de fabriquer l’image sur ce téléphone."; return; }
        var f = null;
        try { f = new File([b], nameOut(), { type: "image/jpeg" }); } catch (e) { f = null; }
        if (f && navigator.canShare && navigator.canShare({ files: [f] }) && navigator.share) {
          navigator.share({ files: [f], title: "Thaïlande 2026" }).catch(function (e) { if (e && e.name !== "AbortError") { save(b); toast("Polaroïd enregistré à la place"); } });
        } else { save(b); toast("Ton téléphone ne partage pas directement : polaroïd enregistré"); }
      });
    });
    return {
      enter: function () {
        name = LS.get("carnet.who", "");
        if (name === "Invité") name = "";
        send.textContent = name === "Anne"
          ? "Quand il te plaît, garde-le : tu le transmets au carnet avec les autres, et il est publié dans le reportage des invité·e·s."
          : "Envoie-le à Anne (message, AirDrop…) : elle le fera publier dans le reportage des invité·e·s.";
        send.textContent = nb(send.textContent);
        if (!form.hidden) redraw();
      }
    };
  })();

  var Rep = (function () {
    var v = $("#v-reportage"); if (!v) return { enter: function () {} };
    var lock = $("#rp-lock"), form = $("#rp-form"), inp = $("#rp-code"), err = $("#rp-err"), msg = $("#rp-msg"), feed = $("#rp-feed"), foot = $("#rp-foot"), big = $("#rp-big");
    var subtle = null, enc = null, dec = null;
    try { subtle = (window.crypto && window.crypto.subtle) || null; enc = new TextEncoder(); dec = new TextDecoder("utf-8"); } catch (e) { subtle = null; }
    var CAN = !!(subtle && enc && dec && window.Promise && window.Uint8Array && window.fetch);
    var KEY = "carnet.rep.code";
    var S = { man: null, key: null, salt: "", urls: {}, busy: false, obs: null };
    var DAYS_ = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
    var MONTHS_ = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
    function dayLabel(iso) {
      var y = +iso.slice(0, 4), m = +iso.slice(5, 7), d = +iso.slice(8, 10), dt = new Date(y, m - 1, d);
      if (!y || !m || !d || isNaN(dt.getTime())) return iso;
      var s = DAYS_[dt.getDay()] + " " + (d === 1 ? "1er" : d) + " " + MONTHS_[m - 1];
      return s.charAt(0).toUpperCase() + s.slice(1);
    }
    function norm(s) {
      var t = String(s).toLowerCase();
      try { t = t.normalize("NFD").replace(/[̀-ͯ]/g, ""); } catch (e) {}
      return t.replace(/[^a-z0-9]/g, "");
    }
    function unb64(s) { var b = atob(s), u = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; }
    function derive(code, saltB64, it) {
      return subtle.importKey("raw", enc.encode(norm(code)), "PBKDF2", false, ["deriveKey"]).then(function (k) {
        return subtle.deriveKey({ name: "PBKDF2", hash: "SHA-256", salt: unb64(saltB64), iterations: it }, k, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
      });
    }
    function say(t) { msg.textContent = t || ""; }
    function showLock(on) { lock.hidden = !on; }
    function clearFeed() { feed.textContent = ""; foot.hidden = true; if (S.obs) { try { S.obs.disconnect(); } catch (e) {} S.obs = null; } }
    function fetchMan() {
      return fetch("reportage/m.json", { cache: "no-cache" }).then(function (r) {
        if (r.status === 404) return null;
        if (!r.ok) throw new Error("http");
        return r.json();
      });
    }
    function openMan(man, key) {
      return subtle.decrypt({ name: "AES-GCM", iv: unb64(man.iv), additionalData: enc.encode("rep|m"), tagLength: 128 }, key, unb64(man.ct))
        .then(function (pt) { return JSON.parse(dec.decode(pt)).p; });
    }
    function sniff(u8) { return u8[0] === 0x89 ? "image/png" : (u8[0] === 0x52 ? "image/webp" : "image/jpeg"); }
    function loadPhoto(f, im, fig) {
      if (S.urls[f]) { im.src = S.urls[f]; fig.classList.remove("wait"); fig.classList.add("on"); return Promise.resolve(); }
      return fetch("reportage/" + f + ".bin").then(function (r) { if (!r.ok) throw new Error("http"); return r.arrayBuffer(); }).then(function (buf) {
        var u = new Uint8Array(buf);
        return subtle.decrypt({ name: "AES-GCM", iv: u.slice(0, 12), additionalData: enc.encode("rep|" + f), tagLength: 128 }, S.key, u.slice(12));
      }).then(function (pt) {
        var url = URL.createObjectURL(new Blob([pt], { type: sniff(new Uint8Array(pt, 0, 4)) }));
        S.urls[f] = url; im.src = url; fig.classList.remove("wait"); fig.classList.add("on");
      }).catch(function () { fig.classList.remove("wait"); fig.title = "Cette photo n’a pas pu être chargée."; });
    }
    function render(list) {
      clearFeed();
      if (!list.length) { say("Le reportage commence : les premières photos arrivent pendant le voyage. Reviens bientôt !"); return; }
      say(nb(list.length + (list.length > 1 ? " photos" : " photo") + " · des plus récentes aux plus anciennes"));
      var items = list.map(function (it, i) { return { f: it.f, d: it.d, w: it.w, i: i }; });
      items.sort(function (a, b) { return a.d < b.d ? 1 : a.d > b.d ? -1 : b.i - a.i; });
      var lastD = "", figs = [];
      items.forEach(function (it) {
        if (it.d !== lastD) { var h = document.createElement("h2"); h.className = "rp-day"; h.textContent = dayLabel(it.d); feed.appendChild(h); lastD = it.d; }
        var fig = document.createElement("figure"), im = document.createElement("img");
        fig.className = "rp-ph wait"; fig.setAttribute("data-f", it.f); fig.setAttribute("role", "button"); fig.setAttribute("tabindex", "0");
        fig.setAttribute("aria-label", "Agrandir la photo de " + it.w + ", " + dayLabel(it.d));
        im.alt = "Polaroïd de " + it.w + ", " + dayLabel(it.d); im.decoding = "async";
        fig.appendChild(im); feed.appendChild(fig); figs.push({ f: it.f, im: im, fig: fig });
      });
      foot.hidden = false;
      if (window.IntersectionObserver) {
        S.obs = new IntersectionObserver(function (es) {
          es.forEach(function (e) {
            if (!e.isIntersecting) return;
            S.obs.unobserve(e.target);
            var o = figs.filter(function (x) { return x.fig === e.target; })[0]; if (o) loadPhoto(o.f, o.im, o.fig);
          });
        }, { rootMargin: "600px 0px" });
        figs.forEach(function (o) { S.obs.observe(o.fig); });
      } else {
        figs.reduce(function (p, o) { return p.then(function () { return loadPhoto(o.f, o.im, o.fig); }); }, Promise.resolve());
      }
    }
    function tryCode(code, silent) {
      if (!S.man) return Promise.resolve(false);
      var man = S.man;
      return derive(code, man.s, man.it || 150000).then(function (key) {
        return openMan(man, key).then(function (list) { S.key = key; S.salt = man.s; LS.set(KEY, norm(code)); showLock(false); err.textContent = ""; render(list); return true; });
      }).catch(function () {
        if (!silent) err.textContent = "Ce n’est pas le bon code. Vérifie-le et réessaie.";
        return false;
      });
    }
    function start() {
      if (S.busy) return; S.busy = true;
      if (!CAN) { say("Ce téléphone ne sait pas ouvrir le reportage. Essaie avec une version récente de Safari ou de Chrome."); S.busy = false; return; }
      if (!S.key) say("Je regarde s’il y a des photos…");
      fetchMan().then(function (man) {
        if (!man) { clearFeed(); showLock(false); say("Le reportage n’a pas encore commencé : les premières photos arrivent pendant le voyage. Reviens bientôt !"); return; }
        S.man = man;
        if (S.key && S.salt === man.s) {       /* déjà ouvert : on met le fil à jour (nouvelles photos) */
          return openMan(man, S.key).then(function (list) { render(list); }).catch(function () { S.key = null; showLock(true); say(""); });
        }
        var saved = LS.get(KEY, "");
        var p = saved ? tryCode(saved, true) : Promise.resolve(false);
        return p.then(function (ok) { if (!ok) { clearFeed(); showLock(true); say(""); try { inp.value = ""; } catch (e) {} } });
      }).catch(function () {
        clearFeed(); showLock(false); say("Impossible de charger le reportage pour le moment. Vérifie ta connexion et reviens.");
      }).then(function () { S.busy = false; });
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault(); err.textContent = "";
      var c = inp.value; if (!norm(c)) { err.textContent = "Tape le code reçu."; return; }
      err.textContent = "Je vérifie…";
      tryCode(c, false).then(function (ok) { if (ok) inp.value = ""; });
    });
    $("#rp-forget").addEventListener("click", function () {
      LS.del(KEY); S.key = null; S.salt = "";
      Object.keys(S.urls).forEach(function (k) { try { URL.revokeObjectURL(S.urls[k]); } catch (e) {} }); S.urls = {};
      clearFeed(); say(""); showLock(true); toast("Code oublié sur ce téléphone");
    });
    function openBig(fig) {
      var im = $("img", fig); if (!im || !im.src || !fig.classList.contains("on")) return;
      $("img", big).src = im.src; $("img", big).alt = im.alt; big.hidden = false;
    }
    feed.addEventListener("click", function (e) { var f = e.target.closest ? e.target.closest(".rp-ph") : null; if (f) openBig(f); });
    feed.addEventListener("keydown", function (e) { if ((e.key === "Enter" || e.key === " ") && e.target.classList && e.target.classList.contains("rp-ph")) { e.preventDefault(); openBig(e.target); } });
    big.addEventListener("click", function () { big.hidden = true; });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !big.hidden) big.hidden = true; });
    return { enter: function () { big.hidden = true; start(); } };
  })();
