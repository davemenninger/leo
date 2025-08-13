const urlsToCache = [
  "/", "static/leo.js"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open("pwa-assets")
    .then(cache => {
      return cache.addAll(urlsToCache);
    });
  );
});

self.addEventListener("activate", event => {
  console.log("service worker activated");
});
