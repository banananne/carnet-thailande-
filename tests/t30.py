"""Étape 4 : calendrier d'ouverture des jeux, mot secret, horoscope du jour, défi + rôles, mot du jour, bingo, carnet gourmand, prix, passeport à 28 tampons, mascottes."""
import sys, json, re
sys.path.insert(0, "/home/claude/site_en_ligne")
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
import data_days as X, data_horo_days as H, data_games as G, site_data as D, build_app as A

BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
ok_n = fail_n = 0
errs = []
IDS = [d["id"] for d in D.DAYS]
NB = "\u00a0"


def check(name, cond, info=""):
    global ok_n, fail_n
    if cond:
        ok_n += 1
    else:
        fail_n += 1
        print("  ✗", name, info)


def ms(y, mo, d, h=12, mi=0, tz="Asia/Bangkok"):
    return datetime(y, mo, d, h, mi, 0, tzinfo=ZoneInfo(tz))


def low(s):
    s = s.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2060", "").replace("\u2019", "'")
    return re.sub(r"\s+", " ", s).strip().lower()


def squash(s):
    """lettres et chiffres seulement : compare deux textes sans se soucier de la typographie française"""
    return re.sub(r"[^0-9a-zà-ÿœæ\u0e00-\u0e7f]", "", low(s))


def newctx(b, vw=390, vh=844, when=None, who=None, master=False, ls=None, dsf=2):
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=dsf, is_mobile=vw < 700, has_touch=True, locale="fr-FR",
                        timezone_id="Asia/Bangkok", service_workers="block")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
    pg.on("console", lambda m: errs.append("CONSOLE " + m.text) if m.type == "error" else None)
    if when is not None:
        pg.clock.set_fixed_time(when)
    inits = []
    if who: inits.append("localStorage.setItem('carnet.who',%r)" % who)
    if master: inits.append("localStorage.setItem('carnet.open','1')")
    for k, v in (ls or {}).items(): inits.append("localStorage.setItem(%r,%r)" % (k, v))
    if inits:
        # une seule fois au premier chargement, pas à chaque rechargement (sinon on écrase l'état gardé)
        ctx.add_init_script("try{if(!sessionStorage.getItem('__init')){sessionStorage.setItem('__init','1');%s}}catch(e){}" % ";".join(inits))
    return ctx, pg


def go(pg, h, wait=300):
    pg.evaluate("location.hash=%r" % h)
    pg.wait_for_timeout(wait)


def vis(pg, sel):
    return pg.is_visible(sel)


def ls_get(pg, k):
    return pg.evaluate("localStorage.getItem(%r)" % k)


def stamps_b(pg):
    v = ls_get(pg, "carnet.stamps")
    return json.loads(v)["b"] if v else []


def cur_view(pg):
    return pg.evaluate("(()=>{const m=[...document.querySelectorAll('main.view')].find(x=>!x.hidden);return m?m.id:null})()")


GATED_VIEWS = {"defi": "defi", "mot": "mot-du-jour", "bingo": "bingo", "gourmand": "gourmand", "prix": "prix", "quiz": "quiz", "blind": "blind-test",
               "mots": "mots-meles", "horo": "horoscope", "pass": "passeport", "doudous": "mascottes"}
VIEW_ID = {"defi": "v-defi", "mot": "v-mot", "bingo": "v-bingo", "gourmand": "v-gourmand", "prix": "v-prix", "quiz": "v-quiz", "blind": "v-blind",
           "mots": "v-mots", "horo": "v-horo", "pass": "v-pass", "doudous": "v-doudous"}


def expected_open(key, iso):
    return iso >= (G.TEST_OPEN if key == "test" else X.GATES[key][0])


