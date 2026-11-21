"""Tampons (vague 2) : variété (statique), affichage, absence de rognage, états vide/plein, clics, identifiants uniques."""
import io, json, sys
from PIL import Image
sys.path.insert(0, "/home/claude/site_en_ligne")
import stamps as ST
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
DAYS = ["2026-12-18","2026-12-19","2026-12-20","2026-12-21","2026-12-22","2026-12-23","2026-12-24","2026-12-25","2026-12-26","2026-12-27","2026-12-28","2026-12-29","2026-12-30","2026-12-31","2027-01-01","2027-01-02","2027-01-03"]
BON = ["quiz", "doudou", "mots", "blind", "etoiles", "photos", "defi", "bingo", "mot", "gourmand", "prix"]
TOT = len(DAYS) + len(BON)
bad = []; n = [0]
def ck(ok, msg):
    n[0] += 1
    if not ok: bad.append(msg); print("KO  " + msg)
# ── statique ──
spec = [ST.DAY_SPEC[d] for d in DAYS]; bsp = [ST.BONUS_SPEC[k] for k in BON]
for i in range(len(DAYS) - 1):
    ck(spec[i][0] != spec[i + 1][0], "cadre différent entre %s et %s" % (DAYS[i], DAYS[i + 1]))
    ck(spec[i][1] != spec[i + 1][1], "encre différente entre %s et %s" % (DAYS[i], DAYS[i + 1]))
