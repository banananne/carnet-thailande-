import time
from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 402, "height": 714}, device_scale_factor=3, is_mobile=True, has_touch=True, locale="fr-FR")
    pg = ctx.new_page()
    logs = []
    pg.on("console", lambda m: logs.append((m.type, m.text)))
    pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
    pg.goto(URL + "#/metro", wait_until="load")
    t0 = time.time()
    pg.wait_for_selector("#mv-stage svg", timeout=20000)
    pg.wait_for_timeout(400)
    print("svg ready after %.2fs" % (time.time() - t0))
    def state():
        return pg.evaluate("""() => { const s = document.querySelector('#mv-stage'); const v = s.querySelector('svg').getAttribute('viewBox');
            return {vb: v, tr: s.style.transform, w: s.style.width, h: s.style.height, box: JSON.stringify(document.querySelector('#mv').getBoundingClientRect())}; }""")
    print("fit:", state())
    pg.screenshot(path=OUT + "metro_fit.png")
    # zoom + bouton
    for i in range(3):
        pg.click(".mctl button[data-z=in]"); pg.wait_for_timeout(450)
    print("zoom x3 buttons:", state())
    pg.screenshot(path=OUT + "metro_zoom.png")
    # glisser (souris)
    box = pg.evaluate("JSON.parse(JSON.stringify(document.querySelector('#mv').getBoundingClientRect()))")
    cx, cy = box["x"] + box["width"]/2, box["y"] + box["height"]/2
    pg.mouse.move(cx, cy); pg.mouse.down(); pg.mouse.move(cx - 120, cy - 40, steps=8)
    print("during drag:", state()["tr"])
    pg.mouse.up(); pg.wait_for_timeout(400)
    print("after drag:", state())
    pg.screenshot(path=OUT + "metro_pan.png")
    # fit
    pg.click(".mctl button[data-z=fit]"); pg.wait_for_timeout(500)
    print("fit again:", state()["vb"])
    # pincer (événements synthétiques)
    r = pg.evaluate("""() => {
      const el = document.querySelector('#mv'); const r = el.getBoundingClientRect();
      const ev = (type, id, x, y) => el.dispatchEvent(new PointerEvent(type, {pointerId: id, pointerType: 'touch', isPrimary: id === 1, bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y}));
      const cy = r.height / 2;
      ev('pointerdown', 1, 150, cy); ev('pointerdown', 2, 250, cy);
      ev('pointermove', 1, 100, cy); ev('pointermove', 2, 300, cy);
      const tr = document.querySelector('#mv-stage').style.transform;
      ev('pointerup', 1, 100, cy); ev('pointerup', 2, 300, cy);
      return tr;
    }""")
    print("pinch transform (x2 expected):", r)
    pg.wait_for_timeout(500)
    print("after pinch:", state()["vb"])
    # double-tap
    pg.click(".mctl button[data-z=fit]"); pg.wait_for_timeout(500)
    pg.evaluate("""() => {
      const el = document.querySelector('#mv'); const r = el.getBoundingClientRect();
      const ev = (type, id, x, y) => el.dispatchEvent(new PointerEvent(type, {pointerId: id, pointerType: 'touch', isPrimary: true, bubbles: true, cancelable: true, clientX: r.left + x, clientY: r.top + y}));
      ev('pointerdown', 7, 200, 250); ev('pointerup', 7, 200, 250);
      ev('pointerdown', 8, 203, 252); ev('pointerup', 8, 203, 252);
    }""")
    pg.wait_for_timeout(600)
    print("after double tap:", state()["vb"])
    pg.screenshot(path=OUT + "metro_dtap.png")
    # mesure : coût d'un re-dessin complet (2 rAF) au zoom courant
    ms = pg.evaluate("""() => new Promise(res => {
      const svg = document.querySelector('#mv-stage svg'); const vb = svg.getAttribute('viewBox').split(' ').map(Number);
      const out = [];
      let i = 0;
      const step = () => {
        const t = performance.now();
        svg.setAttribute('viewBox', (vb[0] + i * 0.3) + ' ' + vb[1] + ' ' + vb[2] + ' ' + vb[3]);
        requestAnimationFrame(() => requestAnimationFrame(() => { out.push(performance.now() - t); i++; if (i < 8) step(); else res(out); }));
      };
      step();
    })""")
    print("redraw ms (2 rAF):", [round(x) for x in ms])
    errs = [l for l in logs if l[0] in ("error","pageerror")]; print("ERRORS:", len(errs), errs[:3]); print("OTHER LOGS:", [l for l in logs if l[0] not in ("error","pageerror")][:5])
    b.close()
