# -*- coding: utf-8 -*-
"""Page principale du carnet (index.html) : toutes les vues sont écrites en HTML ici,
app.js ne fait qu'afficher la bonne et gérer les photos et le plan du métro.
Contenu : site_data.py (repris du Journal_de_bord.pdf). Mise en page : app.css."""
import datetime, html, json, os, re, urllib.parse

import site_data as D
from build_site import ROOT, font_css, icon, sticker

WD = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
WD3 = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
MO = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MO3 = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
NB = " "

# fond de l'en-tête de chaque carte d'hôtel (teinte claire de la couleur de l'étape)
TINT = {"s1": "#F5E6E9", "s2": "#FCE9C5", "s3": "#CCD9F4", "s4": "#F9DDE4"}


# ───────────────────────── texte ─────────────────────────
def esc(s):
    return html.escape(s, quote=True)


def typo(s):
    """Espaces insécables avant : ; ? ! » et après «."""
    s = re.sub(r" ([:;?!»])", NB + r"\1", s)
    return re.sub(r"(«) ", r"\1" + NB, s)


def txt(s):
    return esc(typo(s))


def rich(s):
    """Texte avec « **gras** » → HTML."""
    out = []
    for i, part in enumerate(s.split("**")):
        t = txt(part)
        out.append("<b>%s</b>" % t if i % 2 and t.strip() else t)
    return "".join(out)


def maps_search(q):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q, safe="")


def maps_dir(q):
    return "https://www.google.com/maps/dir/?api=1&destination=" + urllib.parse.quote(q, safe="")


def pills(items):
    return "".join(
        '<a class="maps" href="%s" target="_blank" rel="noopener noreferrer">%s%s</a>' % (esc(maps_search(q)), icon("pin"), txt(label))
        for label, q in items)


# ───────────────────────── dates ─────────────────────────
def dparse(i):
    y, m, d = (int(x) for x in i.split("-"))
    return datetime.date(y, m, d)


def day_no(dt):
    return "1er" if dt.day == 1 else str(dt.day)


def day_title(i):
    dt = dparse(i)
    return "%s %s %s" % (WD[dt.weekday()].capitalize(), day_no(dt), MO[dt.month - 1])


def day_full(i):
    dt = dparse(i)
    return "%s %s %s %d" % (WD[dt.weekday()].capitalize(), day_no(dt), MO[dt.month - 1], dt.year)


def day_short(i):
    dt = dparse(i)
    return "%s %d %s" % (WD3[dt.weekday()], dt.day, MO3[dt.month - 1])


# ───────────────────────── jours ─────────────────────────
def step_html(st):
    cls = ' class="flight"' if st["kind"] == "flight" else ""
    out = "<li%s>" % cls
    if st["t"]:
        out += '<span class="when">%s</span> ' % txt(st["t"])
    out += '<span class="what">%s</span>' % txt(st["x"])
    for ln in st["sub"]:
        c = "sub" + (" b" if ln["b"] else "") + (" head" if ln["head"] else "")
        out += '<p class="%s">%s</p>' % (c, txt(ln["x"]))
        if ln["p"]:
            out += '<div class="pills">%s</div>' % pills(ln["p"])
    if st["p"]:
        out += '<div class="pills">%s</div>' % pills(st["p"])
    return out + "</li>"


def fact_card(paras):
    out = '<div class="fact">'
    for i, p in enumerate(paras):
        # un paragraphe tout en gras en tête de carte = un intitulé
        if i == 0 and p.startswith("**") and p.endswith("**") and p.count("**") == 2 and len(paras) > 1:
            out += '<p class="fh">%s</p>' % rich(p)
        else:
            out += "<p>%s</p>" % rich(p)
    return out + "</div>"


def quiz_html():
    q = D.QUIZ
    out = '<h3 class="sech">%s</h3><p class="sub">%s</p><div class="fact quiz">' % (txt(q["title"]), txt(q["sub"]))
    for n, (question, options, _good) in enumerate(q["qs"], 1):
        out += '<div class="q"><p class="qt">%d. %s</p><ol>' % (n, txt(question))
        for k, o in enumerate(options):
            out += "<li><b>%s.</b> %s</li>" % ("ABC"[k], txt(o))
        out += "</ol></div>"
    return out + "</div>"


