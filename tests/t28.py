"""Plan du métro (nouvelle carte portrait) : mise en page, ajustement, zoom, gestes, débordement."""
import json, sys, time
from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
W0, H0 = 490.392, 601.214
M = 90
ok = fail = 0
def check(name, cond, info=""):
    global ok, fail
    if cond: ok += 1
    else:
        fail += 1; print("  ✗", name, info)
STATE = """() => { const s = document.querySelector('#mv-stage'); const sv = s.querySelector('svg');
  const vb = sv.getAttribute('viewBox').split(' ').map(Number);
  const r = document.querySelector('#mv').getBoundingClientRect();
  return {vb, tr: s.style.transform, w: parseFloat(s.style.width), h: parseFloat(s.style.height), box: {x: r.x, y: r.y, w: r.width, h: r.height},
          sw: document.documentElement.scrollWidth, iw: window.innerWidth, ih: window.innerHeight}; }"""
def view(st):
    """vue effective (après commit) : échelle s, coin haut-gauche (vx,vy), largeur/hauteur visibles en unités du plan"""
    vb = st["vb"]; s = (st["box"]["w"] + 2 * M) / vb[2]
    vx = vb[0] + M / s; vy = vb[1] + M / s
    return s, vx, vy, st["box"]["w"] / s, st["box"]["h"] / s

errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    sizes = [(320, 568, 2), (360, 740, 3), (390, 844, 3), (402, 714, 3), (412, 915, 2.6), (768, 1024, 2), (844, 390, 3), (1024, 768, 1)]
    for (w, h, dsf) in sizes:
        mob = w < 900
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=dsf, is_mobile=mob, has_touch=mob, locale="fr-FR", service_workers="block")
        pg = ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL + "#/metro", wait_until="load")
        pg.wait_for_selector("#mv-stage svg", timeout=20000)
        pg.wait_for_timeout(500)
        st = pg.evaluate(STATE)
        s, vx, vy, vw, vh = view(st)
        tag = "%dx%d" % (w, h)
        # 1. rien ne déborde de l'écran
        check(tag + " pas de défilement horizontal", st["sw"] <= st["iw"] + 1, "%s>%s" % (st["sw"], st["iw"]))
        # 2. au départ, tout le plan est visible (avec une tolérance d'un demi-pixel)
        tol = 0.6 / s
        check(tag + " plan entier visible à l'ouverture", vx <= tol and vy <= tol and vx + vw >= W0 - tol and vy + vh >= H0 - tol, "vx=%.2f vy=%.2f vw=%.1f vh=%.1f" % (vx, vy, vw, vh))
        # 3. le plan n'est pas minuscule : il occupe au moins 70 % d'une des deux dimensions de la boîte
        fillw = W0 * s / st["box"]["w"]; fillh = H0 * s / st["box"]["h"]
        check(tag + " plan bien rempli dans la boîte", max(fillw, fillh) > 0.97, "fillw=%.2f fillh=%.2f" % (fillw, fillh))
        print("  %s boîte %.0fx%.0f  échelle ajustée %.3f px/u  remplissage %.0f%% x %.0f%%  boîte y=%.0f→%.0f / écran %d" % (tag, st["box"]["w"], st["box"]["h"], s, fillw * 100, fillh * 100, st["box"]["y"], st["box"]["y"] + st["box"]["h"], h))
        # 4. boutons : +, −, ajuster
        pg.click(".mctl button[data-z=in]"); pg.wait_for_timeout(500)
        s1 = view(pg.evaluate(STATE))[0]
        check(tag + " bouton + agrandit", s1 > s * 1.5, "%.3f→%.3f" % (s, s1))
        for i in range(12):
            pg.click(".mctl button[data-z=in]"); pg.wait_for_timeout(300)
        pg.wait_for_timeout(300)
        smax = view(pg.evaluate(STATE))[0]
        check(tag + " zoom max ≈ ×12", abs(smax / s - 12) < 0.3 or smax >= 6 * 0.99, "×%.2f" % (smax / s))
        pg.click(".mctl button[data-z=out]"); pg.wait_for_timeout(500)
        s2 = view(pg.evaluate(STATE))[0]
        check(tag + " bouton − réduit", s2 < smax * 0.7)
        pg.click(".mctl button[data-z=fit]"); pg.wait_for_timeout(600)
        st = pg.evaluate(STATE); s3, vx, vy, vw, vh = view(st)
        check(tag + " ajuster ramène au plan entier", abs(s3 - s) / s < 0.01 and vx <= tol and vy <= tol and vx + vw >= W0 - tol and vy + vh >= H0 - tol, "s=%.3f/%.3f" % (s3, s))
        # 5. double-tap : zoome puis revient
        if mob:
            box = st["box"]
            pg.evaluate("""() => {
              const el = document.querySelector('#mv'); const r = el.getBoundingClientRect();
              const ev = (type, id, x, y) => el.dispatchEvent(new PointerEvent(type, {pointerId: id, pointerType: 'touch', isPrimary: true, bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y}));
              const cx = r.width / 2, cy = r.height / 2;
              ev('pointerdown', 7, cx, cy); ev('pointerup', 7, cx, cy);
              ev('pointerdown', 8, cx + 3, cy + 2); ev('pointerup', 8, cx + 3, cy + 2);
            }""")
            pg.wait_for_timeout(700)
            s4 = view(pg.evaluate(STATE))[0]
            check(tag + " double-tap zoome", s4 > s * 2.3, "×%.2f" % (s4 / s))
            pg.evaluate("""() => {
              const el = document.querySelector('#mv'); const r = el.getBoundingClientRect();
              const ev = (type, id, x, y) => el.dispatchEvent(new PointerEvent(type, {pointerId: id, pointerType: 'touch', isPrimary: true, bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y}));
              const cx = r.width / 2, cy = r.height / 2;
              ev('pointerdown', 9, cx, cy); ev('pointerup', 9, cx, cy);
              ev('pointerdown', 10, cx + 3, cy + 2); ev('pointerup', 10, cx + 3, cy + 2);
            }""")
            pg.wait_for_timeout(700)
            s5 = view(pg.evaluate(STATE))[0]
            check(tag + " second double-tap revient à l'ajustement", abs(s5 - s) / s < 0.01, "×%.2f" % (s5 / s))
            # 6. pincer : écart 100 → 300 = ×3
            pg.evaluate("""() => {
              const el = document.querySelector('#mv'); const r = el.getBoundingClientRect();
              const ev = (type, id, x, y) => el.dispatchEvent(new PointerEvent(type, {pointerId: id, pointerType: 'touch', isPrimary: id === 1, bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y}));
              const cy = r.height / 2, cx = r.width / 2;
              ev('pointerdown', 1, cx - 40, cy); ev('pointerdown', 2, cx + 40, cy);
              ev('pointermove', 1, cx - 120, cy); ev('pointermove', 2, cx + 120, cy);
              ev('pointerup', 1, cx - 120, cy); ev('pointerup', 2, cx + 120, cy);
            }""")
            pg.wait_for_timeout(600)
            s6 = view(pg.evaluate(STATE))[0]
            check(tag + " pincer ×3", abs(s6 / s - 3) < 0.2, "×%.2f" % (s6 / s))
            # 7. glisser (déplacement) : le coin haut-gauche bouge
            vx0, vy0 = view(pg.evaluate(STATE))[1:3]
            pg.evaluate("""() => {
              const el = document.querySelector('#mv'); const r = el.getBoundingClientRect();
              const ev = (type, id, x, y) => el.dispatchEvent(new PointerEvent(type, {pointerId: id, pointerType: 'touch', isPrimary: true, bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y}));
              const cx = r.width / 2, cy = r.height / 2;
              ev('pointerdown', 11, cx, cy); for (let i = 1; i <= 8; i++) ev('pointermove', 11, cx + i * 8, cy + i * 6); ev('pointerup', 11, cx + 64, cy + 48);
            }""")
            pg.wait_for_timeout(500)
            vx1, vy1 = view(pg.evaluate(STATE))[1:3]
            check(tag + " glisser déplace la vue", abs(vx1 - vx0) > 1 and abs(vy1 - vy0) > 1, "(%.1f,%.1f)→(%.1f,%.1f)" % (vx0, vy0, vx1, vy1))
        ctx.close()
    b.close()
print("erreurs JS:", errs or "aucune")
print("OK %d  ÉCHECS %d" % (ok, fail))
sys.exit(1 if fail else 0)
