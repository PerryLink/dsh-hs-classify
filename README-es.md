# dsh-hs-classify — Verificación de la coherencia jerárquica del registro de clasificación de mercancías

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-hs-classify` lee un registro de clasificación de mercancías —la cabecera del declarante más una fila por partida— y comprueba la estructura de los números que registra: que el código de mercancía tenga diez dígitos, que el capítulo, la partida y la subpartida sean prefijos sucesivos de ese código, que los niveles vayan de lo general a lo específico, que cada fila registre una base de clasificación, que la cabecera declare la versión del arancel a la que pertenecen los códigos, que los números de ítem sean únicos en el registro y que no quede ningún marcador de plantilla sin sustituir en la denominación.

## Cómo se ve la salida

![Terminal demo of dsh-hs-classify: real output over its HC-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-hs-classify/main/docs/assets/dsh-hs-classify-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `HC-001` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Algunos códigos del registro tienen ocho dígitos y uno termina en letra. ¿Se informa de ellos? | Sí. `HC-001` contrasta cada `hsCode` relleno con el `pattern` del paquete de reglas, `^[0-9]{10}$`, e informa de la fila junto con el valor que leyó. Solo comprueba el número de dígitos y los caracteres, nunca si la mercancía corresponde a ese código. Una celda de código vacía no se mira: lo que informa es un código con la forma incorrecta, no un código que falta. Los diez dígitos son un ajuste del paquete de reglas: cuando el arancel anual cambie la longitud, se edita el `pattern`, no el código. |
| El 章, el 品目 y el 子目 de una fila no concuerdan con su 商品编号. ¿Se detecta? | Sí. `HC-002` lee las columnas de nivel de lo general a lo específico —章, 品目 y 子目, dos, cuatro y seis dígitos en el ejemplo del propio paquete de reglas— e informa del nivel que no es prefijo del `hsCode` leído, o que no es más fino que el nivel anterior. Solo comprueba esa relación de prefijo y ese orden: si el código corresponde a la mercancía es una determinación aduanera que exige el arancel y las decisiones de clasificación, que este plugin no consulta. Una celda de nivel vacía no se compara. |
| Una fila deja vacía la 归类依据. | `HC-003` informa de esa fila: `basis` debe estar relleno en todas las filas que llevan la columna. Comprueba que haya algo escrito, no que la disposición arancelaria, la nota de capítulo, la decisión de clasificación o el dictamen anticipado citados existan o respalden la clasificación: este plugin no consulta nada de eso. Si el registro no tiene columna `basis`, `HC-003` aparece en `skipped` indicando que el material no tiene esa columna, en lugar de pasar en silencio. |
| La cabecera no dice a qué versión del arancel pertenecen los códigos. | `HC-004` exige que la cabecera declare `tariffVersion` e informa del registro cuando la deja vacía. Comprueba que la declaración esté presente, no que la edición nombrada sea la de estos códigos: la regla no lee los códigos, y los códigos se dividen y se fusionan entre ediciones. Su lista `fields` es un ajuste del paquete de reglas: añada `declarant` si su cabecera lo registra. |
| El 项号 5 aparece en dos filas. | `HC-005` informa de la fila posterior como duplicada de la anterior, porque `itemNo` debe ser único dentro de un mismo registro; la comparación ignora los espacios, así que `5` y ` 5 ` son el mismo número de ítem. Solo comprueba la unicidad. Una mercancía declarada en varias filas, por especificaciones distintas, necesita un número de ítem distinto en cada una. Aunque no haya ningún número repetido, `HC-005` sigue apareciendo en `skipped`: entonces con el motivo de que el material cumple las precondiciones de la comprobación y no se hallaron entradas divergentes, un motivo distinto del que da una regla cuando no puede ejecutarse porque falta la columna. |
| La columna 品名 todavía tiene 【】 o 待填 de la plantilla. | `HC-006` informa de la fila y del marcador que encontró. El paquete de reglas busca 【, 】, {{, }}, XXX, xxx, 待填, 待补充, TBD, todo y 示例, y `terms` se puede recortar a su propia plantilla. Solo busca marcadores sin sustituir: no juzga si el nombre es correcto y tampoco exige que la columna esté rellena: una celda `description` vacía no le produce ningún hallazgo, y ninguna otra regla de este paquete la exige. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/hs-classify.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

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
