  /* ───────────── reportage photo : le polaroïd des voyageurs et le fil des invité·e·s ─────────────
     Ce fichier est collé dans games.js (à la place de « @PHOTO@ »). Les polaroïds du reportage sont CHIFFRÉS sur le téléphone de celui qui les publie
     (AES-GCM, clé tirée du code des invité·e·s par PBKDF2) : ni Supabase ni le site ne peuvent les lire ; le code ouvre les photos sur le téléphone des invité·e·s.
     Deux modes : « Supabase » (#rep-cfg présent : publication directe, photos et liste chez Supabase) ou « fichiers » (reportage/m.json + p*.bin publiés par Claude). */
  var RepC = (function () {
    var subtle = null, enc = null, dec = null;
    try { subtle = (window.crypto && window.crypto.subtle) || null; enc = new TextEncoder(); dec = new TextDecoder("utf-8"); } catch (e) { subtle = null; }
    var CAN = !!(subtle && enc && dec && window.Promise && window.Uint8Array && window.fetch);
    var CFG = null; try { var el = $("#rep-cfg"); if (el) CFG = JSON.parse(el.textContent); } catch (e) { CFG = null; }
    var KEY = "carnet.rep.code", MINE = "carnet.rep.mine", st = { key: null, salt: "" };
    function norm(s) {
      var t = String(s).toLowerCase();
      try { t = t.normalize("NFD").replace(/[̀-ͯ]/g, ""); } catch (e) {}
      return t.replace(/[^a-z0-9]/g, "");
    }
    function unb64(s) { var b = atob(s), u = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; }
    function b64(u8) { var s = ""; for (var i = 0; i < u8.length; i += 4096) s += String.fromCharCode.apply(null, u8.subarray(i, i + 4096)); return btoa(s); }
    function rand(n) { var u = new Uint8Array(n); window.crypto.getRandomValues(u); return u; }
    function hex(u8) { var s = ""; for (var i = 0; i < u8.length; i++) s += (u8[i] < 16 ? "0" : "") + u8[i].toString(16); return s; }
    function cat(a, b) { var u = new Uint8Array(a.length + b.length); u.set(a, 0); u.set(b, a.length); return u; }
    function derive(code, saltB64, it) {
      return subtle.importKey("raw", enc.encode(norm(code)), "PBKDF2", false, ["deriveKey"]).then(function (k) {
        return subtle.deriveKey({ name: "PBKDF2", hash: "SHA-256", salt: unb64(saltB64), iterations: it }, k, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
      });
    }
    function readBuf(blob) {
      if (blob.arrayBuffer) return blob.arrayBuffer();
      return new Promise(function (res, rej) { var r = new FileReader(); r.onload = function () { res(r.result); }; r.onerror = rej; r.readAsArrayBuffer(blob); });
    }
    function head(extra) {
      var h = { apikey: CFG.key };
      if (/^eyJ/.test(CFG.key)) h.Authorization = "Bearer " + CFG.key;       /* ancienne clé « anon » (JWT) ; la clé « publishable » ne se met que dans apikey */
      for (var k in extra) h[k] = extra[k];
      return h;
    }
    function ok(r) { if (!r.ok) { var e = new Error("http " + r.status); e.status = r.status; throw e; } return r; }
    function canary() {      /* la « pièce témoin » publiée avec le site : un petit texte chiffré avec le code (sert à vérifier le code) */
      return fetch("reportage/c.json", { cache: "no-cache" }).then(function (r) { if (r.status === 404) return null; ok(r); return r.json(); });
    }
    function verify(code) {      /* → { none: true } si aucun reportage n'existe ; { key } si le code est bon ; rejette OperationError si le code est mauvais */
      return canary().then(function (c) {
        if (!c) return { none: true };
        return derive(code, c.s, c.it || 150000).then(function (key) {
          return subtle.decrypt({ name: "AES-GCM", iv: unb64(c.iv), additionalData: enc.encode("rep|c"), tagLength: 128 }, key, unb64(c.ct)).then(function () {
            st.key = key; st.salt = c.s; return { key: key };
          });
        });
      });
    }
    function unlockSaved() {
      if (st.key) return Promise.resolve(true);
      var saved = LS.get(KEY, ""); if (!saved) return Promise.resolve(false);
      return verify(saved).then(function (r) { return !!r.key; }).catch(function (e) { if (e && e.name === "OperationError") { LS.del(KEY); return false; } throw e; });
    }
    function remember(code) { LS.set(KEY, norm(code)); }
    function forget() { LS.del(KEY); st.key = null; st.salt = ""; }
    /* liste des polaroïds : chaque ligne a une description chiffrée (date, prénom, légende) ; les lignes illisibles (faux envois) sont ignorées */
    function list() {
      return fetch(CFG.url + "/rest/v1/reportage?select=id,f,meta,created_at&order=created_at.desc&limit=500", { headers: head({}), cache: "no-store" }).then(ok).then(function (r) { return r.json(); }).then(function (rows) {
        return Promise.all(rows.map(function (row, i) {
          if (!/^p[0-9a-f]{12}$/.test(row.f || "")) return null;
          var u; try { u = unb64(row.meta); } catch (e) { return null; }
          return subtle.decrypt({ name: "AES-GCM", iv: u.slice(0, 12), additionalData: enc.encode("rep|meta|" + row.f), tagLength: 128 }, st.key, u.slice(12)).then(function (pt) {
            var m = JSON.parse(dec.decode(pt));
            if (!/^\d{4}-\d{2}-\d{2}$/.test(m.d || "")) return null;
            return { f: row.f, id: row.id, d: m.d, w: String(m.w || "").slice(0, 20), c: String(m.c || "").slice(0, 100), i: rows.length - i };
          }).catch(function () { return null; });
        })).then(function (a) { return a.filter(Boolean); });
      });
    }
    function photoUrl(f) { return CFG.url + "/storage/v1/object/public/reportage/" + f; }
    function newId() {
      if (window.crypto.randomUUID) return window.crypto.randomUUID();
      var u = rand(16); u[6] = (u[6] & 15) | 64; u[8] = (u[8] & 63) | 128; var h = hex(u);
      return h.slice(0, 8) + "-" + h.slice(8, 12) + "-" + h.slice(12, 16) + "-" + h.slice(16, 20) + "-" + h.slice(20);
    }
    function sealWith(buf, aad) {
      var iv = rand(12);
      return subtle.encrypt({ name: "AES-GCM", iv: iv, additionalData: enc.encode(aad), tagLength: 128 }, st.key, buf).then(function (ct) { return cat(iv, new Uint8Array(ct)); });
    }
    function publish(blob, meta) {      /* chiffre, dépose le fichier, ajoute la ligne ; → { id, f, token } */
      var f = "p" + hex(rand(6)), id = newId(), token = hex(rand(16));
      return readBuf(blob).then(function (buf) { return sealWith(buf, "rep|" + f); }).then(function (bytes) {
        return fetch(CFG.url + "/storage/v1/object/reportage/" + f, { method: "POST", headers: head({ "Content-Type": "application/octet-stream" }), body: new Blob([bytes], { type: "application/octet-stream" }) }).then(ok);
      }).then(function () {
        return sealWith(enc.encode(JSON.stringify(meta)), "rep|meta|" + f);
      }).then(function (mb) {
        return subtle.digest("SHA-256", enc.encode(token)).then(function (h) {
          return fetch(CFG.url + "/rest/v1/reportage", { method: "POST", headers: head({ "Content-Type": "application/json", Prefer: "return=minimal" }),
            body: JSON.stringify({ id: id, f: f, meta: b64(mb), del_hash: hex(new Uint8Array(h)) }) }).then(ok);
        });
      }).then(function () { return { id: id, f: f, token: token }; });
    }
    function remove(id, token) {
      return fetch(CFG.url + "/rest/v1/rpc/retirer_photo", { method: "POST", headers: head({ "Content-Type": "application/json" }), body: JSON.stringify({ p_id: id, p_token: token }) }).then(ok).then(function (r) { return r.json(); });
    }
    var urls = {};
    function photoObj(f) {      /* photo déchiffrée → adresse locale (mise en mémoire) */
      if (urls[f]) return Promise.resolve(urls[f]);
      return fetch(photoUrl(f)).then(ok).then(function (r) { return r.arrayBuffer(); }).then(function (buf) {
        var u = new Uint8Array(buf);
        return subtle.decrypt({ name: "AES-GCM", iv: u.slice(0, 12), additionalData: enc.encode("rep|" + f), tagLength: 128 }, st.key, u.slice(12));
      }).then(function (pt) {
        var u8 = new Uint8Array(pt, 0, 4); urls[f] = URL.createObjectURL(new Blob([pt], { type: u8[0] === 0x89 ? "image/png" : (u8[0] === 0x52 ? "image/webp" : "image/jpeg") })); return urls[f];
      });
    }
    /* messages des invité·e·s aux voyageurs : un petit texte chiffré par message (même clé que le reportage) */
    var MMINE = "carnet.msg.mine", TOS = ["Tous", "Anne", "Arthur", "Daphne", "Flo"];
    function sendMsg(m) {
      var id = newId(), token = hex(rand(16));
      return sealWith(enc.encode(JSON.stringify(m)), "rep|msg|" + id).then(function (mb) {
        return subtle.digest("SHA-256", enc.encode(token)).then(function (h) {
          return fetch(CFG.url + "/rest/v1/messages", { method: "POST", headers: head({ "Content-Type": "application/json", Prefer: "return=minimal" }),
            body: JSON.stringify({ id: id, c: b64(mb), del_hash: hex(new Uint8Array(h)) }) }).then(ok);
        });
      }).then(function () { return { id: id, token: token }; });
    }
    function listMsgs() {
      return fetch(CFG.url + "/rest/v1/messages?select=id,c,created_at&order=created_at.asc&limit=500", { headers: head({}), cache: "no-store" }).then(ok).then(function (r) { return r.json(); }).then(function (rows) {
        return Promise.all(rows.map(function (row) {
          var u; try { u = unb64(row.c); } catch (e) { return null; }
          if (!/^[0-9a-f-]{36}$/.test(row.id || "") || u.length < 29) return null;
          return subtle.decrypt({ name: "AES-GCM", iv: u.slice(0, 12), additionalData: enc.encode("rep|msg|" + row.id), tagLength: 128 }, st.key, u.slice(12)).then(function (pt) {
            var m = JSON.parse(dec.decode(pt)), t = String(m.t || "").slice(0, 400);
            if (!t.trim()) return null;
            return { id: row.id, ts: row.created_at, w: String(m.w || "").slice(0, 30), to: TOS.indexOf(m.to) >= 0 ? m.to : "Tous", op: /^\d{4}-\d{2}-\d{2}$/.test(m.op || "") ? m.op : "", t: t };
          }).catch(function () { return null; });
        })).then(function (a) { return a.filter(Boolean); });
      });
    }
    function removeMsg(id, token) {
      return fetch(CFG.url + "/rest/v1/rpc/retirer_message", { method: "POST", headers: head({ "Content-Type": "application/json" }), body: JSON.stringify({ p_id: id, p_token: token }) }).then(ok).then(function (r) { return r.json(); });
    }
    function mineMsg() { try { var a = JSON.parse(LS.get(MMINE, "[]")); return Array.isArray(a) ? a : []; } catch (e) { return []; } }
    function setMineMsg(a) { LS.set(MMINE, JSON.stringify(a.slice(-100))); }
    function mine() { try { var a = JSON.parse(LS.get(MINE, "[]")); return Array.isArray(a) ? a : []; } catch (e) { return []; } }
    function setMine(a) { LS.set(MINE, JSON.stringify(a.slice(-100))); }
    return { CAN: CAN, CFG: CFG, norm: norm, unb64: unb64, derive: derive, canary: canary, verify: verify, unlockSaved: unlockSaved, remember: remember, forget: forget, list: list,
             photoUrl: photoUrl, photoObj: photoObj, publish: publish, remove: remove, mine: mine, setMine: setMine,
             sendMsg: sendMsg, listMsgs: listMsgs, removeMsg: removeMsg, mineMsg: mineMsg, setMineMsg: setMineMsg, key: function () { return st.key; }, enc: enc, dec: dec, subtle: subtle, savedCode: function () { return LS.get(KEY, ""); } };
  })();

  var PhotoInv = (function () {
    var v = $("#v-photoinv"); if (!v) return { enter: function () {} };
    var DAYS_ = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
    var MONTHS_ = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
    function dayLabel(iso) {      /* « 2026-12-19 » → « samedi 19 décembre 2026 » */
      var y = +iso.slice(0, 4), m = +iso.slice(5, 7), d = +iso.slice(8, 10), dt = new Date(y, m - 1, d);
      if (!y || !m || !d || isNaN(dt.getTime())) return "";
      return DAYS_[dt.getDay()] + " " + (d === 1 ? "1er" : d) + " " + MONTHS_[m - 1] + " " + y;
    }
    var CLOUD = !!(RepC.CFG && RepC.CAN);
    var file = $("#pi-file"), form = $("#pi-form"), cap = $("#pi-cap"), dateIn = $("#pi-date"), cv = $("#pi-cv"), st = $("#pi-st"), send = $("#pi-send");
    var pub = $("#pi-pub"), codeBox = $("#pi-code-box"), codeIn = $("#pi-code"), pst = $("#pi-pst"), pubBtn = $("#pi-publish"), mineBox = $("#pi-mine"), mineUl = $("#pi-mine-ul");
    var ctx = cv.getContext ? cv.getContext("2d") : null, img = null, imgUrl = "", name = "", fileName = "", busy = false, published = false;
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
    function changed() { clearTimeout(drawT); drawT = setTimeout(draw, 60); if (published) { published = false; setPubBtn(); pst.textContent = ""; } }
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
      imgUrl = ""; img = null; file.value = ""; form.hidden = true; st.textContent = ""; cap.value = ""; pst.textContent = ""; published = false; setPubBtn();
    }
    /* ── publication directe (mode Supabase) ── */
    function setPubBtn() {
      if (!pubBtn) return;
      pubBtn.disabled = busy || published;
      pubBtn.textContent = busy ? "Publication…" : (published ? "Publié ✓" : "Publier chez les invité·e·s");
    }
    function showCode(on) { if (codeBox) codeBox.hidden = !on; }
    function paintMine() {
      if (!mineBox) return;
      var a = RepC.mine().slice().reverse();
      mineBox.hidden = !(CLOUD && a.length);
      mineUl.textContent = "";
      a.forEach(function (m) {
        var li = document.createElement("li"), t = document.createElement("span"), b = document.createElement("button");
        t.textContent = nb(dayLabel(m.d).replace(/ \d{4}$/, "") + (m.c ? " · " + m.c : ""));
        b.type = "button"; b.className = "btn sm alt"; b.textContent = "Retirer"; b.setAttribute("aria-label", "Retirer ce polaroïd du reportage");
        var armed = 0;
        b.addEventListener("click", function () {
          if (!armed) { armed = 1; b.textContent = "Retirer ?"; setTimeout(function () { armed = 0; b.textContent = "Retirer"; }, 3500); return; }
          b.disabled = true; b.textContent = "…";
          RepC.remove(m.id, m.token).then(function () {
            RepC.setMine(RepC.mine().filter(function (x) { return x.id !== m.id; })); paintMine(); toast("Retiré du reportage");
          }).catch(function () { b.disabled = false; b.textContent = "Retirer"; toast("Pas de réseau : réessaie"); });
        });
        li.appendChild(t); li.appendChild(b); mineUl.appendChild(li);
      });
    }
    function doPublish() {
      if (busy || published) return;
      if (!RepC.key()) { showCode(true); pst.textContent = "Tape d’abord le code des invité·e·s."; try { codeIn.focus(); } catch (e) {} return; }
      busy = true; setPubBtn(); pst.textContent = "";
      toBlob(function (b) {
        if (!b) { busy = false; setPubBtn(); pst.textContent = "Impossible de fabriquer l’image sur ce téléphone."; return; }
        var meta = { d: dateIn.value || todayIso(), w: name, c: cap.value.replace(/\s+/g, " ").trim().slice(0, 70) };
        RepC.publish(b, meta).then(function (r) {
          var a = RepC.mine(); a.push({ id: r.id, f: r.f, token: r.token, d: meta.d, c: meta.c }); RepC.setMine(a);
          busy = false; published = true; setPubBtn(); paintMine();
          pst.textContent = "Publié : ton polaroïd est chez les invité·e·s. Tu peux le retirer en bas de la page.";
        }).catch(function () {
          busy = false; setPubBtn();
          pst.textContent = "La publication n’a pas marché (réseau ?). Rien n’est publié : réessaie.";
        });
      });
    }
    if (CLOUD && pub) {
      pub.hidden = false;
      pubBtn.addEventListener("click", doPublish);
      $("#pi-code-ok").addEventListener("click", function () {
        var c = codeIn.value; if (!RepC.norm(c)) { pst.textContent = "Tape le code reçu."; return; }
        pst.textContent = "Je vérifie…";
        RepC.verify(c).then(function (r) {
          if (r.none) { pst.textContent = "Le reportage n’est pas encore prêt."; return; }
          RepC.remember(c); codeIn.value = ""; showCode(false); pst.textContent = "Code validé. Tu peux publier.";
        }).catch(function (e) { pst.textContent = e && e.name === "OperationError" ? "Ce n’est pas le bon code." : "Pas de réseau : réessaie."; });
      });
    }
    file.addEventListener("change", function () {
      var f = file.files && file.files[0]; if (!f) return;
      if (imgUrl) { try { URL.revokeObjectURL(imgUrl); } catch (e) {} }
      st.textContent = "Je prépare ton polaroïd…"; fileName = f.name; published = false; setPubBtn(); pst.textContent = "";
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
    cap.addEventListener("input", changed);
    dateIn.addEventListener("input", changed); dateIn.addEventListener("change", changed);
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
        if (CLOUD) {
          send.textContent = "";
          RepC.unlockSaved().then(function (okk) { showCode(!okk); }).catch(function () { showCode(!RepC.key()); });
          paintMine();
        } else {
          send.textContent = name === "Anne"
            ? "Quand il te plaît, garde-le : tu le transmets au carnet avec les autres, et il est publié dans le reportage des invité·e·s."
            : "Envoie-le à Anne (message, AirDrop…) : elle le fera publier dans le reportage des invité·e·s.";
        }
        send.textContent = nb(send.textContent);
        if (!form.hidden) changed();
      }
    };
  })();

  var Rep = (function () {
    var v = $("#v-reportage"); if (!v) return { enter: function () {} };
    var lock = $("#rp-lock"), form = $("#rp-form"), inp = $("#rp-code"), err = $("#rp-err"), msg = $("#rp-msg"), feed = $("#rp-feed"), foot = $("#rp-foot"), big = $("#rp-big");
    var CAN = RepC.CAN, CLOUD = !!RepC.CFG, subtle = RepC.subtle, enc = RepC.enc, dec = RepC.dec, unb64 = RepC.unb64, norm = RepC.norm;
    var S = { man: null, key: null, salt: "", urls: {}, busy: false, obs: null, sig: "", poll: 0 };
    var DAYS_ = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];
    var MONTHS_ = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
    function dayLabel(iso) {
      var y = +iso.slice(0, 4), m = +iso.slice(5, 7), d = +iso.slice(8, 10), dt = new Date(y, m - 1, d);
      if (!y || !m || !d || isNaN(dt.getTime())) return iso;
      var s = DAYS_[dt.getDay()] + " " + (d === 1 ? "1er" : d) + " " + MONTHS_[m - 1];
      return s.charAt(0).toUpperCase() + s.slice(1);
    }
    var KEY = "carnet.rep.code";
    function say(t) { msg.textContent = t || ""; }
    function showLock(on) { lock.hidden = !on; }
    function clearFeed() { feed.textContent = ""; foot.hidden = true; S.sig = ""; if (S.obs) { try { S.obs.disconnect(); } catch (e) {} S.obs = null; } }
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
      var url = CLOUD ? RepC.photoUrl(f) : "reportage/" + f + ".bin";
      return fetch(url).then(function (r) { if (!r.ok) throw new Error("http"); return r.arrayBuffer(); }).then(function (buf) {
        var u = new Uint8Array(buf);
        return subtle.decrypt({ name: "AES-GCM", iv: u.slice(0, 12), additionalData: enc.encode("rep|" + f), tagLength: 128 }, S.key, u.slice(12));
      }).then(function (pt) {
        var u8 = new Uint8Array(pt, 0, 4), blob = new Blob([pt], { type: sniff(u8) }), objUrl = URL.createObjectURL(blob);
        S.urls[f] = objUrl; im.src = objUrl; fig.classList.remove("wait"); fig.classList.add("on");
      }).catch(function () { fig.classList.remove("wait"); fig.title = "Cette photo n’a pas pu être chargée."; });
    }
    function render(list) {
      var sig = list.map(function (x) { return x.f; }).join(",");
      if (sig === S.sig && feed.firstChild) return;      /* rien de nouveau : on ne redessine pas */
      clearFeed(); S.sig = sig;
      LS.set("carnet.rep.seen", String(list.length)); Dots.clearRep();
      if (!list.length) { say("Le reportage commence : les premières photos arrivent pendant le voyage. Reviens bientôt !"); return; }
      say(nb(list.length + (list.length > 1 ? " photos" : " photo") + " · des plus récentes aux plus anciennes"));
      var items = list.map(function (it, i) { return { f: it.f, d: it.d, w: it.w, c: it.c || "", i: it.i === undefined ? i : it.i }; });
      items.sort(function (a, b) { return a.d < b.d ? 1 : a.d > b.d ? -1 : b.i - a.i; });
      var lastD = "", figs = [];
      items.forEach(function (it) {
        if (it.d !== lastD) { var h = document.createElement("h2"); h.className = "rp-day"; h.textContent = dayLabel(it.d); feed.appendChild(h); lastD = it.d; }
        var fig = document.createElement("figure"), im = document.createElement("img");
        fig.className = "rp-ph wait"; fig.setAttribute("data-f", it.f); fig.setAttribute("role", "button"); fig.setAttribute("tabindex", "0");
        fig.setAttribute("aria-label", "Agrandir la photo de " + it.w + ", " + dayLabel(it.d));
        im.alt = "Polaroïd de " + it.w + ", " + dayLabel(it.d) + (it.c ? " : " + it.c : ""); im.decoding = "async";
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
    function wrongOrNet(e) {
      if (e && e.name === "OperationError") return "Ce n’est pas le bon code. Vérifie-le et réessaie.";
      return "Impossible de joindre le reportage (réseau ?). Réessaie dans un instant.";
    }
    /* ── mode Supabase ── */
    function refreshCloud() {
      S.key = RepC.key();
      return RepC.list().then(function (list) { showLock(false); err.textContent = ""; render(list); });
    }
    function startCloud() {
      if (S.busy) return; S.busy = true;
      if (!feed.firstChild) say("Je regarde s’il y a des photos…");
      RepC.canary().then(function (c) {
        if (!c) { clearFeed(); showLock(false); say("Le reportage n’a pas encore commencé : les premières photos arrivent pendant le voyage. Reviens bientôt !"); return; }
        return RepC.unlockSaved().then(function (okk) {
          if (!okk) { clearFeed(); showLock(true); say(""); return; }
          return refreshCloud();
        });
      }).catch(function () {
        if (!feed.firstChild) { clearFeed(); showLock(false); say("Impossible de charger le reportage pour le moment. Vérifie ta connexion et reviens."); }
      }).then(function () { S.busy = false; });
    }
    function submitCloud(code) {
      err.textContent = "Je vérifie…";
      return RepC.verify(code).then(function (r) {
        if (r.none) { err.textContent = ""; say("Le reportage n’a pas encore commencé."); return; }
        RepC.remember(code); inp.value = ""; return refreshCloud();
      }).catch(function (e) { err.textContent = wrongOrNet(e); });
    }
    /* ── mode fichiers ── */
    function tryCode(code, silent) {
      if (!S.man) return Promise.resolve(false);
      var man = S.man;
      return RepC.derive(code, man.s, man.it || 150000).then(function (key) {
        return openMan(man, key).then(function (list) { S.key = key; S.salt = man.s; LS.set(KEY, norm(code)); showLock(false); err.textContent = ""; render(list); return true; });
      }).catch(function () {
        if (!silent) err.textContent = "Ce n’est pas le bon code. Vérifie-le et réessaie.";
        return false;
      });
    }
    function start() {
      if (CLOUD) return startCloud();
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
      if (!CAN) { err.textContent = "Ce téléphone ne sait pas ouvrir le reportage."; return; }
      if (CLOUD) { submitCloud(c); return; }
      err.textContent = "Je vérifie…";
      tryCode(c, false).then(function (ok) { if (ok) inp.value = ""; });
    });
    $("#rp-forget").addEventListener("click", function () {
      RepC.forget(); LS.del(KEY); S.key = null; S.salt = "";
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
    /* mode Supabase : les nouvelles photos apparaissent toutes seules (toutes les 40 s tant que la page est ouverte et visible) */
    if (CLOUD) setInterval(function () { if (!v.hidden && !document.hidden && lock.hidden && RepC.key() && !S.busy) { S.busy = true; refreshCloud().catch(function () {}).then(function () { S.busy = false; }); } }, 40000);
    return { enter: function () { big.hidden = true; start(); } };
  })();

  /* ───────────── dates : « aujourd'hui » à Bangkok (les voyageurs y sont ; pour les invité·e·s, c'est le jour du voyage) ───────────── */
  function bkkDay() {
    try {
      var o = {}; new Intl.DateTimeFormat("fr-FR", { timeZone: "Asia/Bangkok", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date()).forEach(function (p) { o[p.type] = p.value; });
      return o.year + "-" + o.month + "-" + o.day;
    } catch (e) { var d = new Date(); return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); }
  }
  function me() { return LS.get("carnet.who", ""); }
  function isTrav() { return ["Arthur", "Daphne", "Flo", "Anne"].indexOf(me()) >= 0; }
  function isGuest() { return me() === "Invité"; }
  function seenMsgs() { try { var a = JSON.parse(LS.get("carnet.msg.seen", "[]")); return Array.isArray(a) ? a : []; } catch (e) { return []; } }
  function visibleMsgs(all) {      /* les mots que le voyageur choisi peut voir : pour lui ou pour tous */
    var w = me(); return all.filter(function (m) { return m.to === "Tous" || m.to === w; });
  }

  /* ───────────── messages : les invité·e·s écrivent, les voyageurs lisent ───────────── */
  var Msg = (function () {
    var v = $("#v-messages"); if (!v) return { enter: function () {} };
    var CLOUD = !!(RepC.CFG && RepC.CAN);
    var lock = $("#ms-lock"), form = $("#ms-form"), code = $("#ms-code"), err = $("#ms-err"), who = $("#ms-who"), how = $("#mg-how"), fsec = $("#mg-form"), msec = $("#mg-mine"), tbox = $("#mt-box"), busy = false;
    var tIn = $("#mg-t"), cnt = $("#mg-n"), st = $("#mg-st");
    var MONTHS_ = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
    function dl(iso) { var m = +iso.slice(5, 7), d = +iso.slice(8, 10); return (d === 1 ? "1er" : d) + " " + MONTHS_[m - 1]; }
    function show(a) { how.hidden = !a.how; lock.hidden = !a.lock; fsec.hidden = !a.form; msec.hidden = !a.mine; tbox.hidden = !a.box; who.hidden = !a.who; }
    function wrongOrNet(e) { return e && e.name === "OperationError" ? "Ce n’est pas le bon code. Vérifie-le et réessaie." : "Impossible de joindre le serveur (réseau ?). Réessaie dans un instant."; }
    /* ── invité·e : écrire ── */
    function paintMine() {
      var ul = $("#mg-mine-ul"), a = RepC.mineMsg().slice().reverse(); ul.textContent = ""; msec.hidden = !a.length || !isGuest();
      a.forEach(function (m) {
        var li = document.createElement("li"), p = document.createElement("p"), b = document.createElement("button"), armed = 0;
        p.textContent = "Pour " + (m.to === "Tous" ? "tous les quatre" : m.to) + " · " + (m.op ? "à ouvrir le " + dl(m.op) : "tout de suite") + " : « " + m.t + " »";
        b.type = "button"; b.className = "btn sm alt"; b.textContent = "Retirer";
        b.addEventListener("click", function () {
          if (!armed) { armed = 1; b.textContent = "Retirer ?"; setTimeout(function () { armed = 0; b.textContent = "Retirer"; }, 3500); return; }
          b.disabled = true;
          RepC.removeMsg(m.id, m.token).then(function () { RepC.setMineMsg(RepC.mineMsg().filter(function (x) { return x.id !== m.id; })); paintMine(); toast("Mot retiré"); })
            .catch(function () { b.disabled = false; b.textContent = "Retirer"; toast("Pas de réseau : réessaie"); });
        });
        li.appendChild(p); li.appendChild(b); ul.appendChild(li);
      });
    }
    function showGuest() {
      show({ how: 1, form: 1, mine: 0 }); $("#mg-w").value = LS.get("carnet.msg.name", ""); st.textContent = ""; paintMine(); cnt.textContent = tIn.value.length + " / 400";
    }
    function send() {
      var w = $("#mg-w").value.trim(), t = tIn.value.trim(), to = $("#mg-to").value, op = $("#mg-op").value;
      if (!w) { st.textContent = "Écris ton prénom, pour que les voyageurs sachent de qui vient le mot."; $("#mg-w").focus(); return; }
      if (!t) { st.textContent = "Écris ton message."; tIn.focus(); return; }
      var btn = $("#mg-send"); btn.disabled = true; st.textContent = "J’envoie…";
      RepC.sendMsg({ w: w, to: to, op: op, t: t, d: bkkDay() }).then(function (r) {
        LS.set("carnet.msg.name", w);
        var a = RepC.mineMsg(); a.push({ id: r.id, token: r.token, to: to, op: op, t: t.length > 60 ? t.slice(0, 60) + "…" : t }); RepC.setMineMsg(a);
        tIn.value = ""; cnt.textContent = "0 / 400"; paintMine();
        st.textContent = "C’est parti ! Ton mot est arrivé chez les voyageurs" + (op ? " : il s’ouvrira le " + dl(op) + "." : ".");
        toast("Mot envoyé");
      }).catch(function () { st.textContent = "Le mot n’est pas parti (réseau ?). Ton texte est toujours là : réessaie."; }).then(function () { btn.disabled = false; });
    }
    /* ── voyageur : lire ── */
    function sealed(op) {
      var d = document.createElement("div"); d.className = "mt-seal";
      d.innerHTML = '<span aria-hidden="true">✉</span>'; var p = document.createElement("p"); p.textContent = "Un mot à ouvrir le " + dl(op) + "."; d.appendChild(p); return d;
    }
    function showTrav(all) {
      show({ box: 1 });
      var mine = visibleMsgs(all), today = bkkDay(), list = $("#mt-list"), seen = seenMsgs(), keep = seen.slice();
      list.textContent = "";
      var others = all.length - mine.length;
      var open = mine.filter(function (m) { return !m.op || m.op <= today; }), wait = mine.filter(function (m) { return m.op && m.op > today; });
      $("#mt-msg").textContent = !all.length ? "Pas encore de mot. Les invité·e·s peuvent écrire depuis leur téléphone : reviens voir !" :
        (open.length + wait.length) ? (open.length + (open.length > 1 ? " mots" : " mot") + " pour toi" + (wait.length ? ", " + wait.length + " à ouvrir plus tard" : "") + (others ? " · " + others + (others > 1 ? " mots sont destinés" : " mot est destiné") + " à un autre voyageur" : "")) :
        "Aucun mot pour toi pour l’instant" + (others ? " (" + others + (others > 1 ? " sont destinés" : " est destiné") + " à un autre voyageur)" : "") + ".";
      open.slice().reverse().forEach(function (m) {
        var c = document.createElement("article"), h = document.createElement("h3"), p = document.createElement("p"), s = document.createElement("small");
        c.className = "mt-card" + (seen.indexOf(m.id) < 0 ? " new" : "");
        h.textContent = "De la part de " + m.w; p.textContent = m.t;
        s.textContent = (m.to === "Tous" ? "Pour vous quatre" : "Pour toi") + (m.op ? " · ouvert le " + dl(m.op) : "");
        c.appendChild(h); c.appendChild(p); c.appendChild(s); list.appendChild(c);
        if (keep.indexOf(m.id) < 0) keep.push(m.id);
      });
      wait.forEach(function (m) { list.appendChild(sealed(m.op)); });
      LS.set("carnet.msg.seen", JSON.stringify(keep.slice(-300)));
      Dots.paintMsg(0);
    }
    function loadTrav() {
      RepC.listMsgs().then(showTrav).catch(function () { show({ box: 1 }); $("#mt-msg").textContent = "Impossible de charger les mots pour le moment (réseau ?). Réessaie dans un instant."; });
    }
    function start() {
      if (busy) return;
      show({ who: !(isGuest() || isTrav()) });
      if (!(isGuest() || isTrav())) return;
      if (!CLOUD) { show({}); who.hidden = false; who.textContent = "Les messages ne sont pas disponibles pour le moment."; return; }
      busy = true;
      RepC.canary().then(function (c) {
        if (!c) { show({}); who.hidden = false; who.textContent = "Les messages ne sont pas encore ouverts. Reviens bientôt !"; return; }
        return RepC.unlockSaved().then(function (ok) {
          if (!ok) { show({ how: isGuest(), lock: 1 }); err.textContent = ""; return; }
          if (isGuest()) showGuest(); else loadTrav();
        });
      }).catch(function () { show({}); who.hidden = false; who.textContent = "Impossible de joindre le serveur (réseau ?). Réessaie dans un instant."; }).then(function () { busy = false; });
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault(); err.textContent = "";
      var c = code.value; if (!RepC.norm(c)) { err.textContent = "Tape le code reçu."; return; }
      err.textContent = "Je vérifie…";
      RepC.verify(c).then(function (r) {
        if (r.none) { err.textContent = "Les messages ne sont pas encore ouverts."; return; }
        RepC.remember(c); code.value = ""; err.textContent = ""; if (isGuest()) showGuest(); else loadTrav();
      }).catch(function (e2) { err.textContent = wrongOrNet(e2); });
    });
    tIn.addEventListener("input", function () { cnt.textContent = tIn.value.length + " / 400"; });
    $("#mg-send").addEventListener("click", send);
    $("#mt-forget").addEventListener("click", function () { RepC.forget(); show({ lock: 1 }); toast("Code oublié sur ce téléphone"); });
    return { enter: start };
  })();

  /* ───────────── points de nouveautés sur l'accueil : nouvelles photos (invité·e·s) et nouveaux mots (voyageurs) ───────────── */
  var Dots = (function () {
    var rep = $("#dot-rep"), msg = $("#dot-msg"), busy = false, last = 0;
    function put(el, n) { if (!el) return; el.hidden = !(n > 0); el.textContent = n > 99 ? "99+" : String(n); el.setAttribute("aria-label", n + (n > 1 ? " nouveautés" : " nouveauté")); }
    function paintMsg(n) { put(msg, n); }
    function refresh(force) {
      if (!(RepC.CFG && RepC.CAN) || busy) return;
      var now = Date.now(); if (!force && now - last < 30000) return;
      var g = isGuest(), t = isTrav(); if (!g && !t) { put(rep, 0); put(msg, 0); return; }
      if (!LS.get("carnet.rep.code", "")) return;      /* sans le code gardé sur ce téléphone, on ne peut rien lire */
      busy = true; last = now;
      RepC.unlockSaved().then(function (ok) {
        if (!ok) return;
        if (g) {
          return RepC.list().then(function (l) { var seen = parseInt(LS.get("carnet.rep.seen", "0"), 10) || 0; put(rep, Math.max(0, l.length - seen)); });
        }
        return RepC.listMsgs().then(function (all) {
          var seen = seenMsgs(), today = bkkDay();
          put(msg, visibleMsgs(all).filter(function (m) { return (!m.op || m.op <= today) && seen.indexOf(m.id) < 0; }).length);
        });
      }).catch(function () {}).then(function () { busy = false; });
    }
    return { refresh: refresh, paintMsg: paintMsg, clearRep: function () { put(rep, 0); } };
  })();

  /* ───────────── le voyage en un coup d'œil : jour après jour ───────────── */
  var Recap = (function () {
    var v = $("#v-recap"); if (!v) return { enter: function () {} };
    var rows = $$(".rc-day", v), msg = $("#rc-msg"), stats = $("#rc-stats"), loaded = 0;
    function chip(t) { var s = document.createElement("span"); s.textContent = t; return s; }
    function stat(n, l) { var d = document.createElement("p"), b = document.createElement("b"), s = document.createElement("span"); b.textContent = n; s.textContent = l; d.appendChild(b); d.appendChild(s); return d; }
    function thumbs(list) {
      rows.forEach(function (r) {
        var id = r.getAttribute("data-id"), box = $(".rc-th", r), mine = list.filter(function (x) { return x.d === id; });
        box.textContent = ""; box.hidden = !mine.length;
        mine.slice(0, 4).forEach(function (it) {
          var a = document.createElement("a"), im = document.createElement("img"); a.href = "#/reportage"; a.setAttribute("aria-label", "Voir le polaroïd de " + it.w);
          im.alt = ""; im.width = 60; im.height = 84; a.appendChild(im); box.appendChild(a);
          RepC.photoObj(it.f).then(function (u) { im.src = u; }).catch(function () { a.hidden = true; });
        });
        if (mine.length > 4) { var more = document.createElement("a"); more.href = "#/reportage"; more.className = "rc-more"; more.textContent = "+" + (mine.length - 4); box.appendChild(more); }
      });
    }
    function enter() {
      var today = bkkDay(), ids = rows.map(function (r) { return r.getAttribute("data-id"); }), n = ids.filter(function (i) { return i <= today; }).length;
      var started = n > 0, trav = isTrav();
      $("#rc-fill").style.width = (100 * n / ids.length) + "%";
      $("#rc-sub").textContent = !started ? "Le voyage commence le 18 décembre." : (n >= ids.length ? "Le voyage est terminé : 17 jours, de Paris à Bangkok et retour." : "Jour " + n + " sur " + ids.length);
      msg.textContent = started ? "" : "Les jours s’ajoutent ici au fil du voyage.";
      var stamps = {}, st = jget("carnet.stamps", null) || {}; (st.d instanceof Array ? st.d : []).forEach(function (k) { stamps[k] = 1; });
      rows.forEach(function (r) {
        var id = r.getAttribute("data-id"); r.hidden = id > today;
        var c = $(".rc-chips", r); c.textContent = "";
        if (trav && id <= today) { if (stamps[id]) c.appendChild(chip("Tampon posé")); if (hasPhoto && hasPhoto[id]) c.appendChild(chip("Photo du jour")); }
      });
      stats.textContent = ""; stats.appendChild(stat(Math.min(n, ids.length) + "/" + ids.length, "jours"));
      var cities = {}; rows.forEach(function (r) { if (!r.hidden) { var cn = $(".rc-hd span", r).textContent; if (cn.indexOf("→") < 0) cities[cn] = 1; } });
      stats.appendChild(stat(Object.keys(cities).length, Object.keys(cities).length > 1 ? "étapes" : "étape"));
      if (trav) stats.appendChild(stat(Object.keys(stamps).length + (st.b instanceof Array ? st.b.length : 0), "tampons"));
      if (!(RepC.CFG && RepC.CAN) || !(isGuest() || trav)) return;
      if (!LS.get("carnet.rep.code", "")) {
        if (started) msg.textContent = isGuest() ? "Pour voir les polaroïds ici, ouvre d’abord le Reportage photo avec ton code." : "Pour voir les polaroïds ici, tape le code dans « Photo pour les invités ».";
        return;
      }
      RepC.unlockSaved().then(function (ok) {
        if (!ok) return;
        return RepC.list().then(function (l) { thumbs(l); stats.appendChild(stat(l.length, l.length > 1 ? "polaroïds" : "polaroïd")); });
      }).catch(function () {});
    }
    return { enter: enter };
  })();
  setInterval(function () { if (!document.hidden && curName === "home") Dots.refresh(false); }, 60000);
