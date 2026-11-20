import json, subprocess, sys, time
from playwright.sync_api import sync_playwright
PORT = 8766
BASE = "http://127.0.0.1:%d/carnet-thailande-/" % PORT
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
fails = []; n = [0]; errs = []; failed_req = []


def ok(cond, msg):
    n[0] += 1
    if not cond:
        fails.append(msg); print("ÉCHEC:", msg)


srv = subprocess.Popen([sys.executable, "-I", OUT + "serve.py", str(PORT)])
time.sleep(1.0)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="allow")
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("requestfailed", lambda r: failed_req.append(r.url))
        pg.goto(BASE); pg.wait_for_timeout(500)
        # attendre que le service worker soit actif et que tout soit en cache
        pg.evaluate("navigator.serviceWorker.ready.then(()=>1)")
        for _ in range(100):
            ctl = pg.evaluate("!!navigator.serviceWorker.controller")
            if ctl: break
            pg.wait_for_timeout(100)
        if not pg.evaluate("!!navigator.serviceWorker.controller"):
            pg.reload(); pg.wait_for_timeout(800)
        ok(pg.evaluate("!!navigator.serviceWorker.controller"), "le service worker contrôle la page")
        info = pg.evaluate("""async () => { const ks = await caches.keys(); const out = {}; for (const k of ks) { const c = await caches.open(k); out[k] = (await c.keys()).map(r => new URL(r.url).pathname.replace('/carnet-thailande-/', '')); } return out; }""")
        print("caches :", {k: len(v) for k, v in info.items()})
        ks = list(info.keys()); ok(len(ks) == 1, "un seul cache : %s" % ks)
        files = info[ks[0]] if ks else []
        for need in ("img/doudou_aftonsparv.webp", "img/doudou_boop.webp", "img/doudou_minou.webp", "img/doudou_moomoo.webp", "index.html", "assets/metro.svg", "manifest.webmanifest"):
            ok(need in files or ("" in files and need == "index.html"), "en cache : " + need)
        ok(any(f.startswith("fonts/") for f in files), "polices en cache")
        # visiter chaque page une fois en ligne (pour que le réseau soit « chaud »)
        pg.reload(); pg.wait_for_timeout(500)
        # ───── on coupe le serveur ─────
        srv.terminate(); srv.wait(timeout=5); time.sleep(0.5)
        try:
            import urllib.request
            urllib.request.urlopen(BASE, timeout=2); ok(False, "le serveur devrait être coupé")
        except Exception:
            ok(True, "serveur coupé")
        failed_req.clear()
        pg.reload(); pg.wait_for_timeout(900)
        ok(pg.title() != "", "la page recharge hors-ligne : « %s »" % pg.title())
        ok(pg.evaluate("document.querySelector('.view.on, .view:not([hidden])') !== null"), "une vue est affichée")

        def go(h, w=300):
            pg.evaluate("location.hash=%r" % h); pg.wait_for_timeout(w)

        def vis(sel):
            return pg.evaluate("(s)=>{const e=document.querySelector(s); return !!e && !e.hidden && e.offsetParent!==null}", sel)

        def imgs_ok(scope):
            return pg.evaluate("""(s)=>{const r=[...document.querySelectorAll(s+' img')].filter(i=>i.offsetParent!==null); return {n:r.length, bad:r.filter(i=>!(i.complete&&i.naturalWidth>0)).map(i=>i.getAttribute('src'))}}""", scope)
        # accueil : doudou
        go("#/", 500)
        r = imgs_ok("#v-home"); ok(r["n"] >= 1 and not r["bad"], "accueil : images OK %s" % r)
        ok(vis("#hq-q") and pg.inner_text("#hq-q") != "", "accueil : mot du doudou")
        # hub
        go("#/jeux"); ok(vis("#v-jeux"), "hub visible")
        r = imgs_ok("#v-jeux"); ok(r["n"] == 4 and not r["bad"], "hub : 4 doudous affichés %s" % r)
        # doudous
        go("#/doudous", 400); r = imgs_ok("#v-doudous"); ok(r["n"] >= 4 and not r["bad"], "doudous : images OK %s" % r)
        # quiz
        go("#/quiz"); pg.click('[data-qz="start"]'); pg.wait_for_timeout(120)
        for i in range(6):
            q = pg.locator(".qz-q").nth(i); q.locator(".qz-o").nth(1).click(); pg.wait_for_timeout(60); q.locator('[data-qz="next"]').click(); pg.wait_for_timeout(60)
        ok(vis("#qz-end"), "quiz hors-ligne : fin atteinte"); print("  score:", pg.inner_text("#qz-s"))
        # test du doudou
        go("#/test-doudou"); pg.click('[data-dt="start"]'); pg.wait_for_timeout(120)
        for i in range(10):
            pg.locator(".dt-q").nth(i).locator('.qz-o[data-who="minou"]').click(); pg.wait_for_timeout(40)
        ok(vis("#dt-res"), "test du doudou hors-ligne : résultat"); r = imgs_ok("#dt-res"); ok(r["n"] >= 1 and not r["bad"], "résultat : image OK %s" % r)
        # blind test
        go("#/blind-test"); pg.click('.bt-p[data-n="Daphne"] .bt-main'); ok(pg.inner_text('.bt-p[data-n="Daphne"] [data-score]') == "1", "blind test hors-ligne")
        # mots mêlés
        go("#/mots-meles", 500); ok(pg.locator("#mm-board span").count() == 400, "grille de 400 lettres : %d" % pg.locator("#mm-board span").count())
        # horoscope
        go("#/horoscope", 400); ok(pg.locator(".hs-top").count() == 12, "12 signes : %d" % pg.locator(".hs-top").count())
        # passeport + jour
        go("#/passeport", 400); ok(vis("#v-pass"), "passeport")
        st = json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')") or '{"d":[],"b":[]}')
        print("  tampons hors-ligne :", st)
        ok("quiz" in st["b"] and "doudou" in st["b"] and "blind" in st["b"], "tampons spéciaux gagnés hors-ligne")
        go("#/jours/2026-12-21", 400); pg.set_input_files('#d-2026-12-21 input[type=file] >> nth=1', "test_photo_0.jpg")
        for _ in range(250):
            st = json.loads(pg.evaluate("localStorage.getItem('carnet.stamps')"));
            if "2026-12-21" in st["d"]: break
            pg.wait_for_timeout(20)
        ok("2026-12-21" in st["d"], "photo + tampon du jour hors-ligne")
        # plan du métro (grosse image gardée en cache)
        go("#/metro", 500)
        pg.wait_for_timeout(500)
        ok(pg.evaluate("""()=>{return [...document.querySelectorAll('#v-metro svg')].some(s => s.querySelectorAll('*').length > 200)}"""), "plan du métro affiché hors-ligne")
        # polices
        fonts = pg.evaluate("""async () => { await document.fonts.ready; return ['Barlow','Barlow Condensed','Libre Baskerville','Noto Sans Thai'].map(f => [f, [...document.fonts].some(x => x.family.replace(/"/g,'') === f && x.status === 'loaded')]); }""")
        print("  polices chargées :", fonts)
        pg.screenshot(path=OUT + "s3_offline.png")
        # naviguer vers une page « profonde » directement hors-ligne
        pg.goto(BASE + "#/jeux"); pg.wait_for_timeout(500); ok(vis("#v-jeux"), "ouverture directe de #/jeux hors-ligne")
        pg.goto(BASE + "?utm=1#/passeport"); pg.wait_for_timeout(500); ok(vis("#v-pass"), "ouverture avec paramètre hors-ligne")
        b.close()
finally:
    try:
        srv.terminate()
    except Exception:
        pass
print("\n%d vérifications, %d échecs" % (n[0], len(fails)))
print("Requêtes échouées après coupure :", failed_req if failed_req else "aucune")
print("ERREURS JS:", errs if errs else "aucune")
