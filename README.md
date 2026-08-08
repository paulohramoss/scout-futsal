# Scout Futsal

Scout de futsal para marcar o jogo ao vivo, no iPad ou no computador. Uma página
só, sem login, sem servidor e sem internet: tudo o que você registra fica salvo
no próprio aparelho.

## O que dá para fazer

- **Registro** — um toque por ação, por jogador. Painel separado para goleiro
  (gol sofrido, defesa difícil, reposição). Cronômetro, placar, 1º/2º tempo e
  cinco botões livres que você renomeia para o que quiser marcar.
- **Partidas** — vários scouts no mesmo aparelho, cada um com o próprio plantel
  e o próprio histórico de jogos. Reabra qualquer partida anterior.
- **Campograma** — toca na quadra onde saiu a finalização; entra na conta do
  jogador selecionado e vira coordenada em metros na exportação.
- **Estatísticas** — tabela por jogador, com totais e precisão de passe e chute.
- **Relatório** — o resumo da partida contra o adversário: placar, chutes,
  chutes a gol, precisão, **passes errados**, escanteios, faltas e cartões.
- **Comparação** — dois jogadores lado a lado.
- **Exportação** — CSV completo (relatório + estatísticas + botões livres +
  campograma), resumo em texto para colar no grupo, impressão em PDF e backup
  `.json` que reabre a partida inteira em outro aparelho.

## Como usar sem internet

**No link:** abra uma vez com internet e use o botão Compartilhar →
*Adicionar à Tela de Início* (iPad) ou *Instalar* (Chrome). Depois disso abre em
tela cheia e funciona sem sinal — um service worker guarda o app no aparelho.

**Sem depender do navegador:** na aba **Dados**, botão *Baixar o app (.html)*.
Sai um arquivo único com o app inteiro dentro; guarde no aparelho e abra com dois
toques. É o mesmo que o `index.html` deste repositório.

## Onde ficam os dados

Num banco dentro do próprio navegador — **IndexedDB**, com queda para
`localStorage` e, no pior caso, memória, se o navegador bloquear (Safari em modo
privado). Não existe servidor, conta nem sincronização: **nada sai do aparelho**,
nem quando tem internet.

Três coleções: `perfis` (o scout, seu plantel e seus botões livres), `partidas`
(uma por jogo, ligada ao perfil) e `app` (qual perfil e qual partida estão
abertos, e o tema). Grava sozinho a cada toque.

Isso significa que **os dados não atravessam aparelhos.** Cada iPad tem o próprio
banco. Para levar um scout inteiro de um aparelho para outro — perfil, plantel e
todas as partidas — use **Backup .json** e **Restaurar backup .json** na aba
Dados.

Sobre a trava por PIN: ela evita abrir o perfil errado por engano. **Não é
senha** — quem tem o aparelho na mão passa por ela pelo console do navegador.
Senha que vale alguma coisa só existiria com servidor, que é justamente o que
este projeto não tem.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `scout-futsal.html` | **O fonte.** Corpo do artefato — sem `<html>`/`<head>`/`<body>`, que é o formato exigido pelo publicador de artefatos do Claude. Toda alteração no app é feita aqui. |
| `index.html` | Gerado. A página completa que o Vercel serve e que você salva para usar offline. |
| `build.py` | Gera `index.html` a partir de `scout-futsal.html`. |
| `sw.js`, `manifest.webmanifest`, `icons/` | Fazem o link funcionar offline e instalar como app. |
| `make-icons.py` | Redesenha os ícones (só precisa rodar se o ícone mudar). |
| `vercel.json` | Impede o CDN de segurar versão velha do app e do service worker. |

## Mexer no app

```bash
python3 build.py
```

Edite `scout-futsal.html`, rode o comando acima e faça o commit dos dois
arquivos. `index.html` é gerado, mas **vai versionado** — é ele que o Vercel
publica, e não existe passo de build no deploy.

Depois de um deploy novo, o app abre a versão em cache e baixa a nova em segundo
plano: ela entra no abrir seguinte. Fechar e abrir de novo resolve.

## Códigos do scout

**Linha:** G gol · A assistência · PC/PE passe certo/errado · CC/CE chute
certo/errado · DE desarme · DO desarmado · FS/FC falta sofrida/cometida ·
I impedimento · CA/CV cartões

**Goleiro:** GS gol sofrido · DD defesa difícil · D defesa simples · F chute do
adversário fora · PC/PE passe · RC/RE reposição · FS/FC falta · AI ação
individual · CA/CV cartões

**Equipe:** EF/EC escanteio a favor/contra · ACA/ACV cartão do adversário

Precisão de chute = (G+CC) ÷ (G+CC+CE) — o gol já conta como finalização no
alvo, então em gol você toca só **G**.
