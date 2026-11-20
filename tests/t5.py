import subprocess, time, sys
from playwright.sync_api import sync_playwright
PORT = 8766
URL = "http://127.0.0.1:%d/carnet-thailande-/" % PORT
def ok(c, msg): print(("OK   " if c else "FAIL ") + msg)
srv = subprocess.Popen([sys.executable, "serve.py", str(PORT)])
time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 402, "height": 714}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR")
        pg = ctx.new_page()
        logs = []
        pg.on("pageerror", lambda e: logs.append(str(e)))
        pg.goto(URL, wait_until="load"); pg.wait_for_timeout(500)
        pg.evaluate("navigator.serviceWorker.ready.then(() => 1)"); pg.wait_for_timeout(2000)
        pg.reload(wait_until="load"); pg.wait_for_timeout(600)
        ok(pg.evaluate("!!navigator.serviceWorker.controller"), "service worker actif")
        pg.goto(URL + "test.html", wait_until="load"); pg.wait_for_timeout(500)   # visite préalable de test.html (comme précaché)
        pg.goto(URL + "#/hotels", wait_until="load"); pg.wait_for_timeout(300)
        # --- on coupe vraiment le serveur
        srv.kill(); srv.wait(); time.sleep(0.5)
        pg.goto(URL, wait_until="load"); pg.wait_for_timeout(800)
        ok(pg.is_visible("#v-home") and "THAÏLANDE" in pg.inner_text("#v-home h1").upper(), "SERVEUR COUPÉ : l'accueil s'ouvre")
        pg.goto(URL + "index.html?x=1#/jours/2026-12-21", wait_until="load"); pg.wait_for_timeout(600)
        ok(pg.is_visible("#d-2026-12-21"), "SERVEUR COUPÉ : index.html?x=1#/jours s'ouvre")
        pg.goto(URL + "test.html", wait_until="load"); pg.wait_for_timeout(500)
        ok("TEST DU TÉLÉPHONE" in pg.inner_text("body").upper(), "SERVEUR COUPÉ : test.html s'ouvre")
        ok(pg.is_visible("text=Retour au carnet"), "lien retour présent dans test.html")
        pg.click("text=Retour au carnet"); pg.wait_for_timeout(600)
        ok(pg.is_visible("#v-home"), "retour au carnet -> accueil")
        pg.evaluate("location.hash = '#/metro'")
        pg.wait_for_selector("#mv-stage svg", timeout=8000)
        ok(True, "SERVEUR COUPÉ : plan du métro chargé depuis le cache")
        fonts = pg.evaluate("document.fonts.ready.then(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight + ' ' + f.style))")
        print("     polices chargées :", fonts)
        print("ERREURS JS:", logs)
        b.close()
finally:
    try: srv.kill()
    except Exception: pass
