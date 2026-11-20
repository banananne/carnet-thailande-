import sys, json
from playwright.sync_api import sync_playwright
BASE="http://localhost:8765/carnet-thailande-/"
OUT="/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True,service_workers="block")
    pg=ctx.new_page()
    pg.on("console", lambda m: errs.append(("console",m.type,m.text)) if m.type in ("error","warning") else None)
    pg.on("pageerror", lambda e: errs.append(("pageerror",str(e))))
    pg.goto(BASE); pg.wait_for_timeout(800)
    pg.screenshot(path=OUT+"s3_home_top.png")
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT+"s3_home_bottom.png")
    for name,h in [("jeux","#/jeux"),("quiz","#/quiz"),("test","#/personnalite"),("doudous","#/mascottes"),("blind","#/blind-test"),("mots","#/mots-meles"),("horo","#/horoscope"),("pass","#/passeport")]:
        pg.evaluate("location.hash=%r"%h); pg.wait_for_timeout(500)
        vis = pg.evaluate("[...document.querySelectorAll('.view')].filter(v=>!v.hidden).map(v=>v.id)")
        print(name, vis, pg.evaluate("document.title"))
        pg.screenshot(path=OUT+"s3_%s.png"%name, full_page=(name in ("doudous","horo","pass","mots")))
    pg.evaluate("location.hash='#/jours/2026-12-26'"); pg.wait_for_timeout(500)
    pg.screenshot(path=OUT+"s3_day26.png", full_page=True)
    pg.evaluate("location.hash='#/jours/2026-12-19'"); pg.wait_for_timeout(500)
    pg.screenshot(path=OUT+"s3_day19.png", full_page=True)
    b.close()
print("ERREURS:", json.dumps(errs, ensure_ascii=False, indent=1) if errs else "aucune")
