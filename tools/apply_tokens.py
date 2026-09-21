#!/usr/bin/env python3
"""Token usage per /apply run, read from Claude Code session logs.

Segments a session transcript into /apply runs and totals the tokens each one
cost. A run starts at the human message that triggered /apply and ends at the
turn containing the pipeline's `git commit` (Step 12), or at the next /apply,
or at end of session.

Usage:
    python3 tools/apply_tokens.py                 # runs in the newest session
    python3 tools/apply_tokens.py --all           # every session for this repo
    python3 tools/apply_tokens.py --session <id>  # one session by id or path
    python3 tools/apply_tokens.py --json          # machine-readable

Numbers come from the `usage` block each assistant message records, so they are
what the API actually billed, not an estimate. Subagent totals are read from the
task-notification the agent posts back, since subagent turns are logged
separately from the main transcript.
"""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
# The first line of the skill body /apply injects; the marker that a run began.
# Matched only at the start of a prompt, so a transcript that merely quotes the
# string (this file, a grep of the logs) does not register as a run.
APPLY_MARKER = "# /apply - Drafter-Reviewer Job Application Workflow"
SUBAGENT_TOKENS = re.compile(r"<subagent_tokens>(\d+)</subagent_tokens>")


def project_dir(cwd: Path) -> Path:
    """Claude Code slugifies the cwd to name the project log directory."""
    return PROJECTS / re.sub(r"[^A-Za-z0-9]", "-", str(cwd))


