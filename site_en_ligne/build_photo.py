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
    dot = '<i class="phc-dot" id="%s" hidden></i>'
    return ('<a class="phc phc-trav" href="#/photo-invites">%s<span class="phc-t"><small>%s</small><b>%s</b><em>%s</em></span>%s</a>'
            '<a class="phc phc-guest" href="#/reportage">%s<span class="phc-t"><small>%s</small><b>%s</b><em>%s</em></span>%s%s</a>'
            '<a class="phc phc-sm phc-msg-t" href="#/messages"><span class="phc-ic">%s</span><span class="phc-t"><b>%s</b><em>%s</em></span>%s%s</a>'
            '<a class="phc phc-sm phc-msg-g" href="#/messages"><span class="phc-ic">%s</span><span class="phc-t"><b>%s</b><em>%s</em></span>%s</a>'
            % (pol, A.txt("Pour ceux qui sont restés"), A.txt("Photo pour les invités"), A.txt("Fais un polaroïd et publie-le"), icon("chevr"),
               pol, A.txt("Le voyage en polaroïds"), A.txt("Reportage photo"), A.txt("Avec le code reçu dans ta carte"), icon("chevr"), dot % "dot-rep",
               icon("mail"), A.txt("Messages de la maison"), A.txt("Les mots de ceux qui sont restés"), icon("chevr"), dot % "dot-msg",
               icon("mail"), A.txt("Écrire aux voyageurs"), A.txt("Un mot à lire pendant le voyage"), icon("chevr")))


XMAS_TEXT = ("Ici, tout est très coloré, il fait plus de 30 degrés, et on pense très fort à vous. "
             "Vous nous manquez : on trinque à votre santé avec une noix de coco, et on vous fait de gros bisous. On a hâte de tout vous raconter !")
XMAS_PS = "P.-S. de Moomoo et d’Aftonsparv, qui sont du voyage : on veille sur eux, et on vous rapporte plein d’histoires."
NY_TEXT = ("Ici, la nouvelle année arrive six heures avant chez vous : on trinquera une première fois à minuit, heure de Bangkok, "
           "donc à 18 h chez vous. Puis on trinquera une seconde fois avec vous, à distance. "
           "On vous souhaite une année douce, drôle et pleine de belles surprises, et on a déjà hâte de la commencer avec vous. On vous embrasse très fort !")
NY_PS = "P.-S. de Boop et de Minou, restés à la maison avec vous : on garde la meilleure place pour les histoires du retour."


def _envelope(sec, env, card, hint, heading, aria, hint_txt, title, text, sign, ps, mates, cls="", hidden=True):
    """Une enveloppe à ouvrir (cachée par le script jusqu'à sa date, voir app.js, xmasPaint)."""
    imgs = "".join('<img src="img/doudou_%s.webp" alt="" width="58" height="63" loading="lazy" decoding="async">' % m for m in mates)
    return ('<section class="xmas%s" id="%s" aria-labelledby="h-%s"%s>'
            '<h2 id="h-%s">%s</h2>'
            '<button class="xm-env" id="%s" type="button" aria-expanded="false" aria-controls="%s" aria-label="%s">'
            '<span class="xm-body"></span><span class="xm-letter"></span><span class="xm-pocket"></span><span class="xm-flap"></span><span class="xm-seal">&#10022;</span></button>'
            '<p class="xm-hint" id="%s">%s</p>'
            '<div class="xm-card" id="%s" hidden><div class="xm-mates">%s</div>'
            '<h3>%s</h3><p>%s</p><p class="xm-sign">%s</p><p class="xm-ps">%s</p></div></section>'
            % (cls, sec, sec, " hidden" if hidden else "", sec, A.txt(heading), env, card, A.txt(aria), hint, A.txt(hint_txt), card, imgs,
               A.txt(title), A.txt(text), A.txt(sign), A.txt(ps)))


def xmas_html():
    """Invité·e·s : des enveloppes cachées jusqu'à leur date (heure de Paris), à ouvrir ; le mot reste ensuite sur ce téléphone (voir app.js, xmasPaint).
    La plus récente est en haut."""
    ny = _envelope("ny", "ny-env", "ny-card", "ny-hint", "Une nouvelle enveloppe", "Ouvrir l’enveloppe du Nouvel An", "Touche l’enveloppe pour l’ouvrir.",
                   "Bonne année 2027 !", NY_TEXT, "Anne, Arthur, Daphne et Flo", NY_PS, ("boop", "minou"), " ny")
    xm = _envelope("xmas", "xm-env", "xm-card", "xm-hint", "Une enveloppe pour toi", "Ouvrir l’enveloppe de Noël", "Touche l’enveloppe pour l’ouvrir.",
                   "Joyeux Noël depuis la Thaïlande !", XMAS_TEXT, "Anne, Arthur, Daphne et Flo", XMAS_PS, ("moomoo", "aftonsparv"))
    return ny + xm


