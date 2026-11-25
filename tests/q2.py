from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, locale="fr-FR", service_workers="block")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: print("PAGEERROR", e, "\nSTACK", getattr(e, "stack", None)))
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(600)
    b.close()