def load(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # a partially flushed tail line
    return rows


def text_of(row: dict) -> str:
    content = row.get("message", {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                parts.append(json.dumps(block.get("input", {})))
            elif block.get("type") == "tool_result":
                inner = block.get("content")
                parts.append(inner if isinstance(inner, str) else json.dumps(inner))
        return "\n".join(parts)
    return ""


def is_prompt(row: dict) -> bool:
    """True for a message sent to the model, false for a tool result."""
    content = row.get("message", {}).get("content")
    if isinstance(content, list):
        return not any(
            isinstance(b, dict) and b.get("type") == "tool_result" for b in content
        )
    return True


def is_human(row: dict) -> bool:
    return row.get("type") == "user" and (row.get("origin") or {}).get("kind") == "human"


def commits_in(row: dict) -> list[str]:
    """Commit subject lines from any `git commit` this assistant turn ran."""
    content = row.get("message", {}).get("content")
    if not isinstance(content, list):
        return []
    found = []
    for block in content:
        if not (isinstance(block, dict) and block.get("type") == "tool_use"):
            continue
        cmd = block.get("input", {}).get("command", "")
        if isinstance(cmd, str) and re.search(r"\bgit commit\b", cmd):
            found.append(subject_of(cmd))
    return found


def subject_of(cmd: str) -> str:
    """First real line of a commit message, however the shell supplied it.

    Handles `-m "Subject"`, `-F - <<EOF`, and `-m "$(cat <<EOF ...)"` alike by
    taking the first line that is neither shell plumbing nor a trailer.
    """
    m = re.search(r"-m\s+[\"'](?!\$\()([^\"'\n]+)", cmd)
    if m:
        return m.group(1).strip()
    skip = re.compile(r"^(git |\$\(|[\"']?EOF|[\"']?\)|<<|&&|\||#)|-By:|-Session:")
    for line in cmd.splitlines():
        line = line.strip().strip('"\'')
        if line and not skip.search(line):
            return line
    return "(commit)"


def find_runs(rows: list[dict]) -> list[dict]:
    """Locate each /apply run as a [start, end] row-index span."""
    starts = []
    for i, row in enumerate(rows):
        if (row.get("type") == "user" and is_prompt(row)
                and text_of(row).lstrip().startswith(APPLY_MARKER)):
            # attribute the run to the human message that triggered it
            trigger = next((j for j in range(i, -1, -1) if is_human(rows[j])), i)
            if trigger not in starts:
                starts.append(trigger)

    runs = []
    for n, start in enumerate(starts):
        limit = starts[n + 1] if n + 1 < len(starts) else len(rows)
        end, label = limit - 1, None
        for i in range(start, limit):
            subjects = commits_in(rows[i]) if rows[i].get("type") == "assistant" else []
            if subjects:
                label = subjects[-1]
                # the run ends with the turn that reports the commit
                end = next(
                    (j - 1 for j in range(i + 1, limit) if is_human(rows[j])), limit - 1
                )
                break
        runs.append({"start": start, "end": end, "label": label, "rows": rows})
    return runs


def tally(run: dict) -> dict:
    rows = run["rows"]
    t = {
        "input": 0,
        "output": 0,
        "thinking": 0,
        "cache_write": 0,
        "cache_read": 0,
        "subagent": 0,
        "api_calls": 0,
        "web_search": 0,
        "web_fetch": 0,
    }
    for row in rows[run["start"] : run["end"] + 1]:
        if row.get("type") == "assistant":
            u = row.get("message", {}).get("usage") or {}
            t["api_calls"] += 1
            t["input"] += u.get("input_tokens", 0)
            t["output"] += u.get("output_tokens", 0)
            t["thinking"] += (u.get("output_tokens_details") or {}).get(
                "thinking_tokens", 0
            )
            t["cache_write"] += u.get("cache_creation_input_tokens", 0)
            t["cache_read"] += u.get("cache_read_input_tokens", 0)
            server = u.get("server_tool_use") or {}
            t["web_search"] += server.get("web_search_requests", 0)
            t["web_fetch"] += server.get("web_fetch_requests", 0)
        elif row.get("type") == "user":
            for m in SUBAGENT_TOKENS.finditer(text_of(row)):
                t["subagent"] += int(m.group(1))

    t["billed"] = t["input"] + t["cache_write"] + t["cache_read"] + t["output"]
    t["total"] = t["billed"] + t["subagent"]
    span = rows[run["start"] : run["end"] + 1]
    stamps = [r["timestamp"] for r in span if r.get("timestamp")]
    t["started"] = stamps[0] if stamps else ""
    t["ended"] = stamps[-1] if stamps else ""
    # a run with no commit never reached Step 12: say so rather than labelling
    # it with the raw trigger text
    t["label"] = run["label"] or (
        text_of(span[0])[:40].replace("\n", " ").strip() + "  (no commit, incomplete)"
    )
    t["completed"] = run["label"] is not None
    t["turns"] = sum(1 for r in span if is_human(r))
    return t


def duration(started: str, ended: str) -> str:
    try:
        from datetime import datetime

        parse = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
        mins = (parse(ended) - parse(started)).total_seconds() / 60
        return f"{mins:.0f}m" if mins < 90 else f"{mins / 60:.1f}h"
    except (ValueError, TypeError, AttributeError):
        return "?"


def report(results: list[dict]) -> None:
    if not results:
        print("No /apply runs found in the session log(s).")
        return
    for r in results:
        print(f"\n{r['label']}")
        print(f"  {r['started'][:16].replace('T', ' ')} UTC"
              f"  ({duration(r['started'], r['ended'])}, {r['turns']} prompts,"
              f" {r['api_calls']} API calls)")
        print(f"  {'input (fresh)':<22}{r['input']:>12,}")
        print(f"  {'cache write':<22}{r['cache_write']:>12,}")
        print(f"  {'cache read':<22}{r['cache_read']:>12,}")
        print(f"  {'output':<22}{r['output']:>12,}"
              f"   (thinking {r['thinking']:,})")
        print(f"  {'-' * 34}")
        print(f"  {'main session':<22}{r['billed']:>12,}")
        print(f"  {'reviewer subagent':<22}{r['subagent']:>12,}")
        print(f"  {'TOTAL':<22}{r['total']:>12,}")
        if r["web_search"] or r["web_fetch"]:
            print(f"  web: {r['web_search']} searches, {r['web_fetch']} fetches")

    if len(results) > 1:
        tot = sum(r["total"] for r in results)
        done = [r for r in results if r.get("completed")]
        line = f"\n{len(results)} runs, {tot:,} tokens total"
        if done:
            avg = sum(r["total"] for r in done) // len(done)
            line += f", {avg:,} average per completed application ({len(done)})"
        print(line + ".")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", help="session id or path to a .jsonl transcript")
    ap.add_argument("--all", action="store_true",
                    help="scan every session logged for this repo")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--cwd", default=Path.cwd(), type=Path,
                    help="project directory (default: current)")
    args = ap.parse_args()

    logs = project_dir(args.cwd)
    if args.session:
        path = Path(args.session)
        files = [path if path.exists() else logs / f"{args.session}.jsonl"]
    elif args.all:
        files = sorted(logs.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    else:
        found = sorted(logs.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        files = found[-1:]

    missing = [f for f in files if not f.exists()]
    if missing or not files:
        print(f"No session log found (looked in {logs})", file=sys.stderr)
        return 1

    results = []
    for f in files:
        rows = load(f)
        for run in find_runs(rows):
            r = tally(run)
            r["session"] = f.stem
            results.append(r)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        report(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
