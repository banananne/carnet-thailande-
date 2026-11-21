/* Service worker du carnet : garde les pages, les polices, les icônes et le plan du métro pour fonctionner sans réseau.
   Version 20261121-195156 : le build change cette ligne à chaque publication, ce qui force la mise à jour chez tout le monde. */
const VERSION = "20261121-195156";
const CACHE = "carnet-" + VERSION;
const CORE = ["./", "index.html", "test.html", "manifest.webmanifest", "assets/metro.svg", "icons/apple-touch-icon.png", "icons/favicon.png", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "icons/icon.svg", "fonts/barlow-condensed-latin-700-normal.woff2", "fonts/barlow-condensed-latin-800-normal.woff2", "fonts/barlow-latin-400-italic.woff2", "fonts/barlow-latin-400-normal.woff2", "fonts/barlow-latin-500-normal.woff2", "fonts/barlow-latin-600-italic.woff2", "fonts/barlow-latin-600-normal.woff2", "fonts/barlow-latin-700-normal.woff2", "fonts/libre-baskerville-latin-400-italic.woff2", "fonts/noto-sans-thai-thai-500-normal.woff2", "fonts/noto-sans-thai-thai-600-normal.woff2", "img/doudou_aftonsparv.webp", "img/doudou_boop.webp", "img/doudou_minou.webp", "img/doudou_moomoo.webp"];

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
  /* reste (polices, icônes, plan) : la copie gardée d'abord */
  e.respondWith(
    caches.match(r).then((m) => m || fetch(r).then((res) => {
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(r, copy)); }
      return res;
    }))
  );
});
