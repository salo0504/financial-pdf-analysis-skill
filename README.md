# Financial PDF Analysis — Claude Skill

A Claude skill for extracting sourced, page-cited data from financial
PDFs — government budgets, CAFRs/ACFRs, nonprofit 990s, audited
financial statements, and grant reports. Built by the Economy League of
Greater Philadelphia (ELGP) for use by GRA-affiliated research
organizations.

## What it does

Give it a financial PDF and a research question, and it will:
- Pull the figures you need with a page citation on every one
- Flag unit mismatches (thousands vs. actual dollars), OCR'd or
  low-confidence figures, and internal inconsistencies rather than
  guessing past them
- Produce either a formatted Excel workbook, a written summary, or both

## Install (takes about a minute)

1. Go to this repo's **[Releases page](../../releases)** and download
   the latest `financial-pdf-analysis.zip`.
2. In Claude, go to **Customize → Skills → Upload skill** and upload
   the zip you just downloaded.
3. That's it. Ask Claude to analyze a budget, CAFR, 990, or similar PDF,
   and it'll use the skill automatically.

No coding, no configuration, no GitHub account needed.

## Staying up to date

The skill checks this repo for a newer version each time it runs. If
one's available, Claude will mention it at the end of its response with
a link back here. It never auto-downloads anything — you'll just need
to repeat the two install steps above with the new zip when you see
that notice.

If your organization's Claude account has network access restricted (a
common setting on Team/Enterprise plans), the update check will simply
not run — the skill itself still works fine either way. Check this
repo's `CHANGELOG.md` periodically if you're not seeing update notices
and want to confirm you're current.

## Questions / issues

Contact [ELGP contact info here] or open an issue on this repo.

## Version

Current: see [`VERSION`](VERSION). Changes: see [`CHANGELOG.md`](CHANGELOG.md).
