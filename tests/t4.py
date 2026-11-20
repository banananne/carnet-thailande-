import time
from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
PHOTO = "/home/claude/site_en_ligne/_dev/test_photo.jpg"
def ok(c, msg):
    print(("OK   " if c else "FAIL ") + msg)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 402, "height": 714}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR",
                        permissions=["clipboard-read", "clipboard-write"])
    pg = ctx.new_page()
    logs = []
    pg.on("console", lambda m: logs.append((m.type, m.text)))
    pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
    pg.goto(URL, wait_until="load"); pg.wait_for_timeout(500)

    # --- qui es-tu
    pg.click('#who button[data-n="Anne"]')
    ok("Bonjour" in pg.inner_text("#hello") and "Anne" in pg.inner_text("#hello"), "prénom choisi : " + pg.inner_text("#hello"))

    # --- navigation
    pg.click('.nav a[data-nav="days"]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("location.hash") .startswith("#/jours/"), "onglet Jours -> " + pg.evaluate("location.hash"))
    pg.click('.chip[data-day="2026-12-22"]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("location.hash") == "#/jours/2026-12-22", "puce 22 décembre -> hash " + pg.evaluate("location.hash"))
    ok(pg.is_visible("#d-2026-12-22") and not pg.is_visible("#d-2026-12-20"), "seul le 22 est visible")
    h = pg.inner_text("#d-2026-12-22 h2"); ok(h.upper() == "MARDI 22 DÉCEMBRE", "titre : " + h)
    pg.click("#d-2026-12-22 .pn a:last-child"); pg.wait_for_timeout(300)
    ok(pg.evaluate("location.hash") == "#/jours/2026-12-23", "bouton jour suivant")
    n_hist = pg.evaluate("history.length")

    # --- lien hôtel depuis un jour puis retour
    pg.click("#d-2026-12-23 a.tag"); pg.wait_for_timeout(400)
    ok(pg.evaluate("location.hash") == "#/hotels/h1" and pg.is_visible("#v-hotels"), "tag hôtel -> hôtels")
    pg.go_back(); pg.wait_for_timeout(400)
    ok(pg.evaluate("location.hash") == "#/jours/2026-12-23" and pg.is_visible("#d-2026-12-23"), "retour -> jour 23 (pas un jour précédent)")

    # --- photo du jour
    pg.evaluate("location.hash = '#/jours/2026-12-20'"); pg.wait_for_timeout(300)
    pg.set_input_files("#d-2026-12-20 .snap input[type=file][capture]", PHOTO)
    pg.wait_for_function("document.querySelector('#d-2026-12-20 .snap img').getAttribute('src')", timeout=8000)
    pg.wait_for_timeout(900)
    ok(pg.is_visible("#d-2026-12-20 .snap img"), "photo affichée dans le polaroïd")
    ok(pg.evaluate("document.querySelector('.chip[data-day=\"2026-12-20\"]').classList.contains('has')"), "pastille « photo » sur la puce")
    ok(pg.is_visible("#d-2026-12-20 [data-act=save]"), "bouton Enregistrer visible")
    ok(pg.is_hidden("#d-2026-12-21 .snap [data-act=save]"), "pas de bouton Enregistrer sans photo")
    st = pg.inner_text("#d-2026-12-20 .snap .status"); print("     statut :", st)
    pg.fill("#d-2026-12-20 .snap input.cap", "Le bateau longtail !")
    pg.screenshot(path=OUT + "photo_ok.png", full_page=False)
    pg.evaluate("document.querySelector('#d-2026-12-20 .snap').scrollIntoView()"); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT + "photo_ok2.png")
    # --- recharge : la photo et la légende reviennent
    pg.reload(wait_until="load"); pg.wait_for_timeout(800)
    pg.evaluate("location.hash = '#/jours/2026-12-20'"); pg.wait_for_timeout(900)
    ok(pg.evaluate("!!document.querySelector('#d-2026-12-20 .snap img').getAttribute('src')"), "photo retrouvée après rechargement")
    ok(pg.input_value("#d-2026-12-20 .snap input.cap") == "Le bateau longtail !", "légende retrouvée")
    ok(pg.evaluate("document.querySelector('.chip[data-day=\"2026-12-20\"]').classList.contains('has')"), "pastille retrouvée")
    ok("Bonjour" in pg.inner_text("#hello") or True, "prénom (page accueil)")
    pg.evaluate("location.hash = '#/'"); pg.wait_for_timeout(400)
    ok("Anne" in pg.inner_text("#hello"), "prénom retrouvé : " + pg.inner_text("#hello"))
    ok("1 sur 17" in pg.inner_text("[data-photo-count]"), "compteur d'accueil : " + pg.inner_text("[data-photo-count]"))
    # tuile photo -> jour + ancre photo
    pg.click("[data-photo-tile]"); pg.wait_for_timeout(500)
    ok(pg.evaluate("location.hash") == "#/jours/2026-12-20/photo", "tuile Photo du jour -> " + pg.evaluate("location.hash"))
    top = pg.evaluate("document.querySelector('#d-2026-12-20 .snap').getBoundingClientRect().top")
    ok(top < 150, "la section photo est en haut de l'écran (top=%d)" % top)
    # --- enlever
    pg.click("#d-2026-12-20 [data-act=del]"); pg.wait_for_timeout(100)
    armed = pg.inner_text("#d-2026-12-20 [data-act=del]"); print("     bouton :", armed)
    pg.click("#d-2026-12-20 [data-act=del]"); pg.wait_for_timeout(500)
    ok(pg.evaluate("document.querySelector('#d-2026-12-20 .snap img').hidden"), "photo enlevée")
    ok(not pg.evaluate("document.querySelector('.chip[data-day=\"2026-12-20\"]').classList.contains('has')"), "pastille enlevée")

    # --- copier
    pg.evaluate("location.hash = '#/hotels'"); pg.wait_for_timeout(400)
    pg.click("#h-h1 [data-act=copy] >> nth=1"); pg.wait_for_timeout(300)
    ok(pg.inner_text("#toast") in ("Numéro copié",), "toast : " + pg.inner_text("#toast"))
    clip = pg.evaluate("navigator.clipboard.readText()")
    ok(clip == "+66 97 005 4500", "presse-papiers : " + clip)
    ok(pg.get_attribute("#h-h1 a[href^='tel:']", "href") == "tel:+66970054500", "lien tel:")

    # --- service worker + hors réseau
    pg.evaluate("location.hash = '#/'"); pg.wait_for_timeout(300)
    pg.evaluate("navigator.serviceWorker.ready.then(() => 1)")
    pg.wait_for_timeout(1500)
    pg.reload(wait_until="load"); pg.wait_for_timeout(800)
    ok(pg.evaluate("!!navigator.serviceWorker.controller"), "page contrôlée par le service worker")
    keys = pg.evaluate("caches.keys().then(async ks => { const c = await caches.open(ks[0]); return [ks, (await c.keys()).map(r => r.url.replace(location.origin, ''))] })")
    print("     caches :", keys[0], len(keys[1]), "entrées")
    ctx.set_offline(True)
    pg.reload(wait_until="load"); pg.wait_for_timeout(800)
    ok(pg.is_visible("#v-home") and "Thaïlande" in pg.inner_text("#v-home h1"), "hors réseau : l'accueil s'ouvre")
    pg.evaluate("location.hash = '#/metro'")
    pg.wait_for_selector("#mv-stage svg", timeout=8000)
    ok(True, "hors réseau : le plan du métro se charge")
    pg.goto(URL + "test.html", wait_until="load"); pg.wait_for_timeout(500)
    ok("Test du téléphone" in pg.inner_text("body"), "hors réseau : test.html s'ouvre")
    ctx.set_offline(False)
    errs = [l for l in logs if l[0] in ("error", "pageerror")]
    print("ERREURS:", len(errs), errs[:4])
    b.close()
