# -*- coding: utf-8 -*-
"""Plan du métro de Bangkok (moitié droite de la page 4 du carnet) → SVG vectoriel pour le site.
On retire de la page la moitié gauche (hôtels, photos) et le numéro de page, puis on exporte avec MuPDF
(SVG sans filtres feImage : ceux de poppler/cairo ne s'affichent pas dans Safari)."""
import re, sys, os
import pymupdf

PDF = "/mnt/user-data/uploads/Journal_de_bord.pdf"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/site_en_ligne/web/assets/metro.svg"
SPLIT = 510.236


def build(out=OUT):
    doc = pymupdf.open(PDF)
    doc.select([3])                      # page 4
    pg = doc[0]
    mb = pg.mediabox
    # numéro de page (tout en bas à droite)
    for w in pg.get_text("words"):
        if w[0] > 980 and w[1] > 360:
            pg.add_redact_annot(pymupdf.Rect(w[0] - 2, w[1] - 2, w[2] + 2, w[3] + 2), fill=False)
    pg.add_redact_annot(pymupdf.Rect(0, 0, SPLIT, mb.y1), fill=False)
    pg.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE,
                        graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                        text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    pg.set_cropbox(pymupdf.Rect(SPLIT, 0, mb.x1 - 0.01, mb.y1))
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
    svg = svg.replace(' xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"', "")
    svg = re.sub(r"\n\s*\n", "\n", svg)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(svg)
    m = re.search(r'viewBox="([^"]+)"', svg)
    print("metro.svg : %d Ko, viewBox %s" % (len(svg.encode("utf-8")) // 1024, m.group(1) if m else "?"))


if __name__ == "__main__":
    build()
