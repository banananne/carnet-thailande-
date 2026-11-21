# -*- coding: utf-8 -*-
"""Traducteur français ⇄ thaï (onglet « Utile ») : l'écran #/traduire.
Le texte vient de data_trad.py ; la logique est dans trans.js (collé dans games.js) ; les styles dans trad.css.
Les phrases toutes prêtes sont écrites dans la page : elles marchent sans réseau. Seule une phrase libre part sur internet, quand on touche « Traduire »."""
import re

import build_app as A
import data_trad as T
from build_site import icon

esc, txt, typo = A.esc, A.txt, A.typo


def tr_row(fr, rom, th, np):
    """Une ligne du recueil : même allure et mêmes boutons que le lexique (toucher = montrer en grand, haut-parleur = écouter)."""
    q = 1 if "?" in fr else 0
    label = re.sub(r"[«»]", "", fr).strip()
    npa = " data-np" if np else ""
    return ('<li class="lx long"><button class="lx-main" type="button" data-show data-th="%s" data-rom="%s" data-fr="%s" data-q="%d"%s aria-label="Montrer en grand : %s">'
            '<span class="fr">%s</span><span class="rom">%s</span><span class="th" lang="th">%s</span></button>'
            '<button class="lx-say" type="button" data-say data-th="%s" data-q="%d"%s aria-label="Écouter : %s">%s</button></li>'
            % (esc(th), esc(typo(rom)), esc(typo(fr)), q, npa, esc(typo(label)),
               txt(fr), txt(rom), esc(th),
               esc(th), q, npa, esc(typo(label)), icon("speaker")))


def view_trad():
    n_all = sum(len(rows) for _t, rows in T.BOOK)
    out = ('<main class="view" id="v-trad" hidden data-max="%d,%d">' % (T.MAXLEN["fr"], T.MAXLEN["th"])
           + A.back_head("Traducteur", "Français ⇄ thaï, à lire et à écouter")
           + '<div class="wrap">')
    # ── la boîte de traduction ──
    out += ('<section class="bubble blue tr-box" aria-labelledby="h-tr"><h2 id="h-tr">Traduire une phrase</h2>'
            '<div class="seg tr-dir" role="group" aria-label="Sens de la traduction">'
            '<button type="button" data-tdir="fr" aria-pressed="true"><span><b>Français → thaï</b>j’écris en français</span></button>'
            '<button type="button" data-tdir="th" aria-pressed="false"><span><b>Thaï → français</b>je comprends du thaï</span></button></div>'
            '<label class="tr-lab" id="tr-lab" for="tr-in">Ta phrase en français</label>'
            '<textarea class="tr-in" id="tr-in" rows="3" maxlength="%d" lang="fr" autocomplete="off" autocapitalize="sentences" spellcheck="true" enterkeyhint="go" '
            'placeholder="Ex. : Où est la station de métro ?"></textarea>'
            '<div class="acts"><button class="btn" type="button" id="tr-go">%s <span>Traduire</span></button>'
            '<button class="btn alt" type="button" id="tr-clear">Effacer</button></div>'
            '<p class="status" id="tr-st" role="status"></p>'
            '<p class="tr-priv"><b>Il faut du réseau pour traduire une phrase libre.</b> Le texte que tu écris est alors envoyé à un service de traduction gratuit sur internet (%s, ou à défaut %s). '
            'N’y mets rien de personnel. Les phrases toutes prêtes, plus bas, marchent sans réseau.</p></section>'
            % (T.MAXLEN["fr"], icon("translate"), T.SERVICES[0], T.SERVICES[1]))
    # ── le résultat ──
    out += ('<section class="bubble sand tr-out" id="tr-out" hidden aria-label="Résultat de la traduction" data-dir="fr">'
            '<p class="tr-src" id="tr-src"></p>'
            '<div class="tr-blk tr-t"><small>En thaï</small><p class="tr-th" id="tr-th" lang="th"></p><p class="tr-rom" id="tr-rom"></p></div>'
            '<div class="tr-blk tr-f"><small>En français</small><p class="tr-fr" id="tr-fr"></p></div>'
            '<div class="acts tr-acts">'
            '<button class="btn" type="button" id="tr-say" data-say data-th="" data-q="0">%s <span>Écouter</span></button>'
            '<button class="btn alt" type="button" id="tr-show" data-show data-th="" data-rom="" data-fr="" data-q="0">%s <span>Montrer en grand</span></button>'
            '<button class="btn alt" type="button" id="tr-copy">%s <span>Copier</span></button></div>'
            '<p class="tr-warn" id="tr-warn" hidden>Traduction automatique : elle peut se tromper. Pour une chose importante, garde des phrases simples et courtes, et montre l’écran à la personne. La prononciation s’écoute avec « Écouter ».</p>'
            '</section>' % (icon("speaker"), icon("fit"), icon("copy")))
    # ── les dernières traductions (gardées sur le téléphone, lisibles sans réseau) ──
    out += ('<details class="bubble rose trs" id="tr-recent" hidden><summary><span><b>Mes dernières traductions</b><small>Gardées sur ce téléphone, lisibles sans réseau</small></span>%s</summary>'
            '<ul class="lxl" id="tr-recent-l"></ul>'
            '<div class="acts"><button class="btn sm alt" type="button" id="tr-recent-x"><span>Vider la liste</span></button></div></details>' % icon("chevr"))
    # ── le recueil de phrases toutes prêtes ──
    out += ('<h2 class="sech navy tr-h">Phrases toutes prêtes</h2>'
            '<p class="how">Sans réseau. Touche une ligne pour la <b>montrer en grand</b>, le haut-parleur pour l’<b>écouter</b>. '
            'Ton petit mot poli (ค่ะ ou ครับ) se choisit sur l’écran en grand ; il s’ajoute ensuite à toutes les phrases.</p>'
            '<div class="tr-find"><label for="tr-q">Chercher dans les %d phrases</label>'
            '<input class="tr-q" id="tr-q" type="search" enterkeyhint="search" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" placeholder="Ex. : gare, piment, pharmacie"></div>'
            '<div id="tr-book">' % n_all)
    for gi, (title, rows) in enumerate(T.BOOK):
        out += ('<details class="bubble sand lxs trg" data-g="%d"><summary><h2>%s</h2><span class="trg-n">%d</span>%s</summary><ul class="lxl">%s</ul></details>'
                % (gi, txt(title), len(rows), icon("chevr"), "".join(tr_row(*r) for r in rows)))
    out += '</div><p class="tr-none" id="tr-none" role="status" hidden>Aucune phrase trouvée. Écris-la dans la boîte du haut : elle sera traduite sur internet.</p>'
    return out + "</div></main>"
