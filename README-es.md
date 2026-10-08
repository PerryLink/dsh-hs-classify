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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-hs-classify
dsh --profile <name> --dump-config | grep 'dsh-hs-classify'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`. Las claves y los parámetros de cada regla están en [README.md](README.md#configuration) (versión principal en inglés).

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-hs-classify
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hs-classify contributors.
