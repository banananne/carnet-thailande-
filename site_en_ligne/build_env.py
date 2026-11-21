# -*- coding: utf-8 -*-
"""Enveloppes secrètes : scellement des missions (PBKDF2-SHA256 + AES-GCM) et pièces HTML du site
(écran secret, bouton de l'accueil, page d'essai, données publiques).  Le JavaScript est dans env.js, le style dans env.css.

Ce que le site publié contient : des enveloppes CHIFFRÉES, une par personne et par vague, et les heures d'ouverture. Rien de lisible.
Le tirage au sort, les vrais textes, les codes personnels et les mots secrets ne sont JAMAIS dans ce dossier : ils vivent dans un dossier privé
(/home/claude/prive/), d'où ne sort que le fichier des enveloppes chiffrées (env_public.json), repris tel quel par le build.
Tant que ce fichier n'existe pas, le site publié n'affiche aucune enveloppe (« real » vaut null)."""
import base64, hashlib, json, os, re, unicodedata

import data_env as E

REAL_JSON = os.environ.get("ENV_REAL_JSON") or "/home/claude/prive/env_public.json"


def b64(b):
    return base64.b64encode(b).decode("ascii")


def norm_code(s):
    """Même règle que dans env.js : sans accents ni majuscules, lettres et chiffres seulement (« Essai-Démo 0000 » = « essaidemo0000 »)."""
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]", "", s)


def derive(code, salt, iters=None):
    return hashlib.pbkdf2_hmac("sha256", norm_code(code).encode("utf-8"), salt, iters or E.ITERATIONS, 32)


class _Det:
    """Hasard reproductible, réservé à la SIMULATION (la page d'essai ne change pas à chaque build). Le vrai scellement utilise `secrets`."""
    def __init__(self, seed):
        self.seed, self.n = seed.encode(), 0

    def token_bytes(self, k):
        out = b""
        while len(out) < k:
            self.n += 1
            out += hashlib.sha256(self.seed + b"|" + str(self.n).encode()).digest()
        return out[:k]


