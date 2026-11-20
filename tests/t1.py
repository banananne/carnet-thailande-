import json, sys, time
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 402, "height": 714}, device_scale_factor=2, is_mobile=True, has_touch=True,
                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.7 Mobile/15E148 Safari/604.1",
                        locale="fr-FR", timezone_id="Europe/Paris")
    pg = ctx.new_page()
    logs = []
    pg.on("console", lambda m: logs.append((m.type, m.text)))
    pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
    pg.on("requestfailed", lambda r: logs.append(("requestfailed", r.url)))
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(600)
    def shot(name, full=False):
        pg.screenshot(path=OUT + name + ".png", full_page=full)
    def overflow(tag):
        r = pg.evaluate("() => [document.documentElement.scrollWidth, innerWidth, document.body.scrollWidth]")
        print(tag, "scrollWidth/innerWidth/body:", r)
    shot("home_top"); overflow("home")
    pg.evaluate("window.scrollTo(0, 99999)"); pg.wait_for_timeout(200); shot("home_bottom")
    print("home height", pg.evaluate("document.documentElement.scrollHeight"))
    for route in ["#/jours/2026-12-19", "#/jours/2026-12-20", "#/jours/2026-12-26", "#/jours/2026-12-28", "#/jours/2026-12-30", "#/jours/2027-01-03", "#/hotels", "#/utile"]:
        pg.evaluate("r => { location.hash = r }", route); pg.wait_for_timeout(350)
        name = route.replace("#/", "").replace("/", "_")
        shot(name, full=True); overflow(route)
    print("LOGS:", logs)
    b.close()
