# -*- coding: utf-8 -*-
"""Remise à zéro unique : un téléphone qui avait des données les perd une fois, puis garde ce qu'il fait ensuite."""
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8768/carnet-thailande-/"
n_ok = n_ko = 0
def check(name, c, info=""):
    global n_ok, n_ko
    if c: n_ok += 1
    else: n_ko += 1; print("  ✗", name, info)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block")
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    # un « ancien » état : données de l'ancienne version, posées avant que la page ne tourne
    pg.goto(BASE + "test.html", wait_until="load")      # même origine, sans le script de remise à zéro
    pg.evaluate("""() => { localStorage.setItem('carnet.who','Anne'); localStorage.setItem('carnet.stamps','{"a":1}'); localStorage.setItem('carnet.food','{"x":5}');
        localStorage.setItem('carnet.food.own','["Mon plat"]'); localStorage.setItem('carnet.open','1'); localStorage.setItem('carnet.env.o.Anne.w1','1'); localStorage.setItem('autre.cle','garde');
        return new Promise(res => { var r = indexedDB.open('carnet-thailande',1); r.onupgradeneeded = () => r.result.createObjectStore('photos');
          r.onsuccess = () => { var t = r.result.transaction('photos','readwrite'); t.objectStore('photos').put(new ArrayBuffer(8),'2026-12-18'); t.oncomplete = () => { r.result.close(); res(); }; }; }); }""")
    check("T0 données posées", pg.evaluate("localStorage.getItem('carnet.who')") == "Anne")
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(900)
    ks = pg.evaluate("Object.keys(localStorage).sort()")
    check("T1 tout « carnet.* » est effacé (sauf l'époque) et le reste est intact", ks == ["autre.cle", "carnet.epoch"], ks)
    check("T2 l'accueil demande le prénom", pg.is_visible("#who-box") or pg.is_visible("#who-bar"))
    nph = pg.evaluate("""() => new Promise(res => { var r = indexedDB.open('carnet-thailande',1); r.onupgradeneeded = () => { if (!r.result.objectStoreNames.contains('photos')) r.result.createObjectStore('photos'); };
        r.onsuccess = () => { var q = r.result.transaction('photos').objectStore('photos').count(); q.onsuccess = () => res(q.result); }; })""")
    check("T3 les photos sont effacées", nph == 0, nph)
    pg.click('#who button[data-n="Flo"]'); pg.wait_for_timeout(500)
    pg.evaluate("localStorage.setItem('carnet.stamps','{\"b\":1}')")
    pg.reload(wait_until="load"); pg.wait_for_timeout(600)
    check("T4 après un rechargement, rien n'est ré-effacé", pg.evaluate("localStorage.getItem('carnet.who')") == "Flo" and pg.evaluate("localStorage.getItem('carnet.stamps')") == '{"b":1}')
    check("T5 pas de lien « Tester mon téléphone » en bas de l'accueil", "Tester mon" not in pg.inner_text("body") and pg.evaluate("document.querySelectorAll('a[href=\"test.html\"]').length") == 0)
    check("T6 aucune erreur JavaScript", not errs, errs[:2])
    ctx2 = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, locale="fr-FR", service_workers="block"); pg2 = ctx2.new_page(); e2 = []
    pg2.on("pageerror", lambda e: e2.append(str(e))); pg2.goto(BASE, wait_until="load"); pg2.wait_for_timeout(600)
    check("T7 nouvel invité : accueil normal, époque posée, aucune erreur", pg2.evaluate("localStorage.getItem('carnet.epoch')") is not None and not e2)
print("t37 :", n_ok, "OK,", n_ko, "KO")
