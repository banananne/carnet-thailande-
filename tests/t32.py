# -*- coding: utf-8 -*-
"""Dernier lot avant publication : (1) espaces insécables posées partout dans le texte de la page, sans toucher aux balises,
attributs, scripts, styles et dessins ; (2) transcription « suay » identique partout. Vérifie web/index.html et le générateur."""
import sys, re
from html.parser import HTMLParser

sys.path.insert(0, "/home/claude/site_en_ligne")
import build_app as A
import build_site as S
import data_trad as T
import data_days as X

NB = " "
fails = []
n = [0]


def ck(cond, msg, extra=""):
    n[0] += 1
    if not cond:
        fails.append(msg)
    print(("OK   " if cond else "FAIL ") + msg + ("" if cond or extra == "" else " : " + str(extra)))


class Walk(HTMLParser):
    """Sépare le document en : texte visible, structure (balises + attributs), contenus de script/style/svg."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.text, self.struct, self.blocks, self.skip = [], [], [], 0
        self.cur = None

    def handle_starttag(self, tag, attrs):
        self.struct.append(("s", tag, tuple(attrs)))
        if tag in ("script", "style", "svg"):
            self.skip += 1

    def handle_startendtag(self, tag, attrs):
        self.struct.append(("e", tag, tuple(attrs)))

    def handle_endtag(self, tag):
        self.struct.append(("c", tag))
        if tag in ("script", "style", "svg") and self.skip:
            self.skip -= 1

    def handle_data(self, d):
        (self.blocks if self.skip else self.text).append(d)

    def handle_entityref(self, name):
        (self.blocks if self.skip else self.text).append("&%s;" % name)

    def handle_charref(self, name):
        (self.blocks if self.skip else self.text).append("&#%s;" % name)

    def handle_comment(self, data):
        self.struct.append(("#", data))


def walk(h):
    w = Walk()
    w.feed(h)
    w.close()
    return w


# ── 1. le texte de la page produite ──
page = open("/home/claude/site_en_ligne/web/index.html", encoding="utf-8").read()
w = walk(page)
text = "".join(w.text)
bad = re.findall(r".{0,25}[^\s  ] [:;?!»].{0,10}|.{0,10}« .{0,25}", text)
ck(not bad, "A1 aucun espace ordinaire avant : ; ? ! » ni après « dans le texte de la page (%d trouvés)" % len(bad), bad[:6])
ck(text.count(NB + "?") > 100 and text.count(NB + ":") > 100 and text.count(NB + "!") > 50, "A2 les espaces insécables sont bien là (? : !) : %d / %d / %d" % (text.count(NB + "?"), text.count(NB + ":"), text.count(NB + "!")))
for s in ("Pas encore" + NB + "!", "Qui es-tu" + NB + "?", "Du 30 décembre au 1er janvier" + NB + ":", "Ici, ta photo du jour" + NB + "!"):
    ck(s in text, "A3 « %s » avec espace insécable" % s.replace(NB, "⍽"))

# ── 2. rien d'autre n'a bougé : même page, aux espaces près ──
orig = A.render("t32", S.APP_META)
done = A.nbsp_pass(orig)
ck(done.replace(NB, " ") == orig.replace(NB, " "), "B1 le passage ne change que des espaces en espaces insécables (aucun caractère ajouté ni retiré)")
a, b = walk(orig), walk(done)
ck(a.struct == b.struct, "B2 balises, attributs et commentaires identiques (%d balises)" % len(a.struct))
ck("".join(a.blocks) == "".join(b.blocks), "B3 scripts, styles et dessins identiques (%d morceaux)" % len(a.blocks))
ck(len(a.blocks) > 50 and sum(len(x) for x in a.blocks) > 100000, "B4 les scripts et styles sont bien repérés (%d morceaux, %d Ko)" % (len(a.blocks), sum(len(x) for x in a.blocks) // 1024))
js = "".join(b.blocks)
ck("/ ([:;?!»])/g" in js and "\\u00a0$1" in js, "B5 la fonction nb() des scripts est restée intacte")
ck(re.search(r'placeholder="[^"]* [?:][^"]*"', done) is not None, "B6 les attributs (placeholder) ne sont pas touchés")
ck(done.count("<main ") == orig.count("<main "), "B7 même nombre de vues (%d)" % done.count("<main "))
# le passage ne modifie pas deux fois : repasser dessus ne change plus rien
ck(A.nbsp_pass(done) == done, "B8 repasser dessus ne change plus rien")
# cas limites du passage
t = A.nbsp_pass('<p class="a b" title="Qui es-tu ?">Qui es-tu ? Oui : non</p><script>var s = "a ? b : c";</script><style>a :hover{}</style><svg><text>x !</text></svg><b>Salut</b> ! « ok »')
ck(t == '<p class="a b" title="Qui es-tu ?">Qui es-tu' + NB + '? Oui' + NB + ': non</p><script>var s = "a ? b : c";</script><style>a :hover{}</style><svg><text>x !</text></svg><b>Salut</b>' + NB + '! «' + NB + 'ok' + NB + '»', "B9 cas limites (attribut, script, style, dessin, balise suivie d'un point d'exclamation)", repr(t))

# ── 3. « suay » partout ──
ck("suai" not in page.lower(), "C1 plus de « suai » dans la page")
rows = [r for _t, rs in T.BOOK for r in rs if "สวย" in r[2]]
ck(len(rows) == 2 and all("suay" in r[1] for r in rows), "C2 les deux phrases du traducteur avec สวย s'écrivent « suay »", rows)
ck("suay" in X.MOTS[2][1], "C3 le mot du jour du 20 décembre s'écrit « suay mak »")
ck(page.count("suay mak") >= 2, "C4 « suay mak » apparaît dans le recueil et dans le mot du jour (%d fois)" % page.count("suay mak"))
ck("kho khao suay" in page, "C5 « kho khao suay » dans le recueil")

print()
print("OK %d  ÉCHECS %d" % (n[0] - len(fails), len(fails)))
for f in fails:
    print("   ÉCHEC :", f)
