# Sources du carnet en ligne (branche `sources`)

Cette branche ne sert qu'à garder une copie des fichiers qui fabriquent le site. Le site publié
est sur la branche `main` (GitHub Pages) : ne rien publier ici.

## Reconstruire le site
1. Remettre les fichiers de `site_en_ligne/` dans `/home/claude/site_en_ligne/` et les autocollants
   de `stickers/` dans `/home/claude/lexique/out/stickers_playlist/` (chemins écrits en dur dans
   `build_site.py` : `ROOT`, `STK`).
2. Le plan du métro est fabriqué à partir de `/mnt/user-data/uploads/Journal_de_bord.pdf` (page 4) par
   `build_metro.py`. Le résultat est déjà publié dans `assets/metro.svg` sur `main` : on peut le copier
   dans `web/assets/` si le PDF n'est plus disponible.
3. `python3 -I build.py` fabrique le dossier `web/` (index.html, test.html, sw.js, manifest, polices,
   icônes, plan du métro). Les polices et icônes sont reprises de `main` si besoin.
4. Publier : copier le contenu de `web/` à la racine de la branche `main`, commit, push.

## Fichiers
- `site_data.py` : contenu (étapes, hôtels, jours, quiz, lexique) repris du PDF du 20 novembre 2026.
- `build_app.py` : fabrique les pages HTML (accueil, jours, hôtels, utile, métro).
- `app.css`, `app.js` : style et comportement (navigation, photo du jour, copie, plan du métro).
- `build_site.py` : assemble `web/`, service worker, manifest, `test.html` (depuis `template.html`).
- `build_metro.py` : exporte le plan du métro de la page 4 du PDF en SVG léger.
- `make_qr.py` : QR code de l'adresse du site (PDF et SVG vectoriels).
