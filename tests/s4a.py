"""Fumée étape 4 : toutes les pages, sans erreur JS, avec le mode essai (mot secret) puis à des dates précises."""
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
errs = []
def ms(y, mo, d, h=12, mi=0, tz="Asia/Bangkok"): return datetime(y, mo, d, h, mi, 0, tzinfo=ZoneInfo(tz))
def newctx(b, vw=390, vh=844, when=None, init=None):
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR", timezone_id="Asia/Bangkok", service_workers="block")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
    pg.on("console", lambda m: errs.append("CONSOLE " + m.text) if m.type == "error" else None)
    if when: pg.clock.set_fixed_time(when)
    for i in (init or []): ctx.add_init_script(i)
    return ctx, pg
def go(pg, h): pg.evaluate("location.hash=%r" % h); pg.wait_for_timeout(300)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = newctx(b, when=ms(2026, 12, 22), init=["try{localStorage.setItem('carnet.who','Anne')}catch(e){}"])
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(600)
    print("home horoscope visible:", pg.is_visible("#hsd"), "|", pg.inner_text("#hsd-sub"))
    print(pg.inner_text("#hsd")[:400].replace("\n", " / "))
    pg.screenshot(path=OUT + "s4_home.png", full_page=True)
    for h in ["#/jeux", "#/defi", "#/mot-du-jour", "#/bingo", "#/gourmand", "#/prix", "#/quiz", "#/blind-test", "#/mots-meles", "#/horoscope", "#/passeport", "#/mascottes", "#/personnalite"]:
        go(pg, h)
        name = h[2:]
        v = pg.evaluate("(()=>{const m=[...document.querySelectorAll('main.view')].find(x=>!x.hidden);return m?m.id:null})()")
        lockvis = pg.is_visible(".view:not([hidden]) .lkv") if name not in ("jeux", "personnalite") else None
        print("%-16s -> %-12s lock=%s" % (h, v, lockvis))
        pg.screenshot(path=OUT + "s4_%s_locked.png" % name.replace("#", ""), full_page=True)
    print("ERRORS:", errs)
    b.close()
