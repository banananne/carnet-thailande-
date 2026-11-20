"""Planche des tampons : passeport plein (390 px) + chaque tampon en grand."""
import json, sys
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
DAYS = ["2026-12-18","2026-12-19","2026-12-20","2026-12-21","2026-12-22","2026-12-23","2026-12-24","2026-12-25","2026-12-26","2026-12-27","2026-12-28","2026-12-29","2026-12-30","2026-12-31","2027-01-01","2027-01-02","2027-01-03"]
FULL = json.dumps({"d": DAYS, "b": ["quiz", "doudou", "mots", "blind", "etoiles", "photos"]})
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in (390, 320):
        ctx = b.new_context(viewport={"width": vw, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(BASE); pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % FULL); pg.evaluate("location.hash='#/passeport'"); pg.reload(); pg.wait_for_timeout(500)
        pg.evaluate("location.hash='#/passeport'"); pg.wait_for_timeout(500)
        pg.screenshot(path=OUT + "st_pass_%d.png" % vw, full_page=True)
        HALF = json.dumps({"d": DAYS[:5] + DAYS[7:8], "b": ["quiz", "mots"]})
        pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % HALF); pg.reload(); pg.wait_for_timeout(400); pg.evaluate("location.hash='#/passeport'"); pg.wait_for_timeout(400)
        pg.screenshot(path=OUT + "st_half_%d.png" % vw, full_page=True)
        pg.evaluate("localStorage.removeItem('carnet.stamps')"); pg.reload(); pg.wait_for_timeout(400); pg.evaluate("location.hash='#/passeport'"); pg.wait_for_timeout(400)
        pg.screenshot(path=OUT + "st_empty_%d.png" % vw, full_page=True)
        pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % FULL); pg.reload(); pg.wait_for_timeout(400)
        if vw == 390:
            # chaque tampon à l'échelle 3 (pour juger les détails) puis planche
            ctx2 = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True, service_workers="block")
            pg2 = ctx2.new_page(); pg2.goto(BASE); pg2.evaluate("localStorage.setItem('carnet.stamps', %r)" % FULL); pg2.evaluate("location.hash='#/passeport'"); pg2.reload(); pg2.wait_for_timeout(500)
            pg2.evaluate("location.hash='#/passeport'"); pg2.wait_for_timeout(400)
            pg2.add_style_tag(content=".nav{display:none!important}")
            slots = pg2.locator("#v-pass .slot")
            for i in range(slots.count()):
                slots.nth(i).scroll_into_view_if_needed(); pg2.wait_for_timeout(60)
                slots.nth(i).screenshot(path=OUT + "st_one_%02d.png" % i)
            ctx2.close()
        ctx.close()
    b.close()
print("erreurs JS:", errs or "aucune")
