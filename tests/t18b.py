from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
with sync_playwright() as p:
    b = p.chromium.launch()
    for (vw, vh) in ((390, 844), (320, 640)):
        ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
        pg = ctx.new_page(); cdp = ctx.new_cdp_session(pg)
        pg.goto(BASE + "#/mots-meles"); pg.wait_for_timeout(500)
        def touch(t, pts): cdp.send("Input.dispatchTouchEvent", {"type": t, "touchPoints": [{"x": x, "y": y, "id": 1} for (x, y) in pts]})
        # défilement vers le bas en partant de l'en-tête (hors grille)
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(100)
        before = pg.evaluate("window.scrollY")
        x, y = vw / 2, 150
        touch("touchStart", [(x, y)])
        for i in range(1, 11): touch("touchMove", [(x, y - 30 * i)]); pg.wait_for_timeout(16)
        touch("touchEnd", []); pg.wait_for_timeout(700)
        after = pg.evaluate("window.scrollY")
        print(vw, "défilement depuis l'en-tête :", before, "→", after, "OK" if after > before + 20 else "ÉCHEC")
        # défilement vers le haut depuis la liste des mots
        pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(200)
        before = pg.evaluate("window.scrollY")
        r = pg.evaluate("(()=>{const e=document.querySelector('#mm-words').getBoundingClientRect();return {x:e.left+e.width/2,y:e.top+30}})()")
        touch("touchStart", [(r["x"], r["y"])])
        for i in range(1, 11): touch("touchMove", [(r["x"], r["y"] + 25 * i)]); pg.wait_for_timeout(16)
        touch("touchEnd", []); pg.wait_for_timeout(700)
        after = pg.evaluate("window.scrollY")
        print(vw, "défilement vers le haut depuis la liste :", before, "→", after, "OK" if after < before - 20 else "ÉCHEC")
        # marges de la grille : défiler en partant de la marge gauche (16 px) à côté de la grille
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(100)
        g = pg.evaluate("(()=>{const r=document.querySelector('#mm-board').getBoundingClientRect();return {l:r.left,t:r.top,w:r.width,h:r.height}})()")
        print(vw, "grille : gauche=%.0f largeur=%.0f (marge gauche %.0f px, droite %.0f px)" % (g["l"], g["w"], g["l"], vw - g["l"] - g["w"]))
        ctx.close()
    b.close()
