# Results — USITC HTS public benchmark

Rows: 20; source: USITC HTS current export (U.S. Government work; public domain)

**Overall: precision 1.000 · recall 1.000 (TP 120 · FP 0 · FN 0 · TN 120)**

| rule | TP | FP | FN | TN | precision | recall |
|---|---:|---:|---:|---:|---:|---:|
| HC-001 | 20 | 0 | 0 | 20 | 1.000 | 1.000 |
| HC-002 | 20 | 0 | 0 | 20 | 1.000 | 1.000 |
| HC-003 | 20 | 0 | 0 | 20 | 1.000 | 1.000 |
| HC-004 | 20 | 0 | 0 | 20 | 1.000 | 1.000 |
| HC-005 | 20 | 0 | 0 | 20 | 1.000 | 1.000 |
| HC-006 | 20 | 0 | 0 | 20 | 1.000 | 1.000 |

## Limits

- HTS lines are valid hierarchy examples, not product-classification ground truth.
- The plugin checks hierarchy/format only; it does not decide whether a product belongs to an HTS code.
- HTS is U.S. nomenclature, not the Chinese tariff schedule.
- Positives are one-defect clones, so P/R is a regression signal, not prevalence.