def lexique_html():
    out = '<h3 class="sech">Lexique des temples</h3><div class="fact lex"><dl>'
    for term, thai, meaning in D.LEXIQUE_TEMPLES:
        out += '<dt>%s<span class="th" lang="th">%s</span></dt><dd>%s</dd>' % (txt(term), thai, txt(meaning))
    return out + "</dl></div>"


def snap_html(d):
    full = day_full(d["id"])
    return (
        '<section class="snap" aria-label="Photo du jour">'
        '<h3 class="sech navy">Photo du jour</h3>'
        '<figure class="polaroid"><div class="ph"><img alt="Photo du jour, %(full)s" hidden>'
        '<p class="ph-empty">Ici, ta photo du jour ! (ou autre)</p></div>'
        '<figcaption><input class="cap" type="text" maxlength="60" placeholder="Une légende ?" aria-label="Légende de la photo" autocomplete="off">'
        '<span class="date">%(full)s</span></figcaption></figure>'
        '<div class="acts">'
        '<label class="btn">%(cam)sPrendre une photo<input type="file" accept="image/*" capture="environment" aria-label="Prendre une photo"></label>'
        '<label class="btn alt">%(img)sGalerie<input type="file" accept="image/*" aria-label="Choisir une photo dans la galerie"></label>'
        '</div>'
        '<div class="acts" data-need-photo hidden><button class="btn alt" type="button" data-act="save">%(save)s<span data-save-lbl>Enregistrer</span></button></div>'
        '<button class="del" type="button" data-act="del" data-need-photo hidden>Enlever la photo</button>'
        '<p class="status" role="status"></p>'
        '</section>'
    ) % dict(full=esc(full), cam=icon("camera"), img=icon("image"), save=icon("save"))


def day_nav(i):
    prev = D.DAYS[i - 1] if i > 0 else None
    nxt = D.DAYS[i + 1] if i < len(D.DAYS) - 1 else None
    out = '<nav class="pn" aria-label="Autres jours">'
    if prev:
        out += '<a class="btn alt" href="#/jours/%s" data-go-day="%s">%s%s</a>' % (prev["id"], prev["id"], icon("chevl"), esc(day_short(prev["id"])))
    else:
        out += "<span></span>"
    if nxt:
        out += '<a class="btn alt" href="#/jours/%s" data-go-day="%s">%s%s</a>' % (nxt["id"], nxt["id"], esc(day_short(nxt["id"])), icon("chevr"))
    return out + "</nav>"


def day_html(i, d):
    st = D.STAGE[d["stage"]]
    out = '<article class="day" id="d-%s" data-id="%s" hidden>' % (d["id"], d["id"])
    out += "<h2>%s</h2>" % esc(day_title(d["id"]))
    out += '<div class="where"><span class="tag" style="--c:%s"><i></i>%s</span>' % (st["color"], txt(d["city"]))
    if d["night"]:
        h = D.HOTEL[d["night"]]
        out += '<a class="tag" href="#/hotels/%s">%s%s</a>' % (h["id"], icon("bed"), txt(h["name"]))
    out += "</div>"
    steps = D.FREE_STEPS if d.get("free") else d["steps"]
    if d.get("free"):
        out += '<p class="free-note">Du 30 décembre au 1er janvier : journées libres, on fait ce qui nous plaît.</p>'
    if steps:
        out += '<ol class="tl">%s</ol>' % "".join(step_html(s) for s in steps)
    if d.get("paper"):
        out += '<p class="pen">%s<span>Dans le carnet papier : %s</span></p>' % (icon("pen"), txt(d["paper"].split(" : ")[0]))
    if d.get("free"):
        out += '<p class="pen">%s<span>Dans le carnet papier : le labyrinthe du tuk-tuk</span></p>' % icon("pen")
    if d.get("quiz"):
        out += quiz_html()
    cards = D.facts_for(d)
    if cards:
        out += '<h3 class="sech">Fun facts</h3>' + "".join(fact_card(c) for c in cards)
    if d.get("lexique"):
        out += lexique_html()
    out += snap_html(d)
    if d.get("end"):
        out += '<p class="theend">The end :(</p>'
    out += day_nav(i)
    return out + "</article>"


