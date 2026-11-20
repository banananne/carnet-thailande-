import json
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block")
    pg = ctx.new_page()
    ctx.add_init_script("try{localStorage.setItem('carnet.open','1')}catch(e){}")  # le test de personnalité est ouvert (cadenas levé)
    pg.goto(BASE); pg.wait_for_timeout(400)
    def go(h, w=350):
        pg.evaluate("location.hash=%r" % h); pg.wait_for_timeout(w)
    pg.evaluate("localStorage.setItem('carnet.who','Anne')")
    pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % json.dumps({"d": ["2026-12-18", "2026-12-19", "2026-12-20", "2026-12-21", "2026-12-22", "2026-12-23", "2026-12-24"], "b": ["quiz", "doudou"]}))
    pg.evaluate("localStorage.setItem('carnet.blind', %r)" % json.dumps({"Arthur": 3, "Daphne": 5, "Flo": 2, "Anne": 4}))
    pg.evaluate("localStorage.setItem('carnet.mots', 'BAHT,AVION,BANPHE,GECKO,TEMPLE,MASSAGE,CURRY')")
    pg.reload(); pg.wait_for_timeout(500)
    go("#/jeux"); pg.screenshot(path=OUT + "pv_1_jeux.png")
    go("#/quiz"); pg.click('[data-qz="start"]'); pg.wait_for_timeout(150)
    pg.locator(".qz-q").nth(0).locator(".qz-o").nth(1).click(); pg.wait_for_timeout(250); pg.screenshot(path=OUT + "pv_2_quiz.png")
    go("#/personnalite"); pg.click('[data-dt="start"]'); pg.wait_for_timeout(120)
    for i in range(10):
        pg.locator(".dt-q").nth(i).locator('.qz-o[data-who="boop"]').click(); pg.wait_for_timeout(40)
    pg.wait_for_timeout(3200); pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(200); pg.screenshot(path=OUT + "pv_3_test.png")
    go("#/blind-test"); pg.wait_for_timeout(200); pg.screenshot(path=OUT + "pv_4_blind.png")
    go("#/mots-meles", 500); pg.screenshot(path=OUT + "pv_5_mots.png")
    go("#/passeport", 600); pg.screenshot(path=OUT + "pv_6_passeport.png")
    b.close()
print("ok")
