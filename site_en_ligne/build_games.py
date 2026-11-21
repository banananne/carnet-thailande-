# -*- coding: utf-8 -*-
"""Étape 3 : les jeux du carnet (pages écrites en HTML ici ; logique dans games.js ; styles dans games.css).
Données : data_test_doudou.json, data_horoscope.json, data_motsmeles.json (extraits du PDF), site_data.QUIZ, data_games.py."""
import functools, json, os, re, unicodedata

import site_data as D
import stamps as ST
import data_games as G
import build_app as A
from build_site import ROOT, icon, sticker

esc, txt, back_head = A.esc, A.txt, A.back_head


def jload(name):
    return json.load(open(os.path.join(ROOT, name), encoding="utf-8"))


def fix(s):
    """apostrophes droites → typographiques"""
    return s.replace("'", "’")


TEST = jload("data_test_doudou.json")
HORO = jload("data_horoscope.json")
MOTS = jload("data_motsmeles.json")
DD = {d["key"]: d for d in G.DOUDOUS}


def norm_word(w):
    """même règle que dans games.js : sans accents, sans majuscules, lettres et chiffres seulement"""
    w = unicodedata.normalize("NFD", w)
    w = "".join(c for c in w if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", w)


def fnv(w):
    """FNV-1a sur 32 bits (simple dissuasion : ce n'est pas un coffre-fort), identique à games.js"""
    h = 0x811C9DC5
    for ch in w:
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h


@functools.lru_cache(maxsize=None)
def photo_dims(fn):
    from PIL import Image
    with Image.open(os.path.join(ROOT, "img", fn)) as im:
        return im.size


def dd_img(key, cls="dd-img", lazy=True):
    d = DD[key]
    w, h = photo_dims(d["photo"])
    return ('<img class="%s" src="img/%s" width="%d" height="%d" alt="%s"%s decoding="async">'
            % (cls, d["photo"], w, h, esc(d["alt"]), ' loading="lazy"' if lazy else ""))


# ───────────────────────── accueil des jeux ─────────────────────────
# (couleur, adresse, icône, titre, sous-titre, identifiant du sous-titre, clé du cadenas)
HUB_DAILY = [
    ("blue", "#/defi", "camera", "Défi du jour", "Une mission photo et un rôle pour chacun", "defi", "defi"),
    ("rose", "#/mot-du-jour", "speech", "Mot du jour", "Un mot de thaï à dire chaque jour", "mot", "mot"),
    ("mustard", "#/bingo", "bingo", "Bingo", "9 choses à repérer en route", "bingo", "bingo"),
    ("sand", "#/gourmand", "fork", "Carnet gourmand", "Note les plats que tu goûtes", "gourmand", "gourmand"),
    ("sand", "#/passeport", "stamp", "Passeport", "Un tampon par jour", "pass", "pass"),
    ("rose", "#/mascottes", "paw", "Les mascottes", "Aftonsparv, Boop Boops, Minou, Moomoo", "doudous", "doudous"),
    ("blue", "#/prix", "award", "Prix du voyage", "Le palmarès du 3 janvier", "prix", "prix"),
]
HUB_BOOK = [
    ("sand", "#/quiz", "question", "Quiz du 26 décembre", "6 questions, un cocktail à la clé", "quiz", "quiz"),
    ("rose", "#/personnalite", "heart", "Test de personnalité", "Quelle mascotte es-tu ?", "doudou", "test"),
    ("blue", "#/blind-test", "music", "Blind test", "Le tableau des scores", "blind", "blind"),
    ("mustard", "#/mots-meles", "grid", "Mots mêlés", "40 mots à trouver", "mots", "mots"),
    ("blue", "#/horoscope", "star", "Horoscope", "Les astres ont parlé", "horo", "horo"),
]


def hub_tile(col, href, ic, t, sub, hid, gk):
    import build_days as BD
    import data_days as X
    opens = X.GATES[gk][1] if gk in X.GATES else G.TEST_OPEN_TXT
    # chaque tuile a son icône normale et un cadenas ; la classe « is-locked » (posée par le script) choisit
    pic = icon(ic).replace('class="i"', 'class="i ic-open"') + icon("lock").replace('class="i"', 'class="i ic-lock"')
    return ('<a class="tile %s gated%s" href="%s" data-gate="%s" data-opens="%s"><span class="ic">%s</span><span><b>%s</b><small data-hub="%s" data-def="%s">%s</small></span></a>'
            % (col, " lockable" if gk == "test" else "", href, gk, esc(opens), pic, txt(t), hid, esc(sub), txt(sub)))


def view_jeux():
    import build_days as BD
    import data_days as X
    out = ('<main class="view" id="v-jeux" data-gates="%s" data-k="%s" data-first="%s" data-last="%s" hidden>'
           '<header class="vhead"><div class="wrap"><div><h1 tabindex="-1">Jeux</h1><p>Pour la piscine, la route et les files d’attente</p></div></div></header>'
           '<div class="wrap"><a class="ddrow" href="#/mascottes" aria-label="Voir les quatre mascottes">'
           % (BD.gates_json(), BD.hashes(), X.DAY1, X.DAYN))
    for d in G.DOUDOUS:
        out += dd_img(d["key"], "dd-mini", lazy=False)
    out += '</a>'
    out += '<h2 class="sech navy">Au fil des jours</h2><div class="list">'
    out += "".join(hub_tile(*row) for row in HUB_DAILY)
    out += '</div><h2 class="sech navy">Les jeux du carnet</h2><div class="list">'
    out += "".join(hub_tile(*row) for row in HUB_BOOK)
    out += ('</div><p class="hub-try" id="hub-try" hidden><span>Mode essai : tout est ouvert sur ce téléphone.</span> '
            '<button class="lk-link" type="button" data-relock="1">Remettre les cadenas</button></p>')
    return out + "</div></main>"


# ───────────────────────── quiz du 26 décembre ─────────────────────────
def view_quiz():
    q = D.QUIZ
    n = len(q["qs"])
    out = ('<main class="view" id="v-quiz" hidden>' + back_head("Quiz", "Pour gagner un cocktail à la piscine", "#/jeux")
           + '<div class="wrap"><section class="qz" id="qz" data-n="%d" data-msgs="%s">' % (n, esc(json.dumps(G.QUIZ_MSGS, ensure_ascii=False))))
    out += ('<div class="bubble sand qz-intro" id="qz-intro"><div class="qz-st">%s</div><h2>%s</h2><p>%d questions sur ce que vous avez vu à Bangkok. '
            'Une seule bonne réponse chacune. Le meilleur score gagne un cocktail à la piscine.</p>'
            '<div class="acts"><button class="btn" type="button" data-qz="start">Commencer</button></div>'
            '<p class="qz-best" id="qz-best" hidden></p></div>' % (sticker("question"), txt(q["title"]), n))
    for i, (question, options, good) in enumerate(q["qs"]):
        out += ('<article class="qz-q" data-i="%d" data-good="%d" hidden><p class="qz-n">Question %d sur %d</p>'
                '<div class="qz-bar" aria-hidden="true"><i style="width:%d%%"></i></div><h2 class="qz-t">%s</h2><div class="qz-opts">'
                % (i, good, i + 1, n, round(100 * i / n), txt(question)))
        for k, o in enumerate(options):
            out += '<button class="qz-o" type="button" data-k="%d"><b>%s</b><span>%s</span></button>' % (k, "ABC"[k], txt(o))
        out += ('</div><p class="qz-fb" role="status" hidden></p><div class="acts"><button class="btn" type="button" data-qz="next" hidden>%s</button></div></article>'
                % ("Question suivante" if i < n - 1 else "Voir mon score"))
    out += ('<div class="bubble rose qz-end" id="qz-end" hidden><div class="qz-st">%s</div><p class="qz-score"><b id="qz-s">0</b> / %d</p>'
            '<p class="qz-msg" id="qz-msg" role="status"></p><div class="acts"><button class="btn" type="button" data-qz="again">Rejouer</button>'
            '<a class="btn alt" href="#/jeux">Les autres jeux</a></div></div>' % (sticker("trophee"), n))
    out += "</section></div></main>"
    return out


def quiz_cta():
    """Sur la page du 26 décembre : un bouton vers le quiz (les réponses n'y sont plus affichées)."""
    q = D.QUIZ
    return ('<h3 class="sech">%s</h3><p class="sub">%s</p>'
            '<a class="tile sand qz-cta" href="#/quiz"><span class="ic">%s</span><span><b>Jouer au quiz</b><small>%d questions sur les visites de Bangkok</small></span></a>'
            % (txt(q["title"]), txt(q["sub"]), icon("question"), len(q["qs"])))


# ───────────────────────── les doudous : fiches + test ─────────────────────────
def split_title(t):
    t = re.sub(r"^Tu es ", "", t)
    name, _, epithet = t.partition(", ")
    return name, epithet


TRAVEL = {"aftonsparv": True, "moomoo": True, "boop": False, "minou": False}


def where_tag(key):
    """Seuls Aftonsparv et Moomoo voyagent ; Boop Boops et Minou restent à la maison."""
    if TRAVEL[key]:
        return '<span class="dd-where in">%s Dans la valise</span>' % icon("check")
    return '<span class="dd-where out">%s À la maison, écrit de loin</span>' % icon("home")


def dd_card(key):
    d = DD[key]
    c = TEST["cards"][key]
    name, epithet = split_title(c["title"])
    out = ('<article class="dd-card" id="dd-%s" data-who="%s" style="--dd:%s"><div class="dd-top">%s<div><p class="dd-kick">%s</p><h2>%s</h2>%s</div></div>'
           '<p class="dd-body">%s</p><dl class="dd-facts">' % (key, key, d["bg"], dd_img(key), txt(name), txt(epithet[:1].upper() + epithet[1:]), where_tag(key), txt(c["body"])))
    for lab in ("SUPER-POUVOIR", "POINT FAIBLE", "ALLIÉ", "TON ENDROIT DU VOYAGE"):
        out += "<div><dt>%s</dt><dd>%s</dd></div>" % (txt(lab.capitalize()), txt(c[lab]))
    out += '</dl><p class="dd-quote">%s</p></article>' % txt(c["quote"])
    return out


def view_doudous():
    out = ('<main class="view" id="v-doudous" hidden>' + back_head("Les mascottes", "Deux voyagent, deux écrivent de loin", "#/jeux")
           + '<div class="wrap"><p class="how">Quatre mascottes, quatre caractères. <b>Aftonsparv</b> et <b>Moomoo</b> voyagent avec vous. '
             '<b>Boop Boops</b> et <b>Minou</b> restent à la maison et vous écrivent de loin.</p>'
           '<div class="acts dd-go"><a class="btn" href="#/personnalite">%s Quelle est la mienne ?</a></div>'
           '<p class="how dd-wait">%s Le test pour trouver ta mascotte s’ouvre le %s.</p><div class="ddlist">' % (icon("heart"), icon("lock"), G.TEST_OPEN_TXT))
    for d in G.DOUDOUS:
        out += dd_card(d["key"])
    return out + "</div></div></main>"


def view_test():
    qs = TEST["questions"]
    n = len(qs)
    intro = ("Pour chaque question, choisis la réponse qui te ressemble vraiment, pas celle que tu aimerais être. "
             "À la fin, la mascotte qui revient le plus souvent est la tienne. Égalité ? Tes amis tranchent.")
    out = ('<main class="view" id="v-test" hidden>' + back_head("Test de personnalité", "Quelle mascotte es-tu ?", "#/jeux")
           + '<div class="wrap"><section class="dt" id="dt" data-n="%d" data-open="%s" data-k="%s">'
           % (n, G.TEST_OPEN, ",".join(str(fnv(norm_word(w))) for w in G.TEST_WORDS)))
    out += ('<div class="bubble sand dt-lock" id="dt-lock" hidden><div class="dd-four dd-sleep">%s</div>'
            '<h2><span class="lk-ic">%s</span>Pas encore !</h2>'
            '<p>Les mascottes ont besoin de vous observer encore un peu avant de deviner qui vous êtes. Le test s’ouvre le <b>%s</b>.</p>'
            '<button class="lk-link" type="button" data-lk="ask">J’ai le mot secret</button>'
            '<form class="lk-form" id="lk-form" hidden autocomplete="off"><label for="lk-in">Mot secret</label>'
            '<div class="lk-row"><input id="lk-in" name="mot" type="text" autocapitalize="none" autocorrect="off" spellcheck="false" enterkeyhint="go" maxlength="40">'
            '<button class="btn" type="submit">Ouvrir</button></div><p class="lk-err" id="lk-err" role="status"></p></form></div>'
            % ("".join(dd_img(d["key"], "dd-mini", lazy=False) for d in G.DOUDOUS), icon("lock"), G.TEST_OPEN_TXT))
    out += ('<div class="bubble rose dt-intro" id="dt-intro"><div class="dd-four">%s</div><h2>Quelle mascotte es-tu ?</h2><p>%s</p>'
            '<div class="acts"><button class="btn" type="button" data-dt="start">Commencer</button></div>'
            '<div id="dt-last" hidden><p class="dt-lastp">Ton dernier résultat : <b id="dt-lastn"></b></p><div class="acts"><button class="btn alt" type="button" data-dt="last">Revoir ma mascotte</button></div></div>'
            '<button class="lk-link" id="lk-relock" type="button" data-lk="relock" hidden>Remettre le cadenas</button></div>'
            % ("".join(dd_img(d["key"], "dd-mini", lazy=False) for d in G.DOUDOUS), txt(intro)))
    for i, q in enumerate(qs):
        out += ('<article class="dt-q" data-i="%d" hidden><p class="qz-n">Question %d sur %d</p><div class="qz-bar" aria-hidden="true"><i style="width:%d%%"></i></div>'
                '<h2 class="qz-t">%s</h2><div class="qz-opts">' % (i, i + 1, n, round(100 * i / n), txt(q["q"])))
        for o in q["opts"]:
            out += '<button class="qz-o" type="button" data-who="%s"><span>%s</span></button>' % (o["who"], txt(o["t"]))
        out += '</div><div class="acts"><button class="btn sm alt" type="button" data-dt="prev"%s>%s Précédente</button></div></article>' % (" hidden" if i == 0 else "", icon("chevl"))
    out += ('<div class="bubble sand dt-tie" id="dt-tie" hidden><h2>Égalité !</h2><p id="dt-tiep"></p><div class="dt-ties" id="dt-ties"></div></div>'
            '<div class="dt-res" id="dt-res" hidden></div>')
    return out + "</section></div></main>"


# ───────────────────────── blind test ─────────────────────────
def view_blind():
    out = ('<main class="view" id="v-blind" hidden>' + back_head("Blind test", "Le tableau des scores", "#/jeux")
           + '<div class="wrap"><p class="how">Touche le prénom de celui ou celle qui a trouvé : <b>+1 point</b>. Le bouton « − » sert à corriger.</p>'
           '<div class="bt" id="bt">')
    for name, bg, fg in G.PLAYERS:
        out += ('<article class="bt-p" data-n="%s" style="--bg:%s;--fg:%s"><button class="bt-main" type="button" aria-label="Un point pour %s">'
                '<span class="bt-name">%s</span><b class="bt-score" data-score>0</b><span class="bt-crown" aria-hidden="true">%s</span></button>'
                '<button class="bt-minus" type="button" aria-label="Retirer un point à %s">%s</button></article>'
                % (name, bg, fg, name, name, sticker("trophee"), name, icon("minus")))
    out += '</div><p class="bt-lead" id="bt-lead" role="status"></p><div class="acts">'
    if G.PLAYLIST_URL:
        out += '<a class="btn" href="%s" target="_blank" rel="noopener noreferrer">%s La playlist</a>' % (esc(G.PLAYLIST_URL), icon("music"))
    out += '<button class="btn alt" type="button" id="bt-reset">%s <span>Remettre à zéro</span></button></div>' % icon("refresh")
    out += '<div class="bt-stk" aria-hidden="true">%s%s%s</div>' % (sticker("micro"), sticker("vinyle"), sticker("buzzer"))
    return out + "</div></main>"


# ───────────────────────── mots mêlés ─────────────────────────
def view_mots():
    n = MOTS["n"]
    cells = "".join('<span class="c">%s</span>' % ch for row in MOTS["grid"] for ch in row)
    words = sorted(MOTS["words"], key=lambda w: unicodedata.normalize("NFD", w["w"]))
    data = [[w["k"], w["r"], w["c"], w["dr"], w["dc"]] for w in MOTS["words"]]
    lis = "".join('<li data-k="%s"><i></i><span>%s</span></li>' % (w["k"], txt(w["w"])) for w in words)
    out = ('<main class="view" id="v-mots" hidden>' + back_head("Mots mêlés", "%d mots à trouver" % len(words), "#/jeux")
           + '<div class="wrap"><p class="how">Fais glisser ton doigt sur un mot, dans tous les sens (même en diagonale ou à l’envers). '
           'Ou touche la première lettre, puis la dernière.</p>'
           '<div class="mm-top"><p><b id="mm-count">0</b> sur %d</p><div class="mm-bar" aria-hidden="true"><i id="mm-fill"></i></div></div>'
           '<div class="mm-card" id="mm-card" data-zoom="0"><p class="mm-live" id="mm-live" aria-live="polite">&nbsp;</p>'
           '<div class="mm-scroll" id="mm-scroll"><div class="mm-board" id="mm-board" data-n="%d" data-words="%s" role="group" aria-label="Grille de mots mêlés">'
           '<div class="mm-grid" aria-hidden="true">%s</div>'
           '<svg class="mm-ov" id="mm-ov" viewBox="0 0 %d %d" preserveAspectRatio="none" aria-hidden="true"><g id="mm-found"></g><g id="mm-ref"></g><g id="mm-sel"></g></svg>'
           '</div></div></div>'
           '<div class="acts mm-acts"><button class="btn sm alt" type="button" id="mm-zoom" aria-pressed="false">%s <span>Agrandir</span></button>'
           '<button class="btn sm alt" type="button" id="mm-hint">%s Un indice</button>'
           '<button class="btn sm alt" type="button" id="mm-reset">%s <span>Recommencer</span></button></div>'
           '<h3 class="sech navy">Les mots</h3><ul class="mm-words" id="mm-words">%s</ul></div></main>'
           % (len(words), n, esc(json.dumps(data, separators=(",", ":"))), cells, n, n, icon("zoomin"), icon("bulb"), icon("refresh"), lis))
    return out


# ───────────────────────── horoscope ─────────────────────────
ELEM = {"feu": "Feu", "terre": "Terre", "air": "Air", "eau": "Eau"}


def sky_svg(s):
    def px(v):
        return 10 + 80 * v
    out = '<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false">'
    for i, j in s["lines"]:
        a, b = s["stars"][i], s["stars"][j]
        out += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (px(a[0]), px(a[1]), px(b[0]), px(b[1]))
    for x, y, r in s["stars"]:
        out += '<circle cx="%.1f" cy="%.1f" r="%.1f"/>' % (px(x), px(y), 1.5 + 2.3 * r)
    return out + "</svg>"


def view_horo():
    out = ('<main class="view" id="v-horo" hidden>' + back_head("Horoscope", "Les astres ont parlé", "#/jeux")
           + '<div class="wrap"><div class="bubble sand hs-intro"><div class="qz-st">%s</div><p>Les astres ont parlé : voici ce qui vous attend entre Bangkok, Sukhothaï et Koh Samet.</p></div>'
           '<div class="hslist">' % sticker("etoile"))
    for s in HORO:
        sid = unicodedata.normalize("NFD", s["name"].lower()).encode("ascii", "ignore").decode()
        out += ('<article class="hs el-%s" id="hs-%s"><div class="hs-top"><div class="hs-sky">%s</div><div><h2>%s</h2><p class="hs-el">%s</p></div></div>'
                '<p class="hs-text">%s</p><div class="hs-foot"><button class="lx-say" type="button" data-say data-np="1" data-th="%s" data-q="0" aria-label="Écouter : %s">%s</button>'
                '<p><span class="hs-w">Mot du voyage</span><b>%s</b> <span class="th" lang="th">%s</span><small>%s</small></p>'
                '<p class="hs-day"><span>Jour de chance</span><b>%s</b></p></div></article>'
                % (s["el"], sid, sky_svg(s), txt(s["name"]), ELEM[s["el"]], txt(fix(s["text"])), esc(s["th"]), esc(s["mot"]), icon("speaker"),
                   esc(s["mot"]), esc(s["th"]), txt(fix(s["mean"])), txt(s["chance"])))
    return out + "</div></div></main>"


# ───────────────────────── passeport ─────────────────────────
ROT = [-9, 6, -4, 9, -7, 4, -11, 8, -3, 11, -6, 5, -10, 7, -2, 10, -5, 3, -8, 6, -4, 9, -7]


def day_stamp(i, d):
    """Tampon d'un jour : cadre, encre et petit dessin propres à la journée (voir stamps.DAY_SPEC)."""
    dt = A.dparse(d["id"])
    stage = d["stage"]
    city = "PARIS · BANGKOK" if stage == "vol" else D.STAGE[stage]["city"].upper()
    shape, color, picto = ST.DAY_SPEC[d["id"]]
    mon = A.MO3[dt.month - 1].replace(".", "").upper()
    rot = ROT[i % len(ROT)]
    if shape == "banner":
        rot = max(-4, min(4, rot))
    return ST.stamp_svg("st%d" % i, shape, G.STAMP_WORDS[d["id"]], ST.P[picto], "%d %s" % (dt.day, mon), city, color, rot)


def bonus_stamp(j, key, word):
    shape, color, picto = ST.BONUS_SPEC[key]
    city = "TAMPON SPÉCIAL" if shape in ("round", "arch", "postage", "banner") else ""
    rot = ROT[(j * 3 + 5) % len(ROT)]
    if shape == "banner":
        rot = max(-4, min(4, rot))
    top = {"postmark": "2026", "hex": "THAÏLANDE", "arch": "THAÏLANDE", "octagon": "THAÏLANDE", "postage": "THAÏLANDE", "oval": "THAÏLANDE"}.get(shape, "THAÏLANDE 2026")
    return ST.stamp_svg("sb%d" % j, shape, top, ST.P[picto], word, city, color, rot)


INK_FILTER = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
              '<filter id="ink" x="-6%" y="-6%" width="112%" height="112%" color-interpolation-filters="sRGB">'
              '<feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="4" result="n"/>'
              '<feDisplacementMap in="SourceGraphic" in2="n" scale="1.25" xChannelSelector="R" yChannelSelector="G" result="w"/>'
              '<feTurbulence type="fractalNoise" baseFrequency="0.45" numOctaves="2" seed="11" result="m"/>'
              '<feColorMatrix in="m" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -3.4 2.8" result="holes"/>'
              '<feComposite in="w" in2="holes" operator="in"/></filter></defs></svg>')


