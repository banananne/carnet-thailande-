"""Cadenas du test de personnalité : fermé jusqu'au 29 décembre (heure locale du téléphone), mot secret, retour du cadenas, mise en page."""
import sys
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
    return datetime(y, mo, d, h, mi, s, tzinfo=ZoneInfo(tz))   # Playwright (Python) : un datetime avec fuseau, pas un nombre (un nombre y est en secondes)

def newctx(b, vw=390, vh=844, tz="Asia/Bangkok", when=None, dsf=2, init=None):
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=dsf, is_mobile=vw < 700, has_touch=True, locale="fr-FR", timezone_id=tz, service_workers="block")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    if when is not None: pg.clock.set_fixed_time(when)
    return ctx, pg

def go(pg, h):
    pg.evaluate("location.hash=%r" % h); pg.wait_for_timeout(260)
def locked(pg): return pg.evaluate("document.documentElement.classList.contains('tlock')")
def vis(pg, sel): return pg.is_visible(sel)
def low(s): return s.lower().replace(" ", " ")

with sync_playwright() as p:
    b = p.chromium.launch()

    # ───── A. avant le 29 décembre, téléphone neuf ─────
    ctx, pg = newctx(b, when=ms(2026, 11, 21, 12, 0))
    pg.goto(BASE + "#/jeux", wait_until="load"); pg.wait_for_timeout(500)
    check("A1 le cadenas est allumé (classe tlock)", locked(pg))
    tile = pg.locator("a.tile.lockable")
    check("A2 la tuile du test existe, une seule", tile.count() == 1)
    check("A3 icône cadenas visible, cœur caché", pg.evaluate("""() => { const t = document.querySelector('a.tile.lockable');
        return getComputedStyle(t.querySelector('.ic-lock')).display !== 'none' && getComputedStyle(t.querySelector('.ic-open')).display === 'none'; }"""))
    sub = pg.inner_text('[data-hub="doudou"]')
    check("A4 sous-titre « À partir du 29 décembre »", "à partir du 29 décembre" in low(sub), sub)
    pg.screenshot(path=OUT + "lk_hub_locked.png")
    tile.click(); pg.wait_for_timeout(300)
    check("A5 la tuile mène à la page du test", pg.evaluate("location.hash") == "#/personnalite")
    check("A6 page du test : écran « Pas encore » visible", vis(pg, "#dt-lock") and "pas encore" in low(pg.inner_text("#dt-lock h2")))
    check("A7 la date est écrite", "29 décembre" in low(pg.inner_text("#dt-lock")))
    check("A8 l'introduction et le bouton Commencer sont cachés", not vis(pg, "#dt-intro") and not vis(pg, '[data-dt="start"]'))
    check("A9 les quatre mascottes sont montrées", pg.locator("#dt-lock .dd-mini").count() == 4)
    check("A10 le formulaire du mot secret est replié", not vis(pg, "#lk-form") and vis(pg, '[data-lk="ask"]'))
    pg.screenshot(path=OUT + "lk_test_locked.png")
    # démarrer de force (bouton caché cliqué par script) : doit rester fermé
    pg.evaluate("document.querySelector('[data-dt=\"start\"]').click()"); pg.wait_for_timeout(200)
    check("A11 démarrage forcé refusé : aucune question affichée", pg.locator(".dt-q:visible").count() == 0 and vis(pg, "#dt-lock"))
    go(pg, "#/test-doudou")
    check("A12 ancienne adresse #/test-doudou : même cadenas", vis(pg, "#dt-lock"))
    # page des mascottes
    go(pg, "#/mascottes")
    check("A13 mascottes : le bouton « Quelle est la mienne ? » est caché", not vis(pg, ".dd-go"))
    check("A14 mascottes : la phrase d'attente est visible avec la date", vis(pg, ".dd-wait") and "29 décembre" in low(pg.inner_text(".dd-wait")), pg.inner_text(".dd-wait"))
    pg.screenshot(path=OUT + "lk_mascottes_locked.png")
    # passeport : l'indication du tampon
    how = pg.evaluate("document.querySelector('#v-pass .slot[data-id=\"doudou\"]').getAttribute('data-how')")
    check("A15 passeport : « dès le 29 décembre » dans l'indication du tampon", "dès le 29 décembre" in low(how), how)
    # un résultat déjà gardé ne fait pas apparaître « Ta mascotte » tant que c'est fermé
    pg.evaluate("localStorage.setItem('carnet.doudou','minou')"); pg.reload(); pg.wait_for_timeout(400); go(pg, "#/jeux")
    sub = pg.inner_text('[data-hub="doudou"]')
    check("A16 résultat déjà gardé : la tuile reste « À partir du… »", "à partir du 29 décembre" in low(sub), sub)
    pg.evaluate("localStorage.removeItem('carnet.doudou')")

    # ───── B. le mot secret ─────
    go(pg, "#/personnalite")
    pg.click('[data-lk="ask"]'); pg.wait_for_timeout(200)
    check("B1 le formulaire s'ouvre et le champ a le focus", vis(pg, "#lk-form") and pg.evaluate("document.activeElement && document.activeElement.id") == "lk-in")
    check("B2 le lien « J'ai le mot secret » se range", not vis(pg, '[data-lk="ask"]'))
    fs = pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#lk-in')).fontSize)")
    check("B3 champ en 16 px au moins (pas de zoom sur iPhone)", fs >= 16, fs)
    check("B4 champ : étiquette liée, sans correction automatique", pg.evaluate("""() => { const i = document.querySelector('#lk-in'); return !!document.querySelector('label[for=lk-in]') && i.getAttribute('autocapitalize') === 'none' && i.getAttribute('autocorrect') === 'off' && i.getAttribute('spellcheck') === 'false'; }"""))
    for bad in ("banane", "29 décembre", "aftonsparv", ""):
        pg.fill("#lk-in", bad); pg.click('#lk-form button[type="submit"]'); pg.wait_for_timeout(120)
        check("B5 mauvais mot %r refusé" % bad, locked(pg) and "pas le bon mot" in low(pg.inner_text("#lk-err")) and vis(pg, "#dt-lock"), pg.inner_text("#lk-err"))
    check("B6 rien n'est gardé après les erreurs", pg.evaluate("localStorage.getItem('carnet.open')") is None)
    pg.screenshot(path=OUT + "lk_form_error.png")
    pg.fill("#lk-in", "  MANGOUSTAN "); pg.press("#lk-in", "Enter"); pg.wait_for_timeout(350)
    check("B7 le bon mot (majuscules, espaces) ouvre, avec la touche Entrée", not locked(pg) and vis(pg, "#dt-intro") and not vis(pg, "#dt-lock"))
    check("B8 message « Test débloqué »", "test débloqué" in low(pg.inner_text("#toast")), pg.inner_text("#toast"))
    check("B9 le mot est gardé sur ce téléphone", pg.evaluate("localStorage.getItem('carnet.open')") == "1")
    check("B10 « Remettre le cadenas » est proposé (ouvert avant la date)", vis(pg, "#lk-relock"))
    go(pg, "#/jeux")
    sub = pg.inner_text('[data-hub="doudou"]')
    check("B11 hub : cœur de nouveau, sous-titre d'origine", "quelle mascotte es-tu" in low(sub) and pg.evaluate("getComputedStyle(document.querySelector('a.tile.lockable .ic-open')).display") != "none", sub)
    pg.screenshot(path=OUT + "lk_hub_open.png")
    go(pg, "#/mascottes")
    check("B12 mascottes : le bouton revient, la phrase d'attente disparaît", vis(pg, ".dd-go") and not vis(pg, ".dd-wait"))
    pg.reload(); pg.wait_for_timeout(400); go(pg, "#/personnalite")
    check("B13 après rechargement : toujours ouvert", not locked(pg) and vis(pg, "#dt-intro"))
    pg.click('[data-dt="start"]'); pg.wait_for_timeout(200)
    check("B14 le test démarre : question 1 visible", vis(pg, '.dt-q[data-i="0"]'))
    # le test jusqu'au bout
    for i in range(int(pg.get_attribute("#dt", "data-n"))):
        pg.locator(".dt-q:visible .qz-o").first.click(); pg.wait_for_timeout(60)
    pg.wait_for_timeout(300)
    check("B15 le test va jusqu'au résultat", vis(pg, "#dt-res") or vis(pg, "#dt-tie"))
    if vis(pg, "#dt-tie"):
        pg.locator(".dt-pick").first.click(); pg.wait_for_timeout(300)   # égalité : les amis tranchent
    check("B15b le résultat est gardé", pg.evaluate("localStorage.getItem('carnet.doudou')") is not None and vis(pg, "#dt-res"))
    go(pg, "#/jeux"); go(pg, "#/personnalite")   # (même adresse = pas de changement de page : on passe d'abord par les jeux)
    check("B16 retour sur la page : introduction, bouton « Revoir »", vis(pg, "#dt-intro") and vis(pg, "#dt-last"))
    pg.click("#lk-relock"); pg.wait_for_timeout(250)
    check("B17 « Remettre le cadenas » ferme de nouveau", locked(pg) and vis(pg, "#dt-lock") and pg.evaluate("localStorage.getItem('carnet.open')") is None)
    check("B18 message « Cadenas remis »", "cadenas remis" in low(pg.inner_text("#toast")))
    # variantes acceptées
    for good in ("mangosteen", "Mangoustan", "MANGOUSTAN", "man-gous tan"):
        go(pg, "#/personnalite")
        if not vis(pg, "#lk-form"): pg.click('[data-lk="ask"]')
        pg.fill("#lk-in", good); pg.click('#lk-form button[type="submit"]'); pg.wait_for_timeout(250)
        check("B19 variante %r acceptée" % good, not locked(pg))
        pg.click("#lk-relock"); pg.wait_for_timeout(200)
    ctx.close()

    # ───── C. l'ouverture par la date (heure locale du téléphone) ─────
    cases = [
        ("Bangkok 28/12 23:59", "Asia/Bangkok", ms(2026, 12, 28, 23, 59, 0), True),
        ("Bangkok 29/12 00:00", "Asia/Bangkok", ms(2026, 12, 29, 0, 0, 0), False),
        ("Bangkok 29/12 12:00", "Asia/Bangkok", ms(2026, 12, 29, 12, 0, 0), False),
        ("Bangkok 03/01 08:00", "Asia/Bangkok", ms(2027, 1, 3, 8, 0, 0), False),
        ("Paris 28/12 23:59", "Europe/Paris", ms(2026, 12, 28, 23, 59, 0, "Europe/Paris"), True),
        ("Paris 29/12 00:00", "Europe/Paris", ms(2026, 12, 29, 0, 0, 0, "Europe/Paris"), False),
        ("Paris 18/12 (départ)", "Europe/Paris", ms(2026, 12, 18, 9, 0, 0, "Europe/Paris"), True),
        ("Paris 01/01/2027", "Europe/Paris", ms(2027, 1, 1, 9, 0, 0, "Europe/Paris"), False),
    ]
    for label, tz, t, want_locked in cases:
        ctx, pg = newctx(b, tz=tz, when=t)
        pg.goto(BASE + "#/personnalite", wait_until="load"); pg.wait_for_timeout(400)
        check("C %s : %s" % (label, "fermé" if want_locked else "ouvert"), locked(pg) == want_locked, "tlock=%s" % locked(pg))
        check("C %s : écran cohérent" % label, (vis(pg, "#dt-lock") and not vis(pg, "#dt-intro")) if want_locked else (vis(pg, "#dt-intro") and not vis(pg, "#dt-lock")))
        if not want_locked:
            check("C %s : pas de « Remettre le cadenas » (ouvert par la date)" % label, not vis(pg, "#lk-relock"))
            pg.click('[data-dt="start"]'); pg.wait_for_timeout(200)
            check("C %s : le test démarre" % label, vis(pg, '.dt-q[data-i="0"]'))
        ctx.close()
    # minuit passe pendant que le site est ouvert
    ctx, pg = newctx(b, when=ms(2026, 12, 28, 23, 59, 30))
    pg.goto(BASE + "#/jeux", wait_until="load"); pg.wait_for_timeout(400)
    check("C9 23:59:30 : fermé", locked(pg))
    pg.clock.set_fixed_time(ms(2026, 12, 29, 0, 0, 20))
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(100)
    check("C10 minuit passé, retour au premier plan : ouvert", not locked(pg))
    pg.clock.set_fixed_time(ms(2026, 12, 28, 23, 59, 30))
    pg.evaluate("location.hash='#/utile'"); pg.wait_for_timeout(200); go(pg, "#/jeux")
    check("C11 changement de page : la date est relue (de nouveau fermé si on remonte le temps)", locked(pg))
    pg.clock.set_fixed_time(ms(2026, 12, 29, 0, 5, 0))
    pg.evaluate("location.hash='#/utile'"); pg.wait_for_timeout(200); go(pg, "#/jeux")
    check("C12 changement de page après minuit : ouvert, sous-titre d'origine", not locked(pg) and "quelle mascotte es-tu" in low(pg.inner_text('[data-hub="doudou"]')))
    ctx.close()

    # ───── D. mise en page du cadenas, du formulaire et des pages touchées ─────
    for (vw, vh) in ((320, 568), (360, 740), (390, 844), (412, 915), (768, 1024)):
        ctx, pg = newctx(b, vw, vh, when=ms(2026, 11, 21, 12, 0), dsf=2 if vw <= 412 else 1)
        pg.goto(BASE + "#/personnalite", wait_until="load"); pg.wait_for_timeout(400)
        def overflow(tag):
            r = pg.evaluate("""() => { const w = innerWidth, out = [];
              document.querySelectorAll('main.view:not([hidden]) *').forEach(e => { const r = e.getBoundingClientRect(); if (r.width > 0 && (r.right > w + 1 || r.left < -1)) out.push((e.className && e.className.baseVal === undefined ? e.className : e.tagName) + ':' + Math.round(r.left) + '→' + Math.round(r.right)); });
              return {sw: document.documentElement.scrollWidth, w, out: out.slice(0, 4)}; }""")
            check("D %dpx %s : pas de débordement" % (vw, tag), r["sw"] <= r["w"] + 1 and not r["out"], r)
        overflow("écran fermé")
        link = pg.locator('[data-lk="ask"]').bounding_box()
        check("D %dpx : lien du mot secret ≥ 44 px de haut" % vw, link and link["height"] >= 43.5, link)
        pg.click('[data-lk="ask"]'); pg.wait_for_timeout(150)
        overflow("formulaire ouvert")
        inp = pg.locator("#lk-in").bounding_box(); btn = pg.locator('#lk-form button[type="submit"]').bounding_box()
        check("D %dpx : champ ≥ 44 px, bouton visible dans l'écran" % vw, inp["height"] >= 44 and btn["x"] + btn["width"] <= vw and btn["x"] >= 0 and inp["width"] >= 120, (inp, btn))
        pg.fill("#lk-in", "x"); pg.press("#lk-in", "Enter"); pg.wait_for_timeout(450)
        overflow("après une erreur (animation finie)")
        if vw in (320, 390): pg.screenshot(path=OUT + "lk_form_%d.png" % vw, full_page=True)
        for h in ("#/jeux", "#/mascottes"):
            go(pg, h); overflow(h + " fermé")
        ctx.close()
    # les mêmes pages, ouvertes
    ctx, pg = newctx(b, 320, 568, when=ms(2026, 12, 29, 9, 0))
    pg.goto(BASE + "#/jeux", wait_until="load"); pg.wait_for_timeout(400)
    for h in ("#/jeux", "#/mascottes", "#/personnalite"):
        go(pg, h)
        r = pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
        check("D 320px %s ouvert : pas de débordement" % h, r)
    ctx.close()
    b.close()

print("erreurs JS:", errs or "aucune")
print("OK %d  ÉCHECS %d" % (ok_n, fail_n))
sys.exit(1 if (fail_n or errs) else 0)
