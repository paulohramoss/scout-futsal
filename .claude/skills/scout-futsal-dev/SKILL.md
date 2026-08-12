---
name: scout-futsal-dev
description: Padrão de trabalho do Scout Futsal — app de scout de futsal em página única, offline, sem servidor. Use ao revisar diffs, implementar melhorias ou escrever testes deste projeto (scout-futsal.html, build.py, sw.js, index.html). Cobre estilo de código, migração de dados de partidas antigas, patch por âncora, teste automatizado com jsdom, build e fluxo staging → main.
---

# Scout Futsal — como mexer, revisar e testar

App de scout de futsal para marcar o jogo ao vivo no iPad. Uma página só, sem
login, sem servidor, sem internet. Quem usa é um scout com o tablet na mão no
meio do jogo: **erro em produção custa dado de jogo perdido**, e não existe
"volta amanhã que a gente conserta".

## Mapa dos arquivos

| Arquivo | O que é |
|---|---|
| `scout-futsal.html` | **O fonte.** Corpo do artefato: `<style>`, markup e um `<script>` com toda a lógica dentro de uma IIFE. Toda alteração de app é feita aqui. |
| `index.html` | **Gerado.** `python build.py` = HEAD + fonte + FOOT (registro do service worker). Vai versionado: é o que o Vercel serve. |
| `build.py` | Gera o `index.html` e carimba a versão (sha1 do fonte) no `<meta name="sf-versao">` e no nome do cache do `sw.js`. |
| `sw.js` | Service worker. HTML de rede primeiro, resto do cache. Nome do cache carimbado pelo build. |
| `vercel.json` | Sem cache de CDN em `sw.js`, `index.html` e manifest. |
| `README.md` | Documentação do usuário e a tabela de códigos do scout. Mudou código de ação, muda o README. |

**Nunca edite `index.html` na mão.** Edite o fonte e rode `python build.py`
(neste ambiente o comando é `python`, não `python3`). Commite os dois.

## Estilo de código (não negocie com isto)

- **ES5 puro.** `var`, `function(){}`, nada de `const`/`let`/arrow/template
  literal/`class`/spread. O app roda em iPad velho e é serializável para um
  `.html` avulso. Uma arrow function passa no build e quebra no aparelho do
  usuário — que é onde ninguém está olhando.
- **Zero dependência externa.** Sem CDN, sem fetch para fora, sem fonte remota.
  O app tem que abrir de `file://` e sem sinal.
- **Sem framework.** DOM na mão com os helpers que já existem: `$(sel)`,
  `el(tag,classe,texto)`, `sv(tag,attrs)` para SVG.
