from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, locale="fr-FR", service_workers="block")
    pg = ctx.new_page()
    pg.goto(BASE + "#/essai", wait_until="load"); pg.wait_for_timeout(500)
    pg.click("#sim-env-btn"); pg.wait_for_timeout(250)
    pg.fill("#env-in", "essai-demo-0000"); pg.click("#env-go"); pg.wait_for_timeout(900)
    t = pg.inner_text("#chut-txt")
    print(repr(t))
    print([hex(ord(c)) for c in t[:12]])
    b.close()
