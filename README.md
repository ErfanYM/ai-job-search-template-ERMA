# AI Job Search Workspace

Job-search workspace built on the open-source
[`ai-job-search`](https://github.com/MadsLorentzen/ai-job-search) framework (MIT), with a
single-page resume template, profile, and a Google Drive + Notion + git pipeline layered
on top.

**First run:** use `/setup` to build your profile files before running `/apply`.

## The workflow

```
/scrape                 /rank                   /apply <url-or-text>
  |                       |                        |
job-portal search      batch-score the batch     evaluate fit (eligibility +
(LinkedIn, etc.)        against the fit rubric    enrollment gate, 5 dimensions)
                                                   |
                                                 draft resume + cover letter (always both)
                                                   |
                                                 reviewer agent researches + critiques
                                                   |
                                                 revise -> compile -> ATS-check
                                                   |
                                                 rename PDFs -> ask "good to submit?"
                                                   |
                                                 Drive upload -> Notion row -> git commit
```

Also available: `/apply-lite` (token-efficient single-pass apply), `/apply-premium`
(full reviewer flow), `/interview` (stage-specific prep + mock), `/outcome` (record
results), `/html-report` (offline dashboard), `/upskill` (skill-gap plan), `/expand`
(enrich profile), `/gmail-sync`, `/notion-sync`, `/add-portal`, `/add-template`,
`/setup`, `/reset`.

## Key files

| File | What |
|---|---|
| `CLAUDE.md` | The `/apply` pipeline including the Drive/Notion/commit steps |
| `.claude/skills/job-application-assistant/04-job-evaluation.md` | Fit scoring + eligibility/enrollment gate |
| `.claude/skills/job-application-assistant/05-cv-templates.md` | 1-page resume rules |
| `.claude/skills/job-application-assistant/06-cover-letter-templates.md` | `cover.cls` cover letter rules |
| `.claude/skills/job-application-assistant/07-interview-prep.md` | STAR-format interview prep |
| `cv/main_example.tex` | Master resume template (pdflatex) |
| `cover_letters/cover.cls` + `OpenFonts/` | Cover letter class + fonts (xelatex) |
| `drive_sync.py`, `notion_sync.py` | Drive + Notion sync pipeline |
| `tools/verify_pdf.py` | ATS text-layer check |

## Setup / prereqs

- `bun` - for `linkedin-search` and `freehire-search` CLIs. Run `bun install` in each `.agents/skills/*/cli/`.
- `pdflatex` - resume. `xelatex` - cover letter, needs extra TeX packages on a minimal install:
  ```
  sudo tlmgr install textpos xltxtra xunicode cite realscripts
  ```
- `pypdf` - `tools/verify_pdf.py`.
- Google Drive + Notion (optional): set up your own `drive_sync.py` / `notion_sync.py` credentials, see `SETUP.md`.

## Rules that never bend

- Resume: exactly 1 page, no summary section, order Skills -> Projects -> Experience -> Education, job title before company, 1-2 bolded keywords per bullet, no em-dashes.
- Cover letter for every application.
- Approval gate before Drive/Notion/git, every time.
- Every claim traces to your profile files (built via `/setup`) and `cv/main_example.tex`.
