# dsh-hs-classify — 商品归类层级一致性核对

`dsh-hs-classify` 读取一份商品归类台账——表头加每个商品项一行——核对其中编号的结构：商品编号是否为十位数字、章／品目／子目是否为该编号的逐级前缀、层级是否由粗到细、每行是否填写归类依据、表头是否声明商品编号适用的税则版本、项号是否在台账内唯一、品名栏是否残留未替换的占位符。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 台账里的编号有的是八位，还有一个末位是字母，会被报出吗？ | 会。`HC-001` 把每个已填写的 `hsCode` 与规则库的 `pattern`（`^[0-9]{10}$`）比对，报出该行并附上它读到的值。它只核对位数与字符合法性，绝不判断该商品是否应归入这个编号。编号栏留空的不在本条范围内，所以它报的是形式不对的编号，不是缺填的编号。十位是规则库配置：年度税则改了位数，改 `pattern` 即可，不必改代码。 |
| 某行的章、品目、子目与商品编号对不上，能查出来吗？ | 能。`HC-002` 按由粗到细的顺序读取层级栏——章、品目、子目，规则库自己的示例为 2、4、6 位——报出不是所读 `hsCode` 前缀的那一栏，或不比上一级更细的那一栏。它只核对这一前缀关系与这一顺序：编号是否适用于该商品属海关的归类判断，要查税则与归类决定，本插件不查这些。层级栏留空的不作比较。 |
| 有一行的归类依据是空的。 | `HC-003` 会报出这一行：凡是带这一栏的行，`basis` 都必须填写。它只核对该栏写了没有，不核对所引税则条文、章注、归类决定或预裁定是否存在、是否支持该归类——这些本插件都不查。台账若完全没有 `basis` 栏，`HC-003` 会在 `skipped` 中说明「材料没有『basis』列，本条不适用」，而不是静默通过。 |
| 表头没有声明这些编号适用哪一版税则。 | `HC-004` 要求表头声明 `tariffVersion`，表头留空即报出该台账。它只核对声明在不在，不判断所写的版本是不是这些编号所属的那一版——本条不读编号，而编码会在各版税则之间拆分与合并。它检查的 `fields` 是规则库配置：表头还记申报人的话，把 `declarant` 加进去即可。 |
| 项号 5 在两行里各出现一次。 | `HC-005` 会把后一行报为与前行重复：`itemNo` 在同一台账内应唯一，比较时忽略空白字符，所以 `5` 与 ` 5 ` 是同一个项号。它只核对唯一性。同一商品分多行申报（例如不同规格）时，每行要用不同的项号。项号全都不重复时，`HC-005` 仍会出现在 `skipped` 中：此时给的理由是「材料满足该检查的前置条件且未发现差异条目」，与规则因缺列而无法执行时给的理由不同。 |
| 品名栏还留着模板里的【】或待填。 | `HC-006` 会报出该行以及它匹配到的占位符。规则库查找的是【、】、{{、}}、XXX、xxx、待填、待补充、TBD、todo 与 示例，`terms` 可按本机构模板增减。它只找未替换的占位符：不判断品名对不对，也不要求这一栏必须填写——`description` 单元格留空不会产生差异条目，本规则库中也没有别的规则要求填写品名。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-hs-classify
dsh --profile <name> --dump-config | grep 'dsh-hs-classify'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/hs-classify.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-hs-classify
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hs-classify contributors.
