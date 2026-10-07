# dsh-hs-classify

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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a customs declaration's item list use `ptc` |

## What it does

Registers the `hs_classify` tool. It reads one classification register — the declarant header plus one row per
item — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `HC-001` | the commodity code is ten digits | warn | principle |
| `HC-002` | chapter, heading and subheading are successive prefixes | warn | principle |
| `HC-003` | a classification basis is recorded | warn | principle |
| `HC-004` | the tariff version is declared | warn | principle |
| `HC-005` | item numbers are unique | warn | principle |
| `HC-006` | the description holds no unreplaced placeholder | warn | principle |

## Install

```sh
pnpm pack
dsh plugin --profile <name> add ./dsh-hs-classify-0.1.0.tgz
dsh --profile <name> --dump-config | grep 'dsh-hs-classify'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/hs-classify.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `HC-001` `pattern` — the code's shape, ten digits by default. Change it when the tariff changes.
- `HC-002` `field` / `components` / `digits` — the code column, the level columns in coarse-to-fine order
  (`[chapter, heading, subheading]`), and the expected total length.
- `HC-004` `fields` — header fields that must be present; the tariff version by default. Add `declarant` if
  your register records one.
- `HC-006` `terms` — the placeholders to look for.

## Material format

The tool accepts JSON or YAML:

```yaml
declarant: 某某报关行
tariffVersion: 2026 年版税则
rows:
  - { 序号: '1', 品名: 便携式自动数据处理设备, 材质: 塑料外壳、金属结构件、电子元器件,
      功能: 数据处理与显示，重量 1.2 千克, 章: '84', 品目: '8471', 子目: '847130',
      商品编号: '8471300000', 申报日期: 2026-03-10,
      归类依据: 税则第八十四章章注及品目 8471 条文 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read.

## Rule sources

Rule data lives in `rules/hs-classify.yaml`. The pack's header states what the plugin does and does not judge,
and each rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces
"an excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **It did not flag a code I know is wrong for the goods.** It cannot: it checks the code's internal structure,
  not its fit to the goods. Classification needs the tariff and the notes.
- **`HC-002` fires although the code looks right.** One of the level columns disagrees with the code's leading
  digits. The finding names the level and shows both values.
- **`HC-001` fires on a valid code from last year's tariff.** Digits can change with the annual tariff. Correct
  the code, or adjust the `pattern` if this year's tariff really differs.
- **`HC-004` reports itself as skipped.** The header carries no tariff version. Which tariff a code belongs to
  matters, because codes are split and merged between editions.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-hs-classify@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-hs-classify   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hs-classify contributors.
