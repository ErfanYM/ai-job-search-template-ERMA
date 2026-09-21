---
framework_version: 2.0.0
---

# CV (Resume) Templates and Tailoring Guide

This repo uses a single-page LaTeX resume template, **not** moderncv. The template
lives at `cv/main_example.tex` (the comprehensive master). Every tailored application writes
`cv/main_<company>_<role>.tex`, built from the master by cutting and reframing for the posting.

**Output file:** `cv/main_<company>_<role>.tex`
**Compile with:** `pdflatex` (the template sets `\pdfgentounicode=1` and `\input{glyphtounicode}`
for ATS text extraction; lualatex/xelatex are not used for the CV).
**Master reference:** `cv/main_example.tex`

### Compile command

```bash
cd cv && pdflatex -interaction=nonstopmode main_<company>_<role>.tex
```

Run it twice (references settle). Expected output: `Output written on main_<company>_<role>.pdf (1 page, ...)`.
**Any page count other than 1 is a failure** that must be fixed before presenting. The root
`build.py` compiles `resume.tex` specifically and is not used by `/apply`; `/apply` compiles
the `cv/main_<company>_<role>.tex` file directly.

## Hard rules (never violate)

1. **Exactly one page, fully used.** Not two pages. Not a page that is more than ~30% empty at
   the bottom. If it spills to page 2, cut (see "Relevance-weighted cutting"). If it ends
   high on the page, restore the highest-relevance cut line or add a bullet.
2. **No summary / profile / objective section.** The resume opens with the Skills section
   straight after the contact header. Do not add a summary even if the posting seems to invite one.
3. **Section order is fixed:** Technical Skills (or "Skills"), then Projects, then Experience,
   then Education. **Projects come before Experience** - for an early-career candidate,
   denser, more technically relevant project work often carries more weight than early
   jobs and should be seen first. Preserve this order on every build.
4. **Experience entries lead with the job title, not the company.** With the
   `\resumeSubheading{#1}{#2}{#3}{#4}` macro: `#1` = job title (bold, line 1), `#2` = dates,
   `#3` = company (italic, line 2), `#4` = location. If the companies are not well known, the
   title matters more than the employer. Applies to every job.
5. **Bold 1-2 keywords per bullet** with `\textbf{}` - key technologies, metrics, or
   role-critical concepts that match the job description, so a recruiter scanning for 10
   seconds sees the relevant skills and impact numbers. Do not bold more than 2 phrases per
   bullet; over-bolding defeats the purpose.
6. **Prune the Technical Skills section to the posting.** Remove skill categories and items
   not relevant to this job; add missing ones the candidate genuinely has (check
   `01-candidate-profile.md`). The section stays lean and scannable, not a
   dump of everything.
7. **No em-dashes (`---`) in body text.** Use commas, colons,
   parentheses, or a connective word ("including"). En-dash `--` is fine only for numeric
   ranges (`0--12\%`) and date ranges in prose. **In `\resumeSubheading` date arguments, use
   a single hyphen** (`Jan 2025 - May 2025`), never `--` - see the ATS date rule below.

## Template structure

The master `cv/main_example.tex` defines these macros in the preamble - do not redefine them
per application, just use them:

- `\resumeSubHeadingListStart` / `\resumeSubHeadingListEnd` - wraps a section's entries
- `\resumeSubheading{TITLE}{DATES}{COMPANY}{LOCATION}` - an Experience or Education entry
- `\resumeProjectHeading{\textbf{Name} $|$ \emph{Tech, stack}}{}` - a Project entry header
- `\resumeItemListStart` / `\resumeItemListEnd` - wraps the bullets under one entry
- `\resumeItem{...}` - one bullet

Document skeleton (already in the master; a tailored file keeps this and edits the content):

```latex
\documentclass[letterpaper,10pt]{article}
% ... preamble with macros, \pdfgentounicode=1, \input{glyphtounicode} ...
\begin{document}

\begin{center}
    \textbf{\Huge \scshape Your Name} \\ \vspace{1pt}
    \small [Phone] $|$
    \href{mailto:you@example.com}{\underline{you@example.com}} $|$
    \href{https://www.linkedin.com/in/yourhandle/}{\underline{linkedin.com/yourhandle}} $|$
    \href{https://github.com/yourhandle}{\underline{Github}} $|$
    \href{https://yourportfolio.example}{\underline{Portfolio}}
\end{center}

\section{Technical Skills}   % 5-6 category lines, pruned to the posting
\section{Projects}           % 3-4 projects, 2-3 bullets each, most role-relevant first
\section{Experience}         % title-first, 2-3 bullets each
\section{Education}          % school, degree, date, one coursework line

\end{document}
```

