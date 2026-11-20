"""Pages de jour : les tampons à texte courbé (round, scallop) s'affichent-ils quand le passeport est caché ?"""
import json
from playwright.sync_api import sync_playwright
from PIL import Image
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
DAYS = ["2026-12-19", "2026-12-25", "2026-12-30", "2027-01-03"]
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(BASE); pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % json.dumps({"d": DAYS, "b": []}))
    shots = []
    for d in DAYS:
        pg.evaluate("location.hash='#/jours/%s'" % d); pg.reload(); pg.wait_for_timeout(500)
        pg.add_style_tag(content=".nav{display:none!important}")
        el = pg.locator("#d-%s .dstamp" % d); el.scroll_into_view_if_needed(); pg.wait_for_timeout(150)
        f = OUT + "st_dayarc_%s.png" % d; el.screenshot(path=f); shots.append(f)
        # le texte courbé a-t-il une longueur calculée ? (textPath introuvable => 0)
        r = pg.evaluate("""(d)=>{const t=document.querySelector('#d-'+d+' .dstamp-svg textPath');if(!t)return null;const tx=t.parentNode;const bb=tx.getBBox();return {w:bb.width,h:bb.height,href:t.getAttribute('href'),len:tx.getComputedTextLength()}}""", d)
        print(d, r)
    ims = [Image.open(f) for f in shots]
    W = sum(i.width for i in ims); H = max(i.height for i in ims)
    sheet = Image.new("RGB", (W, H), (255, 252, 246)); x = 0
    for i in ims: sheet.paste(i, (x, 0)); x += i.width
    sheet.save(OUT + "st_dayarc_sheet.png")
    ctx.close(); b.close()
print("erreurs JS:", errs or "aucune")