def view_pass():
    out = ('<main class="view" id="v-pass" hidden>' + back_head("Passeport", "Un tampon par jour", "#/jeux")
           + '<div class="wrap"><p class="how">Touche une case pour la <b>tamponner</b>. Une photo du jour enregistrée tamponne la case toute seule. '
           'Les tampons spéciaux se gagnent en jouant.</p>'
           '<div class="pp-top"><p><b id="pp-count">0</b> sur %d tampons</p><div class="mm-bar" aria-hidden="true"><i id="pp-fill"></i></div></div>'
           '<section class="pp" aria-label="Les jours du voyage"><h2 class="sech navy">Les jours</h2><div class="pp-grid">'
           % (len(D.DAYS) + len(G.BONUS_STAMPS)))
    for i, d in enumerate(D.DAYS):
        dt = A.dparse(d["id"])
        out += ('<button class="slot" type="button" data-stamp="d" data-id="%s" data-word="%s" aria-pressed="false" aria-label="%s">'
                '<span class="slot-ph d"><i>%s</i><b>%d</b><small>%s</small></span>%s</button>'
                % (d["id"], esc(G.STAMP_WORDS[d["id"]].capitalize()), esc("Tampon du " + A.day_title(d["id"]).lower()), ST.picto_icon(ST.DAY_SPEC[d["id"]][2]), dt.day, A.MO3[dt.month - 1], day_stamp(i, d)))
    out += '</div></section><section class="pp" aria-label="Tampons spéciaux"><h2 class="sech navy">Les tampons spéciaux</h2><div class="pp-grid">'
    for j, (key, word, title, how) in enumerate(G.BONUS_STAMPS):
        out += ('<button class="slot" type="button" data-stamp="b" data-id="%s" data-how="%s" data-title="%s" aria-pressed="false" aria-label="%s">'
                '<span class="slot-ph"><i>%s</i><small>%s</small></span>%s</button>'
                % (key, esc(how), esc(title), esc("Tampon spécial : " + title), ST.picto_icon(ST.BONUS_SPEC[key][2]), esc(title), bonus_stamp(j, key, word)))
    out += ('</div></section><div class="acts"><button class="btn sm alt" type="button" id="pp-reset">%s <span>Effacer tous les tampons</span></button></div></div></main>' % icon("refresh"))
    return out


