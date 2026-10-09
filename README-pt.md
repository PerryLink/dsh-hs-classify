# dsh-hs-classify — Verificação da coerência hierárquica do registo de classificação de mercadorias

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-hs-classify` lê um registo de classificação de mercadorias —o cabeçalho do declarante mais uma linha por item— e verifica a estrutura dos números que regista: se o código de mercadoria tem dez dígitos, se o capítulo, a posição e a subposição são prefixos sucessivos desse código, se os níveis vão do mais geral para o mais específico, se cada linha regista um fundamento de classificação, se o cabeçalho declara a versão da pauta a que os códigos pertencem, se os números de item são únicos no registo e se não resta nenhum marcador de modelo por substituir na designação.

## Como é a saída

![Terminal demo of dsh-hs-classify: real output over its HC-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-hs-classify/main/docs/assets/dsh-hs-classify-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `HC-001` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Alguns códigos do registo têm oito dígitos e um termina numa letra. Isso é reportado? | Sim. `HC-001` compara cada `hsCode` preenchido com o `pattern` do pacote de regras, `^[0-9]{10}$`, e reporta a linha com o valor que leu. Verifica apenas o número de dígitos e os caracteres, nunca se a mercadoria pertence a esse código. Uma célula de código em branco é ignorada: o que ele reporta é um código com a forma errada, não um código em falta. Os dez dígitos são uma definição do pacote de regras: quando a pauta anual mudar o comprimento, edita-se o `pattern`, não o código. |
| O 章, o 品目 e o 子目 de uma linha não concordam com o seu 商品编号. Isso é detetado? | Sim. `HC-002` lê as colunas de nível do mais geral para o mais específico — 章, 品目 e 子目, dois, quatro e seis dígitos no exemplo do próprio pacote de regras — e assinala o nível que não é prefixo do `hsCode` lido, ou que não é mais fino do que o nível anterior. Verifica apenas essa relação de prefixo e essa ordem: se o código corresponde à mercadoria é uma determinação aduaneira que exige a pauta e as decisões de classificação, que este plugin não consulta. Uma célula de nível em branco não é comparada. |
| Uma linha deixa a 归类依据 vazia. | `HC-003` reporta essa linha: `basis` tem de estar preenchido em todas as linhas que trazem a coluna. Verifica que algo esteja escrito, não que a disposição pautal, a nota de capítulo, a decisão de classificação ou a informação pautal vinculativa citadas existam ou sustentem a classificação — este plugin não consulta nada disso. Se o registo não tiver coluna `basis`, `HC-003` aparece em `skipped` a indicar que o material não tem essa coluna, em vez de passar em silêncio. |
| O cabeçalho não diz a que versão da pauta pertencem os códigos. | `HC-004` exige que o cabeçalho declare `tariffVersion` e reporta o registo quando o deixa vazio. Verifica que a declaração exista, não que a edição indicada seja a destes códigos: a regra não lê os códigos, e os códigos são divididos e fundidos entre edições. A sua lista `fields` é uma definição do pacote de regras: acrescente `declarant` se o seu cabeçalho o registar. |
| O 项号 5 aparece em duas linhas. | `HC-005` reporta a linha posterior como duplicada da anterior, porque `itemNo` tem de ser único dentro do mesmo registo; a comparação ignora espaços, por isso `5` e ` 5 ` são o mesmo número de item. Verifica apenas a unicidade. Uma mercadoria declarada em várias linhas, por especificações diferentes, precisa de um número de item diferente em cada uma. Mesmo sem números repetidos, `HC-005` continua a aparecer em `skipped`: aí com o motivo de que o material cumpre as precondições da verificação e não foram encontradas entradas divergentes, um motivo diferente do que é dado quando a regra não pode ser executada por faltar a coluna. |
| A coluna 品名 ainda tem 【】 ou 待填 do modelo. | `HC-006` reporta a linha e o marcador que encontrou. O pacote de regras procura 【, 】, {{, }}, XXX, xxx, 待填, 待补充, TBD, todo e 示例, e `terms` pode ser ajustado ao seu próprio modelo. Procura apenas marcadores não substituídos: não julga se o nome está correto e também não exige que a coluna esteja preenchida — uma célula `description` vazia não lhe produz qualquer achado, e nenhuma outra regra deste pacote a exige. |

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 《中华人民共和国进出口税则》 | 现行版本本次未核实 | HC-001, HC-004, HC-005, HC-006 |
| 《商品名称及编码协调制度》 | 现行版本本次未核实 | HC-002 |
| 《中华人民共和国进出口关税条例》 | 国务院令第392号（2003年11月23日公布；根据2011年1月8日、2013年12月7日、2016年2月6日三次《国务院关于修改（废止）部分行政法规的决定》修订） | HC-003 |

**Boundary:** this plugin checks a **商品归类台账** for the *structure* of the numbers it records — that a
commodity code is ten digits, that its chapter, heading and subheading are successive prefixes of it, that the
levels get progressively finer, that a classification basis is recorded, that the tariff version is declared,
that item numbers are unique, and that no placeholder survives. It does **not** decide which code goods should
be classified under.

> ### ⚠️ It checks the shape of a code, never whether the code is right
>
> **Classification is a customs determination**, turning on the goods' material, function and degree of
> processing together with the tariff's section and chapter notes and any classification decisions or advance
> rulings. **This plugin does not consult the tariff, does not consult classification decisions, and does not
> consult rulings.** So:
>
> - it **can** find "this row's code disagrees with the chapter, heading and subheading the same row states";
> - it **cannot** find "this row's code does not match the goods", because that needs the tariff itself.
>
> A register with a structurally perfect code for the wrong goods passes this plugin. That is the documented
> limit, stated in the header, in `HC-002`'s note, and in the troubleshooting section.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The
> regime lives in 《中华人民共和国进出口税则》— whose codes are ten digits, the first six being the WCO
> Harmonized System — and 《中华人民共和国进出口关税条例》. The verification pass could not retrieve
> verbatim clause text, so the pack states the gap in the `excerpt` field itself and keeps every rule at
> `warn` or `info`. **When the texts are in hand, replace each `excerpt` with the real clause and raise `kind`
> to `direct`.** The ten-digit assumption is a `pattern` in the rule pack, so an annual tariff change needs a
> rule-pack edit, not a code change.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-hs-classify
dsh --profile <name> --dump-config | grep 'dsh-hs-classify'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/hs-classify.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-hs-classify
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hs-classify contributors.
