# Scout Futsal

Scout de futsal para marcar o jogo ao vivo, no iPad ou no computador. Uma página
só, sem login, sem servidor e sem internet: tudo o que você registra fica salvo
no próprio aparelho.

## O que dá para fazer

- **Registro** — um toque por ação, por jogador. Duas vistas, no botão
  *Quadra / Lista* no topo da aba:
  - **Quadra** — os cinco em quadra desenhados nas posições (gol, fixo, ala,
    ala, pivô), cada um com o número e dois selos: erros em vermelho, acertos em
    verde. Toca no jogador para marcar; os botões ficam nas laterais — **erros à
    esquerda, acertos à direita**, agrupados (finalização, passe, disciplina...).
    No iPad eles ficam na mesma altura da quadra: dá para trocar de jogador e
    marcar a ação sem rolar a página. Só em tela de celular as duas colunas
    descem para baixo. A barra **Reservas** abre o banco logo abaixo da quadra: com um jogador
    selecionado, tocar num reserva faz a substituição, e ele entra na mesma
    posição. Slot vazio tem um **+** que chama o banco direto.
  - **Lista** — o formato antigo: fila de jogadores no topo e a grade cheia de
    botões embaixo.

  Painel separado para goleiro (gol sofrido, defesa, reposição, chute
  certo/errado). Placar, **dois cronômetros — um para cada tempo** — e cinco
  botões livres em que você troca a sigla *e* a descrição para o que quiser
  marcar.

  No cabeçalho, as **faltas acumuladas do tempo** (nós e eles): fica amarelo na
  quarta e vermelho na quinta, que é quando vira tiro livre de 10 m sem
  barreira. Com o cronômetro andando a **tela não apaga** sozinha.

  O botão **Modo jogo** deixa só Registro e Campograma no topo — ao vivo, oito
  abas é toque errado esperando acontecer. **Modo análise** devolve todas.

  Em *Últimos registros* dá para **trocar o jogador** de um registro antigo ou
  **apagar** um registro errado, sem desfazer tudo o que veio depois.
- **Partidas** — vários scouts no mesmo aparelho, cada um com o próprio plantel
  e o próprio histórico de jogos. Reabra qualquer partida anterior.
- **Campograma** — toca na quadra onde saiu a finalização; entra na conta do
  jogador selecionado e vira coordenada em metros na exportação. Dá para marcar
  as finalizações **do adversário** também (entram na conta do goleiro que está
  em quadra, e saem como quadrado no desenho): é a leitura defensiva que faltava.
  A quadra vem dividida em **seis zonas** — defesa, meio e ataque, em dois
  corredores — com gols ÷ finalizações e o aproveitamento de cada uma.
- **Estatísticas** — tabela por jogador, com totais e precisão de passe e chute.
  Filtro **jogo todo / 1º tempo / 2º tempo** no topo, que também vale no relatório.
  Traz **MIN** (tempo em quadra) e **A/M** (ações por minuto): num esporte de
  rodízio, 3 gols em 8 minutos e 3 gols em 30 não são a mesma linha. A
  minutagem sai das substituições, que viram evento (`SUB`).
- **Relatório** — o resumo da partida contra o adversário: placar, chutes,
  chutes a gol, precisão, **passes errados**, escanteios, faltas e cartões.
  Em *Identificação* você põe **data do jogo, competição, categoria, rodada,
  local, analista e o escudo do time** — tudo isso vai para o cabeçalho do PDF,
  para o CSV e para o resumo em texto, com uma linha de assinatura no fim.
  A data é a **do jogo**, não a de hoje: reabrir uma partida de duas semanas
  atrás e imprimir sai com a data certa.
- **Comparação** — dois jogadores lado a lado.
- **Temporada** — soma todas as partidas do scout: vitórias, empates e derrotas,
  gols por jogo, e a tabela por atleta com jogos, minutos, gols, assistências,
  aproveitamento de chute, ações por minuto e gols por jogo, ordenada por gols.
