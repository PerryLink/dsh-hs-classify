#!/usr/bin/env node
/**
 * Fetch the current US Harmonized Tariff Schedule (HTS) from the official
 * USITC REST export endpoint.
 *
 * Source: https://hts.usitc.gov/reststop/exportList
 * Publisher: U.S. International Trade Commission
 * License: U.S. Government work; public domain in the United States
 *          (data.gov license http://www.usa.gov/publicdomain/label/1.0/).
 *
 * The full export is large and changes with revisions; it is not committed.
 */
import { mkdir, writeFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const target = join(here, '.data', 'hts-current.json')
const url = 'https://hts.usitc.gov/reststop/exportList?from=0101&to=9999.99.99.99&format=JSON&styles=false'

const response = await fetch(url)
if (!response.ok) throw new Error(`download failed: ${response.status} ${response.statusText}`)
const text = await response.text()
if (!text.trimStart().startsWith('[')) throw new Error('download did not return a JSON array')
await mkdir(dirname(target), { recursive: true })
await writeFile(target, text)
console.log(`wrote ${target} (${text.length} bytes)`)
