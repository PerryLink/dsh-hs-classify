#!/usr/bin/env node
/**
 * Public-data end-to-end benchmark for dsh-hs-classify.
 *
 * Input: current USITC HTS export (U.S. Government work, public domain).
 * The adapter maps real HTS lines to the ledger shape; the evaluator then
 * injects one labelled hierarchy/format defect per case and calls the real
 * plugin tool from ../../lib/index.mjs.
 *
 * This tests hierarchy/format self-consistency, not whether an HTS line is the
 * correct classification for a product.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import * as plugin from '../../lib/index.mjs'

const here = dirname(fileURLToPath(import.meta.url))
const input = process.argv[2] ?? join(here, 'cases.json')
const limit = Number(process.argv[3] ?? 20)
const table = JSON.parse(readFileSync(input, 'utf8'))
const rows = table.rows.slice(0, limit)

const registered = []
plugin.apply({ tools: { register: (tool) => { registered.push(tool); return () => {} } } }, plugin.Config ? plugin.Config({}) : {})
const tool = registered.find((item) => item.name === plugin.TOOL_NAME)
if (!tool) throw new Error('hs-classify tool not registered')

const mutate = {
  'HC-001': (row) => ({ ...row, 商品编号: row.商品编号.slice(0, 9) }),
  'HC-002': (row) => ({ ...row, 章: '99' }),
  'HC-003': (row) => ({ ...row, 归类依据: '' }),
  'HC-004': null,
  'HC-005': (row) => ({ ...row, 序号: 'DUPLICATE' }),
  'HC-006': (row) => ({ ...row, 品名: '【待填】' }),
}

async function run(payload) {
  const result = await tool.execute({ material: JSON.stringify(payload) }, { signal: new AbortController().signal })
  const report = JSON.parse(result.reportJson)
  return (report.issues ?? []).map((issue) => issue.ruleId)
}

const byRule = []
for (const [rule, mutateOne] of Object.entries(mutate)) {
  let tp = 0, fp = 0, fn = 0, tn = 0
  for (const base of rows) {
    const clean = { ...table, rows: [base] }
    let positive
    if (rule === 'HC-005') {
      positive = { ...table, rows: [base, { ...base }] }
    } else if (rule === 'HC-004') {
      positive = { ...table, rows: [base] }
      delete positive.tariffVersion
    } else {
      positive = { ...table, rows: [mutateOne(base)] }
    }
    const cleanIssues = await run(clean)
    if (cleanIssues.includes(rule)) { fp += 1 } else { tn += 1 }
    const positiveIssues = await run(positive)
    if (positiveIssues.includes(rule)) { tp += 1 } else { fn += 1 }
  }
  const precision = tp + fp === 0 ? null : tp / (tp + fp)
  const recall = tp + fn === 0 ? null : tp / (tp + fn)
  byRule.push({ rule, tp, fp, fn, tn, precision, recall })
}

const total = { tp: 0, fp: 0, fn: 0, tn: 0 }
for (const row of byRule) { total.tp += row.tp; total.fp += row.fp; total.fn += row.fn; total.tn += row.tn }
const precision = total.tp + total.fp === 0 ? null : total.tp / (total.tp + total.fp)
const recall = total.tp + total.fn === 0 ? null : total.tp / (total.tp + total.fn)
const output = {
  dataset: 'USITC HTS current export (U.S. Government work; public domain)',
  source: 'https://hts.usitc.gov/reststop/exportList?from=0101&to=9999.99.99.99&format=JSON&styles=false',
  license: 'public domain (US federal work)',
  rows: rows.length,
  generatedAt: new Date().toISOString(),
  scoredRules: byRule,
  total: { ...total, precision, recall },
  limitations: [
    'HTS lines are valid hierarchy examples, not product-specific classification ground truth.',
    'The benchmark tests the plugin hierarchy/format rules only; it does not test whether a product belongs to the code.',
    'HTS is U.S. tariff nomenclature, not the Chinese 10-digit tariff schedule.',
  ],
}
writeFileSync(join(here, 'summary.json'), JSON.stringify(output, null, 2) + '\n')
console.log(`rows: ${rows.length}`)
console.log(`precision ${precision === null ? 'n/a' : precision.toFixed(3)} · recall ${recall === null ? 'n/a' : recall.toFixed(3)} (TP ${total.tp} FP ${total.fp} FN ${total.fn} TN ${total.tn})`)
for (const row of byRule) console.log(`  ${row.rule}: TP ${row.tp} FP ${row.fp} FN ${row.fn} TN ${row.tn}`)
