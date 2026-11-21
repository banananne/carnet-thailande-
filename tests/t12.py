import json
from playwright.sync_api import sync_playwright
BASE="http://localhost:8765/carnet-thailande-/"
OUT="/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
days=["2026-12-18","2026-12-19","2026-12-20","2026-12-21","2026-12-22","2026-12-23","2026-12-24","2026-12-25","2026-12-26","2026-12-27","2026-12-28","2026-12-29","2026-12-30","2026-12-31","2027-01-01","2027-01-02","2027-01-03"]
bon=["quiz","doudou","mots","blind","etoiles","photos"]
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True,service_workers="block")
    ctx.add_init_script("try{localStorage.setItem('carnet.open','1')}catch(e){}")  # les jeux sont tous ouverts (mot secret déjà tapé)
    pg=ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE); pg.wait_for_timeout(300)
    pg.evaluate("localStorage.setItem('carnet.stamps', JSON.stringify(%s))" % json.dumps({"d":days,"b":bon}))
    pg.goto(BASE+"#/passeport"); pg.reload(); pg.wait_for_timeout(700)
    pg.screenshot(path=OUT+"s3_pass_full.png", full_page=True)
    # zoom on slots
    el=pg.query_selector("#v-pass .pp-grid")
    el.screenshot(path=OUT+"s3_pass_grid1.png")
    els=pg.query_selector_all("#v-pass .pp-grid")
    els[1].screenshot(path=OUT+"s3_pass_grid2.png")
    b.close()
print(errs)
