/* Service worker do Scout Futsal.

   Serve o app a partir do cache: depois da primeira visita o link abre sem
   internet, inclusive na quadra sem sinal. Quando ha rede, busca a versao nova
   em segundo plano — ela entra no proximo abrir. */
var CACHE = 'scout-futsal-v1';
var ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-180.png',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

self.addEventListener('install', function(e){
  e.waitUntil(
    caches.open(CACHE)
      .then(function(c){ return c.addAll(ASSETS); })
      .then(function(){ return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys().then(function(ks){
      return Promise.all(ks.map(function(k){
        return k === CACHE ? null : caches.delete(k);
      }));
    }).then(function(){ return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function(e){
  var req = e.request;
  if(req.method !== 'GET' || req.url.indexOf(self.location.origin) !== 0) return;

  e.respondWith(
    caches.match(req).then(function(hit){
      var rede = fetch(req).then(function(res){
        if(res && res.ok){
          var copia = res.clone();
          caches.open(CACHE).then(function(c){ c.put(req, copia); });
        }
        return res;
      }).catch(function(){
        return hit || caches.match('./index.html');
      });
      return hit || rede;
    })
  );
});
