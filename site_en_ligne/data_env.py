# -*- coding: utf-8 -*-
"""Enveloppes secrètes : réglages PUBLICS (fenêtres de dates) et données de SIMULATION (faux prénoms, faux mots).

Rien de réel ici : les vrais textes, le tirage, les codes personnels et les mots secrets vivent dans un fichier privé
(hors de ce dossier, jamais publié ni sauvegardé sur la branche publique `sources`). Voir build_env.py.

Forme d'une enveloppe (une par personne et par vague), chiffrée avant d'être publiée :
  m      mascottes du serment (clés : boop, minou, moomoo, aftonsparv)
  kick   petit titre (« Vague 1 · La cacahuète »)
  chut   texte du serment, dit par la mascotte
  intro  « Le jeu » : le contexte, lu AVANT la mission (durée, principe, règles, « même Anne ne sait pas »), un paragraphe par ligne
  title  titre de la mission
  say    paroles de la mascotte : [["boop", "texte"], …] ; plusieurs mascottes : "moomoo+aftonsparv"
  items  la mission, une ligne par consigne
  foot   petit texte de fin
  hunt   (vague 2) words = les mots à faire dire, dans l'ordre ; quips = petites réactions de Minou ; pass, undo, end = ses réponses
  rev    la révélation : title, say, cols, rows (une ligne par joueur : la première colonne est le prénom)
L'encadré « Fin de la mission : jour, heure » du bas de la carte n'est pas dans l'enveloppe : le site le tire de WINDOWS (l'heure de la
révélation), donc il ne peut jamais contredire le calendrier. INTRO et FOOT ci-dessous sont les textes COMMUNS à tous les joueurs d'une vague :
la simulation et le vrai tirage (script privé) les reprennent tels quels, pour que les vraies cartes soient celles que tu as validées.
"""

SIM_ON = True                # False : la page d'essai et ses fausses données disparaissent du site publié
ITERATIONS = 150000          # PBKDF2-SHA256 : ~0,2 à 0,6 s sur un téléphone, à chaque ouverture de l'enveloppe (le code est retapé, jamais gardé)

# (identifiant, apparition, révélation, effacement) en heure locale du téléphone : (année, mois, jour, heure, minute)
WINDOWS = [
    ("w1", (2026, 12, 22, 7, 0), (2026, 12, 25, 20, 0), (2026, 12, 26, 4, 0)),    # la cacahuète (Boop) : du 22 au dîner de Noël (4 jours)
    ("w2", (2026, 12, 27, 7, 0), (2026, 12, 27, 20, 0), (2026, 12, 28, 4, 0)),    # le killer sans victime (Minou) : une journée
    ("w4", (2026, 12, 28, 7, 0), (2026, 12, 28, 20, 0), (2026, 12, 29, 4, 0)),    # les questions de Boop : une journée
    ("w3", (2026, 12, 31, 7, 0), (2026, 12, 31, 20, 0), (2027, 1, 1, 6, 0)),      # un rôle à jouer (Moomoo et Aftonsparv) : réveillon
]

# ───────────────────────── simulation : tout est inventé ─────────────────────────
SIM_WHO = "Mangue"
SIM_CODE = "essai-0000"      # un mot et quatre chiffres : il se retape à chaque ouverture, donc court
WAVES_LABEL = {"w1": "La cacahuète", "w2": "Le killer sans victime", "w3": "Un rôle à jouer", "w4": "Les questions de Boop"}

