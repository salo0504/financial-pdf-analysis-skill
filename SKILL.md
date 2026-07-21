# Extraction schema

Every line item pulled from a financial PDF should become one object in
an `items` array, matching this shape (this is what `build_workbook.py`
consumes):

```json
{
  "id": 1,
  "line_item": "General Fund - Total Revenue",
  "value": 1234567,
  "unit": "actual_dollars",
  "fiscal_year": "FY2025",
  "period": "adopted",
  "fund_or_category": "General Fund",
  "page": 42,
  "table_or_section": "Table 3: Revenue Summary",
  "notes": "Excludes one-time ARPA transfer of $8.1M",
  "confidence": "high"
}
```

Field notes:

- **value**: always the raw number as printed, scaled by `unit` — do not
  pre-convert. If the source table is "in thousands" and shows `1,234`,
  record `value: 1234, unit: "thousands"` — let the workbook script apply
  formatting. Silently converting to actual dollars in your head is the
  single most common source of order-of-magnitude errors in this kind of
  work.
- **unit**: one of `actual_dollars`, `thousands`, `millions`. Always check
  the table header or column note for "(in thousands)" / "(000s omitted)"
  — it's easy to miss and changes every number by 1000x.
- **period**: `adopted` | `proposed` | `actual` | `estimated` | `audited`
  | `unaudited`. Government budgets routinely show all of these side by
  side for the same fiscal year (e.g. "FY24 Adopted" vs "FY24 Actual") —
  never merge them into one figure without preserving which column it
  came from.
- **fiscal_year**: use the entity's own fiscal year label as printed (a
  City fiscal year may run July–June; a federal one Oct–Sept; a nonprofit
  990 covers its own accounting period). Don't normalize to calendar year
  — record what the document says and note the FY start/end once at the
  top of your summary if it's not calendar-aligned.
- **page**: the PDF page number as it appears in your extracted
  `pages.json` (1-indexed from the start of the file), not the printed
  page number in the document footer — those two frequently diverge
  (title pages, roman-numeral front matter). If you cite the printed
  page number instead, say so explicitly so it's not ambiguous later.
- **confidence**: `high` for clean text-layer extraction you're sure of,
  `medium` for anything sourced from an OCR'd page (digits are the most
  common OCR error — a `3` misread as `8`, a `1` as `7`), `low` for
  anything you're inferring rather than reading directly (e.g. an implied
  total that isn't itself printed).

## Common misreads to actively check for

- **Parenthetical numbers** — `(1,234)` means negative in nearly all
  financial reporting. Don't drop the sign.
- **Restated prior-year figures** — a footnote reading "as restated" or
  "reclassified" means the prior-year comparative in this document won't
  match what last year's report said. Note it rather than treating the
  two documents as directly comparable.
- **Subtotal/total mismatches** — if you extract a set of line items that
  should sum to a printed total, check the arithmetic. A mismatch usually
  means a mis-scanned digit or a missed line item, not a documentation
  error — re-examine before reporting either number.
- **Rule-line artifacts in text extraction** — dense financial statements
  often use dot-leaders or underline rules between labels and figures.
  Plain text extraction (pdfplumber's `extract_text()`, `pdftotext`) can
  interleave stray underscores or dashes into the digits themselves
  (e.g. a total rendered as `1_1__7_,2_0_8_,_2_2_8` instead of
  `117,208,228`). This is common on borderless statement pages (fund
  statements, revenue/expenditure summaries) and is easy to miss since
  the number *looks* plausible at a glance. Cross-check any figure that
  looks visually noisy against `camelot` (`flavor="stream"`) output or a
  rasterized read of the page before recording it — don't hand-clean the
  underscores out and assume you reconstructed it correctly.
- **Fund vs. entity-wide figures** — municipal budgets report by fund
  (General, Enterprise, Capital, Debt Service...) as well as
  entity-wide/consolidated totals. Extracting a fund-level number and
  presenting it as the entity total (or vice versa) is a common and
  serious error. Always record `fund_or_category`.
- **Basis of accounting** — cash basis vs. accrual/modified accrual
  changes what a number means (e.g. encumbrances, accounts payable
  timing). CAFRs typically show both governmental funds (modified
  accrual) and government-wide (full accrual) statements — note which
  one a figure came from if the document distinguishes them.
