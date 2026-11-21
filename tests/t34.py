# -*- coding: utf-8 -*-
"""Enveloppes secrètes, VRAI chemin (accueil, prénom, heure du téléphone) avec un FAUX jeu (web34 : 4 prénoms, faux codes test-…).
Heures d'ouverture, révélation, effacement, un code par personne, un téléphone à plusieurs prénoms, mode essai sans effet."""
import sys, re, json
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8766/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
CODES = {"Arthur": "test-alpha-1111", "Daphne": "test-bravo-2222", "Flo": "test-charlie-3333", "Anne": "test-delta-4444"}
ok_n = fail_n = 0
errs = []
def check(name, cond, info=""):
    global ok_n, fail_n
    if cond: ok_n += 1
    else:
        fail_n += 1; print("  ✗", name, info)
def at(y, mo, d, h, mi, tz="Asia/Bangkok"): return datetime(y, mo, d, h, mi, 0, tzinfo=ZoneInfo(tz))
def sp(s): return s.replace(" ", " ").replace(" ", " ")

def newctx(b, tz="Asia/Bangkok", vw=390, vh=844):
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR", timezone_id=tz, service_workers="block")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    return ctx, pg

def vis(pg, sel): return pg.is_visible(sel)
def ls(pg, k): return pg.evaluate("k => localStorage.getItem(k)", k)
def keys(pg, prefix): return sorted(pg.evaluate("p => Object.keys(localStorage).filter(k => k.indexOf(p) === 0)", prefix))
def pane(pg):
    for p in ("code", "chut", "card", "sealed", "rev", "bad"):
        if pg.is_visible("#envp-" + p): return p
    return None
def hold(pg, ms_=1250):
    bb = pg.locator("#env-hold").bounding_box()
    pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); pg.mouse.down(); pg.wait_for_timeout(ms_); pg.mouse.up(); pg.wait_for_timeout(150)
def type_code(pg, code):
    pg.fill("#env-in", code); pg.click("#env-go"); pg.wait_for_timeout(900)
def set_time(pg, t):
    """le téléphone change d'heure ; l'appli s'en aperçoit quand on y revient (comme quand on la rouvre)"""
    pg.clock.set_fixed_time(t)
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(200)
def start(b, t, who="Anne", tz="Asia/Bangkok", extra=None):
    ctx, pg = newctx(b, tz)
    pg.clock.set_fixed_time(t)
    init = []
    if who: init.append("localStorage.setItem('carnet.who', %r)" % who)
    if extra: init.extend(extra)
    if init: pg.add_init_script("if (!sessionStorage.getItem('_i')) { sessionStorage.setItem('_i', '1'); %s }" % ";".join(init))
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(600)
    return ctx, pg
def banner(pg): return vis(pg, "#env-btn")
def btxt(pg): return sp(pg.inner_text("#env-btn"))

