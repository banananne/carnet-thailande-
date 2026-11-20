from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (390, 360, 320):
        ctx = b.new_context(viewport={"width": w, "height": 520}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR")
        pg = ctx.new_page()
        pg.goto(URL + "#/lexique", wait_until="load"); pg.wait_for_timeout(400)
        el = pg.locator(".pol")
        el.screenshot(path=OUT + "s2_pol_%d.png" % w)
        hs = pg.evaluate("Array.from(document.querySelectorAll('.pol .seg button')).map(b => Math.round(b.getBoundingClientRect().height))")
        print(w, "hauteurs des pastilles :", hs)
        if w == 390:
            pg.click("#v-lexique .num >> nth=4"); pg.wait_for_timeout(250)
            pg.screenshot(path=OUT + "s2_show_num.png")
        ctx.close()
    b.close()
