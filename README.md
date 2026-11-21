# Sources du carnet en ligne (branche `sources`)

Cette branche ne sert qu'à garder une copie des fichiers qui fabriquent le site. Le site publié
est sur la branche `main` (GitHub Pages) : ne rien publier ici.

Dernière mise à jour : 21 novembre 2026, 20 h 10. Contenu : étape 1 (en ligne depuis 20 h 51), étape 2 (lexique,
cartes taxi, convertisseur, Good to know) et étape 3 (jeux : quiz, test de personnalité, blind test, mots mêlés,
horoscope, mascottes, passeport de tampons), publiées ensemble à 22 h 24 (commit 34db76e), puis vague 1 des
améliorations (accueil allégé à quatre rubriques, « Qui es-tu ? » qui se replie, « doudous » devenus « mascottes »,
« test du doudou » devenu « test de personnalité ») publiée à 22 h 59 (branche `main`, commit fd09c91, version de
construction 20261120-225758), puis vague 2 (nouveaux tampons du passeport : un cadre, une encre et un dessin par
jour, 6 tampons spéciaux) validée par Anne le 20 novembre à 23 h 32 et publiée à 23 h 33 (branche `main`, commit
1157c6d, version de construction 20261120-232939), puis nouvelle carte complète du métro (BTS, MRT, Airport Link, SRT) publiée
le 21 novembre à 0 h 02 (branche `main`, commit b6f517f, version de construction 20261120-235823).
Puis le cadenas du test de personnalité (ouvert le 29 décembre, ou avec un mot secret) publié le 21 novembre à 0 h 20
(branche `main`, commit 6b85e54, version de construction 20261121-000925).
Puis l'étape 4 : calendrier d'ouverture des jeux, cinq jeux exclusifs au site (défi photo et rôles du jour, mot du jour, bingo,
carnet gourmand, prix du voyage), horoscope du jour sur l'accueil, mascottes qui voyagent (Aftonsparv et Moomoo) ou écrivent
de loin (Boop et Minou), passeport à 28 tampons, traducteur français ⇄ thaï dans Utile, publiés le 21 novembre à 3 h 34
(branche `main`, commit f470d1a, version de construction 20261121-032325).
Puis un correctif publié le 21 novembre à 3 h 57 (branche `main`, commit 037f970, version de construction 20261121-034731) : le traducteur
n'affiche plus la « prononciation » de Google (translittération savante à diacritiques, illisible : on écoute avec « Écouter »),
la transcription « suay » est écrite pareil partout (recueil, mot du jour, carnet imprimé), et `build_app.nbsp_pass` pose
l'espace insécable avant : ; ? ! » et après « dans tout le texte de la page.
Puis les enveloppes secrètes (moteur complet et page d'essai `#/essai` avec de FAUSSES données, aucune vraie enveloppe) publiées le
21 novembre à 11 h 50 (branche `main`, commit ce1ef3e, version de construction 20261121-114529).
Puis une mise à jour des enveloppes (chaque carte : « Le jeu » avec le contexte, « Ta mission », gros encadré « Fin de la mission » ;
code retapé à chaque ouverture, plus aucune clé gardée sur le téléphone ; rôle d'essai « ventilateur ») publiée le 21 novembre à 13 h 10
(branche `main`, commit 7643e2f, version de construction 20261121-130013). Ces sources correspondent à ce qui est publié.

## Reconstruire le site
1. Remettre `site_en_ligne/` dans `/home/claude/site_en_ligne/` et les autocollants de `stickers/`
   dans `/home/claude/lexique/out/stickers_playlist/` (chemins écrits en dur dans `build_site.py` :
   `ROOT`, `STK`).
2. Polices : `cd /home/claude/site_en_ligne/_dev && npm install` (lit `package.json` : Barlow,
   Barlow Condensed, Libre Baskerville, Noto Sans Thai, via @fontsource). Les .woff2 déjà publiés
   sont aussi dans le dossier `fonts/` de la branche `main`.
3. Plan du métro : fabriqué à partir de `site_en_ligne/_dev/bts_metro_map.pdf` (carte complète du réseau envoyée par Anne
   le 20 novembre 2026 à 23 h 47) par `build_metro.py` (pymupdf/MuPDF : bandeau de titre retiré, textes thaï convertis
   en tracés, SVG d'environ 1,9 Mo). Le résultat est déjà publié dans `assets/metro.svg` sur `main` : on peut le copier
   dans `web/assets/` si le PDF ou pymupdf ne sont plus disponibles.
4. `cd /home/claude/site_en_ligne && python3 -I build.py` fabrique le dossier `web/` (index.html,
   test.html, sw.js, manifest, polices, icônes, plan du métro).
5. Publier : copier le contenu de `web/` à la racine de la branche `main` (tout supprimer sauf `.git`
   et `README.md`), commit, push. GitHub Pages met environ 30 s.

## Fichiers de `site_en_ligne/`
- `site_data.py` : contenu (étapes, hôtels, jours, quiz, cartes taxi, taux) repris du PDF du
  20 novembre 2026.
- `data_facts.json` : fun facts par jour. `data_step2.json` : lexique et bulles « Good to know »
  (extraits des pages du carnet par `_dev/extract_step2.py`).
- `data_games.py` : textes et réglages des jeux qui ne viennent pas du PDF (joueurs du blind test, phrases
  des mascottes (nommées `DOUDOUS` dans le code), mots des tampons, `PLAYLIST_URL` à remplir quand le lien arrive).
  `data_test_doudou.json`, `data_horoscope.json`, `data_motsmeles.json` : extraits des pages 19 à 23 du PDF
  (`_dev/extract_step3.py`, `_dev/extract_horoscope.py`, `_dev/ocr_grid.py` et `_dev/solve_grid.py` pour la grille).
- Cadenas du test de personnalité : `data_games.py` (`TEST_OPEN` = date d'ouverture, `TEST_OPEN_TXT`, `TEST_WORDS` = mots secrets ;
  seules leurs empreintes FNV-1a vont dans le site, voir `build_games.fnv`), `games.js` (module `Lock`, classe `tlock` sur `<html>`),
  `games.css` (fin du fichier). Clé de mémoire : `carnet.open` = « 1 » quand le mot secret a été tapé.
- Étape 4 : `data_days.py` (dates d'ouverture `GATES`, rôles du jour, 17 défis photo, 17 mots du jour, bingo, 24 plats, 8 prix ;
  seuls Aftonsparv et Moomoo voyagent), `data_horo_days.py` (horoscope du jour : 3 signes × 17 jours ; `SIGN_OF` = signe de
  chaque prénom), `build_days.py` (pages `v-defi`, `v-mot`, `v-bingo`, `v-gourmand`, `v-prix`, encadré `#hsd` de l'accueil,
  enveloppe des vues fermées `gate`), `games2.js` (comportement de ces jeux ; collé dans `games.js` au repère `/*@GAMES2@*/`),
  `days.css` (ajouté à `app.css`). Clés de mémoire : `carnet.defi`, `carnet.mj`, `carnet.bingo`, `carnet.food`, `carnet.prix`.
- Enveloppes secrètes (missions en cachette sur les téléphones : la cacahuète, le killer sans victime, un rôle à jouer) :
  `data_env.py` (fenêtres de dates PUBLIQUES `WINDOWS` : apparition, révélation sur l'appli à l'heure du dîner, effacement, en heure
  locale du téléphone ; réglages `SIM_ON` et `ITERATIONS` ; textes COMMUNS à tous les joueurs d'une vague, `INTRO` (« Le jeu » : dates,
  principe, règles, « même Anne joue à l'aveugle ») et `FOOT`, repris tels quels par le vrai tirage ; données de SIMULATION inventées :
  faux prénom Mangue, faux code, faux mots ; `sim_payloads()` documente la forme d'une enveloppe), `build_env.py` (chiffrement à la fabrication : PBKDF2-SHA256
  150 000 tours + AES-GCM, une clé par personne et un vecteur par personne et par vague ; bandeau de l'accueil, fenêtre `#env`,
  page d'essai `view_essai()`), `env.js` (collé dans `games.js` au repère `/*@ENV@*/` ; WebCrypto, fenêtres de dates, serment (une seule fois par jeu),
  carte qui se cache après une minute, encadré « Fin de la mission » tiré de `WINDOWS`, révélation, compteur de mots du killer ;
  le code se retape à chaque ouverture : ni code ni clé ne sont gardés, les anciennes clés sont effacées au chargement), `env.css` (ajouté à `app.css`). Clés de mémoire `carnet.env.*`
  (vrai jeu : seulement « vu », score) et `carnet.sim.*` (essai). **Les vraies enveloppes ne sont ni dans ces sources ni en clair sur `main`** : elles viennent
  d'un fichier privé `/home/claude/prive/env_public.json` (ou de la variable `ENV_REAL_JSON`), fabriqué par un script privé (tirage au
  hasard, codes, vrais textes) et gardé hors de `site_en_ligne/` et hors de ce dépôt. Sans ce fichier, l'accueil n'affiche aucune enveloppe ;
  la page `#/essai` n'existe que si `SIM_ON = True` (à passer à `False` avant de donner le lien aux autres). Le mode essai
  (`carnet.open` = « 1 ») n'ouvre aucune enveloppe.
- Traducteur (Utile) : `data_trad.py` (86 phrases toutes prêtes, services, longueurs), `build_trad.py` (page `v-trad`),
  `trans.js` (collé dans `games.js` au repère `/*@TRANS@*/` ; Google Traduction puis MyMemory pour une phrase libre, seul
  endroit du site qui envoie un texte à l'extérieur), `trad.css` (ajouté à `app.css`). Clés : `carnet.trad`, `carnet.trad.dir`.
- `build_app.py` : fabrique les pages HTML (accueil, jours, hôtels, utile, métro, lexique, cartes taxi,
  convertisseur, Good to know, fenêtre « montrer en grand »). `nbsp_pass` est le dernier passage sur la page entière :
  espace insécable avant : ; ? ! » et après « dans le texte (jamais dans les balises, attributs, scripts, styles ni dessins) ;
  il est appelé par `build_site.build_web`.
- `build_games.py` : pages des jeux (hub, quiz, test de personnalité, mascottes, blind test, mots mêlés, horoscope,
  passeport, tampons en SVG), importé par `build_app.py`. Le mot « doudou » reste dans les noms internes (clé de
  mémoire `carnet.doudou`, tampon `doudou`, fichiers `img/doudou_*.webp`, ids `v-doudous`) pour que ceux qui ont
  déjà joué gardent leurs données ; adresses `#/personnalite` et `#/mascottes` (les anciennes `#/test-doudou` et
  `#/doudous` marchent encore).
- `app.css`, `app.js` : style et comportement (navigation, photo du jour, copie, plan du métro, voix thaïe,
  lexique, cartes taxi, convertisseur).
- `stamps.py` (vague 2) : dessins (pictogrammes en traits), cadres (ticket, rond, ovale, arche, hexagone,
  rectangle, timbre, dentelé, cachet postal, bandeau, octogone) et encres des 28 tampons (17 jours + 11 spéciaux) ; `DAY_SPEC` et `BONUS_SPEC` donnent
  cadre, couleur et dessin de chaque jour et de chaque tampon spécial ; `stamp_svg()` dessine un tampon.
- `games.js`, `games.css` : comportement et style des jeux. `games.js` est collé dans `app.js` au moment du
  build (repère `/*@GAMES@*/`) et `games.css` est ajouté à `app.css`.
- `img/` : les quatre mascottes détourées (WebP), extraits de la page 23 du PDF.
- `build_site.py` : assemble `web/`, service worker, manifest, `test.html` (depuis `template.html`).
- `build.py` : point d'entrée (`python3 -I build.py`). `build_metro.py` : plan du métro en SVG léger.
  `make_qr.py` : QR code de l'adresse du site (PDF et SVG vectoriels).
- `_dev/` : `thai_map.json` (carte de l'accueil, fabriquée par `thai_map.py`), `package.json`
  (polices), extracteurs `extract_days.py`, `facts_clean.py`, `blocks.py`, `extract_step2.py`.

## Tests (`tests/`)
Scripts Playwright (Python, Chromium) et Node, écrits pour un serveur local : `serve.py` sert `web/`
sous `/carnet-thailande-/` comme GitHub Pages (`python3 serve.py 8765`). `t7.py` : étape 2 complète ;
`t8.py` : débordements de 320 à 768 px ; `t10.py` : mode hors réseau (serveur coupé) ;
`thainum_test.js` : les nombres en thaï. Étape 3 : `t11.py` parcours et captures ; `t12.py` rendu des tampons ;
`t13.py` quiz, test du doudou, blind test ; `t14.py` mots mêlés (souris) ; `t15.py` tampons, photo, horoscope,
mot du doudou ; `t16.py` débordements de 320 à 768 px sur les vues des jeux ; `t17.py` hors réseau serveur coupé
(lance son propre serveur sur le port 8766) ; `t18.py` et `t18b.py` mots mêlés avec de vrais événements tactiles
(le test « le doigt sur la liste fait défiler la page » de t18 peut échouer à 390 px quand la page est déjà au
bas : c'est un artéfact, t18b le vérifie correctement) ; `t19.py` captures d'aperçu. Vague 1 : `t20.py` accueil
(première visite, choix du prénom, repli automatique, réouverture, clavier, rechargement, prénom inconnu, 5 largeurs,
script d'en-tête sans clignotement) et vocabulaire (mascottes, test de personnalité, anciennes adresses).
Vague 2 (tampons) : `t21.py` planches (passeport plein, à moitié rempli, vide ; un fichier par tampon),
`t22.py` tampon sur les pages de jour, `t23_phone.py` captures du passeport sur téléphone, `t24_planche.py` planche
légendée montrée à Anne (à partir des fichiers de `t21.py`), `t26.py` texte courbé sur les pages de jour,
`t27.py` variété des cadres/encres/dessins, tampons non rognés (contrôle des pixels du bord), cases vides, clics,
identifiants uniques, remise à zéro ; `t27neg.py` contrôle négatif du test de rognage.
Étape 4 : `t30.py` calendrier à dates simulées (horloge de Playwright), mot secret, horoscope du jour, rôles, défi, mot, bingo,
gourmand, prix, 28 tampons, mascottes, mise en page ; `t31.py` traducteur (réseau SIMULÉ : le serveur local ne joint aucun vrai
service) ; `t32.py` espaces insécables du texte de la page (balises, scripts et styles intacts) et transcription « suay » ;
Enveloppes : `t33.py` page d'essai (3 jeux, 4 heures simulées, contexte et encadré de fin, code retapé à chaque ouverture, serment une seule fois, 1 minute d'inactivité, compteur du killer, hors réseau) ;
`t34.py` vrai chemin avec un FAUX jeu (4 prénoms, codes `test-…`) fabriqué par `mkfix.py` et construit à part
(`CARNET_WEB=… ENV_REAL_JSON=… python3 -I build.py`), servi par `serve_any.py PORT DOSSIER` : heures d'ouverture, de révélation et d'effacement,
un code par personne, deux prénoms sur un téléphone, mode essai sans effet ;
`run_srv.sh` lance le serveur local le temps d'une série (`./run_srv.sh t31 t30 …`, résumé dans `summary.log`) ; `run_all.sh`
enchaîne les séries. Les tests t12, t14, t15, t18, t22, t26, t27 et t29 posent `carnet.open` = « 1 » et comptent 28 tampons.
`test_photo_0..4.jpg` : petites photos pour tester la photo du jour. Les chemins de captures (variable `OUT`) sont à adapter.

Puis (21 novembre au soir, branche `main`, commit 5278674) : vraies enveloppes secrètes chiffrées en ligne (jamais de texte, de code ni de tirage dans ce dépôt),
quatre jeux dont « les questions de Boop » (28 décembre, identifiant w4), toutes les révélations à 20 h, serment à chaque ouverture,
révélation sans code quand la mission a été lue (mise de côté sur le téléphone), espace invité·e (cinquième pastille « Je suis invité·e » : tout le site
sauf enveloppes, horoscope du jour et rôles du jour), liens Maps des rendez-vous des activités réservées, bouton de la playlist, date du départ 18.12.2026.
Ces sources correspondent à ce qui est publié. Tests : t33 (164), t34 (90, faux jeu fabriqué par mkfix.py), t35 (53 : invité·e, Maps, playlist).
