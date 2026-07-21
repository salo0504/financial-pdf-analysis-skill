# Changelog

## 1.0.0 — 2026-07-20

Initial release.

- Page-tagged text/table extraction with automatic OCR fallback
  (`scripts/extract_pdf.py`)
- Structured extraction schema with mandatory page citations, unit
  tracking, and confidence flags (`references/extraction-schema.md`)
- Document-type guidance for government budgets/CAFRs, nonprofit 990s,
  and general financial statements (`references/document-types.md`)
- Excel workbook builder with Data + Sources sheets
  (`scripts/build_workbook.py`)
- Self-update check against this repo (`scripts/check_update.py`)

Tested against a real 535-page government ACFR: confirmed page-batching
is needed for documents over ~150 pages, and confirmed that dense
borderless statement tables need a `camelot` (stream mode) fallback —
both are documented in `references/extraction-schema.md`.
