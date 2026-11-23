# -*- coding: utf-8 -*-
"""Étape 4 : calendrier d'ouverture, horoscope du jour (accueil) et jeux exclusifs au site
(défi du jour + rôles, mot du jour, bingo, carnet gourmand, prix du voyage).
Les textes viennent de data_days.py et data_horo_days.py ; la logique est dans games.js et games2.js ; les styles dans days.css.
Tout le contenu de chaque jour est écrit dans la page et caché : le script n'affiche que le jour voulu."""
import json
import re
import unicodedata

import site_data as D
import data_games as G
import data_days as X
import data_horo_days as H
import build_app as A
import build_games as BG
from build_site import icon, sticker

esc, txt, typo = A.esc, A.txt, A.typo
IDS = [d["id"] for d in D.DAYS]
assert len(IDS) == 17 and IDS[0] == X.DAY1 and IDS[-1] == X.DAYN


def hashes():
    return ",".join(str(BG.fnv(BG.norm_word(w))) for w in G.TEST_WORDS)


def gates_json():
    """clé du jeu → date d'ouverture (le test de personnalité garde son propre écran, mais suit la même règle)"""
    g = {k: v[0] for k, v in X.GATES.items()}
    g["test"] = G.TEST_OPEN
    return esc(json.dumps(g, separators=(",", ":")))


# ───────────────────────── écran « Pas encore ! » commun aux jeux fermés ─────────────────────────
def lock_html(key):
    iso, dtxt, msg = X.GATES[key]
    p = typo(msg).replace("{d}", "<b>%s</b>" % dtxt)
    fours = "".join(BG.dd_img(d["key"], "dd-mini", lazy=True) for d in G.DOUDOUS)
    return ('<div class="bubble sand lkv" data-for="%s" hidden><div class="dd-four dd-sleep">%s</div>'
            '<h2><span class="lk-ic">%s</span>Pas encore !</h2><p>%s</p>'
            '<button class="lk-link" type="button" data-lkv="ask">J’ai le mot secret</button>'
            '<form class="lk-form lkv-form" hidden autocomplete="off"><label for="lkv-%s">Mot secret</label>'
            '<div class="lk-row"><input id="lkv-%s" name="mot" type="text" autocapitalize="none" autocorrect="off" spellcheck="false" enterkeyhint="go" maxlength="40">'
            '<button class="btn" type="submit">Ouvrir</button></div><p class="lk-err" role="status"></p></form></div>'
            % (key, fours, icon("lock"), p, key, key))


def gate(key, view):
    """Enveloppe une vue : l'écran « Pas encore ! » en tête, le contenu dans un bloc que le script cache tant que c'est fermé."""
    assert key in X.GATES, key
    head = view.index("</header>")
    i = view.index('<div class="wrap">', head) + len('<div class="wrap">')
    j = view.rindex("</div></main>")
    v = view[:i].replace('<main class="view"', '<main class="view" data-gate="%s"' % key, 1)
    return v + lock_html(key) + '<div class="gbody">' + view[i:j] + "</div>" + view[j:]


# ───────────────────────── petites pièces communes ─────────────────────────
def who_pick():
    """Quatre pastilles de prénom, montrées seulement tant qu'aucun prénom n'est choisi sur ce téléphone."""
    out = ('<div class="whopick" hidden><p>Qui es-tu ? Ton prénom reste sur ce téléphone.</p>'
           '<div class="who" role="group" aria-label="Choisis ton prénom">')
    for n, bg, fg in G.PLAYERS:
        out += ('<button type="button" data-wp="%s"><span class="ini" style="background:%s;color:%s">%s</span>%s</button>' % (n, bg, fg, n[0], n))
    out += ('<button type="button" class="guest" data-wp="Invité"><span class="ini" style="background:#CCD9F4;color:#283881">✦</span>Je suis invité·e</button>')
    return out + "</div></div>"


def daynav(kind):
    return ('<div class="dn" data-dn="%s"><button class="dn-b" type="button" data-step="-1" aria-label="Jour précédent">%s</button>'
            '<div class="dn-t" role="status" aria-live="polite"><b></b><small></small></div>'
            '<button class="dn-b" type="button" data-step="1" aria-label="Jour suivant">%s</button></div>'
            % (kind, icon("chevl"), icon("chevr")))


def day_title(i):
    return A.day_title(IDS[i])


