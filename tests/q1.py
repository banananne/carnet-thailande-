from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: print("PAGEERROR", e))
    pg.on("console", lambda m: print("CONSOLE", m.type, m.text) if m.type in ("error", "warning") else None)
    pg.goto(BASE + "#/utile", wait_until="load"); pg.wait_for_timeout(600)
    print("hash", pg.evaluate("location.hash"))
    print("views visibles:", pg.evaluate("[...document.querySelectorAll('main.view')].filter(m=>!m.hidden).map(m=>m.id)"))
    t = pg.locator('#v-utile a.tile[href="#/traduire"]')
    print("count", t.count(), "bbox", t.bounding_box())
    print(pg.evaluate("""() => { const e = document.querySelector('#v-utile a.tile[href="#/traduire"]'); const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
      let p = e, chain = []; while (p && p.id !== 'v-utile') { const c = getComputedStyle(p); chain.push(p.tagName + '.' + p.className + ' d=' + c.display + ' v=' + c.visibility + ' h=' + p.hidden); p = p.parentElement; }
      return {display: cs.display, vis: cs.visibility, w: r.width, h: r.height, chain}; }"""))
    print(pg.evaluate("document.querySelector('#v-utile').innerHTML.slice(0, 1500)"))
    b.close()
