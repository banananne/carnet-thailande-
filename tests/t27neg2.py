import io, json
from PIL import Image
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
DAYS = ["2026-12-18","2026-12-19","2026-12-20","2026-12-21","2026-12-22","2026-12-23","2026-12-24","2026-12-25","2026-12-26","2026-12-27","2026-12-28","2026-12-29","2026-12-30","2026-12-31","2027-01-01","2027-01-02","2027-01-03"]
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
    pg = ctx.new_page(); pg.goto(BASE)
    pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % json.dumps({"d": DAYS, "b": []})); pg.reload(); pg.wait_for_timeout(400)
    pg.evaluate("location.hash='#/passeport'"); pg.wait_for_timeout(400); pg.add_style_tag(content=".nav{display:none!important}")
    i = 7
    sv = pg.locator("#v-pass .slot").nth(i).locator("svg.stamp"); sv.scroll_into_view_if_needed()
    print(pg.evaluate("(i)=>{const s=document.querySelectorAll('#v-pass .slot')[i];return s.dataset.id+' '+s.querySelector('svg.stamp').getAttribute('viewBox')}", i))
    pg.evaluate("(i)=>document.querySelectorAll('#v-pass .slot')[i].querySelector('svg.stamp').setAttribute('viewBox','12 12 96 96')", i)
    pg.wait_for_timeout(200)
    open("neg_scallop.png","wb").write(sv.screenshot())
    ctx.close(); b.close()