# ───────────────────────── défi du jour (la photo de Minou ; les rôles ont été retirés à la demande d'Anne, 23 novembre) ─────────────────────────
def view_defi():
    minou = BG.dd_img("minou", "df-img", lazy=True)
    out = ('<main class="view" id="v-defi" hidden>' + A.back_head("Défi du jour", "Une mission photo pour la journée", "#/jeux")
           + '<div class="wrap"><p class="how">' + typo('Chaque jour, <b>Minou</b> envoie de loin un défi photo à toute l’équipe.') + '</p>'
           + daynav("defi"))
    for i, d in enumerate(D.DAYS):
        defi, bonus, mk = X.MISSIONS[i]
        out += ('<div class="dfd" data-i="%d" data-id="%s" data-title="%s" hidden>'
                '<section class="bubble sand mis" aria-label="Le défi photo"><div class="mis-top">%s<div><p class="mis-kick">Minou écrit de loin</p><h2>Le défi photo</h2></div></div>'
                '<p class="mis-t">%s</p><p class="mis-b">%s<span><small>Bonus mascotte</small>%s</span></p>'
                '<div class="acts"><button class="btn" type="button" data-df="done" aria-pressed="false">%s<span>Défi relevé</span></button>'
                '<a class="btn alt" href="#/jours/%s/photo">%s Prendre la photo</a></div></section></div>'
                % (i, d["id"], esc(day_title(i)), minou, txt(defi), BG.dd_img(mk, "mis-ph", lazy=True), txt(bonus),
                   icon("check"), d["id"], icon("camera")))
    out += ('<div class="mis-sum"><p class="mis-n" id="mis-n" role="status"></p><div class="dots" id="mis-dots" aria-hidden="true">%s</div></div>'
            % "".join("<i></i>" for _ in IDS))
    return out + "</div></main>"


# ───────────────────────── mot du jour ─────────────────────────
def th_size(th):
    """Taille du mot thaï selon sa longueur (sans les voyelles et tons qui s'empilent) : les longues phrases restent sur la ligne."""
    n = len(re.sub("[\u0E31\u0E34-\u0E3A\u0E47-\u0E4E]", "", th))
    return 1 if n <= 6 else 2 if n <= 9 else 3 if n <= 13 else 4 if n <= 17 else 5


def mot_attrs(m):
    th, rom, fr, tip, defi, pol = m
    q = 1 if "?" in fr else 0
    return 'data-th="%s" data-rom="%s" data-fr="%s" data-q="%d"%s' % (esc(th), esc(typo(rom)), esc(typo(fr)), q, "" if pol else " data-np")


def view_mot():
    boop = BG.dd_img("boop", "df-img", lazy=True)
    out = ('<main class="view" id="v-mot" hidden>' + A.back_head("Mot du jour", "Un mot de thaï, envoyé par Boop", "#/jeux")
           + '<div class="wrap"><p class="how">' + typo('<b>Boop</b> reste à la maison, mais il t’envoie chaque jour un mot de thaï à dire. '
             'Touche le haut-parleur pour l’<b>écouter</b>, « Montrer » pour le lire en grand.') + '</p>' + daynav("mot"))
    for i, m in enumerate(X.MOTS):
        th, rom, fr, tip, defi, pol = m
        out += ('<article class="bubble rose mt" data-i="%d" data-id="%s" data-title="%s" hidden aria-label="Le mot du jour">'
                '<div class="mt-top">%s<p class="mt-kick">Le mot de Boop</p></div>'
                '<p class="mt-th s%d" lang="th">%s</p><p class="mt-rom">%s</p><p class="mt-fr">%s</p>'
                '<div class="acts"><button class="btn" type="button" data-say %s aria-label="Écouter : %s">%s Écouter</button>'
                '<button class="btn alt" type="button" data-show %s aria-label="Montrer en grand : %s">%s Montrer</button></div>'
                '<p class="mt-tip">%s</p><p class="mt-def"><span>Le défi</span>%s</p>'
                '<button class="btn mt-done" type="button" data-mt="done" aria-pressed="false">%s<span>Je l’ai dit !</span></button></article>'
                % (i, IDS[i], esc(day_title(i)), boop, th_size(th), esc(th), txt(rom), txt(fr), mot_attrs(m), esc(typo(fr)), icon("speaker"),
                   mot_attrs(m), esc(typo(fr)), icon("fit"), txt(tip), txt(defi), icon("check")))
    out += ('<p class="mis-n" id="mt-n" role="status"></p>'
            '<details class="bubble sand mtl" id="mtl"><summary><span><b>Les mots déjà vus</b><small id="mtl-n"></small></span>%s</summary><ul class="lxl">' % icon("chevr"))
    for i, m in enumerate(X.MOTS):
        th, rom, fr, tip, defi, pol = m
        label = fr.replace("«", "").replace("»", "").strip()
        out += ('<li class="lx" data-i="%d"><button class="lx-main" type="button" data-show %s aria-label="Montrer en grand : %s">'
                '<span class="fr">%s</span><span class="rom">%s</span><span class="th" lang="th">%s</span></button>%s</li>'
                % (i, mot_attrs(m), esc(typo(label)), txt(fr), txt(rom), esc(th),
                   '<button class="lx-say" type="button" data-say %s aria-label="Écouter : %s">%s</button>' % (mot_attrs(m), esc(typo(label)), icon("speaker"))))
    return out + "</ul></details></div></main>"


