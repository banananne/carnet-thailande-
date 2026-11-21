# -*- coding: utf-8 -*-
"""Contenu du carnet en ligne, repris du Journal_de_bord.pdf (version du 20 novembre 2026).

Les textes des jours viennent des pages 6 à 18 du PDF (extraction vérifiée à l'œil contre les pages).
Corrections faites uniquement dans la version en ligne (le PDF n'est pas touché) :
 - « hotel » → « hôtel », « Diner » → « Dîner », « Sukothai / Sukhothai » → « Sukhothaï » ;
 - quiz du 26 : la question des varans est la n° 6, avec ses réponses A / B / C ;
 - fun fact du massage thaï (p. 18) : « y est enseigné et est inscrit » ;
 - espaces insécables avant « : ; ? ! », apostrophes courbes.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ───────────────────────── étapes du voyage ─────────────────────────
# couleur = trait sous la date dans la frise des jours, point dans la carte
STAGES = [
    dict(id="vol", city="En route", dates="18 → 19 décembre", hotel=None, first="2026-12-18", color="#B3C4EB", short="Vol"),
    dict(id="s1", city="Bangkok", dates="19 → 26 décembre", hotel="h1", first="2026-12-19", color="#A51C36", short="Bangkok"),
    dict(id="s2", city="Sukhothaï", dates="26 → 29 décembre", hotel="h2", first="2026-12-26", color="#F2A71B", short="Sukhothaï"),
    dict(id="s3", city="Ban Phe", dates="29 décembre → 2 janvier", hotel="h3", first="2026-12-29", color="#283881", short="Ban Phe"),
    dict(id="s4", city="Bangkok", dates="2 → 3 janvier", hotel="h4", first="2027-01-02", color="#E9A9B8", short="Bangkok"),
]
STAGE = {s["id"]: s for s in STAGES}

# ───────────────────────── hôtels (page 4) ─────────────────────────
HOTELS = [
    dict(id="h1", name="C’HOUSE", city="Bangkok", dates="19 → 26 décembre", nights="7 nuits", stage="s1",
         addr="114 Salak Hin Alley, Rong Mueang, Pathum Wan, Bangkok 10330, Thaïlande",
         q="C'HOUSE Bangkok, 114 Salak Hin Alley, Rong Mueang, Pathum Wan, Bangkok 10330", ll="13.73991585,100.51773834",
         phone="+66 97 005 4500", tel="+66970054500", mail="c.house.bangkok@gmail.com"),
    dict(id="h2", name="Thai Thai Sukhothaï Resort", city="Sukhothaï", dates="26 → 29 décembre", nights="3 nuits", stage="s2",
         addr="95/8 Moo 3 Napho-Khirimas Road Historical Park Mueang Kao, Mueang Sukhothai District, Sukhothai 64210, Thaïlande",
         q="Thai Thai Sukhothai Resort, 95/8 Moo 3 Napho-Khirimas Road, Sukhothai 64210",
         phone="+66 84 932 1006", tel="+66849321006", mail=None),
    dict(id="h3", name="Novotel Rayong Rim Pae Resort", city="Ban Phe", dates="29 décembre → 2 janvier", nights="4 nuits", stage="s3",
         addr="4/5 Moo 3, Pae Klaeng Kram Road, CHARK PONG KLAENG, 21190 RAYONG, Thaïlande",
         q="Novotel Rayong Rim Pae Resort, 4/5 Moo 3 Pae Klaeng Kram Road, Rayong 21190",
         phone="+66 33 010 100", tel="+6633010100", mail="reservations@novotelrayong.com"),
    dict(id="h4", name="Time Sabai 134", city="Bangkok", dates="2 → 3 janvier", nights="1 nuit", stage="s4",
         addr="134/6 ban Phan Thom Road, ban Phan Thom, Phra Nakhon District, Bangkok Old Town, Bangkok",
         q="Time Sabai 134, 134/6 Ban Phan Thom Road, Phra Nakhon, Bangkok",
         phone="+66 98 481 8737", tel="+66984818737", mail="timesabai.home@gmail.com"),
]
HOTEL = {h["id"]: h for h in HOTELS}

# ───────────────────────── jours ─────────────────────────
# S = une étape de la frise : x (texte), t (pastille horaire), p (liens Maps), sub (lignes en dessous), kind
# L = une ligne en dessous : x, p, b (puce), head (intitulé de liste)
# P = lien Maps : (libellé court, recherche)


def S(x, t=None, p=None, sub=None, kind=None):
    return dict(x=x, t=t, p=p or [], sub=sub or [], kind=kind)


def L(x, p=None, b=False, head=False):
    return dict(x=x, p=p or [], b=b, head=head)


def P(label, q):
    return (label, q)


BKK_AIR = P("Aéroport BKK", "Suvarnabhumi Airport Bangkok")
CHOUSE = P("C’HOUSE", HOTEL["h1"]["q"])
SUKH_AIR = P("Aéroport de Sukhothaï", "Sukhothai Airport")
NOVOTEL = P("Novotel Rim Pae", HOTEL["h3"]["q"])
THAITHAI = P("Thai Thai Resort", HOTEL["h2"]["q"])
TIMESABAI = P("Time Sabai 134", HOTEL["h4"]["q"])
KOHSAMET = P("Koh Samet", "Ko Samet Rayong")
# points de rendez-vous des activités réservées (adresses données par Anne le 21 novembre 2026)
RDV_BATEAU = P("Rendez-vous du bateau", "13.724617765054857,100.465503087047")
SAMYAN = P("Samyan Mitrtown", "KFC Samyan Mitrtown, 974 Phaya Thai Rd, Bangkok")
RDV_TUKTUK = P("Rendez-vous du tuk-tuk", "315-319 Rama IV Road, Pathum Wan, Bangkok 10330")
RDV_CUISINE = P("Rendez-vous du cours", "13.7356647,100.5554998")

# (id, stage, ville affichée, hôtel de la nuit, étapes, page du PDF pour les fun facts, pages spéciales)
DAYS = [
    dict(id="2026-12-18", stage="vol", city="Paris → Bangkok", night=None, page=6, steps=[
        S("Départ Anne et Arthur CDG à 16h05"),
        S("11h10 de vol", kind="flight"),
    ]),
    dict(id="2026-12-19", stage="s1", city="Bangkok", night="h1", page=6, steps=[
        S("Arrivée à 9h15 à BKK", p=[BKK_AIR]),
        S("Aller prendre les chambres à C’HOUSE", p=[CHOUSE]),
        S("Balade et déjeuner à Talat Noi", p=[P("Talat Noi", "Talat Noi Bangkok")]),
        S("Aller chercher les Daflo à l’aéroport", p=[BKK_AIR]),
        S("Briefing de la cheffe du tour et dîner"),
    ]),
    dict(id="2026-12-20", stage="s1", city="Bangkok", night="h1", page=7, steps=[
        S("Tour bateau longtail", t="9h", sub=[
            L("Big Buddha (Wat Paknam)", p=[P("Wat Paknam", "Wat Paknam Bhasicharoen Bangkok")]),
            L("Artist House (Baan Silapin)", p=[P("Baan Silapin", "Baan Silapin Artist House Bangkok")]),
            L("Rendez-vous : 46 Phet Kasem 19/1 Alley (Phasi Charoen)", p=[RDV_BATEAU]),
        ]),
        S("Balade dans le quartier d’Artist House (et éventuellement atelier)"),
        S("Déjeuner"),
        S("Visite de Jim Thompson House", p=[P("Jim Thompson House", "Jim Thompson House Bangkok")]),
        S("Depuis Jim Thompson : bateau sur les klongs jusqu’au Wat Saket"),
        S("Coucher de soleil en haut du Wat Saket", p=[P("Wat Saket", "Wat Saket Golden Mount Bangkok")]),
    ]),
    dict(id="2026-12-21", stage="s1", city="Bangkok", night="h1", page=8, steps=[
        S("Départ pour une journée à Ayutthaya", t="8h00", sub=[
            L("Prise en charge à C’HOUSE, 2 heures de trajet", p=[CHOUSE]),
        ], p=[P("Ayutthaya", "Ayutthaya Historical Park")]),
        S("Wat Maha – visite guidée (45 mn)", p=[P("Wat Mahathat", "Wat Mahathat Ayutthaya")]),
        S("Wat Yai Chai Mongkhon – visite guidée (45 mn)", p=[P("Wat Yai Chai Mongkhon", "Wat Yai Chai Mongkhon Ayutthaya")]),
        S("Phra Nakhon Si Ayutthaya (1 h de pause)"),
        S("Phra Nakhon Si Ayutthaya (croisière de 45 mn)"),
        S("Wat Chaiwatthanaram (visite guidée)", p=[P("Wat Chaiwatthanaram", "Wat Chaiwatthanaram Ayutthaya")]),
        S("Retour à l’auberge en fin d’après-midi", sub=[
            L("Le minibus vous dépose au KFC de Samyan Mitrtown, à Bangkok", p=[SAMYAN]),
        ], p=[CHOUSE]),
    ]),
    dict(id="2026-12-22", stage="s1", city="Bangkok", night="h1", page=9, steps=[
        S("Floating Market + marché du train", t="6h30", sub=[
            L("Prise en charge à C’HOUSE", p=[CHOUSE]),
            L("1h30 de voiture puis 1h de train"),
        ]),
        S("Marché ferroviaire de Maeklong", p=[P("Marché de Maeklong", "Maeklong Railway Market")]),
        S("20 minutes de minibus jusqu’au marché flottant"),
        S("Marché flottant de Damnoen Saduak", sub=[L("Déjeuner")], p=[P("Damnoen Saduak", "Damnoen Saduak Floating Market")]),
        S("Retour (MBK center)", sub=[
            L("Le minibus vous dépose au KFC de Samyan Mitrtown (974 Phaya Thai Rd)", p=[SAMYAN]),
        ], p=[P("MBK Center", "MBK Center Bangkok")]),
        S("Balade à Chinatown", p=[P("Yaowarat", "Yaowarat Road Chinatown Bangkok")]),
        S("Match de boxe thaï au stade Rajadamnern", t="19h", p=[P("Rajadamnern", "Rajadamnern Boxing Stadium Bangkok")]),
    ]),
    dict(id="2026-12-23", stage="s1", city="Bangkok", night="h1", page=10, steps=[
        S("Départ pour la visite du Grand Palais + Wat Phra Kaew", t="8h00", sub=[
            L("Arriver dès l’ouverture à 8h30 (sinon trop de monde)"),
        ], p=[P("Grand Palais", "Grand Palace Bangkok")]),
        S("Wat Pho + Massage", t="11h30", sub=[
            L("École du Wat Pho (si possible)", p=[P("École de massage", "Wat Pho Thai Traditional Medical and Massage School Bangkok")]),
        ], p=[P("Wat Pho", "Wat Pho Bangkok")]),
        S("Déjeuner"),
        S("Songwat Road + Talat Noi", sub=[
            L("(10 min de Grab depuis Wat Pho)"),
            L("Boutiques, street art…"),
        ], p=[P("Songwat Road", "Songwat Road Bangkok"), P("Talat Noi", "Talat Noi Bangkok")]),
        S("Tour street food en tuk-tuk", t="19h", sub=[
            L("Rendez-vous : 315-319 Rama IV Road (Pathum Wan)", p=[RDV_TUKTUK]),
        ]),
        S("Retour à l’auberge", t="23h", p=[CHOUSE]),
    ]),
    dict(id="2026-12-24", stage="s1", city="Bangkok", night="h1", page=11, steps=[
        S("Chatuchak Market", t="9h00", sub=[
            L("(BTS Mo Chit / MRT Chatuchak Park)"),
            L("Arriver tôt : c’est bondé et il fait trop chaud après 11h"),
            L("Possible de faire autre chose selon les envies"),
        ], p=[P("Chatuchak", "Chatuchak Weekend Market Bangkok")]),
        S("Déjeuner"),
        S("Massage", sub=[L("(ou autre, selon les envies)")]),
        S("Ferry > Wat Arun (ça ferme à 17h30)", t="Fin de journée",
          p=[P("Ferry (Tha Tien)", "Tha Tien Pier Bangkok"), P("Wat Arun", "Wat Arun Bangkok")]),
        S("Dîner face au Wat Arun", t="19h30", sub=[
            L("The Deck by Arun Residence ?", p=[P("The Deck", "The Deck by Arun Residence Bangkok")]),
        ]),
    ]),
    dict(id="2026-12-25", stage="s1", city="Bangkok", night="h1", page=12, steps=[
        S("Grasse matinée"),
        S("Parc Lumpini et éventuellement brunch", p=[P("Parc Lumpini", "Lumpini Park Bangkok")]),
        S("Visite de marché et cours de cuisine", t="13h", sub=[
            L("Rendez-vous : 147/4 Sukhumvit 4 (Khlong Toei)", p=[RDV_CUISINE]),
        ]),
        S("Dusit Central Park – coucher de soleil sur le rooftop", t="Fin de journée", p=[P("Dusit Central Park", "Dusit Central Park Bangkok")]),
        S("Dîner de Noël chez Jim Thompson et cocktail chez G.O.D", p=[
            P("Jim Thompson", "Jim Thompson, A Thai Restaurant Bangkok"),
            P("G.O.D", "G.O.D Genius On Drugs bar, 25/27 Soi Rammaitree, Pom Prap, Bangkok 10100"),
        ]),
    ]),
    dict(id="2026-12-26", stage="s2", city="Bangkok → Sukhothaï", night="h2", page=13, quiz=True, steps=[
        S("Grasse matinée", sub=[
            L("Faire les valises, acheter des souvenirs, …"),
            L("Départ pour l’aéroport à 12h30"),
        ]),
        S("Vol Bangkok – Sukhothaï", t="15h30–16h50", sub=[
            L("Transfert hôtel depuis l’aéroport : 1h"),
        ], p=[SUKH_AIR]),
        S("Piscine à l’hôtel", t="Fin de journée", p=[THAITHAI]),
    ]),
    dict(id="2026-12-27", stage="s2", city="Sukhothaï", night="h2", page=14, steps=[
        S("Petit déjeuner hôtel"),
        S("Visite du parc à vélo", sub=[
            L("Zone Centrale :", head=True),
            L("Wat Mahathat (le plus grand)", b=True, p=[P("Wat Mahathat", "Wat Mahathat Sukhothai Historical Park")]),
            L("Wat Sa Si (île aux lotus)", b=True, p=[P("Wat Sa Si", "Wat Sa Si Sukhothai")]),
            L("Wat Trapang Thong", b=True, p=[P("Wat Trapang Thong", "Wat Trapang Thong Sukhothai")]),
            L("Musée Ramkhamhaeng", b=True, p=[P("Musée", "Ramkhamhaeng National Museum Sukhothai")]),
        ]),
        S("Déjeuner en ville ou sur place"),
        S("Zone Nord du parc", sub=[
            L("Wat Si Chum (Bouddha géant 15 m)", b=True, p=[P("Wat Si Chum", "Wat Si Chum Sukhothai")]),
            L("Wat Phra Phai Luang (khmère, moins touristique)", b=True, p=[P("Wat Phra Phai Luang", "Wat Phra Phai Luang Sukhothai")]),
        ]),
        S("Retour à la zone centrale et coucher de soleil sur Wat Sa Si", t="Fin d’aprem", p=[P("Wat Sa Si", "Wat Sa Si Sukhothai")]),
        S("Dîner + piscine", sub=[L("Marché nocturne")]),
    ]),
    dict(id="2026-12-28", stage="s2", city="Sukhothaï", night="h2", page=15, lexique=True, steps=[
        S("Petit déjeuner hôtel"),
        S("Soit matinée tranquille à l’hôtel, soit balade en vélo dans le parc"),
        S("Wat Saphan Hin", t="14h", sub=[
            L("(Bouddha debout au sommet, vue panoramique sur toute la plaine historique)"),
        ], p=[P("Wat Saphan Hin", "Wat Saphan Hin Sukhothai")]),
        S("Piscine à l’hôtel", t="Fin de journée", p=[THAITHAI]),
    ]),
    dict(id="2026-12-29", stage="s3", city="Sukhothaï → Ban Phe", night="h3", page=16, steps=[
        S("Petit déjeuner hôtel"),
        S("Dernière journée à Sukhothaï : programme à déterminer ensemble"),
        S("Départ de l’hôtel vers 15h"),
        S("Avion de Sukhothaï à Bangkok", sub=[L("17h30 > 18h50")], p=[SUKH_AIR]),
        S("Trajet Bangkok > Rayong", sub=[L("Arrivée vers 22h à Rayong")], p=[NOVOTEL]),
    ], paper="Sudoku thaï : dans le carnet papier"),
    dict(id="2026-12-30", stage="s3", city="Ban Phe", night="h3", page=17, steps=None, free=True),
    dict(id="2026-12-31", stage="s3", city="Ban Phe", night="h3", page=17, steps=None, free=True),
    dict(id="2027-01-01", stage="s3", city="Ban Phe", night="h3", page=17, steps=None, free=True),
    dict(id="2027-01-02", stage="s4", city="Ban Phe → Bangkok", night="h4", page=18, steps=[
        S("Dernière matinée piscine :("),
        S("Retour à Bangkok"),
        S("Dernière nuit à Bangkok", p=[TIMESABAI]),
    ]),
    dict(id="2027-01-03", stage="s4", city="Bangkok", night=None, page=18, steps=[], end=True),
]

# Journées libres à Ban Phe (carnet p. 17 : « du 29 décembre au premier janvier »)
FREE_STEPS = [
    S("Piscine"),
    S("Plage"),
    S("Massage"),
    S("Cocktails", sub=[L("Option : passer une journée sur l’île de Koh Samet", p=[KOHSAMET])]),
]

# ───────────────────────── quiz du 26 décembre (carnet p. 24) ─────────────────────────
QUIZ = dict(
    title="QUIZZZZ", sub="pour gagner un cocktail à la piscine",
    qs=[
        ("Le Bouddha d’Émeraude du Wat Phra Kaew, l’objet le plus sacré de Thaïlande, mesure :", ["20 cm", "66 cm", "1,20 m"], 1),
        ("Combien d’années Ayutthaya a-t-elle été capitale du Siam ?", ["150 ans", "250 ans", "417 ans"], 2),
        ("Combien de fois par jour un train traverse-t-il les étals du marché de Maeklong ?", ["2 fois", "8 fois", "15 fois"], 1),
        ("Jim Thompson, qui relança l’industrie de la soie thaïe, disparut mystérieusement en :", ["Birmanie", "Malaisie", "Indonésie"], 1),
        ("Le marché de Chatuchak compte environ combien de stands ?", ["3 000", "8 000", "15 000"], 2),
        ("Les varans du parc Lumpini peuvent atteindre :", ["80 cm", "2 mètres", "4 mètres"], 1),
    ],
)

# ───────────────────────── lexique des temples (carnet p. 28) ─────────────────────────
LEXIQUE_TEMPLES = [
    ("Wat", "วัด", "temple bouddhiste"),
    ("Chedi", "เจดีย์", "tour conique qui abrite des reliques"),
    ("Viharn", "วิหาร", "salle d’assemblée des fidèles"),
    ("Mondop", "มณฑป", "pavillon carré à toit en pointe"),
    ("Phra", "พระ", "préfixe sacré, désigne aussi un moine"),
    ("Ubosot", "อุโบสถ", "salle d’ordination des moines, lieu le plus sacré du temple"),
    ("Prang", "ปรางค์", "tour à flèche d’influence khmère, plus élancée que le chedi"),
    ("Bot", "โบสถ์", "autre nom de l’ubosot, salle des cérémonies officielles"),
    ("Sala", "ศาลา", "pavillon ouvert servant d’abri ou de lieu de repos"),
    ("Kuti", "กุฏิ", "cellules d’habitation des moines dans l’enceinte du temple"),
    ("Naga", "นาค", "serpent mythologique à plusieurs têtes, gardien des temples"),
]


def facts_for(day):
    """Fun facts d'un jour : liste de cartes, chacune = liste de paragraphes (« **gras** » possible)."""
    path = os.path.join(ROOT, "data_facts.json")
    data = json.load(open(path, encoding="utf-8"))
    page = str(day["page"])
    if day["id"] in ("2026-12-18", "2026-12-19"):
        return []
    if day["id"] in ("2026-12-26", "2026-12-29", "2026-12-30", "2026-12-31", "2027-01-01", "2027-01-02", "2027-01-03"):
        return []
    cards = data.get(page, [])
    if page == "15":
        cards = cards[:2]          # la 3e carte est le lexique des temples (mis en forme à part)
    return cards


