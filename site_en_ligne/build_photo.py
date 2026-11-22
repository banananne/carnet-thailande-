# -*- coding: utf-8 -*-
"""Reportage photo : la page des voyageurs (« Photo pour les invités ») et celle des invité·e·s (« Reportage photo »).
Le JavaScript est dans photo.js, le style dans photo.css, l'outil de publication dans reportage_tool.py."""
from build_site import icon
import build_app as A


def cfg_script():
    """Mode Supabase : l'adresse du projet et la clé PUBLIQUE (faite pour être dans le site). Refuse toute clé « secrète »."""
    import base64, json, os
    path = os.environ.get("REPORTAGE_CFG") or os.path.join(A.ROOT, "reportage_cfg.json")
    if not os.path.isfile(path):
        return ""
    cfg = json.load(open(path, encoding="utf-8"))
    url, key = cfg["url"].rstrip("/"), cfg["key"].strip()
    assert url.startswith("https://") or url.startswith("http://127.0.0.1"), "adresse du projet invalide"
    assert key and not key.startswith("sb_secret_"), "clé secrète refusée : il faut la clé publique"
    if key.startswith("eyJ"):
        payload = json.loads(base64.urlsafe_b64decode(key.split(".")[1] + "=="))
        assert payload.get("role") == "anon", "cette clé n'est pas la clé publique (role=%s) : refusée" % payload.get("role")
    return '<script type="application/json" id="rep-cfg">%s</script>' % json.dumps({"url": url, "key": key}, separators=(",", ":"))


def home_cards():
    """Une grande carte en haut de l'accueil ; le style n'en montre qu'une, selon le prénom choisi (html.is-trav / html.is-guest)."""
    pol = ('<span class="phc-pol" aria-hidden="true"><i style="--r:-9deg;--x:0px"><img src="img/doudou_minou.webp" alt="" width="40" height="45" loading="lazy" decoding="async"></i>'
           '<i style="--r:6deg;--x:24px"><img src="img/doudou_moomoo.webp" alt="" width="40" height="45" loading="lazy" decoding="async"></i>'
           '<i style="--r:-3deg;--x:48px"><img src="img/doudou_boop.webp" alt="" width="40" height="45" loading="lazy" decoding="async"></i></span>')
    return ('<a class="phc phc-trav" href="#/photo-invites">%s<span class="phc-t"><small>%s</small><b>%s</b><em>%s</em></span>%s</a>'
            '<a class="phc phc-guest" href="#/reportage">%s<span class="phc-t"><small>%s</small><b>%s</b><em>%s</em></span>%s</a>'
            % (pol, A.txt("Pour ceux qui sont restés"), A.txt("Photo pour les invités"), A.txt("Fais un polaroïd et publie-le"), icon("chevr"),
               pol, A.txt("Le voyage en polaroïds"), A.txt("Reportage photo"), A.txt("Avec le code reçu dans ta carte"), icon("chevr")))


XMAS_TEXT = ("Ici, il fait plus de 30 degrés, il y a des guirlandes dans les centres commerciaux, et on pense très fort à vous. "
             "Vous nous manquez : on trinque à votre santé avec une noix de coco, et on vous fait de gros bisous. On a hâte de tout vous raconter !")


def xmas_html():
    """Invité·e·s : une enveloppe cachée jusqu'au 25 décembre (heure de Paris), à ouvrir ; son petit mot reste ensuite sur ce téléphone (voir app.js, xmasPaint)."""
    return ('<section class="xmas" id="xmas" aria-labelledby="h-xmas" hidden>'
            '<h2 id="h-xmas">%s</h2>'
            '<button class="xm-env" id="xm-env" type="button" aria-expanded="false" aria-controls="xm-card" aria-label="%s">'
            '<span class="xm-body"></span><span class="xm-letter"></span><span class="xm-pocket"></span><span class="xm-flap"></span><span class="xm-seal">&#10022;</span></button>'
            '<p class="xm-hint" id="xm-hint">%s</p>'
            '<div class="xm-card" id="xm-card" hidden><img src="img/doudou_boop.webp" alt="" width="70" height="76" loading="lazy" decoding="async">'
            '<h3>%s</h3><p>%s</p><p class="xm-sign">%s</p><p class="xm-ps">%s</p></div></section>'
            % (A.txt("Une enveloppe pour toi"), A.txt("Ouvrir l’enveloppe de Noël"), A.txt("Touche l’enveloppe pour l’ouvrir."),
               A.txt("Joyeux Noël depuis la Thaïlande !"), A.txt(XMAS_TEXT), A.txt("Anne, Arthur, Daphne et Flo"),
               A.txt("P.-S. de Boop : j’ai gardé mon bonnet de Noël, même par 32 degrés.")))


def view_photoinv():
    out = (cfg_script() + '<main class="view" id="v-photoinv" hidden>' + A.back_head("Photo pour les invités", "Un polaroïd pour ceux qui sont restés", "#/") + '<div class="wrap">')
    out += ('<section class="bubble sand pi" aria-labelledby="pi-h"><h2 id="pi-h">%s</h2>'
            '<p>%s</p>'
            '<label class="btn pi-pick" for="pi-file">%s%s</label>'
            '<input class="pi-file" type="file" id="pi-file" accept="image/*">'
            '<p class="pi-st" id="pi-st" role="status"></p>'
            '<div class="pi-form" id="pi-form" hidden>'
            '<label class="pi-f"><span>%s</span><input id="pi-cap" type="text" maxlength="70" autocomplete="off" placeholder="%s"></label>'
            '<label class="pi-f"><span>%s</span><input id="pi-date" type="date"></label>'
            '<div class="pi-prev"><canvas id="pi-cv" width="1080" height="1500" aria-label="Aperçu du polaroïd"></canvas></div>'
            '<div class="pi-pub" id="pi-pub" hidden>'
            '<button class="btn pi-publish" type="button" id="pi-publish">%s</button>'
            '<div class="pi-codebox" id="pi-code-box" hidden><label class="pi-f"><span>%s</span>'
            '<input id="pi-code" type="text" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" enterkeyhint="go" placeholder="%s"></label>'
            '<button class="btn sm" type="button" id="pi-code-ok">%s</button></div>'
            '<p class="pi-pst" id="pi-pst" role="status"></p></div>'
            '<div class="pi-btns"><button class="btn" type="button" id="pi-share">%s%s</button>'
            '<button class="btn alt" type="button" id="pi-save">%s%s</button></div>'
            '<p class="pi-send" id="pi-send"></p>'
            '<button class="btn sm alt" type="button" id="pi-again">%s</button></div>'
            '</section>'
            '<section class="bubble sand pi-mine" id="pi-mine" aria-labelledby="pi-mh" hidden><h2 id="pi-mh">%s</h2><ul id="pi-mine-ul"></ul></section>'
            '<a class="pi-rep" href="#/reportage">%s<span>%s</span></a>'
            % (A.txt("Fais un polaroïd"),
               A.txt("Choisis une photo et écris une légende : l’appli fabrique un polaroïd à partager. Tes photos du jour, elles, restent entre vous."),
               icon("camera"), A.txt("Choisir une photo"),
               A.txt("Légende"), A.txt("Ex. Le coucher de soleil au Wat Saket"), A.txt("Date de la photo"),
               A.txt("Publier chez les invité·e·s"), A.txt("Le code des invité·e·s"), A.txt("Le code"), A.txt("Valider"),
               icon("go"), A.txt("Partager"), icon("save"), A.txt("Enregistrer"), A.txt("Une autre photo"), A.txt("Mes polaroïds publiés"),
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