def seal_person(code, who, payloads, rng=None):
    """Une personne : un sel, une clé tirée de son code, et une enveloppe par vague. AAD = « vague|prénom » (une enveloppe ne s'ouvre pas à la place d'une autre)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if rng is None:
        import secrets as rng
    salt = rng.token_bytes(16)
    key = derive(code, salt)
    blobs = {}
    for w in sorted(payloads):
        iv = rng.token_bytes(12)
        pt = json.dumps(payloads[w], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        blobs[w] = {"iv": b64(iv), "ct": b64(AESGCM(key).encrypt(iv, pt, ("%s|%s" % (w, who)).encode("utf-8")))}
    return b64(salt), blobs


def fmt(t):
    return "%04d-%02d-%02dT%02d:%02d" % t


def sim_data():
    if not E.SIM_ON:
        return None
    salt, blobs = seal_person(E.SIM_CODE, E.SIM_WHO, E.sim_payloads(), rng=_Det("carnet-essai-enveloppes"))
    return {"s": {E.SIM_WHO: salt}, "b": {E.SIM_WHO: blobs}}


def real_data():
    """Les enveloppes chiffrées du vrai jeu (fichier produit dans le dossier privé), ou None tant qu'il n'existe pas."""
    if not os.path.exists(REAL_JSON):
        return None
    d = json.load(open(REAL_JSON, encoding="utf-8"))
    assert set(d) == {"s", "b"} and set(d["s"]) == set(d["b"]), "env_public.json : forme inattendue"
    for who, bl in d["b"].items():
        for w, x in bl.items():
            assert w in {"w1", "w2", "w3", "w4"} and set(x) == {"iv", "ct"}, (who, w)
            base64.b64decode(x["iv"], validate=True), base64.b64decode(x["ct"], validate=True)
    return d


def public_json():
    d = {"v": 1, "it": E.ITERATIONS, "win": {w: [fmt(a), fmt(b), fmt(c)] for w, a, b, c in E.WINDOWS}, "real": real_data()}
    if E.SIM_ON:
        d.update({"sim": sim_data(), "simWho": E.SIM_WHO, "simCode": E.SIM_CODE})
    return json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def data_script():
    return '<script type="application/json" id="env-data">%s</script>' % public_json()


# ───────────────────────── pièces HTML ─────────────────────────
SEAL = ('<svg viewBox="0 0 48 40" aria-hidden="true" focusable="false">'
        '<rect x="2" y="5" width="44" height="32" rx="4.5" fill="#FFFCF6" stroke="#283881" stroke-width="2"/>'
        '<path d="M3.5 8.5 24 26 44.5 8.5Z" fill="#F7D294" stroke="#283881" stroke-width="2" stroke-linejoin="round"/>'
        '<circle cx="24" cy="26" r="7.2" fill="#A51C36" stroke="#5B1025" stroke-width="1.6"/>'
        '<circle cx="24" cy="26" r="3.7" fill="none" stroke="#F7D294" stroke-width="1.3" opacity=".9"/>'
        '<path d="M19.4 23.4a5.6 5.6 0 0 1 3.2-2.1" fill="none" stroke="#fff" stroke-width="1.2" stroke-linecap="round" opacity=".6"/></svg>')


def env_btn(btn_id):
    """Le bandeau de l'accueil, sous « Bonjour … » : il n'apparaît que pendant un jeu (les textes changent selon l'heure, voir env.js)."""
    from build_app import txt
    from build_site import icon
    return ('<button class="env-btn" id="%s" type="button" hidden><span class="env-ic">%s</span>'
            '<span class="env-tx"><b>%s</b><small>%s</small></span><span class="env-go">%s</span><i class="dot" aria-hidden="true"></i></button>'
            % (btn_id, SEAL, txt("Une enveloppe t’attend"), txt("Secrète : pour toi, et seulement pour toi"), icon("chevr")))


def home_btn():
    return env_btn("env-btn")


def overlay_html():
    from build_app import txt
    from build_site import icon
    P = []
    P.append('<div id="env" class="env" role="dialog" aria-modal="true" aria-label="Enveloppe secrète" hidden>'
             '<div class="env-bar" aria-hidden="true"><i id="env-bar-i"></i></div>'
             '<button class="env-x" type="button" id="env-x" aria-label="Fermer">%s</button>'
             '<div class="env-scroll" id="env-scroll">' % icon("x"))
    # 1. le code (retapé à chaque ouverture : le téléphone ne le garde jamais, au cas où quelqu'un attraperait celui d'un autre)
    P.append('<section class="env-p" id="envp-code" hidden><div class="env-seal">%s</div>'
             '<h2 tabindex="-1">%s</h2><p class="env-lead">%s</p>'
             '<form class="env-form" id="env-form" novalidate autocomplete="off"><label for="env-in">%s</label>'
             '<input id="env-in" name="code" type="text" inputmode="text" autocapitalize="none" autocorrect="off" spellcheck="false" autocomplete="off" enterkeyhint="go" maxlength="60">'
             '<p class="env-err" id="env-err" role="alert"></p>'
             '<div class="env-row"><button class="btn env-go" type="submit" id="env-go">%s</button></div></form>'
             '<p class="env-simhint" id="env-simhint" hidden>%s <b id="env-simcode"></b> <button class="env-fill" type="button" id="env-fill">%s</button></p></section>'
             % (SEAL, txt("Ton code secret"), txt("Il est écrit sur la carte glissée dans ton carnet. Tu le retapes à chaque ouverture : si quelqu’un attrape ton téléphone, il ne verra rien."),
                txt("Ton code"), txt("Ouvrir"), txt("Essai : le code est"), txt("Le remplir pour moi")))
    # 2. le serment
    P.append('<section class="env-p" id="envp-chut" hidden><div class="env-pics" id="chut-pics"></div>'
             '<p class="env-kick" id="chut-kick"></p><p class="env-chut" id="chut-txt" tabindex="-1"></p>'
             '<button class="env-hold" type="button" id="env-hold" aria-describedby="chut-txt"><span class="env-hold-f" aria-hidden="true"></span>'
             '<span class="env-hold-t">%s</span></button></section>' % txt("Maintiens ici"))
    # 3. la mission
    # (le contexte d'abord, puis la mission, puis le gros encadré de fin ; l'heure de fin est remplie par env.js d'après le calendrier public)
    P.append('<section class="env-p env-paper" id="envp-card" hidden><p class="env-kick" id="card-kick" tabindex="-1"></p>'
             '<div class="env-ctx" id="card-ctx" hidden><p class="env-sub">%s</p><div id="card-intro"></div></div>'
             '<p class="env-sub env-sub2">%s</p><div class="env-say" id="card-say"></div>'
             '<h2 class="env-title" id="card-title" tabindex="-1"></h2><ul class="env-items" id="card-items"></ul><p class="env-foot" id="card-foot"></p>'
             '<div class="env-fin" id="card-fin" hidden><small>%s</small><b id="card-fin-d"></b><strong id="card-fin-h"></strong></div>'
             '<div class="env-row"><button class="btn alt" type="button" id="card-close">%s</button></div></section>'
             % (txt("Le jeu"), txt("Ta mission"), txt("Fin de la mission :"), txt("Refermer l’enveloppe")))
    # 4. l'enveloppe refermée
    P.append('<section class="env-p" id="envp-sealed" hidden><div class="env-seal big">%s</div><h2 tabindex="-1">%s</h2><p class="env-lead" id="sealed-p"></p>'
             '<div class="env-row"><button class="btn" type="button" id="sealed-open">%s</button><button class="btn" type="button" id="sealed-rev">%s</button></div>'
             '<p class="env-small">%s</p></section>'
             % (SEAL, txt("L’enveloppe est refermée"), txt("Rouvrir mon enveloppe"), txt("Voir la révélation"),
                txt("Ta mission s’efface de l’écran dès que tu quittes l’appli ou que tu attends trop longtemps. Pour la rouvrir, tu retapes ton code.")))
    # 5. la révélation
    P.append('<section class="env-p env-paper" id="envp-rev" hidden><p class="env-kick">%s</p><div class="env-say" id="rev-say"></div>'
             '<h2 class="env-title" id="rev-title" tabindex="-1"></h2><div class="env-tbl-w"><table class="env-tbl" id="rev-tbl"></table></div>'
             '<p class="env-score" id="rev-score" hidden></p><div class="env-row"><button class="btn" type="button" id="rev-close">%s</button></div></section>'
             % (txt("La révélation"), txt("Fermer")))
    # 6. un souci (appareil trop ancien, enveloppe absente)
    P.append('<section class="env-p" id="envp-bad" hidden><div class="env-seal">%s</div><h2 tabindex="-1">%s</h2><p class="env-lead" id="bad-p"></p>'
             '<div class="env-row"><button class="btn" type="button" id="bad-close">%s</button></div></section>' % (SEAL, txt("Oups"), txt("Fermer")))
    P.append('</div>')
    # le tableau de bord de la chasse (vague 2) : le mot, « Mot dit ! », « Passer ce mot », le score
    P.append('<div class="env-dock" id="env-dock" hidden><div class="ed-w"><small>%s</small><b id="ed-word"></b></div>'
             '<div class="ed-b"><button class="btn" type="button" id="ed-ok">%s</button><button class="btn alt" type="button" id="ed-skip">%s</button></div>'
             '<p class="ed-s"><span><b id="ed-n">0</b> <span id="ed-nl">mot dit</span></span><button type="button" id="ed-undo">%s</button></p>'
             '<p class="ed-q" id="ed-q" role="status" aria-live="polite"><b id="ed-qb">Minou</b> <span id="ed-qt"></span></p></div></div>'
             % (txt("Fais-lui dire"), txt("Mot dit !"), txt("Passer ce mot"), txt("Annuler le dernier")))
    return "".join(P)


def view_essai():
    """La page d'essai : les quatre jeux pour de faux (faux prénoms, faux mots, faux code), avec une horloge simulée.
    Elle n'est liée de nulle part ; elle disparaît du site publié quand data_env.SIM_ON vaut False."""
    if not E.SIM_ON:
        return ""
    from build_app import txt, rich, back_head
    from build_site import icon
    seg_w = "".join(
        '<button type="button" data-sw="%d" aria-pressed="false"><i class="sn">%d</i><span><b>%s</b>%s</span></button>' % (i, i, txt(t), txt(s))
        for i, t, s in [(1, "La cacahuète", "Boop · du 22 au 25 décembre"), (2, "Le killer sans victime", "Minou · le 27 décembre"),
                        (3, "Un rôle à jouer", "Moomoo et Aftonsparv · le 31 décembre"),
                        (4, "Les questions de Boop", "Boop · le 28 décembre")])
    seg_t = "".join(
        '<button type="button" data-st="%d" aria-pressed="false"><span><b>%s</b>%s</span></button>' % (i, txt(t), txt(s))
        for i, t, s in [(0, "Avant", "Rien à voir"), (1, "Pendant", "L’enveloppe est là"), (2, "Révélation", "L’heure des aveux"), (3, "Après", "Tout s’efface")])
    out = ('<main class="view" id="v-essai" hidden>' + back_head("Essai des enveloppes", "Faux prénoms, faux mots : rien n’est vrai ici", "#/")
           + '<div class="wrap">')
    out += ('<p class="how">%s</p>' % rich("Voici les quatre jeux d’enveloppes, **pour de faux**. Tu joues **Mangue**, avec de fausses missions, de faux mots et un faux code. "
                                           "Essaie comme si c’était le jour J : rien ne part nulle part, et tout reste sur ton téléphone. "
                                           "À chaque ouverture de l’enveloppe, tu retapes le code (le téléphone ne le garde pas)."))
    out += ('<section class="bubble sand" aria-labelledby="h-sw"><h2 id="h-sw">%s</h2><div class="seg col" role="group" aria-label="%s">%s</div><p id="sim-w-desc"></p></section>'
            % (txt("1. Choisis un jeu"), txt("Choisis un jeu"), seg_w))
    out += ('<section class="bubble blue" aria-labelledby="h-st"><h2 id="h-st">%s</h2><div class="seg" role="group" aria-label="%s">%s</div><p id="sim-t-desc"></p></section>'
            % (txt("2. Choisis l’heure du téléphone"), txt("Choisis l’heure du téléphone"), seg_t))
    seg_d = "".join('<button type="button" data-sd="%d" aria-pressed="false"><span><b>%s</b></span></button>' % (i, txt(t))
                    for i, t in enumerate(["Mardi 22", "Mercredi 23", "Jeudi 24", "Vendredi 25"]))
    out += ('<section class="bubble sand" id="sim-day" hidden aria-labelledby="h-sd"><h2 id="h-sd">%s</h2><div class="seg" role="group" aria-label="%s">%s</div>'
            '<p>%s</p></section>' % (txt("Jour de la cacahuète"), txt("Jour de la cacahuète"), seg_d,
                                      txt("Chaque matin, deux attentions s’ouvrent. Change de jour pour voir les suivantes apparaître.")))
    out += ('<section class="bubble rose" aria-labelledby="h-sh"><h2 id="h-sh">%s</h2>'
            '<div class="who-row"><div class="who-bar mock"><span class="who-av"><span class="ini" style="background:#F2A71B;color:#5B1025">M</span></span>'
            '<span class="who-hi">Bonjour <b>Mangue</b> !</span><span class="who-chg">Changer<span class="who-chv">%s</span></span></div>'
            '%s</div>'
            '<p id="sim-h-desc"></p><p class="sim-code">%s <b>%s</b></p></section>'
            % (txt("3. Ton accueil, avec l’enveloppe"), icon("chevr"), env_btn("sim-env-btn"), txt("Le code de l’essai :"), E.SIM_CODE))
    out += ('<div class="acts sim-acts"><button class="btn alt" type="button" id="sim-reset"><span>%s</span></button></div>'
            '<p class="hint">%s</p>' % (txt("Tout remettre à zéro"), txt("L’essai garde ton choix et ton score sur ce téléphone, jusqu’à ce que tu touches ce bouton.")))
    return out + "</div></main>"