# Les voix des mascottes (serments et révélations) sont celles du document validé ; le reste est un exemple inventé.
CHUT = {
    "w1": "Chut ! Cette enveloppe est pour toi, et seulement pour toi. Pas un mot à ta cacahuète, au groupe, ni au chauffeur de tuk-tuk. Maintiens le doigt une seconde pour jurer.",
    "w2": "Cette enveloppe n’existe pas. Si quelqu’un t’en parle, tu ne vois pas de quoi il s’agit. Maintiens le doigt pour jurer le silence.",
    "w4": "Chut ! Cette enveloppe est pour toi, et seulement pour toi. Ni ta personne, ni le groupe, ni le serveur du petit-déjeuner ne doivent savoir que tu mènes l’enquête. Maintiens le doigt une seconde pour jurer.",
    "w3": "Message crypté, niveau galactique. Il s’autodétruit demain matin et, d’ici là, il reste entre toi et ton hamac. Maintiens le doigt pour confirmer.",
}

# « Le jeu » : lu avant la mission. Pas de prénom de joueur ici : ces textes sont les mêmes pour tout le monde.
ANNE = "Même Anne, qui a organisé le voyage, %s : tout a été tiré au sort sans elle. Elle joue à l’aveugle, comme toi."
INTRO = {
    "w1": ["Du 22 au 25 décembre, jusqu’au dîner de Noël, nous jouons tous à « la cacahuète ».",
           "Le principe : chacun est le gorille d’une personne du groupe (sa cacahuète) et la cacahuète de quelqu’un d’autre, sans savoir de qui. "
           "Un gorille veille sur sa cacahuète avec de petites attentions anonymes, sans jamais se faire repérer. Chaque matin, deux nouvelles attentions s’ouvrent ici (une facile, une plus malicieuse) : coche-les au fur et à mesure.",
           "Les règles : chaque attention coûte moins de 100 bahts. Tu peux la déposer dans la chambre de ta cacahuète, mais tu ne fouilles rien et "
           "tu ne demandes pas de clé à la réception. Brouille les pistes avec une gentillesse pour quelqu’un d’autre, de temps en temps. "
           "Si on te soupçonne, nie avec panache.",
           ANNE % "ne sait pas qui est le gorille de qui"],
    "w2": ["Aujourd’hui, toute la journée jusqu’au dîner, nous jouons tous au « killer sans victime ».",
           "Le principe : personne n’est éliminé. Chacun a une cible et des mots secrets à lui faire dire, un par un, sans qu’elle s’en doute. "
           "Qui en fait dire le plus gagne : pas de gage, seulement l’honneur.",
           ANNE % "ne connaît ni ta cible ni tes mots"],
    "w3": ["Aujourd’hui, dernier jour de l’année, jusqu’au dîner du réveillon, nous jouons tous un rôle.",
           "Le principe : chacun reçoit un personnage secret, sans cible ni mot, à jouer toute la journée sans jamais dire que c’est un rôle. "
           "Les autres doivent deviner qui joue quoi. Ce n’est pas facile, et c’est fait exprès. Tu as de quoi jouer : la mer, la chaleur, les repas, les départs…",
           ANNE % "ne sait pas quel rôle tu joues, ni ceux des autres"],
    "w4": ["Aujourd’hui, toute la journée jusqu’au dîner, nous jouons tous aux « questions de Boop ».",
           "Le principe : chacun interroge en secret une personne du groupe et lui pose quatre questions (deux simples, deux un peu plus gênantes, toujours bienveillantes), glissées dans la conversation au fil de la journée. "
           "Retiens ses réponses : ce soir, tu raconteras aux autres les questions posées et les réponses obtenues, sans dire qui tu as interrogé, et ils devront le deviner.",
           "Les règles : pose tes quatre questions naturellement, une à la fois, à des moments différents. Si la personne n’a pas envie de répondre, tu laisses tomber, sans insister. "
           "Pas de carnet ni de téléphone sous le nez : tout se retient de tête. Ce qu’on te confie reste dans le groupe.",
           ANNE % "ne sait pas qui tu interroges ni quelles questions tu poses"],
}
FOOT = {   # petit texte sous la mission ("" : aucun)
    "w1": "Au dîner de Noël, chacun devine son gorille, puis les gorilles avouent.",
    "w2": "",
    "w3": "À l’heure du dîner, la révélation s’affiche sur l’appli, puis chacun avoue à table : qui était %s ? Tout s’efface demain matin.",   # %s : la liste des rôles
    "w4": "Ce soir, chacun raconte les questions posées et les réponses obtenues, sans nommer la personne : les autres devinent. Ne regarde la révélation qu’après les devinettes.",
}

