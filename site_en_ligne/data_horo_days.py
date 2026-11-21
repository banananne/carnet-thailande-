# -*- coding: utf-8 -*-
"""Horoscope du jour (page d'accueil) : un texte et un conseil pour chacun des 17 jours et pour chacun des trois signes du groupe.

Bélier = Daphne · Gémeaux = Arthur · Scorpion = Anne et Flo.
Règles d'écriture :
 - « tu », jamais d'adjectif ni de participe accordé (le texte du Scorpion est lu par deux personnes) ;
 - rien qui donne une réponse au quiz du 26 décembre (aucun chiffre sur Ayutthaya, Maeklong, Jim Thompson, Chatuchak, les varans) ;
 - les jours de chance sont ceux du carnet (page 21) : Bélier 25 décembre, Gémeaux 31 décembre, Scorpion 28 décembre ;
 - chaque jour s'appuie sur le programme réel de cette journée (site_data.DAYS).
Chaque entrée : (texte, conseil), dans l'ordre des jours du 18 décembre au 3 janvier.
"""

SIGN_OF = {"Arthur": "gemeaux", "Daphne": "belier", "Flo": "scorpion", "Anne": "scorpion"}
SIGN_NAME = {"belier": "Bélier", "gemeaux": "Gémeaux", "scorpion": "Scorpion"}
LUCKY = {"belier": "2026-12-25", "gemeaux": "2026-12-31", "scorpion": "2026-12-28"}

CHANCE = "Jour de chance annoncé par le carnet !"

