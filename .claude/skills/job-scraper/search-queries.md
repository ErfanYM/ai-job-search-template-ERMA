# Search Queries for Job Scraper (example - customize for your target roles/location)

## Installed portal CLIs (primary for `/scrape`)

`/scrape` discovers every portal skill under `.agents/skills/*/SKILL.md` and runs its CLI.
Installed: **`linkedin-search`** and **`freehire-search`**. Add more with `/add-portal`.
You do not need a `site:` line for those to run.

Typical CLI calls (replace the query/location with your own target roles and city):

```bash
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "data engineer" -l "Your City, Province, Country" --jobage 14 --format json
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "software engineer new grad" -l "Your City, Province, Country" --jobage 14 --format json
bun run .agents/skills/linkedin-search/cli/src/cli.ts search -q "data engineer" -l "Remote" --remote remote --jobage 14 --format json
bun run .agents/skills/freehire-search/cli/src/cli.ts search --query "data engineer" --country CA --format json
bun run .agents/skills/freehire-search/cli/src/cli.ts search --query "data" --remote --format json
```

Keep LinkedIn volume low (ToS - personal use only). The `site:` templates below are the
**WebSearch fallback** for company career pages or when a CLI fails.

**Language scope:** set this to the language(s) you actually work in; only include query
languages that match your target job market.

## Query Categories (organize by function, not exact title)

Below are example categories - replace with your own target roles, skills, and priority order.

### Priority 1: Example category
Titles: Data Engineer, Data Platform Engineer, Analytics Engineer, ETL Developer
Skills: PySpark, Spark, Databricks, SQL, ETL, Delta Lake, data pipelines, Airflow
```
site:linkedin.com/jobs "data engineer" Your City
site:jobs.lever.co OR site:boards.greenhouse.io "data engineer" Your City
```

### Priority 2: Example category
Titles: Data Scientist, Data Analyst, Business Data Analyst, Machine Learning Engineer
Skills: Python, SQL, scikit-learn, machine learning, predictive modelling, dashboards
```
site:linkedin.com/jobs "data scientist" OR "data analyst" Your City
```

## Location Filter
Define your own: acceptable locations/hybrid radius, borderline cities to flag rather than
auto-drop, and a hard deal-breaker rule (e.g. relocation outside your province) unless you
say otherwise.

## Date Filter
Only jobs posted within the last 14 days, or with a future application deadline. `--jobage 14`
on the LinkedIn CLI. If a date cannot be determined, include but flag "date unknown".

## Eligibility pre-filter
Before surfacing a result, apply `04-job-evaluation.md`'s enrollment gate: a posting that
requires a co-op program you don't have is excluded; a "currently a student" wording is
flagged per your own graduation status, not auto-dropped.

## Adapting Queries
If the user gives a focus area ("/scrape data engineering"), run that category's queries plus
2-3 custom focus-specific ones.
