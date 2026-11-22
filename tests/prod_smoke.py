from playwright.sync_api import sync_playwright
BASE="http://127.0.0.1:8767/carnet-thailande-/"
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True,locale="fr-FR",service_workers="block"); pg=ctx.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m:errs.append(m.text) if m.type=="error" else None)
    pg.goto(BASE,wait_until="load"); pg.wait_for_timeout(600)
    print("essai absent:", pg.evaluate("!document.getElementById('v-essai')"))
    pg.evaluate("location.hash='#/essai'"); pg.wait_for_timeout(400)
    print("#/essai -> accueil:", pg.is_visible("#v-home"))
    views=pg.evaluate("[...document.querySelectorAll('main.view')].map(m=>m.id.slice(2))")
    bad=[]
    for v in views:
        pg.evaluate("h=>location.hash='#/'+h",v); pg.wait_for_timeout(150)
        if not pg.evaluate("v=>{var e=document.getElementById('v-'+v);return e&&!e.hidden}",v): bad.append(v)
    print(len(views),"vues, non affichées:",bad)
    print("erreurs JS:",errs[:3])