def strip_html():
    out, prev = [], None
    for d in D.DAYS:
        dt = dparse(d["id"])
        if (dt.year, dt.month) != prev:
            out.append('<li class="mon" aria-hidden="true">%s</li>' % ("déc." if dt.month == 12 else "janv."))
            prev = (dt.year, dt.month)
        st = D.STAGE[d["stage"]]
        label = "%s %s %s, %s" % (WD[dt.weekday()], day_no(dt), MO[dt.month - 1], d["city"])
        out.append(
            '<li><button class="chip" type="button" data-day="%s" data-go-day="%s" aria-pressed="false" aria-label="%s" style="--c:%s">'
            '<span class="w">%s</span><span class="n">%d</span><span class="bar"></span></button></li>'
            % (d["id"], d["id"], esc(label), st["color"], WD3[dt.weekday()], dt.day))
    return '<div class="strip"><ol aria-label="Les jours du voyage">%s</ol></div>' % "".join(out)


def view_days():
    return ('<main class="view" id="v-days" hidden>'
            '<header class="vhead"><div class="wrap"><div><h1 tabindex="-1">Jours</h1></div></div></header>'
            + strip_html() + '<div class="wrap">' + "".join(day_html(i, d) for i, d in enumerate(D.DAYS))
            + "</div></main>")


# ───────────────────────── hôtels ─────────────────────────
def row(label, value, acts, plain_value=None):
    return ('<div class="row"><span class="lab">%s</span><p class="val">%s</p><div class="acts">%s</div></div>'
            % (label, value, acts))


def hotel_html(h):
    st = D.STAGE[h["stage"]]
    addr = typo(h["addr"])
    body = row("Adresse", esc(addr),
               '<a class="btn sm" href="%s" target="_blank" rel="noopener noreferrer">%sVoir sur Maps</a>'
               '<a class="btn sm alt" href="%s" target="_blank" rel="noopener noreferrer">%sItinéraire</a>'
               '<button class="btn sm alt" type="button" data-act="copy" data-copy="%s" data-ok="Adresse copiée">%sCopier</button>'
               % (esc(maps_search(h["q"])), icon("pin"), esc(maps_dir(h["q"])), icon("route"), esc(h["addr"]), icon("copy")))
    body += row("Téléphone", esc(h["phone"]),
                '<a class="btn sm" href="tel:%s">%sAppeler</a>'
                '<button class="btn sm alt" type="button" data-act="copy" data-copy="%s" data-ok="Numéro copié">%sCopier</button>'
                % (esc(h["tel"]), icon("phone"), esc(h["phone"]), icon("copy")))
    if h["mail"]:
        body += row("E-mail", esc(h["mail"]),
                    '<a class="btn sm" href="mailto:%s">%sÉcrire</a>'
                    '<button class="btn sm alt" type="button" data-act="copy" data-copy="%s" data-ok="Adresse e-mail copiée">%sCopier</button>'
                    % (esc(h["mail"]), icon("mail"), esc(h["mail"]), icon("copy")))
    return ('<article class="hotel" id="h-%s" style="--c:%s;--c-bg:%s">'
            '<div class="top"><i></i><div><h2>%s</h2><small>%s · %s · %s</small></div></div>'
            '<div class="body">%s</div></article>'
            % (h["id"], st["color"], TINT[h["stage"]], txt(h["name"]), txt(h["city"]), txt(h["dates"]), txt(h["nights"]), body))


def view_hotels():
    return ('<main class="view" id="v-hotels" hidden>'
            '<header class="vhead"><div class="wrap"><div><h1 tabindex="-1">Hôtels</h1><p>Adresses, téléphones, itinéraires</p></div></div></header>'
            '<div class="wrap">' + "".join(hotel_html(h) for h in D.HOTELS) + "</div></main>")


