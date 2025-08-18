const version = "3";

const urlsToCache = [
  "/leo.js"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open("pwa-assets" + version)
    .then(cache => {
      return cache.addAll(urlsToCache);
    });
  );
});

self.addEventListener("activate", event => {
  console.log("service worker activated");
});
