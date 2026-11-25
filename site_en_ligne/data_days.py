# -*- coding: utf-8 -*-
"""Jeux exclusifs au site (étape 4) : rôles du jour, défis photo, mot du jour, bingo, carnet gourmand, prix du voyage, dates d'ouverture.

Seuls Aftonsparv et Moomoo voyagent (peluches) ; Boop Boops et Minou restent à la maison et « écrivent de loin ».
Les textes écrits par Claude sont à relire par Anne. Rien ici ne donne de réponse au quiz du 26 décembre.
"""

PEOPLE = ["Arthur", "Daphne", "Flo", "Anne"]

# ───────────────────────── dates d'ouverture (heure locale du téléphone ; le mot secret ouvre tout) ─────────────────────────
DAY1 = "2026-12-18"
DAYN = "2027-01-03"
NB = " "
# clé du jeu -> (date d'ouverture ISO, date écrite, phrase de l'écran « Pas encore ! » : {d} = la date en gras)
D18 = "18" + NB + "décembre"
GATES = {
    "blind":    (DAY1, D18, "Le blind test s’ouvre le {d}, le jour du départ."),
    "mots":     (DAY1, D18, "Les mots mêlés s’ouvrent le {d}, le jour du départ."),
    "horo":     (DAY1, D18, "L’horoscope s’ouvre le {d}, le jour du départ."),
    "pass":     (DAY1, D18, "Le passeport s’ouvre le {d}, le jour du départ."),
    "doudous":  (DAY1, D18, "Les mascottes s’ouvrent le {d}, le jour du départ."),
    "defi":     (DAY1, D18, "Le défi du jour s’ouvre le {d}, le jour du départ."),
    "bingo":    (DAY1, D18, "Le bingo s’ouvre le {d}, le jour du départ."),
    "mot":      (DAY1, D18, "Le mot du jour s’ouvre le {d}, le jour du départ."),
    "gourmand": (DAY1, D18, "Le carnet gourmand s’ouvre le {d}, le jour du départ."),
    "gratter":  (DAY1, D18, "La carte à gratter s’ouvre le {d}, le jour du départ."),
    "quiz":     ("2026-12-26", "26" + NB + "décembre", "Le quiz porte sur ce que vous aurez vu à Bangkok : il s’ouvre le {d}."),
    "prix":     (DAYN, "3" + NB + "janvier", "Minou délibère encore. Les prix du voyage sont décernés le {d}."),
}

# ───────────────────────── les quatre rôles (un par mascotte) ─────────────────────────
# Rotation : rôle = (rang de la personne + rang du jour) modulo 4 ; chaque jour les quatre rôles sont tous distribués,
# et chacun passe par les quatre rôles tous les quatre jours. Aucun accord au féminin ou au masculin.
ROLES = [
    dict(key="boussole", mascot="aftonsparv", name="La boussole",
         text="Tu guides le groupe : plan, horaires, bonne sortie de métro, bon sens des rues.",
         voice="Je regarde la carte. Elle est à l’envers. Ou c’est moi ?"),
    dict(key="voix", mascot="boop", name="La voix",
         text="Tu parles thaï pour tout le monde : bonjour, merci, commander, marchander.",
         voice="Allez, tout le monde dans le tuk-tuk !"),
    dict(key="fourchette", mascot="moomoo", name="La fourchette",
         text="Tu choisis les plats, tu goûtes en premier et tu donnes ton avis sans pitié.",
         voice="Quelqu’un a pensé au mango sticky rice ?"),
    dict(key="objectif", mascot="minou", name="L’objectif",
         text="Tu prends la photo du jour et tu relèves le défi de Minou.",
         voice="Je ne boude pas, je règne."),
]

