"""Add a row to the Notion Job Application Tracker database."""
import datetime
import os
import sys
from pathlib import Path

import requests

CONFIG_DIR = Path.home() / ".config" / "resume-bot"
ENV_FILE = CONFIG_DIR / ".env"


def load_env():
    for line in ENV_FILE.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def time_of_day(now=None):
    now = now or datetime.datetime.now()
    if now.hour < 12:
        return "morning"
    if now.hour < 17:
        return "Noon"
    return "Night"


def add_application_row(company, position, link, resume_drive_link,
                         stage="To apply", date=None, time_slot=None):
    load_env()
    token = os.environ["NOTION_TOKEN"]
    db_id = os.environ["NOTION_DB_ID"]
    date = date or datetime.date.today().isoformat()
    time_slot = time_slot or time_of_day()
    link = link or "n/a"

    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "Company": {"title": [{"text": {"content": company}}]},
            "Position": {"rich_text": [{"text": {"content": position}}]},
            "Link": {"url": link},
            "ResumeLinkDrive": {
                "files": [{"name": "resume.pdf", "type": "external",
                           "external": {"url": resume_drive_link}}]
            },
            "Application Date": {"date": {"start": date}},
            "Time": {"select": {"name": time_slot}},
            "Stage": {"status": {"name": stage}},
        },
    }
    resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    resp.raise_for_status()
    return resp.json()["url"]


if __name__ == "__main__":
    if len(sys.argv) < 5:
        raise SystemExit(
            "usage: notion_sync.py <company> <position> <job_link> <resume_drive_link> [stage]"
        )
    company, position, link, resume_link = sys.argv[1:5]
    stage = sys.argv[5] if len(sys.argv) > 5 else "To apply"
    page_url = add_application_row(company, position, link, resume_link, stage=stage)
    print(page_url)