# ───────────────────────── petites pièces pour les autres pages ─────────────────────────
def guide_html(day_id):
    q = G.DAY_QUIPS.get(day_id)
    if not q:
        return ""
    key, text = q
    d = DD[key]
    return ('<a class="guide" href="#/mascottes" style="--dd:%s">%s<p><b>%s%s</b>%s</p></a>'
            % (d["bg"], dd_img(key, "guide-img"), txt(d["short"]), "" if TRAVEL[key] else " · de la maison", txt("« %s »" % text)))


def day_stamp_html(day_id):
    return ('<div class="dstamp" data-day="%s"><button class="btn sm alt" type="button" data-stamp-day="%s">%s <span>Tamponner ce jour</span></button>'
            '<span class="dstamp-svg"></span></div>' % (day_id, day_id, icon("stamp")))


def home_quip_html():
    key, text = G.HOME_QUIPS[9]   # Moomoo, « Cinq minutes de plus ? » : première phrase affichée, le reste est tiré au hasard
    d = DD[key]
    data = esc(json.dumps([[k, t] for k, t in G.HOME_QUIPS], ensure_ascii=False, separators=(",", ":")))
    imgs = {k: "img/" + DD[k]["photo"] for k in DD}
    return ('<section class="bubble blue hq" id="hq" aria-labelledby="h-hq" data-q="%s" data-img="%s">'
            '<h2 id="h-hq">Le mot de la mascotte</h2><div class="hq-in"><button class="hq-btn" type="button" id="hq-btn" aria-label="Un autre mot de la mascotte">'
            '%s<span class="hq-t"><b id="hq-who">%s</b><span id="hq-q">%s</span></span></button></div>'
            '<p class="hq-hint">Touche la mascotte pour un autre mot.</p></section>'
            % (data, esc(json.dumps(imgs)), dd_img(key, "hq-img", lazy=False).replace("<img ", '<img id="hq-img" ', 1), txt(d["short"]), txt("« %s »" % text)))


def all_views():
    import build_days as BD
    g = BD.gate
    return (view_jeux() + g("quiz", view_quiz()) + view_test() + g("doudous", view_doudous()) + g("blind", view_blind()) + g("mots", view_mots())
            + g("horo", view_horo()) + g("pass", view_pass()) + BD.all_views() + INK_FILTER)
