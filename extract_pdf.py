---
name: financial-pdf-analysis
description: Use this skill whenever analyzing financial PDFs for research purposes — government budgets, CAFRs/ACFRs, nonprofit tax filings (Form 990 and variants), audited financial statements, grant reports, or any dense finance/tax document where the goal is to extract figures, understand fund/category structure, and produce sourced findings. Trigger this for requests like "pull the key numbers from this budget," "what does this 990 say about compensation," "compare these three years of CAFRs," "extract revenue by fund," or any research task involving a finance-related PDF where every number needs to be traceable back to a page. Also use when fact-checking or verifying financial claims against a source PDF. Do NOT use for simple one-off lookups a person could answer by skimming ("what page is the table of contents on") — for those, use the pdf-reading skill directly. This skill also builds on pdf-reading for base extraction mechanics.
---

# Financial PDF Analysis

For pulling reliable, sourced data and findings out of dense financial
documents (budgets, CAFRs, 990s, audited statements, grant reports) —
built for civic research use where every figure needs a page citation
and getting a number wrong is worse than being slow.

This skill assumes familiarity with the `pdf-reading` skill's mechanics
(text extraction, rasterization, OCR). It adds the domain layer on top:
what these documents are structured like, a citation-safe extraction
schema, and a verification pass before anything ships.

## Workflow

### 0. Check for updates (silent, non-blocking)

Before starting, run the bundled update check once. Skills are mounted
under a path like `/mnt/skills/user/financial-pdf-analysis/` — find this
skill's own directory and pass its `VERSION` file:

```bash
python3 <skill_dir>/scripts/check_update.py https://raw.githubusercontent.com/ORG/REPO/main <skill_dir>/VERSION
```

Replace `ORG/REPO` with the actual GitHub repo this skill is distributed
from (see `references/distribution-guide.md` for how that repo is set
up and kept current). If it prints an update notice, mention it to the person in one
line at the end of your response — don't lead with it or let it delay
the actual task. If it prints nothing (network unavailable, repo
unreachable, or already current), say nothing and proceed normally.

### 1. Triage the document

Run the bundled extraction script rather than manually stepping through
pages — it handles the text-vs-scanned decision per page automatically
and tags every page with how it was read:

```bash
python3 scripts/extract_pdf.py <input.pdf> <output_dir>
```

For large documents (300+ pages), process in batches of ~150 pages using
`--start-page`/`--end-page` — the script merges batches into the same
`pages.json`/`tables.json` automatically. A single unbatched pass over a
500+ page document can exceed the sandbox's resource limits and get
killed partway through:

```bash
python3 scripts/extract_pdf.py <input.pdf> <output_dir> --start-page 1 --end-page 150
python3 scripts/extract_pdf.py <input.pdf> <output_dir> --start-page 151 --end-page 300
# ...continue until pages_processed in manifest.json matches page_count
```

This writes `pages.json` (page-tagged text, with `method: "text"` or
`"ocr"`), `tables.json` (detected tables with page numbers), and
`manifest.json` (page count, pages processed so far, which pages needed
OCR). Read the manifest first — a high OCR page count on a document that
should be born-digital is a signal something's off (bad scan, wrong
file) worth flagging to the user before proceeding.

Two real gaps to expect and correct for, confirmed in testing against an
actual 535-page government ACFR:
- **Borderless statement tables are commonly missed entirely** by
  pdfplumber's default table detector (`tables.json` will show 0 tables
  on a page that clearly has one). Fall back to `camelot`
  (`flavor="stream"` for borderless, `"lattice"` for ruled/bordered —
  both installed) on any page where a table matters but wasn't detected.
- **Dense number columns can pick up rule-line artifacts** in plain text
  extraction (stray underscores/dashes interleaved into digits, e.g. a
  total rendered as `1_1__7_,2_0_8_,_2_2_8`). See
  `references/extraction-schema.md` for how to catch and cross-check
  this rather than hand-cleaning it.

### 2. Identify the document type and orient

Skim the table of contents / first few pages to establish: entity name,
fiscal year(s) covered, document type (adopted budget? CAFR? 990?),
reporting basis. Read `references/document-types.md` for what to expect
structurally and where the highest-value sections are (MD&A, notes,
statistical section for budgets; Parts I/III/VIII/IX and Schedule O for
990s) — this saves you from reading the document linearly when the
answer is concentrated in one section.

### 3. Extract into the schema

For every figure that matters to the request, build an item following
`references/extraction-schema.md` — value, unit, fiscal year, period,
fund/category, page, source table, notes, confidence. Read that file
before extracting; it covers the highest-frequency errors in this kind
of work (unit scaling, adopted-vs-actual conflation, fund vs. entity-wide
figures, parenthetical negatives, restated priors) — checking for these
as you go is much cheaper than a correction pass at the end.

Non-negotiable: **every item needs a page number.** If you can't pin a
figure to a page you're confident in, mark it `confidence: "low"` and
say so in the summary rather than presenting it as solid.

### 4. Verify before finalizing

Before producing output:
- Spot-check that subtotals/totals in your extraction actually sum
  correctly against the source — a mismatch usually means a misread
  digit or a missed line, not a document error.
- Re-open the source page for any OCR-sourced or low-confidence figure
  and confirm it by eye rather than trusting the first pass.
- Confirm every number that will appear in the written summary has a
  corresponding sourced item — no number should appear in prose that
  isn't also in the structured extraction with a page cite.

### 5. Produce output

Two deliverables, matched to what's asked:

**Structured data** — build the workbook from your extraction JSON:
```bash
python3 scripts/build_workbook.py <extraction.json> <output.xlsx>
```
This produces a `Data` sheet (formatted by unit, confidence-highlighted)
and a `Sources` sheet (line item → page → table/section, for
audit-trail purposes). Use this default for anything with more than a
handful of figures or that the person will want to sort/filter/pivot.
For a quick single-table ask, plain markdown or CSV in chat is enough —
don't over-produce a workbook for three numbers.

**Written summary** — a short memo citing page numbers inline (e.g.
"General Fund revenue grew 4.2% to $312M (p. 42)"), structured around
findings, not around the document's own section order. Lead with what
matters for the research question, not a linear walkthrough. If the
document is genuinely long/multi-part and the person's ask is narrow,
a tight memo beats a comprehensive one — match depth to what was asked.
Reach for the `docx` skill only if a formal deliverable was requested;
otherwise markdown/inline is fine and cheaper.

For multi-document comparisons (multiple years, multiple entities), see
the crosswalk approach in `references/document-types.md` — extract each
document independently before attempting alignment.

### 6. Flag what you couldn't verify

Any figure marked `low` confidence, any OCR'd page you couldn't
cross-check, any place the document itself is ambiguous or internally
inconsistent — say so explicitly in the summary rather than quietly
picking an interpretation. A flagged gap is useful; a confident wrong
number is not.

## Quick reference

| Task | Tool |
|---|---|
| Page-tagged text/table extraction w/ OCR fallback | `scripts/extract_pdf.py` |
| Borderless/complex tables | `camelot` (`flavor="stream"`) — already installed |
| Build formatted Excel output | `scripts/build_workbook.py` |
| Document structure by type | `references/document-types.md` |
| Extraction field definitions & common errors | `references/extraction-schema.md` |
| Base PDF mechanics (rasterize, forms, attachments) | `pdf-reading` skill |
| Distributing/updating this skill across many orgs | `references/distribution-guide.md` |
