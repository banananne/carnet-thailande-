# -*- coding: utf-8 -*-
"""Assemble le « vrai site » du carnet (dossier web/, prêt pour GitHub Pages).

Entrées : template.html (HTML + CSS + JS), autocollants SVG de /home/claude/lexique/out/stickers_playlist/,
          polices @fontsource installées dans _dev/node_modules.
Sorties : web/index.html, web/manifest.webmanifest, web/sw.js, web/robots.txt, web/.nojekyll,
          web/fonts/*.woff2, web/icons/*.png|svg
Le fichier index.html à la racine (site_en_ligne/index.html) est la copie publiée en Artifact (v0.3) : on n'y touche plus."""
import re, os, shutil, subprocess, time

ROOT = "/home/claude/site_en_ligne"
WEB = os.environ.get("CARNET_WEB") or os.path.join(ROOT, "web")     # CARNET_WEB : dossier de sortie des essais (le vrai reste web/)
STK = "/home/claude/lexique/out/stickers_playlist"
NM = os.path.join(ROOT, "_dev", "node_modules", "@fontsource")

ICONS = {
    "camera": '<path d="M4 8h3l1.6-2.4h6.8L17 8h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13" r="3.6"/>',
    "image": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="M4 18l5-5 4 4 3-3 4 4"/>',
    "pin": '<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>',
    "go": '<path d="M5 12h13M13 6l6 6-6 6"/>',
    "speaker": '<path d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M17.8 6.8a7.2 7.2 0 0 1 0 10.4"/>',
    "save": '<path d="M12 4v11M7.5 11 12 15.5 16.5 11M5 19.5h14"/>',
    "memory": '<ellipse cx="12" cy="6" rx="7" ry="2.6"/><path d="M5 6v6c0 1.5 3.1 2.6 7 2.6s7-1.1 7-2.6V6M5 12v6c0 1.5 3.1 2.6 7 2.6s7-1.1 7-2.6v-6"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "train": '<rect x="5" y="3.5" width="14" height="13" rx="3"/><path d="M5 11h14M9 20l-2 1.5M15 20l2 1.5"/><circle cx="9" cy="14" r=".6"/><circle cx="15" cy="14" r=".6"/>',
    "star": '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 16.9 6.8 19.7l1-5.9L3.5 9.7l5.9-.8L12 3.5z"/>',
    "book": '<path d="M5 4.5h10a3 3 0 0 1 3 3V20H8a3 3 0 0 1-3-3V4.5z"/><path d="M8 17h10"/>',
    "car": '<path d="M5 15.5V12l1.8-4.6A1.5 1.5 0 0 1 8.2 6.5h7.6a1.5 1.5 0 0 1 1.4.9L19 12v3.5M4 15.5h16v3H4z"/><circle cx="8" cy="15.5" r=".5"/><circle cx="16" cy="15.5" r=".5"/>',
    "coin": '<circle cx="12" cy="12" r="8"/><path d="M14.5 9.2c-.5-.8-1.5-1.2-2.5-1.2-1.4 0-2.5.8-2.5 2s1 1.7 2.5 2 2.5.8 2.5 2-1.1 2-2.5 2c-1 0-2-.4-2.5-1.2M12 6.5V8M12 16v1.5"/>',
    "home": '<path d="M4 11.2 12 4.5l8 6.7V19a1 1 0 0 1-1 1h-4.2v-5.6H9.2V20H5a1 1 0 0 1-1-1z"/>',
    "wifioff": '<path d="M3.5 9.2a13 13 0 0 1 17 0M6.6 12.6a8.6 8.6 0 0 1 10.8 0M9.6 15.9a4.2 4.2 0 0 1 4.8 0"/><circle cx="12" cy="19" r=".9"/><path d="M4 4l16 16"/>',
    "bed": '<path d="M3.5 18.5V6.5M3.5 14.5h17v4M20.5 14.5V12a2.5 2.5 0 0 0-2.5-2.5h-6.5v5"/><circle cx="7.5" cy="11.2" r="1.7"/>',
    "compass": '<circle cx="12" cy="12" r="8.5"/><path d="m15.7 8.3-2.2 5.2-5.2 2.2 2.2-5.2z"/>',
    "phone": '<path d="M6.6 3.8h3l1.4 4-2 1.3a10 10 0 0 0 4.6 4.6l1.3-2 4 1.4v3a2 2 0 0 1-2.2 2A15.5 15.5 0 0 1 4.6 6 2 2 0 0 1 6.6 3.8z"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.6 7.2 8.4 6.3 8.4-6.3"/>',
    "copy": '<rect x="8.5" y="8.5" width="11" height="11" rx="2"/><path d="M15.5 8.5v-1.8a2 2 0 0 0-2-2H6.7a2 2 0 0 0-2 2v6.8a2 2 0 0 0 2 2h1.8"/>',
    "plus": '<path d="M12 5.5v13M5.5 12h13"/>',
    "minus": '<path d="M5.5 12h13"/>',
    "fit": '<path d="M4 9V5h4M20 9V5h-4M4 15v4h4M20 15v4h-4"/>',
    "chevl": '<path d="m14.5 6-6 6 6 6"/>',
    "chevr": '<path d="m9.5 6 6 6-6 6"/>',
    "route": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h6.5a3 3 0 0 0 0-6h-5a3 3 0 0 1 0-6H16"/>',
    "info": '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5.5M12 7.8v.2"/>',
    "pen": '<path d="M4 20l1-4L16.5 4.5a2 2 0 0 1 2.8 0l.2.2a2 2 0 0 1 0 2.8L8 19l-4 1z"/><path d="M14.5 6.5l3 3"/>',
    "trash": '<path d="M4.5 7h15M9.5 7V4.5h5V7M6.5 7l.8 12.5h9.4L17.5 7M10 11v5M14 11v5"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "x": '<path d="M6 6l12 12M18 6 6 18"/>',
    "dice": '<rect x="4" y="4" width="16" height="16" rx="4"/><circle cx="8.8" cy="8.8" r=".7"/><circle cx="15.2" cy="8.8" r=".7"/><circle cx="12" cy="12" r=".7"/><circle cx="8.8" cy="15.2" r=".7"/><circle cx="15.2" cy="15.2" r=".7"/>',
    "question": '<circle cx="12" cy="12" r="8.5"/><path d="M9.5 9.8a2.6 2.6 0 1 1 3.7 2.3c-.8.5-1.2 1-1.2 1.9M12 16.8v.1"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="9.5" rx="2.2"/><path d="M8.2 10.5V8a3.8 3.8 0 0 1 7.6 0v2.5"/><circle cx="12" cy="15.2" r=".9"/>',
    "heart": '<path d="M12 19.5s-7-4.4-7-9.6A3.9 3.9 0 0 1 12 7.6a3.9 3.9 0 0 1 7 2.3c0 5.2-7 9.6-7 9.6z"/>',
    "music": '<path d="M9 17.5V6.5l9-2v11"/><circle cx="6.8" cy="17.5" r="2.2"/><circle cx="15.8" cy="15.5" r="2.2"/>',
    "grid": '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9.3 4v16M14.7 4v16M4 9.3h16M4 14.7h16"/>',
    "stamp": '<path d="M9 13.5h6l-.8-3.4a2.4 2.4 0 1 0-4.4 0z"/><path d="M6.2 13.5h11.6a1.7 1.7 0 0 1 1.7 1.7v1.3h-15v-1.3a1.7 1.7 0 0 1 1.7-1.7zM5 20h14"/>',
    "paw": '<ellipse cx="12" cy="15.6" rx="4.2" ry="3.3"/><circle cx="6.4" cy="11.2" r="1.8"/><circle cx="9.9" cy="6.9" r="1.8"/><circle cx="14.1" cy="6.9" r="1.8"/><circle cx="17.6" cy="11.2" r="1.8"/>',
    "refresh": '<path d="M19 12a7 7 0 1 1-2.2-5.1M19 4.5V8h-3.5"/>',
    "bulb": '<path d="M9.6 17.5h4.8M10.2 20h3.6M12 3.8a5.2 5.2 0 0 0-3.1 9.4c.7.6 1.1 1.3 1.1 2.3h4c0-1 .4-1.7 1.1-2.3A5.2 5.2 0 0 0 12 3.8z"/>',
    "zoomin": '<circle cx="10.5" cy="10.5" r="5.5"/><path d="m15 15 5 5M10.5 8v5M8 10.5h5"/>',
    # étape 4 : jeux du jour et traducteur
    "speech": '<path d="M5 5h14a1.5 1.5 0 0 1 1.5 1.5v8A1.5 1.5 0 0 1 19 16h-7l-4.5 3.8V16H5a1.5 1.5 0 0 1-1.5-1.5v-8A1.5 1.5 0 0 1 5 5z"/><path d="M8.2 10.6v.1M12 10.6v.1M15.8 10.6v.1"/>',
    "fork": '<path d="M7 3.5v6a2.2 2.2 0 0 0 2.2 2.2H10V20.5M4.6 3.5v6a2.4 2.4 0 0 0 2.4 2.2M9.4 3.5v8.2"/><path d="M17.5 20.5V3.5c-2.2 1.3-3.4 4-3.4 7 0 1.7.8 2.7 2 2.7h1.4"/>',
    "award": '<circle cx="12" cy="9.2" r="5.4"/><path d="m8.9 13.6-1.6 7 4.7-2.5 4.7 2.5-1.6-7"/><path d="m12 6.6.9 1.8 2 .3-1.4 1.4.3 2-1.8-.9-1.8.9.3-2-1.4-1.4 2-.3z"/>',
    "bingo": '<rect x="4" y="3.5" width="16" height="17" rx="2.6"/><path d="M4 8.7h16M9.3 8.7v11.8M14.7 8.7v11.8M4 14.6h16"/><path d="m10.4 12.2.9.9 1.6-1.8"/>',
    "translate": '<path d="M3.5 6h9M8 4v2M5.4 6c.6 3.2 2.7 5.6 5.4 7M11.3 6c-.8 3.4-3.3 6-6.6 7.4"/><path d="m13.2 20.5 3.8-9 3.8 9M14.6 17.5h4.8"/>',
    "unlock": '<rect x="5" y="10.5" width="14" height="9.5" rx="2.2"/><path d="M8.2 10.5V8a3.8 3.8 0 0 1 7.2-1.6"/><circle cx="12" cy="15.2" r=".9"/>',
}

