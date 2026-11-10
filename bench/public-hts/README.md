# Public-data benchmark: USITC HTS

End-to-end benchmark for `dsh-hs-classify` using the current U.S.
Harmonized Tariff Schedule export.

- Source: <https://hts.usitc.gov/reststop/exportList>
- Publisher: U.S. International Trade Commission
- License: **U.S. Government work; public domain in the United States**
  (data.gov `http://www.usa.gov/publicdomain/label/1.0/`)
- The 13 MB JSON export is downloaded by `fetch.mjs` and is **not** committed.
- The HTS is U.S. tariff nomenclature, not the Chinese 10-digit tariff
  schedule; this benchmark tests hierarchy/format self-consistency, not
  product-specific classification.

## Method

1. `fetch.mjs` downloads the current JSON export.
2. `adapter.mjs` selects real 10-digit HTS lines and maps them to the ledger
   fields: chapter/heading/subheading are derived from the HTS number; the
   description and `basis` quote the HTS line.
3. `evaluate.mjs` calls the real `hs_classify` tool from
   `../../lib/index.mjs`; for each of the six rules it uses clean lines as
   negatives and one-defect clones as positives.
4. `summary.json` records per-rule P/R.

## Run

```bash
node bench/public-hts/fetch.mjs
node bench/public-hts/adapter.mjs bench/public-hts/.data/hts-current.json bench/public-hts/cases.json 20
node bench/public-hts/evaluate.mjs bench/public-hts/cases.json 20
```

The P/R is detection on injected format/hierarchy defects; it is not an
estimate of tariff classification accuracy. The plugin itself explicitly does
not decide the correct code for a product.
