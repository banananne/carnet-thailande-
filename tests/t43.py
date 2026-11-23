# -*- coding: utf-8 -*-
"""Retouches du 22 nov. (soir) : masque parlé, carte du reportage en haut, site allégé pour les invité·e·s, BO du jour, enveloppe de Noël, tampon retirable, glissement entre les jours, icône taxi."""
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8782/carnet-thailande-/"
ROOT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/"
n_ok = n_ko = 0
def check(name, c, info=""):
    global n_ok, n_ko
    if c: n_ok += 1
    else: n_ko += 1; print("  ✗", name, info)
errs = []
SPEECH = """
window.__spoken = [];
window.SpeechSynthesisUtterance = function (t) { this.text = t; };
Object.defineProperty(window, "speechSynthesis", { configurable: true, value: { speaking: false, pending: false, speak: function (u) { window.__spoken.push([u.text, u.lang]); if (u.onstart) u.onstart(); setTimeout(function () { if (u.onend) u.onend(); }, 10); },
  cancel: function () {}, resume: function () {}, getVoices: function () { return [{ lang: "th-TH", name: "Kanya" }]; }, addEventListener: function () {} } });
"""
def newpg(b, who, when=None, vw=390, pol=None, speech=False):
    ctx = b.new_context(viewport={"width": vw, "height": 844}, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block", timezone_id="Europe/Paris")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    if speech: pg.add_init_script(SPEECH)
    if when: pg.clock.set_fixed_time(when)
    pg.goto(BASE, wait_until="load")
    pg.evaluate("(a)=>{localStorage.setItem('carnet.who',a[0]); if(a[1]) localStorage.setItem('carnet.pol',a[1]);}", [who, pol])
    pg.reload(wait_until="load"); pg.wait_for_timeout(500)
    return ctx, pg
def swipe(pg, sel, x0, x1, y0=400, y1=410, ms=0):
    pg.evaluate("""([sel, x0, x1, y0, y1]) => {
      const el = document.querySelector(sel);
      const mk = (x, y) => new Touch({ identifier: 1, target: el, clientX: x, clientY: y });
      el.dispatchEvent(new TouchEvent('touchstart', { bubbles: true, cancelable: true, touches: [mk(x0, y0)], targetTouches: [mk(x0, y0)], changedTouches: [mk(x0, y0)] }));
      el.dispatchEvent(new TouchEvent('touchend', { bubbles: true, cancelable: true, touches: [], targetTouches: [], changedTouches: [mk(x1, y1)] }));
    }""", [sel, x0, x1, y0, y1])
    pg.wait_for_timeout(350)
with sync_playwright() as p:
    b = p.chromium.launch()
    # ───── A. le masque se prononce ─────
    for pol, exp in (("kha", "สวัสดีค่ะ"), ("khrap", "สวัสดีครับ"), (None, "สวัสดี")):
        ctx, pg = newpg(b, "Anne", pol=pol, speech=True)
        pg.click("#mask"); pg.wait_for_timeout(400)
        sp = pg.evaluate("window.__spoken")
        check("A %s : le masque prononce « %s » en thaï" % (pol, exp), len(sp) == 1 and sp[0][0] == exp and sp[0][1] == "th-TH", sp)
        check("A %s : le message écrit est toujours là" % pol, "Sawasdee" in pg.inner_text("#toast"), pg.inner_text("#toast"))
        ctx.close()
    # ───── B. la carte du reportage est en haut ─────
    ctx, pg = newpg(b, "Daphne")
    r = pg.evaluate("""() => { const c = document.querySelector('.phc-trav').getBoundingClientRect(), t = document.querySelector('#h-trip').getBoundingClientRect(), hs = document.querySelector('#hsd').getBoundingClientRect(); return {top: c.top + scrollY, hsd: hs.top + scrollY, bg: getComputedStyle(document.querySelector('.phc-trav')).backgroundColor, trip: t.top + scrollY, h: c.height, vis: getComputedStyle(document.querySelector('.phc-trav')).display, g: getComputedStyle(document.querySelector('.phc-guest')).display}; }""")
    check("B1 voyageur : carte « Photo pour les invités » visible, avant « Le voyage »", r["vis"] != "none" and r["g"] == "none" and r["top"] < r["trip"] and r["top"] > r["hsd"] and r["bg"] == "rgb(165, 28, 54)", r)
    check("B2 elle est assez grande", r["h"] >= 70, r)
    pg.screenshot(path=ROOT + "ph/n_trav_home.png")
    pg.click(".phc-trav"); pg.wait_for_timeout(500)
    check("B3 elle ouvre la page de publication", pg.evaluate("location.hash") == "#/photo-invites")
    ctx.close()
    # ───── C. invité·e + enveloppe de Noël ─────
    ctx, pg = newpg(b, "Invité", when="2026-12-24T22:30:00Z")      # 23 h 30 à Paris, le 24
    check("C1 24 décembre : pas d'enveloppe", not pg.is_visible("#xmas"))
    check("C2 invité·e : la carte « Reportage photo » est visible en haut", pg.is_visible(".phc-guest") and not pg.is_visible(".phc-trav"))
    ctx.close()
    ctx, pg = newpg(b, "Invité", when="2026-12-24T23:30:00Z")      # 0 h 30 à Paris, le 25
    check("C3 25 décembre (Paris) : l'enveloppe est là, fermée", pg.is_visible("#xmas") and pg.is_visible("#xm-env") and not pg.is_visible("#xm-card"))
    pg.screenshot(path=ROOT + "ph/n_xmas_closed.png")
    pg.click("#xm-env"); pg.wait_for_timeout(900)
    check("C4 on la touche : le mot s'affiche (tout est très coloré ; P.-S. de Moomoo et d'Aftonsparv)", pg.is_visible("#xm-card") and "joyeux noël depuis la thaïlande" in pg.inner_text("#xm-card").lower() and "bisous" in pg.inner_text("#xm-card") and "très coloré" in pg.inner_text("#xm-card") and "guirlande" not in pg.inner_text("#xm-card") and "Moomoo et d’Aftonsparv" in pg.inner_text("#xm-card"), pg.inner_text("#xm-card")[:80])
    check("C5 aria-expanded et mémoire", pg.get_attribute("#xm-env", "aria-expanded") == "true" and pg.evaluate("localStorage.getItem('carnet.xmas')") == "1")
    pg.screenshot(path=ROOT + "ph/n_xmas_open.png")
    ov = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("C6 pas de débordement", ov <= 0, ov)
    pg.reload(wait_until="load"); pg.wait_for_timeout(600)
    check("C7 après rechargement : toujours ouverte", pg.is_visible("#xm-card") and not pg.is_visible("#xm-hint"))
    ctx.close()
    ctx, pg = newpg(b, "Anne", when="2026-12-25T10:00:00Z")
    check("C8 un voyageur ne voit pas l'enveloppe", not pg.is_visible("#xmas"))
    ctx.close()
    ctx, pg = newpg(b, "Invité", when="2026-12-25T10:00:00Z", vw=320)
    pg.click("#xm-env"); pg.wait_for_timeout(700)
    ov = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("C9 320 px : pas de débordement, mot lisible", ov <= 0 and pg.is_visible("#xm-card"), ov)
    pg.screenshot(path=ROOT + "ph/n_xmas_320.png")
    ctx.close()
    # ───── D. site allégé pour les invité·e·s ─────
    ctx, pg = newpg(b, "Invité")
    pg.evaluate("location.hash = '#/jeux'"); pg.wait_for_timeout(500)
    gone = {h: not pg.locator('#v-jeux a[href="%s"]' % h).first.is_visible() for h in ("#/bingo", "#/gourmand", "#/prix", "#/blind-test")}
    check("D1 invité·e : bingo, carnet gourmand, prix du voyage, blind test absents de Jeux", all(gone.values()), gone)
    stay = {h: pg.locator('#v-jeux a[href="%s"]' % h).first.is_visible() for h in ("#/mascottes", "#/mot-du-jour", "#/passeport", "#/quiz")}
    check("D2 le reste de Jeux reste", all(stay.values()), stay)
    for h in ("bingo", "gourmand", "prix", "blind-test"):
        pg.evaluate("location.hash = '#/%s'" % h); pg.wait_for_timeout(400)
        check("D3 #/%s ramène aux jeux" % h, pg.evaluate("location.hash") == "#/jeux" and pg.is_visible("#v-jeux"), pg.evaluate("location.hash"))
    pg.evaluate("location.hash = '#/jours/2026-12-20'"); pg.wait_for_timeout(500)
    check("D4 invité·e : pas de « Photo du jour » dans les jours", not pg.locator("#d-2026-12-20 .snap").is_visible())
    check("D5 le défi du jour est caché, la BO et le tampon restent", not pg.locator("#d-2026-12-20 .dfl").is_visible() and pg.locator("#d-2026-12-20 .song").is_visible() and pg.locator("#d-2026-12-20 .dstamp").is_visible())
    pg.evaluate("location.hash = '#/jeux'"); pg.wait_for_timeout(400)
    check("D5b pas de « Défi du jour » dans Jeux", not pg.locator('#v-jeux a[href="#/defi"]').first.is_visible())
    pg.evaluate("location.hash = '#/defi'"); pg.wait_for_timeout(400)
    check("D5c #/defi ramène aux jeux", pg.evaluate("location.hash") == "#/jeux")
    ctx.close()
    ctx, pg = newpg(b, "Flo")
    pg.evaluate("location.hash = '#/jeux'"); pg.wait_for_timeout(500)
    ok4 = all(pg.locator('#v-jeux a[href="%s"]' % h).first.is_visible() for h in ("#/bingo", "#/gourmand", "#/prix", "#/blind-test"))
    check("D6 voyageur : tout est là", ok4)
    pg.evaluate("location.hash = '#/jours/2026-12-20'"); pg.wait_for_timeout(500)
    check("D7 voyageur : la photo du jour et le défi sont là", pg.locator("#d-2026-12-20 .snap").is_visible() and pg.locator("#d-2026-12-20 .dfl").is_visible())
    # ───── E. la BO du jour ─────
    sg = pg.evaluate("""() => { const s = document.querySelector('#d-2026-12-20 .song'), i = s.querySelector('img').getBoundingClientRect(); return {t: s.innerText.replace(/\\s+/g,' '), w: i.width, kick: s.querySelector('small').innerText.trim()}; }""")
    check("E1 « La BO du jour » écrit", "la bo du jour" in sg["kick"].lower(), sg)
    check("E2 pochette plus grande (≥ 48 px)", sg["w"] >= 48, sg)
    pg.locator("#d-2026-12-20 .song").screenshot(path=ROOT + "ph/n_song.png")
    pg.click("#d-2026-12-20 .song-cv"); pg.wait_for_timeout(300)
    hr = pg.evaluate("[...document.querySelectorAll('.mus a')].map(a => a.href)")
    check("E3 toucher la pochette ouvre le choix Spotify / Apple Musique / YouTube", pg.is_visible(".mus") and len(hr) == 3 and "spotify" in hr[0] and "music.apple.com" in hr[1] and "youtube.com" in hr[2], hr)
    check("E4 la recherche porte sur le titre et l'artiste du jour", "Someday" in __import__("urllib.parse").parse.unquote(hr[0]) and "Sways" in __import__("urllib.parse").parse.unquote(hr[2]), hr[0])
    pg.screenshot(path=ROOT + "ph/n_music.png")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    check("E5 Échap ferme", not pg.is_visible(".mus"))
    # ───── F. tampon retirable ─────
    pg.evaluate("localStorage.removeItem('carnet.stamps')"); pg.reload(wait_until="load"); pg.wait_for_timeout(500)
    pg.evaluate("location.hash = '#/jours/2026-12-20'"); pg.wait_for_timeout(500)
    pg.locator("#d-2026-12-20 .dstamp").scroll_into_view_if_needed()
    pg.click("#d-2026-12-20 [data-stamp-day]"); pg.wait_for_timeout(700)
    check("F1 tamponner : le tampon s'affiche, le bouton disparaît", pg.locator("#d-2026-12-20 .dstamp-svg svg").count() == 1 and not pg.locator("#d-2026-12-20 [data-stamp-day]").is_visible())
    check("F2 la consigne « Touche le tampon pour l'enlever » apparaît", pg.locator("#d-2026-12-20 .dstamp-hint").is_visible())
    pg.screenshot(path=ROOT + "ph/n_stamp_on.png")
    pg.click("#d-2026-12-20 .dstamp-svg"); pg.wait_for_timeout(500)
    check("F3 retoucher le tampon l'enlève ; le bouton revient", pg.locator("#d-2026-12-20 .dstamp-svg svg").count() == 0 and pg.locator("#d-2026-12-20 [data-stamp-day]").is_visible())
    check("F4 message « Tampon retiré »", "retiré" in pg.inner_text("#toast"), pg.inner_text("#toast"))
    check("F5 mémoire du téléphone mise à jour", "2026-12-20" not in (pg.evaluate("localStorage.getItem('carnet.stamps')") or ""))
    pg.click("#d-2026-12-20 [data-stamp-day]"); pg.wait_for_timeout(500)
    check("F6 on peut retamponner", pg.locator("#d-2026-12-20 .dstamp-svg svg").count() == 1)
    pg.evaluate("location.hash = '#/passeport'"); pg.wait_for_timeout(500)
    check("F7 le passeport compte 1 tampon", pg.inner_text("#pp-count").strip() == "1", pg.inner_text("#pp-count"))
    pg.evaluate("location.hash = '#/jours/2026-12-20'"); pg.wait_for_timeout(400)
    pg.locator("#d-2026-12-20 .dstamp-svg").focus(); pg.keyboard.press("Enter"); pg.wait_for_timeout(400)
    check("F8 au clavier (Entrée) aussi", pg.locator("#d-2026-12-20 .dstamp-svg svg").count() == 0)
    pg.evaluate("location.hash = '#/passeport'"); pg.wait_for_timeout(500)
    check("F9 le passeport est revenu à 0", pg.inner_text("#pp-count").strip() == "0", pg.inner_text("#pp-count"))
    # ───── G. glisser d'un jour à l'autre ─────
    pg.evaluate("location.hash = '#/jours/2026-12-20'"); pg.wait_for_timeout(500)
    h = lambda: pg.evaluate("location.hash")
    swipe(pg, "#d-2026-12-20 h2", 260, 100)
    check("G1 de la droite vers la gauche : jour suivant (21)", h() == "#/jours/2026-12-21", h())
    swipe(pg, "#d-2026-12-21 h2", 100, 260)
    check("G2 de la gauche vers la droite : jour précédent (20)", h() == "#/jours/2026-12-20", h())
    swipe(pg, "#d-2026-12-20 h2", 100, 130)
    check("G3 un petit geste ne change rien", h() == "#/jours/2026-12-20", h())
    swipe(pg, "#d-2026-12-20 h2", 100, 260, 300, 520)
    check("G4 un geste surtout vertical (défilement) ne change rien", h() == "#/jours/2026-12-20", h())
    swipe(pg, "#d-2026-12-20 h2", 10, 200)
    check("G5 un geste qui part du bord de l'écran est ignoré (retour du téléphone)", h() == "#/jours/2026-12-20", h())
    swipe(pg, ".strip ol", 100, 260)
    check("G6 sur le bandeau des jours : ignoré (il défile tout seul)", h() == "#/jours/2026-12-20", h())
    pg.evaluate("location.hash = '#/jours/2026-12-18'"); pg.wait_for_timeout(500)
    swipe(pg, "#d-2026-12-18 h2", 100, 260)
    check("G7 premier jour : rien avant", h() == "#/jours/2026-12-18", h())
    pg.evaluate("location.hash = '#/jours/2027-01-03'"); pg.wait_for_timeout(500)
    swipe(pg, "#d-2027-01-03 h2", 260, 100)
    check("G8 dernier jour : rien après", h() == "#/jours/2027-01-03", h())
    pg.evaluate("location.hash = '#/jours/2026-12-20'"); pg.wait_for_timeout(500)
    for k in range(3):
        swipe(pg, "#d-2026-12-2%d h2" % (k), 100, 260) if False else None
    cap = pg.locator("#d-2026-12-20 .cap")
    if cap.count() and cap.first.is_visible():
        swipe(pg, "#d-2026-12-20 .cap", 100, 260)
        check("G9 un geste sur un champ de texte est ignoré", h() == "#/jours/2026-12-20", h())
    ctx.close()
    # ───── H. icône du taxi ─────
    ctx, pg = newpg(b, "Anne")
    d = pg.evaluate("""() => [...document.querySelectorAll('a.tile[href="#/taxi"] svg path')].map(p => p.getAttribute('d')).join('|')""")
    check("H1 accueil et Utile : la tuile « Cartes taxi » a un panneau de direction (plus la voiture)", d.count("M5 5h10.5") == 2 and "A1.5 1.5" not in d, d[:120])
    pg.evaluate("location.hash = '#/hotels'"); pg.wait_for_timeout(400)
    check("H2 le bouton « Carte taxi » des hôtels aussi", pg.evaluate("document.querySelector('#v-hotels a[href^=\"#/taxi/\"] svg path').getAttribute('d')").startswith("M12 3v18"))
    pg.evaluate("location.hash = '#/'"); pg.wait_for_timeout(400)
    pg.locator('a.tile[href="#/taxi"]').first.scroll_into_view_if_needed(); pg.wait_for_timeout(200)
    pg.locator('a.tile[href="#/taxi"]').first.screenshot(path=ROOT + "ph/n_taxi_tile.png")
    ctx.close()
    # ───── I. enveloppe du Nouvel An ─────
    ctx, pg = newpg(b, "Invité", when="2026-12-25T10:00:00Z")
    check("I1 25 décembre : Noël oui, Nouvel An pas encore", pg.is_visible("#xmas") and not pg.is_visible("#ny"))
    ctx.close()
    ctx, pg = newpg(b, "Invité", when="2026-12-30T22:30:00Z")      # 23 h 30 à Paris, le 30
    check("I2 30 décembre 23 h 30 (Paris) : pas encore", not pg.is_visible("#ny"))
    ctx.close()
    ctx, pg = newpg(b, "Invité", when="2026-12-30T23:30:00Z")      # 0 h 30 à Paris, le 31
    check("I3 31 décembre (Paris) : l'enveloppe du Nouvel An est là, fermée ; celle de Noël a disparu",
          pg.is_visible("#ny-env") and not pg.is_visible("#ny-card") and not pg.is_visible("#xmas"))
    pg.screenshot(path=ROOT + "ph/n_ny_closed.png")
    pg.click("#ny-env"); pg.wait_for_timeout(900)
    t = pg.inner_text("#ny-card")
    check("I4 on l'ouvre : « Bonne année 2027 ! », six heures, P.-S. de Boop et de Minou", pg.is_visible("#ny-card") and "bonne année 2027" in t.lower() and "six heures" in t and "Boop et de Minou" in t, t[:100])
    check("I5 mémoire du Nouvel An seule", pg.evaluate("localStorage.getItem('carnet.ny')") == "1" and pg.evaluate("localStorage.getItem('carnet.xmas')") is None)
    pg.screenshot(path=ROOT + "ph/n_ny_open.png")
    pg.reload(wait_until="load"); pg.wait_for_timeout(600)
    check("I6 après rechargement : le mot du Nouvel An reste ouvert", pg.is_visible("#ny-card"))
    ctx.close()
    ctx, pg = newpg(b, "Flo", when="2027-01-02T10:00:00Z")
    check("I7 un voyageur ne voit aucune enveloppe", not pg.is_visible("#ny") and not pg.is_visible("#xmas"))
    ctx.close()
    ctx, pg = newpg(b, "Invité", when="2027-01-01T10:00:00Z", vw=320)
    pg.click("#ny-env"); pg.wait_for_timeout(700)
    check("I8 1er janvier, 320 px : l'enveloppe est encore là, pas de débordement", pg.is_visible("#ny-card") and pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 0)
    pg.screenshot(path=ROOT + "ph/n_env_320.png", full_page=False)
    ctx.close()
    # ───── les enveloppes disparaissent après leur jour ─────
    for when, xm, ny, lab in (("2026-12-25T22:30:00Z", False, False, "25 déc. 23 h 30 Paris : Noël encore là"), ("2026-12-25T23:30:00Z", False, False, "26 déc. 0 h 30 Paris : Noël a disparu"),
                              ("2026-12-26T10:00:00Z", False, False, "26 décembre : rien"), ("2027-01-01T22:30:00Z", False, True, "1er janv. 23 h 30 Paris : Nouvel An encore là"),
                              ("2027-01-01T23:30:00Z", False, False, "2 janv. 0 h 30 Paris : Nouvel An a disparu")):
        ctx, pg = newpg(b, "Invité", when=when)
        if when.startswith("2026-12-25T22"): xm = True
        check("K %s" % lab, pg.is_visible("#xmas") == xm and pg.is_visible("#ny") == ny, (pg.is_visible("#xmas"), pg.is_visible("#ny")))
        ctx.close()
    ctx, pg = newpg(b, "Invité", when="2026-12-25T10:00:00Z")
    pg.click("#xm-env"); pg.wait_for_timeout(600)
    pg.clock.set_fixed_time("2026-12-26T10:00:00Z"); pg.reload(wait_until="load"); pg.wait_for_timeout(700)
    check("K6 Noël ouverte puis le lendemain : plus rien", not pg.is_visible("#xmas") and not pg.is_visible("#xm-card"))
    ctx.close()
    # ───── J. page d'aperçu (hors menus) ─────
    ctx, pg = newpg(b, "Anne")
    pg.evaluate("location.hash = '#/previsualisation'"); pg.wait_for_timeout(600)
    check("J1 aperçu : les deux enveloppes sont visibles, fermées, sans attendre la date", pg.is_visible("#pvx-env") and pg.is_visible("#pvn-env") and not pg.is_visible("#pvx-card") and not pg.is_visible("#pvn-card"))
    pg.click("#pvx-env"); pg.wait_for_timeout(700)
    check("J2 Noël s'ouvre avec le vrai texte", pg.is_visible("#pvx-card") and "très coloré" in pg.inner_text("#pvx-card") and "Moomoo et d’Aftonsparv" in pg.inner_text("#pvx-card"))
    pg.click("#pvn-env"); pg.wait_for_timeout(700)
    check("J3 Nouvel An s'ouvre avec le vrai texte", pg.is_visible("#pvn-card") and "six heures" in pg.inner_text("#pvn-card") and "Boop et de Minou" in pg.inner_text("#pvn-card"))
    check("J4 l'aperçu ne touche pas à la mémoire des vraies enveloppes", pg.evaluate("localStorage.getItem('carnet.xmas')") is None and pg.evaluate("localStorage.getItem('carnet.ny')") is None)
    pg.click('[data-pv-close="0"]'); pg.wait_for_timeout(400)
    check("J5 « Refermer » referme", not pg.is_visible("#pvx-card") and pg.is_visible("#pvn-card"))
    check("J6 carte postale : jour 1 sur 17 (Moomoo)", "Jour 1 sur 17" in pg.inner_text("#pv-pc-n") and "Moomoo" in pg.inner_text("#pv-pc"), pg.inner_text("#pv-pc-n"))
    pg.click('[data-pv-pc="1"]'); pg.wait_for_timeout(200)
    check("J7 jour suivant : Aftonsparv", "Jour 2 sur 17" in pg.inner_text("#pv-pc-n") and "Aftonsparv" in pg.inner_text("#pv-pc"))
    pg.click('[data-pv-pc="-1"]'); pg.click('[data-pv-pc="-1"]'); pg.wait_for_timeout(200)
    check("J8 on ne dépasse pas le premier jour", "Jour 1 sur 17" in pg.inner_text("#pv-pc-n"))
    pg.screenshot(path=ROOT + "ph/n_preview.png", full_page=True)
    check("J9 aucun accueil ni menu ne mène à la page (pas de lien)", pg.evaluate("document.querySelectorAll('a[href=\"#/previsualisation\"]').length") == 0)
    ctx.close()
    ctx, pg = newpg(b, "Invité", vw=320)
    pg.evaluate("location.hash = '#/previsualisation'"); pg.wait_for_timeout(500); pg.click("#pvn-env"); pg.wait_for_timeout(700)
    check("J10 320 px : pas de débordement", pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 0)
    ctx.close()
    b.close()
check("Z0 aucune erreur JavaScript", not errs, errs)
print("t43 : %d OK, %d échecs" % (n_ok, n_ko))