# (famille, paquet fontsource, graisse, style, fichier, unicode-range ou None)
FONTS = [
    ("Barlow", "barlow", 400, "normal", "barlow-latin-400-normal.woff2", None),
    ("Barlow", "barlow", 500, "normal", "barlow-latin-500-normal.woff2", None),
    ("Barlow", "barlow", 600, "normal", "barlow-latin-600-normal.woff2", None),
    ("Barlow", "barlow", 700, "normal", "barlow-latin-700-normal.woff2", None),
    ("Barlow", "barlow", 400, "italic", "barlow-latin-400-italic.woff2", None),
    ("Barlow", "barlow", 600, "italic", "barlow-latin-600-italic.woff2", None),
    ("Barlow Condensed", "barlow-condensed", 700, "normal", "barlow-condensed-latin-700-normal.woff2", None),
    ("Barlow Condensed", "barlow-condensed", 800, "normal", "barlow-condensed-latin-800-normal.woff2", None),
    ("Libre Baskerville", "libre-baskerville", 400, "italic", "libre-baskerville-latin-400-italic.woff2", None),
    ("Noto Sans Thai", "noto-sans-thai", 500, "normal", "noto-sans-thai-thai-500-normal.woff2", "U+0E01-0E5B,U+200C-200D,U+25CC"),
    ("Noto Sans Thai", "noto-sans-thai", 600, "normal", "noto-sans-thai-thai-600-normal.woff2", "U+0E01-0E5B,U+200C-200D,U+25CC"),
]