# ───────────────────────── défi photo du jour (Minou) : (défi, bonus mascotte, mascotte du bonus) ─────────────────────────
# Le bonus ne met en scène que les mascottes qui voyagent : Aftonsparv et Moomoo. Toujours à distance respectueuse des statues de Bouddha.
MISSIONS = [
    ("Le trio du départ : le passeport, la carte d’embarquement et la valise, photographiés ensemble.",
     "Aftonsparv s’invite sur la valise.", "aftonsparv"),
    ("Le premier plat thaï du voyage, vu de dessus, avant la première bouchée.",
     "Moomoo garde la table.", "moomoo"),
    ("La plus belle lumière du jour : sur l’eau des klongs ou en haut du Wat Saket.",
     "Aftonsparv admire la ville depuis le bateau.", "aftonsparv"),
    ("Les briques rouges d’Ayutthaya : un détail de ruine, en gros plan.",
     "Aftonsparv pose devant les ruines (jamais sur une statue).", "aftonsparv"),
    ("Un étal de marché vu de tout près, les couleurs à fond.",
     "Moomoo goûte un fruit du marché (en photo seulement).", "moomoo"),
    ("Le plus beau détail doré du Grand Palais, en gros plan (les photos sont interdites dans la salle du Bouddha d’Émeraude).",
     "Aftonsparv devant les toits colorés.", "aftonsparv"),
    ("La trouvaille de Chatuchak : l’objet le plus improbable, tenu à bout de bras.",
     "Moomoo choisit lui aussi son souvenir.", "moomoo"),
    ("Noël sous les palmiers : toute l’équipe avec au moins un accessoire de Noël.",
     "Moomoo porte lui aussi quelque chose de rouge.", "moomoo"),
    ("L’arrivée à Sukhothaï : la première image de l’hôtel ou de sa piscine.",
     "Moomoo teste la piscine (du bord, au sec).", "moomoo"),
    ("Le groupe à vélo, vu de dos, au milieu des ruines.",
     "Aftonsparv s’accroche au guidon.", "aftonsparv"),
    ("La plaine vue d’en haut, depuis le Wat Saphan Hin.",
     "Aftonsparv face à la vue.", "aftonsparv"),
    ("Dernière image de Sukhothaï : ce que tu ne veux pas oublier.",
     "Moomoo prend l’avion, bien attaché.", "moomoo"),
    ("Les pieds dans le sable ou dans l’eau de la piscine, cadrés d’en haut.",
     "Moomoo s’installe sur un transat.", "moomoo"),
    ("Le dernier coucher de soleil de l’année.",
     "Aftonsparv compte les étoiles qui arrivent.", "aftonsparv"),
    ("La première photo de l’année : un verre, un sourire et la mer derrière.",
     "Moomoo trinque, avec une paille.", "moomoo"),
    ("La dernière baignade : un plouf, une éclaboussure, une bulle.",
     "Moomoo regarde depuis le bord (au sec, toujours).", "moomoo"),
    ("La photo souvenir du voyage : toute l’équipe, valises comprises, devant un dernier bout de Bangkok.",
     "Aftonsparv et Moomoo côte à côte pour la photo finale.", "aftonsparv"),
]

