import json
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
DAYS = ["2026-12-18", "2026-12-19", "2026-12-20", "2026-12-21", "2026-12-22", "2026-12-23", "2026-12-24", "2026-12-25",
        "2026-12-26", "2026-12-27", "2026-12-28", "2026-12-29", "2026-12-30", "2026-12-31", "2027-01-01", "2027-01-02", "2027-01-03"]
FULL = json.dumps({"d": DAYS, "b": ["quiz", "doudou", "mots", "blind", "etoiles", "photos"]})
BLIND = json.dumps({"Arthur": 99, "Daphne": 100, "Flo": 8, "Anne": 0})
errs = []
bad = []
count = [0]

JS = """() => {
  const de = document.documentElement, W = de.clientWidth;
  const over = [];
  const clipped = (e) => { for (let a = e.parentElement; a && a !== document.body && a !== de; a = a.parentElement) {
      const o = getComputedStyle(a).overflowX; if (o !== 'visible') return true; } return false; };
  document.querySelectorAll('body *').forEach(e => {
    if (e.closest('[hidden]')) return;
    if (e.closest('svg') && e.tagName.toLowerCase() !== 'svg') return;
    const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed') return;
    let p = e.parentElement, hid = false; while (p) { if (getComputedStyle(p).display === 'none') { hid = true; break; } p = p.parentElement; } if (hid) return;
    const r = e.getBoundingClientRect(); if (r.width === 0 && r.height === 0) return;
    if (clipped(e)) return;
    if (r.right > W + 1 || r.left < -1) over.push((e.tagName + '.' + ((typeof e.className === 'string') ? e.className : '')).slice(0, 50) + ' [' + Math.round(r.left) + ',' + Math.round(r.right) + ']');
  });
  return { sw: de.scrollWidth, cw: W, over: over.slice(0, 6) };
}"""


def check(pg, w, label):
    m = pg.evaluate(JS)
    count[0] += 1
    flag = m["sw"] > m["cw"] or m["over"]
    if flag:
        bad.append((w, label, m))
    print(("!! " if flag else "ok ") + "%d %-34s sw=%d cw=%d %s" % (w, label, m["sw"], m["cw"], m["over"] if m["over"] else ""))


with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in ((320, 640), (360, 740), (390, 844), (412, 915), (768, 1024)):
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, is_mobile=(w < 700), has_touch=True, locale="fr-FR", service_workers="block")
        pg = ctx.new_page()
        ctx.add_init_script("try{localStorage.setItem('carnet.open','1')}catch(e){}")  # le test de personnalité est ouvert (cadenas levé)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(BASE); pg.wait_for_timeout(300)

        def go(hh, wait=300):
            pg.evaluate("location.hash=%r" % hh); pg.wait_for_timeout(wait)

        def shot(name):
            if w in (320, 390):
                pg.screenshot(path=OUT + "o_%d_%s.png" % (w, name), full_page=True)

        # accueil, hub, passeport vide
        go("#/"); check(pg, w, "accueil"); shot("accueil")
        go("#/jeux"); check(pg, w, "jeux"); shot("jeux")
        go("#/passeport"); check(pg, w, "passeport (vide)"); shot("passeport_vide")
        # quiz : intro, question, fin
        go("#/quiz"); check(pg, w, "quiz intro")
        pg.click('[data-qz="start"]'); pg.wait_for_timeout(150); check(pg, w, "quiz question 1")
        pg.locator(".qz-q").nth(0).locator(".qz-o").nth(1).click(); pg.wait_for_timeout(120); check(pg, w, "quiz q1 répondue"); shot("quiz_q1")
        for i in range(6):
            q = pg.locator(".qz-q").nth(i)
            if i > 0:
                q.locator(".qz-o").nth(0).click(); pg.wait_for_timeout(60)
            q.locator('[data-qz="next"]').click(); pg.wait_for_timeout(80)
        check(pg, w, "quiz fin"); shot("quiz_fin")
        # test du doudou : intro, question, résultat
        go("#/personnalite"); check(pg, w, "test intro")
        pg.click('[data-dt="start"]'); pg.wait_for_timeout(120); check(pg, w, "test question 1")
        for i in range(10):
            pg.locator(".dt-q").nth(i).locator('.qz-o[data-who="boop"]').click(); pg.wait_for_timeout(50)
        pg.wait_for_timeout(200); check(pg, w, "test résultat"); shot("test_res")
        go("#/mascottes"); check(pg, w, "doudous"); shot("doudous")
        # blind test : grands scores
        pg.evaluate("localStorage.setItem('carnet.blind', %r)" % BLIND)
        pg.reload(); pg.wait_for_timeout(350); go("#/blind-test"); check(pg, w, "blind test (99/100)"); shot("blind")
        # mots mêlés
        go("#/mots-meles", 400); check(pg, w, "mots mêlés"); shot("mots")
        pg.click("#mm-zoom"); pg.wait_for_timeout(200); check(pg, w, "mots mêlés zoom"); pg.click("#mm-zoom"); pg.wait_for_timeout(100)
        # horoscope
        go("#/horoscope", 400); check(pg, w, "horoscope"); shot("horoscope")
        # passeport plein
        pg.evaluate("localStorage.setItem('carnet.stamps', %r)" % FULL)
        pg.reload(); pg.wait_for_timeout(350); go("#/passeport", 500); check(pg, w, "passeport (plein)"); shot("passeport_plein")
        # pages de jours (tampon gagné + pas gagné)
        for d in ("2026-12-19", "2026-12-26", "2026-12-31", "2027-01-03"):
            go("#/jours/" + d, 350); check(pg, w, "jour " + d)
            if d == "2026-12-26":
                shot("jour26")
        pg.evaluate("localStorage.removeItem('carnet.stamps')")
        pg.reload(); pg.wait_for_timeout(300); go("#/jours/2026-12-20", 350); check(pg, w, "jour 20 (sans tampon)")
        # toast long visible
        go("#/passeport"); pg.click('.slot[data-id="quiz"]'); pg.wait_for_timeout(200); check(pg, w, "passeport + toast")
        ctx.close()
    b.close()
print("\n%d vues contrôlées, %d problèmes" % (count[0], len(bad)))
for x in bad:
    print("  ", x)
print("ERREURS JS:", errs if errs else "aucune")
