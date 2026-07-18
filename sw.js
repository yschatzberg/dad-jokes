/* Sticky Jokes service worker.

   Everything ships in the page itself, so the whole app is a handful of files.
   Precache them and serve cache-first: once installed, it works on a plane.

   Bump CACHE whenever you deploy, or the old files keep being served. */

const CACHE = 'sticky-jokes-v1';

const ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  event.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).catch(() => {
        // an offline navigation still needs a page to land on
        if (req.mode === 'navigate') return caches.match('./index.html');
        throw new Error('offline and uncached: ' + req.url);
      });
    })
  );
});