def postcards_html():
    """Invité·e·s : la carte postale du jour (Moomoo ou Aftonsparv) et, repliées, les précédentes (voir app.js, guestNow). Les 17 cartes sont dans le HTML, cachées."""
    import data_cards as C
    ids = [d["id"] for d in A.D.DAYS]
    assert set(C.POSTCARDS) == set(ids), "il faut une carte par jour"
    src = ""
    for d in A.D.DAYS:
        who, text = C.POSTCARDS[d["id"]]
        src += ('<article class="pc" data-id="%s"><div class="pc-top"><p class="pc-date">%s<small>%s</small></p>'
                '<span class="pc-stamp"><img src="img/doudou_%s.webp" alt="" width="46" height="50" loading="lazy" decoding="async"></span></div>'
                '<p class="pc-t">%s</p><p class="pc-sign">%s</p></article>'
                % (d["id"], A.txt(A.day_title(d["id"])), A.txt(d["city"]), who, A.txt(text), A.txt("— " + C.NAMES[who])))
    return ('<section class="bubble post" id="pcard" aria-labelledby="h-pc" hidden><h2 id="h-pc">%s</h2>'
            '<div class="pc-cur" id="pc-cur"></div>'
            '<details class="pc-old" id="pc-old" hidden><summary>%s</summary><div id="pc-old-l"></div></details>'
            '<div id="pc-src" hidden>%s</div></section>' % (A.txt("La carte postale du jour"), A.txt("Les cartes précédentes"), src))


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


OPENS = [("", "Dès qu’ils ouvrent l’appli"), ("2026-12-25", "Le jour de Noël (25 décembre)"), ("2026-12-31", "Pour le Nouvel An (31 décembre)"), ("2027-01-02", "Pour leur dernier soir (2 janvier)")]
TOS = ["Tous", "Anne", "Arthur", "Daphne", "Flo"]


def view_messages():
    t = A.txt
    out = ('<main class="view" id="v-messages" hidden>' + A.back_head("Messages", "Entre ceux qui voyagent et ceux qui sont restés", "#/") + '<div class="wrap">')
    out += '<p class="rp-msg msg-n" id="ms-who">%s</p>' % t("Choisis ton prénom sur l’accueil pour ouvrir les messages.")
    out += ('<section class="bubble sand msg-g" id="mg-how" aria-labelledby="mg-h"><h2 id="mg-h">%s</h2><ol class="msg-steps">'
            '<li><b>%s</b> %s</li><li><b>%s</b> %s</li><li><b>%s</b> %s</li><li><b>%s</b> %s</li></ol>'
            '<p class="msg-note">%s</p></section>'
            % (t("Écrire aux voyageurs"),
               t("Le code."), t("Tape une fois le code de ta carte postale : il reste ensuite sur ce téléphone."),
               t("Ton mot."), t("Écris-le, choisis pour qui il est et quand il doit être ouvert."),
               t("Envoyer."), t("Il part sur les téléphones des voyageurs. Il est chiffré avec le code : personne d’autre ne peut le lire."),
               t("Retirer."), t("Tu peux reprendre un mot envoyé, depuis ce téléphone, dans « Mes mots envoyés »."),
               t("Ils ne répondent pas ici : ils te répondront de vive voix à leur retour, et les mots sont lus quand ils ont du réseau.")))
    out += ('<section class="bubble sand msg-lock" id="ms-lock" aria-labelledby="ms-lh" hidden><h2 id="ms-lh">%s</h2><p id="ms-lp">%s</p>'
            '<form class="rp-form" id="ms-form" autocomplete="off"><input id="ms-code" type="text" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" '
            'enterkeyhint="go" aria-label="Le code des invité·e·s" placeholder="%s"><button class="btn" type="submit">%s</button></form>'
            '<p class="rp-err" id="ms-err" role="alert"></p></section>'
            % (t("Le code"), t("C’est celui de la carte postale des invité·e·s."), t("Le code"), t("Valider")))
    sel_to = "".join('<option value="%s">%s</option>' % (x, t("Tous les quatre" if x == "Tous" else "Pour " + x)) for x in TOS)
    sel_op = "".join('<option value="%s">%s</option>' % (v, t(l)) for v, l in OPENS)
    out += ('<section class="bubble sand msg-g" id="mg-form" aria-labelledby="mg-fh" hidden><h2 id="mg-fh">%s</h2>'
            '<label class="pi-f"><span>%s</span><input id="mg-w" type="text" maxlength="30" autocomplete="off" placeholder="%s"></label>'
            '<label class="pi-f"><span>%s</span><select id="mg-to">%s</select></label>'
            '<label class="pi-f"><span>%s</span><select id="mg-op">%s</select></label>'
            '<label class="pi-f"><span>%s</span><textarea id="mg-t" maxlength="400" rows="5" placeholder="%s"></textarea></label>'
            '<p class="msg-cnt" id="mg-n" aria-hidden="true">0 / 400</p>'
            '<button class="btn" type="button" id="mg-send">%s</button><p class="pi-pst" id="mg-st" role="status"></p></section>'
            % (t("Ton mot"), t("Ton prénom"), t("Ex. Julie"), t("Pour qui ?"), sel_to, t("À ouvrir quand ?"), sel_op,
               t("Ton message"), t("Ex. On pense à vous, profitez bien du soleil !"), t("Envoyer"))
            )
    out += ('<section class="bubble msg-g" id="mg-mine" aria-labelledby="mg-mh" hidden><h2 id="mg-mh">%s</h2><ul class="msg-mine" id="mg-mine-ul"></ul></section>' % t("Mes mots envoyés"))
    out += ('<section class="msg-t" id="mt-box" hidden><p class="rp-msg" id="mt-msg" role="status"></p><div id="mt-list"></div>'
            '<p class="rp-foot"><button class="btn sm alt" type="button" id="mt-forget">%s</button></p></section>' % t("Oublier le code sur ce téléphone"))
    return out + '</div></main>'


