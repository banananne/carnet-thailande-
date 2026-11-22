# -*- coding: utf-8 -*-
"""Invité·e : « Reportage photo » (photos chiffrées, code, fil de polaroïds)."""
import sys
from playwright.sync_api import sync_playwright
BASE_R = "http://127.0.0.1:8771/carnet-thailande-/"     # avec reportage (3 photos, code d'essai)
BASE_N = "http://127.0.0.1:8770/carnet-thailande-/"     # sans reportage
ROOT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/"
n_ok = n_ko = 0
def check(name, c, info=""):
    global n_ok, n_ko
    if c: n_ok += 1
    else: n_ko += 1; print("  ✗", name, info)
errs = []
sp = lambda s: s.replace(" ", " ")
def newpg(b, vw=390):
    ctx = b.new_context(viewport={"width": vw, "height": 844}, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); return ctx, pg
with sync_playwright() as p:
    b = p.chromium.launch()
    # ───── sans aucun reportage publié ─────
    ctx, pg = newpg(b)
    pg.goto(BASE_N, wait_until="load"); pg.wait_for_timeout(400)
    pg.click('#who button[data-n="Invité"]'); pg.wait_for_timeout(600)
    check("A1 invité·e : carte « Reportage photo » visible, pas celle des voyageurs", pg.is_visible(".phc-guest") and not pg.is_visible(".phc-trav"))
    pg.click(".phc-guest"); pg.wait_for_timeout(900)
    check("A2 aucun reportage publié : message d'attente, pas de champ de code", "pas encore commencé" in sp(pg.inner_text("#rp-msg")) and not pg.is_visible("#rp-lock"), pg.inner_text("#rp-msg"))
    ctx.close()
    # ───── avec le reportage d'essai ─────
    ctx, pg = newpg(b)
    pg.goto(BASE_R, wait_until="load"); pg.wait_for_timeout(400)
    pg.evaluate("localStorage.setItem('carnet.who','Invité')"); pg.reload(wait_until="load"); pg.wait_for_timeout(500)
    pg.evaluate("location.hash = '#/reportage'"); pg.wait_for_timeout(900)
    check("B1 le code est demandé", pg.is_visible("#rp-lock") and not pg.is_visible("#rp-feed figure"))
    pg.fill("#rp-code", "mauvais-0000"); pg.click("#rp-form button"); pg.wait_for_timeout(2500)
    check("B2 mauvais code refusé", "pas le bon code" in sp(pg.inner_text("#rp-err")) and pg.locator("#rp-feed figure").count() == 0, pg.inner_text("#rp-err"))
    pg.fill("#rp-code", "  ESSAI 1234 "); pg.click("#rp-form button"); pg.wait_for_timeout(3500)
    check("B3 bon code (majuscules, espaces) : trois polaroïds", pg.locator("#rp-feed figure").count() == 3 and not pg.is_visible("#rp-lock"), pg.locator("#rp-feed figure").count())
    check("B4 « 3 photos »", "3 photos" in sp(pg.inner_text("#rp-msg")), pg.inner_text("#rp-msg"))
    days = [sp(x) for x in pg.eval_on_selector_all("#rp-feed h2", "els => els.map(e => e.textContent)")]
    check("B5 deux jours, le plus récent d'abord", days == ["Mardi 22 décembre", "Dimanche 20 décembre"], days)
    order = pg.eval_on_selector_all("#rp-feed figure img", "els => els.map(e => e.alt)")
    check("B6 ordre : Flo (ajoutée en dernier) puis Daphne le 22, Anne le 20", [("Flo" in a, "Daphne" in a, "Anne" in a) for a in order] == [(True, False, False), (False, True, False), (False, False, True)], order)
    pg.wait_for_timeout(1500)
    nat = pg.eval_on_selector_all("#rp-feed figure img", "els => els.map(e => [e.naturalWidth, e.naturalHeight])")
    check("B7 les trois photos sont déchiffrées et affichées (1080 × 1500)", nat == [[1080, 1500]] * 3, nat)
    check("B8 le bouton « Oublier le code » apparaît", pg.is_visible("#rp-forget"))
    pg.screenshot(path=ROOT + "ph/viewer.png", full_page=True)
    ov = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("B9 pas de débordement horizontal", ov <= 0, ov)
    pg.click("#rp-feed figure"); pg.wait_for_timeout(300)
    check("B10 toucher une photo l'agrandit", pg.is_visible("#rp-big") and pg.evaluate("document.querySelector('#rp-big img').naturalWidth") == 1080)
    pg.click("#rp-big"); pg.wait_for_timeout(200)
    check("B11 toucher l'image agrandie la referme", not pg.is_visible("#rp-big"))
    # mémoire du code
    check("B12 le code est gardé sur ce téléphone (normalisé)", pg.evaluate("localStorage.getItem('carnet.rep.code')") == "essai1234")
    pg.reload(wait_until="load"); pg.wait_for_timeout(500); pg.evaluate("location.hash = '#/jours'"); pg.wait_for_timeout(300); pg.evaluate("location.hash = '#/reportage'"); pg.wait_for_timeout(3500)
    check("B13 au retour : ouvert tout seul, sans redemander le code", pg.locator("#rp-feed figure").count() == 3 and not pg.is_visible("#rp-lock"))
    pg.click("#rp-forget"); pg.wait_for_timeout(500)
    check("B14 « Oublier le code » : verrouillé, photos retirées", pg.is_visible("#rp-lock") and pg.locator("#rp-feed figure").count() == 0 and pg.evaluate("localStorage.getItem('carnet.rep.code')") is None)
    # le code d'une autre personne (sans accents ni majuscules) est équivalent ; un code vide est refusé
    pg.click("#rp-form button"); pg.wait_for_timeout(300)
    check("B15 code vide : on le demande", "Tape le code" in sp(pg.inner_text("#rp-err")))
    # hors réseau
    pg.fill("#rp-code", "essai-1234"); pg.click("#rp-form button"); pg.wait_for_timeout(3000)
    ctx.set_offline(True); pg.evaluate("location.hash = '#/jours'"); pg.wait_for_timeout(200); pg.evaluate("location.hash = '#/reportage'"); pg.wait_for_timeout(1500)
    check("B16 sans réseau : message clair (sans planter)", pg.locator("#rp-feed figure").count() >= 0 and ("Impossible" in sp(pg.inner_text("#rp-msg")) or pg.locator("#rp-feed figure").count() == 3), pg.inner_text("#rp-msg"))
    ctx.close()
    # voyageur : peut aussi voir le reportage (aperçu) depuis sa page
    ctx, pg = newpg(b)
    pg.goto(BASE_R, wait_until="load"); pg.wait_for_timeout(400)
    pg.evaluate("localStorage.setItem('carnet.who','Flo')"); pg.reload(wait_until="load"); pg.wait_for_timeout(500)
    pg.evaluate("location.hash = '#/photo-invites'"); pg.wait_for_timeout(400); pg.click(".pi-rep"); pg.wait_for_timeout(700)
    check("C1 un voyageur ouvre le reportage depuis sa page", pg.evaluate("location.hash") == "#/reportage" and pg.is_visible("#rp-lock"))
    ctx.close()
    # petits écrans
    for vw in (360, 320):
        ctx, pg = newpg(b, vw)
        pg.goto(BASE_R, wait_until="load"); pg.wait_for_timeout(300)
        pg.evaluate("localStorage.setItem('carnet.who','Invité')"); pg.reload(wait_until="load"); pg.wait_for_timeout(400)
        pg.evaluate("location.hash = '#/reportage'"); pg.wait_for_timeout(500)
        ov1 = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        pg.fill("#rp-code", "essai-1234"); pg.click("#rp-form button"); pg.wait_for_timeout(3500)
        ov2 = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        check("D %d px : pas de débordement (verrouillé et ouvert)" % vw, ov1 <= 0 and ov2 <= 0, (ov1, ov2))
        ctx.close()
    check("Z aucune erreur JavaScript", not errs, errs[:2])
# confidentialité des fichiers publiés
import os, glob, json
d = ROOT + "web_r/reportage/"
raw = b"".join(open(f, "rb").read() for f in glob.glob(d + "*"))
check("P1 aucun JPEG en clair dans les fichiers publiés", b"\xff\xd8\xff" not in raw and b"JFIF" not in raw and b"Exif" not in raw)
check("P2 la liste est chiffrée (aucun prénom, aucune date lisibles)", all(w not in open(d + "m.json").read() for w in ("Anne", "Daphne", "Flo", "2026-12")))
check("P3 seuls m.json et p*.bin sont publiés", sorted(os.listdir(d)) == sorted(["m.json"] + [os.path.basename(f) for f in glob.glob(d + "p*.bin")]))
print("t41 :", n_ok, "OK,", n_ko, "KO")
