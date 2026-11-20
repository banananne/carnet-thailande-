from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
def ok(c, msg): print(("OK   " if c else "FAIL ") + msg)
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(320, 640), (360, 740), (430, 900), (768, 1024)]:
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR")
        pg = ctx.new_page()
        pg.goto(URL, wait_until="load"); pg.wait_for_timeout(400)
        res = []
        for route in ["#/", "#/jours/2026-12-26", "#/jours/2026-12-21", "#/hotels", "#/utile", "#/metro"]:
            pg.evaluate("r => { location.hash = r }", route); pg.wait_for_timeout(250)
            sw = pg.evaluate("document.documentElement.scrollWidth")
            res.append((route, sw))
        bad = [r for r in res if r[1] > w]
        ok(not bad, "largeur %d : pas de débordement horizontal %s" % (w, bad or ""))
        if w in (320, 360):
            pg.evaluate("location.hash = '#/'"); pg.wait_for_timeout(300)
            pg.screenshot(path=OUT + "w%d_home.png" % w)
            pg.evaluate("location.hash = '#/jours/2026-12-26'"); pg.wait_for_timeout(300)
            pg.screenshot(path=OUT + "w%d_day.png" % w)
        if w == 768:
            pg.evaluate("location.hash = '#/'"); pg.wait_for_timeout(300)
            pg.screenshot(path=OUT + "w768_home.png")
        # retour depuis une étape de l'accueil
        pg.evaluate("location.hash = '#/'"); pg.wait_for_timeout(250)
        pg.click(".stages li:nth-child(2) a"); pg.wait_for_timeout(300)
        ok(pg.evaluate("location.hash") == "#/jours/2026-12-26", "étape 2 -> " + pg.evaluate("location.hash"))
        pg.go_back(); pg.wait_for_timeout(300)
        ok(pg.is_visible("#v-home"), "retour -> accueil")
        ctx.close()
    b.close()