def view_preview():
    """Page hors menus, pour Anne : montre les surprises des invité·e·s comme elles s'afficheront, sans attendre la date (/#/previsualisation)."""
    t = A.txt
    xm = _envelope("pvx", "pvx-env", "pvx-card", "pvx-hint", "Une enveloppe pour toi", "Ouvrir l’enveloppe de Noël", "Touche l’enveloppe pour l’ouvrir.",
                   "Joyeux Noël depuis la Thaïlande !", XMAS_TEXT, "Anne, Arthur, Daphne et Flo", XMAS_PS, ("moomoo", "aftonsparv"), hidden=False)
    ny = _envelope("pvn", "pvn-env", "pvn-card", "pvn-hint", "Une nouvelle enveloppe", "Ouvrir l’enveloppe du Nouvel An", "Touche l’enveloppe pour l’ouvrir.",
                   "Bonne année 2027 !", NY_TEXT, "Anne, Arthur, Daphne et Flo", NY_PS, ("boop", "minou"), " ny", hidden=False)
    out = ('<main class="view" id="v-previsu" hidden>' + A.back_head("Aperçu des surprises", "Ce que verront les invité·e·s", "#/") + '<div class="wrap">')
    out += '<p class="rp-msg">%s</p>' % t("Cette page n’est dans aucun menu. Elle montre les surprises des invité·e·s comme elles s’afficheront, sans attendre la date. Touche une enveloppe pour l’ouvrir.")
    out += ('<h2 class="pv-h">%s</h2><p class="pv-d">%s</p>%s<p class="pv-b"><button class="btn sm alt" type="button" data-pv-close="0">%s</button></p>'
            % (t("Noël"), t("Chez les invité·e·s : le 25 décembre seulement, puis l’enveloppe disparaît."), xm, t("Refermer l’enveloppe")))
    out += ('<h2 class="pv-h">%s</h2><p class="pv-d">%s</p>%s<p class="pv-b"><button class="btn sm alt" type="button" data-pv-close="1">%s</button></p>'
            % (t("Nouvel An"), t("Chez les invité·e·s : les 31 décembre et 1er janvier, puis l’enveloppe disparaît."), ny, t("Refermer l’enveloppe")))
    out += ('<h2 class="pv-h">%s</h2><p class="pv-d">%s</p>'
            '<div class="pv-step"><button class="btn sm alt" type="button" data-pv-pc="-1" aria-label="Jour précédent">%s</button><b id="pv-pc-n"></b>'
            '<button class="btn sm alt" type="button" data-pv-pc="1" aria-label="Jour suivant">%s</button></div><div id="pv-pc"></div>'
            % (t("La carte postale du jour"), t("Chez les invité·e·s, sur l’accueil, à partir du 18 décembre : une carte par jour, écrite par Moomoo ou Aftonsparv."), icon("chevl"), icon("chevr")))
    return out + '</div></main>'


def all_views():
    return view_photoinv() + view_reportage() + view_messages() + view_preview()
