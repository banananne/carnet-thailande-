"""Mots mêlés avec de VRAIS événements tactiles (CDP Input.dispatchTouchEvent), comme sur un téléphone."""
import json
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
M = json.load(open("/home/claude/site_en_ligne/data_motsmeles.json", encoding="utf-8"))
W = {w["k"]: w for w in M["words"]}
errs = []; fails = []; n = [0]


def ok(cond, msg):
    n[0] += 1
    if not cond:
        fails.append(msg); print("ÉCHEC:", msg)


with sync_playwright() as p:
    b = p.chromium.launch()
    for (vw, vh) in ((390, 844), (320, 640)):
        ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        cdp = ctx.new_cdp_session(pg)
        pg.goto(BASE + "#/mots-meles"); pg.wait_for_timeout(500)

        def geo():
            return pg.evaluate("(()=>{const r=document.querySelector('#mm-board').getBoundingClientRect();return {l:r.left,t:r.top,w:r.width}})()")

        def center(r, c, dx=0, dy=0):
            g = geo(); cw = g["w"] / 20
            return g["l"] + (c + .5 + dx) * cw, g["t"] + (r + .5 + dy) * cw

        def to_view(r):
            g = geo(); cw = g["w"] / 20; y = g["t"] + (r + .5) * cw
            if y < 100 or y > vh - 110:
                pg.evaluate("window.scrollBy(0,%f)" % (y - vh / 2)); pg.wait_for_timeout(120)

        def touch(type_, pts):
            cdp.send("Input.dispatchTouchEvent", {"type": type_, "touchPoints": [{"x": x, "y": y, "id": 1} for (x, y) in pts]})

        def finger_drag(r0, c0, r1, c1, dx1=0, dy1=0, steps=8):
            to_view((r0 + r1) / 2)
            x0, y0 = center(r0, c0); x1, y1 = center(r1, c1, dx1, dy1)
            touch("touchStart", [(x0, y0)]); pg.wait_for_timeout(30)
            for i in range(1, steps + 1):
                touch("touchMove", [(x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps)]); pg.wait_for_timeout(16)
            touch("touchEnd", []); pg.wait_for_timeout(80)

        def finger_tap(r, c):
            to_view(r); x, y = center(r, c)
            pg.touchscreen.tap(x, y); pg.wait_for_timeout(80)

        def end(w):
            return w["r"] + (len(w["k"]) - 1) * w["dr"], w["c"] + (len(w["k"]) - 1) * w["dc"]

        def count():
            return int(pg.inner_text("#mm-count"))

        tag = "%d" % vw
        sy0 = pg.evaluate("window.scrollY")
        ok(count() == 0, "[%s] départ à 0" % tag)
        # 1) glisser au doigt : BAHT (diagonale)
        w = W["BAHT"]; e = end(w); finger_drag(w["r"], w["c"], e[0], e[1]); ok(count() == 1, "[%s] BAHT au doigt (diagonale)" % tag)
        # 2) à l'envers : AVION
        w = W["AVION"]; e = end(w); finger_drag(e[0], e[1], w["r"], w["c"]); ok(count() == 2, "[%s] AVION à l'envers au doigt" % tag)
        # 3) doigt de travers
        w = W["BANPHE"]; e = end(w); finger_drag(w["r"], w["c"], e[0], e[1], 0, 0.42); ok(count() == 3, "[%s] BANPHE doigt de travers" % tag)
        # 4) un glissement vertical sur la grille ne doit PAS faire défiler la page
        w = W["GECKO"]; to_view(w["r"]); y_before = pg.evaluate("window.scrollY")
        x0, y0 = center(w["r"], w["c"]); touch("touchStart", [(x0, y0)])
        for i in range(1, 9):
            touch("touchMove", [(x0, y0 - 14 * i)]); pg.wait_for_timeout(16)
        touch("touchEnd", []); pg.wait_for_timeout(100)
        ok(abs(pg.evaluate("window.scrollY") - y_before) < 2, "[%s] glisser sur la grille ne fait pas défiler la page (%s → %s)" % (tag, y_before, pg.evaluate("window.scrollY")))
        # 5) toucher-toucher : GECKO au doigt
        w = W["GECKO"]; e = end(w); n0 = count()
        finger_tap(w["r"], w["c"]); finger_tap(e[0], e[1]); ok(count() == n0 + 1, "[%s] GECKO en toucher-toucher (tactile)" % tag)
        # 6) la page défile toujours en touchant hors de la grille (sur la liste des mots)
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(100)
        g = geo(); startY = min(vh - 130, max(g["t"] + g["w"] + 90, 0))
        # (la liste est en bas de page : centrée, la page est déjà au maximum et ne peut plus défiler ; on se place donc 300 px plus haut)
        pg.evaluate("window.scrollTo(0, Math.max(0, document.documentElement.scrollHeight - innerHeight - 300))"); pg.wait_for_timeout(120)
        before = pg.evaluate("window.scrollY")
        r = pg.evaluate("(()=>{const e=document.querySelector('#mm-words').getBoundingClientRect();return {x:e.left+e.width/2,y:e.top+20}})()")
        touch("touchStart", [(r["x"], r["y"])])
        for i in range(1, 9):
            touch("touchMove", [(r["x"], r["y"] - 25 * i)]); pg.wait_for_timeout(16)
        touch("touchEnd", []); pg.wait_for_timeout(500)
        after = pg.evaluate("window.scrollY")
        ok(after > before + 20, "[%s] le doigt sur la liste fait défiler la page (%s → %s)" % (tag, before, after))
        # 7) tout trouver au doigt, dans les deux sens
        pg.click("#mm-reset") if False else None
        for k, w in W.items():
            if k in ("BAHT", "AVION", "BANPHE", "GECKO"):
                continue
            e = end(w)
            if (hash(k) % 2):
                finger_drag(w["r"], w["c"], e[0], e[1])
            else:
                finger_drag(e[0], e[1], w["r"], w["c"])
        got = count()
        ok(got == 40, "[%s] 40 mots trouvés au doigt (obtenu %d)" % (tag, got))
        if got != 40:
            miss = pg.evaluate("[...document.querySelectorAll('#mm-words li:not(.found)')].map(l=>l.textContent.trim())")
            print("   manquants:", miss)
        pg.wait_for_timeout(700)
        st = json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')") or '{"d":[],"b":[]}')
        ok("mots" in st["b"], "[%s] tampon mots mêlés gagné au doigt" % tag)
        ctx.close()
    b.close()
print("\n%d vérifications, %d échecs" % (n[0], len(fails)))
print("ERREURS JS:", errs if errs else "aucune")