# ───────────────────────── mot du jour (Boop) ─────────────────────────
# (thaï, transcription, français, petit conseil, défi, petit mot poli ?) — transcription comme dans le lexique du carnet (p. 5)
MOTS = [
    ("สวัสดี", "sa-wat-dee", "Bonjour, au revoir", "Les hommes ajoutent khrap à la fin, les femmes kha.",
     "Entraîne-toi dans l’avion, et dis-le pour de vrai demain dès l’arrivée.", True),
    ("อร่อย", "a-roi", "Délicieux", "Dis-le avec un grand sourire : le cuisinier adore.",
     "Dis a-roi au premier plat, même s’il est tout juste correct.", True),
    ("สวยมาก", "suay mak", "Très beau, très belle", "Mak veut dire « très » : il se glisse derrière presque tout.",
     "Dis-le au coucher du soleil, devant le panorama.", False),
    ("ร้อนมาก", "ron mak", "Très chaud", "Ron = chaud, mak = très. Facile à retenir quand le soleil tape.",
     "Dis-le à voix haute quand la chaleur te tombe dessus.", False),
    ("ลดหน่อย", "lot noi", "Un petit rabais, s’il te plaît", "Souris, propose ton prix, et n’aie pas peur de dire non merci.",
     "Obtiens un rabais sur un achat (même minuscule).", True),
    ("เผ็ดน้อย", "phet noi", "Peu piquant", "Phet = piquant, noi = peu. Avec mak à la place de noi, c’est pour les braves.",
     "Commande ton plat de ce soir avec phet noi.", True),
    ("เอาอันนี้", "ao an-ni", "Je prends celui-ci", "Ao = prendre, vouloir. An-ni = celui-ci, avec le doigt qui montre.",
     "Achète ta trouvaille de Chatuchak avec cette phrase.", True),
    ("สุขสันต์วันคริสต์มาส", "suk-san wan khrit-sa-mat", "Joyeux Noël", "Suk-san = joyeux, wan = jour. C’est long, mais ça sonne bien.",
     "Souhaite un joyeux Noël à quelqu’un en thaï, un serveur par exemple.", False),
    ("สระว่ายน้ำอยู่ที่ไหน", "sa wai nam yu thi nai ?", "Où est la piscine ?", "Wai nam = nager. Remplace sa wai nam par hong nam et tu cherches les toilettes.",
     "Pose la question à l’hôtel, juste pour le plaisir.", True),
    ("จักรยาน", "jak-kra-yan", "Vélo", "Pour dire « faire du vélo », on ajoute pan : pan jak-kra-yan.",
     "Dis-le à voix haute en démarrant.", False),
    ("ใจเย็น", "jai yen", "Du calme, cool", "Littéralement « cœur frais » : jai = cœur, yen = frais. Le grand art de vivre thaï.",
     "Quand quelque chose t’agace aujourd’hui, dis jai yen à voix haute.", False),
    ("ไปกันเถอะ", "pai kan thoe", "Allons-y !", "Pai = aller, kan = ensemble.",
     "Lance-le au moment de partir vers l’aéroport.", False),
    ("ทะเล", "tha-le", "La mer", "Facile : on dirait « talé », avec le l bien net.",
     "Dis-le les pieds dans l’eau.", False),
    ("ไชโย", "chai-yo", "Hourra ! Santé !", "On le crie à pleins poumons en levant son verre.",
     "Crie-le à minuit.", False),
    ("สวัสดีปีใหม่", "sa-wat-dee pi mai", "Bonne année", "Pi = année, mai = nouveau : « bonjour, nouvelle année ».",
     "Souhaite la bonne année à quelqu’un en thaï.", True),
    ("แล้วเจอกันใหม่", "laeo choe kan mai", "À la prochaine", "Littéralement « on se retrouve de nouveau ».",
     "Dis-le à l’hôtel avant de partir.", True),
    ("ขอบคุณมาก", "khop khun mak", "Merci beaucoup", "Le mot qui résume le voyage.",
     "Dis-le une dernière fois, à quelqu’un qui t’a aidé.", True),
]

# ───────────────────────── bingo d'Aftonsparv : 16 cases tirées dans cette liste, une grille différente pour chacun ─────────────────────────
BINGO = [
    ("moine", "Un moine en robe orange"),
    ("tuk", "Un tuk-tuk décoré"),
    ("chat", "Un chat qui dort"),
    ("varan", "Un varan"),
    ("scoot", "Un scooter à trois"),
    ("fleurs", "Une offrande de fleurs"),
    ("roi", "Un portrait du roi"),
    ("seven", "Un 7-Eleven"),
    ("dore", "Un temple tout doré"),
    ("fruit", "Un fruit inconnu"),
    ("panneau", "Un panneau 100 % thaï"),
    ("chien", "Un chien qui fait la sieste"),
    ("elephant", "Un éléphant, même en statue"),
    ("fils", "Des fils électriques emmêlés"),
    ("cuisto", "Un cuisinier de rue en action"),
    ("moto", "Un moto-taxi en gilet orange"),
    ("sunset", "Un coucher de soleil sur l’eau"),
    ("noel", "Une déco de Noël sous les tropiques"),
    ("esprits", "Une maison des esprits"),
    ("gecko", "Un gecko au plafond"),
    ("ombrelle", "Un cocktail avec ombrelle"),
    ("coq", "Un coq en liberté"),
    ("couche", "Un Bouddha couché"),
    ("coco", "Une noix de coco et sa paille"),
    ("longtail", "Un bateau longtail"),
    ("brique", "Un temple en briques rouges"),
    ("geant", "Un Bouddha géant"),
    ("musicien", "Un musicien de rue"),
    ("sourire", "Un sourire échangé avec un inconnu"),
    ("feu", "Un feu d’artifice"),
]

