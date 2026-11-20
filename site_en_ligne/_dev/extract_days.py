#!/usr/bin/env python3
"""Extrait la structure des pages « jours » du Journal_de_bord.pdf (p. 6 à 18).

Pour chaque double page : titre (Arial-Black 12 pt), déroulé (Barlow-Regular 9 pt,
colonne de gauche, repéré par les pastilles), fun facts (pastilles orange, texte
Barlow-LightItalic 7 pt, mot-clé en Barlow-SemiBoldItalic).
Sortie : _dev/days_raw.json (à relire avec les images avant de s'en servir).
"""
import json, sys, re
import pdfplumber

PDF = "/mnt/user-data/uploads/Journal_de_bord.pdf"
OUT = "/home/claude/site_en_ligne/_dev/days_raw.json"
MID = 510.236  # moitié de la double page


def group_lines(chars, ytol=2.2):
    """Regroupe des caractères en lignes (par 'top' proche), triés par x."""
    chars = sorted(chars, key=lambda c: (round(c["top"], 1), c["x0"]))
    lines = []
    for c in chars:
        if lines and abs(lines[-1]["top"] - c["top"]) <= ytol:
            lines[-1]["chars"].append(c)
        else:
            lines.append({"top": c["top"], "chars": [c]})
    out = []
    for ln in lines:
        cs = sorted(ln["chars"], key=lambda c: c["x0"])
        # reconstruit le texte avec espaces selon les écarts
        txt = ""
        last = None
        spans = []  # (texte, bold)
        for c in cs:
            if last is not None:
                gap = c["x0"] - last["x1"]
                if gap > c["size"] * 0.18 and not txt.endswith(" ") and c["text"] != " ":
                    txt += " "
                    spans.append((" ", False))
            if c["text"] == " ":
                if not txt.endswith(" "):
                    txt += " "
                    spans.append((" ", False))
                last = c
                continue
            txt += c["text"]
            spans.append((c["text"], "SemiBold" in c["fontname"] or "Bold" in c["fontname"] or "NotoSansThai" in c["fontname"]))
            last = c
        out.append({
            "top": ln["top"],
            "bottom": max(c["bottom"] for c in cs),
            "x0": cs[0]["x0"],
            "x1": cs[-1]["x1"],
            "text": txt.strip(),
            "spans": spans,
        })
    return out


def spans_to_md(spans):
    s = ""
    cur = False
    for t, b in spans:
        if b and not cur:
            s += "**"
            cur = True
        if not b and cur and t != " ":
            s = s.rstrip()
            s += "** "
            cur = False
        s += t
    if cur:
        s += "**"
    s = re.sub(r"\*\*\s*\*\*", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def main(first=6, last=18):
    pdf = pdfplumber.open(PDF)
    res = {}
    for n in range(first, last + 1):
        p = pdf.pages[n - 1]
        chars = p.chars
        # titres
        heads = [c for c in chars if "Arial-Black" in c["fontname"]]
        head_lines = group_lines(heads)
        # déroulé : Barlow-Regular 9 pt dans la moitié gauche
        tl = [c for c in chars if "Barlow-Regular" in c["fontname"] and abs(c["size"] - 9) < 0.6 and c["x0"] < MID]
        tl_lines = group_lines(tl)
        # puces (cercles) du déroulé
        bullets = sorted(
            [round((c["top"] + c["bottom"]) / 2, 1) for c in p.curves
             if c["x0"] > 280 and c["x1"] < 340 and (c["x1"] - c["x0"]) < 10 and (c["bottom"] - c["top"]) < 10 and c.get("fill")],
        )
        # pastilles orange (fun facts)
        pills = sorted(
            {(round(c["top"]), round(c["bottom"]), round(c["x0"]), round(c["x1"])) for c in p.curves
             if c.get("fill") and (c["x1"] - c["x0"]) > 120 and (c["bottom"] - c["top"]) > 30 and c["x0"] > MID},
        )
        # texte des fun facts
        ff = [c for c in chars if c["x0"] > MID
              and "Arial-Black" not in c["fontname"] and "MinionPro" not in c["fontname"]
              and not ("Barlow-Regular" in c["fontname"] and (abs(c["size"] - 8) < 0.6 or abs(c["size"] - 12) < 0.6))]
        ff_lines = group_lines(ff)
        # autre texte (numéro de page, etc.)
        other = [c for c in chars if "MinionPro" in c["fontname"]]
        other_lines = group_lines(other)
        res[n] = {
            "heads": [(l["text"], round(l["x0"]), round(l["top"])) for l in head_lines],
            "timeline": [{"top": round(l["top"], 1), "x0": round(l["x0"]), "x1": round(l["x1"]), "text": l["text"]} for l in tl_lines],
            "bullets": bullets,
            "pills": [{"top": a, "bottom": b, "x0": c, "x1": d} for a, b, c, d in pills],
            "facts_lines": [{"top": round(l["top"], 1), "x0": round(l["x0"]), "text": spans_to_md(l["spans"])} for l in ff_lines],
            "other": [(l["text"], round(l["x0"]), round(l["top"])) for l in other_lines],
        }
    json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)
    print("ok ->", OUT)


if __name__ == "__main__":
    a = [int(x) for x in sys.argv[1:3]] if len(sys.argv) > 2 else [6, 18]
    main(*a)
