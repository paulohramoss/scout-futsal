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
    A barra **Reservas** abre o banco logo abaixo da quadra: com um jogador
    selecionado, tocar num reserva faz a substituição, e ele entra na mesma
    posição. Slot vazio tem um **+** que chama o banco direto.
  - **Lista** — o formato antigo: fila de jogadores no topo e a grade cheia de
    botões embaixo.

  Painel separado para goleiro (gol sofrido, defesa, reposição, chute
  certo/errado). Placar, **dois cronômetros — um para cada tempo** — e cinco
  botões livres em que você troca a sigla *e* a descrição para o que quiser
  marcar.
- **Partidas** — vários scouts no mesmo aparelho, cada um com o próprio plantel
  e o próprio histórico de jogos. Reabra qualquer partida anterior.
- **Campograma** — toca na quadra onde saiu a finalização; entra na conta do
  jogador selecionado e vira coordenada em metros na exportação.
- **Estatísticas** — tabela por jogador, com totais e precisão de passe e chute.
  Filtro **jogo todo / 1º tempo / 2º tempo** no topo, que também vale no relatório.
- **Relatório** — o resumo da partida contra o adversário: placar, chutes,
  chutes a gol, precisão, **passes errados**, escanteios, faltas e cartões.
- **Comparação** — dois jogadores lado a lado.
- **Exportação** — CSV completo (relatório + estatísticas **do jogo todo, do 1º
  e do 2º tempo** + botões livres + campograma), resumo em texto para colar no
  grupo, impressão em PDF e backup `.json` que reabre a partida inteira em outro
  aparelho.

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

**Livres:** L1..L5 de fábrica — na aba Plantel você troca a sigla e a descrição
de cada um. Por dentro o código continua L1..L5, então trocar a sigla no meio do
jogo não perde o que já foi marcado.

Partida antiga abre normal: **DD** (defesa difícil) vira **D**, e **I**
(impedimento) some das tabelas mas continua no log e no CSV de eventos.

**Equipe:** EF/EC escanteio a favor/contra · ACA/ACV cartão do adversário

Precisão de chute = (G+CC) ÷ (G+CC+CE) — o gol já conta como finalização no
alvo, então em gol você toca só **G**.
