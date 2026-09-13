#!/usr/bin/env python3
"""Gera a pagina publicavel a partir do fonte do artefato.

css/*.css         -> o estilo, dividido por assunto. E AQUI que se mexe em CSS.
scout-futsal.html -> markup e JavaScript, escritos na mao. Nao tem estilo
                     nenhum dentro: no lugar do <style> ha uma marca que este
                     script troca pelo CSS montado.
index.html        -> a pagina completa e unica: markup, JS e o CSS embutido.
                     E o que o Vercel serve no link, e tambem o arquivo que
                     voce salva no aparelho para usar sem internet.

O CSS fica em arquivo separado para trabalhar, mas volta embutido na pagina:
o app tem que abrir de file://, salvo como arquivo unico e sem sinal, e o
service worker serve tudo que nao e HTML pelo cache — folha de estilo a parte
daria markup novo com estilo velho depois de um deploy.

A ordem dos arquivos em css/ e a ordem das regras na pagina, e em CSS ordem
decide empate. Por isso o nome comeca com numero e este script recusa arquivo
fora do padrao NN-nome.css em vez de adivinhar a posicao.

Cada geracao carimba uma versao (hash do corpo do app) no index.html e no
nome do cache do service worker. E o carimbo que faz o aparelho perceber que
saiu versao nova e trocar sozinho. O hash sai do corpo JA MONTADO, com o CSS
dentro: se saisse so do fonte, mexer numa cor nao mudaria a versao e o
aparelho continuaria servindo o estilo velho do cache.

Rode `python3 build.py` sempre que mexer em css/ ou em scout-futsal.html.
"""
import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "scout-futsal.html")
OUT = os.path.join(HERE, "index.html")
SW = os.path.join(HERE, "sw.js")
CSS_DIR = os.path.join(HERE, "css")

# A linha que o fonte guarda no lugar do estilo. Tem que bater exatamente.
MARCA_CSS = "<!-- estilo: montado por build.py a partir de css/ -->"
# Aviso que vai no <style> gerado, para quem abrir o index.html procurando CSS.
AVISO_CSS = "/* gerado por build.py a partir de css/ - nao edite aqui */"
NOME_CSS = re.compile(r"^\d\d-[a-z0-9-]+\.css$")

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


def indenta(txt):
    """Duas casas, como o resto do <style>. Linha em branco fica em branco."""
    return "\n".join(("  " + l) if l.strip() else "" for l in txt.split("\n"))


def monta_css():
    """Junta css/*.css na ordem do nome. Falha alto: um erro aqui viraria app
    sem estilo nenhum no aparelho, e isso so aparece na hora do jogo."""
    if not os.path.isdir(CSS_DIR):
        raise SystemExit("build: falta a pasta css/ — o estilo mora la")
    arqs = sorted(f for f in os.listdir(CSS_DIR) if f.endswith(".css"))
    if not arqs:
        raise SystemExit("build: css/ esta vazia")
    fora = [f for f in arqs if not NOME_CSS.match(f)]
    if fora:
        raise SystemExit("build: nome fora do padrao NN-nome.css em css/: "
                         + ", ".join(fora))
    blocos = []
    for f in arqs:
        txt = io.open(os.path.join(CSS_DIR, f), encoding="utf-8").read().strip("\n")
        if txt:
            blocos.append(indenta(txt))
    return "\n\n".join(blocos), arqs


def injeta_css(body, css):
    """Troca a marca do fonte pelo <style> montado."""
    if body.count(MARCA_CSS) != 1:
        raise SystemExit("build: esperava exatamente uma marca de estilo em "
                         "scout-futsal.html, achei %d.\n       linha esperada: %s"
                         % (body.count(MARCA_CSS), MARCA_CSS))
    bloco = "<style>\n  " + AVISO_CSS + "\n\n" + css + "\n</style>"
    return body.replace(MARCA_CSS, bloco)


def carimba_sw(versao):
    """Poe a versao no nome do cache: cache novo a cada build."""
    sw = io.open(SW, encoding="utf-8").read()
    novo = re.sub(r"var CACHE = '[^']*';",
                  "var CACHE = 'scout-futsal-%s';" % versao, sw, count=1)
    if novo != sw:
        io.open(SW, "w", encoding="utf-8").write(novo)
    return novo != sw


def main():
    fonte = io.open(SRC, encoding="utf-8").read().strip()
    css, arqs = monta_css()
    body = injeta_css(fonte, css)
    versao = hashlib.sha1(body.encode("utf-8")).hexdigest()[:8]
    io.open(OUT, "w", encoding="utf-8").write(
        HEAD.format(versao=versao) + body + FOOT)
    mexeu = carimba_sw(versao)
    print("css:", len(arqs), "arquivos ->", css.count("\n") + 1, "linhas embutidas")
    print("gerado:", OUT, os.path.getsize(OUT), "bytes")
    print("versao:", versao, "(sw.js atualizado)" if mexeu else "(sw.js ja estava nesta versao)")


if __name__ == "__main__":
    main()