# remise à zéro que le squelette des Artifacts fournissait : on la reprend à l'identique, avec le fond papier sous les zones sûres
RESET = (":root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
         "html{scroll-padding-top:env(safe-area-inset-top,0px);background:#FFFCF6}"
         "body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}"
         "img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}")


def icon(name):
    return '<svg class="i" viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % ICONS[name]


def sticker_raw(name):
    return open(os.path.join(STK, "sticker_%s.svg" % name), encoding="utf-8").read()


def sticker(name):
    s = sticker_raw(name)
    s = re.sub(r"<\?xml[^>]*\?>\s*", "", s)
    s = re.sub(r'(<svg[^>]*?)\s+width="[^"]*"\s+height="[^"]*"', r"\1", s, count=1)
    s = s.replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)
    return s.strip()


def font_css():
    faces = []
    for fam, _pkg, w, style, fn, rng in FONTS:
        r = (";unicode-range:%s" % rng) if rng else ""
        faces.append("@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:swap;src:url('fonts/%s') format('woff2')%s}" % (fam, style, w, fn, r))
    return "<style>" + "".join(faces) + "</style>"


def build_content():
    t = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
    t = t.replace("<!--FONTS-->", font_css())
    t = t.replace("<!--STK_ELEPHANT-->", sticker("elephant")).replace("<!--STK_TUKTUK-->", sticker("tuktuk"))
    t = re.sub(r"<!--I:(\w+)-->", lambda m: icon(m.group(1)), t)
    return t


