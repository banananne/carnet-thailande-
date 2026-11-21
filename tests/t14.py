import json, re, math
from playwright.sync_api import sync_playwright
BASE="http://localhost:8765/carnet-thailande-/"
OUT="/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
M=json.load(open("/home/claude/site_en_ligne/data_motsmeles.json",encoding="utf-8"))
W={w["k"]:w for w in M["words"]}
errs=[]; fails=[]; n=[0]
def ok(cond, msg):
    n[0]+=1
    if not cond: fails.append(msg); print("ÉCHEC:", msg)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True,service_workers="block")
    ctx.add_init_script("try{localStorage.setItem('carnet.open','1')}catch(e){}")  # les jeux sont tous ouverts (mot secret déjà tapé)
    pg=ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(BASE+"#/mots-meles"); pg.wait_for_timeout(500)
    def geo():
        return pg.evaluate("(()=>{const r=document.querySelector('#mm-board').getBoundingClientRect();return {l:r.left,t:r.top,w:r.width}})()")
    def center(r,c,dx=0,dy=0):
        g=geo(); cw=g["w"]/20
        return g["l"]+(c+.5+dx)*cw, g["t"]+(r+.5+dy)*cw
    def to_view(r):
        # fait défiler pour que la ligne r soit visible
        g=geo(); cw=g["w"]/20; y=g["t"]+(r+.5)*cw
        if y<120 or y>pg.viewport_size["height"]-120:
            pg.evaluate("window.scrollBy(0,%f)"%(y-pg.viewport_size["height"]/2)); pg.wait_for_timeout(80)
    def drag(r0,c0,r1,c1,dx1=0,dy1=0):
        to_view((r0+r1)/2)
        x0,y0=center(r0,c0); x1,y1=center(r1,c1,dx1,dy1)
        pg.mouse.move(x0,y0); pg.mouse.down(); pg.mouse.move((x0+x1)/2,(y0+y1)/2,steps=4); pg.mouse.move(x1,y1,steps=4); pg.mouse.up(); pg.wait_for_timeout(60)
    def tap(r,c):
        to_view(r); x,y=center(r,c); pg.mouse.click(x,y); pg.wait_for_timeout(60)
    def end(w): return w["r"]+(len(w["k"])-1)*w["dr"], w["c"]+(len(w["k"])-1)*w["dc"]
    def count(): return int(pg.inner_text("#mm-count"))
    ok(count()==0, "départ à 0")
    pg.screenshot(path=OUT+"s3_mots_start.png")
    # 1) glisser BAHT (diagonale)
    w=W["BAHT"]; e=end(w); drag(w["r"],w["c"],e[0],e[1]); ok(count()==1,"BAHT trouvé (diagonale)")
    pg.screenshot(path=OUT+"s3_mots_one.png")
    # 2) à l'envers : AVION de la fin vers le début
    w=W["AVION"]; e=end(w); drag(e[0],e[1],w["r"],w["c"]); ok(count()==2,"AVION trouvé à l'envers")
    # 3) fin du doigt un peu de travers : BANPHE (horizontal) avec dy=+0.45
    w=W["BANPHE"]; e=end(w); drag(w["r"],w["c"],e[0],e[1],0,0.45); ok(count()==3,"BANPHE trouvé avec doigt de travers")
    # 4) toucher-toucher : GECKO
    w=W["GECKO"]; e=end(w); tap(w["r"],w["c"]); ok("touche la dernière lettre" in pg.inner_text("#mm-live"),"message 1re lettre : "+pg.inner_text("#mm-live")); tap(e[0],e[1]); ok(count()==4,"GECKO trouvé en toucher-toucher")
    # 5) mauvaise sélection
    drag(0,0,0,3); ok(count()==4,"mauvaise sélection ignorée"); t=pg.inner_text("#mm-live"); ok("pas dans la liste" in t,"message erreur : "+t)
    # 6) indice
    pg.click("#mm-hint"); pg.wait_for_timeout(100); ok(pg.locator("#mm-ref circle").count()==1,"indice affiché"); print("indice:", pg.inner_text("#mm-live"))
    # 7) persistance
    pg.reload(); pg.wait_for_timeout(500); ok(count()==4,"4 mots gardés après rechargement")
    ok(pg.locator("#mm-found line").count()==4,"4 capsules redessinées")
    ok(pg.locator("#mm-words li.found").count()==4,"4 pastilles barrées")
    pg.screenshot(path=OUT+"s3_mots_four.png")
    # 8) zoom + toucher-toucher dans la grille agrandie
    pg.click("#mm-zoom"); pg.wait_for_timeout(150)
    gz=geo(); ok(abs(gz["w"]-640)<2, "grille agrandie à 640 px : %.0f"%gz["w"])
    w=W["TEMPLE"]; e=end(w)
    def tapz(r,c):
        pg.evaluate("""([r,c])=>{const b=document.querySelector('#mm-board'),cw=b.getBoundingClientRect().width/20,s=document.querySelector('#mm-scroll');
           const x=(c+.5)*cw, y=(r+.5)*cw; s.scrollLeft=Math.max(0,x-s.clientWidth/2); s.scrollTop=Math.max(0,y-s.clientHeight/2);}""",[r,c]); pg.wait_for_timeout(80)
        x,y=center(r,c); pg.mouse.click(x,y); pg.wait_for_timeout(60)
    # il faut amener la grille à l'écran
    pg.evaluate("document.querySelector('#mm-card').scrollIntoView({block:'center'})"); pg.wait_for_timeout(100)
    tapz(w["r"],w["c"]); tapz(e[0],e[1]); ok(count()==5,"TEMPLE trouvé dans la grille agrandie")
    pg.screenshot(path=OUT+"s3_mots_zoom.png")
    pg.click("#mm-zoom"); pg.wait_for_timeout(100)
    # 9) reset en deux touches
    pg.click("#mm-reset"); ok(count()==5,"1re touche : rien n'est effacé"); pg.click("#mm-reset"); pg.wait_for_timeout(100); ok(count()==0,"reset"); ok(pg.locator("#mm-found line").count()==0,"capsules effacées")
    # 10) tout trouver
    for k,w in W.items():
        e=end(w); drag(w["r"],w["c"],e[0],e[1]) if (hash(k)%2) else drag(e[0],e[1],w["r"],w["c"])
    ok(count()==40, "40 mots trouvés (obtenu %d)"%count())
    pg.wait_for_timeout(900)
    st=json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')")); ok("mots" in st["b"],"tampon mots mêlés")
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT+"s3_mots_all.png")
    b.close()
print("\n%d vérifications, %d échecs"%(n[0],len(fails)))
print("ERREURS JS:", errs if errs else "aucune")
