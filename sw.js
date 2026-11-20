/* Service worker du carnet : garde la page, les polices et les icônes pour fonctionner sans réseau.
   Version 20261120-200753 : changer cette ligne (le build le fait) force la mise à jour chez tout le monde. */
const VERSION = "20261120-200753";
const CACHE = "carnet-" + VERSION;
const CORE = ["./", "index.html", "manifest.webmanifest", "icons/apple-touch-icon.png", "icons/favicon.png", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "icons/icon.svg", "fonts/barlow-condensed-latin-700-normal.woff2", "fonts/barlow-condensed-latin-800-normal.woff2", "fonts/barlow-latin-400-italic.woff2", "fonts/barlow-latin-400-normal.woff2", "fonts/barlow-latin-500-normal.woff2", "fonts/barlow-latin-600-normal.woff2", "fonts/barlow-latin-700-normal.woff2", "fonts/libre-baskerville-latin-400-italic.woff2", "fonts/noto-sans-thai-thai-500-normal.woff2", "fonts/noto-sans-thai-thai-600-normal.woff2"];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting())
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
      Promise.race([fetch(r), new Promise((_, rej) => setTimeout(() => rej(new Error("lent")), 4000))])
        .then((res) => {
          if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put("index.html", copy)); }
          return res;
        })
        .catch(() => caches.match("index.html").then((m) => m || caches.match("./")))
    );
    return;
  }
  /* reste (polices, icônes, données) : la copie gardée d'abord */
  e.respondWith(
    caches.match(r).then((m) => m || fetch(r).then((res) => {
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(r, copy)); }
      return res;
    }))
  );
});