# ───────────────────────── bingo d'Aftonsparv ─────────────────────────
def view_bingo():
    af = BG.dd_img("aftonsparv", "df-img", lazy=True)
    items = esc(json.dumps([[k, typo(t).replace("-", "-\u2060")] for k, t in X.BINGO], ensure_ascii=False, separators=(",", ":")))
    intro = typo("Chacun a sa grille. Dès que tu repères une chose pendant le voyage, touche la case. Une <b>ligne</b>, une <b>colonne</b> ou une <b>diagonale</b> complète : <b>bingo</b> !")
    out = ('<main class="view" id="v-bingo" hidden>' + A.back_head("Bingo", "La grille d’Aftonsparv", "#/jeux")
           + '<div class="wrap"><section class="bubble blue bg-intro"><div class="mis-top">' + af + '<div><p class="mis-kick">Aftonsparv voyage avec vous</p><h2>9 choses à repérer</h2></div></div>'
           + '<p>' + intro + '</p></section>'
           + who_pick()
           + '<p class="bg-name" id="bg-name"></p>'
             '<div class="bg" id="bg" role="group" aria-label="Ma grille de bingo" data-items="%s"></div>'
             '<p class="mis-n" id="bg-n" role="status"></p>'
             '<div class="acts bg-acts"><button class="btn sm alt" type="button" id="bg-reset">%s <span>Effacer ma grille</span></button></div></div></main>'
             % (items, icon("refresh")))
    return out


# ───────────────────────── carnet gourmand de Moomoo ─────────────────────────
def view_gourmand():
    mo = BG.dd_img("moomoo", "df-img", lazy=True)
    intro = typo("Note chaque plat ou boisson que tu goûtes avec les cœurs : <b>1</b> pour « bof », <b>5</b> pour « je le redemande ». Touche encore le même cœur pour effacer.")
    out = ('<main class="view" id="v-gourmand" hidden>' + A.back_head("Carnet gourmand", "Les plats de Moomoo", "#/jeux")
           + '<div class="wrap"><section class="bubble rose bg-intro"><div class="mis-top">' + mo + '<div><p class="mis-kick">Moomoo voyage avec vous</p><h2>À goûter, à noter</h2></div></div>'
           + '<p>' + intro + '</p></section>'
             '<p class="mis-n" id="fd-n" role="status"></p><div class="dots fd-dots" id="fd-dots" aria-hidden="true">%s</div>'
             '<section class="bubble sand fd-top" id="fd-top" hidden aria-label="Mon top 3"><h2>Mon top 3</h2><ol id="fd-top-l"></ol></section>'
             '<section class="bubble blue fd-add" aria-labelledby="h-fda"><h2 id="h-fda">Un plat qui n’est pas dans la liste ?</h2>'
             '<form class="fd-form" id="fd-form" autocomplete="off">'
             '<input id="fd-in" type="text" aria-label="Nom du plat ou de la boisson" maxlength="40" enterkeyhint="done" placeholder="Nom du plat ou de la boisson">'
             '<button class="btn sm" type="submit"><span>Ajouter</span></button></form>'
             '<ul class="fd-l fd-own" id="fd-own" aria-label="Mes plats ajoutés"></ul></section>'
             % "".join("<i></i>" for _ in range(24)))
    for gname, items in X.FOOD:
        out += '<h3 class="sech navy">%s</h3><ul class="fd-l">' % txt(gname)
        for key, nom, th, mot in items:
            hearts = "".join('<button type="button" role="radio" aria-checked="false" data-r="%d" aria-label="%d sur 5">%s</button>' % (r, r, icon("heart")) for r in range(1, 6))
            out += ('<li class="fd" data-k="%s"><div class="fd-h"><button class="fd-name" type="button" data-show data-np data-th="%s" data-fr="%s" aria-label="Montrer en grand : %s">'
                    '<b>%s</b><span class="th" lang="th">%s</span></button>'
                    '<button class="lx-say" type="button" data-say data-np data-th="%s" data-q="0" aria-label="Écouter : %s">%s</button></div>'
                    '<p class="fd-d">%s</p><div class="fd-r" role="radiogroup" aria-label="Ma note pour %s">%s</div></li>'
                    % (key, esc(th), esc(typo(nom)), esc(typo(nom)), txt(nom), esc(th), esc(th), esc(typo(nom)), icon("speaker"), txt(mot), esc(typo(nom)), hearts))
        out += "</ul>"
    return out + "</div></main>"


