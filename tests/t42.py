# -*- coding: utf-8 -*-
"""Mode Supabase (faux serveur) : un voyageur publie, un·e invité·e voit, retrait, erreurs, lignes parasites."""
import json, urllib.request, sys
from playwright.sync_api import sync_playwright
SITE = "http://127.0.0.1:8781/carnet-thailande-/"
SB = "http://127.0.0.1:8780"
ROOT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/"
POL = ROOT + "ph/pol/pol%d.jpg"
n_ok = n_ko = 0
def check(name, c, info=""):
    global n_ok, n_ko
    if c: n_ok += 1
    else: n_ko += 1; print("  ✗", name, info)
sp = lambda s: s.replace(" ", " ").replace(" ", " ")
errs = []
def ctl(p): return json.load(urllib.request.urlopen(SB + p))
def newpg(b, who, vw=390):
    ctx = b.new_context(viewport={"width": vw, "height": 844}, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block")
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(SITE, wait_until="load"); pg.evaluate("localStorage.setItem('carnet.who','%s')" % who); pg.reload(wait_until="load"); pg.wait_for_timeout(500)
    return ctx, pg
def photo_page(pg, img):
    pg.evaluate("location.hash = '#/photo-invites'"); pg.wait_for_timeout(500)
    pg.set_input_files("#pi-file", img); pg.wait_for_timeout(900)
ctl("/__ctl/reset")
with sync_playwright() as p:
    b = p.chromium.launch()
    # ───── voyageur : publier ─────
    ctx, pg = newpg(b, "Daphne")
    photo_page(pg, POL % 1)
    check("A1 bouton « Publier » visible en mode Supabase", pg.is_visible("#pi-publish") and "Publier chez les invit" in sp(pg.inner_text("#pi-publish")))
    check("A2 sans code : le champ de code est proposé", pg.is_visible("#pi-code-box"))
    pg.fill("#pi-cap", "Le marché de nuit"); pg.wait_for_timeout(200)
    pg.click("#pi-publish"); pg.wait_for_timeout(400)
    check("A3 publier sans code : rien n'est envoyé, message", "code" in sp(pg.inner_text("#pi-pst")) and ctl("/__ctl/state")["obj"] == [], pg.inner_text("#pi-pst"))
    pg.fill("#pi-code", "mauvais-0000"); pg.click("#pi-code-ok"); pg.wait_for_timeout(2500)
    check("A4 mauvais code refusé", "pas le bon code" in sp(pg.inner_text("#pi-pst")) and pg.is_visible("#pi-code-box"), pg.inner_text("#pi-pst"))
    pg.fill("#pi-code", " ESSAI 1234 "); pg.click("#pi-code-ok"); pg.wait_for_timeout(2500)
    check("A5 bon code : validé, champ replié", "validé" in sp(pg.inner_text("#pi-pst")).lower() and not pg.is_visible("#pi-code-box"), pg.inner_text("#pi-pst"))
    check("A6 code gardé (normalisé)", pg.evaluate("localStorage.getItem('carnet.rep.code')") == "essai1234")
    pg.click("#pi-publish"); pg.wait_for_timeout(1500)
    s = ctl("/__ctl/state")
    check("A7 un fichier + une ligne côté serveur", len(s["obj"]) == 1 and len(s["rows"]) == 1, s["obj"])
    check("A8 bouton « Publié ✓ » et message", "Publié" in sp(pg.inner_text("#pi-publish")) and pg.is_disabled("#pi-publish"), pg.inner_text("#pi-publish"))
    f = s["obj"][0]; raw = urllib.request.urlopen(SB + "/storage/v1/object/public/reportage/" + f).read()
    check("A9 le fichier stocké est chiffré (pas un JPEG) et assez gros", raw[:3] != b"\xff\xd8\xff" and len(raw) > 20000, raw[:4])
    meta = s["rows"][0]["meta"]
    check("A10 la description est chiffrée (ni légende ni prénom lisibles)", "marché" not in meta and "Daphne" not in meta and "2026" not in meta)
    check("A11 le jeton de retrait n'est PAS envoyé au serveur (seulement son empreinte)", len(s["rows"][0]["del_hash"]) == 64 and "token" not in json.dumps(s["rows"][0]))
    mine = json.loads(pg.evaluate("localStorage.getItem('carnet.rep.mine')"))
    check("A12 « Mes polaroïds publiés » : 1 ligne", pg.is_visible("#pi-mine") and pg.locator("#pi-mine li").count() == 1 and len(mine) == 1 and mine[0]["token"] not in json.dumps(s))
    pg.fill("#pi-cap", "autre légende"); pg.wait_for_timeout(300)
    check("A13 modifier le polaroïd réactive « Publier »", not pg.is_disabled("#pi-publish"))
    ctx.close()
    # ───── invité·e : voir ─────
    ctx, pg = newpg(b, "Invité")
    pg.evaluate("location.hash = '#/reportage'"); pg.wait_for_timeout(1200)
    check("B1 code demandé", pg.is_visible("#rp-lock") and pg.locator("#rp-feed figure").count() == 0)
    pg.fill("#rp-code", "faux-1111"); pg.click("#rp-form button"); pg.wait_for_timeout(2500)
    check("B2 mauvais code refusé", "pas le bon code" in sp(pg.inner_text("#rp-err")), pg.inner_text("#rp-err"))
    pg.fill("#rp-code", "essai 1234"); pg.click("#rp-form button"); pg.wait_for_timeout(3500)
    check("B3 bon code : 1 polaroïd", pg.locator("#rp-feed figure").count() == 1 and not pg.is_visible("#rp-lock"), pg.locator("#rp-feed figure").count())
    nat = pg.eval_on_selector_all("#rp-feed figure img", "els => els.map(e => [e.naturalWidth, e.naturalHeight])")
    check("B4 la photo est déchiffrée et affichée (1080 × 1500)", nat == [[1080, 1500]], nat)
    alt = pg.eval_on_selector_all("#rp-feed figure img", "els => els.map(e => e.alt)")[0]
    check("B5 prénom et légende (celle du moment de la publication)", "Daphne" in alt and "marché" in alt, alt)
    # un 2e voyageur publie pendant que l'invité·e regarde : arrive tout seul (rafraîchissement)
    ctx2, pg2 = newpg(b, "Flo"); pg2.evaluate("localStorage.setItem('carnet.rep.code','essai1234')"); pg2.reload(wait_until="load"); pg2.wait_for_timeout(500)
    photo_page(pg2, POL % 2); pg2.fill("#pi-cap", "Pad thaï"); pg2.wait_for_timeout(200); pg2.wait_for_timeout(1500)
    check("C1 code déjà gardé : pas de champ de code", not pg2.is_visible("#pi-code-box"))
    pg2.click("#pi-publish"); pg2.wait_for_timeout(1500)
    check("C2 deux fichiers côté serveur", len(ctl("/__ctl/state")["obj"]) == 2)
    pg.evaluate("location.hash = '#/jours'"); pg.wait_for_timeout(300); pg.evaluate("location.hash = '#/reportage'"); pg.wait_for_timeout(3500)
    check("C3 l'invité·e retrouve les deux polaroïds en revenant sur la page", pg.locator("#rp-feed figure").count() == 2, pg.locator("#rp-feed figure").count())
    # lignes parasites : une ligne illisible + un fichier bidon ne cassent rien
    junk = json.dumps({"id": "00000000-0000-4000-8000-000000000001", "f": "pdeadbeef0001", "meta": "AAAA", "del_hash": "0" * 64}).encode()
    urllib.request.urlopen(urllib.request.Request(SB + "/rest/v1/reportage", data=junk, method="POST", headers={"apikey": "sb_publishable_test", "Content-Type": "application/json"}))
    pg.evaluate("location.hash = '#/jours'"); pg.wait_for_timeout(300); pg.evaluate("location.hash = '#/reportage'"); pg.wait_for_timeout(3500)
    check("C4 une ligne illisible (faux envoi) est ignorée", pg.locator("#rp-feed figure").count() == 2, pg.locator("#rp-feed figure").count())
    # retrait par le voyageur
    pg3 = pg2
    pg3.evaluate("location.hash = '#/jours'"); pg3.wait_for_timeout(300); photo_page(pg3, POL % 2)
    check("D1 Flo voit sa ligne « Mes polaroïds publiés »", pg3.locator("#pi-mine li").count() == 1)
    pg3.click("#pi-mine li button"); pg3.wait_for_timeout(300)
    check("D2 premier toucher : demande confirmation, rien retiré", "Retirer ?" in sp(pg3.inner_text("#pi-mine li button")) and len(ctl("/__ctl/state")["rows"]) == 3)
    pg3.click("#pi-mine li button"); pg3.wait_for_timeout(1200)
    check("D3 second toucher : ligne retirée côté serveur", len(ctl("/__ctl/state")["rows"]) == 2 and pg3.locator("#pi-mine li").count() == 0, len(ctl("/__ctl/state")["rows"]))
    pg.evaluate("location.hash = '#/jours'"); pg.wait_for_timeout(300); pg.evaluate("location.hash = '#/reportage'"); pg.wait_for_timeout(3500)
    check("D4 l'invité·e ne voit plus le polaroïd retiré", pg.locator("#rp-feed figure").count() == 1, pg.locator("#rp-feed figure").count())
    # mauvais jeton : rien retiré
    r = urllib.request.urlopen(urllib.request.Request(SB + "/rest/v1/rpc/retirer_photo", data=json.dumps({"p_id": ctl("/__ctl/state")["rows"][0]["id"], "p_token": "x"}).encode(), method="POST", headers={"apikey": "sb_publishable_test", "Content-Type": "application/json"}))
    check("D5 un mauvais jeton ne retire rien", r.read() == b"false" and len(ctl("/__ctl/state")["rows"]) == 2)
    # panne à la publication
    photo_page(pg3, POL % 3); pg3.fill("#pi-cap", "Panne"); pg3.wait_for_timeout(300)
    nrows = len(ctl("/__ctl/state")["rows"]); ctl("/__ctl/fail?n=1")
    pg3.click("#pi-publish"); pg3.wait_for_timeout(1500)
    check("E1 panne : message clair, rien d'ajouté, bouton réutilisable", "pas marché" in sp(pg3.inner_text("#pi-pst")) and len(ctl("/__ctl/state")["rows"]) == nrows and not pg3.is_disabled("#pi-publish"), pg3.inner_text("#pi-pst"))
    pg3.click("#pi-publish"); pg3.wait_for_timeout(1500)
    check("E2 nouvel essai : publié", len(ctl("/__ctl/state")["rows"]) == nrows + 1 and "Publié" in sp(pg3.inner_text("#pi-publish")))
    # oublier le code côté invité·e
    pg.click("#rp-forget"); pg.wait_for_timeout(400)
    check("F1 « Oublier le code » : verrouillé", pg.is_visible("#rp-lock") and pg.locator("#rp-feed figure").count() == 0)
    # réseau absent côté invité·e : message, pas d'erreur
    pg.fill("#rp-code", "essai1234"); ctx.set_offline(True); pg.click("#rp-form button"); pg.wait_for_timeout(2500)
    check("F2 hors ligne : message de réseau", "réseau" in sp(pg.inner_text("#rp-err")), pg.inner_text("#rp-err"))
    ctx.set_offline(False)
    ov = pg3.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("G1 pas de débordement horizontal (page de publication)", ov <= 0, ov)
    pg3.screenshot(path=ROOT + "ph/cloud_publish.png", full_page=True)
    ctx.close(); ctx2.close(); b.close()
check("Z0 aucune erreur JavaScript", not errs, errs)
print("t42 : %d OK, %d échecs" % (n_ok, n_ko))
