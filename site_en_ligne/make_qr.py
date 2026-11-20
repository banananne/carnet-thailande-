# -*- coding: utf-8 -*-
"""QR code du carnet en ligne (GitHub Pages) : l'adresse ne change jamais tant que le dépôt garde son nom."""
import segno, subprocess, os, sys
URL = "https://banananne.github.io/carnet-thailande-/"
OUT = "/mnt/user-data/outputs"
NAVY = "#283881"
qr = segno.make(URL, error="q", micro=False, boost_error=False)
print("version", qr.version, "modules", qr.symbol_size(border=0), "niveau", qr.error)

# 1) fond transparent, modules bleu marine, marge de 4 modules (zone de silence) : à poser sur un fond CLAIR
qr.save(f"{OUT}/QR_carnet_site_marine.svg", scale=10, border=4, dark=NAVY, light=None, xmldecl=True, svgns=True, nl=False)

# 2) plaque blanche aux coins arrondis, marge de 4 modules incluse : sûr sur n'importe quel fond (même bordeaux)
qr.save(f"{OUT}/QR_carnet_site_plaque_blanche.svg", scale=10, border=4, dark=NAVY, light="#FFFFFF", xmldecl=True, svgns=True, nl=False)

# 3) PDF vectoriels (pour InDesign : Fichier > Importer) via rsvg-convert
for n in ("marine", "plaque_blanche"):
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", f"{OUT}/QR_carnet_site_{n}.pdf", f"{OUT}/QR_carnet_site_{n}.svg"], check=True)

# 4) aperçu PNG pour tester le scan depuis l'écran
qr.save(f"{OUT}/QR_carnet_site_apercu.png", scale=14, border=4, dark=NAVY, light="#FFFFFF")
print(os.listdir(OUT))
