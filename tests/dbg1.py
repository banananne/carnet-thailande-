from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, locale="fr-FR", timezone_id="Asia/Bangkok", service_workers="block")
    pg = ctx.new_page()
    logs = []
    pg.on("pageerror", lambda e: logs.append("PAGEERROR " + str(e)))
    pg.on("console", lambda m: logs.append(m.type + " " + m.text))
    pg.goto(BASE + "#/jeux", wait_until="load"); pg.wait_for_timeout(500)
    print(pg.evaluate("""() => ({cls: document.documentElement.className, open: localStorage.getItem('carnet.open'), now: new Date().toString(),
       dtopen: document.querySelector('#dt').getAttribute('data-open'), hasGames: typeof window.CarnetGames})"""))
    print(logs)
    b.close()
