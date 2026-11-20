#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Horoscope du voyage : rassemble les 12 signes (texte imprimé p. 21 du carnet, jour de chance, mot du voyage, constellation)
dans data_horoscope.json à partir des fichiers de mise en page de /mnt/user-data/uploads/jeux2.
Exécution unique : python3 -I _dev/extract_horoscope.py"""
import ast, json, os
SRC = "/mnt/user-data/uploads/jeux2"
HERE = os.path.dirname(os.path.abspath(__file__))


def literal_assign(path, name):
    """Valeur littérale de `name = {...}` (dict de dict(...) acceptés) dans un fichier Python, sans l'exécuter."""
    tree = ast.parse(open(os.path.join(SRC, path), encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ev(node.value)
    raise KeyError((path, name))


def ev(n):
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dict":
        return {k.arg: ev(k.value) for k in n.keywords}
    if isinstance(n, ast.Dict):
        return {ev(k): ev(v) for k, v in zip(n.keys, n.values)}
    if isinstance(n, (ast.List, ast.Tuple)):
        return [ev(x) for x in n.elts]
    return ast.literal_eval(n)


SHORT = literal_assign("short12.py", "SHORT")
TEXTS = literal_assign("horoscope_36x14.py", "TEXTS36")
COMPACT = literal_assign("horoscope_36x14.py", "COMPACT")
CONST = dict(literal_assign("horoscope.py", "CONST"))
for k, v in literal_assign("signs12.py", "CONST_NEW").items():
    CONST[k] = v
CONST.update(COMPACT)                     # le carnet imprimé utilise la version allégée du Scorpion

ORDER = [  # nom, élément, constellation, mot du voyage (latin), thaï
    ("Bélier", "feu", "ARIES", "sanuk", "สนุก"), ("Taureau", "terre", "TAURUS", "aroi", "อร่อย"),
    ("Gémeaux", "air", "GEMINI", "sawasdee", "สวัสดี"), ("Cancer", "eau", "CANCER", "sabai", "สบาย"),
    ("Lion", "feu", "LEO", "suay", "สวย"), ("Vierge", "terre", "VIRGO", "riap roi", "เรียบร้อย"),
    ("Balance", "air", "LIBRA", "khop khun", "ขอบคุณ"), ("Scorpion", "eau", "SCORPIUS", "mai pen rai", "ไม่เป็นไร"),
    ("Sagittaire", "feu", "SAGITTARIUS", "pai tiao", "ไปเที่ยว"), ("Capricorne", "terre", "CAPRICORNUS", "chok dee", "โชคดี"),
    ("Verseau", "air", "AQUARIUS", "nam", "น้ำ"), ("Poissons", "eau", "PISCES", "pla", "ปลา"),
]
out = []
for name, el, const, mot, th in ORDER:
    s = SHORT[name]
    c = CONST[const]
    out.append(dict(name=name, el=el, chance=s["chance"], mot=mot, th=th, mean=s["mean"][0], text=TEXTS[name],
                    stars=[[round(x, 3), round(y, 3), r] for x, y, r in c["stars"]], lines=[list(l) for l in c["lines"]]))
    print(f"{name:11s} {el:5s} {s['chance']:9s} {mot:12s} {th:10s} ({s['mean'][0]})  étoiles={len(c['stars'])} lignes={len(c['lines'])}")
json.dump(out, open(os.path.join(HERE, "..", "data_horoscope.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
