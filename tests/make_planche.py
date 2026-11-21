"""Planche légendée des 11 tampons spéciaux (les 5 derniers sont exclusifs au site), générée depuis stamps.py / build_games.py de la version finale."""
import sys
sys.path.insert(0, "/home/claude/site_en_ligne")
import data_games as G
import build_games as BG
from playwright.sync_api import sync_playwright

OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/planche/"
FONTS = "file:///home/claude/site_en_ligne/web/fonts/"


def face(fam, style, w, fn, extra=""):
    return "@font-face{font-family:'%s';font-style:%s;font-weight:%s;src:url('%s%s') format('woff2')%s}" % (fam, style, w, FONTS, fn, extra)


CSS_FONTS = (face("Barlow", "normal", 500, "barlow-latin-500-normal.woff2") + face("Barlow", "normal", 600, "barlow-latin-600-normal.woff2")
             + face("Barlow", "normal", 700, "barlow-latin-700-normal.woff2")
             + face("Barlow Condensed", "normal", 700, "barlow-condensed-latin-700-normal.woff2")
             + face("Barlow Condensed", "normal", 800, "barlow-condensed-latin-800-normal.woff2"))

CSS = CSS_FONTS + """
*{box-sizing:border-box}
body{margin:0;background:#FFFCF6;color:#1B2557;font:600 14px/1.3 Barlow,sans-serif;width:680px}
header{background:#A51C36;padding:20px 24px 14px}
header h1{margin:0;font:800 38px/1 'Barlow Condensed',sans-serif;letter-spacing:.02em;text-transform:uppercase;color:#F7D294}
header p{margin:6px 0 0;color:#fff;font-weight:500;font-size:15px}
.g{display:grid;grid-template-columns:repeat(3,200px);gap:18px 16px;padding:20px 24px 8px}
figure{margin:0;text-align:center}
.s{width:200px;height:200px;border-radius:24px;background:#FFFDF7;box-shadow:inset 0 0 0 2px #EFE6D2}
.s svg{width:100%;height:100%;mix-blend-mode:multiply}
.stamp text{fill:currentColor;stroke:none}
figcaption{margin-top:6px}
figcaption b{display:block;font:800 18px/1.1 'Barlow Condensed',sans-serif;letter-spacing:.04em;text-transform:uppercase;color:#283881}
figcaption span{display:block;margin-top:2px;font-weight:500;font-size:13px;line-height:1.25;color:#566086}
.new b::after{content:" · nouveau";color:#A51C36}
h2{margin:0;padding:6px 24px 0;font:800 22px/1 'Barlow Condensed',sans-serif;letter-spacing:.03em;text-transform:uppercase;color:#283881}
footer{padding:6px 24px 20px;color:#566086;font-weight:500;font-size:13px;line-height:1.35}
"""

NEW = {"defi", "bingo", "mot", "gourmand", "prix"}


def fig(j, key, word, title, how):
    return ('<figure class="%s"><div class="s">%s</div><figcaption><b>%s</b><span>%s</span></figcaption></figure>'
            % ("new" if key in NEW else "old", BG.bonus_stamp(j, key, word), title, how))


old = "".join(fig(j, *r) for j, r in enumerate(G.BONUS_STAMPS) if r[0] not in NEW)
new = "".join(fig(j, *r) for j, r in enumerate(G.BONUS_STAMPS) if r[0] in NEW)
html = ("<!doctype html><meta charset=utf-8><style>%s</style>%s" % (CSS, BG.INK_FILTER)
        + "<header><h1>Passeport · tampons spéciaux</h1><p>11 tampons à gagner en jouant, en plus des 17 tampons des jours (28 en tout)</p></header>"
        + "<h2 style='padding-top:16px'>Les 6 déjà prévus</h2><div class='g'>%s</div>" % old
        + "<h2>Les 5 nouveaux, exclusifs au site</h2><div class='g'>%s</div>" % new
        + "<footer>Chaque jeu rapporte son tampon. Sur le téléphone, la case vide montre le petit dessin en pâle ; le tampon s’imprime avec un léger effet d’encre quand le jeu est réussi.</footer>")
open(OUT + "planche.html", "w", encoding="utf-8").write(html)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 680, "height": 300}, device_scale_factor=2)
    pg.goto("file://" + OUT + "planche.html")
    pg.wait_for_timeout(500)
    pg.screenshot(path=OUT + "planche_bonus.png", full_page=True)
    b.close()
from PIL import Image
print(Image.open(OUT + "planche_bonus.png").size)
