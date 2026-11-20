import json, re
d = json.load(open("/home/claude/site_en_ligne/_dev/days_raw.json"))

def clean(s):
    s = s.replace("'", "’")
    parts = s.split("**")            # alterne : normal, gras, normal, gras…
    toks = []                         # (texte, gras)
    for i, t in enumerate(parts):
        if t == "": continue
        toks.append([t, i % 2 == 1])
    # fusion des segments gras séparés par des espaces seulement
    out = []
    for t, b in toks:
        if out and b and out[-1][1] and False: pass
        out.append([t, b])
    merged = []
    for t, b in out:
        if merged and merged[-1][1] and b:
            merged[-1][0] += t
        elif merged and b and not merged[-1][1] and merged[-1][0].strip() == "" and len(merged) >= 2 and merged[-2][1]:
            merged[-2][0] += merged[-1][0] + t; merged.pop()
        else:
            merged.append([t, b])
    # espaces : sortir les espaces de début/fin des segments gras
    res = []
    for t, b in merged:
        if b:
            lead = t[:len(t)-len(t.lstrip())]; trail = t[len(t.rstrip()):]
            core = t.strip()
            res.append([lead, False]); res.append([core, True]); res.append([trail, False])
        else:
            res.append([t, False])
    s2 = ""
    for i, (t, b) in enumerate(res):
        if b:
            s2 += "**" + t + "**"
        else:
            s2 += t
    # pas d'espace entre la fin d'un gras et une ponctuation
    s2 = re.sub(r"\*\*\s+([,.;:)])", r"**\1", s2)
    s2 = re.sub(r"\s{2,}", " ", s2).strip()
    return s2

def pills(n):
    x = d[str(n)]
    res = []
    for pl in x["pills"]:
        lines = [l for l in x["facts_lines"] if pl["top"] - 2 <= l["top"] <= pl["bottom"] + 2]
        paras = []; cur = []; last = None
        for l in lines:
            if last is not None and l["top"] - last["top"] > 12.5:
                paras.append(cur); cur = []
            cur.append(l); last = l
        if cur: paras.append(cur)
        res.append([clean(" ".join(l["text"] for l in para)) for para in paras])
    return res

out = {str(n): pills(n) for n in (7, 8, 9, 10, 11, 12, 14, 15)}
# correction d'une coquille du carnet (p.18 : « y est enseigné est inscrit »)
for pl in out["10"]:
    for i, q in enumerate(pl):
        pl[i] = q.replace("Le massage thaï y est enseigné est inscrit", "Le massage thaï y est enseigné et est inscrit")
json.dump(out, open("/home/claude/site_en_ligne/data_facts.json", "w"), ensure_ascii=False, indent=1)
for n in ("10", "8"):
    print("== p", n)
    for i, p in enumerate(out[n], 1):
        for q in p: print(f"  [{i}] {q}")
print({k: len(v) for k, v in out.items()})