HORO_DAILY = {
    "belier": [
        # 18 déc. · départ
        ("Mars te souffle de décoller avant même l’annonce : tu es déjà là-bas en pensée. La seule chose qui peut te ralentir, c’est la file du contrôle des bagages.",
         "Respire, la file avance même quand on la regarde."),
        # 19 déc. · arrivée, Talat Noi
        ("Les premières odeurs de rue te réveillent : tu veux tout goûter, tout voir, tout photographier avant même d’avoir posé la valise. Mars valide, ton estomac négociera.",
         "Pose la valise d’abord, goûte ensuite."),
        # 20 déc. · bateau longtail, Jim Thompson, Wat Saket
        ("Un bateau longtail, ça démarre comme une fusée : Mars est aux commandes et tu adores ça. Sur les klongs, tu pousseras un cri de joie sans t’en rendre compte.",
         "Tiens bien ton chapeau, il rêve de nager."),
        # 21 déc. · Ayutthaya
        ("Dans les ruines d’Ayutthaya, tu marches plus vite que le guide : Mars t’a mis des ressorts dans les mollets. Les briques rouges attendront que tu aies fini de courir.",
         "Reste sur les chemins, les ruines ont plus de patience que toi."),
        # 22 déc. · marchés, boxe thaï
        ("Un train qui frôle les étals, des barques chargées de fruits, et ce soir de la boxe thaï : ta planète est en première ligne. Garde ta voix pour les encouragements.",
         "Crie « chok dee » quand le ring s’emballe."),
        # 23 déc. · Grand Palais, Wat Pho, tuk-tuk
        ("Grand Palais dès l’ouverture : tu y seras en tête de file, et Mars adore ça. Ce soir, en tuk-tuk, c’est toi qui donnes le signal du départ.",
         "Donne le signal, sans klaxonner."),
        # 24 déc. · Chatuchak, Wat Arun
        ("À Chatuchak, ton œil repère la bonne affaire en une seconde et Mars te pousse à la saisir. Face au Wat Arun, ce soir, c’est toi qui lèves ton verre en premier.",
         "Garde un peu de place dans ton sac pour demain."),
        # 25 déc. · Noël (jour de chance)
        (CHANCE + " Noël sous les palmiers te réussit : tout ce que tu tentes tombe du bon côté, jusqu’au cours de cuisine. Mars trinque avec toi.",
         "Ose le plat que tu n’as jamais goûté."),
        # 26 déc. · vol vers Sukhothaï, piscine, quiz
        ("Valises, avion, piscine, quiz : tu enchaînes tout à toute allure. Mars te donne une longueur d’avance, à toi de ne pas répondre avant la fin de la question.",
         "Lis la question jusqu’au bout avant de foncer."),
        # 27 déc. · Sukhothaï à vélo
        ("À vélo dans le parc de Sukhothaï, tu seras en tête du peloton sans l’avoir décidé. Mars te demande juste de t’arrêter pour admirer, au moins une fois.",
         "Freine à Wat Sa Si : la lumière vaut le détour."),
        # 28 déc. · matinée tranquille, Wat Saphan Hin
        ("Une matinée tranquille, ce n’est pas ton rythme, mais Mars te fait une fleur : il te laisse souffler. Au sommet du Wat Saphan Hin, tu auras retrouvé toute ton énergie.",
         "Profite de la sieste, elle est offerte."),
        # 29 déc. · avion, route vers la mer
        ("Un avion, une route, la mer au bout : voilà un jour fait pour toi. Mars tient le volant de ton énergie, tu tiendras jusqu’à l’arrivée tardive à Rayong.",
         "Garde un en-cas pour la route de nuit."),
        # 30 déc. · piscine, plage
        ("Piscine, plage, cocktail : Mars est en vacances, toi aussi. Tu seras à l’eau avant tout le monde et tu en sortiras en dernier.",
         "Mets de la crème avant de plonger."),
        # 31 déc. · réveillon
        ("Dernier soir de l’année : tu veux danser plus fort que la musique. Mars promet un minuit mémorable, à condition de garder un peu de souffle pour le compte à rebours.",
         "Bois un verre d’eau entre deux danses."),
        # 1er janv.
        ("Première journée de l’année : tu veux tout recommencer, et vite. Mars te souffle une bonne résolution, de celles qui font plaisir plutôt que de celles qu’on subit.",
         "Choisis une résolution que tu as vraiment envie de tenir."),
        # 2 janv. · dernière piscine, retour à Bangkok
        ("Dernière matinée de piscine : Mars exige un plongeon de plus. Puis la route vers Bangkok, où tu parleras déjà du prochain voyage.",
         "Plonge une dernière fois avant de boucler la valise."),
        # 3 janv. · fin du voyage
        ("Le voyage se termine, mais Mars a déjà une idée pour le suivant. Garde cet élan : tu as tout le vol du retour pour choisir la destination.",
         "Note ta prochaine destination avant l’atterrissage."),
    ],
    "gemeaux": [
        ("Mercure te met en forme avant le départ : tu as une histoire pour chaque personne croisée dans la file. Pendant le vol, tu auras de quoi alimenter dix conversations.",
         "Garde de la batterie pour le reste du voyage."),
        ("Les ruelles de Talat Noi sont faites pour toi : un détour, une rencontre, une adresse secrète. Mercure te souffle un « sa-wat-dee » au bon moment.",
         "Dis bonjour en premier, la suite viendra toute seule."),
        ("Entre les klongs et la maison de Jim Thompson, tu poses dix questions à la minute. Mercure est ravi, le guide aussi, sauf peut-être à la quatrième.",
         "Pose une question de plus que prévu."),
        ("Des siècles d’histoire, un guide bavard et toi qui ajoutes tes commentaires : Mercure applaudit. Le groupe, lui, n’a pas dit son dernier mot.",
         "Retiens un seul fait et sers-le au dîner."),
        ("Marchander est ton sport préféré et le marché flottant ton terrain de jeu. Mercure te promet un rabais, ou au moins une histoire pour le raconter.",
         "Dis « lot noi » avec ton plus grand sourire."),
        ("Entre dorures, massage et tuk-tuk, tu changes d’avis sur ta journée préférée toutes les dix minutes. Au dîner, tu auras goûté plus de plats que tu ne pourras en raconter.",
         "Garde de la place pour le dernier arrêt."),
        ("Des allées à n’en plus finir, et tu parles à tous les vendeurs. Mercure t’aide à dénicher la trouvaille que personne d’autre n’aurait osé prendre.",
         "Prends l’allée que personne ne regarde."),
        ("Noël en short, cours de cuisine, rooftop au coucher du soleil : Mercure te donne un public à chaque étape. Tu parleras un peu plus que tu n’éplucheras.",
         "Épluche d’abord, raconte ensuite."),
        ("Dans l’avion pour Sukhothaï, tu auras la vue et les mots pour la raconter. Au quiz de la piscine, Mercure te prête sa mémoire.",
         "Relis tes souvenirs de Bangkok avant le quiz."),
        ("Entre deux temples à vélo, tu changes d’avis sur ton préféré. Mercure te glisse un secret : au coucher du soleil, Wat Sa Si fera l’unanimité.",
         "Garde le plus beau temple pour la fin de journée."),
        ("Une matinée calme te laisse le temps de raconter toutes tes histoires, même celles que personne n’a demandées. Du haut de Wat Saphan Hin, tu auras enfin une vue qui te fait taire.",
         "Écoute le silence du sommet, quelques secondes."),
        ("Entre l’avion et la longue route vers Rayong, tu fais office de radio. Mercure te rappelle quand même d’éteindre l’émission quand les autres s’endorment.",
         "Parle bas quand les autres dorment."),
        ("Hamac, cocktail et conversation de plage : Mercure te prépare des heures de discussions sans queue ni tête, les meilleures.",
         "Raconte l’histoire que personne ne connaît."),
        (CHANCE + " Le réveillon est ton terrain : toasts, anecdotes, nouvelles rencontres. Mercure te prête sa langue la plus dorée.",
         "Porte un toast, tout le monde t’écoutera."),
        ("Réveil lent, chacun raconte sa soirée : tu es le meilleur public (et le meilleur conteur). Mercure applaudit.",
         "Écoute d’abord, raconte ensuite."),
        ("Une dernière fois dans l’eau, une dernière fois à table. Mercure te souffle tous les mots thaïs appris : ils reviennent pour l’occasion.",
         "Remercie en thaï avant de partir."),
        ("Mercure vient d’avoir une idée : raconter ce voyage à tout le monde, pendant des semaines. Tes amis te le pardonneront, c’est un beau récit.",
         "Commence par la meilleure anecdote."),
    ],
    "scorpion": [
        ("Pluton t’accorde un calme étrange pendant que tout le monde s’agite. Tu as vérifié les passeports deux fois, tu les vérifieras une troisième, en secret.",
         "Compte les valises plutôt que les minutes."),
        ("À peine arrivé, tu repères avant les autres l’endroit le plus intéressant du quartier. Pluton aime ton flair, tes amis un peu moins quand tu disparais.",
         "Préviens quand tu pars explorer."),
        ("Du haut du Wat Saket, la ville s’étend à tes pieds et tu retiens ton souffle. Pluton te glisse : regarde bien, la lumière ne reste pas.",
         "Reste jusqu’à la dernière lueur du coucher de soleil."),
        ("Les briques rouges et les Bouddhas sans tête te parlent plus qu’aux autres. Pluton te souffle des questions que personne n’ose poser au guide.",
         "Pose-la quand même, cette question."),
        ("Au milieu de la foule du marché, tu observes tout sans qu’on te remarque. Pluton te réserve un moment de silence sur l’eau, et ce soir de l’intensité sur le ring.",
         "Garde un moment pour regarder, sans parler."),
        ("Devant le Bouddha couché de Wat Pho, tu ressens quelque chose d’intense que tu ne diras à personne. Le massage fera le reste, Pluton te laisse savourer.",
         "Respire, le massage ne s’échappera pas."),
        ("Dans les allées de Chatuchak, tu sais exactement ce que tu cherches, même si tu ne le savais pas. Pluton te le met dans la main au dernier moment.",
         "Fais confiance à ton premier regard."),
        ("Un Noël loin des rituels te va très bien. Pluton te fait remarquer au parc Lumpini une chose que personne n’a vue : c’est ton secret, tu le garderas.",
         "Envoie une photo à quelqu’un qui pense à toi."),
        ("Tu en as retenu plus que tu ne le dis. Au quiz, tu joueras discret puis tu gagneras : Pluton adore les victoires silencieuses.",
         "Réponds sans bruit, triomphe sans bruit."),
        ("Devant le Bouddha géant de Wat Si Chum, tu ressens un silence qui n’appartient qu’à toi. Pluton t’en fait cadeau : prends ce temps-là.",
         "Fais un détour que personne n’a prévu."),
        (CHANCE + " Du sommet du Wat Saphan Hin, la plaine entière s’étale devant toi. Pluton te laisse formuler un vœu : fais-le là-haut.",
         "Fais ton vœu au sommet et garde-le."),
        ("Le test de personnalité des mascottes s’ouvre aujourd’hui. Pluton prédit que tu feras mine de t’en moquer, avant d’y répondre en premier.",
         "Réponds honnêtement : les mascottes savent."),
        ("Face à la mer, Pluton te rend lent et profond. Tu ne diras pas grand-chose, mais ce sera exactement ce qu’il fallait.",
         "Laisse le silence travailler."),
        ("Pluton te fait regarder l’année qui finit en face : ce qui a compté, ce que tu laisses derrière toi. À minuit, un vœu secret que personne ne devinera.",
         "Écris ton vœu et garde-le pour toi."),
        ("Un matin neuf, une mer calme. Pluton te laisse penser à l’année qui commence. Tu garderas l’idée pour toi, mais elle sera bonne.",
         "Note l’idée avant qu’elle s’échappe."),
        ("Pluton te dit que ce voyage a changé quelque chose en toi, d’une manière que tu ne diras pas. Une dernière nuit à Bangkok pour le sceller.",
         "Regarde la ville une dernière fois depuis ta fenêtre."),
        ("Tu ramènes plus que des souvenirs : une manière de regarder. Pluton te confie un secret du voyage, et tu sais déjà lequel.",
         "Garde un souvenir rien que pour toi."),
    ],
}

assert all(len(v) == 17 for v in HORO_DAILY.values()), {k: len(v) for k, v in HORO_DAILY.items()}
