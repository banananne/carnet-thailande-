from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block")
    pg = ctx.new_page()
    pg.goto(BASE + "#/mots-meles"); pg.wait_for_timeout(600)
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(100)
    pg.evaluate("document.querySelector('#mm-words').scrollIntoView({block:'center'})"); pg.wait_for_timeout(200)
    print(pg.evaluate("""() => ({y: scrollY, max: document.documentElement.scrollHeight - innerHeight, sh: document.documentElement.scrollHeight, ih: innerHeight,
        words: (r => [Math.round(r.top), Math.round(r.bottom)])(document.querySelector('#mm-words').getBoundingClientRect())})"""))
    b.close()