# ───────────────────────── carnet gourmand de Moomoo : (clé, nom, thaï, petit mot) par rayon ─────────────────────────
FOOD = [
    ("Plats", [
        ("phat-thai", "Pad thaï", "ผัดไทย", "nouilles de riz sautées, cacahuètes, citron vert"),
        ("tom-yam", "Tom yam kung", "ต้มยำกุ้ง", "soupe aigre-piquante aux crevettes"),
        ("kaeng-khiao", "Curry vert", "แกงเขียวหวาน", "au lait de coco, doux ou pas"),
        ("som-tam", "Salade de papaye verte", "ส้มตำ", "croquante, et très piquante"),
        ("khao-phat", "Riz sauté", "ข้าวผัด", "avec œuf, ciboule et citron vert"),
        ("kaphrao", "Porc au basilic sacré", "ผัดกะเพรา", "avec du riz et un œuf au plat"),
        ("khao-man-kai", "Riz au poulet", "ข้าวมันไก่", "poulet poché, riz parfumé, sauce"),
        ("massaman", "Curry massaman", "แกงมัสมั่น", "doux, avec cacahuètes et pommes de terre"),
        ("kuai-tiao", "Soupe de nouilles", "ก๋วยเตี๋ยวเรือ", "les nouilles « du bateau »"),
        ("kai-yang", "Poulet grillé", "ไก่ย่าง", "avec du riz gluant et une sauce pimentée"),
        ("hoi-thot", "Omelette de moules", "หอยทอด", "croustillante, un classique de Chinatown"),
        ("phak-bung", "Liseron d’eau sauté", "ผักบุ้งไฟแดง", "le légume qui flambe au wok"),
        ("kung-phao", "Crevettes grillées", "กุ้งเผา", "à croquer au bord de la mer"),
    ]),
    ("Snacks et desserts", [
        ("mango-sticky", "Mango sticky rice", "ข้าวเหนียวมะม่วง", "riz gluant, mangue, lait de coco"),
        ("roti", "Roti", "โรตี", "crêpe croustillante, banane et chocolat"),
        ("glace-coco", "Glace à la noix de coco", "ไอศกรีมกะทิ", "souvent servie avec des cacahuètes"),
        ("banane-frite", "Bananes frites", "กล้วยทอด", "chaudes, en petit sachet"),
        ("mu-ping", "Brochettes de porc", "หมูปิ้ง", "grillées, avec du riz gluant"),
        ("popiah", "Rouleaux frits", "ปอเปี๊ยะทอด", "croustillants, sauce douce"),
    ]),
    ("Boissons", [
        ("cha-yen", "Thé glacé thaï", "ชาเย็น", "orange, sucré, au lait"),
        ("noix-coco", "Noix de coco", "น้ำมะพร้าว", "à boire à la paille"),
        ("cafe-glace", "Café glacé", "กาแฟเย็น", "fort et sucré"),
        ("jus-orange", "Jus d’orange pressé", "น้ำส้ม", "pressé à la minute"),
        ("biere-chang", "Bière Chang", "เบียร์ช้าง", "à l’ombre, de préférence"),
    ]),
]

# ───────────────────────── les prix du voyage (3 janvier, Minou) : (clé, titre, précision) ─────────────────────────
AWARDS = [
    ("sieste", "Le prix de la sieste", "Pour qui s’endort n’importe où."),
    ("boussole", "Le prix de la boussole", "Pour qui a le mieux trouvé le chemin."),
    ("voix", "Le prix de la voix d’or", "Pour le meilleur thaï, ou le plus courageux."),
    ("fourchette", "Le prix de la fourchette d’or", "Pour la meilleure fourchette du voyage."),
    ("objectif", "Le prix de l’œil de lynx", "Pour les plus belles photos."),
    ("marchandage", "Le prix du marchandage", "Pour le plus beau rabais."),
    ("rire", "Le prix du fou rire", "Pour qui a le plus fait rire les autres."),
    ("planete", "Le prix « Sur ma planète, ça n’existe pas »", "Pour la plus belle réaction de surprise."),
]

