import json
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(BASE); pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % json.dumps({"d": ["2026-12-24", "2026-12-26", "2027-01-01"], "b": []}))
    for d in ("2026-12-24", "2026-12-26", "2027-01-01", "2026-12-20"):
        pg.evaluate("location.hash='#/jours/%s'" % d); pg.reload(); pg.wait_for_timeout(500)
        pg.add_style_tag(content=".nav{display:none!important}")
        el = pg.locator("#d-%s .dstamp" % d)
        el.scroll_into_view_if_needed(); pg.wait_for_timeout(150)
        el.screenshot(path=OUT + "st_day_%s.png" % d)
        print(d, "tampon visible:", pg.locator("#d-%s .dstamp-svg svg" % d).count(), "| bouton:", pg.inner_text("#d-%s .dstamp button" % d).strip())
    # tamponner un jour au clic puis voir l'animation finale
    pg.evaluate("location.hash='#/jours/2026-12-20'"); pg.wait_for_timeout(300)
    pg.click("#d-2026-12-20 [data-stamp-day]"); pg.wait_for_timeout(900)
    print("après clic :", pg.locator("#d-2026-12-20 .dstamp-svg svg").count(), "| toast:", pg.inner_text("#toast").strip())
    pg.locator("#d-2026-12-20 .dstamp").screenshot(path=OUT + "st_day_after_click.png")
    ctx.close(); b.close()
print("erreurs JS:", errs or "aucune")
