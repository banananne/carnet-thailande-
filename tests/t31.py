"""Traducteur français ⇄ thaï : écran, recueil hors réseau, recherche, traduction en ligne (réseau SIMULÉ : le conteneur ne peut pas joindre ces services),
solutions de repli, sens thaï → français, hors réseau, sécurité du texte reçu, mise en page."""
import sys, json, re, unicodedata
sys.path.insert(0, "/home/claude/site_en_ligne")
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright
import data_trad as T

BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
CORS = {"access-control-allow-origin": "*"}
ok_n = fail_n = 0
errs = []
ROWS = [(t, r) for t, rows in T.BOOK for r in rows]
N = len(ROWS)


def check(name, cond, info=""):
    global ok_n, fail_n
    if cond:
        ok_n += 1
    else:
        fail_n += 1
        print("  ✗", name, info)


def low(s):
    s = s.replace(" ", " ").replace(" ", " ").replace("⁠", "").replace("’", "'")
    return re.sub(r"\s+", " ", s).strip().lower()


def pnorm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c)).replace("œ", "oe").replace("æ", "ae")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9฀-๿]+", " ", s)).strip()


def thkey(s):
    s = re.sub(r"[\s.!?…]+", "", s)
    return re.sub(r"(นะคะ|นะครับ|ครับ|ค่ะ|คะ|นะ)+$", "", s)


class Net:
    """réseau simulé : deux services, chacun avec un mode de panne ; hold = la réponse de Google est retenue jusqu'à release()"""
    def __init__(self):
        self.g, self.m, self.other = [], [], []
        self.gmode, self.mmode, self.hold = "ok", "ok", False
        self.refs, self.held = [], []

    def release(self):
        held, self.held = self.held, []
        for route, args in held:
            route.fulfill(**args)

    def _send(self, route, **args):
        if self.hold:
            self.held.append((route, args))
        else:
            route.fulfill(**args)

    def google(self, route, request):
        self.g.append(request.url); self.refs.append(request.headers.get("referer"))
        q = parse_qs(urlparse(request.url).query); text = q["q"][0]; sl = q["sl"][0]
        m = self.gmode
        J = dict(status=200, headers=CORS, content_type="application/json")
        if m == "ok":
            if sl == "fr":
                body = [[["ขอบคุณมาก", text, None, None, 10], [None, None, "K̄hxbkhuṇ māk", text]], None, "fr"]
            else:
                body = [[["Je voudrais manger du riz sauté", text, None, None, 10], [None, None, "Je voudrais manger", "C̄hạn yāk kin k̄hâw p̄hạd"]], None, "th"]
            self._send(route, body=json.dumps(body), **J)
        elif m == "500": self._send(route, status=500, headers=CORS, content_type="text/plain", body="oups")
        elif m == "html": self._send(route, status=200, headers=CORS, content_type="text/html", body="<html>unusual traffic from your network</html>")
        elif m == "abort": route.abort()
        elif m == "same": self._send(route, body=json.dumps([[[text, text, None, None, 10]], None, sl]), **J)
        elif m == "empty": self._send(route, body="{}", **J)
        elif m == "xss": self._send(route, body=json.dumps([[["ไทย<img src=x onerror=window.__xss=1><b>gras</b>", text, None, None, 10]], None, "fr"]), **J)

    def mymemory(self, route, request):
        self.m.append(request.url)
        q = parse_qs(urlparse(request.url).query); text = q["q"][0]; lp = q["langpair"][0]
        m = self.mmode
        if m == "ok":
            tr = "สวัสดีค่ะ" if lp == "fr|th" else "C&#39;est bon &amp; simple"
            body = {"responseData": {"translatedText": tr, "match": 0.88}, "quotaFinished": False, "responseDetails": "", "responseStatus": 200, "matches": []}
        elif m == "quota":
            body = {"responseData": {"translatedText": "MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS FOR TODAY. NEXT AVAILABLE IN  05 HOURS 12 MINUTES 31 SECONDS", "match": ""},
                    "quotaFinished": True, "responseDetails": "MYMEMORY WARNING", "responseStatus": 429, "matches": ""}
        elif m == "same":
            body = {"responseData": {"translatedText": text, "match": 0}, "quotaFinished": False, "responseStatus": "200", "matches": []}
        elif m == "500":
            route.fulfill(status=503, headers=CORS, content_type="text/plain", body="down"); return
        route.fulfill(status=200, headers=CORS, content_type="application/json", body=json.dumps(body))


