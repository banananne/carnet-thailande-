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


_MARKUP = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<svg\b.*?</svg>|<[^>]*>)", re.S | re.I)


def nbsp_pass(page):
    """Dernier passage sur la page entière : espace insécable avant : ; ? ! » et après « dans le texte de TOUTES les pièces,
    y compris celles qui ne passent pas par txt() (gabarit, pages des jours, écrans « Pas encore ! »).
    Ne touche ni aux balises ni aux attributs, ni aux scripts, aux styles et aux dessins."""
    parts = _MARKUP.split(page)
    for i in range(0, len(parts), 2):      # indices pairs = texte entre deux balises
        parts[i] = typo(parts[i])
    return "".join(parts)


def rich(s):
    """Texte avec « **gras** » → HTML."""
    out = []
    for i, part in enumerate(s.split("**")):
        t = txt(part)
        out.append("<b>%s</b>" % t if i % 2 and t.strip() else t)
    return "".join(out)


TOKEN = re.compile(r"\*\*(.+?)\*\*|__(.+?)__|\^\^(.+?)\^\^|~~(.+?)~~", re.S)


def rich2(s):
    """Texte des pages « Good to know » : **gras**, __transcription__, ^^thaï^^, ~~exposant~~ (imbriquables)."""
    out, pos = [], 0
    for m in TOKEN.finditer(s):
        out.append(txt(s[pos:m.start()]))
        if m.group(1) is not None:
            out.append("<b>%s</b>" % rich2(m.group(1)))
        elif m.group(2) is not None:
            out.append('<i class="rom">%s</i>' % txt(m.group(2)))
        elif m.group(3) is not None:
            out.append('<span class="th" lang="th">%s</span>' % esc(m.group(3)))
        else:
            out.append("<sup>%s</sup>" % txt(m.group(4)))
        pos = m.end()
    out.append(txt(s[pos:]))
    return "".join(out).replace("\n", "<br>")


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
    import build_games as BG0
    out += BG0.song_html(d["id"])
    out += '<div class="where"><span class="tag" style="--c:%s"><i></i>%s</span>' % (st["color"], txt(d["city"]))
    if d["night"]:
        h = D.HOTEL[d["night"]]
        out += '<a class="tag" href="#/hotels/%s">%s%s</a>' % (h["id"], icon("bed"), txt(h["name"]))
    out += "</div>"
    import build_games as BG
    out += BG.guide_html(d["id"])
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
        out += BG.quiz_cta()
    cards = D.facts_for(d)
    if cards:
        out += '<h3 class="sech">Fun facts</h3>' + "".join(fact_card(c) for c in cards)
    if d.get("lexique"):
        out += lexique_html()
    import build_days as BD
    out += BD.day_link_html(d["id"])
    out += snap_html(d)
    out += BG.day_stamp_html(d["id"])
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
               '<a class="btn sm alt" href="#/taxi/%s">%sCarte taxi</a>'
               % (esc(maps_search(h["q"])), icon("pin"), esc(maps_dir(h.get("ll") or h["q"])), icon("route"), esc(h["addr"]), icon("copy"),
                  h["id"], icon("car")))
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
    items = [("rose", "#/metro", "train", "Plan du métro", "Tout le réseau, à zoomer"),
             ("sand", "#/lexique", "book", "Lexique en thaï", "À montrer ou à écouter"),
             ("blue", "#/traduire", "translate", "Traducteur", "Français ⇄ thaï, à lire et à écouter"),
             ("mustard", "#/taxi", "car", "Cartes taxi", "Les hôtels écrits en thaï"),
             ("blue", "#/convertisseur", "coin", "Convertisseur", "Baht et euro"),
             ("rose", "#/good-to-know", "info", "Good to know", "Histoire, savoir-vivre, urgences")]
    out = ('<main class="view" id="v-utile" hidden>'
           '<header class="vhead"><div class="wrap"><div><h1 tabindex="-1">Utile</h1><p>Ce qui dépanne en route</p></div></div></header>'
           '<div class="wrap"><div class="list">')
    for col, href, ic, t, sub in items:
        out += '<a class="tile %s" href="%s"><span class="ic">%s</span><span><b>%s</b><small>%s</small></span></a>' % (col, href, icon(ic), txt(t), txt(sub))
    return out + "</div></div></main>"


