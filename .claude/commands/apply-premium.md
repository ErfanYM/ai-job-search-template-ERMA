# /apply-premium - Full Drafter-Reviewer Application (high-priority jobs only)

Premium mode for a job that genuinely deserves the extra spend: a reviewer agent in fresh context, deep independent company research, and the full verification checklist. This is the **expensive** path (~70+ turns, ~$25+ on Opus); use it only for high-priority roles. For ordinary applications use `/apply-lite --yes` instead.

**Run the complete workflow defined in `.claude/commands/apply.md`, verbatim, all steps in order** - Step 1 fit evaluation with the proceed gate, Step 2 drafting, Step 3 reviewer agent (research + critique + Factual Grounding Audit), Step 4 revise, Step 5 compile/inspect/ATS, Step 6 present + record, Step 7 the outward pipeline (rename → approval → Drive → Notion → git).

`$ARGUMENTS` (URL or pasted posting text) is passed straight through to that workflow. Every gate in `apply.md` stays in force, including the approval-before-submit gate.

Deep research is the differentiator: the reviewer agent may use Opus, multiple `WebSearch`/`WebFetch` calls, and the company-research cache. That is the reason to pick this mode - do not strip it down.
