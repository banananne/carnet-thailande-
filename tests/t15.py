import json
from playwright.sync_api import sync_playwright
BASE="http://localhost:8765/carnet-thailande-/"
OUT="/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
errs=[]; fails=[]; n=[0]
def ok(cond, msg):
    n[0]+=1
    if not cond: fails.append(msg); print("ÉCHEC:", msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True,service_workers="block")
    pg=ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(BASE); pg.wait_for_timeout(400)
    def go(h): pg.evaluate("location.hash=%r"%h); pg.wait_for_timeout(250)
    def stamps(): return json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')") or '{"d":[],"b":[]}')
    # ── passeport : toucher une case
    go("#/passeport")
    pg.click('.slot[data-id="2026-12-19"]'); pg.wait_for_timeout(200)
    ok("2026-12-19" in stamps()["d"], "case 19 déc. tamponnée")
    ok(pg.locator('.slot[data-id="2026-12-19"].on').count()==1, "classe .on")
    ok(pg.inner_text("#pp-count")=="1", "compteur 1")
    print("toast:", pg.inner_text("#toast"))
    pg.click('.slot[data-id="2026-12-19"]'); ok("Déjà" in pg.inner_text("#toast"), "déjà tamponné")
    pg.click('.slot[data-id="quiz"]'); ok("À gagner" in pg.inner_text("#toast"), "à gagner : "+pg.inner_text("#toast"))
    pg.screenshot(path=OUT+"s3_pass_one.png")
    # ── page d'un jour : Tamponner ce jour
    go("#/jours/2026-12-20")
    btn=pg.locator('#d-2026-12-20 [data-stamp-day]'); ok(btn.is_visible(),"bouton tamponner visible")
    btn.click(); pg.wait_for_timeout(700)
    ok(not btn.is_visible(),"bouton caché après tampon")
    ok(pg.locator('#d-2026-12-20 .dstamp-svg svg.stamp').count()==1, "tampon affiché sur la page du jour")
    pg.locator('#d-2026-12-20 .dstamp').scroll_into_view_if_needed(); pg.wait_for_timeout(500)
    pg.screenshot(path=OUT+"s3_day_stamped.png")
    # ── photo -> tampon automatique
    for i,d in enumerate(["2026-12-21","2026-12-22","2026-12-23","2026-12-24","2026-12-25"]):
        go("#/jours/"+d)
        pg.set_input_files('#d-%s input[type=file] >> nth=1'%d, "test_photo_%d.jpg"%i)
        for _ in range(250):
            if d in stamps()["d"]: break
            pg.wait_for_timeout(20)
        ok(d in stamps()["d"], "tampon auto pour la photo du %s"%d)
    ok("photos" in stamps()["b"], "tampon spécial photographe (5 photos)")
    print("après 5 photos :", stamps())
    # ── horoscope : aller en bas
    go("#/horoscope"); pg.wait_for_timeout(300)
    ok("etoiles" not in stamps()["b"], "pas de tampon avant d'avoir lu")
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(800)
    ok("etoiles" in stamps()["b"], "tampon horoscope en bas de page")
    # ── mot du doudou
    go("#/")
    seen=set()
    for i in range(14):
        pg.click("#hq-btn"); pg.wait_for_timeout(60)
        seen.add(pg.inner_text("#hq-q"))
    ok(len(seen)>=6, "le mot change (%d différents)"%len(seen))
    ok(pg.get_attribute("#hq-img","src").startswith("img/doudou_"), "image du doudou")
    # ── hub : sous-titres
    go("#/jeux")
    print("hub passeport:", pg.inner_text('[data-hub="pass"]'))
    ok("sur 23" in pg.inner_text('[data-hub="pass"]'), "compteur passeport dans le hub")
    go("#/"); ok(pg.locator("[data-pass-count]").count() == 0, "l'accueil n'a plus la tuile Passeport (compteur dans le hub Jeux)")
    # ── passeport complet (via LS) + two-tap reset
    go("#/passeport")
    pg.click("#pp-reset"); ok("Sûr" in pg.inner_text("#pp-reset"), "reset armé"); pg.click("#pp-reset"); pg.wait_for_timeout(100)
    ok(stamps()=={"d":[],"b":[]}, "passeport vidé")
    ok(pg.locator('#d-2026-12-20 .dstamp-svg svg').count()==0, "tampon du jour retiré")
    pg.screenshot(path=OUT+"s3_pass_empty2.png")
    b.close()
print("\n%d vérifications, %d échecs"%(n[0],len(fails)))
print("ERREURS JS:", errs if errs else "aucune")
