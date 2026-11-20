#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrait du PDF Journal_de_bord.pdf (pages 20 et 23) le test « Quel doudou es-tu ? » et les fiches des quatre doudous,
et les range dans data_test_doudou.json. Exécution unique : python3 -I _dev/extract_step3.py"""
import json, os, re, sys
import pymupdf
PDF = "/mnt/user-data/uploads/Journal_de_bord.pdf"
HERE = os.path.dirname(os.path.abspath(__file__))
doc = pymupdf.open(PDF)
SYM = {"★": "aftonsparv", "■": "boop", "▲": "minou", "●": "moomoo"}


def spans_of(pno):
    out = []
    for b in doc[pno].get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                if s["text"].strip():
                    out.append((s["bbox"], s["text"].strip()))
    return out


def lines_of(spans, x0, x1, ymin, ymax, step=2.0):
    sel = [s for s in spans if x0 <= s[0][0] < x1 and ymin <= s[0][1] < ymax]
    rows = {}
    for bb, t in sel:
        rows.setdefault(round(bb[1] / step), []).append((bb[0], t))
    return [(k * step, " ".join(t for _, t in sorted(v))) for k, v in sorted(rows.items())]


# ───── test (p. 20) ─────
sp = spans_of(19)
qs = []
for (x0, x1) in ((150, 520), (520, 1000)):
    rows = lines_of(sp, x0, x1, 90, 360)
    cur, pend = None, None
    for y, t in rows:
        if "coller ici la photo" in t or t.startswith("du jour"):
            t = t.replace("coller ici la photo", "").strip()
            if not t or t.startswith("du jour"):
                continue
        m = re.match(r"^(\d{1,2})$", t)
        if m:                                   # numéro seul : l'intitulé est la ligne précédente, déjà lue
            cur = dict(n=int(m.group(1)), q=pend, opts=[]); qs.append(cur); pend = None
            continue
        m = re.match(r"^(\d{1,2}) (.+)$", t)
        if m and not t[0] in SYM:                # numéro + intitulé sur la même ligne
            cur = dict(n=int(m.group(1)), q=m.group(2), opts=[]); qs.append(cur); pend = None
            continue
        if t[0] in SYM:                          # option : symbole (+ texte)
            rest = t[1:].strip()
            if rest:
                cur["opts"].append((t[0], rest))
            else:
                pend = ("sym", t[0])
            continue
        if isinstance(pend, tuple) and pend[0] == "sym":
            cur["opts"].append((pend[1], t)); pend = None
            continue
        pend = t                                  # intitulé de la question suivante (numéro lu après)
out_q = []
for q in sorted(qs, key=lambda z: z["n"]):
    assert len(q["opts"]) == 4, q
    assert sorted(s for s, _ in q["opts"]) == sorted(SYM), q
    out_q.append(dict(n=q["n"], q=q["q"], opts=[dict(sym=s, who=SYM[s], t=t) for s, t in q["opts"]]))
assert [q["n"] for q in out_q] == list(range(1, 11)) and all(q["q"] for q in out_q)

# ───── fiches des doudous (p. 23) ─────
sp = spans_of(22)
cards = {}
for who, (x0, x1) in zip(("aftonsparv", "boop", "minou", "moomoo"), ((54, 232), (287, 465), (560, 740), (795, 975))):
    rows = [(y, t) for y, t in lines_of(sp, x0, x1, 95, 330, step=1.5) if t not in ("★", "■", "▲", "●")]
    title_lines, body, sec, secs, quote = [], [], None, {}, None
    for y, t in rows:
        if t.startswith("Tu es ") and sec is None and not title_lines:
            title_lines.append(t)
        elif title_lines and not body and sec is None and len(title_lines) < 3 and not re.search(r"[.!:]$", t) and (y < 113):
            title_lines.append(t)
        elif t in ("SUPER-POUVOIR", "POINT FAIBLE", "ALLIÉ", "TON ENDROIT DU VOYAGE"):
            sec = t; secs[sec] = []
        elif t.startswith("«") and t.endswith("»"):
            quote = t; sec = None
        elif sec:
            secs[sec].append(t)
        else:
            body.append(t)
    cards[who] = dict(title=" ".join(title_lines), body=" ".join(body), **{k: " ".join(v) for k, v in secs.items()}, quote=quote)
for k, v in cards.items():
    print(k, json.dumps(v, ensure_ascii=False, indent=1))
json.dump(dict(questions=out_q, cards=cards), open(os.path.join(HERE, "..", "data_test_doudou.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for q in out_q:
    print(q["n"], q["q"])
    for o in q["opts"]:
        print("    ", o["sym"], o["who"], "|", o["t"])
