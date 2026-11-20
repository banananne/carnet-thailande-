"""Contrôle négatif : le test de rognage détecte-t-il bien un tampon coupé ?"""
import io, json
from PIL import Image
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
DAYS = ["2026-12-18","2026-12-19","2026-12-20","2026-12-21","2026-12-22","2026-12-23","2026-12-24","2026-12-25","2026-12-26","2026-12-27","2026-12-28","2026-12-29","2026-12-30","2026-12-31","2027-01-01","2027-01-02","2027-01-03"]
def ring_ink(png):
    im = Image.open(io.BytesIO(png)).convert("RGB"); W, H = im.size; px = im.load()
    ring = [px[x, y] for x in range(W) for y in (0, H - 1)] + [px[x, y] for y in range(H) for x in (0, W - 1)]
    return sum(1 for c in ring if max(c) - min(c) > 45)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
    pg = ctx.new_page(); pg.goto(BASE)
    pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % json.dumps({"d": DAYS, "b": []})); pg.reload(); pg.wait_for_timeout(400)
    pg.evaluate("location.hash='#/passeport'"); pg.wait_for_timeout(400); pg.add_style_tag(content=".nav{display:none!important}")
    for i in (1, 7):
        sv = pg.locator("#v-pass .slot").nth(i).locator("svg.stamp"); sv.scroll_into_view_if_needed()
        a = ring_ink(sv.screenshot())
        pg.evaluate("(i)=>document.querySelectorAll('#v-pass .slot')[i].querySelector('svg.stamp').setAttribute('viewBox','12 12 96 96')", i)  # zoom : coupe volontairement
        c = ring_ink(sv.screenshot())
        print("case", i, "bord normal :", a, "px d'encre | viewBox resserré :", c, "px d'encre")
    ctx.close(); b.close()
