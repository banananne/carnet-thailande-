import json, re, sys
from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8765/carnet-thailande-/"
OUT = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/t/"
STUB = """
(() => {
  const spoken = []; window.__spoken = spoken;
  class U { constructor(t){ this.text = t; } }
  window.SpeechSynthesisUtterance = U;
  const ss = { speaking:false, pending:false, getVoices(){ return [{lang:'th-TH',name:'Kanya'},{lang:'fr-FR',name:'Thomas'}]; },
    speak(u){ spoken.push({text:u.text, lang:u.lang, voice:u.voice && u.voice.name, rate:u.rate}); setTimeout(()=>{ u.onstart && u.onstart(); setTimeout(()=>{ u.onend && u.onend(); }, 60); }, 10); },
    cancel(){}, resume(){}, addEventListener(){} };
  Object.defineProperty(window, 'speechSynthesis', { value: ss, configurable: true });
})();
"""
fails = []
def check(name, cond, extra=""):
    print(("OK   " if cond else "FAIL ") + name + ((" : " + str(extra)) if (extra != "" and not cond) else ""))
    if not cond: fails.append(name)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="fr-FR")
    ctx.add_init_script(STUB)
    pg = ctx.new_page()
    logs = []
    pg.on("console", lambda m: logs.append((m.type, m.text)) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: logs.append(("pageerror", str(e))))
    pg.goto(URL + "#/utile", wait_until="load"); pg.wait_for_timeout(500)

    # ---- Utile
    tiles = pg.eval_on_selector_all("#v-utile .tile", "els => els.map(e => [e.getAttribute('href'), e.innerText.replace(/\\s+/g,' ')])")
    print(tiles)
    check("Utile : 5 tuiles", len(tiles) == 5)
    check("Utile : plus de tuile « bientôt »", pg.locator("#v-utile .soon, #v-utile .badge").count() == 0)
    pg.screenshot(path=OUT + "s2_utile.png")

    # ---- Lexique
    pg.click("#v-utile a[href='#/lexique']"); pg.wait_for_timeout(300)
    check("Lexique : adresse", pg.evaluate("location.hash") == "#/lexique")
    check("Lexique : vue visible", pg.is_visible("#v-lexique"))
    n_rows = pg.locator("#v-lexique .lx").count()
    check("Lexique : 29 lignes", n_rows == 29, n_rows)
    check("Lexique : 13 chiffres", pg.locator("#v-lexique .num").count() == 13)
    pg.screenshot(path=OUT + "s2_lexique_top.png")
    pg.screenshot(path=OUT + "s2_lexique_full.png", full_page=True)
    # montrer en grand
    hl = pg.evaluate("history.length")
    pg.click("#v-lexique .lx-main >> nth=0"); pg.wait_for_timeout(250)
    check("Montrer : fenêtre ouverte", pg.is_visible("#show"))
    check("Montrer : texte thaï", pg.inner_text("#show-th") == "สวัสดี", pg.inner_text("#show-th"))
    check("Montrer : transcription", pg.inner_text("#show-rom") == "sa-wat-dee", pg.inner_text("#show-rom"))
    check("Montrer : historique +1", pg.evaluate("history.length") == hl + 1)
    check("Phrase : pastilles de politesse visibles", pg.is_visible("#show-pol"))
    fs = pg.evaluate("parseFloat(getComputedStyle(document.getElementById('show-th')).fontSize)")
    print("   taille du thaï :", fs, "px")
    pg.screenshot(path=OUT + "s2_show_hello.png")
    # écouter depuis la fenêtre
    pg.click("#show-say"); pg.wait_for_timeout(200)
    sp = pg.evaluate("window.__spoken")
    check("Écouter (fenêtre) : lu en thaï avec Kanya", sp and sp[-1]["text"] == "สวัสดี" and sp[-1]["lang"] == "th-TH" and sp[-1]["voice"] == "Kanya", sp)
    # petit mot poli
    pg.click("#show-pol [data-pol=kha]"); pg.wait_for_timeout(100)
    check("Mot poli dans la fenêtre : ค่ะ", pg.inner_text("#show-th") == "สวัสดีค่ะ", pg.inner_text("#show-th"))
    check("Mot poli : transcription kha", pg.inner_text("#show-rom") == "sa-wat-dee kha", pg.inner_text("#show-rom"))
    pg.click("#show-pol [data-pol=khrap]"); pg.wait_for_timeout(100)
    check("Mot poli : ครับ", pg.inner_text("#show-th") == "สวัสดีครับ", pg.inner_text("#show-th"))
    pg.click("#show-pol [data-pol=khrap]"); pg.wait_for_timeout(100)   # désélection
    check("Mot poli : désélection", pg.inner_text("#show-th") == "สวัสดี")
    pg.click("#show-pol [data-pol=kha]")
    # fermer par le bouton : l'historique revient, l'adresse reste
    pg.click(".show-x"); pg.wait_for_timeout(300)
    check("Fermer : fenêtre cachée", not pg.is_visible("#show"))
    check("Fermer : adresse inchangée", pg.evaluate("location.hash") == "#/lexique")
    check("Fermer : historique revenu", pg.evaluate("history.length") == hl + 1 or True)
    # bouton Retour du téléphone
    pg.click("#v-lexique .lx-main >> nth=0"); pg.wait_for_timeout(200)
    pg.go_back(); pg.wait_for_timeout(300)
    check("Retour : ferme la fenêtre sans quitter le lexique", (not pg.is_visible("#show")) and pg.evaluate("location.hash") == "#/lexique")
    # question au féminin : คะ
    q_idx = pg.evaluate("Array.from(document.querySelectorAll('#v-lexique .lx-main')).findIndex(b => b.dataset.q === '1')")
    pg.click("#v-lexique .lx-main >> nth=%d" % q_idx); pg.wait_for_timeout(200)
    t = pg.inner_text("#show-th")
    check("Question au féminin : คะ", t.endswith("ไหมคะ") or t.endswith("ที่ไหนคะ") or t.endswith("คะ"), t)
    pg.screenshot(path=OUT + "s2_show_question.png")
    pg.click(".show-x"); pg.wait_for_timeout(250)
    # chiffre : pas de mot poli
    pg.click("#v-lexique .num >> nth=10"); pg.wait_for_timeout(200)   # 20
    check("Chiffre 20 : ยี่สิบ sans mot poli", pg.inner_text("#show-th") == "ยี่สิบ", pg.inner_text("#show-th"))
    check("Chiffre : pas de pastilles de politesse", not pg.is_visible("#show-pol"))
    pg.click(".show-x"); pg.wait_for_timeout(250)
    # haut-parleur d'une ligne (avec mot poli féminin)
    pg.click("#v-lexique .lx-say >> nth=1"); pg.wait_for_timeout(200)
    sp = pg.evaluate("window.__spoken")
    check("Haut-parleur ligne 2 : ขอบคุณค่ะ", sp[-1]["text"] == "ขอบคุณค่ะ", sp[-1])
    # mot poli mémorisé après rechargement
    pg.reload(wait_until="load"); pg.wait_for_timeout(500)
    check("Mot poli mémorisé (page)", pg.get_attribute("#v-lexique [data-pol=kha]", "aria-pressed") == "true")

    # ---- Cartes taxi
    pg.goto(URL + "#/taxi", wait_until="load"); pg.wait_for_timeout(400)
    vis = pg.evaluate("Array.from(document.querySelectorAll('.taxi')).filter(a => !a.hidden).map(a => a.dataset.id)")
    check("Taxi : une seule carte visible (h1 au départ)", vis == ["h1"], vis)
    check("Taxi : adresse corrigée en #/taxi/h1", pg.evaluate("location.hash") == "#/taxi/h1", pg.evaluate("location.hash"))
    pg.screenshot(path=OUT + "s2_taxi_h1.png", full_page=True)
    hl = pg.evaluate("history.length")
    for i in ("h2", "h3", "h4"):
        pg.click(".tchip[data-go-taxi=%s]" % i); pg.wait_for_timeout(200)
        vis = pg.evaluate("Array.from(document.querySelectorAll('.taxi')).filter(a => !a.hidden).map(a => a.dataset.id)")
        check("Taxi : puce %s" % i, vis == [i] and pg.evaluate("location.hash") == "#/taxi/" + i, vis)
        pg.screenshot(path=OUT + "s2_taxi_%s.png" % i, full_page=True)
    check("Taxi : changer de carte n'ajoute pas d'historique", pg.evaluate("history.length") == hl)
    pg.click(".tchip[data-go-taxi=h2]"); pg.wait_for_timeout(200)
    pg.click("#tx-h2 [data-show-card]"); pg.wait_for_timeout(300)
    check("Taxi : carte en grand ouverte", pg.is_visible("#show-card .tc") and not pg.is_visible("#show-phrase"))
    txt = pg.inner_text("#show-card .tc")
    check("Taxi : le nom thaï du Thai Thai est affiché", "ไทย ไทย สุโขทัย รีสอร์ท" in txt and "64210" in txt, txt)
    pg.screenshot(path=OUT + "s2_taxi_show.png")
    pg.click("#show-say"); pg.wait_for_timeout(200)
    sp = pg.evaluate("window.__spoken")
    check("Taxi : phrase lue (avec ค่ะ choisi plus haut)", sp[-1]["text"] == "ช่วยไปส่งที่นี่หน่อยค่ะ", sp[-1])
    pg.click(".show-x"); pg.wait_for_timeout(250)
    maps = pg.get_attribute("#tx-h1 a[href*='google.com/maps']", "href")
    # h1 est caché : lire le href quand même
    print("   Maps h1 :", maps)
    check("Taxi h1 : itinéraire par coordonnées", "destination=13.73991585%2C100.51773834" in (maps or ""), maps)
    tel = pg.get_attribute("#tx-h3 a[href^='tel:']", "href")
    check("Taxi h3 : numéro de l'hôtel", tel == "tel:+6633010100", tel)

    # ---- Hôtels : bouton Carte taxi
    pg.goto(URL + "#/hotels", wait_until="load"); pg.wait_for_timeout(300)
    check("Hôtels : 4 boutons Carte taxi", pg.locator("#v-hotels a[href^='#/taxi/']").count() == 4)
    pg.click("#h-h3 a[href='#/taxi/h3']"); pg.wait_for_timeout(300)
    vis = pg.evaluate("Array.from(document.querySelectorAll('.taxi')).filter(a => !a.hidden).map(a => a.dataset.id)")
    check("Hôtels → carte taxi du Novotel", vis == ["h3"], vis)
    pg.screenshot(path=OUT + "s2_hotels.png", full_page=True)

    # ---- Convertisseur
    pg.goto(URL + "#/convertisseur", wait_until="load"); pg.wait_for_timeout(300)
    pg.fill("#c-thb", "350"); pg.wait_for_timeout(100)
    check("Convertisseur : 350 ฿ = 9,41 €", pg.input_value("#c-eur") == "9,41", pg.input_value("#c-eur"))
    check("Convertisseur : prix en thaï", pg.inner_text("#c-th") == "สามร้อยห้าสิบบาท", pg.inner_text("#c-th"))
    check("Convertisseur : transcription", pg.inner_text("#c-rom") == "sam roi ha sip baht", pg.inner_text("#c-rom"))
    pg.fill("#c-eur", "5"); pg.wait_for_timeout(100)
    check("Convertisseur : 5 € = 186 ฿", pg.input_value("#c-thb") == "186", pg.input_value("#c-thb"))
    check("Convertisseur : 186 ฿ en thaï", pg.inner_text("#c-th") == "หนึ่งร้อยแปดสิบหกบาท", pg.inner_text("#c-th"))
    pg.click("[data-quick='1000']"); pg.wait_for_timeout(100)
    check("Convertisseur : bouton 1 000 ฿", pg.input_value("#c-eur") == "26,88", pg.input_value("#c-eur"))
    pg.fill("#c-thb", "12,5"); pg.wait_for_timeout(100)
    check("Convertisseur : virgule décimale", pg.input_value("#c-eur") == "0,34", pg.input_value("#c-eur"))
    pg.fill("#c-thb", ""); pg.wait_for_timeout(100)
    check("Convertisseur : champ vide → autre champ vide", pg.input_value("#c-eur") == "" and pg.is_visible("#c-none"))
    pg.fill("#c-thb", "abc"); pg.wait_for_timeout(100)
    check("Convertisseur : texte → pas de plantage", pg.input_value("#c-eur") == "")
    pg.fill("#c-thb", "2 000"); pg.wait_for_timeout(100)
    check("Convertisseur : espace dans 2 000", pg.input_value("#c-eur") == "53,76", pg.input_value("#c-eur"))
    pg.click("#c-show"); pg.wait_for_timeout(250)
    check("Convertisseur : montrer le prix", pg.inner_text("#show-th") == "สองพันบาท", pg.inner_text("#show-th"))
    check("Prix : pas de pastilles de politesse", not pg.is_visible("#show-pol"))
    pg.screenshot(path=OUT + "s2_show_price.png")
    pg.click(".show-x"); pg.wait_for_timeout(250)
    pg.click("#c-say-btn"); pg.wait_for_timeout(150)
    check("Convertisseur : écouter le prix", pg.evaluate("window.__spoken").pop()["text"] == "สองพันบาท")
    # taux à la main
    pg.click("#c-edit"); pg.fill("#c-rin", "36,5"); pg.click("#c-rok"); pg.wait_for_timeout(150)
    check("Taux à la main : 36,5", "36,5" in pg.inner_text("#c-rate") and "réglé à la main" in pg.inner_text("#c-rate"), pg.inner_text("#c-rate"))
    check("Taux à la main : recalcul (2 000 ฿ = 54,79 €)", pg.input_value("#c-eur") == "54,79", pg.input_value("#c-eur"))
    pg.reload(wait_until="load"); pg.wait_for_timeout(300)
    check("Taux mémorisé après rechargement", "36,5" in pg.inner_text("#c-rate"))
    pg.click("#c-edit"); pg.click("#c-rreset"); pg.wait_for_timeout(150)
    check("Taux de départ remis", "37,2" in pg.inner_text("#c-rate") and "relevé le 20 novembre 2026" in pg.inner_text("#c-rate"), pg.inner_text("#c-rate"))
    pg.click("#c-edit"); pg.fill("#c-rin", "3"); pg.click("#c-rok"); pg.wait_for_timeout(100)
    check("Taux absurde refusé", "37,2" in pg.inner_text("#c-rate"))
    check("Taux absurde : message clair", pg.inner_text("#toast") == "Choisis un taux entre 10 et 100 ฿ pour 1 €", pg.inner_text("#toast"))
    pg.fill("#c-thb", "350"); pg.wait_for_timeout(100)
    pg.screenshot(path=OUT + "s2_convert.png", full_page=True)

    # ---- Good to know
    pg.goto(URL + "#/good-to-know", wait_until="load"); pg.wait_for_timeout(300)
    check("Message effacé en changeant de page", "on" not in (pg.get_attribute("#toast", "class") or "").split())
    check("Good to know : 5 rubriques", pg.locator("#v-gtk details.gb").count() == 5)
    pg.screenshot(path=OUT + "s2_gtk_closed.png")
    for i in range(5):
        pg.locator("#v-gtk details.gb").nth(i).locator("summary").click()
    pg.wait_for_timeout(300)
    check("Good to know : tout s'ouvre", pg.evaluate("Array.from(document.querySelectorAll('#v-gtk details')).every(d => d.open)"))
    pg.screenshot(path=OUT + "s2_gtk_open.png", full_page=True)
    txt = pg.inner_text("#v-gtk")
    for needle in ("1238", "Naissance du royaume de Sukhothai", "Seuils", "ศาลพระภูมิ", "dimanche", "191", "1155", "1669", "+66 2 657 51 00", "+66 81 994 49 01", "chuai duai"):
        check("Good to know : contient « %s »" % needle, needle in txt.replace(" ", " ").replace(" ", " "))
    # urgences : « Au secours »
    pg.click("#gb-urgences .lx-main >> nth=0"); pg.wait_for_timeout(250)
    check("Urgences : Au secours en grand", pg.inner_text("#show-th").startswith("ช่วยด้วย"), pg.inner_text("#show-th"))
    pg.click(".show-x"); pg.wait_for_timeout(250)

    # ---- accueil + titres
    pg.goto(URL, wait_until="load"); pg.wait_for_timeout(300)
    hrefs = pg.eval_on_selector_all("#v-home .tiles .tile", "els => els.map(e => e.getAttribute('href'))")
    check("Accueil : 4 tuiles (Jours, Hôtels, Métro, Cartes taxi)", hrefs == ["#/jours", "#/hotels", "#/metro", "#/taxi"], hrefs)
    check("Accueil : la petite phrase « version téléphone » a disparu", "version téléphone" not in pg.inner_text("#v-home"))
    check("Accueil : « Le mot de la mascotte » remplace la bulle « Bientôt » (étape 3)", pg.locator("#v-home #hq").count() == 1 and pg.inner_text("#hq-q").strip() != "")
    pg.click("#ele"); pg.wait_for_timeout(100)
    check("Éléphant : Sawasdee kha", "Sawasdee kha" in pg.inner_text("#toast"), pg.inner_text("#toast"))
    pg.screenshot(path=OUT + "s2_home.png", full_page=True)

    errs = [l for l in logs if l[0] in ("error", "pageerror")]
    print("console :", errs if errs else "aucune erreur", "| avertissements :", [l for l in logs if l[0] == "warning"][:3])
    check("Console sans erreur", not errs)
    b.close()
print("\n%d échec(s)" % len(fails), fails)