def view_metro():
    return ('<main class="view" id="v-metro" hidden>'
            '<header class="vhead"><div class="wrap"><a class="back" href="#/utile" aria-label="Retour">%s</a>'
            '<div><h1 tabindex="-1">Plan du métro</h1><p>Tout le réseau de Bangkok</p></div></div></header>'
            '<div class="wrap"><div class="mv" id="mv" role="img" aria-label="Plan du métro de Bangkok, à zoomer avec deux doigts">'
            '<div class="mv-stage" id="mv-stage"></div>'
            '<div class="load" id="mv-load">Chargement du plan…</div>'
            '<div class="mctl"><button type="button" data-z="in" aria-label="Zoomer">%s</button>'
            '<button type="button" data-z="out" aria-label="Dézoomer">%s</button>'
            '<button type="button" data-z="fit" aria-label="Tout le plan">%s</button></div></div>'
            '<p class="hint">Pince avec deux doigts pour zoomer, glisse pour te déplacer, touche deux fois pour zoomer d’un coup. Les stations sont écrites en thaï et en anglais.</p></div></main>'
            % (icon("chevl"), icon("plus"), icon("minus"), icon("fit")))


# ───────────────────────── étape 2 : lexique, cartes taxi, convertisseur, Good to know ─────────────────────────
NUM_TH = {"1": "หนึ่ง", "2": "สอง", "3": "สาม", "4": "สี่", "5": "ห้า", "6": "หก", "7": "เจ็ด", "8": "แปด", "9": "เก้า", "10": "สิบ",
          "20": "ยี่สิบ", "100": "หนึ่งร้อย", "1000": "หนึ่งพัน"}


def back_head(title, sub, to="#/utile"):
    return ('<header class="vhead"><div class="wrap"><a class="back" href="%s" aria-label="Retour">%s</a>'
            '<div><h1 tabindex="-1">%s</h1><p>%s</p></div></div></header>' % (to, icon("chevl"), txt(title), txt(sub)))


def say_btn(th, q, label):
    return ('<button class="lx-say" type="button" data-say data-th="%s" data-q="%d" aria-label="Écouter : %s">%s</button>'
            % (esc(th), q, esc(label), icon("speaker")))


def lx_row(fr, rom, th, long=False):
    q = 1 if "?" in fr else 0
    label = re.sub(r"[«»]", "", fr).strip()
    return ('<li class="lx%s"><button class="lx-main" type="button" data-show data-th="%s" data-rom="%s" data-fr="%s" data-q="%d" aria-label="Montrer en grand : %s">'
            '<span class="fr">%s</span><span class="rom">%s</span><span class="th" lang="th">%s</span></button>%s</li>'
            % (" long" if long else "", esc(th), esc(typo(rom)), esc(typo(fr)), q, esc(label),
               txt(fr), txt(rom), esc(th), say_btn(th, q, label)))


def num_tile(d, rom):
    key = d.replace(NB, "").replace(" ", "")
    th = NUM_TH[key]
    return ('<button class="num" type="button" data-show data-np="1" data-th="%s" data-rom="%s" data-fr="%s" aria-label="Montrer en grand : %s">'
            '<b>%s</b><small>%s</small></button>' % (esc(th), esc(rom), esc(d), esc(d), esc(d), esc(rom)))


