# -*- coding: utf-8 -*-
"""Plan du métro de Bangkok pour le site : le plan complet BTS / MRT envoyé par Anne le 20 novembre 2026
(PDF vectoriel de une page, _dev/bts_metro_map.pdf) converti en SVG.
On retire le bandeau gris du titre (le site a son propre titre), on recadre, puis on exporte avec MuPDF :
texte converti en tracés (le thaï s'affiche sans police) et SVG sans filtres feImage (ceux de poppler / cairo
ne s'affichent pas dans Safari)."""
import re, sys, os
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "_dev", "bts_metro_map.pdf")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "web", "assets", "metro.svg")
TOP = 92.0        # bas du bandeau gris de titre, en points (le plan commence plus bas)


def build(out=OUT):
    doc = pymupdf.open(PDF)
    pg = doc[0]
    mb = pg.mediabox
    pg.add_redact_annot(pymupdf.Rect(-12, -12, mb.x1 + 12, TOP), fill=False)
    pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                        graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
                        text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    pg.set_cropbox(pymupdf.Rect(0, TOP, mb.x1, mb.y1))
    svg = pg.get_svg_image(text_as_path=True)

    TOK = re.compile(r"[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")

    def num(t):
        out = ("%.3f" % float(t)).rstrip("0").rstrip(".")
        return "0" if out in ("-0", "") else out

    def fix_d(m):
        """Arrondit les nombres d'un tracé à 3 décimales, en gardant toujours un séparateur entre deux nombres."""
        out, prev_num = [], False
        for t in TOK.findall(m.group(1)):
            if t[0].isalpha():
                out.append(t); prev_num = False
            else:
                n = num(t)
                if prev_num and not n.startswith("-"):
                    out.append(" ")
                out.append(n); prev_num = True
        return 'd="' + "".join(out) + '"'

    def fix_tr(m):
        return 'transform="matrix(' + re.sub(r"-?\d*\.\d+", lambda n: ("%.4f" % float(n.group(0))).rstrip("0").rstrip(".") or "0", m.group(1)) + ')"'

    svg = re.sub(r'\bd="([^"]*)"', fix_d, svg)
    svg = re.sub(r'transform="matrix\(([^)]*)\)"', fix_tr, svg)
    svg = re.sub(r' data-text="[^"]*"', "", svg)          # texte de secours des glyphes : inutile à l'écran
    svg = re.sub(r' inkscape:[A-Za-z]+="[^"]*"', "", svg)       # calques Inkscape : inutiles (et sans eux, on peut retirer la déclaration)
    svg = svg.replace(' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"', "")
    svg = re.sub(r"\n\s*\n", "\n", svg)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(svg)
    m = re.search(r'viewBox="([^"]+)"', svg)
    print("metro.svg : %d Ko, viewBox %s" % (len(svg.encode("utf-8")) // 1024, m.group(1) if m else "?"))


if __name__ == "__main__":
    build()
