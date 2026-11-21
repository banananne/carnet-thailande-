"""Fabrique un faux « env_public.json » (4 prénoms, faux codes) pour tester le VRAI chemin du site sans toucher au vrai jeu."""
import sys, json, copy
sys.path.insert(0, "/home/claude/site_en_ligne")
import build_env as BE, data_env as E
OUT = sys.argv[1]
PEOPLE = {"Arthur": "test-alpha-1111", "Daphne": "test-bravo-2222", "Flo": "test-charlie-3333", "Anne": "test-delta-4444"}
base = E.sim_payloads()
S, B = {}, {}
for who, code in PEOPLE.items():
    pl = copy.deepcopy(base)
    for w in pl:
        pl[w]["title"] = "Mission secrète de %s (%s)" % (who, w)
        nc = len(pl[w]["rev"]["cols"])
        pl[w]["rev"]["rows"] = [[n] + ["x%d" % i for i in range(1, nc)] for n in PEOPLE]
    pl["w2"]["hunt"]["words"] = ["%s-mot%d" % (who.lower(), i) for i in range(1, 9)]
    salt, blobs = BE.seal_person(code, who, pl)
    S[who] = salt; B[who] = blobs
json.dump({"s": S, "b": B}, open(OUT, "w"))
print("faux jeu écrit :", OUT, sorted(S))