# ───────────────────────── prix du voyage (3 janvier) ─────────────────────────
def view_prix():
    mi = BG.dd_img("minou", "df-img", lazy=True)
    intro = typo("Minou est resté à la maison, mais il a préparé huit prix. Pour chacun, touche le prénom de la personne qui le mérite. Touche encore pour changer d’avis.")
    out = ('<main class="view" id="v-prix" hidden>' + A.back_head("Prix du voyage", "Minou a préparé le palmarès", "#/jeux")
           + '<div class="wrap"><section class="bubble sand bg-intro"><div class="mis-top">' + mi + '<div><p class="mis-kick">Minou écrit de loin</p><h2>Huit prix à décerner</h2></div></div>'
           + '<p>' + intro + '</p></section>'
             '<p class="mis-n" id="aw-n" role="status"></p><ul class="aw-l">')
    for k, title, sub in X.AWARDS:
        chips = "".join('<button type="button" role="radio" aria-checked="false" data-n="%s" style="--bg:%s;--fg:%s"><span class="ini">%s</span>%s</button>'
                        % (n, bg, fg, n[0], n) for n, bg, fg in G.PLAYERS)
        out += ('<li class="aw" data-k="%s"><div class="aw-h"><b>%s</b><small>%s</small></div><div class="aw-c" role="radiogroup" aria-label="%s">%s</div></li>'
                % (k, txt(title), txt(sub), esc(typo(title)), chips))
    out += ('</ul><section class="bubble blue aw-end" id="aw-end" hidden aria-label="Le palmarès"><div class="qz-st">%s</div><h2>Le palmarès</h2><p id="aw-tally"></p>'
            '<div class="acts"><button class="btn" type="button" id="aw-img">%s <span>Créer l’image du palmarès</span></button></div>'
            '<p class="status" id="aw-st" role="status"></p><div class="aw-prev" id="aw-prev" hidden></div></section>' % (sticker("trophee"), icon("image")))
    return out + "</div></main>"


# ───────────────────────── horoscope du jour (accueil) ─────────────────────────
def sign_id(name):
    return unicodedata.normalize("NFD", name.lower()).encode("ascii", "ignore").decode()


def horo_home_html():
    skies = {sign_id(s["name"]): BG.sky_svg(s) for s in BG.HORO}
    for k in H.SIGN_NAME:
        assert k in skies, k
    names = {n: H.SIGN_NAME[s] for n, s in H.SIGN_OF.items()}
    out = ('<section class="bubble hsd" id="hsd" aria-labelledby="h-hsd" hidden data-signs="%s" data-wait="%s">'
           '<div class="hsd-top"><div class="hsd-sky" aria-hidden="true">'
           % (esc(json.dumps(H.SIGN_OF, separators=(",", ":"))), esc(typo("Tes étoiles se réveillent le %s, jour du départ." % X.GATES["horo"][1]))))
    for k, svg in skies.items():
        out += '<span data-sign="%s" hidden>%s</span>' % (k, svg)
    out += '</div><div><h2 id="h-hsd">Ton horoscope du jour</h2><p class="hsd-sub" id="hsd-sub"></p></div></div>'
    for k in ("belier", "gemeaux", "scorpion"):
        for i, (texte, conseil) in enumerate(H.HORO_DAILY[k]):
            lucky = texte.startswith(H.CHANCE)
            body = texte[len(H.CHANCE):].strip() if lucky else texte
            out += ('<div class="hsd-i" data-sign="%s" data-i="%d" data-sub="%s"%s hidden>%s<p class="hsd-t">%s</p><p class="hsd-c"><b>Le conseil</b>%s</p></div>'
                    % (k, i, esc(typo("%s · %s" % (H.SIGN_NAME[k], day_title(i)))), " data-lucky" if lucky else "",
                       '<p class="hsd-luck">%s%s</p>' % (icon("star"), txt(H.CHANCE)) if lucky else "", txt(body), txt(conseil)))
    out += '<p class="hsd-wait" id="hsd-wait" hidden></p>'
    out += ('<div class="hsd-nav" id="hsd-nav" hidden><button class="dn-b" type="button" data-hs="-1" aria-label="Jour précédent">%s</button>'
            '<p><b>Mode essai</b><small id="hsd-nav-t"></small></p><button class="dn-b" type="button" data-hs="1" aria-label="Jour suivant">%s</button></div>'
            % (icon("chevl"), icon("chevr")))
    return out + "</section>"


# ───────────────────────── pièces pour les autres pages ─────────────────────────
def day_link_html(day_id):
    """Sur la page d'un jour : un raccourci vers le défi photo de ce jour."""
    return ('<a class="tile blue qz-cta dfl" href="#/defi/%s"><span class="ic">%s</span><span><b>Le défi du jour</b><small>Une mission photo par jour</small></span></a>'
            % (day_id, icon("camera")))


def all_views():
    return (gate("defi", view_defi()) + gate("mot", view_mot()) + gate("bingo", view_bingo()) + gate("gourmand", view_gourmand()) + gate("prix", view_prix()))