def make_icons(outdir):
    os.makedirs(outdir, exist_ok=True)
    raw = re.sub(r"<\?xml[^>]*\?>\s*", "", sticker_raw("elephant")).strip()
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', raw)
    w0 = float(vb.group(1))
    inner = raw[raw.index(">") + 1: raw.rindex("</svg>")]

    def svg(size_ratio, with_bg=True):
        side = 512 * size_ratio
        s = side / w0
        off = (512 - side) / 2
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">%s<g transform="translate(%.2f %.2f) scale(%.4f)">%s</g></svg>'
                % ('<rect width="512" height="512" fill="#A51C36"/>' if with_bg else "", off, off, s, inner))

    open(os.path.join(outdir, "icon.svg"), "w", encoding="utf-8").write(svg(0.74))
    jobs = [("icon-512.png", 512, 0.74), ("icon-192.png", 192, 0.74), ("apple-touch-icon.png", 180, 0.74),
            ("icon-maskable-512.png", 512, 0.58), ("favicon.png", 64, 0.80)]
    tmp = os.path.join(outdir, "_tmp.svg")
    for fn, px, ratio in jobs:
        open(tmp, "w", encoding="utf-8").write(svg(ratio))
        subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), "-o", os.path.join(outdir, fn), tmp], check=True)
    os.remove(tmp)


APP_META = ('<meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<meta name="theme-color" content="#A51C36">'
            '<meta name="robots" content="noindex,nofollow,noarchive">'
            '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">'
            '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
            '<meta name="apple-mobile-web-app-title" content="Thaïlande">'
            '<meta name="format-detection" content="telephone=no">'
            '<link rel="manifest" href="manifest.webmanifest">'
            '<link rel="icon" type="image/svg+xml" href="icons/icon.svg"><link rel="icon" type="image/png" sizes="64x64" href="icons/favicon.png">'
            '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">')

# page de test (ancienne page d'accueil, gardée pour vérifier un téléphone)
TEST_HEAD = ('<!doctype html><html lang="fr"><head>' + APP_META.replace('<meta name="apple-mobile-web-app-title" content="Thaïlande">', '<meta name="apple-mobile-web-app-title" content="Thaïlande">')
             + '<title>Test du téléphone · Carnet Thaïlande</title><style>' + RESET + '</style></head><body>\n')

MANIFEST = """{
  "name": "Carnet Thaïlande 2026",
  "short_name": "Thaïlande",
  "lang": "fr",
  "id": "./",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#FFFCF6",
  "theme_color": "#A51C36",
  "icons": [
    {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
"""

SW = r"""/* Service worker du carnet : garde les pages, les polices, les icônes et le plan du métro pour fonctionner sans réseau.
   Version __VERSION__ : le build change cette ligne à chaque publication, ce qui force la mise à jour chez tout le monde. */
const VERSION = "__VERSION__";
const CACHE = "carnet-" + VERSION;
const CORE = __CORE__;

self.addEventListener("install", (e) => {
  /* cache: "reload" : on prend la version du serveur, jamais une copie vieillie du cache du navigateur */
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(CORE.map((u) => new Request(u, { cache: "reload" }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k.startsWith("carnet-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const r = e.request;
  if (r.method !== "GET") return;
  const u = new URL(r.url);
  if (u.origin !== location.origin) return;
  if (r.mode === "navigate") {
    /* page : le réseau d'abord (pour voir les mises à jour), la copie gardée si le réseau est absent ou trop lent */
    e.respondWith(
      Promise.race([fetch(r, { cache: "no-cache" }), new Promise((_, rej) => setTimeout(() => rej(new Error("lent")), 4000))])
        .then((res) => {
          if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(r, copy)); }
          return res;
        })
        .catch(() => caches.match(r, { ignoreSearch: true }).then((m) => m || caches.match("index.html")))
    );
    return;
  }
  /* reportage photo : le réseau d'abord (nouvelles photos), la copie gardée si le réseau est absent */
  if (u.pathname.indexOf("/reportage/") >= 0) {
    e.respondWith(
      fetch(r, { cache: "no-cache" }).then((res) => {
        if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(r, copy)); }
        return res;
      }).catch(() => caches.match(r).then((m) => m || Response.error()))
    );
    return;
  }
  /* reste (polices, icônes, plan) : la copie gardée d'abord */
  e.respondWith(
    caches.match(r).then((m) => m || fetch(r).then((res) => {
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(r, copy)); }
      return res;
    }))
  );
});
"""