with sync_playwright() as p:
    b = p.chromium.launch()

    # ───── A. avant le jeu, et le mode essai n'ouvre rien ─────
    ctx, pg = start(b, at(2026, 12, 19, 12, 0))
    check("A1 avant le 20 décembre : pas d'enveloppe sur l'accueil", not banner(pg) and vis(pg, "#who-bar"))
    check("A2 le fichier contient bien les quatre personnes", pg.evaluate("Object.keys(JSON.parse(document.getElementById('env-data').textContent).real.b).sort().join()") == "Anne,Arthur,Daphne,Flo")
    pg.evaluate("localStorage.setItem('carnet.open','1')"); pg.reload(wait_until="load"); pg.wait_for_timeout(500)
    check("A3 le mot secret du mode essai n'ouvre PAS l'enveloppe", not banner(pg))
    pg.evaluate("location.hash = '#/jeux'"); pg.wait_for_timeout(300); pg.evaluate("location.hash = '#/'"); pg.wait_for_timeout(300)
    check("A4 même après un tour par les jeux ouverts", not banner(pg))
    ctx.close()
    ctx, pg = start(b, at(2026, 12, 21, 10, 0), who=None)
    check("A5 sans prénom choisi : pas d'enveloppe", not banner(pg) and vis(pg, "#who-box"))
    pg.click('#who button[data-n="Anne"]'); pg.wait_for_timeout(900)
    check("A6 dès qu'on choisit son prénom, l'enveloppe apparaît", banner(pg))
    ctx.close()

    # ───── B. l'heure du téléphone décide (minute près, fuseau local) ─────
    ctx, pg = start(b, at(2026, 12, 20, 6, 59, "Europe/Paris"), tz="Europe/Paris")
    check("B1 20 décembre 6 h 59 (heure du téléphone) : rien", not banner(pg))
    set_time(pg, at(2026, 12, 20, 7, 0, "Europe/Paris"))
    check("B2 20 décembre 7 h 00 : l'enveloppe apparaît", banner(pg))
    ctx.close()

    # ───── C. vague 1, Anne ─────
    ctx, pg = start(b, at(2026, 12, 21, 10, 0))
    check("C1 pendant la vague 1 : le bandeau est là, avec son point", banner(pg) and vis(pg, "#env-btn .dot") and "Une enveloppe t’attend" in btxt(pg), btxt(pg))
    pg.screenshot(path=OUT + "env_r1_accueil.png")
    pg.click("#env-btn"); pg.wait_for_timeout(300)
    check("C2 écran du code, SANS l'aide de l'essai", pane(pg) == "code" and not vis(pg, "#env-simhint"))
    type_code(pg, "abracadabra")
    check("C3 mauvais code refusé", pane(pg) == "code" and "pas le bon code" in sp(pg.inner_text("#env-err")))
    type_code(pg, CODES["Daphne"])
    check("C4 le code de Daphne n'ouvre pas l'enveloppe d'Anne", pane(pg) == "code" and keys(pg, "carnet.env.k.") == [])
    type_code(pg, CODES["Anne"])
    check("C5 le code d'Anne mène au serment", pane(pg) == "chut", pane(pg))
    hold(pg)
    check("C6 la mission est celle d'Anne", pane(pg) == "card" and "mission secrète de anne (w1)" in sp(pg.inner_text("#card-title")).lower(), pg.inner_text("#card-title"))
    check("C7 rien de secret n'est gardé : ni clé ni code (seulement « vu » sous « carnet.env »), rien sous « carnet.sim »",
          keys(pg, "carnet.env.k.") == [] and keys(pg, "carnet.sim.") == [] and keys(pg, "carnet.env.") == ["carnet.env.o.Anne.w1"]
          and "test-delta" not in pg.evaluate("JSON.stringify(Object.assign({}, localStorage))"), keys(pg, "carnet.env."))
    intro = sp(pg.inner_text("#card-intro"))
    check("C7b contexte de la vague 1 et « même Anne »", "Du 20 au 25 décembre" in intro and "Même Anne, qui a organisé le voyage" in intro, intro)
    fin = pg.evaluate("() => [...document.querySelectorAll('#card-fin small, #card-fin b, #card-fin strong')].map(e => e.textContent)")
    check("C7c encadré : fin de la mission, vendredi 25 décembre, 19 h", len(fin) == 3 and sp(fin[0]).startswith("Fin de la mission") and sp(fin[1]) == "vendredi 25 décembre" and sp(fin[2]) == "19 h", fin)
    pg.click("#env-x"); pg.wait_for_timeout(250)
    check("C8 le bandeau change de texte une fois l'enveloppe ouverte", banner(pg) and "Ton enveloppe secrète" in btxt(pg) and not vis(pg, "#env-btn .dot"), btxt(pg))
    pg.click("#env-btn"); pg.wait_for_timeout(500)
    check("C9 rouvrir : le code est redemandé, champ vide", pane(pg) == "code" and pg.input_value("#env-in") == "", pane(pg))
    type_code(pg, CODES["Anne"])
    check("C9b avec le bon code : la mission, sans refaire le serment", pane(pg) == "card" and "mission secrète de anne (w1)" in sp(pg.inner_text("#card-title")).lower(), pane(pg))
    pg.evaluate("document.querySelector('#card-close').click()"); pg.wait_for_timeout(250)
    pg.click("#sealed-open"); pg.wait_for_timeout(300)
    check("C9c refermer puis rouvrir : encore le code", pane(pg) == "code" and pg.input_value("#env-in") == "", pane(pg))
    pg.click("#env-x"); pg.wait_for_timeout(200)

    # ───── D. un autre prénom sur le même téléphone ─────
    pg.click("#who-bar"); pg.wait_for_timeout(300)
    pg.click('#who button[data-n="Daphne"]'); pg.wait_for_timeout(900)
    check("D1 autre prénom : le bandeau est de nouveau « neuf »", banner(pg) and "Une enveloppe t’attend" in btxt(pg), btxt(pg))
    pg.click("#env-btn"); pg.wait_for_timeout(300)
    check("D2 le code est demandé", pane(pg) == "code", pane(pg))
    type_code(pg, CODES["Anne"])
    check("D3 le code d'Anne ne marche pas avec le prénom de Daphne", pane(pg) == "code")
    type_code(pg, CODES["Daphne"]); hold(pg)
    check("D4 mission de Daphne", pane(pg) == "card" and "mission secrète de daphne (w1)" in sp(pg.inner_text("#card-title")).lower(), pg.inner_text("#card-title"))
    check("D5 aucune clé gardée, même avec deux prénoms", keys(pg, "carnet.env.k.") == [] and sorted(keys(pg, "carnet.env.")) == ["carnet.env.o.Anne.w1", "carnet.env.o.Daphne.w1"], keys(pg, "carnet.env."))
    pg.click("#env-x"); pg.wait_for_timeout(200)

    # ───── E. l'heure de la révélation (vague 1) ─────
    pg.click("#who-bar"); pg.wait_for_timeout(300); pg.click('#who button[data-n="Anne"]'); pg.wait_for_timeout(900)
    set_time(pg, at(2026, 12, 25, 18, 59))
    check("E1 25 décembre 18 h 59 : encore la mission", banner(pg) and "Ton enveloppe secrète" in btxt(pg))
    set_time(pg, at(2026, 12, 25, 19, 0))
    check("E2 25 décembre 19 h 00 : « L'heure des aveux »", banner(pg) and "L’heure des aveux" in btxt(pg) and vis(pg, "#env-btn .dot"), btxt(pg))
    pg.click("#env-btn"); pg.wait_for_timeout(500)
    check("E3a la révélation demande aussi le code", pane(pg) == "code", pane(pg))
    type_code(pg, CODES["Anne"])
    check("E3 puis la révélation s'ouvre directement", pane(pg) == "rev", pane(pg))
    check("E4 quatre lignes, celle d'Anne en valeur", pg.locator("#rev-tbl tbody tr").count() == 4 and pg.locator("#rev-tbl tr.me").count() == 1 and "Anne" in pg.inner_text("#rev-tbl tr.me"))
    check("E5 voix de Boop", "aveux" in pg.inner_text("#rev-say") and pg.locator('#rev-say img[src$="doudou_boop.webp"]').count() == 1)
    pg.screenshot(path=OUT + "env_r2_revelation.png")
    pg.click("#rev-close"); pg.wait_for_timeout(200)
    check("E6 une fois vue : « La révélation », sans point", "La révélation" in btxt(pg) and not vis(pg, "#env-btn .dot"), btxt(pg))

    # ───── F. fin de la vague 1 : tout s'efface ─────
    set_time(pg, at(2026, 12, 26, 5, 0))
    check("F1 26 décembre 5 h : plus d'enveloppe", not banner(pg))
    check("F2 les traces de la vague 1 sont effacées", [k for k in keys(pg, "carnet.env.") if k.endswith(".w1")] == [], keys(pg, "carnet.env."))
    check("F3 toujours aucune clé sur le téléphone", keys(pg, "carnet.env.k.") == [])
    set_time(pg, at(2026, 12, 29, 12, 0))
    check("F4 29 décembre : entre deux vagues, rien", not banner(pg))

    # ───── G. vague 2 : les mots, avec l'état gardé d'un rechargement à l'autre ─────
    set_time(pg, at(2026, 12, 27, 6, 59)); check("G0 27 décembre 6 h 59 : rien", not banner(pg))
    set_time(pg, at(2026, 12, 27, 9, 0))
    check("G1 27 décembre : l'enveloppe du killer", banner(pg) and "Une enveloppe t’attend" in btxt(pg))
    pg.click("#env-btn"); pg.wait_for_timeout(500)
    check("G1b le code est demandé (jamais gardé)", pane(pg) == "code", pane(pg))
    type_code(pg, CODES["Anne"])
    check("G2 puis le serment de Minou", pane(pg) == "chut" and pg.locator('#chut-pics img[src$="doudou_minou.webp"]').count() == 1, pane(pg))
    hold(pg)
    fin = pg.evaluate("() => [...document.querySelectorAll('#card-fin small, #card-fin b, #card-fin strong')].map(e => e.textContent)")
    check("G2b encadré du killer : dimanche 27 décembre, 19 h", len(fin) == 3 and sp(fin[1]) == "dimanche 27 décembre" and sp(fin[2]) == "19 h", fin)
    check("G3 mots propres à Anne", pane(pg) == "card" and sp(pg.inner_text("#ed-word")) == "anne-mot1", pg.inner_text("#ed-word"))
    pg.click("#ed-ok"); pg.click("#ed-ok"); pg.wait_for_timeout(150)
    check("G4 deux mots dits", pg.inner_text("#ed-n") == "2" and sp(pg.inner_text("#ed-word")) == "anne-mot3")
    check("G5 score gardé sous « carnet.env.h »", ls(pg, "carnet.env.h.Anne.w2") is not None and keys(pg, "carnet.sim.") == [])
    pg.reload(wait_until="load"); pg.wait_for_timeout(600)
    pg.click("#env-btn"); pg.wait_for_timeout(500); type_code(pg, CODES["Anne"])
    check("G6 après un rechargement et le code retapé : même mot, même score", pane(pg) == "card" and sp(pg.inner_text("#ed-word")) == "anne-mot3" and pg.inner_text("#ed-n") == "2", pg.inner_text("#ed-word"))
    pg.click("#env-x"); pg.wait_for_timeout(200)
    set_time(pg, at(2026, 12, 27, 19, 30))
    pg.click("#env-btn"); pg.wait_for_timeout(500); type_code(pg, CODES["Anne"])
    check("G7 19 h 30 : la révélation, avec mon score", pane(pg) == "rev" and "Ton score : 2 mots dits" in sp(pg.inner_text("#rev-score")), pg.inner_text("#rev-score") if vis(pg, "#rev-score") else pane(pg))
    pg.click("#rev-close"); pg.wait_for_timeout(200)
    set_time(pg, at(2026, 12, 28, 5, 0))
    check("G8 28 décembre 5 h : plus d'enveloppe, score effacé", not banner(pg) and [k for k in keys(pg, "carnet.env.") if k.endswith(".w2")] == [], keys(pg, "carnet.env."))

    # ───── H. vague 3 : le réveillon (la révélation à 20 h) ─────
    set_time(pg, at(2026, 12, 31, 8, 0))
    pg.click("#env-btn"); pg.wait_for_timeout(500); type_code(pg, CODES["Anne"]); hold(pg)
    check("H1 mission du réveillon, deux mascottes", pane(pg) == "card" and pg.locator("#card-say .env-sp").count() == 2 and "(w3)" in pg.inner_text("#card-title").lower())
    fin = pg.evaluate("() => [...document.querySelectorAll('#card-fin small, #card-fin b, #card-fin strong')].map(e => e.textContent)")
    check("H1b encadré du réveillon : jeudi 31 décembre, 20 h", len(fin) == 3 and sp(fin[1]) == "jeudi 31 décembre" and sp(fin[2]) == "20 h", fin)
    pg.click("#env-x"); pg.wait_for_timeout(200)
    set_time(pg, at(2026, 12, 31, 19, 59))
    check("H2 19 h 59 le 31 : pas encore les aveux", "Ton enveloppe secrète" in btxt(pg), btxt(pg))
    set_time(pg, at(2026, 12, 31, 20, 0))
    check("H3 20 h 00 : « L'heure des aveux »", "L’heure des aveux" in btxt(pg))
    # fin du jeu
    set_time(pg, at(2027, 1, 1, 5, 59))
    check("H4 1er janvier 5 h 59 : la révélation est encore là", banner(pg))
    set_time(pg, at(2027, 1, 1, 6, 0))
    check("H5 1er janvier 6 h : fini, plus rien sur l'accueil", not banner(pg))
    check("H6 le téléphone a tout oublié : plus de score, plus aucune trace", keys(pg, "carnet.env.") == [], keys(pg, "carnet.env."))
    ctx.close()

    # ───── I. l'heure passe pendant la lecture (horloge simulée : le minuteur de l'appli tourne) ─────
    def clocked(t, who="Anne"):
        ctx, pg = newctx(b)
        pg.add_init_script("localStorage.setItem('carnet.who', %r)" % who)
        pg.clock.install(time=t)
        pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(600)
        return ctx, pg
    def hold_fake(pg):
        bb = pg.locator("#env-hold").bounding_box()
        pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); pg.mouse.down(); pg.clock.run_for(1100); pg.mouse.up(); pg.wait_for_timeout(150)
    ctx, pg = clocked(at(2026, 12, 31, 19, 59, "Asia/Bangkok").replace(second=40))
    pg.click("#env-btn"); pg.wait_for_timeout(300); type_code(pg, CODES["Anne"]); hold_fake(pg)
    check("I1 mission du réveillon ouverte à 19 h 59 min 40", pane(pg) == "card", pane(pg))
    pg.clock.run_for(21000); pg.wait_for_timeout(250)
    check("I2 à 20 h : l'enveloppe se referme et propose la révélation", pane(pg) == "sealed" and vis(pg, "#sealed-rev") and not vis(pg, "#sealed-open") and pg.inner_text("#card-items").strip() == "", pane(pg))
    pg.click("#sealed-rev"); pg.wait_for_timeout(500)
    check("I3a « Voir la révélation » redemande le code", pane(pg) == "code" and pg.input_value("#env-in") == "", pane(pg))
    type_code(pg, CODES["Anne"])
    check("I3 puis ouvre la révélation", pane(pg) == "rev" and pg.locator("#rev-tbl tbody tr").count() == 4, pane(pg))
    ctx.close()
    ctx, pg = clocked(at(2026, 12, 26, 3, 59).replace(second=40))
    pg.click("#env-btn"); pg.wait_for_timeout(300); type_code(pg, CODES["Anne"])
    check("I4 à 3 h 59 le 26 : le code mène directement à la révélation", pane(pg) == "rev", pane(pg))
    pg.clock.run_for(21000); pg.wait_for_timeout(250)
    check("I5 à 4 h : fini, tout se ferme et s'efface, plus de bandeau", not vis(pg, "#env") and not banner(pg) and keys(pg, "carnet.env.r.") == [])
    ctx.close()

    # ───── J. rien de lisible dans le site publié de test ─────
    page = open("/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/web34/index.html", encoding="utf-8").read()
    for needle in ["Mission secrète de", "anne-mot1", "test-delta", "test-alpha", "Fais apparaître une banane", "Même Anne", "tiré au sort sans elle", "brassais l’air"]:
        check("J1 « %s » absent du fichier publié" % needle, needle not in page)
    ctx, pg = start(b, at(2026, 12, 21, 10, 0))
    pg.evaluate("location.hash = '#/essai'"); pg.wait_for_timeout(300)
    check("J2 la page d'essai marche aussi avec le vrai jeu présent", vis(pg, "#sim-env-btn"))
    pg.click("#sim-env-btn"); pg.wait_for_timeout(300)
    check("J3 l'essai reste séparé : il demande son propre code", pane(pg) == "code" and vis(pg, "#env-simhint"))
    ctx.close()

    # ───── K. une ancienne clé gardée par une version précédente est effacée, et ne remplace pas le code ─────
    ctx, pg = start(b, at(2026, 12, 21, 10, 0), extra=["localStorage.setItem('carnet.env.k.Anne', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=')"])
    check("K1 l'ancienne clé est effacée au chargement", keys(pg, "carnet.env.k.") == [], keys(pg, "carnet.env."))
    pg.click("#env-btn"); pg.wait_for_timeout(300)
    check("K2 et l'enveloppe demande le code", pane(pg) == "code")
    ctx.close()

    b.close()

print("\nt34 : %d OK, %d échec(s)" % (ok_n, fail_n))
if errs:
    print("erreurs console/page :", sorted(set(errs))[:8])
sys.exit(1 if fail_n or errs else 0)