## Section-by-section tailoring

### Technical Skills
- 5-6 category lines (`\textbf{Category}: item, item, ...`). Category names change per posting:
  a data-engineering posting gets "Data Engineering", "CI/CD & DevOps", "Cloud"; a BA posting
  gets "Business Analysis", "Documentation & Process", "Coordination & Support".
- Put the posting's own core terms in the category labels and item lists where they truthfully
  apply - ATS matches literally, so "ETL pipelines" beats "data movement".
- Mark genuinely-familiar-but-not-hands-on items `(familiar)` - e.g. `Power BI (familiar)`,
  `Azure (familiar)`. Never drop the qualifier to look stronger.

### Projects (comes before Experience)
- Pick the **3-4 projects** that best match the posting from the 13 in `01-candidate-profile.md`.
  Rename the project heading to foreground the posting's angle (e.g. the Bank Marketing project
  becomes "Term-Deposit Propensity Model" for a data-science posting, "Distributed & Parallel
  ML Pipelines" pairs the Stanford graph and Instacart work for a systems posting).
- 2-3 bullets each. Lead the most role-relevant project first.
- Every metric must trace to `01-candidate-profile.md` / `bird_view.md`. Do not round up or
  invent numbers.

### Experience
- Both roles, title-first (rule 4). Choose the honest title variant that fits the posting from
  the "Title framing note" in `01-candidate-profile.md` (e.g. "Data Analyst Intern" for
  analytics roles, "Software Engineer Intern" for SWE roles, "Embedded Software Engineer" for
  firmware roles).
- Each role: 2-3 bullets, more for the role most relevant to the posting.
- Reframe bullets toward the posting; keep the metrics exact.

### Education
- One entry: `\resumeSubheading{Your University}{City, Province}{Your Degree}{Month Year}`
  - Note: for Education the macro is used as `{#1=school}{#2=location}{#3=degree}{#4=date}`
    (school-first is fine here - the rule-4 title-first swap is for jobs only).
- One coursework bullet, 5-6 courses pruned to the posting's domain.
- **Match the degree wording to your actual status** (completed, expected date, etc). Do not
  add "currently pursuing" anywhere - it contradicts the truth and the eligibility gate.

## LaTeX special characters (important)

Postings and profile data are plain text; the CV is LaTeX. Escape wherever they land in body
text - company names, bullets, skill lists:

| Character | Write | Typical trigger |
|---|---|---|
| `&` | `\&` | company names: AT\&T, H\&M; "research \& development" |
| `%` | `\%` | every quantified achievement: "cut latency by 40\%" |
| `$` | `\$` | salary and cost figures: "\$29M dataset" |
| `#` | `\#` | "ranked \#1", C\# |
| `_` | `\_` | file names, identifiers |
| `~` | `\textasciitilde{}` | "\textasciitilde{}131K orders" |

**`%` fails silently.** An unescaped `%` starts a LaTeX comment: the compile succeeds with zero
errors and everything after the `%` on that line vanishes from the PDF. "improved accuracy by
40% and cut noise 30%" renders as "improved accuracy by 40" - the bullet keeps an
impressive-looking fragment and loses the real result. Check every `%` in every bullet before
compiling. **`&` fails loudly** inside the tabular macros (alignment errors) - escape employer
names up front.

A bullet whose text begins with a literal `[` must be braced - `\resumeItem{{[text]}}` - or
LaTeX parses the bracket as an optional argument.

## ATS parseability (verify after the layout is clean)

Most employers run the resume through an ATS that reads the PDF's **text layer**, not the
rendered page. After the compile-and-inspect loop passes:

```bash
python3 tools/verify_pdf.py cv/main_<company>_<role>.pdf --dump-text cv/main_<company>_<role>.txt
```

Tries pypdf, then `pdftotext`. If neither is installed, skip the mechanical check with a
warning and check keyword coverage from the visual read. What to check:

- **Clean extraction** - no `(cid:NNN)` markers, no `�` replacement characters, no text visible
  in the PDF but missing from the extraction. This template compiled with pdflatex and
  `\pdfgentounicode=1` extracts cleanly; this is here as a guard.
- **Email and phone as literal text.** The contact line prints them as text (not icon-only),
  so they must appear verbatim in the extraction. The `Github` link text carries a URL that is
  not in the text layer - that is acceptable because GitHub is not a screening field, but the
  email and phone must be literal.
