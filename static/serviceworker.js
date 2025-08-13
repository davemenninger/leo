const urlsToCache = [
  "/", "leo.js"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open("pwa-assets")
    .then(cache -> {
      return cache.addAll(urlsToCache);
    });
  );
});
