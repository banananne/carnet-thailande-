# -*- coding: utf-8 -*-
"""Enveloppes secrètes : réglages PUBLICS (fenêtres de dates) et données de SIMULATION (faux prénoms, faux mots).

Rien de réel ici : les vrais textes, le tirage, les codes personnels et les mots secrets vivent dans un fichier privé
(hors de ce dossier, jamais publié ni sauvegardé sur la branche publique `sources`). Voir build_env.py.

Forme d'une enveloppe (une par personne et par vague), chiffrée avant d'être publiée :
  m      mascottes du serment (clés : boop, minou, moomoo, aftonsparv)
  kick   petit titre (« Vague 1 · La cacahuète »)
  chut   texte du serment, dit par la mascotte
  title  titre de la mission
  say    paroles de la mascotte : [["boop", "texte"], …] ; plusieurs mascottes : "moomoo+aftonsparv"
  items  la mission, une ligne par consigne
  foot   petit texte de fin
  hunt   (vague 2) words = les mots à faire dire, dans l'ordre ; quips = petites réactions de Minou ; pass, undo, end = ses réponses
  rev    la révélation : title, say, cols, rows (une ligne par joueur : la première colonne est le prénom)
"""

SIM_ON = True                # False : la page d'essai et ses fausses données disparaissent du site publié
ITERATIONS = 150000          # PBKDF2-SHA256 : ~0,2 à 0,6 s sur un téléphone, une seule fois par téléphone

# (identifiant, apparition, révélation, effacement) en heure locale du téléphone : (année, mois, jour, heure, minute)
WINDOWS = [
    ("w1", (2026, 12, 20, 7, 0), (2026, 12, 25, 19, 0), (2026, 12, 26, 4, 0)),    # la cacahuète (Boop) : dîner de Noël
    ("w2", (2026, 12, 27, 7, 0), (2026, 12, 27, 19, 0), (2026, 12, 28, 4, 0)),    # le killer sans victime (Minou) : une journée
    ("w3", (2026, 12, 31, 7, 0), (2026, 12, 31, 20, 0), (2027, 1, 1, 6, 0)),      # un rôle à jouer (Moomoo et Aftonsparv) : réveillon
]

# ───────────────────────── simulation : tout est inventé ─────────────────────────
SIM_WHO = "Mangue"
SIM_CODE = "essai-demo-0000"
WAVES_LABEL = {"w1": "La cacahuète", "w2": "Le killer sans victime", "w3": "Un rôle à jouer"}

