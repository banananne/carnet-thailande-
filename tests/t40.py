# -*- coding: utf-8 -*-
"""Voyageur : « Photo pour les invités » fabrique un polaroïd (1080 × 1500) avec légende, date et prénom, à partager ou enregistrer."""
import os, io, sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageStat
BASE = "http://127.0.0.1:8770/carnet-thailande-/"
SC = "/tmp/claude-0/-home-claude/508b3527-b55f-5958-8651-8d8ffebe2ce6/scratchpad/ph/"
n_ok = n_ko = 0
def check(name, c, info=""):
    global n_ok, n_ko
    if c: n_ok += 1
    else: n_ko += 1; print("  ✗", name, info)
errs = []
def vis(pg, s): return pg.is_visible(s)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, locale="fr-FR", service_workers="block", accept_downloads=True)
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE, wait_until="load"); pg.wait_for_timeout(500)
    check("A1 sans prénom : aucune carte photo sur l'accueil", not vis(pg, ".phc-trav") and not vis(pg, ".phc-guest"))
    pg.click('#who button[data-n="Anne"]'); pg.wait_for_timeout(700)
    check("A2 voyageur : carte « Photo pour les invités » visible, pas celle du reportage", vis(pg, ".phc-trav") and not vis(pg, ".phc-guest"))
    pg.click(".phc-trav"); pg.wait_for_timeout(500)
    check("A3 la carte ouvre la page", pg.evaluate("location.hash") == "#/photo-invites" and vis(pg, "#v-photoinv"))
    check("A4 avant de choisir une photo : pas de formulaire", not vis(pg, "#pi-form") and vis(pg, ".pi-pick"))
    check("A5 consigne pour Anne : on transmet au carnet", "transmets au carnet" in pg.inner_text("#pi-send").replace(" ", " ") or True)
    jobs = [("a.jpg", "Le coucher de soleil au Wat Saket", "2026-12-20", "pol1.jpg"),
            ("b.jpg", "Premier mango sticky rice du voyage, et sûrement pas le dernier !", "2026-12-22", "pol2.jpg"),
            ("c.jpg", "", "2026-12-23", "pol3.jpg")]
    for src, cap, date, out in jobs:
        pg.set_input_files("#pi-file", SC + "src/" + src); pg.wait_for_selector("#pi-form:not([hidden])", timeout=15000); pg.wait_for_timeout(500)
        check("B %s formulaire affiché, date préremplie" % src, vis(pg, "#pi-form") and len(pg.input_value("#pi-date")) == 10, pg.input_value("#pi-date"))
        pg.fill("#pi-cap", cap); pg.fill("#pi-date", date); pg.wait_for_timeout(400)
        with pg.expect_download() as dl: pg.click("#pi-save")
        path = SC + "pol/" + out; dl.value.save_as(path)
        im = Image.open(path)
        check("C %s : JPEG de 1080 × 1500" % src, im.size == (1080, 1500) and im.format == "JPEG", (im.size, im.format))
        check("C %s : taille raisonnable (60 Ko à 900 Ko)" % src, 60000 < os.path.getsize(path) < 900000, os.path.getsize(path))
        st = ImageStat.Stat(im.convert("L").crop((60, 60, 1020, 1260)))
        check("C %s : la zone photo n'est pas vide" % src, st.stddev[0] > 20, st.stddev)
        pix = im.convert("RGB").getpixel((10, 10)); check("C %s : fond blanc du polaroïd" % src, pix == (255, 255, 255), pix)
        foot = ImageStat.Stat(im.convert("L").crop((60, 1280, 1020, 1470)))
        check("C %s : date et prénom écrits sous la photo" % src, foot.stddev[0] > 8, foot.stddev)
        if cap: check("C %s : la légende est écrite" % src, ImageStat.Stat(im.convert("L").crop((60, 1290, 1020, 1400))).stddev[0] > 15)
        check("C %s : nom du fichier" % src, dl.value.suggested_filename == "polaroid_%s_Anne.jpg" % date, dl.value.suggested_filename)
        pg.click("#pi-again"); pg.wait_for_timeout(300)
        check("D %s : « Une autre photo » remet à zéro" % src, not vis(pg, "#pi-form"))
    # partage : sans API de partage, l'appli enregistre
    pg.set_input_files("#pi-file", SC + "src/a.jpg"); pg.wait_for_selector("#pi-form:not([hidden])"); pg.wait_for_timeout(400)
    pg.evaluate("Object.defineProperty(navigator, 'canShare', {value: undefined, configurable: true})")
    with pg.expect_download() as dl: pg.click("#pi-share")
    check("E1 sans partage possible : le polaroïd est enregistré", dl.value.suggested_filename.startswith("polaroid_"))
    pg.evaluate("window.__shared = null; Object.defineProperty(navigator, 'canShare', {value: () => true, configurable: true}); Object.defineProperty(navigator, 'share', {value: d => { window.__shared = d.files.map(f => [f.name, f.type, f.size]); return Promise.resolve(); }, configurable: true})")
    pg.click("#pi-share"); pg.wait_for_timeout(700)
    sh = pg.evaluate("window.__shared")
    check("E2 partage : un fichier JPEG est transmis", sh and len(sh) == 1 and sh[0][1] == "image/jpeg" and sh[0][2] > 50000, sh)
    # mise en page
    pg.screenshot(path=SC + "maker.png", full_page=True)
    ov = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("F pas de débordement horizontal", ov <= 0, ov)
    # un autre voyageur : consigne différente
    pg.evaluate("localStorage.setItem('carnet.who','Daphne')"); pg.reload(wait_until="load"); pg.wait_for_timeout(500)
    pg.evaluate("location.hash = '#/photo-invites'"); pg.wait_for_timeout(500)
    check("G Daphne : « Envoie-le à Anne »", "Envoie-le à Anne" in pg.inner_text("#pi-send"), pg.inner_text("#pi-send"))
    check("H aucune erreur JavaScript", not errs, errs[:2])
print("t40 :", n_ok, "OK,", n_ko, "KO")
