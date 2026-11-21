# -*- coding: utf-8 -*-
"""Enveloppes secrètes, SIMULATION (#/essai) : code, serment (1 s), mission, mots de la vague 2, révélation, effacement, remise à zéro.
Faux téléphone 390×844 et 320×568. Les captures vont dans le dossier des tests pour être regardées."""
import sys, re, json
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
ok_n = fail_n = 0
errs = []
def check(name, cond, info=""):
    global ok_n, fail_n
    if cond: ok_n += 1
    else:
        fail_n += 1; print("  ✗", name, info)
def ms(y, mo, d, h, mi, s=0, tz="Asia/Bangkok"):
    return datetime(y, mo, d, h, mi, s, tzinfo=ZoneInfo(tz))
def sp(s): return s.replace("\u00a0", " ").replace("\u202f", " ")

def newctx(b, vw=390, vh=844, clock=None, init=None):
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2, is_mobile=vw < 700, has_touch=True, locale="fr-FR", timezone_id="Asia/Bangkok", service_workers="block")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    if init: pg.add_init_script(init)
    if clock is not None: pg.clock.install(time=clock)
    return ctx, pg

def go(pg, h):
    pg.evaluate("location.hash=%r" % h); pg.wait_for_timeout(250)
def vis(pg, sel): return pg.is_visible(sel)
def pane(pg):
    for p in ("code", "chut", "card", "sealed", "rev", "bad"):
        if pg.is_visible("#envp-" + p): return p
    return None
def ls(pg, k): return pg.evaluate("k => localStorage.getItem(k)", k)
def keys(pg, prefix): return pg.evaluate("p => Object.keys(localStorage).filter(k => k.indexOf(p) === 0)", prefix)
def hold(pg, ms_=1250, fake=False):
    bb = pg.locator("#env-hold").bounding_box()
    pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); pg.mouse.down()
    if fake: pg.clock.run_for(ms_)
    else: pg.wait_for_timeout(ms_)
    pg.mouse.up(); pg.wait_for_timeout(150)
def type_code(pg, code):
    pg.fill("#env-in", code); pg.click("#env-go"); pg.wait_for_timeout(900)
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth > innerWidth + 1")
def open_sim(pg):
    pg.click("#sim-env-btn"); pg.wait_for_timeout(250)

