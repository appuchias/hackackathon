// Service worker para instalar la PWA, y que hace funcionar la caché en la misma
self.addEventListener("install", event => {
    console.log("Service worker installed");
});
self.addEventListener("activate", event => {
    console.log("Service worker activated");    
});

caches.open("pwa-assets")
.then(cache => {
    cache.addAll(["/static/css/style.css"]);
});

 self.addEventListener("fetch", event => {
    event.respondWith(
      fetch(event.request)
      .catch(error => {
        return caches.match(event.request) ;
      })
    );
 });