- **Reading order matches visual order.** The template is single-column and safe.
- **Dates recognizable.** Each role and the degree must show its year(s) in the extraction.

### Date fields must be ASCII hyphens, not en-dashes (silent ATS-import failure)

This fails **silently** - clean extraction, no cid markers, contact intact, and the dates still
get dropped on import to Workday / Greenhouse / iCIMS.

`--` in LaTeX ligatures into an en-dash (U+2013). Many parsers split a date range only on an
ASCII hyphen (U+002D) and see no range. **Write every `\resumeSubheading` date argument with a
single hyphen:**

```latex
\resumeSubheading{Data Engineer Intern}{Jan 2025 - May 2025}{Acme Corp}{Toronto, ON}   % parses
\resumeSubheading{Data Engineer Intern}{Jan 2025 -- May 2025}{Acme Corp}{Toronto, ON}  % en-dash, may not
```

Keep `--` where it is typographically correct in prose (a coverage range like `0--12\%`).
After extracting the text layer, confirm every Experience entry and the Education entry shows
its dates with an ASCII hyphen.

### Keyword coverage

Reuse the required/preferred keyword list from Step 1 - do not re-derive. Match each against
the extracted text, report a table:

| Keyword | Priority | Status | Note |
|---|---|---|---|

- **covered** - term appears (verbatim or trivial inflection)
- **synonym-only** - concept present under a different term; if the posting's exact term is
  truthfully applicable, switch to it (ATS matches are literal)
- **missing (have it)** - profile shows the candidate genuinely has this but the CV never says it: add
  it where it fits, preferring a project or experience bullet over the skills list, then
  recompile
- **missing (gap)** - a genuine gap: leave it out. **Never stuff keywords.** A gap is
  acknowledged in the cover letter's framing, not hidden in the resume.

## Compile-and-inspect loop (MANDATORY)

After writing the tailored CV, before presenting:

1. `cd cv && pdflatex -interaction=nonstopmode main_<company>_<role>.tex` (twice)
2. Check the page count in the log: must be exactly 1.
3. Read the PDF via the Read tool. Check: no orphaned section heading at the very bottom; no
   entry title separated from its bullets; the last line of text sits reasonably close to the
   bottom margin (not a big empty gap, not spilling over).
4. A quick fill check without opening the PDF:
   ```bash
   python3 -c "from pypdf import PdfReader; r=PdfReader('cv/main_<company>_<role>.pdf'); p=r.pages[0]; ys=[]; p.extract_text(visitor_text=lambda t,cm,tm,*a: ys.append(tm[5]) if t.strip() else None); print('pages', len(r.pages), 'lowest_y', min(y for y in ys if y>1))"
   ```
   `lowest_y` around 30-45 means a well-filled page. Above ~70 means too much white space at
   the bottom - add content. `pages` must be 1.

### Fixing layout

- **Spills to page 2 by a few lines:** cut with relevance-weighted cutting (below). First cut a
  redundant skills item or a low-relevance older bullet. As a last resort, tighten
  `\resumeItemListStart` itemsep (it is `-3pt` in the master; `-4pt` buys a little) or merge
  two short bullets into one - never shrink the font or page geometry.
- **Ends high on the page (thin):** restore the highest-relevance line previously cut, or add a
  third bullet to a two-bullet project, or add a skills item. A resume that ends at the middle
  of the page looks unfinished.

## Relevance-weighted cutting (how to shrink)

Cut by signal, not by section. An older-role bullet that hits the posting's keywords is worth
more than a recent-role bullet that does not. For each candidate line score:

1. **Relevance to THIS posting** - does it hit a named tool, keyword, or responsibility?
2. **Uniqueness** - is this the only place the claim appears?
3. **Narrative load** - does the cover letter lean on it? If cutting it forces a cover-letter rewrite, it is load-bearing.

Cut the lowest-total-score line first, regardless of section. Practical order:

1. A skills-section item duplicated by a project or experience bullet (cut the skills version).
2. A project bullet about work that does not touch any posting keyword.
3. A fourth project (drop to 3) if one is clearly the weakest match.
4. A role's third bullet (keep it only when clearly relevant to the posting).
5. Coursework entries beyond 5.

Never invent projects to fill space, never quietly change employment dates, never cut the one
concrete example the cover letter depends on.

## Tenure vs visible output

Short roles with a few strong bullets read fine. If a role is added with a long span and
few bullets, surface more real work or make the phases explicit rather than padding.
