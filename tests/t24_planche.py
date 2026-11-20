"""Planche légendée des tampons (jours + spéciaux), pour Anne. Entrée : st_one_XX.png (t21)."""
import base64, datetime, sys
sys.path.insert(0, "/home/claude/site_en_ligne")
import data_games as G
from playwright.sync_api import sync_playwright
T = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
FONTS = "/home/claude/site_en_ligne/web/fonts/"
def b64(path): return base64.b64encode(open(path, "rb").read()).decode()
def font(family, weight, fn): return "@font-face{font-family:'%s';font-weight:%s;src:url(data:font/woff2;base64,%s) format('woff2')}" % (family, weight, b64(FONTS + fn))
CSS_FONTS = font("Barlow", 500, "barlow-latin-500-normal.woff2") + font("Barlow", 700, "barlow-latin-700-normal.woff2") + font("Barlow Condensed", 800, "barlow-condensed-latin-800-normal.woff2")
DAYS = [("2026-12-18", "Un avion qui décolle"), ("2026-12-19", "Une valise"), ("2026-12-20", "Un bateau longtail"), ("2026-12-21", "Un prang, tour de temple"),
        ("2026-12-22", "Un chapeau conique"), ("2026-12-23", "Le palais"), ("2026-12-24", "Un étal de marché"), ("2026-12-25", "Un sapin"),
        ("2026-12-26", "Un avion au-dessus des vagues"), ("2026-12-27", "Un vélo"), ("2026-12-28", "Un bouddha"), ("2026-12-29", "Le soleil sur la mer"),
        ("2026-12-30", "Un palmier"), ("2026-12-31", "Deux flûtes qui trinquent"), ("2027-01-01", "Un feu d’artifice"), ("2027-01-02", "La ville"), ("2027-01-03", "Une fleur de lotus")]
JOURS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
def img(i): return "data:image/png;base64," + b64(T + "st_one_%02d.png" % i)
def cell(i, l1, l2): return '<figure><div class="box"><img src="%s" alt=""></div><figcaption><b>%s</b><span>%s</span></figcaption></figure>' % (img(i), l1, l2)
days_html = ""
for i, (d, what) in enumerate(DAYS):
    dt = datetime.date.fromisoformat(d)
    days_html += cell(i, "%s %d %s" % (JOURS[dt.weekday()], dt.day, MOIS[dt.month - 1]), "%s · %s" % (G.STAMP_WORDS[d].capitalize() if False else G.STAMP_WORDS[d], what))
bonus_html = ""
for j, (k, word, title, how) in enumerate(G.BONUS_STAMPS):
    bonus_html += cell(17 + j, title, how)
CSS = CSS_FONTS + """
*{box-sizing:border-box}body{margin:0;background:#FFFCF6;color:#1F2548;font:500 14px/1.35 'Barlow',sans-serif;width:600px}
header{background:#A51C36;padding:22px 24px 16px}header h1{margin:0;font:800 40px/1 'Barlow Condensed',sans-serif;letter-spacing:.02em;text-transform:uppercase;color:#F7D294}
header p{margin:6px 0 0;color:#fff;font-size:15px}
section{padding:20px 24px 6px}h2{margin:0 0 12px;font:800 24px/1 'Barlow Condensed',sans-serif;letter-spacing:.02em;text-transform:uppercase;color:#283881}
.lead{margin:-4px 0 14px;color:#566086;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px 12px}
figure{margin:0;text-align:center}figure .box{aspect-ratio:1/1}figure img{display:block;width:100%;height:100%;object-fit:fill}
figcaption{margin-top:5px}figcaption b{display:block;font:800 16px/1.1 'Barlow Condensed',sans-serif;letter-spacing:.04em;text-transform:uppercase;color:#283881}
figcaption span{display:block;margin-top:2px;font-size:12.5px;line-height:1.25;color:#566086}
footer{padding:10px 24px 22px;color:#566086;font-size:13px}
"""
def page(title, sub, body):
    return "<!doctype html><meta charset=utf-8><style>%s</style><header><h1>%s</h1><p>%s</p></header>%s" % (CSS, title, sub, body)
p1 = page("Passeport", "Un tampon différent chaque jour : forme, couleur d’encre et dessin",
          '<section><h2>Les 17 jours</h2><div class="grid">%s</div></section><footer>Sur le téléphone, chaque case vide montre déjà le petit dessin du jour en pâle ; le tampon s’imprime quand on la touche (ou quand on prend une photo du jour).</footer>' % days_html)
p2 = page("Passeport", "Les 6 tampons spéciaux, gagnés en jouant",
          '<section><h2>Les tampons spéciaux</h2><div class="grid">%s</div></section><footer>Chaque jeu rapporte son tampon : quiz, test de personnalité, mots mêlés, blind test, horoscope et photos.</footer>' % bonus_html)
open(T + "planche_jours.html", "w", encoding="utf8").write(p1)
open(T + "planche_speciaux.html", "w", encoding="utf8").write(p2)
with sync_playwright() as p:
    b = p.chromium.launch()
    for name in ("jours", "speciaux"):
        pg = b.new_page(viewport={"width": 600, "height": 200}, device_scale_factor=2)
        pg.goto("file://" + T + "planche_%s.html" % name); pg.wait_for_timeout(400)
        pg.screenshot(path=T + "planche_%s.png" % name, full_page=True)
        pg.close()
    b.close()
from PIL import Image
for n in ("jours", "speciaux"): print(n, Image.open(T + "planche_%s.png" % n).size)