# ───────────────────────── utile + métro ─────────────────────────
def view_utile():
    soon = [("book", "Lexique en thaï", "À lire ou à écouter"), ("car", "Cartes taxi", "Les adresses des hôtels, en thaï"),
            ("coin", "Convertisseur", "Baht et euro"), ("info", "Bon à savoir", "Les petits conseils du carnet")]
    out = ('<main class="view" id="v-utile" hidden>'
           '<header class="vhead"><div class="wrap"><div><h1 tabindex="-1">Utile</h1><p>Ce qui dépanne en route</p></div></div></header>'
           '<div class="wrap"><div class="list">'
           '<a class="tile rose" href="#/metro"><span class="ic">%s</span><span><b>Plan du métro</b><small>Bangkok : pince pour zoomer</small></span></a>'
           % icon("train"))
    for ic, t, sub in soon:
        out += ('<div class="tile soon"><span class="ic">%s</span><span><b>%s</b><small>%s</small></span><span class="badge">bientôt</span></div>'
                % (icon(ic), txt(t), txt(sub)))
    return out + "</div></div></main>"


def view_metro():
    return ('<main class="view" id="v-metro" hidden>'
            '<header class="vhead"><div class="wrap"><a class="back" href="#/utile" aria-label="Retour">%s</a>'
            '<div><h1 tabindex="-1">Plan du métro</h1><p>Bangkok</p></div></div></header>'
            '<div class="wrap"><div class="mv" id="mv" role="img" aria-label="Plan du métro de Bangkok, à zoomer avec deux doigts">'
            '<div class="mv-stage" id="mv-stage"></div>'
            '<div class="load" id="mv-load">Chargement du plan…</div>'
            '<div class="mctl"><button type="button" data-z="in" aria-label="Zoomer">%s</button>'
            '<button type="button" data-z="out" aria-label="Dézoomer">%s</button>'
            '<button type="button" data-z="fit" aria-label="Tout le plan">%s</button></div></div>'
            '<p class="hint">Pince avec deux doigts pour zoomer, glisse pour te déplacer, touche deux fois pour zoomer d’un coup.</p></div></main>'
            % (icon("chevl"), icon("plus"), icon("minus"), icon("fit")))


# ───────────────────────── accueil ─────────────────────────
def thai_map_svg():
    m = json.load(open(os.path.join(ROOT, "_dev", "thai_map.json"), encoding="utf-8"))
    c = m["cities"]
    names = {"sukhothai": "Sukhothaï", "bangkok": "Bangkok", "banphe": "Ban Phe"}
    out = ('<svg viewBox="0 0 %s %s" role="img" aria-label="Carte de la Thaïlande avec Sukhothaï, Bangkok et Ban Phe">'
           '<path class="land" d="%s"/>' % (m["w"], m["h"], m["d"]))
    for k in ("sukhothai", "bangkok", "banphe"):
        x, y = c[k]
        out += '<circle class="ring" cx="%.1f" cy="%.1f" r="5.2"/><text x="%.1f" y="%.1f">%s</text>' % (x, y, x + 9, y + 5, names[k])
    return out + "</svg>"