def lexique_section(d):
    sid = re.sub(r"\W+", "-", d["title"].lower()).strip("-")
    out = '<section class="lxs bubble sand" aria-labelledby="lx-%s"><h2 id="lx-%s">%s</h2>' % (sid, sid, txt(d["title"].capitalize()))
    for b in d["blocks"]:
        k = b["kind"]
        if k in ("words", "phrases"):
            out += '<ul class="lxl%s">%s</ul>' % (" sep" if b.get("sep") else "", "".join(lx_row(fr, rom, th, long=(k == "phrases")) for fr, rom, th in b["rows"]))
        elif k == "words2":
            rows = list(b["left"]) + list(b["right"])
            out += '<ul class="lxl">%s</ul>' % "".join(lx_row(fr, rom, th) for fr, rom, th in rows)
        elif k == "numbers":
            lines = b["lines"]
            top = [x for ln in lines[:2] for x in ln]
            out += '<div class="nums">%s</div>' % "".join(num_tile(dg, rom) for dg, rom in top)
            out += '<div class="nums n3">%s</div>' % "".join(num_tile(dg, rom) for dg, rom in lines[2])
        elif k == "note":
            out += '<p class="lx-note">%s</p>' % rich2(b["text"])
        else:
            raise ValueError(k)
    return out + "</section>"


def pol_html():
    return ('<section class="pol" aria-labelledby="h-pol"><h2 id="h-pol">Mon petit mot poli</h2>'
            '<p>En thaï, une phrase se termine par un petit mot poli, selon qui parle. Choisis le tien : il s’ajoutera quand tu montres ou écoutes une phrase.</p>'
            '<div class="seg" role="group" aria-label="Mon petit mot poli">'
            '<button type="button" data-pol="kha" aria-pressed="false"><span class="th" lang="th">ค่ะ</span><span><b>kha</b>pour une femme</span></button>'
            '<button type="button" data-pol="khrap" aria-pressed="false"><span class="th" lang="th">ครับ</span><span><b>khrap</b>pour un homme</span></button>'
            '</div></section>')


def view_lexique():
    out = ('<main class="view" id="v-lexique" hidden>' + back_head("Lexique", "Du thaï à montrer ou à écouter")
           + '<div class="wrap"><p class="how">Touche une ligne pour la <b>montrer en grand</b>. Touche le haut-parleur pour l’<b>écouter</b>.</p>')
    out += pol_html()
    out += "".join(lexique_section(d) for d in D.STEP2["lexique"])
    out += ('<p class="hint">Prononciation simplifiée, sans les tons : kh, ph, th = k, p, t avec un petit souffle (ph ne se dit jamais f). '
            'Un doute ? Montre l’écriture thaïe.</p>')
    return out + "</div></main>"


# ── cartes taxi ──
TAXI_SHORT = {"h1": "C’HOUSE", "h2": "Thai Thai", "h3": "Novotel", "h4": "Time Sabai"}


def taxi_card(t):
    h = D.HOTEL[t["hotel"]]
    ask, meter, call = D.TAXI_PHRASES
    name = ('<p class="tc-name" lang="th">%s</p><p class="tc-lat">%s</p>' % (esc(t["name_th"]), esc(t["name_lat"])) if t["name_th"]
            else '<p class="tc-name lat">%s</p>' % esc(t["name_lat"]))
    near = '<p class="tc-near" lang="th">%s</p>' % esc(t["near_th"]) if t["near_th"] else ""
    card = ('<div class="tc"><p class="tc-ask" lang="th">%s</p>%s%s<p class="tc-addr" lang="th">%s</p><p class="tc-en">%s</p>'
            '<p class="tc-meter" lang="th">%s</p><p class="tc-call" lang="th">%s</p><p class="tc-tel">%s</p></div>'
            % (esc(ask[0]), name, near, esc(t["addr_th"]), esc(h["addr"].replace("Thaïlande", "Thailand")), esc(meter[0]), esc(call[0]), esc(h["phone"])))
    help_ = "".join("<li><i class=\"rom\">%s</i><br>%s</li>" % (esc(rom), txt(fr)) for _th, rom, fr in D.TAXI_PHRASES)
    near_fr = '<p class="tc-hint">%s%s</p>' % (icon("pin"), txt(t["near_fr"])) if t["near_fr"] else ""
    acts = ('<div class="acts">'
            '<button class="btn" type="button" data-show-card>%s Montrer en grand</button>'
            '<button class="btn alt" type="button" data-say data-th="%s" data-q="0">%s Écouter</button>'
            '<a class="btn alt" href="%s" target="_blank" rel="noopener noreferrer">%s Ouvrir dans Maps</a>'
            '<a class="btn alt" href="tel:%s">%s Appeler l’hôtel</a>'
            '<a class="btn alt" href="#/hotels/%s">%s Fiche de l’hôtel</a></div>'
            % (icon("fit"), esc(ask[0].split("ครับ")[0]), icon("speaker"), esc(maps_dir(h.get("ll") or h["q"])), icon("route"),
               esc(h["tel"]), icon("phone"), h["id"], icon("bed")))
    return ('<article class="taxi" id="tx-%s" data-id="%s" hidden>%s%s%s<ul class="tc-help">%s</ul></article>'
            % (t["id"], t["id"], card, acts, near_fr, help_))


