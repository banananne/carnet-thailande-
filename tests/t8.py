from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
ROUTES = ["#/", "#/utile", "#/lexique", "#/taxi/h1", "#/taxi/h2", "#/taxi/h3", "#/taxi/h4", "#/convertisseur", "#/good-to-know", "#/hotels"]
bad = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in ((320, 640), (360, 740), (390, 844), (412, 915), (768, 1024)):
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, is_mobile=(w < 700), has_touch=True, locale="fr-FR")
        pg = ctx.new_page()
        for r in ROUTES:
            pg.goto(URL + r, wait_until="load"); pg.wait_for_timeout(250)
            if r == "#/good-to-know":
                for i in range(pg.locator("#v-gtk details.gb").count()):
                    pg.locator("#v-gtk details.gb").nth(i).locator("summary").click()
                pg.wait_for_timeout(150)
            if r == "#/convertisseur":
                pg.fill("#c-thb", "123456"); pg.wait_for_timeout(100)
            m = pg.evaluate("""() => {
              const de = document.documentElement, W = de.clientWidth;
              const over = [];
              document.querySelectorAll('body *').forEach(e => {
                if (e.closest('[hidden]')) return;
                const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed') return;
                const r = e.getBoundingClientRect(); if (r.width === 0 && r.height === 0) return;
                if (r.right > W + 1 || r.left < -1) over.push((e.tagName + '.' + (e.className && e.className.baseVal === undefined ? e.className : '')).slice(0, 60) + ' [' + Math.round(r.left) + ',' + Math.round(r.right) + ']');
              });
              return { sw: de.scrollWidth, cw: W, over: over.slice(0, 6) };
            }""")
            flag = m["sw"] > m["cw"] or m["over"]
            if flag:
                bad.append((w, r, m))
            print(("!! " if flag else "ok ") + "%d %-16s scrollWidth=%d clientWidth=%d %s" % (w, r, m["sw"], m["cw"], m["over"] if m["over"] else ""))
        ctx.close()
    b.close()
print("\nproblèmes :", len(bad))
