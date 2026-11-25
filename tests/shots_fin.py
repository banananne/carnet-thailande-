# -*- coding: utf-8 -*-
"""Captures de la carte complète (fenêtre très haute) pour les trois vagues : contexte, mission, encadré de fin."""
import sys
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
W, H = int(sys.argv[1]) if len(sys.argv) > 1 else 390, int(sys.argv[2]) if len(sys.argv) > 2 else 1900
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (1, 2, 3):
        ctx = b.new_context(viewport={"width": W, "height": H}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR", timezone_id="Asia/Bangkok", service_workers="block")
        pg = ctx.new_page()
        pg.goto(BASE + "#/essai", wait_until="load"); pg.wait_for_timeout(400)
        pg.click('[data-sw="%d"]' % w); pg.wait_for_timeout(100)
        pg.click("#sim-env-btn"); pg.wait_for_timeout(250)
        pg.fill("#env-in", "essai-0000"); pg.click("#env-go"); pg.wait_for_timeout(1000)
        bb = pg.locator("#env-hold").bounding_box()
        pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); pg.mouse.down(); pg.wait_for_timeout(1250); pg.mouse.up(); pg.wait_for_timeout(300)
        pg.screenshot(path=OUT + "fin_w%d_%d.png" % (w, W))
        ctx.close()
    b.close()
print("ok")