def view_taxi():
    out = ('<main class="view" id="v-taxi" hidden>' + back_head("Cartes taxi", "À montrer au chauffeur")
           + '<div class="wrap"><p class="how">Choisis où tu vas, puis montre l’écran au chauffeur.</p><div class="tpick" role="group" aria-label="Où vas-tu ?">')
    for t in D.TAXI:
        h = D.HOTEL[t["hotel"]]
        st = D.STAGE[h["stage"]]
        out += ('<button class="tchip" type="button" data-go-taxi="%s" aria-pressed="false" style="--c:%s"><i></i><b>%s</b><small>%s</small></button>'
                % (t["id"], st["color"], txt(TAXI_SHORT[t["id"]]), txt(h["city"])))
    out += "</div>" + "".join(taxi_card(t) for t in D.TAXI)
    return out + "</div></main>"


# ── convertisseur ──
def fr_num(x, dec=2):
    s = ("%." + str(dec) + "f") % x
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    ip, _, fp = s.partition(".")
    ip = re.sub(r"(?<=\d)(?=(\d{3})+$)", NB, ip)
    return ip + ("," + fp if fp else "")


def view_convert():
    r = D.RATE
    out = ('<main class="view" id="v-convert" hidden>' + back_head("Convertisseur", "Baht et euro")
           + '<div class="wrap"><section class="conv" id="conv" data-rate="%s" data-label="%s" aria-label="Convertisseur">'
           % (r["value"], esc(r["label"])))
    out += ('<label class="cf"><span class="cl"><b>฿</b>Baht</span><input id="c-thb" type="text" inputmode="decimal" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="0" aria-label="Montant en baht"></label>'
            '<label class="cf"><span class="cl"><b>€</b>Euro</span><input id="c-eur" type="text" inputmode="decimal" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="0" aria-label="Montant en euros"></label>')
    out += ('<div class="quick" role="group" aria-label="Montants rapides en baht">%s</div>'
            % "".join('<button type="button" data-quick="%d">%s ฿</button>' % (v, fr_num(v, 0)) for v in (20, 50, 100, 200, 500, 1000)))
    out += ('<p class="rate" id="c-rate">1 € = <b>%s ฿</b><span> · taux relevé le %s</span></p>'
            '<div class="acts"><button class="btn sm alt" type="button" id="c-edit">Changer le taux</button></div>'
            '<div class="redit" id="c-redit" hidden><label for="c-rin">1 € =</label><input id="c-rin" type="text" inputmode="decimal" autocomplete="off" aria-label="Taux : baht pour un euro"><span>฿</span>'
            '<button class="btn sm" type="button" id="c-rok">OK</button><button class="btn sm alt" type="button" id="c-rreset">Taux de départ</button></div>'
            '<p class="hint">Taux moyen du marché : un bureau de change, un distributeur ou ta carte donneront un peu moins. Règle le taux à la main quand tu veux.</p>'
            % (fr_num(r["value"], 2), esc(r["label"])))
    out += "</section>"
    out += ('<section class="bubble sand" id="c-say" aria-labelledby="h-csay"><h2 id="h-csay">Dire le prix en thaï</h2>'
            '<p class="csay-none" id="c-none">Tape un montant en baht, il s’écrira ici en thaï.</p>'
            '<div id="c-sayin" hidden><p class="say-th" id="c-th" lang="th"></p><p class="say-rom" id="c-rom"></p>'
            '<div class="acts"><button class="btn" type="button" id="c-show">%s Montrer</button>'
            '<button class="btn alt" type="button" id="c-say-btn">%s Écouter</button></div></div></section>'
            % (icon("fit"), icon("speaker")))
    out += ('<section class="bubble blue" aria-labelledby="h-rep"><h2 id="h-rep">Repères</h2><div class="ref" id="c-ref" data-rate="%s">'
            '<div><h3>Baht → euro</h3><ul>%s</ul></div><div><h3>Euro → baht</h3><ul>%s</ul></div></div></section>'
            % (r["value"],
               "".join('<li><span>%s ฿</span><b data-b="%d">%s €</b></li>' % (fr_num(v, 0), v, fr_num(v / r["value"], 2)) for v in (20, 50, 100, 200, 500, 1000, 2000)),
               "".join('<li><span>%s €</span><b data-e="%d">%s ฿</b></li>' % (fr_num(v, 0), v, fr_num(v * r["value"], 0)) for v in (1, 5, 10, 20, 50, 100))))
    return out + "</div></main>"


