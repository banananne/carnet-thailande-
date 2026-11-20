"""Vague 1 des améliorations d'Anne (22 h 47) : accueil allégé, « Qui es-tu ? » qui se replie, vocabulaire mascottes / test de personnalité."""
import json, re
from playwright.sync_api import sync_playwright
BASE = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
errs = []; fails = []; n = [0]

OVER = """() => {
  const de = document.documentElement, W = de.clientWidth, over = [];
  const clipped = (e) => { for (let a = e.parentElement; a && a !== document.body && a !== de; a = a.parentElement) { if (getComputedStyle(a).overflowX !== 'visible') return true; } return false; };
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


def ok(cond, msg):
    n[0] += 1
    if not cond:
        fails.append(msg); print("ÉCHEC:", msg)


with sync_playwright() as p:
    b = p.chromium.launch()
    for (vw, vh) in ((320, 640), (360, 740), (390, 844), (412, 915), (768, 1024)):
        tag = "%d" % vw
        ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=2 if vw in (320, 390) else 1, is_mobile=vw < 700, has_touch=True, locale="fr-FR", service_workers="block")
        pg = ctx.new_page()
        ctx.add_init_script("try{localStorage.setItem('carnet.open','1')}catch(e){}")  # le test de personnalité est ouvert (cadenas levé)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)

        def over(label):
            m = pg.evaluate(OVER)
            ok(m["sw"] <= m["cw"] and not m["over"], "[%s] débordement (%s) : %s" % (tag, label, m))

        def shot(name):
            if vw in (320, 390):
                pg.screenshot(path=OUT + "h_%s_%s.png" % (tag, name))

        # ── 1) première visite : bloc ouvert, accueil allégé
        pg.goto(BASE); pg.wait_for_timeout(350)
        ok(pg.is_visible("#who-box") and not pg.is_visible("#who-bar"), "[%s] 1re visite : « Qui es-tu ? » ouvert, ligne repliée cachée" % tag)
        ok(pg.locator("#v-home .hero .lead").count() == 0 and "version téléphone" not in pg.inner_text("#v-home"), "[%s] petite phrase « version téléphone » supprimée" % tag)
        hrefs = pg.eval_on_selector_all("#v-home .tiles .tile", "els => els.map(e => e.getAttribute('href'))")
        ok(hrefs == ["#/jours", "#/hotels", "#/metro", "#/taxi"], "[%s] 4 tuiles : %s" % (tag, hrefs))
        ok(pg.locator("#v-home #hq").count() == 1 and pg.inner_text("#hq-q").strip() != "", "[%s] mot de la mascotte présent" % tag)
        ok("mascotte" in pg.inner_text("#v-home .hq").lower() if pg.locator("#v-home .hq").count() else True, "[%s] bloc « mot de la mascotte »" % tag)
        over("accueil 1re visite"); shot("accueil_ouvert")
        # ── 2) choisir un prénom : « Bonjour Flo ! » puis repli automatique
        pg.click('#who button[data-n="Flo"]'); pg.wait_for_timeout(120)
        ok("Flo" in pg.inner_text("#hello") and pg.is_visible("#who-box"), "[%s] juste après le clic : message affiché, bloc encore ouvert" % tag)
        pg.wait_for_timeout(800)
        ok(not pg.is_visible("#who-box") and pg.is_visible("#who-bar"), "[%s] repli automatique du bloc" % tag)
        ok(pg.inner_text("#who-hi").strip() == "Bonjour Flo !", "[%s] ligne repliée : %r" % (tag, pg.inner_text("#who-hi")))
        ok(pg.inner_text("#who-av").strip() == "F", "[%s] pastille F : %r" % (tag, pg.inner_text("#who-av")))
        ok(pg.get_attribute("#who-bar", "aria-expanded") == "false", "[%s] aria-expanded=false une fois replié" % tag)
        ok(pg.evaluate("localStorage.getItem('carnet.who')") == "Flo", "[%s] prénom enregistré" % tag)
        ok(pg.evaluate("document.activeElement && document.activeElement.id") == "who-bar", "[%s] le focus passe sur la ligne repliée" % tag)
        ok(pg.evaluate("window.scrollY") == 0, "[%s] pas de saut de page au repli" % tag)
        over("accueil replié"); shot("accueil_replie")
        # ── 3) rouvrir / refermer
        pg.click("#who-bar"); pg.wait_for_timeout(150)
        ok(pg.is_visible("#who-box") and pg.get_attribute("#who-bar", "aria-expanded") == "true", "[%s] la ligne rouvre le bloc" % tag)
        pressed = pg.eval_on_selector_all('#who button[aria-pressed="true"]', "els => els.map(e => e.getAttribute('data-n'))")
        ok(pressed == ["Flo"], "[%s] Flo est coché à la réouverture : %s" % (tag, pressed))
        over("accueil rouvert"); shot("accueil_rouvert")
        pg.click("#who-bar"); pg.wait_for_timeout(150)
        ok(not pg.is_visible("#who-box") and pg.get_attribute("#who-bar", "aria-expanded") == "false", "[%s] la ligne referme le bloc" % tag)
        # ── 4) changer de prénom
        pg.click("#who-bar"); pg.wait_for_timeout(100)
        pg.click('#who button[data-n="Arthur"]'); pg.wait_for_timeout(900)
        ok(not pg.is_visible("#who-box") and pg.inner_text("#who-hi").strip() == "Bonjour Arthur !" and pg.inner_text("#who-av").strip() == "A",
           "[%s] changement de prénom → Arthur, replié : %r" % (tag, pg.inner_text("#who-hi")))
        ok(pg.evaluate("localStorage.getItem('carnet.who')") == "Arthur", "[%s] prénom Arthur enregistré" % tag)
        # ── 5) clavier : Entrée sur la ligne
        pg.focus("#who-bar"); pg.keyboard.press("Enter"); pg.wait_for_timeout(120)
        ok(pg.is_visible("#who-box"), "[%s] clavier : Entrée rouvre" % tag)
        pg.keyboard.press("Enter"); pg.wait_for_timeout(120)
        ok(not pg.is_visible("#who-box"), "[%s] clavier : Entrée referme" % tag)
        # ── 6) autre écran puis retour, puis rechargement : reste replié
        pg.evaluate("location.hash='#/jours'"); pg.wait_for_timeout(250)
        pg.evaluate("location.hash='#/'"); pg.wait_for_timeout(250)
        ok(pg.is_visible("#who-bar") and not pg.is_visible("#who-box"), "[%s] retour à l'accueil : toujours replié" % tag)
        pg.reload(); pg.wait_for_timeout(450)
        ok(pg.is_visible("#who-bar") and not pg.is_visible("#who-box") and pg.inner_text("#who-hi").strip() == "Bonjour Arthur !",
           "[%s] rechargement : replié et « Bonjour Arthur ! »" % tag)
        ok(not pg.evaluate("document.documentElement.classList.contains('has-who')"), "[%s] classe provisoire has-who retirée" % tag)
        over("accueil rechargé"); shot("accueil_recharge")
        # ── 7) prénom périmé (absent de la liste) : on redemande
        pg.evaluate("localStorage.setItem('carnet.who','Zoé')"); pg.reload(); pg.wait_for_timeout(450)
        ok(pg.is_visible("#who-box") and not pg.is_visible("#who-bar") and "Appuie" in pg.inner_text("#hello"), "[%s] prénom inconnu → le bloc reste ouvert" % tag)
        pg.evaluate("localStorage.removeItem('carnet.who')")
        ctx.close()

    # ── 8) avant l'exécution du script principal : pas de clignotement (script du bas retiré)
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, service_workers="block")
    pg = ctx.new_page()
    ctx.add_init_script("try{localStorage.setItem('carnet.open','1')}catch(e){}")  # le test de personnalité est ouvert (cadenas levé)
    ctx.add_init_script("try{localStorage.setItem('carnet.who','Daphne')}catch(e){}")

    def strip_main(route):
        r = route.fetch(); body = r.text()
        i = body.rindex("<script>")
        route.fulfill(response=r, body=body[:i] + "</body></html>", headers={**r.headers, "content-type": "text/html; charset=utf-8"})
    pg.route(re.compile(r".*/carnet-thailande-/(index\.html)?$"), strip_main)
    pg.goto(BASE); pg.wait_for_timeout(300)
    st = pg.evaluate("""() => { const b = document.getElementById('who-box'), a = document.getElementById('who-bar');
        return { cls: document.documentElement.classList.contains('has-who'), box: getComputedStyle(b).display, bar: getComputedStyle(a).display, vis: getComputedStyle(a).visibility, h: a.getBoundingClientRect().height, js: !!window.__x } }""")
    ok(st["cls"] and st["box"] == "none" and st["bar"] == "flex" and st["vis"] == "hidden" and st["h"] >= 56, "avant le script principal : bloc masqué, place réservée pour la ligne (%s)" % st)
    ctx.close()

    # ── 9) vocabulaire : anciens liens et nouveaux noms
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, service_workers="block")
    pg = ctx.new_page()
    ctx.add_init_script("try{localStorage.setItem('carnet.open','1')}catch(e){}")  # le test de personnalité est ouvert (cadenas levé)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(BASE); pg.wait_for_timeout(300)
    for h, view, ttl in (("#/personnalite", "#v-test", "Test de personnalité"), ("#/test-doudou", "#v-test", "Test de personnalité"),
                         ("#/mascottes", "#v-doudous", "Les mascottes"), ("#/doudous", "#v-doudous", "Les mascottes")):
        pg.evaluate("location.hash=%r" % h); pg.wait_for_timeout(250)
        ok(pg.is_visible(view) and ttl in pg.title(), "%s → %s (%r)" % (h, view, pg.title()))
    pg.evaluate("location.hash='#/jeux'"); pg.wait_for_timeout(250)
    hub = pg.inner_text("#v-jeux").lower()
    ok("test de personnalité" in hub and "les mascottes" in hub and "quelle mascotte es-tu ?" in hub, "hub Jeux : nouveaux noms")
    # plus aucun « doudou » dans les textes visibles, les alt, aria-label et title
    leaks = pg.evaluate("""() => { const out = [];
        document.querySelectorAll('main.view, nav, #toast, #show').forEach(v => { const t = v.textContent || ''; const m = t.match(/.{0,30}doudou.{0,30}/i); if (m) out.push((v.id || v.tagName) + ' : ' + m[0]); });
        document.querySelectorAll('[alt],[aria-label],[title],[placeholder]').forEach(e => ['alt','aria-label','title','placeholder'].forEach(a => { const v = e.getAttribute(a); if (v && /doudou/i.test(v)) out.push(a + '=' + v); }));
        return out; }""")
    ok(not leaks, "aucun « doudou » visible ou lu à voix haute : %s" % leaks)
    ok(pg.evaluate("[...document.querySelectorAll('.tile,.hub a,.hubtile')].every(e => !/doudou/i.test(e.textContent))"), "tuiles : pas de « doudou »")
    ctx.close()
    b.close()
print("\n%d vérifications, %d échecs" % (n[0], len(fails)))
print("ERREURS JS:", errs if errs else "aucune")
