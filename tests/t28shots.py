from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block")
    pg = ctx.new_page()
    pg.goto(URL + "#/metro", wait_until="load")
    pg.wait_for_selector("#mv-stage svg", timeout=20000); pg.wait_for_timeout(600)
    pg.screenshot(path=OUT + "m28_page_fit.png")
    # zoom ×3 puis ×6 au centre
    for i in range(3):
        pg.click(".mctl button[data-z=in]"); pg.wait_for_timeout(450)
    pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + "m28_zoom3.png")
    for i in range(2):
        pg.click(".mctl button[data-z=in]"); pg.wait_for_timeout(450)
    pg.wait_for_timeout(400)
    pg.screenshot(path=OUT + "m28_zoom5.png")
    b.close()
