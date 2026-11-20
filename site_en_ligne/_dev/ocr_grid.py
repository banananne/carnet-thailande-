import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from fontTools.ttLib import TTFont

SB = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/s3"
img = Image.open(SB + "/grid_crop.png").convert("RGB")
a = np.asarray(img).astype(int)
ink = (a[:, :, 0] < 150) & (a[:, :, 1] < 70) & (a[:, :, 2] < 90)
lab, n = ndimage.label(ink)
objs = ndimage.find_objects(lab)
comps = []
for i, sl in enumerate(objs, 1):
    h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
    area = int((lab[sl] == i).sum())
    comps.append((sl, h, w, area, i))
hs = sorted(c[1] for c in comps if c[3] > 40)
medh = hs[len(hs) // 2]
print("composantes", n, "hauteur médiane", medh)
letters = [c for c in comps if 0.7 * medh < c[1] < 1.3 * medh and c[2] < 1.5 * medh and c[3] > 40]
print("lettres", len(letters))
# polices : Barlow 500/600/700 -> TTF
tmp = SB + "/fonts"; os.makedirs(tmp, exist_ok=True)
FONTS = {}
for w in (500, 600, 700):
    out = f"{tmp}/barlow{w}.ttf"
    if not os.path.exists(out):
        f = TTFont(f"/home/claude/site_en_ligne/_dev/node_modules/@fontsource/barlow/files/barlow-latin-{w}-normal.woff")
        f.flavor = None; f.save(out)
    FONTS[w] = out
S = 32
def norm(mask):
    ys, xs = np.where(mask)
    m = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray((m * 255).astype("uint8")).resize((S, S), Image.BILINEAR)
    return np.asarray(im).astype(float) / 255.0, m.shape
tpl = {}
for w, path in FONTS.items():
    font = ImageFont.truetype(path, 120)
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        im = Image.new("L", (200, 200), 0)
        ImageDraw.Draw(im).text((30, 20), ch, font=font, fill=255)
        mk = np.asarray(im) > 128
        if not mk.any(): continue
        v, shp = norm(mk)
        tpl.setdefault(ch, []).append((v, shp[1] / shp[0]))
res = {}
for sl, h, w, area, i in letters:
    mask = (lab[sl] == i)
    v, shp = norm(mask)
    ar = shp[1] / shp[0]
    best = []
    for ch, lst in tpl.items():
        for tv, tar in lst:
            d = np.abs(v - tv).mean() + 0.15 * abs(ar - tar)
            best.append((d, ch))
    best.sort()
    top = {}
    for d, ch in best:
        top.setdefault(ch, d)
    cands = sorted(top.items(), key=lambda kv: kv[1])[:3]
    cy = (sl[0].start + sl[0].stop) / 2; cx = (sl[1].start + sl[1].stop) / 2
    res[(cy, cx)] = cands
# placer en grille 20 x 20
ys = sorted(k[0] for k in res)
xs = sorted(k[1] for k in res)
def cluster(vals, n):
    # k-means 1D simple par découpage en n groupes selon les plus grands écarts
    vals = sorted(vals); gaps = sorted(range(1, len(vals)), key=lambda i: vals[i] - vals[i - 1], reverse=True)[:n - 1]
    cuts = sorted(gaps); groups, prev = [], 0
    for c in cuts + [len(vals)]:
        groups.append(vals[prev:c]); prev = c
    return [sum(g) / len(g) for g in groups]
rows = cluster(ys, 20); cols = cluster(xs, 20)
print("lignes :", [round(r) for r in rows][:5], "... colonnes :", [round(c) for c in cols][:5])
grid = [[None] * 20 for _ in range(20)]; conf = [[None] * 20 for _ in range(20)]
for (cy, cx), cands in res.items():
    r = min(range(20), key=lambda k: abs(rows[k] - cy)); c = min(range(20), key=lambda k: abs(cols[k] - cx))
    if grid[r][c] is not None:
        print("collision", r, c)
    grid[r][c] = cands[0][0]; conf[r][c] = cands
missing = [(r, c) for r in range(20) for c in range(20) if grid[r][c] is None]
print("cases manquantes :", missing)
doubt = [(r, c, conf[r][c]) for r in range(20) for c in range(20) if conf[r][c] and (conf[r][c][0][1] > 0.12 or (conf[r][c][1][1] - conf[r][c][0][1]) < 0.02)]
print("cases douteuses :", [(r, c, [(ch, round(d, 3)) for ch, d in cands]) for r, c, cands in doubt])
json.dump(["".join(x or "?" for x in row) for row in grid], open(SB + "/grid.json", "w"))
for row in grid: print(" ".join(x or "?" for x in row))
