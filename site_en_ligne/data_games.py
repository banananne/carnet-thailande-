# -*- coding: utf-8 -*-
"""Étape 3 (les jeux) : textes et réglages qui ne viennent pas du PDF.
Ce qui vient du PDF est dans data_test_doudou.json, data_horoscope.json, data_motsmeles.json et site_data.QUIZ."""

# Lien de la playlist du blind test : à remplir quand Anne l'envoie (tant que c'est vide, le bouton n'apparaît pas)
PLAYLIST_URL = ""

PLAYERS = [("Arthur", "#283881", "#FFFFFF"), ("Daphne", "#E9A9B8", "#5B1025"), ("Flo", "#F2A71B", "#5B1025"), ("Anne", "#A51C36", "#FFFFFF")]

# ───────────── les quatre doudous (clé = celle du test : ★ aftonsparv, ■ boop, ▲ minou, ● moomoo) ─────────────
DOUDOUS = [
    dict(key="aftonsparv", name="Aftonsparv", short="Aftonsparv", bg="#F7D294",
         alt="Aftonsparv, mascotte extraterrestre verte en maillot argenté", photo="doudou_aftonsparv.webp"),
    dict(key="boop", name="Boop Boops", short="Boop", bg="#CCD9F4",
         alt="Boop Boops, mascotte en forme de homard orange, en bonnet de Père Noël", photo="doudou_boop.webp"),
    dict(key="minou", name="Minou minou the dark lord", short="Minou", bg="#F5E6E9",
         alt="Minou minou the dark lord, mascotte en forme de chat noir", photo="doudou_minou.webp"),
    dict(key="moomoo", name="Moomoo", short="Moomoo", bg="#FCE9C5",
         alt="Moomoo, mascotte en forme de vache noire et blanche", photo="doudou_moomoo.webp"),
]

# petits mots tirés au hasard sur l'accueil (le premier de chaque doudou est sa phrase du carnet)
HOME_QUIPS = [
    ("aftonsparv", "Sur ma planète, ça n’existe pas !"),
    ("aftonsparv", "J’ai repéré trois choses bizarres. On y va ?"),
    ("aftonsparv", "Un panneau en thaï ! Je le lis jusqu’au bout."),
    ("boop", "Allez, tout le monde dans le tuk-tuk !"),
    ("boop", "Photo de groupe ! Tout le monde se serre !"),
    ("boop", "Je connais déjà le vendeur de mangues."),
    ("minou", "Je ne boude pas, je règne."),
    ("minou", "Il y a de la clim ? Sinon, je reste ici."),
    ("minou", "Réveillez-moi pour le dîner."),
    ("moomoo", "Cinq minutes de plus ?"),
    ("moomoo", "Quelqu’un a pensé au mango sticky rice ?"),
    ("moomoo", "Je pilote, Aftonsparv navigue."),
]

# un doudou « guide » par jour (jamais un indice du quiz du 26 décembre)
DAY_QUIPS = {
    "2026-12-18": ("moomoo", "Un siège, un plaid, un plateau-repas : le voyage commence très bien."),
    "2026-12-19": ("boop", "Premier jour, premier marché, premiers copains : je suis déjà en mode tuk-tuk !"),
    "2026-12-20": ("aftonsparv", "Un bateau, des klongs, un coucher de soleil sur un temple : sur ma planète, ça n’existe pas !"),
    "2026-12-21": ("aftonsparv", "Des temples en briques rouges et des Bouddhas sans tête… Je prends des notes pour le quiz."),
    "2026-12-22": ("boop", "Un train au milieu des étals, des barques-boutiques… et ce soir, boxe thaï ! Je crie le plus fort."),
    "2026-12-23": ("boop", "Ce soir, street food en tuk-tuk. Allez, tout le monde dans le tuk-tuk !"),
    "2026-12-24": ("boop", "Chatuchak ! Je négocie, je discute, et je repars avec trois porte-clés et un nouvel ami."),
    "2026-12-25": ("minou", "Noël au parc Lumpini : les varans me regardent, je les regarde. Personne ne cligne."),
    "2026-12-26": ("moomoo", "Grasse matinée, avion, piscine : cinq minutes de plus, mais ensuite, le quiz !"),
    "2026-12-27": ("moomoo", "À vélo dans les ruines : je pilote, Aftonsparv navigue."),
    "2026-12-28": ("minou", "Une matinée tranquille à l’hôtel ? Enfin une idée de génie."),
    "2026-12-29": ("aftonsparv", "Un avion, puis la route vers la mer. Je regarde par le hublot, au cas où il y aurait des extraterrestres."),
    "2026-12-30": ("moomoo", "Piscine, plage, massage, cocktails. Quelqu’un a vu un hamac ?"),
    "2026-12-31": ("boop", "Dernier soir de l’année : musique, plage, et tout le monde danse !"),
    "2027-01-01": ("minou", "Bonne année. Ne me parlez pas avant midi."),
    "2027-01-02": ("moomoo", "Dernière matinée piscine… Cinq minutes de plus, s’il vous plaît."),
    "2027-01-03": ("boop", "Merci la Thaïlande ! C’était le plus beau des voyages. On recommence quand ?"),
}

# ───────────── quiz du 26 décembre ─────────────
QUIZ_MSGS = {
    6: "Sans faute ! Le cocktail est pour toi.",
    5: "Presque parfait : le cocktail est à portée de paille.",
    4: "Belle performance : tu as bien écouté les guides.",
    3: "Moitié-moitié : un demi-cocktail, sans glaçons.",
    2: "On dira que c’était la chaleur.",
    1: "Un seul point… mais les massages, eux, tu les as bien retenus.",
    0: "Zéro ! Tu dormais dans le tuk-tuk ? Heureusement, on peut rejouer.",
}

# ───────────── passeport : un mot-clé par jour, et les tampons spéciaux ─────────────
STAMP_WORDS = {
    "2026-12-18": "DÉPART", "2026-12-19": "ARRIVÉE", "2026-12-20": "LONGTAIL", "2026-12-21": "AYUTTHAYA",
    "2026-12-22": "MARCHÉS", "2026-12-23": "GRAND PALAIS", "2026-12-24": "CHATUCHAK", "2026-12-25": "JOYEUX NOËL",
    "2026-12-26": "ENVOL", "2026-12-27": "À VÉLO", "2026-12-28": "WAT SAPHAN HIN", "2026-12-29": "VERS LA MER",
    "2026-12-30": "PLAGE", "2026-12-31": "RÉVEILLON", "2027-01-01": "BONNE ANNÉE", "2027-01-02": "RETOUR",
    "2027-01-03": "À BIENTÔT",
}

# (clé, mot du tampon, titre affiché, comment on le gagne)
BONUS_STAMPS = [
    ("quiz", "QUIZZZZ", "Quiz", "Aller au bout du quiz du 26 décembre"),
    ("doudou", "MASCOTTE", "Mascotte", "Faire le test de personnalité"),
    ("mots", "MOTS MÊLÉS", "Mots mêlés", "Trouver les 40 mots"),
    ("blind", "BLIND TEST", "Blind test", "Marquer un point au blind test"),
    ("etoiles", "ÉTOILES", "Horoscope", "Lire l’horoscope du voyage"),
    ("photos", "PHOTOGRAPHE", "Photographe", "Prendre 5 photos du jour"),
]
