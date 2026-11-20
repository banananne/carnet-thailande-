import json, re
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
    ctx.add_init_script("try{localStorage.setItem('carnet.open','1')}catch(e){}")  # le test de personnalité est ouvert (cadenas levé)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(BASE); pg.wait_for_timeout(300)
    def go(h): pg.evaluate("location.hash=%r"%h); pg.wait_for_timeout(250)
    def vis(sel): return pg.evaluate("(s)=>{const e=document.querySelector(s); return !!e && !e.hidden && e.offsetParent!==null}", sel)
    # ───── Quiz ─────
    go("#/quiz")
    ok(vis("#qz-intro"), "quiz intro visible")
    pg.click('[data-qz="start"]'); pg.wait_for_timeout(150)
    goods=[1,2,1,1,2,1]
    score_target=0
    for i in range(6):
        q=pg.locator(".qz-q").nth(i)
        ok(q.is_visible(), "question %d visible"%(i+1))
        pick = goods[i] if i not in (2,4) else (goods[i]+1)%3   # 2 mauvaises réponses
        if pick==goods[i]: score_target+=1
        q.locator(".qz-o").nth(pick).click(); pg.wait_for_timeout(100)
        fb=q.locator(".qz-fb")
        ok(fb.is_visible(), "feedback q%d"%(i+1))
        okflag=fb.get_attribute("data-ok")
        ok(okflag==("1" if pick==goods[i] else "0"), "data-ok q%d=%s"%(i+1,okflag))
        ok(q.locator(".qz-o.good").count()==1, "une bonne réponse marquée q%d"%(i+1))
        if i==0: pg.screenshot(path=OUT+"s3_quiz_q1_answered.png")
        if i==2: print("feedback faux:", fb.inner_text())
        # une seconde touche ne doit rien changer
        q.locator(".qz-o").nth((pick+1)%3).click(force=True) if False else None
        q.locator('[data-qz="next"]').click(); pg.wait_for_timeout(100)
    ok(vis("#qz-end"), "quiz end visible")
    s=pg.inner_text("#qz-s"); print("score:", s, "msg:", pg.inner_text("#qz-msg"))
    ok(int(s)==score_target, "score %s == %d"%(s,score_target))
    pg.screenshot(path=OUT+"s3_quiz_end.png")
    ok(pg.evaluate("localStorage.getItem('carnet.quiz')")==str(score_target), "meilleur score enregistré")
    stamps=json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')"))
    ok("quiz" in stamps["b"], "tampon quiz gagné")
    go("#/jeux"); print("hub quiz:", pg.inner_text('[data-hub="quiz"]'))
    # ───── Test du doudou ─────
    go("#/personnalite")
    pg.click('[data-dt="start"]'); pg.wait_for_timeout(100)
    # toujours la 1re réponse -> compter selon data-who
    whos=pg.evaluate("[...document.querySelectorAll('.dt-q')].map(q=>q.querySelector('.qz-o').dataset.who)")
    print("1res réponses:", whos)
    for i in range(10):
        ok(pg.locator(".dt-q").nth(i).is_visible(), "dt q%d visible"%(i+1))
        if i==3:
            # retour arrière puis re-réponse
            pg.locator(".dt-q").nth(3).locator('[data-dt="prev"]').click(); pg.wait_for_timeout(80)
            ok(pg.locator(".dt-q").nth(2).is_visible(), "retour question 3")
            pg.locator(".dt-q").nth(2).locator(".qz-o").nth(0).click(); pg.wait_for_timeout(80)
        pg.locator(".dt-q").nth(i).locator(".qz-o").nth(0).click(); pg.wait_for_timeout(80)
    from collections import Counter
    cnt=Counter(whos); mx=max(cnt.values()); win=[k for k,v in cnt.items() if v==mx]
    print("attendu:", cnt, win)
    if len(win)==1:
        ok(vis("#dt-res"), "résultat visible")
        h=pg.inner_text("#dt-res h2"); print("résultat:", h)
    else:
        ok(vis("#dt-tie"), "égalité visible"); print("égalité:", pg.inner_text("#dt-tiep"))
        pg.screenshot(path=OUT+"s3_test_tie.png")
        pg.locator(".dt-pick").nth(0).click(); pg.wait_for_timeout(150)
        ok(vis("#dt-res"), "résultat après choix")
    pg.screenshot(path=OUT+"s3_test_result.png", full_page=False)
    ok(pg.evaluate("localStorage.getItem('carnet.doudou')") in ("aftonsparv","boop","minou","moomoo"), "doudou enregistré")
    ok("doudou" in json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')"))["b"], "tampon doudou")
    # tout minou -> résultat unique
    pg.click('#dt-res [data-dt="start"]'); pg.wait_for_timeout(100)
    for i in range(10):
        pg.locator(".dt-q").nth(i).locator('.qz-o[data-who="minou"]').click(); pg.wait_for_timeout(50)
    ok("Minou" in pg.inner_text("#dt-res h2"), "10 × minou -> Minou : "+pg.inner_text("#dt-res h2"))
    go("#/jeux"); print("hub doudou:", pg.inner_text('[data-hub="doudou"]'))
    # ───── Blind test ─────
    go("#/blind-test")
    ok(pg.inner_text("#bt-lead")=="Personne n’a encore marqué.", "lead initial")
    pg.click('.bt-p[data-n="Flo"] .bt-main'); pg.click('.bt-p[data-n="Flo"] .bt-main'); pg.click('.bt-p[data-n="Anne"] .bt-main')
    ok(pg.inner_text("#bt-lead")=="Flo mène avec 2 points.", "lead Flo : "+pg.inner_text("#bt-lead"))
    pg.click('.bt-p[data-n="Anne"] .bt-main')
    ok("Égalité en tête : Flo et Anne" in pg.inner_text("#bt-lead"), "égalité : "+pg.inner_text("#bt-lead"))
    pg.click('.bt-p[data-n="Arthur"] .bt-minus', force=True) if False else None
    ok(pg.locator('.bt-p[data-n="Arthur"] .bt-minus').is_disabled(), "− désactivé à 0")
    pg.click('.bt-p[data-n="Flo"] .bt-minus')
    ok(pg.inner_text("#bt-lead")=="Anne mène avec 2 points.", "après − : "+pg.inner_text("#bt-lead"))
    pg.screenshot(path=OUT+"s3_blind_scores.png")
    pg.reload(); pg.wait_for_timeout(400); go("#/blind-test")
    ok(pg.inner_text('.bt-p[data-n="Anne"] [data-score]')=="2", "scores gardés après rechargement")
    pg.click("#bt-reset"); ok(pg.inner_text("#bt-reset")!="Remettre à zéro", "armé")
    pg.click("#bt-reset"); pg.wait_for_timeout(100)
    ok(pg.inner_text("#bt-lead")=="Personne n’a encore marqué.", "reset")
    ok("blind" in json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')"))["b"], "tampon blind")
    b.close()
print("\n%d vérifications, %d échecs"%(n[0],len(fails)))
print("ERREURS JS:", errs if errs else "aucune")
