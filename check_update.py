# Distribution guide: sharing this skill with 60+ external orgs

This covers hosting the skill on GitHub, how the built-in update check
works, what it costs you to maintain, and what each org needs to do.

## 1. One-time setup (you, ELGP)

**Create a public GitHub repo.** Something like
`github.com/ELGP-PHL/financial-pdf-analysis-skill`. Public, so any org
can reach the raw files without a GitHub account or auth token —
important, since you don't want 60 separate orgs needing GitHub logins
just to check a version file.

**Repo layout:**
```
financial-pdf-analysis-skill/
├── VERSION                      ← plain text, e.g. "1.0.0" — this is
│                                   the file the skill checks against
├── README.md                    ← plain-language install instructions
│                                   for a non-technical org contact
├── CHANGELOG.md                 ← what changed each version, so an org
│                                   deciding whether to update can tell
│                                   at a glance if it matters to them
└── financial-pdf-analysis/      ← the actual skill folder (what gets
    ├── SKILL.md                    zipped and uploaded to Claude)
    ├── VERSION                     (keep a copy in here too, matching
    ├── scripts/                     the root one — this is the copy
    │   ├── extract_pdf.py           that travels inside the zip and
    │   ├── build_workbook.py        gets compared against the repo's
    │   └── check_update.py          root VERSION at runtime)
    └── references/
        ├── document-types.md
        ├── extraction-schema.md
        └── distribution-guide.md
```

**Fix the placeholder.** In `financial-pdf-analysis/SKILL.md`, replace
`ORG/REPO` in the update-check command with your actual repo path, e.g.
`ELGP-PHL/financial-pdf-analysis-skill`.

**Cut a release.** On GitHub: Releases → Draft a new release → tag it
`v1.0.0` → attach the zipped `financial-pdf-analysis/` folder as the
release asset. This gives every org a stable, direct download link:
`github.com/ELGP-PHL/financial-pdf-analysis-skill/releases`.

## 2. What each org does (one-time)

Send them: the repo link, and this three-step note (this is what
`README.md` in the repo should say too, so it's not just in your email):

1. Go to the repo's **Releases** page, download the latest
   `financial-pdf-analysis.zip`.
2. In Claude, go to **Customize → Skills → Upload skill**, upload the
   zip.
3. Done — no further setup. Skills mounted this way run automatically
   when relevant.

That's it from their side. No GitHub account, no code, no ongoing
action unless they see an update notice (see below).

## 3. How the update check actually works

Every time the skill runs, it fetches a two-line request to
`raw.githubusercontent.com/ELGP-PHL/financial-pdf-analysis-skill/main/VERSION`
and compares it to the version bundled inside their zip. If yours is
newer, it prints one line at the end of Claude's response, something
like:

> *[financial-pdf-analysis skill: update available — you're on v1.0.0, v1.1.0 is out. Get it from github.com/ELGP-PHL/financial-pdf-analysis-skill/releases]*

Important properties of this design, worth relaying to any org's IT
contact who asks:

- **It never auto-downloads or auto-replaces anything.** It only prints
  a message with a link. A human on their side decides whether to
  re-download and re-upload.
- **It fails silently if it can't reach GitHub** — a locked-down network
  policy, code execution disabled, or the repo being briefly unreachable
  all just result in no message, not an error that interrupts the task.
- **It reads one small public text file** (`VERSION`) — no data about
  the org, their documents, or their usage is sent anywhere. Nothing is
  transmitted; it's an outbound GET request only.

## 4. Your ongoing maintenance loop

When you update the skill:

1. Make your changes inside `financial-pdf-analysis/`.
2. Bump the version number in **both** VERSION files (repo root and
   inside the skill folder) — e.g. `1.0.0` → `1.1.0`. Use plain
   `major.minor.patch` numbers; the check script compares them
   numerically, not alphabetically, so `1.10.0` is correctly understood
   as newer than `1.9.0`.
3. Add a line to `CHANGELOG.md` describing what changed.
4. Commit and push.
5. Cut a new GitHub Release with the updated zip attached, tagged to
   match (e.g. `v1.1.0`).

From that point on, every org's next run of the skill will surface the
update notice automatically — you don't need to re-contact anyone.
They'll still need to manually download and re-upload the new zip
(Claude.ai doesn't support auto-replacing an uploaded skill's contents
in place), but they'll know it's available without you tracking down
60 separate contacts.

## 5. Limitations to set expectations on up front

- **Orgs on network-restricted or code-execution-disabled Claude
  accounts won't see update notices at all.** The skill will still work
  for document analysis; they'll just need to periodically check the
  repo themselves. Mention this in the README so it's not a silent gap.
- **This is a notice, not a push.** If an update fixes something
  important (e.g. a correctness bug in extraction), don't rely solely
  on the in-skill notice reaching everyone promptly — for anything
  urgent, still email the group directly.
- **Version numbers only mean what you make them mean.** Bump the minor
  version for anything that changes extraction behavior or output
  format, not just typo fixes, so orgs can gauge at a glance whether an
  update is worth their time.
