from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 402, "height": 714}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR")
    pg = ctx.new_page()
    pg.goto(URL, wait_until="load"); pg.wait_for_timeout(500)
    pg.evaluate("window.scrollTo(0, 560)"); pg.wait_for_timeout(200)
    pg.screenshot(path=OUT + "home_mid.png")
    b.close()