QUIPS = [
    "Noté. C’est presque élégant.",
    "Encore ? Je commence à croire en toi.",
    "Je ne bouge pas du canapé, mais j’applaudis.",
    "Tu n’as pas triché ? Je vérifierai.",
    "Un de plus. Tu m’inquiètes.",
    "Très bien. Ne prends pas la grosse tête.",
    "Je ne boude pas, je règne. Et ton travail me plaît.",
    "Continue. Le canapé te regarde.",
]

SIM_WORDS = ["kangourou", "parapluie", "trottinette", "chandelier", "xylophone", "marmotte", "spaghetti", "accordéon", "dromadaire", "cornichon"]


def sim_payloads():
    """Une enveloppe d'exemple par jeu, pour le joueur « Mangue »."""
    w1 = {
        "m": ["boop"], "kick": "Vague 1 · La cacahuète", "chut": CHUT["w1"], "intro": INTRO["w1"],
        "title": "Tu es le gorille de Litchi.",
        "say": [["boop", "Ceci est une simulation : rien n’est vrai ici, mais tout fonctionne. Allez, tout le monde dans le tuk-tuk !"]],
        "days": [{"d": "2026-12-22", "l": "Mardi 22 décembre", "a": ["Garde à Litchi la meilleure part du plat à partager.", "Fais apparaître une banane devant Litchi, sans dire d’où elle vient."]},
                 {"d": "2026-12-23", "l": "Mercredi 23 décembre", "a": ["Laisse passer Litchi en premier : la porte, le buffet.", "Laisse un petit mot gentil, sans signature, dans les affaires de Litchi."]},
                 {"d": "2026-12-24", "l": "Jeudi 24 décembre", "a": ["Remplis le verre d’eau de Litchi dès qu’il est vide.", "Dessine une scène du jour et laisse-la où Litchi la trouvera."]},
                 {"d": "2026-12-25", "l": "Vendredi 25 décembre", "a": ["Garde à Litchi la dernière part, sans dire que c’est exprès.", "Avant le dîner de Noël, dépose un fruit dans la chambre de Litchi, sans rien fouiller."]}],
        "foot": FOOT["w1"],
        "rev": {"title": "Les gorilles et leurs cacahuètes",
                "say": [["boop", "Allez, tout le monde à table : c’est l’heure des aveux ! Cacahuètes, devinez votre gorille. Gorilles, préparez vos excuses. Boop, qui vous voit de loin (merci le Wi-Fi)."]],
                "cols": ["Gorille", "Cacahuète", "Style"],
                "rows": [["Mangue", "Litchi", "Le gorille gourmand"], ["Litchi", "Durian", "Le gorille artiste"],
                         ["Durian", "Ramboutan", "Le gorille de l’ombre"], ["Ramboutan", "Mangue", "Le gorille serviable"]]},
    }
    w2 = {
        "m": ["minou"], "kick": "Vague 2 · Le killer sans victime", "chut": CHUT["w2"], "intro": INTRO["w2"],
        "title": "Ta cible : Litchi.",
        "say": [["minou", "Je ne demande pas de la force. Je demande de l’élégance."]],
        "items": ["Fais dire à Litchi, de ce matin jusqu’au dîner, le mot que l’appli te propose, sans que la personne s’en doute.",
                  "Le mot doit sortir de la bouche de Litchi, dans une vraie phrase.",
                  "Tu ne dis jamais le mot en premier, et tu ne demandes pas de le répéter, de l’épeler ni de le lire.",
                  "Pas de jeu pendant les trajets à vélo, ni devant un Bouddha.",
                  "Dès que le mot est dit, touche « Mot dit ! » : un autre mot arrive. Qui en fait dire le plus gagne.",
                  "Quelqu’un te traque aussi."],
        "foot": FOOT["w2"],
        "hunt": {"words": SIM_WORDS, "quips": QUIPS,
                 "pass": "Passer est permis. Le faire sans regret, non.",
                 "undo": "Revenir en arrière ? Soit. Le canapé a tout vu.",
                 "end": "Plus un seul mot en réserve. Pour une fois, je suis sans voix."},
        "rev": {"title": "Qui chassait qui",
                "say": [["minou", "Le tribunal siège. Qui devait faire dire quoi à qui ? Avouez. Je juge depuis le canapé, et je suis sévère."]],
                "cols": ["Chasseur", "Cible"],
                "rows": [["Mangue", "Litchi"], ["Litchi", "Durian"], ["Durian", "Ramboutan"], ["Ramboutan", "Mangue"]]},
    }
    # Un rôle d'essai doit pouvoir se jouer ici, dans ce décor : il ne pleut presque jamais en décembre, mais il fait chaud (d'où le ventilateur).
    w3 = {
        "m": ["moomoo", "aftonsparv"], "kick": "Vague 3 · Un rôle à jouer", "chut": CHUT["w3"], "intro": INTRO["w3"],
        "title": "Aujourd’hui, tu es le ventilateur.",
        "say": [["moomoo", "Il fait chaud ? Je m’en occupe."], ["aftonsparv", "Ça tourne, ça tourne… Ah non, c’est moi qui tourne."]],
        "items": ["Dès que quelqu’un dit « il fait chaud » (ça va arriver), agite doucement un menu, un livre ou ta main devant son visage, sans un mot.",
                  "Quand on te parle, tourne lentement la tête de gauche à droite, comme si tu brassais l’air autour de toi. Garde ton sérieux.",
                  "Au dessert, avoue : « Je suis le ventilateur. » Puis rafraîchis toute la table une dernière fois."],
        "foot": FOOT["w3"] % "le ventilateur, le glaçon, le tuk-tuk, le palmier",
        "rev": {"title": "Qui était qui",
                "say": [["moomoo+aftonsparv", "À table ! Moomoo a prévu cinq minutes de plus. Aftonsparv, qui lit la carte à l’envers, demande : qui était qui ?"]],
                "cols": ["Joueur", "Rôle"],
                "rows": [["Mangue", "Le ventilateur"], ["Litchi", "Le glaçon"], ["Durian", "Le tuk-tuk"], ["Ramboutan", "Le palmier"]]},
    }
    w4 = {
        "m": ["boop"], "kick": "Vague 4 · Les questions de Boop", "chut": CHUT["w4"], "intro": INTRO["w4"],
        "title": "Ta personne : Litchi.",
        "say": [["boop", "Ceci est une simulation : de fausses questions, pour de faux. Une question, ça ne mord pas."]],
        "items": ["Quel est le fruit que tu manges le plus vite ?",
                  "Quelle est la dernière chose que tu as perdue et jamais retrouvée ?",
                  "Quel petit objet de voyage ne quitte jamais ton sac ?",
                  "Quelle est la chose la plus bizarre que tu fais chez toi, sans aucun témoin ?",
                  "Pose-les à des moments différents, naturellement, et retiens les réponses : ce soir, tu raconteras les questions et les réponses aux autres."],
        "foot": FOOT["w4"],
        "rev": {"title": "Qui interrogeait qui",
                "say": [["boop", "À table ! Racontez vos questions et vos réponses, et devinez qui était interrogé. Boop, qui écoute de loin (merci le Wi-Fi), prend des notes."]],
                "cols": ["Enquêteur", "Personne interrogée"],
                "rows": [["Mangue", "Litchi"], ["Litchi", "Durian"], ["Durian", "Ramboutan"], ["Ramboutan", "Mangue"]]},
    }
    return {"w1": w1, "w2": w2, "w3": w3, "w4": w4}