# ───────────────────────── étape 2 : lexique, cartes taxi, convertisseur, Good to know ─────────────────────────
# Lexique et bulles « Good to know » : copie fidèle des pages 5 du carnet (extraites par _dev/extract_step2.py).
STEP2 = json.load(open(os.path.join(ROOT, "data_step2.json"), encoding="utf-8"))

# Taux du convertisseur : réglable à la main sur chaque téléphone ; valeur de départ = taux moyen du marché relevé le 20 novembre 2026
# (1 € = 37,24 ฿ sur currencyconvert.online, 37,21 ฿ sur OFX le 18 novembre) : un taux de bureau de change ou de carte sera un peu moins bon.
RATE = dict(value=37.2, label="20 novembre 2026")

# Cartes taxi : noms et adresses en thaï relevés sur des pages thaïes (Accor pour le Novotel, hotels.com pour le Thai Thai,
# page de réservation du C'HOUSE pour « Trok Salakhin », hotels.com pour la rue du Time Sabai). Quand le nom thaï n'est pas
# connu (C'HOUSE, Time Sabai 134), la carte montre le nom en lettres latines, comme sur l'enseigne.
TAXI = [
    dict(id="h1", hotel="h1", name_th=None, name_lat="C’HOUSE Bangkok",
         addr_th="114 ตรอกสลักหิน แขวงรองเมือง เขตปทุมวัน กรุงเทพมหานคร 10330",
         near_th="ใกล้สถานีหัวลำโพง", near_fr="Près de la gare de Hua Lamphong"),
    dict(id="h2", hotel="h2", name_th="ไทย ไทย สุโขทัย รีสอร์ท", name_lat="Thai Thai Sukhothai Resort",
         addr_th="95/8 หมู่ 3 ถนนนาโพธิ์-คีรีมาศ (อุทยานประวัติศาสตร์) ต.เมืองเก่า อ.เมือง จ.สุโขทัย 64210",
         near_th=None, near_fr="Près du parc historique de Sukhothaï"),
    dict(id="h3", hotel="h3", name_th="โนโวเทล ระยอง ริมเพ รีสอร์ท", name_lat="Novotel Rayong Rim Pae Resort",
         addr_th="4/5 หมู่ 3 ถนนเพ-แกลง-กล่ำ ต.ชากพง อ.แกลง จ.ระยอง 21190",
         near_th=None, near_fr="En bord de mer, à environ 12 km de Ban Phe"),
    dict(id="h4", hotel="h4", name_th=None, name_lat="Time Sabai 134",
         addr_th="134/6 ถนนบ้านพานถม แขวงบ้านพานถม เขตพระนคร กรุงเทพมหานคร 10200",
         near_th=None, near_fr=None),
]
TAXI_PHRASES = [  # (thaï, transcription, français)
    ("ช่วยไปส่งที่นี่หน่อยครับ/ค่ะ", "chuai pai song thi ni noi khrap/kha", "Emmenez-moi ici, s’il vous plaît."),
    ("ขอเปิดมิเตอร์ด้วยครับ/ค่ะ", "kho poet mi-toe duai khrap/kha", "Mettez le compteur, s’il vous plaît."),
    ("ถ้าหาไม่เจอ ช่วยโทรหาโรงแรมให้หน่อยครับ/ค่ะ", "tha ha mai jer, chuai tho ha rong-raem hai noi khrap/kha",
     "Si vous ne trouvez pas, appelez l’hôtel, s’il vous plaît."),
]
