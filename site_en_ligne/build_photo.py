# -*- coding: utf-8 -*-
"""Reportage photo : la page des voyageurs (« Photo pour les invités ») et celle des invité·e·s (« Reportage photo »).
Le JavaScript est dans photo.js, le style dans photo.css, l'outil de publication dans reportage_tool.py."""
from build_site import icon
import build_app as A


def home_cards():
    """Deux cartes sous les rubriques de l'accueil ; le style n'en montre qu'une, selon le prénom choisi (html.is-trav / html.is-guest)."""
    return ('<a class="phc phc-trav" href="#/photo-invites">%s<span><b>%s</b><small>%s</small></span>%s</a>'
            '<a class="phc phc-guest" href="#/reportage">%s<span><b>%s</b><small>%s</small></span>%s</a>'
            % (icon("camera"), A.txt("Photo pour les invités"), A.txt("Un polaroïd à partager avec ceux qui sont restés"), icon("chevr"),
               icon("image"), A.txt("Reportage photo"), A.txt("Les photos du voyage, avec un code"), icon("chevr")))


def view_photoinv():
    out = ('<main class="view" id="v-photoinv" hidden>' + A.back_head("Photo pour les invités", "Un polaroïd pour ceux qui sont restés", "#/") + '<div class="wrap">')
    out += ('<section class="bubble sand pi" aria-labelledby="pi-h"><h2 id="pi-h">%s</h2>'
            '<p>%s</p>'
            '<label class="btn pi-pick" for="pi-file">%s%s</label>'
            '<input class="pi-file" type="file" id="pi-file" accept="image/*">'
            '<p class="pi-st" id="pi-st" role="status"></p>'
            '<div class="pi-form" id="pi-form" hidden>'
            '<label class="pi-f"><span>%s</span><input id="pi-cap" type="text" maxlength="70" autocomplete="off" placeholder="%s"></label>'
            '<label class="pi-f"><span>%s</span><input id="pi-date" type="date"></label>'
            '<div class="pi-prev"><canvas id="pi-cv" width="1080" height="1500" aria-label="Aperçu du polaroïd"></canvas></div>'
            '<div class="pi-btns"><button class="btn" type="button" id="pi-share">%s%s</button>'
            '<button class="btn alt" type="button" id="pi-save">%s%s</button></div>'
            '<p class="pi-send" id="pi-send"></p>'
            '<button class="btn sm alt" type="button" id="pi-again">%s</button></div>'
            '</section>'
            '<a class="pi-rep" href="#/reportage">%s<span>%s</span></a>'
            % (A.txt("Fais un polaroïd"),
               A.txt("Choisis une photo et écris une légende : l’appli fabrique un polaroïd à partager. Tes photos du jour, elles, restent entre vous."),
               icon("camera"), A.txt("Choisir une photo"),
               A.txt("Légende"), A.txt("Ex. Le coucher de soleil au Wat Saket"), A.txt("Date de la photo"),
               icon("go"), A.txt("Partager"), icon("save"), A.txt("Enregistrer"), A.txt("Une autre photo"),
               icon("image"), A.txt("Voir le reportage tel que les invités le voient")))
    return out + '</div></main>'


def view_reportage():
    out = ('<main class="view" id="v-reportage" hidden>' + A.back_head("Reportage photo", "Le voyage en polaroïds", "#/") + '<div class="wrap">')
    out += ('<section class="bubble sand rp-lock" id="rp-lock" aria-labelledby="rp-h" hidden><h2 id="rp-h">%s</h2><p>%s</p>'
            '<form class="rp-form" id="rp-form" autocomplete="off"><input id="rp-code" type="text" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" '
            'enterkeyhint="go" aria-label="Le code des invité·e·s" placeholder="%s"><button class="btn" type="submit">%s</button></form>'
            '<p class="rp-err" id="rp-err" role="alert"></p></section>'
            % (A.txt("Réservé aux invité·e·s"), A.txt("Tape le code que tu as reçu pour voir les photos du voyage."), A.txt("Le code"), A.txt("Ouvrir")))
    out += ('<p class="rp-msg" id="rp-msg" role="status"></p><div id="rp-feed"></div>'
            '<p class="rp-foot" id="rp-foot" hidden><button class="btn sm alt" type="button" id="rp-forget">%s</button></p>'
            % A.txt("Oublier le code sur ce téléphone"))
    out += ('<div class="rp-big" id="rp-big" role="dialog" aria-modal="true" aria-label="Photo en grand" hidden>'
            '<button class="rp-x" type="button" aria-label="Fermer">%s</button><img alt=""></div>' % icon("x"))
    return out + '</div></main>'


def all_views():
    return view_photoinv() + view_reportage()
