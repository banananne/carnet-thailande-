# -*- coding: utf-8 -*-
"""« Qui es-tu ? » : après le choix du prénom (voyageur ou invité·e), le bloc reste ouvert tant qu'on ne le referme pas."""
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8767/carnet-thailande-/"
n_ok = n_ko = 0
def check(name, c, info=""):
    global n_ok, n_ko
    if c: n_ok += 1
    else: n_ko += 1; print("  ✗", name, info)
with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    for who in ("Anne", "Daphne", "Flo", "Arthur", "Invité"):
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block")
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(500)
        pg.click('#who button[data-n="%s"]' % who); pg.wait_for_timeout(1000)
        check("%s : juste après le choix, le bloc est ouvert et la ligne de repli est là" % who, pg.is_visible("#who-box") and pg.is_visible("#who-bar"))
        pg.wait_for_timeout(15000)
        check("%s : 16 s après, toujours ouvert" % who, pg.is_visible("#who-box"))
        pg.click("#who-bar"); pg.wait_for_timeout(400)
        check("%s : il se referme quand on touche la ligne" % who, not pg.is_visible("#who-box") and pg.is_visible("#who-bar"))
        pg.click("#who-bar"); pg.wait_for_timeout(400)
        check("%s : il se rouvre au toucher" % who, pg.is_visible("#who-box"))
        pg.click("#who-bar"); pg.wait_for_timeout(300); pg.reload(wait_until="load"); pg.wait_for_timeout(600)
        check("%s : au rechargement, il reste replié et le prénom est gardé" % who, not pg.is_visible("#who-box") and pg.evaluate("localStorage.getItem('carnet.who')") == who)
        ctx.close()
    check("aucune erreur JavaScript", not errs, errs[:2])
print("t39 :", n_ok, "OK,", n_ko, "KO")
