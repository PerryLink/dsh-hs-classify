#!/usr/bin/env node
/**
 * Adapt USITC HTS lines to the dsh-hs-classify ledger contract.
 *
 * Mapping:
 *   htsno "8471.30.01.00" -> hsCode "8471300100", chapter "84",
 *   heading "8471", subheading "847130".
 *
 * The HTS line is a real tariff line; the case's `basis` quotes the HTS
 * description, not a fabricated customs ruling. The plugin checks hierarchy
 * self-consistency, not whether the code is the correct classification for a
 * particular product.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))

export function buildCases(lines, limit = 20) {
  const rows = []
  for (const line of lines) {
    const htsno = String(line.htsno ?? '').trim()
    const code = htsno.replace(/\./g, '')
    if (!/^\d{10}$/.test(code)) continue
    if (!line.description || !String(line.description).trim()) continue
    rows.push({
      序号: String(rows.length + 1),
      品名: String(line.description).trim().slice(0, 300),
      章: code.slice(0, 2),
      品目: code.slice(0, 4),
      子目: code.slice(0, 6),
      商品编号: code,
      申报日期: '2026-11-10',
      归类依据: `HTS ${htsno}: ${String(line.description).trim().slice(0, 300)}`,
      备注: 'public HTS line; hierarchy only',
    })
    if (rows.length >= limit) break
  }
  return {
    declarant: 'public benchmark',
    tariffVersion: 'HTS current (USITC)',
    checkedAt: '2026-11-10',
    rows,
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const input = process.argv[2] ?? join(here, '.data', 'hts-current.json')
  const output = process.argv[3] ?? join(here, 'cases.json')
  const limit = Number(process.argv[4] ?? 20)
  const lines = JSON.parse(readFileSync(input, 'utf8'))
  if (!Array.isArray(lines)) throw new Error('HTS export must be an array')
  const table = buildCases(lines, limit)
  writeFileSync(output, JSON.stringify(table, null, 2) + '\n')
  console.log(`wrote ${output}: ${table.rows.length} rows`)
}
