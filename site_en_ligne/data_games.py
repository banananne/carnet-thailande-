# -*- coding: utf-8 -*-
"""Étape 3 (les jeux) : textes et réglages qui ne viennent pas du PDF.
Ce qui vient du PDF est dans data_test_doudou.json, data_horoscope.json, data_motsmeles.json et site_data.QUIZ."""

# Lien de la playlist du blind test (Spotify, envoyé par Anne le 21 novembre 2026) ; si on le vide, le bouton disparaît
PLAYLIST_URL = "https://open.spotify.com/playlist/1OMK0fTqq4Q0TOFdvUxt05"

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
    ("boop", "Rapportez-moi des mangues !"),
    ("boop", "Hola que tal, ça boum les frères ?"),
    ("minou", "Je ne boude pas, je règne."),
    ("minou", "Il y a de la clim ? Sinon, je reste ici."),
    ("minou", "Réveillez-moi pour le dîner."),
    ("moomoo", "Cinq minutes de plus ?"),
    ("moomoo", "Quelqu’un a pensé au mango sticky rice ?"),
    ("moomoo", "Je pilote, Aftonsparv navigue."),
]

# la chanson du jour (playlist du voyage : une chanson par jour, choisie par Anne ; un petit texte sous la date de chaque jour)
SONGS = {
    "2026-12-18": ("Holiday", "Madonna"),
    "2026-12-19": ("Be Young, Be Foolish, Be Happy", "The Tams"),
    "2026-12-20": ("Someday We Will Dream About Today", "The Sways"),
    "2026-12-21": ("Jungle Boogie", "Kool & The Gang"),
    "2026-12-22": ("Eye of the Tiger", "Survivor"),
    "2026-12-23": ("Born to Be Wild", "Steppenwolf"),
    "2026-12-24": ("Last Christmas", "Wham!"),
    "2026-12-25": ("Underneath the Tree", "Kelly Clarkson"),
    "2026-12-26": ("Come Fly with Me", "Frank Sinatra"),
    "2026-12-27": ("Bicycle Race", "Queen"),
    "2026-12-28": ("Baby Elephant Walk", "Henry Mancini"),
    "2026-12-29": ("On the Road Again", "Willie Nelson"),
    "2026-12-30": ("Kokomo", "The Beach Boys"),
    "2026-12-31": ("Celebration", "Kool & The Gang"),
    "2027-01-01": ("What a View", "DeWolff & Dawn Brothers"),
    "2027-01-02": ("One Night in Bangkok", "Murray Head"),
    "2027-01-03": ("Beanie", "Chezile"),
}

# un doudou « guide » par jour (jamais un indice du quiz du 26 décembre)
DAY_QUIPS = {
    "2026-12-18": ("moomoo", "Un siège, un plaid, un plateau-repas : le voyage commence très bien."),
    "2026-12-19": ("boop", "Sawasdee de ma part à tout Bangkok ! Je reste à la maison, mais mon cœur est déjà dans le tuk-tuk."),
    "2026-12-20": ("aftonsparv", "Un bateau, des klongs, un coucher de soleil sur un temple : sur ma planète, ça n’existe pas !"),
    "2026-12-21": ("aftonsparv", "Des temples en briques rouges et des Bouddhas sans tête… Je prends des notes pour le quiz."),
    "2026-12-22": ("boop", "Un train au milieu des étals, des barques-boutiques… et ce soir, boxe thaï ! Je crie le plus fort, depuis le canapé."),
    "2026-12-23": ("boop", "Ce soir, street food en tuk-tuk. Allez, tout le monde dans le tuk-tuk (moi, je garde la maison) !"),
    "2026-12-24": ("boop", "Chatuchak ! Négociez bien, et rapportez-moi un porte-clés. Un seul. Enfin, trois."),
    "2026-12-25": ("minou", "Joyeux Noël depuis la maison. Les varans du parc Lumpini ? Ne clignez pas des yeux : c’est un concours."),
    "2026-12-26": ("moomoo", "Grasse matinée, avion, piscine : cinq minutes de plus, mais ensuite, le quiz !"),
    "2026-12-27": ("moomoo", "À vélo dans les ruines : je pilote, Aftonsparv navigue."),
    "2026-12-28": ("minou", "Une matinée tranquille à l’hôtel ? Enfin une idée de génie. Je vous approuve depuis mon fauteuil."),
    "2026-12-29": ("aftonsparv", "Un avion, puis la route vers la mer. Je regarde par le hublot, au cas où il y aurait des extraterrestres."),
    "2026-12-30": ("moomoo", "Piscine, plage, massage, cocktails. Quelqu’un a vu un hamac ?"),
    "2026-12-31": ("boop", "Dernier soir de l’année : musique, plage, et tout le monde danse ! Moi aussi, depuis la maison."),
    "2027-01-01": ("minou", "Bonne année. Ne me parlez pas avant midi."),
    "2027-01-02": ("moomoo", "Dernière matinée piscine… Cinq minutes de plus, s’il vous plaît."),
    "2027-01-03": ("boop", "Vous rentrez, je vous attends ! C’était le plus beau des voyages. On recommence quand ?"),
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
    ("doudou", "MASCOTTE", "Mascotte", "Faire le test de personnalité (dès le 29\u00a0décembre)"),
    ("mots", "MOTS MÊLÉS", "Mots mêlés", "Trouver les 40 mots"),
    ("blind", "BLIND TEST", "Blind test", "Marquer un point au blind test"),
    ("etoiles", "ÉTOILES", "Horoscope", "Lire l’horoscope du voyage"),
    ("photos", "PHOTOGRAPHE", "Photographe", "Prendre 5 photos du jour"),
    # jeux exclusifs au site (étape 4)
    ("defi", "DÉFI", "Défi photo", "Relever 5 défis photo"),
    ("bingo", "BINGO", "Bingo", "Faire une ligne au bingo"),
    ("mot", "MOT DU JOUR", "Mot du jour", "Dire 5 mots du jour"),
    ("gourmand", "GOURMAND", "Gourmand", "Goûter 10 plats ou boissons"),
    ("prix", "PALMARÈS", "Prix du voyage", "Décerner les prix du voyage"),
]

# ───────────── cadenas : le test de personnalité s'ouvre à une date (heure locale du téléphone) ─────────────
# Anne peut l'ouvrir plus tôt en tapant un mot secret (sans accents ni majuscules, comme sur tous les téléphones).
# Dans le site publié, seules les empreintes (FNV-1a, voir build_games.fnv) des mots sont écrites : un coup d'œil dans la page ne les révèle pas.
# Mais les mots sont ici, en clair, dans la branche `sources` du dépôt public : c'est un verrou de jeu, pas un coffre-fort.
TEST_OPEN = "2026-12-29"
TEST_OPEN_TXT = "29\u00a0décembre"   # espace insécable : le jour et le mois ne se séparent pas en fin de ligne
TEST_WORDS = ["mangoustan", "mangosteen"]