- **Exportação** — CSV completo (relatório + estatísticas **do jogo todo, do 1º
  e do 2º tempo** + botões livres + campograma), resumo em texto para colar no
  grupo, impressão em PDF e backup `.json` que reabre a partida inteira em outro
  aparelho.

## Como usar sem internet

**No link:** abra uma vez com internet e use o botão Compartilhar →
*Adicionar à Tela de Início* (iPad) ou *Instalar* (Chrome). Depois disso abre em
tela cheia e funciona sem sinal — um service worker guarda o app no aparelho.

O **PDF sai inteiro** — relatório, estatísticas por jogador e campograma, cada
bloco em sua página.

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

**Nunca versione um backup.** Ele leva o PIN do perfil, o nome do time e o nome
de cada atleta — nome de atleta de base em repositório é dor de cabeça garantida
com pai de jogador. O `.gitignore` bloqueia todo `.json` justamente por isso, com
exceção nominal só para `vercel.json` e para os arquivos de `.claude/`.

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

## Fluxo de trabalho

Duas branches, dois endereços:

| Branch | Endereço | Para quê |
|---|---|---|
| `staging` | `scout-futsal-git-staging-paulohramoss-projects.vercel.app` | Testar antes de soltar |
| `main` | **scoutfutsal.vercel.app** | O link que o pessoal usa no jogo |

Todo push gera deploy sozinho. Trabalhe sempre na `staging`:

```bash
git checkout staging
# edita scout-futsal.html, roda python3 build.py
git add -A && git commit -m "..."
git push
```

Testou e aprovou, sobe para produção:

```bash
git checkout main && git merge staging && git push
git checkout staging
```

### Atenção: os dois endereços têm bancos separados

Staging e produção são domínios diferentes, e o IndexedDB é preso ao domínio.
**O que você marcar testando na staging não existe em produção**, e o contrário
também. Nunca marque um jogo de verdade no endereço de teste — não tem como
trazer os dados de lá para cá, a não ser exportando o backup `.json` num e
restaurando no outro.

### Versão nova chega sozinha

Cada `python3 build.py` carimba uma versão (hash do fonte) no `index.html` e no
nome do cache do `sw.js`. Com isso o aparelho percebe que saiu build novo: o
service worker novo assume na hora e **a página recarrega sozinha** — sem fechar
e abrir o app.

A única exceção é o jogo em andamento: **com o cronômetro correndo o app nunca
recarrega sozinho**, aparece um botão *Versão nova · atualizar* e quem decide é o
scout. O HTML passou a ser buscado na rede primeiro (cache só de reserva), então
abrir com sinal já traz a versão do dia; sem sinal abre a última guardada.

A versão que está rodando no aparelho aparece na aba **Dados → Versão**. É por
ela que você confere se o iPad já pegou o build novo.

## Códigos do scout

**Linha:** G gol · A assistência · PC/PE passe certo/errado · CC/CE chute
certo/errado · DE desarme · DO desarmado · FS/FC falta sofrida/cometida ·
CA/CV cartões

**Goleiro:** GS gol sofrido · D defesa · F chute do adversário fora · CC/CE
chute certo/errado (do goleiro) · PC/PE passe · RC/RE reposição · FS/FC falta ·
AI ação individual · CA/CV cartões

**Campograma do adversário:** GS gol sofrido · D defesa · F pra fora — os
mesmos códigos do painel do goleiro, com o lugar do chute junto.

**Substituição:** SUB, gravada com quem entrou e quem saiu. Não conta em
nenhuma estatística; serve para a minutagem.

**Livres:** L1..L5 de fábrica — na aba Plantel você troca a sigla e a descrição
de cada um. Por dentro o código continua L1..L5, então trocar a sigla no meio do
jogo não perde o que já foi marcado.

Partida antiga abre normal: **DD** (defesa difícil) vira **D**, e **I**
(impedimento) some das tabelas mas continua no log e no CSV de eventos.

**Equipe:** EF/EC escanteio a favor/contra · ACA/ACV cartão do adversário

Precisão de chute = (G+CC) ÷ (G+CC+CE) — o gol já conta como finalização no
alvo, então em gol você toca só **G**.