def newpage(b, net, vw=390, vh=844, ls=None, offline=False):
    ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2, is_mobile=vw < 700, has_touch=True, locale="fr-FR",
                        permissions=["clipboard-read", "clipboard-write"], service_workers="block")
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
    pg.on("console", lambda m: errs.append("CONSOLE " + m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)

    def watch(req):
        h = urlparse(req.url).hostname
        if h not in ("127.0.0.1", "localhost"):
            net.other.append(req.url)
    pg.on("request", watch)
    ctx.route("https://translate.googleapis.com/**", net.google)
    ctx.route("https://api.mymemory.translated.net/**", net.mymemory)
    if ls:
        ctx.add_init_script("try{if(!sessionStorage.getItem('__i')){sessionStorage.setItem('__i','1');%s}}catch(e){}" % ";".join("localStorage.setItem(%r,%r)" % kv for kv in ls.items()))
    if offline:
        ctx.set_offline(True)
    return ctx, pg


def go(pg, h, wait=300):
    pg.evaluate("location.hash=%r" % h); pg.wait_for_timeout(wait)


def vis(pg, sel):
    return pg.is_visible(sel)


def translate(pg, text, wait=500):
    pg.fill("#tr-in", text); pg.click("#tr-go"); pg.wait_for_timeout(wait)


with sync_playwright() as p:
    b = p.chromium.launch()

    # ───────────── A. l'entrée dans Utile, le titre, l'état de départ ─────────────
    net = Net()
    ctx, pg = newpage(b, net)
    pg.goto(BASE + "#/utile", wait_until="load"); pg.wait_for_timeout(450)
    tile = pg.locator('#v-utile a.tile[href="#/traduire"]')
    check("A1 tuile « Traducteur » dans Utile", tile.count() == 1 and "traducteur" in low(tile.inner_text()) and "thaï" in low(tile.inner_text()), tile.inner_text() if tile.count() else "")
    check("A2 la tuile a une icône", tile.locator("svg").count() >= 1)
    tile.click(); pg.wait_for_timeout(350)
    check("A3 l'écran s'ouvre", vis(pg, "#v-trad") and pg.evaluate("location.hash") == "#/traduire")
    check("A4 titre de l'onglet", pg.title() == "Traducteur · Carnet Thaïlande", pg.title())
    check("A5 l'onglet Utile reste allumé", pg.get_attribute('.nav a[aria-current="page"]', "data-nav") == "utile")
    check("A6 flèche retour vers Utile", pg.get_attribute("#v-trad .back", "href") == "#/utile")
    check("A7 titre de page", "traducteur" in low(pg.inner_text("#v-trad h1")))
    go(pg, "#/traducteur")
    check("A8 l'adresse #/traducteur marche aussi", vis(pg, "#v-trad"))
    check("A9 au départ : pas de résultat, pas de dernières traductions", not vis(pg, "#tr-out") and not vis(pg, "#tr-recent"))
    check("A10 sens français → thaï au départ", pg.get_attribute('[data-tdir="fr"]', "aria-pressed") == "true" and pg.get_attribute('[data-tdir="th"]', "aria-pressed") == "false")
    check("A11 champ : français, 200 signes, étiqueté", pg.get_attribute("#tr-in", "lang") == "fr" and pg.get_attribute("#tr-in", "maxlength") == "200"
          and pg.locator('label[for="tr-in"]').count() == 1 and "français" in low(pg.inner_text("#tr-lab")))
    fs = pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#tr-in')).fontSize)")
    fq = pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#tr-q')).fontSize)")
    check("A12 champs en 16 px au moins (pas de zoom sur iPhone)", fs >= 16 and fq >= 16, (fs, fq))
    priv = low(pg.inner_text("#v-trad .tr-priv"))
    check("A13 mention de confidentialité : réseau, service nommé, rien de personnel",
          "réseau" in priv and "envoyé" in priv and "google traduction" in priv and "mymemory" in priv and "rien de personnel" in priv and "sans réseau" in priv, priv)
    check("A14 aucune requête externe avant d'avoir touché « Traduire »", net.other == [] and net.g == [] and net.m == [], (net.other, net.g, net.m))
    pg.screenshot(path=OUT + "t31_start.png")
    ctx.close()

    # ───────────── B. le recueil hors réseau et sa recherche ─────────────
    net = Net()
    ctx, pg = newpage(b, net)
    pg.goto(BASE + "#/traduire", wait_until="load"); pg.wait_for_timeout(450)
    check("B1 %d phrases dans %d groupes" % (N, len(T.BOOK)), pg.locator("#tr-book .lx").count() == N == 86 and pg.locator("#tr-book .trg").count() == len(T.BOOK))
    check("B2 le total est écrit au-dessus de la recherche", ("dans les %d phrases" % N) in low(pg.inner_text(".tr-find label")))
    counts = pg.eval_on_selector_all("#tr-book .trg-n", "els => els.map(e => parseInt(e.textContent, 10))")
    check("B3 le nombre de phrases de chaque groupe est écrit", counts == [len(r) for _t, r in T.BOOK], counts)
    check("B4 groupes fermés au départ", pg.locator("#tr-book .trg[open]").count() == 0)
    pg.click("#tr-book .trg >> nth=0 >> summary"); pg.wait_for_timeout(150)
    check("B5 un groupe s'ouvre au toucher", pg.locator("#tr-book .trg[open]").count() == 1 and pg.locator("#tr-book .trg >> nth=0 >> .lx >> nth=0").is_visible())
    pg.click("#tr-book .trg >> nth=0 >> summary"); pg.wait_for_timeout(100)
    bad = pg.eval_on_selector_all("#tr-book .lx-main", """els => els.filter(e => !(e.dataset.th && /[\\u0e00-\\u0e7f]/.test(e.dataset.th) && e.dataset.rom && e.dataset.fr
        && e.hasAttribute('data-show'))).length""")
    check("B6 chaque ligne a thaï, prononciation, français", bad == 0, bad)
    sayb = pg.eval_on_selector_all("#tr-book .lx-say", "els => els.map(e => [e.hasAttribute('data-say'), e.dataset.th, e.hasAttribute('data-np')])")
    check("B7 chaque ligne a son haut-parleur (même thaï)", len(sayb) == N and all(s[0] and s[1] for s in sayb))
    nps = sum(1 for _t, r in ROWS if r[3])
    check("B8 petit mot poli : lignes sans mot poli (data-np) = %d" % nps, sum(1 for s in sayb if s[2]) == nps and pg.locator("#tr-book .lx-main[data-np]").count() == nps)
    qs = pg.eval_on_selector_all("#tr-book .lx-main", "els => els.map(e => e.dataset.q)")
    check("B9 les questions portent data-q=1", all((q == "1") == ("?" in r[0]) for q, (_t, r) in zip(qs, ROWS)), [(q, r[0]) for q, (_t, r) in zip(qs, ROWS) if (q == "1") != ("?" in r[0])])
    # unicité des phrases (pas de doublon français ni thaï)
    check("B10 aucun doublon dans le recueil", len({pnorm(r[0]) for _t, r in ROWS}) == N and len({r[2] for _t, r in ROWS}) == N)
    # recherche
    for query in ["gare", "piment", "PHARMACIE", "où est", "ou est la", "taxi", "kho", "ขอ", "hotel", "reservation", "ça ouvre", "a-han", "médecin", "xyzxyz", "  "]:
        pg.fill("#tr-q", query); pg.wait_for_timeout(120)
        toks = pnorm(query).split(" ") if pnorm(query) else []
        exp = [(t, r) for t, r in ROWS if not toks or all(tk in (pnorm(r[0] + " " + r[1]) + " " + thkey(r[2])) for tk in toks)]
        vis_rows = pg.locator("#tr-book .lx:not([hidden])").count()
        check("B11 recherche %r : %d ligne(s) attendue(s)" % (query, len(exp)), vis_rows == len(exp), vis_rows)
        gv = pg.eval_on_selector_all("#tr-book .trg", "els => els.map(e => [!e.hidden, e.open])")
        for gi, (t, rows) in enumerate(T.BOOK):
            has = any(tt == t for tt, _r in exp)
            check("B12 recherche %r : groupe %r %s" % (query, t, "ouvert" if has and toks else "caché" if toks else "fermé"),
                  (gv[gi][0] == (has or not toks)) and (gv[gi][1] == bool(has and toks)), gv[gi])
        check("B13 recherche %r : message « aucune phrase »" % query, vis(pg, "#tr-none") == bool(toks and not exp))
        bn = pg.eval_on_selector_all("#tr-book .trg-n", "els => els.map(e => parseInt(e.textContent, 10))")
        want = [sum(1 for tt, _r in exp if tt == t) if toks else len(rows) for t, rows in T.BOOK]
        check("B13b recherche %r : le badge de chaque groupe compte les phrases trouvées" % query, bn == want, (bn, want))
    pg.fill("#tr-q", "gare"); pg.wait_for_timeout(150)
    pg.screenshot(path=OUT + "t31_search.png", full_page=False)
    pg.fill("#tr-q", ""); pg.wait_for_timeout(150)
    check("B14b recherche effacée : les badges ont retrouvé le total de chaque groupe", pg.eval_on_selector_all("#tr-book .trg-n", "els => els.map(e => parseInt(e.textContent, 10))") == [len(r) for _t, r in T.BOOK])
    check("B14 recherche effacée : tout est revenu, groupes fermés", pg.locator("#tr-book .lx:visible").count() == 0 and pg.locator("#tr-book .trg:visible").count() == len(T.BOOK) and pg.locator("#tr-book .trg[open]").count() == 0)
    # montrer en grand une ligne du recueil
    pg.fill("#tr-q", "gare"); pg.wait_for_timeout(150)
    pg.click("#tr-book .lx:visible .lx-main >> nth=0"); pg.wait_for_timeout(300)
    check("B15 « montrer en grand » depuis le recueil", vis(pg, "#show") and pg.text_content("#show-th").startswith("สถานีรถไฟอยู่ที่ไหน"), pg.text_content("#show-th"))
    pg.click(".show-x"); pg.wait_for_timeout(250)
    check("B16 aucune requête réseau pendant la recherche", net.g == [] and net.m == [] and net.other == [])
    ctx.close()

    # ───────────── C. phrases déjà connues : réponse immédiate, sans réseau ─────────────
    net = Net()
    ctx, pg = newpage(b, net, ls={"carnet.pol": "kha"})
    pg.goto(BASE + "#/traduire", wait_until="load"); pg.wait_for_timeout(450)
    translate(pg, "Où est la gare ?", 250)
    check("C1 résultat affiché", vis(pg, "#tr-out"))
    check("C2 thaï, prononciation, français", pg.text_content("#tr-th") == "สถานีรถไฟอยู่ที่ไหน" and low(pg.text_content("#tr-rom")) == "sa-tha-ni rot fai yu thi nai ?" and low(pg.text_content("#tr-fr")) == "où est la gare ?",
          (pg.text_content("#tr-th"), pg.text_content("#tr-rom"), pg.text_content("#tr-fr")))
    check("C3 source : phrase toute prête, sans réseau ; pas d'avertissement", "phrase toute prête" in low(pg.text_content("#tr-src")) and not vis(pg, "#tr-warn"))
    check("C4 aucune requête réseau", net.g == [] and net.m == [] and net.other == [], (net.g, net.m))
    check("C5 boutons : Écouter (même thaï, mot poli permis), Montrer, Copier",
          pg.get_attribute("#tr-say", "data-th") == "สถานีรถไฟอยู่ที่ไหน" and pg.get_attribute("#tr-say", "data-np") is None and pg.get_attribute("#tr-say", "data-q") == "1"
          and pg.get_attribute("#tr-show", "data-th") == "สถานีรถไฟอยู่ที่ไหน" and vis(pg, "#tr-copy"))
    pg.click("#tr-show"); pg.wait_for_timeout(300)
    check("C6 « Montrer en grand » : le thaï + « คะ » (question, petit mot poli de Kha)", vis(pg, "#show") and pg.text_content("#show-th") == "สถานีรถไฟอยู่ที่ไหนคะ", pg.text_content("#show-th"))
    check("C7 la prononciation reçoit « kha »", pg.text_content("#show-rom").endswith("kha"), pg.text_content("#show-rom"))
    pg.click(".show-x"); pg.wait_for_timeout(250)
    for variant in ["ou est la gare", "OÙ EST LA GARE?", "  Où   est la   gare ?? "]:
        pg.fill("#tr-in", variant); pg.click("#tr-go"); pg.wait_for_timeout(120)
        check("C8 variante %r reconnue" % variant, pg.text_content("#tr-th") == "สถานีรถไฟอยู่ที่ไหน" and net.g == [])
    translate(pg, "merci", 200)
    check("C9 un mot du lexique : merci → ขอบคุณ (sans « ครับ »)", pg.text_content("#tr-th") == "ขอบคุณ" and "khop khun" in pg.text_content("#tr-rom"), pg.text_content("#tr-th"))
    translate(pg, "Bonjour", 200)
    check("C10 « Bonjour » (une des deux formes du lexique) → สวัสดี", pg.text_content("#tr-th") == "สวัสดี")
    translate(pg, "Au secours !", 200)
    check("C11 « Au secours ! » : pas de petit mot poli (data-np)", pg.text_content("#tr-th") == "ช่วยด้วย" and pg.get_attribute("#tr-say", "data-np") is not None)
    check("C12 les dernières traductions apparaissent (sans doublon)", vis(pg, "#tr-recent") and pg.locator("#tr-recent-l .lx").count() == 4, pg.locator("#tr-recent-l .lx").count())
    check("C13 la plus récente est en tête", "secours" in low(pg.locator("#tr-recent-l .lx .fr >> nth=0").text_content()))
    # Entrée envoie, Maj+Entrée saute une ligne
    pg.fill("#tr-in", "Je suis malade"); pg.press("#tr-in", "Enter"); pg.wait_for_timeout(200)
    check("C14 la touche Entrée traduit", pg.text_content("#tr-th") == "ไม่สบาย")
    pg.fill("#tr-in", "ligne un"); pg.press("#tr-in", "Shift+Enter"); pg.wait_for_timeout(100)
    check("C15 Maj+Entrée ajoute une ligne, ne traduit pas", "\n" in pg.input_value("#tr-in") and pg.text_content("#tr-th") == "ไม่สบาย")
    # Effacer
    pg.click("#tr-clear"); pg.wait_for_timeout(120)
    check("C16 « Effacer » vide le champ et cache le résultat", pg.input_value("#tr-in") == "" and not vis(pg, "#tr-out"))
    # champ vide
    pg.click("#tr-go"); pg.wait_for_timeout(120)
    check("C17 champ vide : message, rien n'est envoyé", "écris d" in low(pg.text_content("#tr-st")) and net.g == [])
    # mémoire après rechargement
    pg.reload(wait_until="load"); pg.wait_for_timeout(450); go(pg, "#/traduire")
    check("C18 les dernières traductions sont gardées après rechargement", vis(pg, "#tr-recent") and pg.locator("#tr-recent-l .lx").count() >= 4)
    pg.click("#tr-recent summary"); pg.wait_for_timeout(200)
    pg.click("#tr-recent-l .lx-main >> nth=0"); pg.wait_for_timeout(300)
    check("C19 une ancienne traduction se montre en grand", vis(pg, "#show") and pg.text_content("#show-th").startswith("ไม่สบาย"), pg.text_content("#show-th"))
    pg.click(".show-x"); pg.wait_for_timeout(250)
    pg.click("#tr-recent-x"); pg.wait_for_timeout(100)
    check("C20 « Vider la liste » demande une 2e touche", pg.locator("#tr-recent-l .lx").count() >= 4)
    pg.click("#tr-recent-x"); pg.wait_for_timeout(200)
    check("C21 liste vidée et cachée", not vis(pg, "#tr-recent") and pg.evaluate("localStorage.getItem('carnet.trad')") is None)
    ctx.close()

    # ───────────── D. traduction en ligne (Google Traduction simulé) ─────────────
    net = Net()
    ctx, pg = newpage(b, net)
    pg.goto(BASE + "#/traduire", wait_until="load"); pg.wait_for_timeout(450)
    FREE = "Je voudrais un taxi pour l’aéroport, s’il vous plaît"
    net.hold = True
    pg.fill("#tr-in", FREE); pg.click("#tr-go"); pg.wait_for_timeout(250)
    check("D1 pendant l'attente : bouton bloqué, message", pg.is_disabled("#tr-go") and pg.get_attribute("#tr-go", "aria-busy") == "true" and "en cours" in low(pg.text_content("#tr-st")))
    net.hold = False; net.release(); pg.wait_for_timeout(500)
    check("D2 une seule requête, au bon service", len(net.g) == 1 and len(net.m) == 0, (len(net.g), len(net.m)))
    u = urlparse(net.g[0]); qq = parse_qs(u.query)
    check("D3 l'adresse : Google, français vers thaï, texte tapé, texte seulement (pas de translittération demandée)", u.hostname == "translate.googleapis.com" and qq["sl"] == ["fr"] and qq["tl"] == ["th"] and qq["q"] == [FREE] and qq["dt"] == ["t"], qq)
    check("D4 aucune adresse de page envoyée (pas de Referer)", net.refs == [None], net.refs)
    check("D5 résultat : thaï et texte tapé ; pas de prononciation écrite (celle de Google est illisible) et aucun signe savant à l'écran", vis(pg, "#tr-out") and pg.text_content("#tr-th") == "ขอบคุณมาก" and not vis(pg, "#tr-rom") and pg.text_content("#tr-rom") == "" and pg.text_content("#tr-fr") == FREE
          and not re.search("[\u0300-\u036f\u1e00-\u1eff]", pg.inner_text("#v-trad")), pg.text_content("#tr-rom"))
    check("D6 source : Google Traduction ; avertissement visible, avec le renvoi vers « Écouter »", "google traduction" in low(pg.text_content("#tr-src")) and vis(pg, "#tr-warn") and "se tromper" in low(pg.text_content("#tr-warn")) and "écouter" in low(pg.text_content("#tr-warn")))
    check("D7 bouton de nouveau libre, message « Traduit »", not pg.is_disabled("#tr-go") and "traduit" in low(pg.text_content("#tr-st")))
    check("D8 Écouter/Montrer : sans petit mot poli (data-np), thaï du résultat", pg.get_attribute("#tr-say", "data-np") is not None and pg.get_attribute("#tr-say", "data-th") == "ขอบคุณมาก"
          and pg.get_attribute("#tr-show", "data-rom") == "" and pg.get_attribute("#tr-show", "data-fr") == FREE)
    pg.click("#tr-show"); pg.wait_for_timeout(300)
    check("D9 « Montrer en grand » : thaï seul, pastilles du petit mot poli cachées", pg.text_content("#show-th") == "ขอบคุณมาก" and not vis(pg, "#show-pol"))
    pg.click(".show-x"); pg.wait_for_timeout(250)
    pg.click("#tr-copy"); pg.wait_for_timeout(300)
    clip = pg.evaluate("navigator.clipboard.readText()")
    check("D10 « Copier » met le thaï dans le presse-papiers", clip == "ขอบคุณมาก", clip)
    check("D11 la traduction est dans les dernières", vis(pg, "#tr-recent") and pg.locator("#tr-recent-l .lx").count() == 1)
    # même phrase une 2e fois : refait une requête (pas de cache caché) et ne double pas la liste
    pg.fill("#tr-in", FREE); pg.click("#tr-go"); pg.wait_for_timeout(400)
    check("D12 même phrase : liste sans doublon", pg.locator("#tr-recent-l .lx").count() == 1 and len(net.g) == 2)
    pg.screenshot(path=OUT + "t31_result_fr.png")
    # texte reçu : jamais interprété comme du code
    net.gmode = "xss"
    translate(pg, "Un texte piégé", 500)
    check("D13 texte reçu affiché tel quel (pas de HTML, pas de script)", pg.evaluate("window.__xss") is None and pg.locator("#tr-th img, #tr-th b").count() == 0 and "<img" in pg.text_content("#tr-th"), pg.text_content("#tr-th"))
    ctx.close()

    # ───────────── E. solutions de repli ─────────────
    def scenario(name, gmode, mmode, text="Je cherche une pharmacie ouverte la nuit", dir_th=False, js_fill=False):
        net = Net(); net.gmode, net.mmode = gmode, mmode
        ctx, pg = newpage(b, net, ls={"carnet.trad.dir": "th"} if dir_th else None)
        pg.goto(BASE + "#/traduire", wait_until="load"); pg.wait_for_timeout(400)
        if js_fill:
            pg.evaluate("t => { document.querySelector('#tr-in').value = t; }", text); pg.click("#tr-go"); pg.wait_for_timeout(900)
        else:
            translate(pg, text, 900)
        shown = vis(pg, "#tr-out")
        res = {"shown": shown, "net": net, "th": pg.text_content("#tr-th"), "fr": pg.text_content("#tr-fr"), "src": low(pg.text_content("#tr-src")),
               "rom_vis": vis(pg, "#tr-rom"), "st": low(pg.text_content("#tr-st")), "busy": pg.is_disabled("#tr-go")}
        ctx.close()
        return res

    r = scenario("E1", "500", "ok")
    check("E1 Google en panne (500) → MyMemory répond", r["shown"] and r["th"] == "สวัสดีค่ะ" and "mymemory" in r["src"] and len(r["net"].g) == 1 and len(r["net"].m) == 1 and not r["rom_vis"], r)
    r = scenario("E2", "html", "ok")
    check("E2 Google répond autre chose que du JSON → MyMemory", r["shown"] and "mymemory" in r["src"] and len(r["net"].m) == 1, r["src"])
    r = scenario("E3", "abort", "ok")
    check("E3 Google injoignable → MyMemory", r["shown"] and "mymemory" in r["src"])
    r = scenario("E4", "same", "ok")
    check("E4 Google renvoie le texte tel quel (pas traduit) → MyMemory", r["shown"] and "mymemory" in r["src"])
    r = scenario("E5", "empty", "ok")
    check("E5 Google répond {} → MyMemory", r["shown"] and "mymemory" in r["src"])
    r = scenario("E6", "500", "quota")
    check("E6 MyMemory : limite du jour atteinte → message d'échec, pas de résultat", not r["shown"] and "n’a pas répondu".replace("’", "'") in r["st"] and not r["busy"], r["st"])
    r = scenario("E7", "500", "same")
    check("E7 MyMemory renvoie le texte tel quel → échec", not r["shown"] and "n'a pas répondu" in r["st"])
    r = scenario("E8", "500", "500")
    check("E8 les deux en panne → message clair, bouton libre", not r["shown"] and "n'a pas répondu" in r["st"] and not r["busy"] and len(r["net"].g) == 1 and len(r["net"].m) == 1)
    r = scenario("E9", "ok", "500", text="Je cherche une pharmacie ouverte la nuit")
    check("E9 Google répond : MyMemory n'est PAS contacté", r["shown"] and len(r["net"].m) == 0 and "google" in r["src"])
    r = scenario("E10", "500", "ok", text="ก" * 170, dir_th=True, js_fill=True)
    check("E10 thaï trop long pour MyMemory (> 480 octets) : pas d'envoi au service de secours", not r["shown"] and len(r["net"].m) == 0 and "n'a pas répondu" in r["st"], r["st"])

    # ───────────── F. sens thaï → français ─────────────
    net = Net()
    ctx, pg = newpage(b, net)
    pg.goto(BASE + "#/traduire", wait_until="load"); pg.wait_for_timeout(450)
    translate(pg, "Au secours", 150)
    check("F0 (préparation) un résultat est affiché", vis(pg, "#tr-out"))
    pg.click('[data-tdir="th"]'); pg.wait_for_timeout(200)
    check("F1 changer de sens cache le résultat et allume le bon bouton", not vis(pg, "#tr-out") and pg.get_attribute('[data-tdir="th"]', "aria-pressed") == "true")
    check("F2 champ : thaï, 120 signes, étiquette et exemple en thaï", pg.get_attribute("#tr-in", "lang") == "th" and pg.get_attribute("#tr-in", "maxlength") == "120"
          and "thaï" in low(pg.text_content("#tr-lab")) and re.search("[฀-๿]", pg.get_attribute("#tr-in", "placeholder") or ""))
    check("F3 le sens est gardé sur le téléphone", pg.evaluate("localStorage.getItem('carnet.trad.dir')") == "th")
    translate(pg, "สวัสดีครับ", 200)
    check("F4 thaï déjà connu (avec « ครับ ») → français, sans réseau", pg.text_content("#tr-fr") == "Bonjour, au revoir" and net.g == [] and pg.get_attribute("#tr-out", "data-dir") == "th", pg.text_content("#tr-fr"))
    yf = pg.evaluate("document.querySelector('.tr-f').getBoundingClientRect().top < document.querySelector('.tr-t').getBoundingClientRect().top")
    check("F5 en sens thaï → français, le français est au-dessus", yf)
    translate(pg, "ฉันอยากกินข้าวผัด", 600)
    check("F6 thaï libre → Google (th vers fr)", len(net.g) == 1 and parse_qs(urlparse(net.g[0]).query)["sl"] == ["th"] and parse_qs(urlparse(net.g[0]).query)["tl"] == ["fr"])
    check("F7 résultat : français du service, thaï tapé, pas de prononciation écrite ni de signes savants",
          pg.text_content("#tr-fr") == "Je voudrais manger du riz sauté" and pg.text_content("#tr-th") == "ฉันอยากกินข้าวผัด" and not vis(pg, "#tr-rom") and not re.search("[\u0300-\u036f\u1e00-\u1eff]", pg.inner_text("#v-trad")), (pg.text_content("#tr-fr"), pg.text_content("#tr-rom")))
    pg.click("#tr-copy"); pg.wait_for_timeout(250)
    check("F8 « Copier » : en sens thaï → français, on copie le français", pg.evaluate("navigator.clipboard.readText()") == "Je voudrais manger du riz sauté")
    pg.click("#tr-say"); pg.wait_for_timeout(200)       # ne doit pas planter (pas de voix dans le conteneur : un message s'affiche)
    pg.screenshot(path=OUT + "t31_result_th.png")
    # MyMemory : entités HTML décodées
    net.gmode = "500"
    translate(pg, "ดีมากเลย", 700)
    check("F9 MyMemory : « C&#39;est bon &amp; simple » est décodé", pg.text_content("#tr-fr") == "C'est bon & simple", pg.text_content("#tr-fr"))
    pg.reload(wait_until="load"); pg.wait_for_timeout(450); go(pg, "#/traduire")
    check("F10 sens gardé après rechargement", pg.get_attribute('[data-tdir="th"]', "aria-pressed") == "true" and pg.get_attribute("#tr-in", "lang") == "th")
    ctx.close()

    # ───────────── G. hors réseau, annulations, ordre des réponses ─────────────
    net = Net()
    ctx, pg = newpage(b, net)
    pg.goto(BASE + "#/traduire", wait_until="load"); pg.wait_for_timeout(450)
    ctx.set_offline(True); pg.wait_for_timeout(200)
    translate(pg, "Une phrase libre hors réseau", 300)
    check("G1 hors réseau : message clair, aucune tentative", "pas de réseau" in low(pg.text_content("#tr-st")) and not vis(pg, "#tr-out") and net.g == [] and net.m == [])
    translate(pg, "Où est l’hôpital ?", 200)
    check("G2 hors réseau : une phrase du recueil marche quand même", pg.text_content("#tr-th") == "โรงพยาบาลอยู่ที่ไหน")
    ctx.set_offline(False)
    # une réponse tardive après « Effacer » ne doit pas réapparaître
    net.hold = True
    translate(pg, "Un texte lent", 250)
    pg.click("#tr-clear"); net.release(); pg.wait_for_timeout(600)
    check("G3 « Effacer » pendant l'attente : la réponse tardive est ignorée", not vis(pg, "#tr-out") and pg.input_value("#tr-in") == "" and not pg.is_disabled("#tr-go"))
    # changer de sens pendant l'attente
    translate(pg, "Un autre texte lent", 250)
    pg.click('[data-tdir="th"]'); net.release(); pg.wait_for_timeout(600)
    check("G4 changement de sens pendant l'attente : la réponse tardive est ignorée", not vis(pg, "#tr-out") and not pg.is_disabled("#tr-go"))
    # deux touches rapides : une seule requête
    n0 = len(net.g)
    pg.click('[data-tdir="fr"]'); pg.fill("#tr-in", "Une phrase unique à traduire")
    pg.click("#tr-go"); pg.click("#tr-go", force=True); pg.wait_for_timeout(300)
    check("G5 double touche : une seule requête", len(net.g) - n0 == 1, len(net.g) - n0)
    net.hold = False; net.release(); pg.wait_for_timeout(400)
    ctx.close()

    # ───────────── H. mise en page, tailles de téléphone ─────────────
    for vw, vh in [(320, 640), (360, 740), (390, 844), (768, 1024)]:
        net = Net()
        ctx, pg = newpage(b, net, vw=vw, vh=vh, ls={"carnet.pol": "khrap"})
        pg.goto(BASE + "#/traduire", wait_until="load"); pg.wait_for_timeout(450)
        pg.fill("#tr-in", "Je voudrais un taxi pour l’aéroport, s’il vous plaît"); pg.click("#tr-go"); pg.wait_for_timeout(500)
        check("H %d : le résultat est visible à l'écran (défilement)" % vw, pg.evaluate("(() => { const r = document.querySelector('#tr-out').getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight; })()"))
        pg.click("#tr-recent summary"); pg.wait_for_timeout(150)
        pg.click("#tr-book .trg >> nth=3 >> summary"); pg.wait_for_timeout(200)
        sw = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
        check("H %d : pas de défilement horizontal" % vw, sw <= 1, sw)
        small = pg.evaluate("""() => { const out = []; document.querySelectorAll('#v-trad button, #v-trad summary, #v-trad input, #v-trad textarea').forEach(e => {
            const r = e.getBoundingClientRect(); if (!r.width || !r.height) return; const cs = getComputedStyle(e); if (cs.visibility === 'hidden') return;
            if (r.height < 38 || r.width < 38) out.push((e.id || e.className || e.tagName) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height)); }); return out; }""")
        check("H %d : zones à toucher assez grandes" % vw, not small, small[:5])
        clip = pg.evaluate("""() => { const W = innerWidth, out = []; document.querySelectorAll('#v-trad *').forEach(e => { const r = e.getBoundingClientRect();
            if (r.width > 0 && (r.right > W + 1 || r.left < -1)) out.push((e.id || e.className || e.tagName) + ' ' + Math.round(r.left) + '→' + Math.round(r.right)); }); return out.slice(0, 5); }""")
        check("H %d : rien ne dépasse de l'écran" % vw, not clip, clip)
        if vw in (320, 390):
            pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(150)
            pg.screenshot(path=OUT + "t31_layout_%d.png" % vw)
            pg.evaluate("document.querySelector('#tr-book').scrollIntoView()"); pg.wait_for_timeout(150)
            pg.screenshot(path=OUT + "t31_book_%d.png" % vw)
        ctx.close()

    print("erreurs JS :", errs if errs else "aucune")
    print("OK", ok_n, " ÉCHECS", fail_n)
    b.close()
