import json
SB = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/s3"
G = json.load(open(SB + "/grid.json"))
N = 20
WORDS = ["AVION", "BAHT", "BAN PHE", "BANGKOK", "BOUDDHA", "COCOTIER", "CURRY", "DURIAN", "ÉLÉPHANT", "ENCENS", "ESCALE", "FERRY", "GECKO",
         "KHAO SAN", "KHOP KHUN", "KOH SAMET", "LOTUS", "MANGUE", "MARCHÉ DE NUIT", "MASSAGE", "NOUILLES", "OFFRANDE", "ORCHIDÉE", "PAD THAI",
         "PASSEPORT", "PLAGE", "RAMBOUTAN", "SABAI", "SANUK", "SAWASDEE", "SKYTRAIN", "SUKHOTHAI", "TEMPLE", "TOM YUM", "TONGS", "TUK TUK",
         "VALISE", "VÉLO", "VOYAGE", "WAT"]
def key(w): return w.replace(" ", "").replace("É", "E")
DIRS = [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]
bad = 0
found = {}
for w in WORDS:
    k = key(w); L = len(k); occ = []
    for d in DIRS:
        for r in range(N):
            for c in range(N):
                r2, c2 = r + d[0] * (L - 1), c + d[1] * (L - 1)
                if 0 <= r2 < N and 0 <= c2 < N and all(G[r + d[0] * i][c + d[1] * i] == k[i] for i in range(L)):
                    occ.append((r, c, d))
    found[w] = occ
    if len(occ) != 1:
        bad += 1
    print(f"{w:16s} {len(occ)} {occ[:3]}")
print("mots non uniques/absents :", bad)
cov = set()
for w, occ in found.items():
    if len(occ) == 1:
        r, c, d = occ[0]
        for i in range(len(key(w))): cov.add((r + d[0] * i, c + d[1] * i))
print("cases couvertes par les mots :", len(cov), "/ 400 ; cases de remplissage :", 400 - len(cov))
