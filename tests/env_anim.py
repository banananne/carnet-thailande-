from playwright.sync_api import sync_playwright
S="/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/ph/"
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={"width":390,"height":700},device_scale_factor=2,is_mobile=True,has_touch=True,service_workers="block",locale="fr-FR")
    pg=ctx.new_page(); pg.goto("http://127.0.0.1:8790/carnet-thailande-/#/previsualisation",wait_until="load"); pg.wait_for_timeout(1500)
    el=pg.locator("#pvx-env"); el.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
    box=pg.locator("#pvx-env").bounding_box()
    clip={"x":0,"y":max(0,box["y"]-110),"width":390,"height":330}
    pg.screenshot(path=S+"an0.png",clip=clip)
    el.click()
    for i,t in enumerate([150,200,250,300,500]):
        pg.wait_for_timeout(t); pg.screenshot(path=S+"an%d.png"%(i+1),clip={"x":0,"y":max(0,pg.locator("#pvx-env").bounding_box()["y"]-110),"width":390,"height":330})
    b.close()