ck(len({s[2] for s in spec}) == 17, "17 dessins différents pour les 17 jours")
ck(len({s[2] for s in bsp}) == len(BON), "%d dessins différents pour les %d tampons spéciaux" % (len(BON), len(BON)))
ck(not ({s[2] for s in spec} & {s[2] for s in bsp}), "aucun dessin partagé entre jours et spéciaux")
ck(len({s[0] for s in spec}) >= 10, "au moins 10 cadres différents (%d)" % len({s[0] for s in spec}))
ck(len({s[1] for s in spec}) >= 5, "au moins 5 encres différentes (%d)" % len({s[1] for s in spec}))
errs = []
FULL = json.dumps({"d": DAYS, "b": BON})
with sync_playwright() as p:
    b = p.chromium.launch()
    for vw in (390, 320):
        ctx = b.new_context(viewport={"width": vw, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
        ctx.add_init_script("try{localStorage.setItem('carnet.open','1')}catch(e){}")  # les jeux sont tous ouverts (mot secret déjà tapé)
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        def show(state):
            if state is None: pg.evaluate("localStorage.removeItem('carnet.stamps')")
            else: pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % state)
            pg.reload(); pg.wait_for_timeout(350); pg.evaluate("location.hash='#/passeport'"); pg.wait_for_timeout(400)
        pg.goto(BASE)
        # ── plein ──
        show(FULL)
        ck(pg.locator("#v-pass .slot").count() == TOT, "%d px : %d cases" % (vw, TOT))
        ck(pg.locator("#v-pass .slot.on").count() == TOT, "%d px : %d cases tamponnées" % (vw, TOT))
        pg.add_style_tag(content=".nav{display:none!important}")
        for i in range(TOT):
            sv = pg.locator("#v-pass .slot").nth(i).locator("svg.stamp")
            sv.scroll_into_view_if_needed(); pg.wait_for_timeout(40)
            bx = sv.bounding_box(); sid = pg.locator("#v-pass .slot").nth(i).get_attribute("data-id")
            ck(bx and bx["width"] >= (70 if vw == 320 else 85), "%d px : tampon %s visible et assez grand (%.0f px)" % (vw, sid, bx["width"] if bx else 0))
            im = Image.open(io.BytesIO(sv.screenshot())).convert("RGB"); W, H = im.size; px = im.load()
            ring = [px[x, y] for x in range(W) for y in (0, H - 1)] + [px[x, y] for y in range(H) for x in (0, W - 1)]
            ink = sum(1 for c in ring if max(c) - min(c) > 45)   # l'encre est saturée ; le papier et le liseré beige ne le sont pas
            ck(ink == 0, "%d px : tampon %s non rogné (%d pixels d'encre sur le bord)" % (vw, sid, ink))
        # ── vide ──
        show(None)
        ck(pg.locator("#v-pass .slot.on").count() == 0, "%d px : aucune case tamponnée à vide" % vw)
        ck(pg.locator("#v-pass .slot-ph.d i svg").count() == 17, "%d px : 17 dessins pâles sur les jours" % vw)
        ck(pg.locator("#v-pass .slot-ph:not(.d) i svg").count() == len(BON), "%d px : %d dessins pâles sur les spéciaux" % (vw, len(BON)))
        hid = pg.evaluate("Array.from(document.querySelectorAll('#v-pass .slot svg.stamp')).every(v=>getComputedStyle(v).display==='none')")
        ck(hid, "%d px : tampons cachés tant que non gagnés" % vw)
        ph = pg.evaluate("""()=>Array.from(document.querySelectorAll('#v-pass .slot-ph.d')).map(e=>{const s=e.closest('.slot').getBoundingClientRect();const b=e.querySelector('b').getBoundingClientRect();const sm=e.querySelector('small').getBoundingClientRect();const i=e.querySelector('i svg').getBoundingClientRect();
          return {num:e.querySelector('b').textContent, ok: i.top>=s.top-0.5 && sm.bottom<=s.bottom+0.5 && b.left>=s.left && b.right<=s.right, ov: i.bottom<=b.top+3}})""")
        ck(all(o["ok"] for o in ph), "%d px : dessin, numéro et mois tiennent dans chaque case vide" % vw)
        ck(all(o["ov"] for o in ph), "%d px : le dessin ne recouvre pas le numéro" % vw)
        lab = pg.evaluate("""()=>Array.from(document.querySelectorAll('#v-pass .slot-ph:not(.d)')).map(e=>{const s=e.closest('.slot').getBoundingClientRect();const sm=e.querySelector('small').getBoundingClientRect();return sm.left>=s.left-0.5&&sm.right<=s.right+0.5})""")
        ck(all(lab), "%d px : libellés des cases spéciales dans la case" % vw)
        if vw == 390:
            # ── clics ──
            pg.locator('#v-pass .slot[data-id="2026-12-18"]').click(); pg.wait_for_timeout(300)
            ck(pg.locator('#v-pass .slot[data-id="2026-12-18"]').get_attribute("aria-pressed") == "true", "clic : le 18 déc. est tamponné")
            ck("Tamponné" in pg.inner_text("#toast"), "clic : message « Tamponné »")
            ck(json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')"))["d"] == ["2026-12-18"], "clic : mémorisé")
            ck(pg.inner_text("#pp-count").strip() == "1", "clic : compteur à 1")
            pg.locator('#v-pass .slot[data-id="quiz"]').click(); pg.wait_for_timeout(250)
            ck("À gagner" in pg.inner_text("#toast"), "clic : case spéciale non gagnée → « À gagner »")
            # ── identifiants uniques (copie du tampon sur la page de jour) ──
            pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % FULL)
            pg.evaluate("location.hash='#/jours/2026-12-19'"); pg.reload(); pg.wait_for_timeout(500)
            dup = pg.evaluate("""()=>{const c={};document.querySelectorAll('[id]').forEach(e=>c[e.id]=(c[e.id]||0)+1);return Object.keys(c).filter(k=>c[k]>1)}""")
            ck(dup == [], "identifiants uniques dans la page (doublons : %s)" % dup)
            ok = pg.evaluate("""()=>{const v=document.querySelector('#d-2026-12-19 .dstamp-svg svg');if(!v)return false;
              return Array.from(v.querySelectorAll('textPath')).every(t=>{const h=t.getAttribute('href');return h&&v.querySelector(h)})}""")
            ck(ok, "page de jour : le texte courbé pointe vers son propre tracé")
            ck(pg.locator("#d-2026-12-19 .dstamp-svg svg").count() == 1, "page de jour : tampon présent")
            # ── remise à zéro ──
            pg.evaluate("location.hash='#/passeport'"); pg.wait_for_timeout(300)
            pg.click("#pp-reset"); pg.wait_for_timeout(150); pg.click("#pp-reset"); pg.wait_for_timeout(300)
            ck(json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')")) == {"d": [], "b": []}, "remise à zéro")
            ck(pg.locator("#d-2026-12-19 .dstamp-svg svg").count() == 0, "remise à zéro : plus de tampon sur la page de jour")
        ctx.close()
    b.close()
print("%d contrôles, %d échecs" % (n[0], len(bad)))
print("erreurs JS:", errs or "aucune")