# ── Good to know ──
GTK_TEASER = {"HISTOIRE EN DATES": "De Sukhothaï à aujourd’hui", "SAVOIR-VIVRE EN PLUS": "Seuils, moines, repas…",
              "BOUDDHISME ET ESPRITS": "Temples, moines, maisons des esprits", "UNE COULEUR PAR JOUR": "Chaque jour a la sienne",
              "URGENCES": "Numéros utiles et mots clés"}


def gtk_block(b):
    k = b["kind"]
    if k == "timeline":
        return '<dl class="tm">%s</dl>' % "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (esc(dt), rich2(t)) for dt, t in b["rows"])
    if k == "bullets":
        return '<ul class="bl">%s</ul>' % "".join("<li>%s</li>" % rich2(t) for t in b["items"])
    if k == "para":
        t = re.sub(r"\+66[\d ]+\d", lambda m: m.group(0).replace(" ", NB), b["text"])
        return '<p class="gp%s">%s</p>' % (" sepl" if b.get("sep") else "", rich2(t))
    if k == "days":
        return '<ul class="dy">%s</ul>' % "".join('<li><i style="background:%s"></i><b>%s</b>%s</li>' % (c, esc(j), esc(col)) for j, col, c in b["items"])
    if k == "emergency":
        return '<div class="em">%s</div>' % "".join("<div><small>%s</small><b>%s</b></div>" % (txt(lab), esc(num)) for lab, num in b["items"])
    if k == "words":
        return '<ul class="lxl">%s</ul>' % "".join(lx_row(fr, rom, th, long=True) for fr, rom, th in b["rows"])
    raise ValueError(k)


def view_gtk():
    out = ('<main class="view" id="v-gtk" hidden>' + back_head("Good to know", "Histoire, savoir-vivre, urgences")
           + '<div class="wrap"><p class="how">Touche un titre pour ouvrir.</p>')
    for d in D.STEP2["gtk"]:
        sid = re.sub(r"\W+", "-", d["title"].lower()).strip("-")
        out += ('<details class="gb" id="gb-%s"><summary><span><b>%s</b><small>%s</small></span>%s</summary><div class="gb-in">%s</div></details>'
                % (sid, txt(d["title"].capitalize()), txt(GTK_TEASER[d["title"]]), icon("chevr"), "".join(gtk_block(b) for b in d["blocks"])))
    return out + "</div></main>"


