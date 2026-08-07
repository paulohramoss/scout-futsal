#!/usr/bin/env python3
"""Gera a pagina publicavel a partir do fonte do artefato.

scout-futsal.html -> corpo do artefato (sem <html>/<head>/<body>, que e o
                     formato exigido por quem publica o artefato no Claude)
index.html        -> mesma coisa dentro de uma pagina HTML completa. E o que
                     o Vercel serve no link, e tambem o arquivo que voce salva
                     no aparelho para usar sem internet.

Rode `python3 build.py` sempre que mexer em scout-futsal.html.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "scout-futsal.html")
OUT = os.path.join(HERE, "index.html")

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
<link rel="manifest" href="./manifest.webmanifest">
<link rel="icon" href="./icons/icon-192.png">
<link rel="apple-touch-icon" href="./icons/icon-180.png">
<title>Scout Futsal</title>
</head>
<body>
"""

# O service worker so entra na versao hospedada: fora de iframe e em http(s).
# Aberto como arquivo (file://) o app ja funciona offline por natureza.
FOOT = """
<script>
if('serviceWorker' in navigator && window===top && location.protocol.indexOf('http')===0){
  window.addEventListener('load',function(){
    navigator.serviceWorker.register('./sw.js').catch(function(){});
  });
}
</script>
</body>
</html>
"""


def main():
    body = io.open(SRC, encoding="utf-8").read()
    io.open(OUT, "w", encoding="utf-8").write(HEAD + body.strip() + FOOT)
    print("gerado:", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
