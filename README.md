# Sources du carnet en ligne (branche `sources`)

Cette branche ne sert qu'à garder une copie des fichiers qui fabriquent le site. Le site publié
est sur la branche `main` (GitHub Pages) : ne rien publier ici.

Dernière mise à jour : 20 novembre 2026, 21 h 50. Contenu : étape 1 (en ligne) et étape 2 (lexique,
cartes taxi, convertisseur, Good to know), prête et testée en local mais pas encore publiée.

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
- `build_app.py` : fabrique les pages HTML (accueil, jours, hôtels, utile, métro, lexique, cartes taxi,
  convertisseur, Good to know, fenêtre « montrer en grand »).
- `app.css`, `app.js` : style et comportement (navigation, photo du jour, copie, plan du métro, voix thaïe,
  lexique, cartes taxi, convertisseur).
- `build_site.py` : assemble `web/`, service worker, manifest, `test.html` (depuis `template.html`).
- `build.py` : point d'entrée (`python3 -I build.py`). `build_metro.py` : plan du métro en SVG léger.
  `make_qr.py` : QR code de l'adresse du site (PDF et SVG vectoriels).
- `_dev/` : `thai_map.json` (carte de l'accueil, fabriquée par `thai_map.py`), `package.json`
  (polices), extracteurs `extract_days.py`, `facts_clean.py`, `blocks.py`, `extract_step2.py`.

## Tests (`tests/`)
Scripts Playwright (Python, Chromium) et Node, écrits pour un serveur local : `serve.py` sert `web/`
sous `/carnet-thailande-/` comme GitHub Pages (`python3 serve.py 8765`). `t7.py` : étape 2 complète ;
`t8.py` : débordements de 320 à 768 px ; `t10.py` : mode hors réseau (serveur coupé) ;
`thainum_test.js` : les nombres en thaï. Les chemins de captures (variable `OUT`) sont à adapter.
