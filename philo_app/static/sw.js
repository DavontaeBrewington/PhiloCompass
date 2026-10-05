/* PhiloCompass service worker — enables full offline use of the SPA.
   Cache-first for static assets. Bump CACHE_VERSION whenever you change
   JS/CSS/HTML to force an update (the app already version-URLs its assets
   with ?v=, but this is a second safety net). */

const CACHE_VERSION = "philocompass-v25";
const STATIC_ASSETS = [
  "/",
  "/static/style.css?v=17",
  "/static/app.js?v=20",
  "/static/manifest.webmanifest",
  "/static/favicon.svg",
  "/static/icon.svg",
  "/api/domains",
  "/api/map",
  "/api/paths",
  "/api/glossary",
  "/api/health",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  // Only handle same-origin GETs
  if (url.origin !== location.origin) return;
  if (e.request.method !== "GET") return;
  // API reads: network-first, fall back to cache (so offline sessions still show the map)
  if (url.pathname.startsWith("/api/")) {
    e.respondWith(
      fetch(e.request)
        .then((resp) => {
          const copy = resp.clone();
          const cacheOpen = caches.open(CACHE_VERSION);
          if (resp.ok) cacheOpen.then((c) => c.put(e.request, copy));
          return resp;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }
  // Static + shell: cache-first
  e.respondWith(
    caches.match(e.request).then(
      (cached) =>
        cached ||
        fetch(e.request).then((resp) => {
          const copy = resp.clone();
          caches.open(CACHE_VERSION).then((c) => c.put(e.request, copy));
          return resp;
        })
    )
  );
});