# Les voix des mascottes (serments et révélations) sont celles du document validé ; le reste est un exemple inventé.
CHUT = {
    "w1": "Chut ! Cette enveloppe est pour toi, et seulement pour toi. Pas un mot à ta cacahuète, au groupe, ni au chauffeur de tuk-tuk. Maintiens le doigt une seconde pour jurer.",
    "w2": "Cette enveloppe n’existe pas. Si quelqu’un t’en parle, tu ne vois pas de quoi il s’agit. Maintiens le doigt pour jurer le silence.",
    "w3": "Message crypté, niveau galactique. Il s’autodétruit demain matin et, d’ici là, il reste entre toi et ton hamac. Maintiens le doigt pour confirmer.",
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
        "m": ["boop"], "kick": "Vague 1 · La cacahuète", "chut": CHUT["w1"],
        "title": "Tu es le gorille de Litchi.",
        "say": [["boop", "Ceci est une simulation : rien n’est vrai ici, mais tout fonctionne. Allez, tout le monde dans le tuk-tuk !"]],
        "items": ["Fais apparaître une banane devant Litchi, sans dire d’où elle vient.",
                  "Garde à Litchi la meilleure place à table.",
                  "Laisse un petit mot gentil, sans signature, dans les affaires de Litchi."],
        "foot": "Chaque attention coûte moins de 100 bahts. Tu peux la déposer dans la chambre de ta cacahuète, mais tu ne fouilles rien et tu ne demandes pas de clé à la réception. Brouille les pistes : une gentillesse pour quelqu’un d’autre, de temps en temps. Si on te soupçonne, nie avec panache. Au dîner de Noël, chacun devine son gorille, puis les gorilles avouent.",
        "rev": {"title": "Les gorilles et leurs cacahuètes",
                "say": [["boop", "Allez, tout le monde à table : c’est l’heure des aveux ! Cacahuètes, devinez votre gorille. Gorilles, préparez vos excuses. Boop, qui vous voit de loin (merci le Wi-Fi)."]],
                "cols": ["Gorille", "Cacahuète", "Style"],
                "rows": [["Mangue", "Litchi", "Le gorille gourmand"], ["Litchi", "Durian", "Le gorille artiste"],
                         ["Durian", "Ramboutan", "Le gorille de l’ombre"], ["Ramboutan", "Mangue", "Le gorille serviable"]]},
    }
    w2 = {
        "m": ["minou"], "kick": "Vague 2 · Le killer sans victime", "chut": CHUT["w2"],
        "title": "Ta cible : Litchi.",
        "say": [["minou", "Je ne demande pas de la force. Je demande de l’élégance."]],
        "items": ["Fais dire à Litchi, de ce matin jusqu’au dîner, le mot que l’appli te propose, sans que la personne s’en doute.",
                  "Le mot doit sortir de la bouche de Litchi, dans une vraie phrase.",
                  "Tu ne dis jamais le mot en premier, et tu ne demandes pas de le répéter, de l’épeler ni de le lire.",
                  "Pas de jeu pendant les trajets à vélo, ni devant un Bouddha.",
                  "Dès que le mot est dit, touche « Mot dit ! » : un autre mot arrive. Qui en fait dire le plus gagne.",
                  "Quelqu’un te traque aussi."],
        "foot": "",
        "hunt": {"words": SIM_WORDS, "quips": QUIPS,
                 "pass": "Passer est permis. Le faire sans regret, non.",
                 "undo": "Revenir en arrière ? Soit. Le canapé a tout vu.",
                 "end": "Plus un seul mot en réserve. Pour une fois, je suis sans voix."},
        "rev": {"title": "Qui chassait qui",
                "say": [["minou", "Le tribunal siège. Qui devait faire dire quoi à qui ? Avouez. Je juge depuis le canapé, et je suis sévère."]],
                "cols": ["Chasseur", "Cible"],
                "rows": [["Mangue", "Litchi"], ["Litchi", "Durian"], ["Durian", "Ramboutan"], ["Ramboutan", "Mangue"]]},
    }
    w3 = {
        "m": ["moomoo", "aftonsparv"], "kick": "Vague 3 · Un rôle à jouer", "chut": CHUT["w3"],
        "title": "Aujourd’hui, tu es le parapluie.",
        "say": [["moomoo", "Cinq minutes de plus ?"], ["aftonsparv", "Sur ma planète, ça n’existe pas !"]],
        "items": ["Dès que quelqu’un dit « il va pleuvoir », réponds « je suis là » et lève le bras.",
                  "Abrite quelqu’un à chaque pas dehors, même sous un ciel bleu.",
                  "Au dessert, avoue : « Je suis le parapluie. »"],
        "foot": "Joue toute la journée sans jamais dire que c’est un rôle. Les autres devinent. À l’heure du dîner, la révélation s’affiche sur l’appli, puis chacun avoue à table. Tout s’efface demain matin.",
        "rev": {"title": "Qui était qui",
                "say": [["moomoo+aftonsparv", "À table ! Moomoo a prévu cinq minutes de plus. Aftonsparv, qui lit la carte à l’envers, demande : qui était qui ?"]],
                "cols": ["Joueur", "Rôle"],
                "rows": [["Mangue", "Le parapluie"], ["Litchi", "La lanterne"], ["Durian", "Le tapis volant"], ["Ramboutan", "Le cactus"]]},
    }
    return {"w1": w1, "w2": w2, "w3": w3}
