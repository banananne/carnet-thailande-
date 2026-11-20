# -*- coding: utf-8 -*-
"""Étape 3 : les jeux du carnet (pages écrites en HTML ici ; logique dans games.js ; styles dans games.css).
Données : data_test_doudou.json, data_horoscope.json, data_motsmeles.json (extraits du PDF), site_data.QUIZ, data_games.py."""
import json, os, re, unicodedata

import site_data as D
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
HUB = [
    ("sand", "#/quiz", "question", "Quiz du 26 décembre", "6 questions, un cocktail à la clé", "quiz"),
    ("rose", "#/personnalite", "heart", "Test de personnalité", "Quelle mascotte es-tu ?", "doudou"),
    ("blue", "#/blind-test", "music", "Blind test", "Le tableau des scores", "blind"),
    ("mustard", "#/mots-meles", "grid", "Mots mêlés", "40 mots à trouver", "mots"),
    ("blue", "#/horoscope", "star", "Horoscope", "Les astres ont parlé", "horo"),
    ("sand", "#/passeport", "stamp", "Passeport", "Un tampon par jour", "pass"),
    ("rose", "#/mascottes", "paw", "Les mascottes", "Aftonsparv, Boop Boops, Minou, Moomoo", "doudous"),
]


def view_jeux():
    out = ('<main class="view" id="v-jeux" hidden>'
           '<header class="vhead"><div class="wrap"><div><h1 tabindex="-1">Jeux</h1><p>Pour la piscine, la route et les files d’attente</p></div></div></header>'
           '<div class="wrap"><a class="ddrow" href="#/mascottes" aria-label="Voir les quatre mascottes">')
    for d in G.DOUDOUS:
        out += dd_img(d["key"], "dd-mini", lazy=False)
    out += '</a><div class="list">'
    for col, href, ic, t, sub, hid in HUB:
        out += ('<a class="tile %s" href="%s"><span class="ic">%s</span><span><b>%s</b><small data-hub="%s" data-def="%s">%s</small></span></a>'
                % (col, href, icon(ic), txt(t), hid, esc(sub), txt(sub)))
    return out + "</div></div></main>"


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


def dd_card(key):
    d = DD[key]
    c = TEST["cards"][key]
    name, epithet = split_title(c["title"])
    out = ('<article class="dd-card" id="dd-%s" data-who="%s" style="--dd:%s"><div class="dd-top">%s<div><p class="dd-kick">%s</p><h2>%s</h2></div></div>'
           '<p class="dd-body">%s</p><dl class="dd-facts">' % (key, key, d["bg"], dd_img(key), txt(name), txt(epithet[:1].upper() + epithet[1:]), txt(c["body"])))
    for lab in ("SUPER-POUVOIR", "POINT FAIBLE", "ALLIÉ", "TON ENDROIT DU VOYAGE"):
        out += "<div><dt>%s</dt><dd>%s</dd></div>" % (txt(lab.capitalize()), txt(c[lab]))
    out += '</dl><p class="dd-quote">%s</p></article>' % txt(c["quote"])
    return out


def view_doudous():
    out = ('<main class="view" id="v-doudous" hidden>' + back_head("Les mascottes", "Elles voyagent avec vous", "#/jeux")
           + '<div class="wrap"><p class="how">Quatre mascottes, quatre caractères. Elles ont leur avis sur tout, et elles vous guident jour après jour.</p>'
           '<div class="acts"><a class="btn" href="#/personnalite">%s Quelle est la mienne ?</a></div><div class="ddlist">' % icon("heart"))
    for d in G.DOUDOUS:
        out += dd_card(d["key"])
    return out + "</div></div></main>"


