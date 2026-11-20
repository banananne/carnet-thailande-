# Sources du carnet en ligne (branche `sources`)

Cette branche ne sert qu'à garder une copie des fichiers qui fabriquent le site. Le site publié
est sur la branche `main` (GitHub Pages) : ne rien publier ici.

Dernière mise à jour : 20 novembre 2026, 22 h 30. Contenu : étape 1 (en ligne depuis 20 h 51), étape 2 (lexique,
cartes taxi, convertisseur, Good to know) et étape 3 (jeux : quiz, test du doudou, blind test, mots mêlés,
horoscope, doudous, passeport de tampons), publiées ensemble à 22 h 24 (branche `main`, commit 34db76e,
version de construction 20261120-222245). Ces sources correspondent à ce qui est publié.

## Reconstruire le site
1. Remettre `site_en_ligne/` dans `/home/claude/site_en_ligne/` et les autocollants de `stickers/`
   dans `/home/claude/lexique/out/stickers_playlist/` (chemins écrits en dur dans `build_site.py` :
   `ROOT`, `STK`).
2. Polices : `cd /home/claude/site_en_ligne/_dev && npm install` (lit `package.json` : Barlow,
   Barlow Condensed, Libre Baskerville, Noto Sans Thai, via @fontsource). Les .woff2 déjà publiés
   sont aussi dans le dossier `fonts/` de la branche `main`.
3. Plan du métro : fabriqué à partir de `/mnt/user-data/uploads/Journal_de_bord.pdf` (page 4) par
   `build_metro.py`. Le résultat est déjà publié dans `assets/metro.svg` sur `main` : on peut le copier
   dans `web/assets/` si le PDF n'est plus disponible.
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
  des doudous, mots des tampons, `PLAYLIST_URL` à remplir quand le lien arrive).
  `data_test_doudou.json`, `data_horoscope.json`, `data_motsmeles.json` : extraits des pages 19 à 23 du PDF
  (`_dev/extract_step3.py`, `_dev/extract_horoscope.py`, `_dev/ocr_grid.py` et `_dev/solve_grid.py` pour la grille).
- `build_app.py` : fabrique les pages HTML (accueil, jours, hôtels, utile, métro, lexique, cartes taxi,
  convertisseur, Good to know, fenêtre « montrer en grand »).
- `build_games.py` : pages des jeux (hub, quiz, test du doudou, doudous, blind test, mots mêlés, horoscope,
  passeport, tampons en SVG), importé par `build_app.py`.
- `app.css`, `app.js` : style et comportement (navigation, photo du jour, copie, plan du métro, voix thaïe,
  lexique, cartes taxi, convertisseur).
- `games.js`, `games.css` : comportement et style des jeux. `games.js` est collé dans `app.js` au moment du
  build (repère `/*@GAMES@*/`) et `games.css` est ajouté à `app.css`.
- `img/` : les quatre doudous détourés (WebP), extraits de la page 23 du PDF.
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
(lance son propre serveur sur le port 8766) ; `t18.py` et `t18b.py` mots mêlés avec de vrais événements tactiles.
`test_photo_0..4.jpg` : petites photos pour tester la photo du jour. Les chemins de captures (variable `OUT`) sont à adapter.
