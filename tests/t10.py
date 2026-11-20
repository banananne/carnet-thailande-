import subprocess, time, sys
from playwright.sync_api import sync_playwright
PORT = 8767
URL = "http://127.0.0.1:%d/carnet-thailande-/" % PORT
fails = []
def ok(c, msg, extra=""):
    print(("OK   " if c else "FAIL ") + msg + ("" if c or extra == "" else " : " + str(extra)))
    if not c: fails.append(msg)
srv = subprocess.Popen([sys.executable, "serve.py", str(PORT)])
time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR")
        pg = ctx.new_page()
        logs = []
        pg.on("pageerror", lambda e: logs.append(str(e)))
        pg.on("console", lambda m: logs.append(m.text) if m.type == "error" else None)
        # on ne visite QUE l'accueil en ligne : tout le reste doit venir du cache
        pg.goto(URL, wait_until="load"); pg.wait_for_timeout(500)
        pg.evaluate("navigator.serviceWorker.ready.then(() => 1)"); pg.wait_for_timeout(2500)
        pg.reload(wait_until="load"); pg.wait_for_timeout(600)
        ok(pg.evaluate("!!navigator.serviceWorker.controller"), "service worker actif")
        names = pg.evaluate("caches.keys().then(async ks => { const out = []; for (const k of ks) { const c = await caches.open(k); out.push(...(await c.keys()).map(r => new URL(r.url).pathname.replace('/carnet-thailande-/', ''))); } return out; })")
        print("     en cache :", len(names), "fichiers :", sorted(names))
        thai_cached = [n for n in names if "thai" in n.lower()]
        ok(len(thai_cached) > 0, "police thaïe dans le cache (précache)", names)
        # --- on coupe vraiment le serveur
        srv.kill(); srv.wait(); time.sleep(0.5)
        pg.goto(URL + "#/lexique", wait_until="load"); pg.wait_for_timeout(700)
        ok(pg.locator("#v-lexique .lx").count() == 29 and pg.is_visible("#v-lexique"), "HORS LIGNE : le lexique s'ouvre (29 lignes)")
        pg.click("#v-lexique .lx-main >> nth=2"); pg.wait_for_timeout(400)
        ok(pg.is_visible("#show") and pg.inner_text("#show-th") == "ขอโทษ", "HORS LIGNE : montrer en grand « Excusez-moi »", pg.inner_text("#show-th"))
        pg.click(".show-x"); pg.wait_for_timeout(300)
        fonts = pg.evaluate("document.fonts.ready.then(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight))")
        print("     polices chargées :", fonts)
        ok(any("Thai" in f for f in fonts), "HORS LIGNE : la police thaïe (Noto Sans Thai) est bien chargée depuis le cache", fonts)
        pg.goto(URL + "#/taxi/h2", wait_until="load"); pg.wait_for_timeout(600)
        vis = pg.evaluate("Array.from(document.querySelectorAll('.taxi')).filter(a => !a.hidden).map(a => a.dataset.id)")
        ok(vis == ["h2"], "HORS LIGNE : carte taxi du Thai Thai", vis)
        pg.click("#tx-h2 [data-show-card]"); pg.wait_for_timeout(400)
        ok("ไทย ไทย" in pg.inner_text("#show-card .tc"), "HORS LIGNE : carte taxi en grand")
        pg.click(".show-x"); pg.wait_for_timeout(300)
        pg.goto(URL + "#/convertisseur", wait_until="load"); pg.wait_for_timeout(500)
        pg.fill("#c-thb", "350"); pg.wait_for_timeout(100)
        ok(pg.input_value("#c-eur") == "9,41", "HORS LIGNE : convertisseur 350 ฿ = 9,41 €", pg.input_value("#c-eur"))
        pg.goto(URL + "#/good-to-know", wait_until="load"); pg.wait_for_timeout(500)
        ok(pg.locator("#v-gtk details.gb").count() == 5, "HORS LIGNE : Good to know")
        pg.goto(URL + "#/hotels", wait_until="load"); pg.wait_for_timeout(500)
        ok(pg.locator("#v-hotels a[href^='#/taxi/']").count() == 4, "HORS LIGNE : hôtels + cartes taxi")
        pg.reload(wait_until="load"); pg.wait_for_timeout(800)
        ok(pg.is_visible("#v-hotels"), "HORS LIGNE : rechargement sur #/hotels")
        print("ERREURS JS :", logs if logs else "aucune")
        b.close()
finally:
    try: srv.kill()
    except Exception: pass
print("\n%d échec(s)" % len(fails), fails)
