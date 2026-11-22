# -*- coding: utf-8 -*-
"""Invité·e : carte « En ce moment, là-bas » (heures de Bangkok et de Paris, jour du voyage, programme du jour)."""
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8767/carnet-thailande-/"
n_ok = n_ko = 0
def check(name, c, info=""):
    global n_ok, n_ko
    if c: n_ok += 1
    else: n_ko += 1; print("  ✗", name, info)
def at(y, mo, d, h, mi, tz="Europe/Paris"): return datetime(y, mo, d, h, mi, 0, tzinfo=ZoneInfo(tz))
sp = lambda s: s.replace(" ", " ").replace(" ", " ")
errs = []
def open_guest(b, t, tz="Europe/Paris", vw=390):
    ctx = b.new_context(viewport={"width": vw, "height": 844}, is_mobile=True, has_touch=True, locale="fr-FR", timezone_id=tz, service_workers="block")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.clock.set_fixed_time(t)
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(500)
    pg.click('#who button[data-n="Invité"]'); pg.wait_for_timeout(500)
    return ctx, pg
def txt(pg, sel): return sp(pg.inner_text(sel))
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg = open_guest(b, at(2026, 12, 1, 9, 0))
    check("A1 la carte est visible pour l'invité·e", pg.is_visible("#gnow") and "en ce moment, là-bas" in txt(pg, "#gnow").lower())
    check("A2 compte à rebours : 17 jours", txt(pg, "#gn-day") == "Départ dans 17 jours", txt(pg, "#gn-day"))
    check("A3 heures : Bangkok = Paris + 6 h (9 h → 15 h)", txt(pg, "#gn-par") == "09 h 00" and txt(pg, "#gn-bkk") == "15 h 00", (txt(pg, "#gn-par"), txt(pg, "#gn-bkk")))
    check("A4 pas de bouton avant le départ", not pg.is_visible("#gn-link"))
    check("A5 pas d'horoscope du jour ni d'enveloppe sur l'accueil invité", not pg.is_visible("#hsd") and not pg.is_visible("#env-btn"))
    pg.screenshot(path="t/gn_avant.png")
    # l'invité·e redevient Anne : la carte disparaît ; puis retour invité·e
    check("A5b le bloc « Qui es-tu ? » reste ouvert pour l'invité·e", pg.is_visible("#who-box"))
    pg.click('#who button[data-n="Anne"]'); pg.wait_for_timeout(1200)
    check("A6 un voyageur ne voit pas la carte", not pg.is_visible("#gnow"))
    pg.click('#who button[data-n="Invité"]'); pg.wait_for_timeout(700)
    check("A7 de retour en invité·e : la carte revient", pg.is_visible("#gnow"))
    ctx.close()
    ctx, pg = open_guest(b, at(2026, 12, 17, 10, 0))
    check("B1 la veille : « Départ demain »", txt(pg, "#gn-day") == "Départ demain", txt(pg, "#gn-day")); ctx.close()
    ctx, pg = open_guest(b, at(2026, 12, 18, 12, 0))
    check("C1 18 décembre : jour 1 sur 17", txt(pg, "#gn-day").startswith("Jour 1 sur 17 · Vendredi 18 décembre"), txt(pg, "#gn-day"))
    check("C2 programme du départ", "16 h 05" in txt(pg, "#gn-plan") and "Anne et Arthur" in txt(pg, "#gn-plan"), txt(pg, "#gn-plan"))
    check("C3 heures : 12 h Paris, 18 h Bangkok", txt(pg, "#gn-par") == "12 h 00" and txt(pg, "#gn-bkk") == "18 h 00")
    check("C4 bouton vers la page du jour", pg.is_visible("#gn-link") and pg.get_attribute("#gn-link", "href") == "#/jours/2026-12-18")
    pg.click("#gn-link"); pg.wait_for_timeout(500)
    check("C5 le bouton ouvre la page du 18 décembre", pg.evaluate("location.hash") == "#/jours/2026-12-18" and pg.is_visible("#d-2026-12-18"))
    ctx.close()
    # le jour est celui de Bangkok, pas celui du téléphone : 22 déc. 23 h 30 à Paris = 23 déc. 5 h 30 à Bangkok
    ctx, pg = open_guest(b, at(2026, 12, 22, 23, 30))
    check("D1 le jour suit Bangkok (jour 6, 23 décembre)", txt(pg, "#gn-day").startswith("Jour 6 sur 17 · Mercredi 23 décembre"), txt(pg, "#gn-day"))
    check("D2 programme du 23", "Grand Palais" in txt(pg, "#gn-plan")); ctx.close()
    ctx, pg = open_guest(b, at(2026, 12, 22, 12, 0, "America/New_York"), tz="America/New_York")
    check("D3 téléphone à New York : les heures restent celles de Bangkok et de Paris", txt(pg, "#gn-par") == "18 h 00" and txt(pg, "#gn-bkk") == "00 h 00", (txt(pg, "#gn-par"), txt(pg, "#gn-bkk"))); ctx.close()
    for (mo, d, y, h, label, key) in [(12, 26, 2026, 12, "26 déc.", "Sukhothaï"), (12, 31, 2026, 12, "31 déc.", "réveillon"), (1, 2, 2027, 10, "2 janv.", "Dernière"), (1, 3, 2027, 10, "3 janv.", "retour")]:
        ctx, pg = open_guest(b, at(y, mo, d, h, 0)); check("E %s : le programme du jour s'affiche" % label, key in txt(pg, "#gn-plan"), txt(pg, "#gn-plan")); ctx.close()
    ctx, pg = open_guest(b, at(2027, 1, 3, 10, 0)); check("E5 3 janvier : jour 17 sur 17", txt(pg, "#gn-day").startswith("Jour 17 sur 17"), txt(pg, "#gn-day")); ctx.close()
    ctx, pg = open_guest(b, at(2027, 1, 5, 10, 0))
    check("F1 après le voyage : « Le voyage est terminé »", txt(pg, "#gn-day") == "Le voyage est terminé" and pg.is_visible("#gn-link"), txt(pg, "#gn-day")); ctx.close()
    # mise en page
    for vw in (390, 360, 320):
        ctx, pg = open_guest(b, at(2026, 12, 25, 12, 0), vw=vw)
        ov = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        r = pg.evaluate("(() => { var c = document.querySelector('#gnow').getBoundingClientRect(); var ks = [...document.querySelectorAll('#gnow .gn-clocks p')].map(e => { var r = e.getBoundingClientRect(); var b = e.querySelector('b'); return [r.width, b.scrollWidth, b.clientWidth]; }); return [c.left, c.right, innerWidth, ks]; })()")
        check("G %d px : pas de débordement et les heures tiennent" % vw, ov <= 0 and r[0] >= 0 and r[1] <= r[2] and all(k[1] <= k[2] + 1 for k in r[3]), (ov, r))
        if vw == 390: pg.locator("#gnow").screenshot(path="t/gn_jour.png")
        ctx.close()
    check("H aucune erreur JavaScript", not errs, errs[:2])
print("t38 :", n_ok, "OK,", n_ko, "KO")