with sync_playwright() as p:
    b = p.chromium.launch()
    # ───── A. essai : le jour de la cacahuète se choisit, les jours futurs restent fermés ─────
    ctx, pg = newctx(b)
    pg.goto(BASE + "#/essai", wait_until="load"); pg.wait_for_timeout(500)
    check("A1 le choix du jour est visible pour le jeu 1", vis(pg, "#sim-day") and pg.locator("[data-sd]").count() == 4 and pg.get_attribute('[data-sd="0"]', "aria-pressed") == "true")
    pg.click('[data-sw="2"]'); pg.wait_for_timeout(100)
    check("A2 absent pour les autres jeux", not vis(pg, "#sim-day"))
    pg.click('[data-sw="1"]'); pg.wait_for_timeout(100)
    open_sim(pg); type_code(pg, "essai-0000"); hold(pg)
    check("A3 mardi 22 : 2 attentions seulement", pane(pg) == "card" and pg.locator("#card-items li.act").count() == 2 and pg.locator("#card-items li.env-day.off").count() == 3)
    txt = pg.inner_text("#card-items")
    check("A4 les attentions des jours suivants ne sont pas dans la page", "Remplis le verre" not in txt and "Laisse passer Litchi" not in txt and "Avant le dîner de Noël" not in txt, txt)
    pg.click("#env-x"); pg.wait_for_timeout(250)
    pg.click('[data-sd="2"]'); pg.wait_for_timeout(150)
    check("A5 jour choisi mémorisé", pg.get_attribute('[data-sd="2"]', "aria-pressed") == "true" and ls(pg, "carnet.sim.day") == "2")
    open_sim(pg); type_code(pg, "essai-0000"); hold(pg)
    check("A6 jeudi 24 : 6 attentions (22, 23, 24), le 25 fermé", pg.locator("#card-items li.act").count() == 6 and pg.locator("#card-items li.env-day.off").count() == 1 and "Avant le dîner de Noël" not in pg.inner_text("#card-items"))
    pg.click("#env-x"); pg.wait_for_timeout(250)
    pg.click('[data-sd="3"]'); pg.wait_for_timeout(150); open_sim(pg); type_code(pg, "essai-0000"); hold(pg)
    check("A7 vendredi 25 : 8 attentions", pg.locator("#card-items li.act").count() == 8 and pg.locator("#card-items li.env-day.off").count() == 0)
    pg.click("#env-x"); pg.wait_for_timeout(250)
    pg.click("#sim-reset"); pg.click("#sim-reset"); pg.wait_for_timeout(300)
    check("A8 remise à zéro : retour au mardi 22", pg.get_attribute('[data-sd="0"]', "aria-pressed") == "true" and ls(pg, "carnet.sim.day") is None)
    ctx.close()
    # ───── B. l'onglet Jeux : trois rubriques, rangées par ordre de parution ─────
    ctx, pg = newctx(b, clock=ms(2026, 12, 22, 10, 0))
    pg.goto(BASE + "#/jeux", wait_until="load"); pg.wait_for_timeout(500)
    heads = pg.evaluate("() => [...document.querySelectorAll('#v-jeux h2.sech')].map(e => e.textContent.trim())")
    check("B1 trois rubriques dans l'ordre", heads == ["À faire tous les jours", "Au fil des jours", "Les jeux du carnet"], heads)
    secs = pg.evaluate("() => [...document.querySelectorAll('#v-jeux .list')].map(l => [...l.querySelectorAll('a.tile, a[href]')].map(a => a.getAttribute('href')))")
    check("B2 à faire tous les jours : défi, mot, gourmand, passeport", secs[0] == ["#/defi", "#/mot-du-jour", "#/gourmand", "#/passeport"], secs[0])
    check("B3 au fil des jours : bingo, mascottes, prix (3 janvier en dernier)", secs[1] == ["#/bingo", "#/mascottes", "#/prix"], secs[1])
    check("B4 jeux du carnet : 18 déc. (blind test, mots mêlés, horoscope), quiz du 26, test du 29", secs[2] == ["#/blind-test", "#/mots-meles", "#/horoscope", "#/quiz", "#/personnalite"], secs[2])
    pg.screenshot(path=OUT + "jeux_rubriques.png", full_page=True)
    check("B5 pas de débordement", not overflow(pg))
    ctx.close()
    # ───── C. retour : depuis un jour, on revient au jour ─────
    ctx, pg = newctx(b, clock=ms(2026, 12, 22, 10, 0), init="localStorage.setItem('carnet.open','1')")
    pg.goto(BASE + "#/jours/2026-12-22", wait_until="load"); pg.wait_for_timeout(600)
    pg.click("#d-2026-12-22 .dfl"); pg.wait_for_timeout(400)
    check("C1 le défi du jour s'ouvre", vis(pg, "#v-defi") and pg.evaluate("location.hash").startswith("#/defi"))
    pg.click("#v-defi .vhead .back"); pg.wait_for_timeout(400)
    check("C2 « Retour » ramène à la page du jour (22 décembre), pas à l'accueil des jeux", vis(pg, "#v-days") and pg.evaluate("location.hash") == "#/jours/2026-12-22" and not vis(pg, "#v-jeux"), pg.evaluate("location.hash"))
    pg.evaluate("location.hash = '#/jeux'"); pg.wait_for_timeout(300)
    pg.click('#v-jeux a[href="#/defi"]'); pg.wait_for_timeout(400)
    pg.click("#v-defi .vhead .back"); pg.wait_for_timeout(400)
    check("C3 depuis l'onglet Jeux : « Retour » ramène aux jeux", vis(pg, "#v-jeux") and pg.evaluate("location.hash") == "#/jeux", pg.evaluate("location.hash"))
    pg.goto(BASE + "#/defi", wait_until="load"); pg.wait_for_timeout(400)
    pg.click("#v-defi .vhead .back"); pg.wait_for_timeout(400)
    check("C4 ouvert directement : « Retour » va aux jeux", vis(pg, "#v-jeux"), pg.evaluate("location.hash"))
    pg.evaluate("location.hash = '#/jours/2026-12-23'"); pg.wait_for_timeout(300)
    pg.click("#d-2026-12-23 .dfl"); pg.wait_for_timeout(300)
    pg.click("#v-defi .vhead .back"); pg.wait_for_timeout(400)
    check("C5 un autre jour : retour au 23", pg.evaluate("location.hash") == "#/jours/2026-12-23", pg.evaluate("location.hash"))
    ctx.close()
    # ───── D. le mot de Boop ─────
    # ───── E. la chanson du jour : une par page de jour, avec son code Spotify ─────
    ctx, pg = newctx(b, clock=ms(2026, 12, 21, 10, 0))
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(500)
    n = pg.evaluate("document.querySelectorAll('.day .song').length")
    check("E1 une chanson du jour sur chacune des 17 pages de jour", n == 17, n)
    exp = {"2026-12-18": "Holiday", "2026-12-24": "Last Christmas", "2026-12-27": "Bicycle Race", "2027-01-02": "One Night in Bangkok", "2027-01-03": "Beanie"}
    for day, ti in exp.items():
        t_ = pg.evaluate("d => document.querySelector('#d-' + d + ' .song-t b').textContent", day)
        check("E2 %s : %s" % (day, ti), t_ == ti, t_)
    pg.evaluate("location.hash = '#/jours/2026-12-26'"); pg.wait_for_timeout(500)
    pg.locator("#d-2026-12-26 .song").scroll_into_view_if_needed(); pg.wait_for_timeout(500)
    check("E3 images chargées (pochette et code)", pg.evaluate("[...document.querySelectorAll('#d-2026-12-26 .song img')].every(i => i.complete && i.naturalWidth > 10)"))
    check("E4 le code a un texte alternatif", "Code Spotify" in pg.get_attribute("#d-2026-12-26 .song-code", "alt"))
    check("E5 pas de débordement", not overflow(pg))
    ctx.close()
    page = open("/home/claude/site_en_ligne/web/index.html", encoding="utf-8").read()
    check("D1 « Hola que tal, ça boum les frères ? » est parmi les mots des mascottes", "Hola que tal, ça boum les frères ?" in page)

    print("errs:", errs)
    b.close()
print("t36 : %d OK, %d échec(s)" % (ok_n, fail_n)); sys.exit(1 if fail_n or errs else 0)