with sync_playwright() as p:
    b = p.chromium.launch()

    # ───────────────────────── A. les dates d'ouverture ─────────────────────────
    cases = [("2026-11-21 midi", ms(2026, 11, 21), "2026-11-21"),
             ("17 déc. 23 h 59 (Bangkok)", ms(2026, 12, 17, 23, 59), "2026-12-17"),
             ("18 déc. 00 h 00", ms(2026, 12, 18, 0, 0), "2026-12-18"),
             ("25 déc.", ms(2026, 12, 25), "2026-12-25"),
             ("26 déc.", ms(2026, 12, 26), "2026-12-26"),
             ("29 déc.", ms(2026, 12, 29), "2026-12-29"),
             ("2 janv.", ms(2027, 1, 2), "2027-01-02"),
             ("3 janv.", ms(2027, 1, 3), "2027-01-03"),
             ("10 janv. (après le voyage)", ms(2027, 1, 10), "2027-01-10")]
    for label, when, iso in cases:
        ctx, pg = newctx(b, when=when)
        pg.goto(BASE + "#/jeux", wait_until="load"); pg.wait_for_timeout(450)
        for key in list(VIEW_ID) + ["test"]:
            tile = pg.locator('#v-jeux a.tile[data-gate="%s"]' % key)
            want_open = expected_open(key, iso)
            check("A %s : tuile %s existe" % (label, key), tile.count() == 1)
            locked_cls = "is-locked" in (tile.get_attribute("class") or "")
            check("A %s : tuile %s %s" % (label, key, "ouverte" if want_open else "fermée"), locked_cls != want_open, tile.get_attribute("class"))
            sub = low(pg.locator('#v-jeux a.tile[data-gate="%s"] small' % key).text_content())
            if not want_open:
                check("A %s : tuile %s dit « à partir du … »" % (label, key), sub.startswith("à partir du "), sub)
            else:
                check("A %s : tuile %s ne dit plus « à partir du »" % (label, key), "à partir du" not in sub, sub)
        for key, route in GATED_VIEWS.items():
            go(pg, "#/" + route)
            vid = VIEW_ID[key]
            want_open = expected_open(key, iso)
            check("A %s : %s s'affiche" % (label, route), cur_view(pg) == vid, cur_view(pg))
            lock_v = vis(pg, "#%s .lkv" % vid)
            body_v = vis(pg, "#%s .gbody" % vid)
            check("A %s : %s écran « pas encore » %s" % (label, route, "caché" if want_open else "visible"), lock_v != want_open)
            check("A %s : %s contenu %s" % (label, route, "visible" if want_open else "caché"), body_v == want_open)
            if not want_open:
                msg = low(pg.locator("#%s .lkv p" % vid).first.text_content())
                dtxt = low(X.GATES[key][1])
                check("A %s : %s écrit la date d'ouverture (%s)" % (label, route, dtxt), dtxt in msg, msg)
                check("A %s : %s mot secret replié" % (label, route), not vis(pg, "#%s .lk-form" % vid) and vis(pg, '#%s [data-lkv="ask"]' % vid))
        # le mode essai n'apparaît pas sans mot secret
        go(pg, "#/jeux")
        check("A %s : pas de « mode essai » sans mot secret" % label, not vis(pg, "#hub-try"))
        ctx.close()

    # ───────────────────────── B. le mot secret ouvre tout ─────────────────────────
    ctx, pg = newctx(b, when=ms(2026, 11, 21))
    pg.goto(BASE + "#/gourmand", wait_until="load"); pg.wait_for_timeout(450)
    check("B1 carnet gourmand fermé avant le départ", vis(pg, "#v-gourmand .lkv") and not vis(pg, "#v-gourmand .gbody"))
    pg.click('#v-gourmand [data-lkv="ask"]'); pg.wait_for_timeout(120)
    check("B2 le formulaire s'ouvre et le champ a le focus", vis(pg, "#v-gourmand .lk-form") and pg.evaluate("document.activeElement && document.activeElement.id") == "lkv-gourmand")
    fs = pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#lkv-gourmand')).fontSize)")
    check("B3 champ en 16 px au moins (pas de zoom sur iPhone)", fs >= 16, fs)
    inp = pg.locator("#lkv-gourmand")
    check("B4 champ sans correction automatique, étiqueté", inp.get_attribute("autocapitalize") == "none" and inp.get_attribute("autocorrect") == "off"
          and inp.get_attribute("spellcheck") == "false" and pg.locator('label[for="lkv-gourmand"]').count() == 1)
    for bad in ["", "mangue", "manga", "oups"]:
        pg.fill("#lkv-gourmand", bad); pg.click('#v-gourmand .lkv-form button[type="submit"]'); pg.wait_for_timeout(120)
        check("B5 mauvais mot %r refusé" % bad, vis(pg, "#v-gourmand .lkv") and "pas le bon mot" in low(pg.locator("#v-gourmand .lk-err").text_content()))
    check("B6 rien n'est gardé après les erreurs", ls_get(pg, "carnet.open") is None)
    pg.fill("#lkv-gourmand", "  MANGOUSTAN "); pg.press("#lkv-gourmand", "Enter"); pg.wait_for_timeout(350)
    check("B7 le bon mot (majuscules, espaces) ouvre la page", vis(pg, "#v-gourmand .gbody") and not vis(pg, "#v-gourmand .lkv"))
    check("B8 le mot est gardé sur ce téléphone", ls_get(pg, "carnet.open") == "1")
    go(pg, "#/jeux")
    for key in list(VIEW_ID) + ["test"]:
        cls = pg.locator('#v-jeux a.tile[data-gate="%s"]' % key).get_attribute("class")
        check("B9 tuile %s ouverte avec le mot secret" % key, "is-locked" not in cls, cls)
    check("B10 « mode essai » proposé", vis(pg, "#hub-try") and "remettre les cadenas" in low(pg.inner_text("#hub-try")))
    for key, route in GATED_VIEWS.items():
        go(pg, "#/" + route)
        check("B11 %s ouvert" % route, vis(pg, "#%s .gbody" % VIEW_ID[key]) and not vis(pg, "#%s .lkv" % VIEW_ID[key]))
    go(pg, "#/personnalite")
    check("B12 le test de personnalité s'ouvre aussi", vis(pg, "#dt-intro") and not vis(pg, "#dt-lock"))
    go(pg, "#/jeux")
    pg.click('[data-relock="1"]'); pg.wait_for_timeout(250)
    check("B13 « Remettre les cadenas » ferme tout", ls_get(pg, "carnet.open") is None and "is-locked" in pg.locator('#v-jeux a.tile[data-gate="gourmand"]').get_attribute("class")
          and not vis(pg, "#hub-try"))
    go(pg, "#/gourmand")
    check("B14 écran « pas encore » de retour", vis(pg, "#v-gourmand .lkv") and not vis(pg, "#v-gourmand .gbody"))
    # le mot secret tapé sur le quiz ou sur le test ouvre tout aussi bien
    go(pg, "#/quiz")
    pg.click('#v-quiz [data-lkv="ask"]'); pg.fill("#lkv-quiz", "mangosteen"); pg.press("#lkv-quiz", "Enter"); pg.wait_for_timeout(300)
    check("B15 le 2e mot (mangosteen) ouvre aussi, depuis le quiz", vis(pg, "#v-quiz .gbody") and ls_get(pg, "carnet.open") == "1")
    ctx.close()

    # ───────────────────────── C. horoscope du jour sur l'accueil ─────────────────────────
    ctx, pg = newctx(b, when=ms(2026, 11, 21))
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(450)
    check("C1 sans prénom : pas de carte horoscope", not vis(pg, "#hsd"))
    pg.click('#who button[data-n="Daphne"]'); pg.wait_for_timeout(300)
    check("C2 prénom choisi, avant le départ : carte d'attente (Bélier)", vis(pg, "#hsd") and vis(pg, "#hsd-wait") and "18 décembre" in low(pg.text_content("#hsd-wait")))
    check("C3 avant le départ : aucun texte du jour", pg.locator("#hsd .hsd-i:visible").count() == 0)
    ctx.close()
    SIGNS = {"Arthur": "gemeaux", "Daphne": "belier", "Flo": "scorpion", "Anne": "scorpion"}
    for who, sg in SIGNS.items():
        ctx, pg = newctx(b, when=ms(2026, 12, 18), who=who, master=True)
        pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(450)
        check("C4 %s : carte visible, signe %s" % (who, H.SIGN_NAME[sg]), vis(pg, "#hsd") and low(H.SIGN_NAME[sg]) in low(pg.text_content("#hsd-sub")), pg.text_content("#hsd-sub"))
        for i in range(17):
            texte, conseil = H.HORO_DAILY[sg][i]
            lucky = texte.startswith(H.CHANCE)
            body = texte[len(H.CHANCE):].strip() if lucky else texte
            it = pg.locator("#hsd .hsd-i:visible")
            check("C5 %s jour %d : une seule entrée visible" % (who, i + 1), it.count() == 1, it.count())
            t = low(it.locator(".hsd-t").text_content()); c = low(it.locator(".hsd-c").text_content())
            check("C6 %s jour %d : texte du jour" % (who, i + 1), squash(t) == squash(body), t[:60])
            check("C7 %s jour %d : conseil" % (who, i + 1), squash(conseil) in squash(c), c[:60])
            check("C8 %s jour %d : date écrite" % (who, i + 1), squash(A.day_title(IDS[i])) in squash(pg.text_content("#hsd-sub")))
            check("C9 %s jour %d : badge « jour de chance » seulement le bon jour" % (who, i + 1), (it.locator(".hsd-luck").count() == 1) == (H.LUCKY[sg] == IDS[i]) and lucky == (H.LUCKY[sg] == IDS[i]))
            if i < 16:
                pg.click('[data-hs="1"]'); pg.wait_for_timeout(60)
        check("C10 %s : constellation du signe %s affichée" % (who, sg), pg.locator('#hsd .hsd-sky [data-sign="%s"]:visible' % sg).count() == 1 and pg.locator("#hsd .hsd-sky span:visible").count() == 1)
        ctx.close()
    # une date précise, sans mode essai
    for who, iso_d, when in [("Flo", "2026-12-28", ms(2026, 12, 28)), ("Arthur", "2026-12-31", ms(2026, 12, 31, 23, 50)), ("Anne", "2027-01-03", ms(2027, 1, 3, 0, 5))]:
        ctx, pg = newctx(b, when=when, who=who)
        pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(450)
        i = IDS.index(iso_d); sg = SIGNS[who]
        t = low(pg.locator("#hsd .hsd-i:visible .hsd-t").text_content())
        texte, _c = H.HORO_DAILY[sg][i]
        body = texte[len(H.CHANCE):].strip() if texte.startswith(H.CHANCE) else texte
        check("C11 %s le %s : le bon texte, sans mode essai" % (who, iso_d), squash(t) == squash(body) and not vis(pg, "#hsd-nav"))
        ctx.close()
    ctx, pg = newctx(b, when=ms(2027, 1, 12), who="Daphne")
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(450)
    check("C12 après le voyage : le dernier jour reste affiché", "3 janvier" in low(pg.text_content("#hsd-sub")))
    # changer de prénom change le signe tout de suite
    pg.click("#who-bar"); pg.wait_for_timeout(200); pg.click('#who button[data-n="Arthur"]'); pg.wait_for_timeout(300)
    check("C13 changer de prénom change le signe (Gémeaux)", "gémeaux" in low(pg.text_content("#hsd-sub")))
    pg.screenshot(path=OUT + "t30_home_horo.png")
    ctx.close()

    # ───────────────────────── D. défi du jour + rôles ─────────────────────────
    ctx, pg = newctx(b, when=ms(2026, 12, 22), who="Anne")
    pg.goto(BASE + "#/defi", wait_until="load"); pg.wait_for_timeout(500)
    check("D1 défi du jour ouvert le 22 décembre", cur_view(pg) == "v-defi" and vis(pg, "#v-defi .gbody"))
    check("D2 le jour affiché est aujourd'hui", "mardi 22 décembre" in low(pg.locator("#v-defi .dn-t b").text_content()) and "jour 5 sur 17" in low(pg.locator("#v-defi .dn-t small").text_content())
          and "aujourd" in low(pg.locator("#v-defi .dn-t small").text_content()))
    check("D3 pas de jour suivant (demain n'est pas ouvert)", pg.locator('#v-defi [data-step="1"]').is_disabled() and not pg.locator('#v-defi [data-step="-1"]').is_disabled())
    blk = pg.locator("#v-defi .dfd:visible")
    check("D4 un seul bloc visible", blk.count() == 1)
    i = 4
    texts = [low(x) for x in blk.locator(".rl-i .rl-r").all_text_contents()]
    want = [low(X.ROLES[(pp + i) % 4]["name"]) for pp in range(4)]
    check("D5 les quatre rôles sont distribués (jour 5)", [squash(x) for x in texts] == [squash(x) for x in want] and len(set(texts)) == 4, texts)
    me = blk.locator(".rl-i.me")
    check("D6 ma ligne est mise en avant (Anne) avec le texte du rôle", me.count() == 1 and me.get_attribute("data-n") == "Anne" and squash(X.ROLES[(3 + i) % 4]["text"]) in squash(me.locator(".rl-more").text_content()))
    check("D7 le texte du rôle n'est montré que pour moi", blk.locator(".rl-i:not(.me) .rl-more:visible").count() == 0)
    check("D8 la mission du jour", squash(X.MISSIONS[i][0]) in squash(blk.locator(".mis-t").text_content()) and squash(X.MISSIONS[i][1]) in squash(blk.locator(".mis-b").text_content()))
    check("D9 le lien « Prendre la photo » mène à la photo de ce jour", blk.locator("a.btn.alt").get_attribute("href") == "#/jours/2026-12-22/photo")
    check("D10 pas de pastilles de prénom (prénom déjà choisi)", not vis(pg, "#v-defi .whopick"))
    # les jours précédents, les rôles qui tournent
    seen_roles = {}
    for k in range(4, -1, -1):
        blk = pg.locator("#v-defi .dfd:visible")
        rows = [low(x) for x in blk.locator(".rl-i .rl-r").all_text_contents()]
        check("D11 jour %d : quatre rôles différents" % (k + 1), len(set(rows)) == 4)
        seen_roles[k] = rows
        check("D12 jour %d : défi relevé non coché au départ" % (k + 1), blk.locator('[data-df="done"]').get_attribute("aria-pressed") == "false")
        blk.locator('[data-df="done"]').click(); pg.wait_for_timeout(120)
        check("D13 jour %d : coché" % (k + 1), pg.locator("#v-defi .dfd:visible [data-df=done]").get_attribute("aria-pressed") == "true")
        if k > 0:
            pg.click('#v-defi [data-step="-1"]'); pg.wait_for_timeout(100)
    check("D14 chaque personne change de rôle tous les jours (jours 1→5)", all(seen_roles[k][pp] != seen_roles[k + 1][pp] for k in range(4) for pp in range(4)))
    check("D15 le premier jour : « précédent » désactivé", pg.locator('#v-defi [data-step="-1"]').is_disabled() and "18 décembre" in low(pg.locator("#v-defi .dn-t b").text_content()))
    check("D16 5 défis → tampon spécial « défi »", "defi" in stamps_b(pg), stamps_b(pg))
    check("D17 compteur : 5 défis sur 17", "5 défis relevés sur 17" in low(pg.text_content("#mis-n")), pg.text_content("#mis-n"))
    check("D18 points de progression", pg.locator("#mis-dots i.on").count() == 5 and pg.locator("#mis-dots i").count() == 17)
    # mémoire après rechargement
    pg.reload(wait_until="load"); pg.wait_for_timeout(500); go(pg, "#/defi/2026-12-19")
    check("D19 lien profond #/defi/2026-12-19", "19 décembre" in low(pg.locator("#v-defi .dn-t b").text_content()) and pg.locator("#v-defi .dfd:visible [data-df=done]").get_attribute("aria-pressed") == "true")
    go(pg, "#/defi/2026-12-25")
    check("D20 un jour pas encore ouvert est ramené à aujourd'hui", "22 décembre" in low(pg.locator("#v-defi .dn-t b").text_content()))
    pg.click('#v-defi [data-step="-1"]'); pg.wait_for_timeout(100)
    pg.locator("#v-defi .dfd:visible [data-df=done]").click(); pg.wait_for_timeout(100)
    check("D21 on peut décocher", pg.locator("#v-defi .dfd:visible [data-df=done]").get_attribute("aria-pressed") == "false" and "4 défis" in low(pg.text_content("#mis-n")))
    go(pg, "#/jeux")
    check("D22 le sous-titre de la tuile suit", "4 défis relevés sur 17" in low(pg.locator('[data-hub="defi"]').text_content()), pg.locator('[data-hub="defi"]').text_content())
    # l'état est par jour, pas par prénom : on garde les 4
    pg.screenshot(path=OUT + "t30_hub.png", full_page=True)
    ctx.close()

    # sans prénom : pastilles pour choisir, puis rôle surligné
    ctx, pg = newctx(b, when=ms(2026, 12, 19))
    pg.goto(BASE + "#/defi", wait_until="load"); pg.wait_for_timeout(500)
    check("D23 sans prénom : pastilles visibles", vis(pg, "#v-defi .whopick") and pg.locator("#v-defi .rl-i.me").count() == 0)
    pg.click('#v-defi .whopick [data-wp="Flo"]'); pg.wait_for_timeout(250)
    check("D24 après avoir choisi : pastilles cachées, ligne de Flo en avant", not vis(pg, "#v-defi .whopick") and pg.locator("#v-defi .dfd:visible .rl-i.me").get_attribute("data-n") == "Flo"
          and ls_get(pg, "carnet.who") == "Flo")
    ctx.close()

    # ───────────────────────── E. mot du jour ─────────────────────────
    ctx, pg = newctx(b, when=ms(2026, 12, 22), who="Anne")
    pg.goto(BASE + "#/mot-du-jour", wait_until="load"); pg.wait_for_timeout(500)
    m = X.MOTS[4]
    card = pg.locator("#v-mot article.mt:visible")
    check("E1 le mot du 22 décembre (ลดหน่อย)", card.count() == 1 and card.locator(".mt-th").text_content() == m[0] and squash(card.locator(".mt-rom").text_content()) == squash(m[1]))
    check("E2 le sens, le conseil et le défi", squash(m[2]) in squash(card.locator(".mt-fr").text_content()) and squash(m[3]) in squash(card.locator(".mt-tip").text_content()) and squash(m[4]) in squash(card.locator(".mt-def").text_content()))
    say = card.locator("[data-say]")
    check("E3 bouton Écouter : thaï, petit mot poli selon le mot", say.get_attribute("data-th") == m[0] and (say.get_attribute("data-np") is None) == bool(m[5]) and say.get_attribute("data-q") == "0")
    card.locator("[data-show]").click(); pg.wait_for_timeout(300)
    check("E4 « Montrer » ouvre l'écran en grand avec le mot", vis(pg, "#show") and pg.text_content("#show-th").startswith(m[0]))
    pg.click(".show-x"); pg.wait_for_timeout(250)
    check("E5 l'écran en grand se referme", not vis(pg, "#show"))
    # un mot sans petit mot poli (mot du 20 décembre : สวยมาก)
    pg.click('#v-mot [data-step="-1"]'); pg.click('#v-mot [data-step="-1"]'); pg.wait_for_timeout(150)
    card = pg.locator("#v-mot article.mt:visible")
    check("E6 mot du 20 décembre : sans petit mot poli (data-np)", card.locator(".mt-th").text_content() == X.MOTS[2][0] and X.MOTS[2][5] is False and card.locator("[data-say]").get_attribute("data-np") is not None)
    # question : la piscine (26 décembre) porte data-q=1
    ctx.close()
    ctx, pg = newctx(b, when=ms(2026, 12, 26), who="Anne")
    pg.goto(BASE + "#/mot-du-jour", wait_until="load"); pg.wait_for_timeout(500)
    card = pg.locator("#v-mot article.mt:visible")
    check("E7 mot du 26 décembre = question (data-q=1)", card.locator("[data-say]").get_attribute("data-q") == "1" and "?" in X.MOTS[8][2], card.locator("[data-say]").get_attribute("data-q"))
    # 5 mots dits → tampon
    for k in range(8, 3, -1):
        pg.locator("#v-mot article.mt:visible [data-mt=done]").click(); pg.wait_for_timeout(100)
        if k > 4: pg.click('#v-mot [data-step="-1"]'); pg.wait_for_timeout(80)
    check("E8 5 mots dits → tampon « mot »", "mot" in stamps_b(pg), stamps_b(pg))
    check("E9 compteur", "5 mots dits sur 17" in low(pg.text_content("#mt-n")), pg.text_content("#mt-n"))
    rows_vis = pg.locator("#mtl .lx:visible")
    pg.click("#mtl summary"); pg.wait_for_timeout(250)
    check("E10 la liste des mots déjà vus montre les 9 premiers jours (18→26 déc.)", pg.locator("#mtl .lx:visible").count() == 9, pg.locator("#mtl .lx:visible").count())
    pg.locator("#mtl .lx:visible .lx-main").first.click(); pg.wait_for_timeout(300)
    check("E11 un mot de la liste s'ouvre en grand", vis(pg, "#show") and pg.text_content("#show-th").startswith(X.MOTS[0][0]))
    pg.click(".show-x"); pg.wait_for_timeout(250)
    ctx.close()

    # ───────────────────────── F. bingo ─────────────────────────
    grids = {}
    for who in ["Arthur", "Daphne", "Flo", "Anne"]:
        ctx, pg = newctx(b, when=ms(2026, 12, 22), who=who)
        pg.goto(BASE + "#/bingo", wait_until="load"); pg.wait_for_timeout(500)
        cells = pg.locator("#bg .bg-c")
        check("F1 %s : 9 cases" % who, cells.count() == 9)
        keys = cells.evaluate_all("els => els.map(e => e.getAttribute('data-k'))")
        check("F2 %s : 9 cases différentes, toutes dans la liste" % who, len(set(keys)) == 9 and all(k in dict(X.BINGO) for k in keys), keys)
        grids[who] = keys
        pg.reload(wait_until="load"); pg.wait_for_timeout(400); go(pg, "#/bingo")
        check("F3 %s : même grille après rechargement" % who, pg.locator("#bg .bg-c").evaluate_all("els => els.map(e => e.getAttribute('data-k'))") == keys)
        check("F4 %s : titre « La grille de … »" % who, who in pg.text_content("#bg-name"))
        if who == "Anne":
            for idx in (0, 1):
                cells.nth(idx).click(); pg.wait_for_timeout(80)
            check("F5 deux cases : pas encore de ligne, pas de tampon", "bingo" not in stamps_b(pg) and pg.locator("#bg .bg-c.win").count() == 0)
            check("F6 le compteur", "2 cases sur 9" in low(pg.text_content("#bg-n")), pg.text_content("#bg-n"))
            cells.nth(2).click(); pg.wait_for_timeout(700)
            check("F7 trois cases en ligne : les cases gagnantes sont marquées", pg.locator("#bg .bg-c.win").count() == 3 and "1 ligne complète" in low(pg.text_content("#bg-n")), pg.text_content("#bg-n"))
            check("F8 une ligne → tampon « bingo »", "bingo" in stamps_b(pg), stamps_b(pg))
            check("F9 l'état est gardé après rechargement", (pg.reload(wait_until="load"), pg.wait_for_timeout(400), go(pg, "#/bingo"), pg.locator("#bg .bg-c.on").count())[-1] == 3)
            # colonne et diagonale : toutes les lignes comptent
            for idx in (3, 4, 5, 6, 7, 8):
                pg.locator("#bg .bg-c").nth(idx).click(); pg.wait_for_timeout(50)
            check("F10 grille complète : message", "grille complète" in low(pg.text_content("#bg-n")) and pg.locator("#bg .bg-c.win").count() == 9, pg.text_content("#bg-n"))
            go(pg, "#/jeux")
            check("F11 tuile du hub : « Bingo ! 9 cases sur 9 »", "9 cases sur 9" in low(pg.locator('[data-hub="bingo"]').text_content()), pg.locator('[data-hub="bingo"]').text_content())
            go(pg, "#/bingo")
            pg.click("#bg-reset"); pg.wait_for_timeout(100)
            check("F12 « Effacer » demande une deuxième touche", pg.locator("#bg .bg-c.on").count() == 9)
            pg.click("#bg-reset"); pg.wait_for_timeout(200)
            check("F13 grille effacée", pg.locator("#bg .bg-c.on").count() == 0)
            pg.screenshot(path=OUT + "t30_bingo.png", full_page=True)
        ctx.close()
    check("F14 grilles différentes pour chaque prénom", len({tuple(v) for v in grids.values()}) == 4, grids)
    # les lignes : test direct des 8 lignes avec des cases choisies
    ctx, pg = newctx(b, when=ms(2026, 12, 22), who="Daphne")
    pg.goto(BASE + "#/bingo", wait_until="load"); pg.wait_for_timeout(500)
    LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    for ln in LINES:
        pg.click("#bg-reset"); pg.click("#bg-reset"); pg.wait_for_timeout(120)
        for idx in ln:
            pg.locator("#bg .bg-c").nth(idx).click(); pg.wait_for_timeout(40)
        check("F15 ligne %s reconnue" % ln, pg.locator("#bg .bg-c.win").count() == 3 and "1 ligne complète" in low(pg.text_content("#bg-n")), pg.text_content("#bg-n"))
    pg.click("#bg-reset"); pg.click("#bg-reset"); pg.wait_for_timeout(120)
    for idx in (0, 1, 3, 5, 7, 8):          # pas de ligne
        pg.locator("#bg .bg-c").nth(idx).click(); pg.wait_for_timeout(40)
    check("F16 six cases sans ligne : pas de bingo", pg.locator("#bg .bg-c.win").count() == 0)
    ctx.close()

    # ───────────────────────── G. carnet gourmand ─────────────────────────
    ctx, pg = newctx(b, when=ms(2026, 12, 22), who="Anne")
    pg.goto(BASE + "#/gourmand", wait_until="load"); pg.wait_for_timeout(500)
    n_food = sum(len(it) for _g, it in X.FOOD)
    rows = pg.locator("#v-gourmand .fd")
    check("G1 %d plats et boissons" % n_food, rows.count() == n_food == 24)
    check("G2 cinq cœurs par plat", rows.nth(0).locator(".fd-r button").count() == 5 and rows.locator(".fd-r button").count() == 5 * 24)
    r0 = rows.nth(0)
    r0.locator('.fd-r button[data-r="3"]').click(); pg.wait_for_timeout(100)
    check("G3 trois cœurs allumés, note 3 cochée", r0.locator(".fd-r button.on").count() == 3 and r0.locator('.fd-r button[aria-checked="true"]').get_attribute("data-r") == "3" and "tasted" in (r0.get_attribute("class") or ""))
    check("G4 compteur : 1 plat goûté sur 24", "1 plat goûté sur 24" in low(pg.text_content("#fd-n")), pg.text_content("#fd-n"))
    r0.locator('.fd-r button[data-r="3"]').click(); pg.wait_for_timeout(100)
    check("G5 même cœur : on efface", r0.locator(".fd-r button.on").count() == 0 and "tasted" not in (r0.get_attribute("class") or ""))
    ratings = [5, 4, 4, 3, 2, 5, 1, 3, 4, 5]
    for k, r in enumerate(ratings):
        rows.nth(k).locator('.fd-r button[data-r="%d"]' % r).click(); pg.wait_for_timeout(60)
        if k == 2:
            check("G6 trois plats notés : « Mon top 3 » apparaît", vis(pg, "#fd-top") and pg.locator("#fd-top-l li").count() == 3)
        if k == 8:
            check("G7 neuf plats : pas encore de tampon", "gourmand" not in stamps_b(pg))
    check("G8 dix plats → tampon « gourmand »", "gourmand" in stamps_b(pg), stamps_b(pg))
    tops = [low(x) for x in pg.locator("#fd-top-l li").all_text_contents()]
    check("G9 le top 3 est celui des meilleures notes (5 sur 5 d'abord)", len(tops) == 3 and all("5 sur 5" in t for t in tops), tops)
    pg.reload(wait_until="load"); pg.wait_for_timeout(450); go(pg, "#/gourmand")
    check("G10 notes gardées après rechargement", pg.locator("#v-gourmand .fd.tasted").count() == 10 and "10 plats goûtés sur 24" in low(pg.text_content("#fd-n")))
    go(pg, "#/jeux")
    check("G11 tuile du hub", "10 plats goûtés sur 24" in low(pg.locator('[data-hub="gourmand"]').text_content()), pg.locator('[data-hub="gourmand"]').text_content())
    # le nom en thaï se montre en grand, sans petit mot poli
    go(pg, "#/gourmand")
    pg.locator("#v-gourmand .fd-name").first.click(); pg.wait_for_timeout(300)
    check("G12 le nom du plat en thaï s'ouvre en grand", vis(pg, "#show") and pg.text_content("#show-th").strip() == X.FOOD[0][1][0][2])
    pg.click(".show-x"); pg.wait_for_timeout(250)
    ctx.close()

    # ───────────────────────── H. prix du voyage ─────────────────────────
    ctx, pg = newctx(b, when=ms(2027, 1, 3), who="Anne")
    pg.goto(BASE + "#/prix", wait_until="load"); pg.wait_for_timeout(500)
    check("H1 prix ouverts le 3 janvier", vis(pg, "#v-prix .gbody") and not vis(pg, "#v-prix .lkv"))
    aws = pg.locator("#v-prix .aw")
    check("H2 huit prix, quatre prénoms chacun", aws.count() == 8 == len(X.AWARDS) and aws.locator(".aw-c button").count() == 32)
    titles = [low(x) for x in aws.locator(".aw-h b").all_text_contents()]
    check("H3 titres des prix", [squash(t) for t in titles] == [squash(t) for _k, t, _s in X.AWARDS], titles)
    check("H4 pas de palmarès tant que tout n'est pas décerné", not vis(pg, "#aw-end"))
    pick = ["Anne", "Daphne", "Anne", "Flo", "Arthur", "Anne", "Daphne", "Flo"]
    for k, w in enumerate(pick):
        aws.nth(k).locator('.aw-c button[data-n="%s"]' % w).click(); pg.wait_for_timeout(80)
        if k == 0:
            check("H5 un prix décerné : prénom coché", aws.nth(0).locator('button[aria-checked="true"]').get_attribute("data-n") == "Anne" and "1 prix décerné sur 8" in low(pg.text_content("#aw-n")))
    check("H6 huit prix : palmarès + tampon", vis(pg, "#aw-end") and "prix" in stamps_b(pg), stamps_b(pg))
    tally = low(pg.text_content("#aw-tally"))
    check("H7 le grand gagnant est Anne (3 prix)", "anne (3 prix)" in tally and "anne 3" in tally and "daphne 2" in tally and "flo 2" in tally and "arthur 1" in tally, tally)
    # changer d'avis
    aws.nth(7).locator('.aw-c button[data-n="Arthur"]').click(); pg.wait_for_timeout(100)
    check("H8 on peut changer d'avis (Flo → Arthur)", aws.nth(7).locator('button[aria-checked="true"]').get_attribute("data-n") == "Arthur" and "arthur 2" in low(pg.text_content("#aw-tally")))
    aws.nth(7).locator('.aw-c button[data-n="Arthur"]').click(); pg.wait_for_timeout(100)
    check("H9 même prénom : on retire le prix", aws.nth(7).locator('button[aria-checked="true"]').count() == 0 and not vis(pg, "#aw-end"))
    aws.nth(7).locator('.aw-c button[data-n="Flo"]').click(); pg.wait_for_timeout(100)
    # l'image du palmarès
    pg.click("#aw-img"); pg.wait_for_timeout(1500)
    im = pg.locator("#aw-prev img")
    check("H10 l'image du palmarès est créée et montrée", vis(pg, "#aw-prev") and im.count() == 1)
    dims = pg.evaluate("(() => { const i = document.querySelector('#aw-prev img'); return i ? [i.naturalWidth, i.naturalHeight, i.src.slice(0, 5)] : null })()")
    check("H11 image 1080 × 1350, adresse blob:", dims and dims[0] == 1080 and dims[1] == 1350 and dims[2] == "blob:", dims)
    im.screenshot(path=OUT + "t30_palmares.png")
    pg.reload(wait_until="load"); pg.wait_for_timeout(450); go(pg, "#/prix")
    check("H12 prix gardés après rechargement", vis(pg, "#aw-end") and pg.locator("#v-prix .aw.set").count() == 8)
    pg.screenshot(path=OUT + "t30_prix.png", full_page=True)
    ctx.close()

    # ───────────────────────── I. passeport à 28 tampons, mascottes ─────────────────────────
    ctx, pg = newctx(b, when=ms(2026, 12, 22), who="Anne")
    pg.goto(BASE + "#/passeport", wait_until="load"); pg.wait_for_timeout(500)
    check("I1 28 cases (17 jours + 11 spéciaux)", pg.locator("#v-pass .slot").count() == 28 and pg.locator('#v-pass .slot[data-stamp="b"]').count() == 11 and pg.locator('#v-pass .slot[data-stamp="d"]').count() == 17)
    check("I2 « 0 sur 28 tampons »", "0 sur 28" in low(pg.inner_text("#v-pass .pp-top")), pg.inner_text("#v-pass .pp-top"))
    for k in ("defi", "bingo", "mot", "gourmand", "prix"):
        check("I3 tampon spécial %s présent" % k, pg.locator('#v-pass .slot[data-stamp="b"][data-id="%s"]' % k).count() == 1 and pg.locator('#v-pass .slot[data-stamp="b"][data-id="%s"] svg' % k).count() >= 1)
    ctx.close()
    ctx, pg = newctx(b, when=ms(2026, 12, 22), who="Anne")
    pg.goto(BASE + "#/mascottes", wait_until="load"); pg.wait_for_timeout(500)
    for key, want in [("aftonsparv", "dans la valise"), ("moomoo", "dans la valise"), ("boop", "à la maison"), ("minou", "à la maison")]:
        tag = low(pg.locator("#dd-%s .dd-where" % key).text_content())
        check("I4 %s : %s" % (key, want), want in tag, tag)
    how = low(pg.locator("#v-doudous .gbody .how").first.text_content())
    check("I5 phrase d'introduction", "aftonsparv" in how and "moomoo" in how and "voyagent" in how and "restent à la maison" in how, how)
    # les jours : les mots de Boop et Minou viennent « de la maison »
    for d_id, (mk, _t) in G.DAY_QUIPS.items():
        go(pg, "#/jours/" + d_id)
        g = low(pg.locator("#d-%s .guide b" % d_id).text_content())
        if mk in ("boop", "minou"):
            check("I6 %s : le mot de %s vient « de la maison »" % (d_id, mk), "de la maison" in g, g)
        else:
            check("I6 %s : %s voyage (pas « de la maison »)" % (d_id, mk), "de la maison" not in g, g)
        check("I7 %s : le raccourci vers le défi du jour" % d_id, pg.locator("#d-%s a.dfl" % d_id).get_attribute("href") == "#/defi/" + d_id)
    # le raccourci mène au bon jour
    go(pg, "#/jours/2026-12-22")
    pg.click("#d-2026-12-22 a.dfl"); pg.wait_for_timeout(400)
    check("I8 le raccourci ouvre le défi du 22 décembre", cur_view(pg) == "v-defi" and "22 décembre" in low(pg.locator("#v-defi .dn-t b").text_content()))
    ctx.close()

    # ───────────────────────── J. mise en page sur plusieurs écrans ─────────────────────────
    PAGES = ["#/jeux", "#/defi", "#/mot-du-jour", "#/bingo", "#/gourmand", "#/prix", "#/quiz", "#/mots-meles", "#/passeport", "#/mascottes", "#/horoscope", "#/blind-test"]
    for vw, vh in [(320, 640), (360, 740), (390, 844), (768, 1024)]:
        ctx, pg = newctx(b, vw=vw, vh=vh, when=ms(2026, 12, 29), who="Anne", master=True, dsf=1)
        pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(450)
        check("J %d : accueil sans défilement horizontal" % vw, pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
        for h in PAGES:
            go(pg, h, 350)
            vid = cur_view(pg)
            sw = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
            check("J %d %s : pas de défilement horizontal" % (vw, h), sw <= 1, sw)
            small = pg.evaluate("""() => {
                const v = document.querySelector('main.view:not([hidden])'); const out = [];
                v.querySelectorAll('button, a.btn, a.tile, .qz-o, summary').forEach(e => {
                    const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
                    if (r.width === 0 || r.height === 0 || cs.visibility === 'hidden') return;
                    if (r.height < 38 && !e.classList.contains('lk-link')) out.push((e.className || e.tagName) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
                }); return out; }""")
            if h in ("#/jeux", "#/defi", "#/mot-du-jour", "#/bingo", "#/gourmand", "#/prix"):
                check("J %d %s : zones à toucher assez hautes" % (vw, h), not small, small[:4])
            clip = pg.evaluate("""() => {
                const v = document.querySelector('main.view:not([hidden])'); const W = innerWidth; const out = [];
                v.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect(); if (r.width > 0 && (r.right > W + 1 || r.left < -1)) out.push((e.className && e.className.baseVal === undefined ? e.className : e.tagName) + ' ' + Math.round(r.left) + '→' + Math.round(r.right)); });
                return out.slice(0, 5); }""")
            check("J %d %s : rien ne dépasse de l'écran" % (vw, h), not clip, clip)
        ctx.close()

    print("erreurs JS :", errs if errs else "aucune")
    print("OK", ok_n, " ÉCHECS", fail_n)
    b.close()