# ── fenêtre « montrer en grand » (une seule pour tout le site) ──
def show_overlay():
    return ('<div id="show" class="show" role="dialog" aria-modal="true" aria-label="Montrer en grand" hidden>'
            '<button class="show-x" type="button" data-show-close aria-label="Fermer">%s</button>'
            '<div class="show-scroll"><div id="show-phrase"><p class="show-th" id="show-th" lang="th"></p><p class="show-rom" id="show-rom"></p><p class="show-fr" id="show-fr"></p></div>'
            '<div id="show-card" hidden></div></div>'
            '<div class="show-bar"><button class="btn" type="button" id="show-say">%s Écouter</button>'
            '<div class="seg sm" id="show-pol" role="group" aria-label="Mon petit mot poli">'
            '<button type="button" data-pol="kha" aria-pressed="false"><span class="th" lang="th">ค่ะ</span> kha</button>'
            '<button type="button" data-pol="khrap" aria-pressed="false"><span class="th" lang="th">ครับ</span> khrap</button></div></div></div>'
            % (icon("x"), icon("speaker")))


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
           '<p class="dates">18.12.2026 — 03.01.2027</p>'
           '<button class="stk stk-mask" id="mask" type="button" aria-label="Le masque te salue">'
           '<img src="img/sticker_masque.webp" width="296" height="356" alt="" decoding="async"></button>'
           '</div></header><div class="wrap">')
    import build_env as BE
    out += ('<section class="sec" id="who-sec" aria-labelledby="h-who"><div class="who-row">'
            '<button class="who-bar" id="who-bar" type="button" aria-expanded="false" aria-controls="who-box" hidden>'
            '<span class="who-av" id="who-av" aria-hidden="true"></span><span class="who-hi" id="who-hi"></span>'
            '<span class="who-chg">Changer<span class="who-chv">%s</span></span></button>%s</div>'
            '<div id="who-box"><h2 id="h-who">Qui es-tu ?</h2>'
            '<p class="sub">Ton prénom reste sur ce téléphone.</p><div class="who" id="who" role="group" aria-label="Choisis ton prénom">'
            % (icon("chevr"), BE.home_btn()))
    for n, bg, fg in who:
        out += ('<button type="button" data-n="%s" aria-pressed="false"><span class="ini" style="background:%s;color:%s">%s</span>%s</button>'
                % (n, bg, fg, n[0], n))
    out += ('<button type="button" class="guest" data-n="Invité" aria-pressed="false"><span class="ini" style="background:#CCD9F4;color:#283881">✦</span>'
            'Je suis invité·e</button>')   # espace visiteur : tout le site, sans les enveloppes, l’horoscope du jour ni les rôles du jour
    out += '</div><p class="hello" id="hello" role="status">Appuie sur ton prénom.</p></div></section>'

    import build_days as BD
    out += BD.horo_home_html()

    out += '<section class="bubble blue" aria-labelledby="h-trip"><h2 id="h-trip">Le voyage</h2><div class="trip"><div class="tmap">%s</div><ul class="stages">' % thai_map_svg()
    for s in D.STAGES:
        if s["id"] == "vol":
            continue
        h = D.HOTEL[s["hotel"]]
        out += ('<li><a href="#/jours/%s" data-go-day="%s" style="--c:%s"><span class="dot"></span>'
                '<span><b>%s</b><small>%s</small><small>%s</small></span><span class="go">%s</span></a></li>'
                % (s["first"], s["first"], s["color"], txt(s["city"]), txt(s["dates"]), txt(h["name"]), icon("chevr")))
    out += "</ul></div></section>"

    # l'accueil ne garde que l'essentiel : le reste est dans la barre du bas (Jeux, Utile)
    tiles = [("sand", "#/jours", "calendar", "Jours", "18 décembre → 3 janvier"),
             ("blue", "#/hotels", "bed", "Hôtels", "Adresses et téléphones"),
             ("rose", "#/metro", "train", "Métro", "Tout le réseau, à zoomer"),
             ("mustard", "#/taxi", "car", "Cartes taxi", "Les hôtels écrits en thaï")]
    out += '<div class="tiles">'
    for col, href, ic, t, sub in tiles:
        out += '<a class="tile %s" href="%s"><span class="ic">%s</span><span><b>%s</b><small>%s</small></span></a>' % (col, href, icon(ic), txt(t), txt(sub))
    out += "</div>"

    import build_games as BG
    out += BG.home_quip_html()
    out += ('<section class="bubble rose install" id="install-box" hidden aria-labelledby="h-inst"><h2 id="h-inst">Sur ton écran d’accueil</h2>'
            '<p id="install-hint"></p><div class="acts"><button class="btn" type="button" id="install-btn" hidden>Installer l’appli</button></div></section>')
    out += ('<p class="foot">Carnet Thaïlande 2026<small>version %s</small></p>' % esc(version))
    return out + "</div></main>"


