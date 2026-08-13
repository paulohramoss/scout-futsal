/* Service worker do Scout Futsal.

   Serve o app a partir do cache: depois da primeira visita o link abre sem
   internet, inclusive na quadra sem sinal.

   A pagina em si (o HTML) vai de rede primeiro, com o cache de reserva: com
   sinal voce sempre abre a versao mais nova; sem sinal abre a ultima que ficou
   guardada. O resto (icones, manifest) vai do cache na hora e se renova atras.

   O nome do cache carrega o carimbo do build (build.py reescreve a linha
   abaixo a cada geracao), entao versao nova = cache novo, e o antigo e apagado
   no activate. */
var CACHE = 'scout-futsal-31c6a2d1';
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

function ehPagina(req){
  if(req.mode === 'navigate') return true;
  var aceita = req.headers.get('accept') || '';
  return aceita.indexOf('text/html') >= 0;
}

self.addEventListener('fetch', function(e){
  var req = e.request;
  if(req.method !== 'GET' || req.url.indexOf(self.location.origin) !== 0) return;

  /* HTML: rede primeiro. E o que faz a versao nova aparecer sem ficar
     fechando e abrindo o app. */
  if(ehPagina(req)){
    e.respondWith(
      fetch(req).then(function(res){
        if(res && res.ok){
          var copia = res.clone();
          caches.open(CACHE).then(function(c){ c.put('./index.html', copia); });
        }
        return res;
      }).catch(function(){
        return caches.match(req).then(function(hit){
          return hit || caches.match('./index.html');
        });
      })
    );
    return;
  }

  /* resto: do cache na hora, renovando em segundo plano */
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
