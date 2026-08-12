#!/usr/bin/env python3
"""Gera a pagina publicavel a partir do fonte do artefato.

scout-futsal.html -> corpo do artefato (sem <html>/<head>/<body>, que e o
                     formato exigido por quem publica o artefato no Claude)
index.html        -> mesma coisa dentro de uma pagina HTML completa. E o que
                     o Vercel serve no link, e tambem o arquivo que voce salva
                     no aparelho para usar sem internet.

Cada geracao carimba uma versao (hash do corpo do app) no index.html e no
nome do cache do service worker. E o carimbo que faz o aparelho perceber que
saiu versao nova e trocar sozinho.

Rode `python3 build.py` sempre que mexer em scout-futsal.html.
"""
import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "scout-futsal.html")
OUT = os.path.join(HERE, "index.html")
SW = os.path.join(HERE, "sw.js")

HEAD = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Scout de futsal: registro por jogador, campograma, relatorio da partida e exportacao. Funciona sem internet.">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#0A1214">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Scout Futsal">
<meta name="sf-versao" content="{versao}">
<link rel="manifest" href="./manifest.webmanifest">
<link rel="icon" href="./icons/icon-192.png">
<link rel="apple-touch-icon" href="./icons/icon-180.png">
<title>Scout Futsal</title>
</head>
<body>
"""

# O service worker so entra na versao hospedada: fora de iframe e em http(s).
# Aberto como arquivo (file://) o app ja funciona offline por natureza.
#
# Versao nova no ar: o service worker novo assume na hora (skipWaiting +
# clients.claim) e a pagina recarrega sozinha. Com o relogio do jogo andando
# ela nao recarrega sozinha nunca — mostra um botao e quem decide e o scout.
FOOT = """
<script>
(function(){
  if(!('serviceWorker' in navigator)) return;
  if(window !== top || location.protocol.indexOf('http') !== 0) return;

  var recarregou = false;
  var tinhaControle = !!navigator.serviceWorker.controller;
  var reg = null;

  function aplica(){
    if(recarregou) return;
    recarregou = true;
    location.reload();
  }
  function botao(){
    if(document.getElementById('sf-att')) return;
    var b = document.createElement('button');
    b.id = 'sf-att';
    b.type = 'button';
    b.textContent = 'Versao nova · atualizar';
    b.setAttribute('style',
      'position:fixed;left:50%;bottom:22px;transform:translateX(-50%);z-index:70;' +
      'border:0;border-radius:999px;padding:11px 18px;cursor:pointer;' +
      'font:600 14px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;' +
      'background:#0B6E5F;color:#fff;box-shadow:0 6px 20px rgba(0,0,0,.3)');
    b.addEventListener('click', aplica);
    document.body.appendChild(b);
  }
  navigator.serviceWorker.addEventListener('controllerchange', function(){
    if(!tinhaControle) return;              /* primeira instalacao: nada a trocar */
    if(window.SF_ocupado && window.SF_ocupado()){ botao(); return; }
    aplica();
  });

  function procura(){ if(reg) { try{ reg.update(); }catch(e){} } }
  window.addEventListener('load', function(){
    navigator.serviceWorker.register('./sw.js').then(function(r){
      reg = r; procura();
    }).catch(function(){});
  });
  document.addEventListener('visibilitychange', function(){
    if(!document.hidden) procura();
  });
  setInterval(procura, 15 * 60 * 1000);
})();
</script>
</body>
</html>
"""


def carimba_sw(versao):
    """Poe a versao no nome do cache: cache novo a cada build."""
    sw = io.open(SW, encoding="utf-8").read()
    novo = re.sub(r"var CACHE = '[^']*';",
                  "var CACHE = 'scout-futsal-%s';" % versao, sw, count=1)
    if novo != sw:
        io.open(SW, "w", encoding="utf-8").write(novo)
    return novo != sw


def main():
    body = io.open(SRC, encoding="utf-8").read().strip()
    versao = hashlib.sha1(body.encode("utf-8")).hexdigest()[:8]
    io.open(OUT, "w", encoding="utf-8").write(
        HEAD.format(versao=versao) + body + FOOT)
    mexeu = carimba_sw(versao)
    print("gerado:", OUT, os.path.getsize(OUT), "bytes")
    print("versao:", versao, "(sw.js atualizado)" if mexeu else "(sw.js ja estava nesta versao)")


if __name__ == "__main__":
    main()