assert len(MISSIONS) == len(MOTS) == 17
assert len({b[0] for b in BINGO}) == len(BINGO) >= 16
assert sum(len(items) for _, items in FOOD) == 24


# ───────────────────────── carte à gratter du jour (un mélange : loto thaï rigolo et fortune du jour) ─────────────────────────
# Rien n'est un vrai bon : les lots sont imaginaires. Aucun accord au féminin ou au masculin.
SCRATCH_LOTO = [
    "La moitié gauche d’une vache de Moomoo. La droite est restée à la maison.",
    "Un tuk-tuk, mais seulement le bruit.",
    "Un éléphant à ta taille, livré dans ton imagination avec trois jours de retard.",
    "Le droit de rebaptiser le 7-Eleven, jusqu’à ce que quelqu’un s’en aperçoive.",
    "Un hamac qui n’existe pas, pour une sieste qui n’aura pas lieu.",
    "La moitié d’un mango sticky rice. L’autre moitié est chez Boop.",
    "Un voyage de rêve : l’aller seulement, dans ta tête.",
    "Un regard noir de Minou, valable à vie.",
    "Un câlin de Moomoo. Moomoo est en tissu : le câlin est donc un peu court.",
    "Un million de bahts en monnaie de Moomoo, soit zéro baht.",
    "Un cocktail sans glaçons, sans verre et sans cocktail.",
    "Un fou rire à retardement, à ouvrir dans six à huit mois.",
    "Une moitié de selfie, l’autre moitié est floue.",
    "Un permis de conduire le tuk-tuk, valable uniquement dans ta tête.",
    "Le plus beau coucher de soleil de la journée, en copropriété avec tout le monde.",
    "Un baiser d’éléphant, envoyé par la poste. Délai de livraison : jamais.",
    "Un ticket de loto gagnant… pour un autre loto.",
    "Zéro baht, mais zéro avec beaucoup de style.",
    "Un « bravo » prononcé par Moomoo, en meuglement.",
    "Un moustique en exclusivité mondiale, à garder de préférence loin de toi.",
]
SCRATCH_FORTUNE = [
    "Un détour inattendu mènera aujourd’hui au meilleur souvenir.",
    "Ce que tu cherches est déjà dans ton sac. Fouille mieux.",
    "Un plat dont tu ne sais pas dire le nom sera ta meilleure découverte.",
    "La chance sourit à qui goûte le piment… avec modération.",
    "Quelqu’un du groupe aura besoin d’un fou rire. Ce sera peut-être toi qui le donnes.",
    "Ne cherche pas l’ombre : elle arrive avec le prochain nuage.",
    "Une rencontre brève laissera une trace longue.",
    "Prends la ruelle que personne ne prend.",
    "Ce soir, le ciel fera un effort. Pense à le regarder.",
    "Sourire fait baisser le prix, dit-on. Essaie, pour voir.",
    "Boire de l’eau est un acte de sagesse (Aftonsparv insiste).",
    "Ton sens de l’orientation sera mis à l’épreuve. Fais confiance à la personne la plus lente.",
    "Une petite fatigue annonce une grande joie. Assieds-toi.",
    "Aujourd’hui, dis oui à la deuxième proposition.",
    "L’imprévu a bon goût, aujourd’hui.",
    "La patience est une monnaie qui n’a pas de taux de change.",
    "Quelqu’un pense à toi, de loin, avec un tout petit peu de jalousie.",
    "Un mot de politesse en thaï ouvrira un grand sourire.",
    "Ce qui tombe dans la mer est rendu à la mer, sauf les lunettes de soleil. Attention.",
    "Le meilleur moment de la journée n’a pas encore commencé.",
]
# couleur du jour en Thaïlande, selon le jour de la semaine (dimanche = 0)
SCRATCH_COLORS = ["rouge", "jaune", "rose", "vert", "orange", "bleu clair", "violet"]
