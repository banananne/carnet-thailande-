"""Captures du passeport sur téléphone (barre du bas masquée) : à moitié rempli et vide."""
import json
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
DAYS = ["2026-12-18","2026-12-19","2026-12-20","2026-12-21","2026-12-22","2026-12-23","2026-12-24","2026-12-25","2026-12-26","2026-12-27","2026-12-28","2026-12-29","2026-12-30","2026-12-31","2027-01-01","2027-01-02","2027-01-03"]
HALF = json.dumps({"d": DAYS[1:3] + DAYS[4:5] + DAYS[7:8] + DAYS[9:10], "b": ["quiz", "mots"]})
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(BASE)
    for name, val in (("half", HALF), ("empty", None)):
        if val: pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % val)
        else: pg.evaluate("localStorage.removeItem('carnet.stamps')")
        pg.reload(); pg.wait_for_timeout(400); pg.evaluate("location.hash='#/passeport'"); pg.wait_for_timeout(500)
        pg.add_style_tag(content=".nav{display:none!important}")
        pg.screenshot(path=OUT + "ph_%s.png" % name, full_page=True)
    ctx.close(); b.close()
print("erreurs JS:", errs or "aucune")
