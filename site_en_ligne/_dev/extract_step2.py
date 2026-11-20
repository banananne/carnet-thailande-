# -*- coding: utf-8 -*-
"""Extrait de /home/claude/lexique (sources des pages du carnet papier) le lexique et les bulles « Good to know »
et les range dans data_step2.json, pour que le générateur du site n'ait plus besoin de ce dossier.
Exécution unique : python3 -I _dev/extract_step2.py"""
import json, os, sys
sys.path.insert(0, "/home/claude/lexique")
import content as K            # lexique (page de gauche) + URGENCES
import content_culture as C    # HISTOIRE EN DATES, SAVOIR-VIVRE EN PLUS, BOUDDHISME ET ESPRITS, UNE COULEUR PAR JOUR


def pick(lst, title):
    return next(d for d in lst if d["title"] == title)


savoir = pick(C.RIGHT_B, "SAVOIR-VIVRE EN PLUS")
# comme sur la page « Good to know » du carnet : la puce « Tenue » est retirée
savoir = dict(savoir, blocks=[dict(b, items=[t for t in b["items"] if not t.startswith("**Tenue**")]) if b["kind"] == "bullets" else b
                              for b in savoir["blocks"]])
gtk = [pick(C.LEFT_B, "HISTOIRE EN DATES"), savoir, pick(C.RIGHT_A, "BOUDDHISME ET ESPRITS"),
       pick(C.LEFT_A, "UNE COULEUR PAR JOUR"), pick(K.RIGHT_A, "URGENCES")]
lex = K.LEFT_A + K.LEFT_B
out = dict(lexique=lex, gtk=gtk)
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_step2.json")
json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("écrit", os.path.abspath(dest), len(json.dumps(out)), "octets")
for d in lex + gtk:
    print(" -", d["title"], [b["kind"] for b in d["blocks"]])
