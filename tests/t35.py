# -*- coding: utf-8 -*-
"""Mise à jour du 21 novembre soir : espace visiteur (« Je suis invité·e »), liens Maps des rendez-vous GetYourGuide,
bouton de la playlist, date du 18.12.2026, aucune clé d'enveloppe ni vraie donnée visibles."""
import sys, re, json, urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
ok_n = fail_n = 0
errs = []
def check(name, cond, info=""):
    global ok_n, fail_n
    if cond: ok_n += 1
    else:
        fail_n += 1; print("  ✗", name, info)
def at(y, mo, d, h, mi, tz="Asia/Bangkok"): return datetime(y, mo, d, h, mi, 0, tzinfo=ZoneInfo(tz))
def sp(s): return s.replace(" ", " ").replace(" ", " ")
def vis(pg, sel): return pg.is_visible(sel)
def newctx(b, t, vw=390, vh=844):
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=1, is_mobile=True, has_touch=True, locale="fr-FR", timezone_id="Asia/Bangkok", service_workers="block")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.clock.set_fixed_time(t)
    return ctx, pg
def overflow(pg): return pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1")
def hrefs(pg, view):
    return [urllib.parse.unquote(h) for h in pg.evaluate("v => [...document.querySelectorAll(v + ' a[href]')].map(a => a.getAttribute('href'))", view)]

