# -*- coding: utf-8 -*-
"""Tampons du passeport : onze cadres, un petit dessin par jour et par jeu (grille 48 x 48), mise en page.

stamp_svg(uid, shape, word, picto, date, city, color, rot) renvoie un <svg> de 120 x 120 « tamponné à la main »
(le filtre #ink est défini une seule fois dans la page, voir build_games.INK_FILTER).
"""
import math
from html import escape


def esc(s):
    return escape(str(s), quote=True)


# ───────────────────────── petits dessins (grille 48 x 48, traits seulement) ─────────────────────────
def _star(cx, cy, ro, ri, n=5):
    pts = []
    for k in range(2 * n):
        r = ro if k % 2 == 0 else ri
        a = math.radians(-90 + k * 180.0 / n)
        pts.append("%.1f %.1f" % (cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + "L".join(pts) + "Z"


def _rays(cx, cy, r1, r2, n, rot=0.0):
    d = ""
    for k in range(n):
        a = math.radians(rot + k * 360.0 / n)
        d += "M%.1f %.1fL%.1f %.1f" % (cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r2 * math.cos(a), cy + r2 * math.sin(a))
    return d


def _dots(cx, cy, r, n, rad=1.4, rot=0.0):
    out = ""
    for k in range(n):
        a = math.radians(rot + k * 360.0 / n)
        out += '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="currentColor" stroke="none"/>' % (cx + r * math.cos(a), cy + r * math.sin(a), rad)
    return out


def _dot(x, y, r):
    return '<circle cx="%s" cy="%s" r="%s" fill="currentColor" stroke="none"/>' % (x, y, r)


def _spark(x, y, s):
    return "M%s %sV%sM%s %sH%s" % (x, y - s, y + s, x - s, y, x + s)


def _zoom(k, inner):
    return '<g transform="translate(24 24) scale(%s) translate(-24 -24)">%s</g>' % (k, inner)


WAVE = "q4.5-4 9 0t9 0t9 0t9 0t9 0"
FLUTE = '<path d="M-5.5 -21H5.5L4.2 -7Q0 -2 -4.2 -7Z"/><path d="M-4.6 -14H4.6"/><path d="M0 -2.5V12.5M-5.5 12.5H5.5"/>'

P = {
    # ── les jours ──
    "avion_haut": ('<g transform="translate(24 24) rotate(45) scale(.9) translate(-24 -24)">'
                   '<path d="M24 3C26 3 27.5 6 27.5 10V19L45 31V35.5L27.5 30.5V38L33 42V45L24 43L15 45V42L20.5 38V30.5L3 35.5V31L20.5 19V10C20.5 6 22 3 24 3Z"/></g>'
                   '<path d="M4 44C8 41 11 38 14 34" stroke-dasharray="0.1 5.4"/>'),
    "valise": ('<rect x="8" y="16" width="32" height="24" rx="4.5"/>'
               '<path d="M18 16V12.5A3 3 0 0 1 21 9.5H27A3 3 0 0 1 30 12.5V16"/>'
               '<path d="M17 16V40M31 16V40M14 40V43.5M34 40V43.5"/>'),
    "longtail": ('<path d="M5 28H43Q41 38 33 38H16Q8 38 5 28Z"/><path d="M10 23H38L34.5 16.5H13.5Z"/><path d="M14 23V28M34 23V28"/>'
                 '<path d="M41 28L46 15"/>' + _dot(46, 14, 1.7) + '<path d="M3 44' + WAVE + '"/>'),
    "prang": ('<path d="M24 3V9"/><path d="M24 9C27 15 29 18 32 24C35 29 36 34 38 41H10C12 34 13 29 16 24C19 18 21 15 24 9Z"/>'
              '<path d="M20 17H28M17 25H31M14 33H34"/><path d="M6 41H42M4 45H44"/>'),
    "nonla": _zoom(1.12, '<path d="M24 9L44 31H4Z"/><path d="M4 31Q24 40 44 31"/><path d="M24 9V5.5"/>'
                   '<path d="M13 22.5Q24 27 35 22.5M8.5 27Q24 32.5 39.5 27"/><path d="M14 35Q24 45 34 35"/>'),
    "palais": _zoom(1.1, '<path d="M24 3V10"/><path d="M14 21Q22 19 24 10Q26 19 34 21Z"/><path d="M6 31Q19 29 22 21H26Q29 29 42 31Z"/>'
                    '<path d="M12 31V44M36 31V44M9 44H39M18 34V44M24 34V44M30 34V44"/>'),
    "etal": ('<path d="M6 17L9.5 7H38.5L42 17"/><path d="M3 17q4.5 7 9 0t9 0t9 0t9 0t9 0"/><path d="M17 7L15 17M24 7V17M31 7L33 17"/>'
             '<path d="M7 27V44M41 27V44M4 27H44"/><circle cx="15" cy="23.2" r="2.6"/><circle cx="24" cy="23.2" r="2.6"/><circle cx="33" cy="23.2" r="2.6"/>'),
    "sapin": ('<path d="%s"/>' % _star(24, 7, 5.2, 2.3) + '<path d="M24 13L32 23H27.5L35.5 32H29.5L38 41H10L18.5 32H12.5L20.5 23H16Z"/>'
              '<path d="M21 41V45.5H27V41"/>' + _dot(21, 29, 1.7) + _dot(28, 36, 1.7) + _dot(18.5, 37, 1.5)),
    "avion_cote": ('<g transform="rotate(-16 24 26)"><path d="M9 21.5H36C41 21.5 45 23 45 25C45 27 41 28.5 36 28.5H11C8 28.5 6.5 26 5 21.5Z"/>'
                   '<path d="M5 21.5L3.5 11H8.5L16 21.5"/><path d="M20.5 28.5L13.5 40.5H20L33 28.5"/><path d="M27 25H28M31.5 25H32.5M36 25H37"/></g>'
                   '<path d="M3 44H12M17 44H26M31 44H40"/>'),
    "velo": ('<circle cx="11" cy="33" r="8.5"/><circle cx="37" cy="33" r="8.5"/><path d="M11 33L18 20H32L22 33Z"/><path d="M18 20L22 33M32 20L37 33"/>'
             '<path d="M32 20L30.5 14.5H35.5"/><path d="M14.5 17H21.5"/>' + _dot(22, 33, 1.8)),
    "bouddha": ('<path d="M24 2C35 12 38.5 31 24 46C9.5 31 13 12 24 2Z"/>' + _dot(24, 14, 3.4) +
                '<path d="M24 19C21 19 20 21 19.6 25L18.4 40H29.6L28.4 25C28 21 27 19 24 19Z" fill="currentColor"/>'
                '<path d="M28.6 26L33 21.5" stroke-width="2.6"/><path d="M12 44H36" stroke-width="2.6"/>'),
    "mer": _zoom(1.14, '<path d="M14 27A10 10 0 0 1 34 27"/><path d="M24 11V14.5M9.5 16.5L12.5 19.5M38.5 16.5L35.5 19.5"/><path d="M6 27H42"/>'
                 '<path d="M3 33' + WAVE + 'M3 40' + WAVE + '"/>'),
    "palmier": ('<path d="M26 45C24 37 24 28 28 19"/>'
                '<path d="M28 19C22 12 14 12 8 19M28 19C23 10 15 7 9 10M28 19C33 10 41 9 45 14M28 19C36 15 42 20 43 28M28 19C26 12 28 7 33 4"/>'
                + _dot(26.5, 22.5, 2) + _dot(30.3, 22, 2) + '<path d="M8 45H42"/>'),
    "flutes": _zoom(1.2, '<g transform="translate(17 28) rotate(11)">' + FLUTE + '</g><g transform="translate(31 28) rotate(-11)">' + FLUTE + '</g>'
                    '<path d="%s%s"/>' % (_spark(7.5, 11, 3), _spark(40.5, 11, 3))),
    "feu": _zoom(1.12, '<path d="%s"/><path d="%s"/>' % (_rays(24, 24, 6, 15, 8, 0), _rays(24, 24, 8, 12, 8, 22.5)) + _dots(24, 24, 19, 8, 1.4)
                 + '<path d="%s%s%s%s"/>' % (_spark(7, 7, 2.6), _spark(41, 7, 2.6), _spark(41, 41, 2.6), _spark(7, 41, 2.6))),
    "ville": ('<path d="M5 44V26H15V44M15 44V11H28V44M28 44V21H43V44"/><path d="M21.5 11V4"/>'
              '<path d="M19 18H24M19 25H24M19 32H24M32 28H39M32 35H39M9 32H11M9 38H11"/><path d="M3 44H45"/>'),
    "lotus": _zoom(1.1, '<path d="M24 6C31 14 31.5 26 24 36C16.5 26 17 14 24 6Z"/><path d="M24 36C14 36 8 29 8 20C16 21 22 27 24 36Z"/>'
                   '<path d="M24 36C34 36 40 29 40 20C32 21 26 27 24 36Z"/><path d="M10 41H38M15 45H33"/>'),
    # ── les jeux (tampons spéciaux) ──
    "b_quiz": ('<path d="M16 19C16 8 32 8 32 18.5C32 25.5 24 25 24 32.5"/>' + _dot(24, 40, 2.3)
               + '<path d="%s%s"/>' % (_spark(9, 10, 3), _spark(40, 36, 3))),
    "b_mascotte": ('<path d="M24 26C17.5 26 12.5 31.5 14.5 36.5C16 40 20 39.5 24 38C28 39.5 32 40 33.5 36.5C35.5 31.5 30.5 26 24 26Z"/>'
                   '<circle cx="10.5" cy="22" r="3.8"/><circle cx="18.5" cy="13.5" r="4.2"/><circle cx="29.5" cy="13.5" r="4.2"/><circle cx="37.5" cy="22" r="3.8"/>'),
    "b_mots": ('<rect x="7" y="7" width="34" height="34" rx="4.5"/><path d="M18.3 7V41M29.7 7V41M7 18.3H41M7 29.7H41"/>'
               '<path d="M12.5 12.5L35.5 35.5" stroke-width="6"/>'),
    "b_blind": ('<path d="M9 30V25A15 15 0 0 1 39 25V30"/><rect x="6" y="28" width="9" height="14" rx="3.5"/><rect x="33" y="28" width="9" height="14" rx="3.5"/>'
                '<path d="M26 18V32M26 18Q31 19 30 25"/>' + _dot(23.5, 32, 2.6)),
    "b_etoiles": ('<path d="%s"/>' % _star(24, 25, 15, 6.4) + '<path d="%s%s"/>' % (_spark(39, 7, 3), _spark(8, 39, 3))),
    "b_photo": ('<rect x="6" y="15" width="36" height="25" rx="5"/><path d="M16.5 15L19.5 9.5H28.5L31.5 15"/>'
                '<circle cx="24" cy="27.5" r="8"/><circle cx="24" cy="27.5" r="3.3"/>' + _dot(36, 21, 1.5)),
    # ── les jeux exclusifs au site ──
    "b_defi": ('<rect x="8" y="6" width="29" height="36" rx="3.5"/><rect x="12.5" y="10.5" width="20" height="19" rx="1.5"/>'
               '<path d="M12.5 29.5L21 21L26 26L29 23L32.5 27.5"/><path d="M16 36.5H29"/>' + _dot(18.5, 16, 1.8)
               + '<path d="%s"/>' % _spark(41, 9, 3.2)),
    "b_bingo": ('<circle cx="24" cy="24" r="17"/><circle cx="24" cy="24" r="9.5"/><path d="%s"/>' % _star(24, 24.5, 5.4, 2.4)
                + '<path d="%s%s"/>' % (_spark(7.5, 8, 2.6), _spark(41, 40.5, 2.6))),
    "b_mot": ('<path d="M10 10H38A4 4 0 0 1 42 14V28A4 4 0 0 1 38 32H26L16.5 41V32H10A4 4 0 0 1 6 28V14A4 4 0 0 1 10 10Z"/>'
              '<path d="M13.5 18.5H34.5M13.5 24.5H26.5"/>'),
    "b_gourmand": ('<path d="M6 25H42C42 35 34 41.5 24 41.5C14 41.5 6 35 6 25Z"/><path d="M17.5 45.5H30.5"/>'
                   '<path d="M13 19Q10.5 15.5 13 12M20 19Q17.5 15.5 20 12M27 19Q24.5 15.5 27 12"/>'
                   '<path d="M34 23L43 5M39 24.5L46.5 9"/>'),
    "b_curieux": ('<circle cx="20" cy="20" r="13"/><path d="M30 30L42.5 42.5"/><path d="M13.5 17.5Q15.5 12.5 21.5 12.5"/>'),
    "b_prix": ('<path d="M15 6H33V18C33 24.5 29 28.5 24 28.5C19 28.5 15 24.5 15 18Z"/><path d="M15 10H9.5Q9 20 16.5 21.5M33 10H38.5Q39 20 31.5 21.5"/>'
               '<path d="M24 28.5V34.5"/><path d="M18 34.5H30V41.5H18Z"/><path d="M14 41.5H34"/>'
               '<path d="%s"/>' % _star(24, 16.5, 4.2, 1.9)),
}


def picto_icon(name, sw=2.7):
    """Le même dessin, pour les cases du passeport pas encore tamponnées (gris clair, voir games.css)."""
    return ('<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="%s" '
            'stroke-linecap="round" stroke-linejoin="round">%s</svg>' % (sw, P[name]))


# ───────────────────────── choix des cadres, des encres et des dessins ─────────────────────────
NAVY, WINE, TEAL, OCHRE, GREEN, PLUM = "#283881", "#A51C36", "#0F6B73", "#B25E00", "#1E7B4F", "#6B2F7A"

# jour -> (cadre, encre, dessin)  : deux cases voisines n'ont jamais le même cadre ni la même encre
DAY_SPEC = {
    "2026-12-18": ("ticket", NAVY, "avion_haut"),
    "2026-12-19": ("round", WINE, "valise"),
    "2026-12-20": ("oval", TEAL, "longtail"),
    "2026-12-21": ("arch", OCHRE, "prang"),
    "2026-12-22": ("hex", TEAL, "nonla"),
    "2026-12-23": ("rect", PLUM, "palais"),
    "2026-12-24": ("postage", WINE, "etal"),
    "2026-12-25": ("scallop", GREEN, "sapin"),
    "2026-12-26": ("postmark", NAVY, "avion_cote"),
    "2026-12-27": ("octagon", GREEN, "velo"),
    "2026-12-28": ("banner", OCHRE, "bouddha"),
    "2026-12-29": ("oval", TEAL, "mer"),
    "2026-12-30": ("round", OCHRE, "palmier"),
    "2026-12-31": ("hex", PLUM, "flutes"),
    "2027-01-01": ("postage", WINE, "feu"),
    "2027-01-02": ("rect", NAVY, "ville"),
    "2027-01-03": ("scallop", WINE, "lotus"),
}
# jeu -> (cadre, encre, dessin)
BONUS_SPEC = {
    "quiz": ("octagon", GREEN, "b_quiz"),
    "doudou": ("scallop", PLUM, "b_mascotte"),
    "mots": ("postage", TEAL, "b_mots"),
    "blind": ("banner", WINE, "b_blind"),
    "etoiles": ("arch", NAVY, "b_etoiles"),
    "photos": ("rect", OCHRE, "b_photo"),
    # jeux exclusifs au site : jamais deux cases voisines (3 par ligne) avec le même cadre ni la même encre
    "defi": ("hex", TEAL, "b_defi"),
    "bingo": ("round", WINE, "b_bingo"),
    "mot": ("octagon", PLUM, "b_mot"),
    "gourmand": ("arch", OCHRE, "b_gourmand"),
    "prix": ("postmark", NAVY, "b_prix"),
    "curieux": ("scallop", GREEN, "b_curieux"),
}

# ───────────────────────── mise en page ─────────────────────────
ARC_TOP = "M 21.5 60 A 38.5 38.5 0 0 1 98.5 60"
ARC_BOT = "M 15.5 60 A 44.5 44.5 0 0 0 104.5 60"


def fit(s, width, mx, mn=6.5):
    return max(mn, min(mx, width / (max(1, len(s)) * 0.6)))


def _t(x, y, s, fs, extra=""):
    return '<text x="%s" y="%s" text-anchor="middle" font-size="%.1f"%s>%s</text>' % (x, y, fs, extra, esc(s))


def _pic(picto, cx, cy, box, sw=2.1):
    k = box / 48.0
    return '<g transform="translate(%.2f %.2f) scale(%.4f)" stroke-width="%.2f" fill="none" stroke-linejoin="round">%s</g>' % (cx - box / 2.0, cy - box / 2.0, k, sw / k, picto)


def _poly(r, n=8, rot=22.5, cx=60, cy=60):
    return " ".join("%.1f,%.1f" % (cx + r * math.cos(math.radians(rot + k * 360.0 / n)), cy + r * math.sin(math.radians(rot + k * 360.0 / n))) for k in range(n))


def _scallop(r=47, n=18, cx=60, cy=60):
    rho = r * math.sin(math.pi / n)
    pts = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    d = "M%.2f %.2f" % pts[0]
    for k in range(1, n + 1):
        x, y = pts[k % n]
        d += "A%.2f %.2f 0 0 1 %.2f %.2f" % (rho, rho, x, y)
    return d + "Z"


def stamp_svg(uid, shape, word, picto, date, city, color, rot):
    g = '<g transform="rotate(%d 60 60)" filter="url(#ink)" fill="none" stroke="currentColor" stroke-linecap="round">' % rot
    B = ' font-weight="800"'
    LS = ' letter-spacing="1"'
    if shape == "round":
        g += '<circle cx="60" cy="60" r="55" stroke-width="3.4"/><circle cx="60" cy="60" r="49" stroke-width="1.2"/>'
        g += '<defs><path id="%st" d="%s"/><path id="%sb" d="%s"/></defs>' % (uid, ARC_TOP, uid, ARC_BOT)
        g += '<text font-size="%.1f" letter-spacing="1.1"><textPath href="#%st" startOffset="50%%" text-anchor="middle">%s</textPath></text>' % (fit(word, 96, 11.5), uid, esc(word))
        if city:
            g += '<text font-size="%.1f" letter-spacing="1.1"><textPath href="#%sb" startOffset="50%%" text-anchor="middle">%s</textPath></text>' % (fit(city, 100, 10.5), uid, esc(city))
        g += _pic(picto, 60, 51, 34) + _t(60, 83, date, fit(date, 46, 13.5), B)
    elif shape == "rect":
        g += '<rect x="7" y="21" width="106" height="78" rx="11" stroke-width="3.2"/><rect x="12.5" y="26.5" width="95" height="67" rx="6.5" stroke-width="1.2"/>'
        g += _t(60, 43, word, fit(word, 88, 12.5), LS) + '<path d="M20 49.5h80M20 79.5h80" stroke-width="1"/>'
        g += _pic(picto, 60, 64.5, 27)
        bl = (date + (" · " + city if city else "")).strip()
        g += _t(60, 90.5, bl, fit(bl, 88, 11.5), LS)
    elif shape == "oval":
        g += '<ellipse cx="60" cy="60" rx="56" ry="41" stroke-width="3.2"/><ellipse cx="60" cy="60" rx="50" ry="35" stroke-width="1.2"/>'
        g += _t(60, 41.5, word, fit(word, 62, 11), LS) + _pic(picto, 60, 60, 29) + _t(60, 88, date, fit(date, 48, 13), B)
    elif shape == "hex":
        g += ('<polygon points="114,60 87,106.8 33,106.8 6,60 33,13.2 87,13.2" stroke-width="3.2" stroke-linejoin="round"/>'
              '<polygon points="107,60 83.5,100.7 36.5,100.7 13,60 36.5,19.3 83.5,19.3" stroke-width="1.2" stroke-linejoin="round"/>')
        g += _t(60, 37, word, fit(word, 56, 11), LS) + _pic(picto, 60, 59, 31) + _t(60, 92, date, fit(date, 40, 12.5), B)
    elif shape == "ticket":
        g += ('<path d="M9 22H111V50a10 10 0 0 0 0 20V98H9V70a10 10 0 0 0 0-20Z" stroke-width="3.2" stroke-linejoin="round"/>'
              '<path d="M16 29H104V50M104 70V91H16V70M16 50V29" stroke-width="1.1" stroke-dasharray="3 2.2"/>')
        g += _t(60, 44, word, fit(word, 80, 12.5), LS)
        g += _pic(picto, 38, 67, 33) + '<path d="M62 55V85" stroke-width="1.3" stroke-dasharray="2 3"/>'
        bits = date.split(" ", 1)
        if len(bits) == 2:
            g += _t(85, 75, bits[0], 29, B) + _t(85, 87, bits[1], 11, ' letter-spacing="1.6"')
        else:
            g += _t(85, 79, date, fit(date, 40, 13), B)
    elif shape == "scallop":
        g += '<path d="%s" stroke-width="3"/><circle cx="60" cy="60" r="40" stroke-width="1.2"/>' % _scallop()
        g += '<defs><path id="%st" d="M 31 58 A 29 29 0 0 1 89 58"/></defs>' % uid
        g += '<text font-size="%.1f" letter-spacing="1"><textPath href="#%st" startOffset="50%%" text-anchor="middle">%s</textPath></text>' % (fit(word, 70, 10.5), uid, esc(word))
        g += _pic(picto, 60, 58, 28) + _t(60, 84, date, fit(date, 40, 12), B)
    elif shape == "arch":
        g += '<path d="M17 106V54A43 43 0 0 1 103 54V106Z" stroke-width="3.2" stroke-linejoin="round"/><path d="M23 100V54A37 37 0 0 1 97 54V100Z" stroke-width="1.2" stroke-linejoin="round"/>'
        g += _t(60, 38, word, fit(word, 58, 11.5), LS) + _pic(picto, 60, 63, 31) + _t(60, 92, date, fit(date, 56, 13), B)
    elif shape == "postage":
        g += '<rect x="13" y="13" width="94" height="94" stroke-width="4.8" stroke-dasharray="0.1 5.9"/>'
        g += '<rect x="20" y="20" width="80" height="80" stroke-width="2.4"/><rect x="24" y="24" width="72" height="72" stroke-width="1"/>'
        g += _t(60, 38, word, fit(word, 58, 11.5), LS) + _pic(picto, 60, 59, 29) + _t(60, 86, date, fit(date, 56, 13), B)
    elif shape == "octagon":
        g += '<polygon points="%s" stroke-width="3.2" stroke-linejoin="round"/><polygon points="%s" stroke-width="1.2" stroke-linejoin="round"/>' % (_poly(57), _poly(51))
        g += _t(60, 33, word, fit(word, 62, 11.5), LS) + _pic(picto, 60, 58, 32) + _t(60, 91, date, fit(date, 56, 13), B)
    elif shape == "postmark":
        g += '<circle cx="44" cy="60" r="38" stroke-width="3.2"/><circle cx="44" cy="60" r="33" stroke-width="1.2"/>'
        g += ''.join('<path d="M84 %d q4 -5 8 0 t8 0 t8 0 t8 0" stroke-width="2.4"/>' % y for y in (38, 51, 64, 77))
        g += _t(44, 41.5, word, fit(word, 40, 10.5), LS) + _pic(picto, 44, 58.5, 28) + _t(44, 84.5, date, fit(date, 40, 11.5), B)
    else:  # banner : ruban en travers
        g += '<path d="M4 51H116L108 63L116 75H4L12 63Z" stroke-width="3" stroke-linejoin="round"/><path d="M12 55.5H108M12 70.5H108" stroke-width="0.9"/>'
        g += _t(60, 67.5, word, fit(word, 86, 12.5), LS) + _pic(picto, 60, 28, 36)
        g += _t(60, 92, date, fit(date, 70, 14), B)
        if city:
            g += _t(60, 105, city, fit(city, 80, 9), ' letter-spacing="1.2"')
    g += "</g>"
    return ('<svg class="stamp" viewBox="0 0 120 120" aria-hidden="true" focusable="false" style="color:%s" '
            'font-family="\'Barlow Condensed\',\'Barlow\',sans-serif" font-weight="700">%s</svg>' % (color, g))
