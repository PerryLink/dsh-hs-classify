/**
 * dsh-hs-classify — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'hs_classify'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  itemNo: ['序号', '项号', '编号', 'itemNo'],
  description: ['品名', '商品名称', '货物名称', 'description'],
  material: ['材质', '材料', '成分', 'material'],
  function: ['功能', '用途', '工作原理', 'function'],
  chapter: ['章', '章号', '第几章', 'chapter'],
  heading: ['品目', '四位品目', '品目号', 'heading'],
  subheading: ['子目', '六位子目', '子目号', 'subheading'],
  hsCode: ['商品编号', 'HS编码', '税则号列', 'hsCode'],
  declaredAt: ['申报日期', '归类日期', 'declaredAt'],
  basis: ['归类依据', '归类理由', '依据', 'basis'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'classifications', '归类'],
  columns: COLUMNS,
  header: {
  declarant: ['declarant', '申报人', '归类人'],
  tariffVersion: ['tariffVersion', '税则版本', '适用年度税则'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '商品编号',
  'hsCode',
  '品名',
  'description',
  '章',
  'chapter',
  '品目',
  'heading',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