def build_test():
    """Page de test du téléphone : l'ancienne page d'accueil (v0.4), avec un lien de retour vers le carnet."""
    t = build_content()
    t = re.sub(r"<title>.*?</title>\s*", "", t, count=1, flags=re.S)
    t = re.sub(r'<section class="bubble sand" aria-labelledby="h-soon">.*?</section>\s*', "", t, count=1, flags=re.S)
    t = t.replace('<p class="eyebrow">Carnet en ligne <span class="v">bêta</span></p>',
                  '<a class="btn alt" href="./" style="min-height:40px;padding:0 16px;font-size:.95rem;margin-bottom:1rem">‹ Retour au carnet</a>'
                  '<p class="eyebrow">Carnet en ligne <span class="v">test</span></p>')
    t = t.replace('<p class="lead">Le carnet papier, version téléphone.</p>', '<p class="lead">Quelques essais pour vérifier ton téléphone.</p>')
    t = t.replace("Carnet Thaïlande 2026 · version 0.4, page de test", "Carnet Thaïlande 2026 · test du téléphone")
    assert "Retour au carnet" in t and "h-soon" not in t
    return TEST_HEAD + t + "\n</body></html>\n"


def build_web():
    import json
    import build_app, build_metro
    if os.path.isdir(WEB):
        shutil.rmtree(WEB)
    os.makedirs(os.path.join(WEB, "fonts"))
    os.makedirs(os.path.join(WEB, "assets"))
    for _fam, pkg, _w, _s, fn, _r in FONTS:
        shutil.copy(os.path.join(NM, pkg, "files", fn), os.path.join(WEB, "fonts", fn))
    make_icons(os.path.join(WEB, "icons"))
    build_metro.build(os.path.join(WEB, "assets", "metro.svg"))
    imgdir = os.path.join(ROOT, "img")
    if os.path.isdir(imgdir):
        os.makedirs(os.path.join(WEB, "img"))
        for fn in sorted(os.listdir(imgdir)):
            if fn.endswith(".webp"):
                shutil.copy(os.path.join(imgdir, fn), os.path.join(WEB, "img", fn))

    # reportage photo des invité·e·s (voir reportage_tool.py). Mode « Supabase » : reportage_cfg.json présent → seul c.json (pièce témoin du code) est publié,
    # les photos vivent chez Supabase, chiffrées. Sinon, mode « fichiers » : m.json + p*.bin publiés tels quels (chiffrés).
    repdir = os.environ.get("REPORTAGE_DIR") or os.path.join(ROOT, "reportage")
    cloud = os.path.isfile(os.environ.get("REPORTAGE_CFG") or os.path.join(ROOT, "reportage_cfg.json"))
    if cloud and os.path.isfile(os.path.join(repdir, "c.json")):
        os.makedirs(os.path.join(WEB, "reportage"))
        shutil.copy(os.path.join(repdir, "c.json"), os.path.join(WEB, "reportage", "c.json"))
    elif not cloud and os.path.isfile(os.path.join(repdir, "m.json")):
        os.makedirs(os.path.join(WEB, "reportage"))
        for fn in sorted(os.listdir(repdir)):
            if fn == "m.json" or re.fullmatch(r"p[0-9a-f]{8}\.bin", fn):
                shutil.copy(os.path.join(repdir, fn), os.path.join(WEB, "reportage", fn))

    version = time.strftime("%Y%m%d-%H%M%S")
    index = build_app.nbsp_pass(build_app.render(version, APP_META))
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(index)
    open(os.path.join(WEB, "test.html"), "w", encoding="utf-8").write(build_test())
    open(os.path.join(WEB, "manifest.webmanifest"), "w", encoding="utf-8").write(MANIFEST)
    open(os.path.join(WEB, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
    open(os.path.join(WEB, ".nojekyll"), "w").write("")

    core = ["./", "index.html", "test.html", "manifest.webmanifest", "assets/metro.svg"]
    for sub in ("icons", "fonts", "img"):
        if not os.path.isdir(os.path.join(WEB, sub)):
            continue
        for fn in sorted(os.listdir(os.path.join(WEB, sub))):
            if fn.endswith(".svg") and sub == "icons" and fn != "icon.svg":
                continue
            core.append("%s/%s" % (sub, fn))
    for c in core:
        if c != "./":
            assert os.path.exists(os.path.join(WEB, c)), c
    sw = SW.replace("__VERSION__", version).replace("__CORE__", json.dumps(core, ensure_ascii=False))
    open(os.path.join(WEB, "sw.js"), "w", encoding="utf-8").write(sw)
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(WEB) for f in fs)
    print("web/ prêt : index.html %d Ko, test.html %d Ko, total %d Ko, version %s, %d fichiers en cache"
          % (len(index.encode("utf-8")) // 1024, os.path.getsize(os.path.join(WEB, "test.html")) // 1024, total // 1024, version, len(core)))


if __name__ == "__main__":
    build_web()
