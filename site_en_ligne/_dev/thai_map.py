import pdfplumber, math, json
pdf = pdfplumber.open("/mnt/user-data/uploads/Journal_de_bord.pdf")
p = pdf.pages[2]
big = [c for c in p.curves if (c["x1"]-c["x0"]) > 60 and (c["bottom"]-c["top"]) > 60 and c["x0"] > 250 and c["x1"] < 500]
B, A = big[0]["pts"], big[1]["pts"]
loop = list(A) + list(B[1:])      # A fini où B commence (écart 0.03) : boucle fermée
OX, OY = 304.4, 48.9

def rdp(pts, eps):
    if len(pts) < 3: return pts
    # itératif
    keep = [False]*len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts)-1)]
    while stack:
        i, j = stack.pop()
        (x1, y1), (x2, y2) = pts[i], pts[j]
        dx, dy = x2-x1, y2-y1
        L = math.hypot(dx, dy) or 1e-9
        dmax, k = 0, None
        for m in range(i+1, j):
            x0, y0 = pts[m]
            dd = abs(dy*x0 - dx*y0 + x2*y1 - y2*x1)/L
            if dd > dmax: dmax, k = dd, m
        if dmax > eps and k is not None:
            keep[k] = True
            stack += [(i, k), (k, j)]
    return [p for p, kf in zip(pts, keep) if kf]

pts = [((x-OX), (y-OY)) for x, y in loop]
s = rdp(pts, 0.28)
print("points", len(loop), "->", len(s))
d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in s) + "Z"
cities = {"sukhothai": (353.15-OX, 122.85-OY), "bangkok": (367.35-OX, 186.65-OY), "banphe": (384.65-OX, 206.75-OY)}
json.dump({"d": d, "w": 160.5, "h": 295.5, "cities": cities}, open("thai_map.json", "w"))
print(len(d), cities)
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 161 296" width="322" height="592"><path d="{d}" fill="#F7B71B"/>' + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#A51C36"/>' for x, y in cities.values()) + "</svg>"
open("thai_map.svg", "w").write(svg)