# ───────────────────────── page complète ─────────────────────────
def nav_html():
    items = [("home", "#/", "home", "Accueil"), ("days", "#/jours", "calendar", "Jours"),
             ("hotels", "#/hotels", "bed", "Hôtels"), ("jeux", "#/jeux", "dice", "Jeux"), ("utile", "#/utile", "compass", "Utile")]
    return ('<nav class="nav" aria-label="Menu">%s</nav>'
            % "".join('<a href="%s" data-nav="%s"><span class="ni">%s</span>%s</a>' % (h, k, icon(ic), t) for k, h, ic, t in items))


def css_text():
    s = "\n".join(open(os.path.join(ROOT, f), encoding="utf-8").read() for f in ("app.css", "games.css", "days.css", "trad.css", "env.css"))
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return "\n".join(ln.strip() for ln in s.splitlines() if ln.strip())


def render(version, head_meta):
    import build_env as BE
    import build_games as BG
    import build_trad as BT
    body = (view_home(version) + view_days() + view_hotels() + view_utile() + BT.view_trad() + view_metro() + view_lexique() + view_taxi()
            + view_convert() + view_gtk() + BG.all_views() + BE.view_essai() + nav_html() + show_overlay() + BE.overlay_html()
            + '<div id="toast" role="status" aria-live="polite"></div>'
            + '<div id="upd" hidden><span>Une nouvelle version est prête.</span><button class="btn sm" type="button" id="upd-btn">Actualiser</button></div>')
    js = open(os.path.join(ROOT, "app.js"), encoding="utf-8").read()
    assert "/*@GAMES@*/" in js
    games = open(os.path.join(ROOT, "games.js"), encoding="utf-8").read()
    assert "/*@GAMES2@*/" in games
    games = games.replace("/*@GAMES2@*/", open(os.path.join(ROOT, "games2.js"), encoding="utf-8").read())
    assert "/*@TRANS@*/" in games
    games = games.replace("/*@TRANS@*/", open(os.path.join(ROOT, "trans.js"), encoding="utf-8").read())
    assert "/*@ENV@*/" in games
    games = games.replace("/*@ENV@*/", open(os.path.join(ROOT, "env.js"), encoding="utf-8").read())
    js = js.replace("/*@GAMES@*/", games)
    assert "</script" not in js
    # prénom déjà choisi : on masque « Qui es-tu ? » dès le premier affichage (pas de clignotement avant que le script du bas ne s'exécute)
    # Remise à zéro UNIQUE : un téléphone qui n'a pas encore cette « époque » efface tout ce qu'il avait (prénom, tampons, jeux, plats, photos).
    # Un nouvel arrivant n'a rien à effacer. NE JAMAIS changer EPOCH après le partage du lien : tout le monde perdrait sa progression.
    # CARNET_NO_RESET=1 (tests uniquement) supprime ce script : les tests posent leurs propres données avant le chargement.
    EPOCH = "2026-11-22-remise-a-zero"
    reset = "" if os.environ.get("CARNET_NO_RESET") else (
        '<script>try{var E="%s";if(localStorage.getItem("carnet.epoch")!==E){var k=[],i,n;for(i=0;i<localStorage.length;i++){n=localStorage.key(i);if(n&&n.indexOf("carnet.")===0)k.push(n)}'
        'k.forEach(function(n){localStorage.removeItem(n)});localStorage.setItem("carnet.epoch",E);try{indexedDB.deleteDatabase("carnet-thailande")}catch(e){}}}catch(e){}</script>' % EPOCH)
    early = reset + '<script>try{if(localStorage.getItem("carnet.who"))document.documentElement.classList.add("has-who")}catch(e){}</script>'
    return ('<!doctype html><html lang="fr" data-v="%s"><head>%s%s<title>Carnet Thaïlande 2026</title>%s<style>%s</style></head><body>%s%s<script>%s</script></body></html>\n'
            % (esc(version), head_meta, early, font_css(), css_text(), body, BE.data_script(), js))
