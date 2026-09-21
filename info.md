# AI Job Search Framework — Getting Started Guide

This is a fork of an AI-powered job application framework. It automates resume tailoring,
cover letter generation, ATS optimization, and application tracking using Claude Code or
Cursor agents. Give a job posting URL, get a perfectly tailored 1-page resume + cover letter
compiled to PDF, verified for ATS parsability, and optionally uploaded to Google Drive / Notion.

---

## First-Time Setup

### Prerequisites

| Tool | Why | Install |
|------|-----|---------|
| **Python 3.10+** | Salary lookup, ATS verification, Drive/Notion sync | `python3 --version` to check |
| **LaTeX** | Compile resume (`pdflatex`) and cover letter (`xelatex`) | macOS: [MacTeX](https://tug.org/mactex/) · Linux: `sudo apt install texlive-full` · Windows: [MiKTeX](https://miktex.org/download) |
| **Bun** | Job search CLI tools (LinkedIn, freehire.me) | `curl -fsSL https://bun.sh/install \| bash` |
| **Claude Code or Cursor** | The AI agent that runs the workflow | [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or [Cursor](https://cursor.com) |
| **pypdf** | ATS text extraction from compiled PDFs | `pip install pypdf` |

For minimal LaTeX installs (TinyTeX / BasicTeX), install extra packages:

```bash
tlmgr install moderncv fontawesome5 fontawesome6 academicons import luatexbase pgf \
  titlesec textpos xltxtra xunicode cite realscripts needspace
```

### Install job search CLI dependencies

```bash
for tool in linkedin-search freehire-search; do
  (cd .agents/skills/$tool/cli && bun install)
done
```

### Personalize with `/setup`

Open the repo in Claude Code or Cursor, then run:

```
/setup
```

This interviews you and fills all profile files with **your** data. Three paths:
- **Path A:** Drop your CV, LinkedIn export, or other docs into `documents/` — the agent reads and cross-references them
- **Path B:** Share a single CV file — the agent extracts it and asks follow-ups
- **Path C:** Answer structured interview questions section by section

All three produce the same result: fully populated profile files ready for `/apply`.

---

## Key Commands

| Command | What it does | Cost/turns |
|---------|-------------|------------|
| `/setup` | One-time personalization interview | ~10-15 turns |
| `/apply-lite --yes <url>` | **Default.** Parse posting → evaluate fit → draft resume + cover letter → compile → ATS-check → rename PDFs → upload/commit. Continuous, no reviewer agent. | ~15-25 turns |
| `/apply-premium <url>` | Full pipeline with a reviewer agent in fresh context + deep company research. For high-priority jobs only. | ~70+ turns |
| `/apply <url>` | Same as premium | ~70+ turns |
| `/rank` | Batch-score scraped job postings against your profile. Scoring only, no drafts. | Cheapest |
| `/scrape` | Search LinkedIn + freehire.me for matching jobs | ~5-10 turns |
| `/interview` | Stage-specific mock interview prep with STAR examples | Variable |
| `/outcome` | Record application results (offer, rejection, etc.) | ~3 turns |

**Typical workflow:** `/scrape` → `/rank` → `/apply-lite --yes <url>` for each shortlisted job.

---

## Files You Will Personalize

These files contain **your** profile data. `/setup` fills them in. You can also edit them directly.

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Profile summary, pipeline configuration, standing rules |
| `.claude/skills/job-application-assistant/01-candidate-profile.md` | Structured profile — education, experience, skills, projects. **The single source of truth for all resume/cover letter claims.** |
| `bird_view.md` | Fullest narrative version of your experience |
| `cv/main_example.tex` | Master LaTeX resume with all your details |
| `.claude/skills/job-application-assistant/07-interview-prep.md` | STAR examples from your real work experience |
| `drive_sync.py` | Google Drive upload integration (optional, configure your folder IDs) |
| `notion_sync.py` | Notion tracker integration (optional, configure your database ID) |

### Factual grounding rule

Every claim in a generated resume or cover letter **must** trace back to one of these files:
- `01-candidate-profile.md`
- `cv/main_example.tex`
- `bird_view.md`
- `CLAUDE.md` (profile section)

If a claim doesn't appear in any of these, the agent treats it as a fabrication and removes it. To add a new skill/project/metric, add it to the profile files first.

---

## Files You Should NOT Edit

These are framework methodology files. They define how the agent behaves.

| File | What it controls |
|------|-----------------|
| `.claude/skills/job-application-assistant/04-job-evaluation.md` | Fit scoring rubric, eligibility gates |
| `.claude/skills/job-application-assistant/05-cv-templates.md` | Resume formatting rules and LaTeX template logic |
| `.claude/skills/job-application-assistant/06-cover-letter-templates.md` | Cover letter formatting rules and `cover.cls` usage |
| `tools/*.py` | ATS verification, salary lookup, upstream update checker |
| `cover_letters/cover.cls` | Cover letter LaTeX class file |
| `cover_letters/OpenFonts/` | Fonts for the cover letter (Lato, Raleway) |

---

## How the Pipeline Works

```
/scrape                 /rank                   /apply <url>
  │                       │                        │
LinkedIn + freehire     Batch-score against      1. Parse the job posting
search for matching     your fit rubric          2. Evaluate fit (eligibility + 5 dimensions)
jobs                    → shortlist              3. Draft tailored resume + cover letter
                                                 4. [Premium only] Reviewer agent critiques
                                                 5. Compile to PDF (pdflatex + xelatex)
                                                 6. ATS-check (text extraction, keywords)
                                                 7. Rename PDFs → approval gate
                                                 8. Upload to Drive → Notion row → git commit
```

### What the agent produces per application

- `cv/main_<company>_<role>.tex` — tailored resume LaTeX source
- `cover_letters/cover_<company>_<role>.tex` — tailored cover letter LaTeX source
- `<Company>_YourName_<JobTitle>.pdf` — renamed resume PDF at repo root
- `<Company>_YourName_<JobTitle>_CoverLetter.pdf` — renamed cover letter PDF at repo root
- `documents/applications/<company>_<role>/job_posting.md` — archived posting text
- Row in `job_search_tracker.csv`

---

## Resume Rules (enforced by the agent)

- **Exactly 1 page**, fully used (no big empty gaps at the bottom)
- **No summary/objective section**
- **Section order:** Skills → Projects → Experience → Education
- **Experience entries:** job title first, company second (italic)
- **1-2 keywords bolded per bullet** matching the job posting
- **No em-dashes** (`---`) — use commas, colons, parentheses instead
- **Cover letter for every application** (never skipped)
- **Cover letter:** exactly 1 page, signature visible
- **Contact header:** must render on exactly ONE line in the compiled PDF

---

## Optional Integrations

### Google Drive upload (`drive_sync.py`)

Automatically uploads compiled PDFs to your Google Drive. Configure your folder IDs in `drive_sync.py`:

```python
# Resume folder ID
python3 drive_sync.py "Company_YourName_Title.pdf" <your-resume-folder-id>

# Cover letter folder ID
python3 drive_sync.py "Company_YourName_Title_CoverLetter.pdf" <your-cover-folder-id>
```

Requires Google Drive API credentials. See `drive_sync.py` for setup.

### Notion tracker (`notion_sync.py`)

Inserts a row into a Notion database for each application:

```bash
python3 notion_sync.py "Company" "Job Title" "posting-url" "drive-link"
```

Requires a Notion integration token and database ID. See `notion_sync.py` for setup.

### Salary benchmarking

Create `salary_data.json` manually or convert from Excel:

```bash
pip install openpyxl
python3 tools/convert_salary_excel.py path/to/salary-data.xlsx --source "My Salary Data"
```

If skipped, the agent simply omits the salary comparison step.

---

## Getting Started in 5 Minutes

```bash
# 1. Clone the repo
git clone https://github.com/<your-fork-url>.git
cd Resume-maker

# 2. Create your own branch
git checkout -b <yourname>_jobsearch

# 3. Install search tool dependencies
for tool in linkedin-search freehire-search; do
  (cd .agents/skills/$tool/cli && bun install)
done

# 4. Open in Claude Code or Cursor, run /setup to personalize

# 5. Apply to your first job
#    /apply-lite --yes <job-posting-url>
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `salary_data.json not found` | Expected if you haven't set up salary benchmarking. Agent skips it automatically. |
| LaTeX compilation errors | Resume uses `pdflatex`. Cover letter uses `xelatex`. Make sure both are installed. |
| Fonts not found in cover letter | Check `cover_letters/OpenFonts/fonts/` exists with Lato and Raleway font files. |
| Job search CLIs not working | Run `bun install` in each `.agents/skills/*/cli/` directory. |
| `pdflatex` fails with fontawesome5 errors | Try `lualatex` instead — some TeX distributions handle it better. |

---

## More Details

- Full setup guide with Windows/Linux/macOS instructions: `SETUP.md`
- Framework architecture and all commands: `README.md`
- Resume template rules: `.claude/skills/job-application-assistant/05-cv-templates.md`
- Cover letter template rules: `.claude/skills/job-application-assistant/06-cover-letter-templates.md`
- Fit evaluation rubric: `.claude/skills/job-application-assistant/04-job-evaluation.md`