with sync_playwright() as p:
    b = p.chromium.launch()

    # ───── A. l'accueil : cinq pastilles, la dernière est « Je suis invité·e » ─────
    ctx, pg = newctx(b, at(2026, 12, 21, 10, 0))
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(600)
    btns = pg.locator("#who button")
    check("A1 cinq pastilles : Arthur, Daphne, Flo, Anne, invité·e", btns.count() == 5 and [btns.nth(i).get_attribute("data-n") for i in range(5)] == ["Arthur", "Daphne", "Flo", "Anne", "Invité"], btns.count())
    check("A2 la pastille invité·e porte le bon texte", "invité" in sp(btns.nth(4).inner_text()).lower())
    g = btns.nth(4).bounding_box(); a = btns.nth(3).bounding_box()
    check("A3 la pastille invité·e est sur toute la largeur, sous les autres", g["y"] > a["y"] + a["height"] - 2 and g["width"] > a["width"] * 1.8, (g, a))
    check("A4 cible de 44 px au moins", g["height"] >= 44, g)
    check("A5 date du départ : 18.12.2026", "18.12.2026" in sp(pg.inner_text("#v-home")) or "18.12.2026" in pg.content(), "")
    check("A6 pas d'ancienne date 19.12.2026 dans le bandeau", "19.12.2026" not in sp(pg.inner_text("#v-home")))
    check("A7 pas de débordement", not overflow(pg))
    pg.screenshot(path="/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/g_a_accueil.png")

    # ───── B. choisir « invité·e » : tout le site, sans enveloppe, sans horoscope du jour, sans rôles ─────
    btns.nth(4).click(); pg.wait_for_timeout(900)
    check("B1 la classe is-guest est posée", pg.evaluate("document.documentElement.classList.contains('is-guest')"))
    check("B2 mémoire : carnet.who = Invité", pg.evaluate("localStorage.getItem('carnet.who')") == "Invité")
    check("B3 le bandeau replié dit bonjour à l'invité·e", vis(pg, "#who-bar") and "bienvenue" in pg.inner_text("#who-hi").lower(), pg.inner_text("#who-hi"))
    check("B4 message d'accueil : enveloppes et rôles réservés aux voyageurs", "réservés aux voyageurs" in sp(pg.evaluate("document.querySelector('#who-box').textContent")), "")
    check("B5 AUCUNE enveloppe sur l'accueil (même pendant une fenêtre de jeu, le 21 décembre)", not vis(pg, "#env-btn"))
    check("B6 pas d'horoscope du jour pour l'invité·e", not vis(pg, "#hsd"))
    check("B7 les rubriques du site restent là (Jours, Hôtels, Métro, Cartes taxi)", pg.locator("#v-home .tile, #v-home a.tile, #v-home [data-go]").count() >= 4 or pg.locator("#v-home a[href^='#/']").count() >= 4)
    pg.evaluate("location.hash = '#/defi'"); pg.wait_for_timeout(500)
    check("B8 défi du jour : pas de rôles du jour pour l'invité·e", not vis(pg, ".rl-box") and not vis(pg, "#v-defi .rl-box"))
    for h, v in [("#/jours/2026-12-20", "#v-days"), ("#/hotels", "#v-hotels"), ("#/utile", "#v-utile"), ("#/jeux", "#v-jeux"), ("#/taxi", "#v-taxi"), ("#/convertisseur", "#v-convert"), ("#/mots-meles", "#v-mots"), ("#/blind-test", "#v-blind"), ("#/lexique", "#v-lexique"), ("#/traduire", "#v-trad")]:
        pg.evaluate("h => { location.hash = h }", h); pg.wait_for_timeout(350)
        check("B9 invité·e : %s s'affiche sans débordement" % h, pg.evaluate("v => !!document.querySelector(v) && document.querySelector(v).offsetParent !== null", v) and not overflow(pg), h)
    pg.evaluate("location.hash = '#/essai'"); pg.wait_for_timeout(300)
    pg.evaluate("location.hash = '#/'"); pg.wait_for_timeout(300)
    # un invité qui recharge reste invité
    pg.reload(wait_until="load"); pg.wait_for_timeout(700)
    check("B10 après rechargement : toujours invité·e, toujours sans enveloppe", pg.evaluate("document.documentElement.classList.contains('is-guest')") and not vis(pg, "#env-btn"))
    # l'invité·e ne peut pas ouvrir une enveloppe de l'essai par l'accueil, et rien n'est mis de côté
    ks = pg.evaluate("Object.keys(localStorage).filter(k => k.indexOf('carnet.env.') === 0)")
    check("B11 aucune trace d'enveloppe réelle sur ce téléphone", ks == [], ks)
    # repasser voyageur
    pg.click("#who-bar"); pg.wait_for_timeout(300)
    pg.click('#who button[data-n="Flo"]'); pg.wait_for_timeout(900)
    check("B12 Flo : la classe is-guest disparaît, l'enveloppe revient", not pg.evaluate("document.documentElement.classList.contains('is-guest')") and vis(pg, "#env-btn"))
    check("B13 l'horoscope du jour revient pour Flo", vis(pg, "#hsd"))
    ctx.close()

    # ───── C. depuis la page « rôles du jour » : choix du prénom avec invité·e ─────
    ctx, pg = newctx(b, at(2026, 12, 21, 10, 0))
    pg.goto(BASE + "#/defi", wait_until="load"); pg.wait_for_timeout(600)
    wp = pg.locator(".whopick button")
    check("C1 sur la page du défi, aussi : « Je suis invité·e »", wp.count() >= 5 and pg.locator('.whopick button[data-wp="Invité"]').count() >= 1, wp.count())
    pg.locator('.whopick button[data-wp="Invité"]').first.click(); pg.wait_for_timeout(500)
    check("C2 invité·e choisi : le choix du prénom se range et les rôles restent cachés", pg.evaluate("localStorage.getItem('carnet.who')") == "Invité" and not vis(pg, ".rl-box"))
    ctx.close()

    # ───── D. les rendez-vous GetYourGuide : liens Maps ─────
    ctx, pg = newctx(b, at(2026, 12, 18, 9, 0))
    pg.goto(BASE + "#/jours/2026-12-20", wait_until="load"); pg.wait_for_timeout(600)
    h = hrefs(pg, "#v-days")
    check("D1 20 déc. : rendez-vous du bateau (coordonnées de Phet Kasem 19/1)", any("13.724617765054857,100.465503087047" in x for x in h), [x for x in h if "maps" in x][:4])
    check("D1b texte du rendez-vous", "Phet Kasem 19/1 Alley" in sp(pg.inner_text("#v-days")), "")
    for day, label in (("2026-12-21", "Ayutthaya"), ("2026-12-22", "marché flottant")):
        pg.evaluate("d => { location.hash = '#/jours/' + d }", day); pg.wait_for_timeout(500)
        h = hrefs(pg, "#v-days"); txt = sp(pg.inner_text("#v-days"))
        check("D2 %s : prise en charge à C’HOUSE" % day, "Prise en charge à C’HOUSE" in txt, "")
        check("D3 %s : retour au KFC de Samyan Mitrtown, lien Maps" % day, "Samyan Mitrtown" in txt and any("KFC Samyan Mitrtown, 974 Phaya Thai Rd" in x for x in h), [x for x in h if "maps" in x][:6])
    pg.evaluate("location.hash = '#/jours/2026-12-23'"); pg.wait_for_timeout(500)
    h = hrefs(pg, "#v-days")
    check("D4 23 déc. : rendez-vous du tuk-tuk (315-319 Rama IV)", any("315-319 Rama IV Road" in x for x in h) and "315-319 Rama IV Road" in sp(pg.inner_text("#v-days")), "")
    pg.evaluate("location.hash = '#/jours/2026-12-25'"); pg.wait_for_timeout(500)
    h = hrefs(pg, "#v-days")
    check("D5 25 déc. : rendez-vous du cours de cuisine (Sukhumvit 4)", any("13.7356647,100.5554998" in x for x in h) and "147/4 Sukhumvit 4" in sp(pg.inner_text("#v-days")), "")
    # liens externes sûrs, aucun lien de réservation GetYourGuide dans le site
    page = open("/home/claude/site_en_ligne/web/index.html", encoding="utf-8").read()
    check("D6 aucun lien de réservation GetYourGuide dans le site public", "getyourguide" not in page.lower())
    for day in ("2026-12-20", "2026-12-21", "2026-12-22", "2026-12-23", "2026-12-25"):
        pg.evaluate("d => { location.hash = '#/jours/' + d }", day); pg.wait_for_timeout(300)
        bad = pg.evaluate("() => [...document.querySelectorAll('#v-days a.maps')].filter(a => a.target !== '_blank' || !/noopener/.test(a.rel)).length")
        check("D7 %s : liens Maps en nouvel onglet, noopener" % day, bad == 0, bad)
    check("D8 pas de débordement", not overflow(pg))
    ctx.close()

    # ───── E. la playlist ─────
    ctx, pg = newctx(b, at(2026, 12, 18, 9, 0))
    pg.goto(BASE + "#/blind-test", wait_until="load"); pg.wait_for_timeout(600)
    pl = pg.locator('#v-blind a[href^="https://open.spotify.com/playlist/"]')
    check("E1 le bouton « La playlist » est visible", pl.count() == 1 and pl.first.is_visible() and "playlist" in sp(pl.first.inner_text()).lower(), pl.count())
    check("E2 lien exact, sans paramètre de suivi", pl.first.get_attribute("href") == "https://open.spotify.com/playlist/1OMK0fTqq4Q0TOFdvUxt05", pl.first.get_attribute("href"))
    check("E3 nouvel onglet, noopener", pl.first.get_attribute("target") == "_blank" and "noopener" in (pl.first.get_attribute("rel") or ""))
    check("E4 pas de débordement", not overflow(pg))
    ctx.close()

    # ───── F. rien de secret en clair, pas de clé ─────
    ctx, pg = newctx(b, at(2026, 12, 21, 10, 0))
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(500)
    pg.evaluate("localStorage.setItem('carnet.who','Anne')"); pg.reload(wait_until="load"); pg.wait_for_timeout(700)
    check("F1 Anne, le 21 décembre : l'enveloppe est là (code à taper)", vis(pg, "#env-btn"))
    pg.click("#env-btn"); pg.wait_for_timeout(500)
    check("F2 l'écran demande le code, sans aide d'essai", vis(pg, "#env-in") and not vis(pg, "#env-simhint"))
    pg.click("#env-x"); pg.wait_for_timeout(300)
    check("F3 rien gardé en mémoire (ni clé ni code ni mission)", pg.evaluate("Object.keys(localStorage).filter(k => k.indexOf('carnet.env.') === 0)") == [])
    ctx.close()

    b.close()

print("\nt35 : %d OK, %d échec(s)" % (ok_n, fail_n))
if errs:
    print("erreurs console/page :", sorted(set(errs))[:8])
sys.exit(1 if fail_n or errs else 0)
