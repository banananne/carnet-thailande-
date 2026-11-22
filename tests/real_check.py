# -*- coding: utf-8 -*-
"""Contrôle du VRAI jeu (silencieux : ne montre ni code ni texte, seulement des OK/KO)."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
CODES = json.load(open('/home/claude/prive/codes.json'))['codes']
BASE = "http://127.0.0.1:8767/carnet-thailande-/"
def at(y, mo, d, h, mi): return datetime(y, mo, d, h, mi, 0, tzinfo=ZoneInfo("Europe/Paris"))
def pane(pg):
    for p in ("code", "chut", "card", "sealed", "rev", "bad"):
        if pg.is_visible("#envp-" + p): return p
res = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for who in ("Arthur", "Daphne", "Flo", "Anne"):
        for w, t in (("w1", at(2026,12,23,10,0)), ("w2", at(2026,12,27,10,0)), ("w4", at(2026,12,28,10,0)), ("w3", at(2026,12,31,10,0))):
            ctx = b.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True, locale="fr-FR", timezone_id="Europe/Paris", service_workers="block")
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(1))
            pg.clock.set_fixed_time(t)
            pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(500)
            pg.click('#who button[data-n="%s"]' % who); pg.wait_for_timeout(900)
            ok = pg.is_visible("#env-btn")
            if ok:
                pg.click("#env-btn"); pg.wait_for_timeout(250)
                pg.fill("#env-in", CODES[who]); pg.click("#env-go"); pg.wait_for_timeout(1000)
                ok = pane(pg) == "chut"
                if ok:
                    bb = pg.locator("#env-hold").bounding_box()
                    pg.mouse.move(bb["x"]+bb["width"]/2, bb["y"]+bb["height"]/2); pg.mouse.down(); pg.wait_for_timeout(1300); pg.mouse.up(); pg.wait_for_timeout(300)
                    ok = pane(pg) == "card"
            res.append((who, w, ok and not errs))
            ctx.close()
print(sum(1 for r in res if r[2]), "/", len(res), "ouvertures réelles OK")
for r in res:
    if not r[2]: print("KO", r[0], r[1])