- **Comentário explica o porquê, nunca o quê.** O código do projeto comenta
  decisão ("o gol já conta como finalização no alvo, então em gol você toca só
  G"), não mecânica. Comentário em português, sem emoji.
- **Vocabulário misto é proposital**: infraestrutura em português (`banco`,
  `partidaNova`, `normaliza`, `gravaJa`), render em inglês (`renderStats`,
  `count`, `sumAll`). Nome novo imita o vizinho mais próximo, não uma regra
  global.
- **Tema por variável CSS.** Nada de cor literal em regra nova: use
  `var(--accent)`, `var(--neg)`, `var(--muted)`... Existem quatro blocos de
  tema (claro, escuro por `prefers-color-scheme`, e os dois forçados por
  `[data-theme]`) — cor nova entra nos quatro.
- **Botão é `<button type="button">`** com `aria-pressed` quando tem estado.
  Alvo de toque grande: isso é usado com o dedo, em pé, na beira da quadra.

## Modelo de dados

Três objetos globais dentro da IIFE:

- `P` — perfil (o scout): `plantel`, `freeLabels`, `freeCodes`, `time`, `pin`.
- `S` — partida atual: `players`, `events`, `shots`, `clocks`, `run`, `period`,
  `view`, `freeLabels`, `freeCodes`, `sel`, `shotMode`.
- `CFG` — tema e ponteiros de qual perfil/partida estão abertos.

Evento: `{p:<id do jogador ou null p/ equipe>, c:<código>, t:<segundos no tempo>,
per:<1|2>, id:<único>, x?, y?}`.

Regras que o modelo impõe:

1. **Código de evento gravado é imutável.** Botão livre é `L1..L5` por dentro
   para sempre; a sigla que o scout escolhe é só apresentação (`sigla()`,
   `descr()`). Trocar a sigla no meio do jogo não pode perder marcação.
2. **Partida antiga tem que abrir.** Todo campo novo entra com valor padrão em
   `normaliza(m)` — que roda em partida vinda do banco — e também em
   `partidaNova()`, que **não** passa por `normaliza`. Código que sumiu vira
   migração explícita (`DD` → `D`) ou fica documentado em `DESC` como antigo.
3. **`save()` é debounce de 300 ms; `gravaJa()` é imediato.** Toda mutação de
   `S` termina em `save()`. Nunca gravar direto no banco fora deles.
4. **Contadores da aba Registro são do jogo todo** (`count`, `sumAll`,
   `teamCount`). Estatísticas e Relatório respeitam o filtro de tempo
   (`countF`, `sumAllF`, `teamCountF`, variável `PERF`). Se alguma exportação
   mexer em `PERF`, guarda o valor antes e **restaura no fim** — senão a tela
   fica mentindo depois de exportar.
5. **Cronômetro:** `S.clocks[1]`, `S.clocks[2]` acumulados, `S.run` diz qual
   corre. `now()` é o tempo do período atual. Ao reabrir, o relógio volta
   **pausado** de propósito — o tempo em que o app ficou fechado não é jogo.

## Como aplicar mudança grande no fonte

O fonte é um arquivo só, grande. Editar às cegas quebra. O padrão do projeto:

1. Leia o trecho alvo antes (`grep -n`, `sed -n`).
2. Escreva um script Python de patch com pares (trecho antigo, trecho novo)
   **exatos**, e antes de aplicar verifique `s.count(old) == 1` — âncora
   ambígua ou sumida aborta o patch inteiro em vez de corromper o arquivo.
3. Rode, depois `python build.py`.
4. Confira a sintaxe: extraia o `<script>` e passe `node --check`.

Patch em pedaço pequeno é melhor que um gigante: âncora quebrada em patch de 20
trechos é difícil de achar.

## Teste automatizado

O app não tem framework de teste. O que vale é um **smoke em jsdom carregando o
`index.html` de verdade** — o mesmo arquivo que vai para o ar, service worker à
parte.

Molde:

```js
const { JSDOM, VirtualConsole } = require('jsdom');
const erros = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => erros.push(String(e)));
const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true,
                              url: 'https://exemplo.test/', virtualConsole: vc });
// espere ~700 ms: o boot do banco é assíncrono (IndexedDB cai para localStorage)
```

Regras do teste:

- Instale o `jsdom` no diretório de scratchpad da sessão, **nunca** no projeto:
  o repositório não tem `package.json` e não vai ter.
- Interaja como o usuário: `dispatchEvent(new w.MouseEvent('click',{bubbles:true}))`
  em botão real, `new w.Event('input',{bubbles:true})` em campo.
- **Re-consulte o nó depois de cada clique que registra evento.** Quase todo
  handler chama `renderAll()`, que refaz o DOM — referência velha fica órfã e o
  teste falha por engano.
- Cheque primeiro `erros.length === 0`: erro de script no boot invalida o resto.
- Nome do caso em português, curto, dizendo o comportamento
  (`'2o tempo: chutes do adversario a gol = 2'`), e imprima o valor recebido
  quando falha.
- Cubra, para cada mudança: o caminho feliz na tela, o número que sai na
  estatística/relatório, a exportação (stub em `URL.createObjectURL`) e a
  partida antiga (monte um objeto sem os campos novos e veja se abre).

O que jsdom **não** cobre e precisa de teste no aparelho: service worker e
atualização de versão, layout/responsivo, gesto e toque, impressão em PDF.
Diga isso no relatório em vez de dar por testado.

## Revisão de código — checklist

- [ ] ES5? Sem dependência nova? Sem chamada de rede?
- [ ] Campo novo em `S` ou no jogador tem padrão em `normaliza()` **e** em
      `partidaNova()`?
- [ ] Código de ação novo/removido: atualizou `LINE`/`GK`/`TEAM` (com `k`, `g`,
      `s`), `COLS_LINE`/`COLS_GK`, `vals()`, `HEAD_LINE`/`HEAD_GK`,
      `reportRows()`, legenda e a tabela de códigos do `README.md`? A ordem de
      `vals()` tem que casar coluna a coluna com `COLS_*` e `HEAD_*`.
- [ ] Render novo foi ligado em `renderAll()`?
- [ ] Mutação termina em `save()`?
- [ ] Mexeu em `PERF`? Restaurou?
- [ ] Cor nova saiu de variável de tema? Ficou legível no claro e no escuro?
- [ ] Elemento novo que não deve sair no PDF entrou na regra `@media print`?
- [ ] Texto de tela em português, com a mesma voz seca do resto (sem "ops!",
      sem exclamação).
- [ ] `README.md` continua verdadeiro?
- [ ] `python build.py` rodou e o `index.html` está no commit?

Achou problema: aponte arquivo e linha, diga o que quebra na prática ("com
partida de antes de X, abre com a tabela desalinhada"), proponha a correção
mínima. Nada de reescrever o que já funciona.

## Receitas

**Ação nova no painel:** entrada em `LINE` ou `GK` com `c` (código), `d`
(descrição), `k` (cor: `pos`/`neg`/`gol`/`ca`/`cv`), `g` (grupo na coluna da
quadra) e `s` (`a` acerto à direita, `e` erro à esquerda) → coluna em `COLS_*`
e `HEAD_*` → conta em `vals()` → se conta placar/chute, entra em `reportRows()`
→ README.

**Campo novo na partida:** padrão em `partidaNova()` e em `normaliza()` →
usa → se for de plantel, copia para o perfil em `save()` → se vier de backup
antigo, trata no `#impFile`.

**Aba nova:** `<button class="tab" data-t="x">` + `<section id="x" hidden>` +
o id na lista do handler de abas + `renderX()` em `renderAll()`.

**Mudou algo que o usuário vê:** README na mesma leva do commit.

## Publicar

```bash
git checkout staging
# edita scout-futsal.html, python build.py
git add -A && git commit
git push                       # deploy automático na staging
# aprovado no iPad:
git checkout main && git merge staging && git push
git checkout staging
```

- Trabalhe sempre em `staging`. `main` é o link que o pessoal abre no jogo.
- Staging e produção têm **bancos separados** (IndexedDB é preso ao domínio).
  Jogo de verdade nunca na staging.
- Mensagem de commit em português: assunto curto no que mudou, corpo dizendo o
  problema que existia e a decisão tomada, com `Co-Authored-By` no fim. O
  histórico deste repositório é escrito assim; siga o tom.
- Commit só quando o usuário pedir.