def view_home(version):
    who = [("Arthur", "#283881", "#fff"), ("Daphne", "#E9A9B8", "#5B1025"), ("Flo", "#F2A71B", "#5B1025"), ("Anne", "#A51C36", "#fff")]
    out = ('<main class="view" id="v-home">'
           '<header class="hero"><div class="wrap">'
           '<p class="eyebrow">Carnet de voyage</p><h1>Thaïlande <span>2026</span></h1>'
           '<p class="dates">19.12.2026 — 03.01.2027</p><p class="lead">Le carnet papier, version téléphone.</p>'
           '<button class="stk stk-ele" id="ele" type="button" aria-label="L’éléphant te salue">%s</button>'
           '<button class="stk stk-tuk" id="tuk" type="button" aria-label="Le tuk-tuk démarre">%s</button>'
           '</div></header><div class="wrap">'
           % (sticker("elephant"), sticker("tuktuk")))
    out += ('<section class="sec" aria-labelledby="h-who"><h2 id="h-who">Qui es-tu ?</h2>'
            '<p class="sub">Ton prénom reste sur ce téléphone.</p><div class="who" id="who" role="group" aria-label="Choisis ton prénom">')
    for n, bg, fg in who:
        out += ('<button type="button" data-n="%s" aria-pressed="false"><span class="ini" style="background:%s;color:%s">%s</span>%s</button>'
                % (n, bg, fg, n[0], n))
    out += '</div><p class="hello" id="hello" role="status">Appuie sur ton prénom.</p></section>'

    out += '<section class="bubble blue" aria-labelledby="h-trip"><h2 id="h-trip">Le voyage</h2><div class="trip"><div class="tmap">%s</div><ul class="stages">' % thai_map_svg()
    for s in D.STAGES:
        if s["id"] == "vol":
            continue
        h = D.HOTEL[s["hotel"]]
        out += ('<li><a href="#/jours/%s" data-go-day="%s" style="--c:%s"><span class="dot"></span>'
                '<span><b>%s</b><small>%s</small><small>%s</small></span><span class="go">%s</span></a></li>'
                % (s["first"], s["first"], s["color"], txt(s["city"]), txt(s["dates"]), txt(h["name"]), icon("chevr")))
    out += "</ul></div></section>"

    tiles = [("sand", "#/jours", "calendar", "Jours", "18 décembre → 3 janvier", ""),
             ("blue", "#/hotels", "bed", "Hôtels", "Adresses et téléphones", ""),
             ("rose", "#/metro", "train", "Métro", "Plan de Bangkok à zoomer", ""),
             ("mustard", "#/jours", "camera", "Photo du jour", "Un polaroïd par jour", " data-photo-tile")]
    out += '<div class="tiles">'
    for col, href, ic, t, sub, extra in tiles:
        small = '<small data-photo-count>%s</small>' % txt(sub) if extra else "<small>%s</small>" % txt(sub)
        out += '<a class="tile %s" href="%s"%s><span class="ic">%s</span><span><b>%s</b>%s</span></a>' % (col, href, extra, icon(ic), txt(t), small)
    out += "</div>"

    out += ('<section class="bubble sand" aria-labelledby="h-soon"><h2 id="h-soon">Bientôt</h2>'
            '<p>Lexique en thaï, cartes taxi, convertisseur de baht, jeux et doudous : ça arrive !</p></section>')
    out += ('<section class="bubble rose install" id="install-box" hidden aria-labelledby="h-inst"><h2 id="h-inst">Sur ton écran d’accueil</h2>'
            '<p id="install-hint"></p><div class="acts"><button class="btn" type="button" id="install-btn" hidden>Installer l’appli</button></div></section>')
    out += ('<p class="foot">Carnet Thaïlande 2026 · <a href="test.html">Tester mon téléphone</a><small>version %s</small></p>' % esc(version))
    return out + "</div></main>"


# ───────────────────────── page complète ─────────────────────────
def nav_html():
    items = [("home", "#/", "home", "Accueil"), ("days", "#/jours", "calendar", "Jours"),
             ("hotels", "#/hotels", "bed", "Hôtels"), ("utile", "#/utile", "compass", "Utile")]
    return ('<nav class="nav" aria-label="Menu">%s</nav>'
            % "".join('<a href="%s" data-nav="%s"><span class="ni">%s</span>%s</a>' % (h, k, icon(ic), t) for k, h, ic, t in items))


def css_text():
    s = open(os.path.join(ROOT, "app.css"), encoding="utf-8").read()
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return "\n".join(ln.strip() for ln in s.splitlines() if ln.strip())


def render(version, head_meta):
    body = (view_home(version) + view_days() + view_hotels() + view_utile() + view_metro() + nav_html()
            + '<div id="toast" role="status" aria-live="polite"></div>'
            + '<div id="upd" hidden><span>Une nouvelle version est prête.</span><button class="btn sm" type="button" id="upd-btn">Actualiser</button></div>')
    js = open(os.path.join(ROOT, "app.js"), encoding="utf-8").read()
    assert "</script" not in js
    return ('<!doctype html><html lang="fr" data-v="%s"><head>%s<title>Carnet Thaïlande 2026</title>%s<style>%s</style></head><body>%s<script>%s</script></body></html>\n'
            % (esc(version), head_meta, font_css(), css_text(), body, js))
