import sys
from playwright.sync_api import sync_playwright
URL = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, locale="fr-FR")
    pg = ctx.new_page()
    logs = []
    pg.on("console", lambda m: logs.append((m.type, m.text[:150])))
    pg.goto(URL, wait_until="load"); pg.wait_for_timeout(1500)
    pg.evaluate("navigator.serviceWorker.ready.then(() => 1)"); pg.wait_for_timeout(1500)
    pg.reload(wait_until="load"); pg.wait_for_timeout(800)
    print("controller:", pg.evaluate("!!navigator.serviceWorker.controller"))
    ctx.set_offline(True)
    try:
        pg.reload(wait_until="load", timeout=15000); pg.wait_for_timeout(800)
        print("offline reload OK ->", pg.url, "|", pg.title(), "|", pg.inner_text("body")[:120].replace("\n", " "))
    except Exception as e:
        print("offline reload ERREUR:", str(e)[:200])
    ctx.set_offline(False)
    print(logs[:5])
    b.close()