def view_test():
    qs = TEST["questions"]
    n = len(qs)
    intro = ("Pour chaque question, choisis la réponse qui te ressemble vraiment, pas celle que tu aimerais être. "
             "À la fin, la mascotte qui revient le plus souvent est la tienne. Égalité ? Tes amis tranchent.")
    out = ('<main class="view" id="v-test" hidden>' + back_head("Test de personnalité", "Quelle mascotte es-tu ?", "#/jeux")
           + '<div class="wrap"><section class="dt" id="dt" data-n="%d">' % n)
    out += ('<div class="bubble rose dt-intro" id="dt-intro"><div class="dd-four">%s</div><h2>Quelle mascotte es-tu ?</h2><p>%s</p>'
            '<div class="acts"><button class="btn" type="button" data-dt="start">Commencer</button></div>'
            '<div id="dt-last" hidden><p class="dt-lastp">Ton dernier résultat : <b id="dt-lastn"></b></p><div class="acts"><button class="btn alt" type="button" data-dt="last">Revoir ma mascotte</button></div></div></div>'
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
INK = {"vol": "#283881", "s1": "#A51C36", "s2": "#B25E00", "s3": "#283881", "s4": "#6B2F7A"}
BONUS_INK = ["#1E7B4F", "#6B2F7A", "#0F6B73", "#A51C36", "#283881", "#B25E00"]
ROT = [-9, 6, -4, 9, -7, 4, -11, 8, -3, 11, -6, 5, -10, 7, -2, 10, -5, 3, -8, 6, -4, 9, -7]
ARC_TOP = "M 21.5 60 A 38.5 38.5 0 0 1 98.5 60"
ARC_BOT = "M 15.5 60 A 44.5 44.5 0 0 0 104.5 60"


def fit(s, width, mx):
    return max(6.5, min(mx, width / (max(1, len(s)) * 0.6)))


def stamp_svg(uid, shape, top, big, small, bottom, color, rot, picto=None):
    """Tampon de passeport dessiné à la main (SVG), encre irrégulière grâce au filtre #ink défini une fois dans la page."""
    g = '<g transform="rotate(%d 60 60)" filter="url(#ink)" fill="none" stroke="currentColor" stroke-linecap="round">' % rot
    t = lambda x, y, s, fs, extra="": '<text x="%s" y="%s" text-anchor="middle" font-size="%.1f"%s>%s</text>' % (x, y, fs, extra, esc(s))
    if shape == "round":
        g += '<circle cx="60" cy="60" r="55" stroke-width="3.4"/><circle cx="60" cy="60" r="49" stroke-width="1.2"/>'
        g += ('<defs><path id="%st" d="%s"/><path id="%sb" d="%s"/></defs>' % (uid, ARC_TOP, uid, ARC_BOT))
        g += ('<text font-size="%.1f" letter-spacing="1.1"><textPath href="#%st" startOffset="50%%" text-anchor="middle">%s</textPath></text>' % (fit(top, 96, 11.5), uid, esc(top)))
        g += ('<text font-size="%.1f" letter-spacing="1.1"><textPath href="#%sb" startOffset="50%%" text-anchor="middle">%s</textPath></text>' % (fit(bottom, 112, 11), uid, esc(bottom)))
        if picto:
            g += '<g transform="translate(34 32) scale(2.1)" stroke-width="1.35" fill="none">%s</g>' % picto
        else:
            g += t(60, 67, big, 33, ' font-weight="800"') + t(60, 80, small, 9.5, ' letter-spacing="1.2"')
        g += '<path d="M44 52h-6M76 52h6" stroke-width="1.2"/>' if not picto else ""
    elif shape == "rect":
        g += '<rect x="7" y="21" width="106" height="78" rx="11" stroke-width="3.2"/><rect x="12.5" y="26.5" width="95" height="67" rx="6.5" stroke-width="1.2"/>'
        g += t(60, 43, top, fit(top, 88, 12.5), ' letter-spacing="1.2"')
        g += '<path d="M20 49.5h80M20 79.5h80" stroke-width="1"/>'
        if picto:
            g += '<g transform="translate(46 50) scale(1.1)" stroke-width="1.7" fill="none">%s</g>' % picto
        else:
            g += t(60, 74, big, 27, ' font-weight="800"')
        bl = (bottom + " " + small).strip() if not picto else bottom
        g += t(60, 90, bl, fit(bl, 88, 11), ' letter-spacing="1.2"')
    elif shape == "oval":
        g += '<ellipse cx="60" cy="60" rx="56" ry="41" stroke-width="3.2"/><ellipse cx="60" cy="60" rx="50" ry="35" stroke-width="1.2"/>'
        g += t(60, 41, top, fit(top, 76, 11), ' letter-spacing="1.1"')
        if picto:
            g += '<g transform="translate(40 42) scale(1.65)" stroke-width="1.4" fill="none">%s</g>' % picto
        else:
            g += t(60, 69, big, 30, ' font-weight="800"') + t(60, 79, small, 8.5, ' letter-spacing="1.2"')
        g += t(60, 91, bottom, fit(bottom, 76, 10.5), ' letter-spacing="1.1"')
    elif shape == "hex":
        g += ('<polygon points="114,60 87,106.8 33,106.8 6,60 33,13.2 87,13.2" stroke-width="3.2" stroke-linejoin="round"/>'
              '<polygon points="107,60 83.5,100.7 36.5,100.7 13,60 36.5,19.3 83.5,19.3" stroke-width="1.2" stroke-linejoin="round"/>')
        g += t(60, 38, top, fit(top, 56, 11), ' letter-spacing="1"')
        if picto:
            g += '<g transform="translate(38 41) scale(1.75)" stroke-width="1.4" fill="none">%s</g>' % picto
        else:
            g += t(60, 69, big, 30, ' font-weight="800"') + t(60, 79, small, 8.5, ' letter-spacing="1.2"')
        g += t(60, 93, bottom, fit(bottom, 58, 10.5), ' letter-spacing="1"')
    else:  # ticket : bords encochés
        g += ('<path d="M9 22H111V50a10 10 0 0 0 0 20V98H9V70a10 10 0 0 0 0-20Z" stroke-width="3.2" stroke-linejoin="round"/>'
              '<path d="M16 29H104V50M104 70V91H16V70M16 50V29" stroke-width="1.1" stroke-dasharray="3 2.2"/>')
        g += t(60, 44, top, fit(top, 76, 12), ' letter-spacing="1.2"')
        if picto:
            g += '<g transform="translate(47 48) scale(1.05)" stroke-width="1.7" fill="none">%s</g>' % picto
        else:
            g += t(60, 74, big, 26, ' font-weight="800"')
        bl = (bottom + " " + small).strip() if not picto else bottom
        g += t(60, 88, bl, fit(bl, 76, 11), ' letter-spacing="1.2"')
    g += "</g>"
    return ('<svg class="stamp" viewBox="0 0 120 120" aria-hidden="true" focusable="false" style="color:%s" '
            'font-family="\'Barlow Condensed\',\'Barlow\',sans-serif" font-weight="700">%s</svg>' % (color, g))


SHAPES = ["round", "rect", "oval", "hex", "ticket"]
ICON_OF = {"quiz": "question", "doudou": "heart", "mots": "grid", "blind": "music", "etoiles": "star", "photos": "camera"}


def inner_icon(name):
    return re.sub(r'^<svg[^>]*>|</svg>$', "", icon(name))


def day_stamp(i, d):
    dt = A.dparse(d["id"])
    stage = d["stage"]
    city = "PARIS · BANGKOK" if stage == "vol" else D.STAGE[stage]["city"].upper()
    word = G.STAMP_WORDS[d["id"]]
    shape = SHAPES[i % 5]
    mon = A.MO3[dt.month - 1].replace(".", "").upper()
    if shape in ("rect", "ticket"):
        big, small = "%d %s" % (dt.day, mon), str(dt.year)
    else:
        big, small = str(dt.day), "%s %d" % (mon, dt.year)
    return stamp_svg("st%d" % i, shape, word, big, small, city, INK[stage], ROT[i % len(ROT)])


def bonus_stamp(j, key, word):
    shape = ["round", "hex", "oval", "round", "hex", "oval"][j]
    return stamp_svg("sb%d" % j, shape, "THAÏLANDE 2026" if shape != "oval" else "THAÏLANDE", "", "", word, BONUS_INK[j], ROT[(j * 3 + 5) % len(ROT)], inner_icon(ICON_OF[key]))


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
                '<span class="slot-ph"><b>%d</b><small>%s</small></span>%s</button>'
                % (d["id"], esc(G.STAMP_WORDS[d["id"]].capitalize()), esc("Tampon du " + A.day_title(d["id"]).lower()), dt.day, A.MO3[dt.month - 1], day_stamp(i, d)))
    out += '</div></section><section class="pp" aria-label="Tampons spéciaux"><h2 class="sech navy">Les tampons spéciaux</h2><div class="pp-grid">'
    for j, (key, word, title, how) in enumerate(G.BONUS_STAMPS):
        out += ('<button class="slot" type="button" data-stamp="b" data-id="%s" data-how="%s" data-title="%s" aria-pressed="false" aria-label="%s">'
                '<span class="slot-ph"><i>%s</i><small>%s</small></span>%s</button>'
                % (key, esc(how), esc(title), esc("Tampon spécial : " + title), icon(ICON_OF[key]), esc(title), bonus_stamp(j, key, word)))
    out += ('</div></section><div class="acts"><button class="btn sm alt" type="button" id="pp-reset">%s <span>Effacer tous les tampons</span></button></div></div></main>' % icon("refresh"))
    return out


# ───────────────────────── petites pièces pour les autres pages ─────────────────────────
def guide_html(day_id):
    q = G.DAY_QUIPS.get(day_id)
    if not q:
        return ""
    key, text = q
    d = DD[key]
    return ('<a class="guide" href="#/mascottes" style="--dd:%s">%s<p><b>%s</b>%s</p></a>' % (d["bg"], dd_img(key, "guide-img"), txt(d["short"]), txt("« %s »" % text)))


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
    return (view_jeux() + view_quiz() + view_test() + view_doudous() + view_blind() + view_mots() + view_horo() + view_pass() + INK_FILTER)
