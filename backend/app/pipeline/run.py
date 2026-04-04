"""Pipeline: fetch data from all sources, write a draft issue YAML file.

Called by the GHA cron workflow. Outputs a YAML file to issues/ directory
which the GHA then commits and opens as a draft PR.
"""

import asyncio
from datetime import date, timedelta
from pathlib import Path

import yaml

from app.pipeline.blogs import fetch_official_news
from app.pipeline.discourse import fetch_pep_discussions
from app.pipeline.github_prs import fetch_github_prs
from app.pipeline.musings import fetch_musings
from app.pipeline.peps import fetch_pep_updates
from app.pipeline.releases import fetch_events, fetch_upcoming_releases
from app.pipeline.steering_council import fetch_steering_council


def _normalize_title(title: str) -> str:
    key = title.strip().lower()
    return (
        key.replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )


def week_slug(d: date) -> str:
    year, week, _ = d.isocalendar()
    return f"{year}-w{week:02d}"


def _last_issue_date(issues_dir: Path) -> date | None:
    """Find the period_end of the most recent issue."""
    latest_number = 0
    latest_end: date | None = None
    for f in issues_dir.glob("*.yml"):
        if f.name.startswith("_"):
            continue
        try:
            data = yaml.safe_load(f.read_text())
            if (
                data
                and isinstance(data.get("number"), int)
                and data["number"] > latest_number
            ):
                latest_number = data["number"]
                end = data.get("period_end", "")
                if end:
                    latest_end = date.fromisoformat(end)
        except Exception:
            continue
    return latest_end


async def run_pipeline(issues_dir: Path, since: date | None = None):
    if since is None:
        # Look back to the last issue's end date, or default to 14 days
        last_end = _last_issue_date(issues_dir)
        if last_end:
            since = last_end
        else:
            since = date.today() - timedelta(days=14)

    period_start = since
    period_end = date.today()
    slug = week_slug(period_end)

    print(f"Fetching data for {slug} ({period_start} to {period_end})...")

    all_items: list[dict] = []

    days_back = (period_end - period_start).days

    fetchers = [
        ("Upcoming releases", fetch_upcoming_releases()),
        ("Official news", fetch_official_news(days=days_back)),
        ("PEP updates", fetch_pep_updates(since)),
        ("Steering Council", fetch_steering_council(days=days_back)),
        ("PRs", fetch_github_prs(since)),
        ("PEP discussions", fetch_pep_discussions(days=days_back)),
        ("Events", fetch_events()),
        ("Core dev musings", fetch_musings(days=days_back)),
    ]

    for name, coro in fetchers:
        try:
            items = await coro
            print(f"  -> {len(items)} {name}")
            all_items.extend(items)
        except Exception as e:
            print(f"  !! {name} failed: {e}")

    # Dedupe across sections by title — prefer earlier sections (official_news > musings)
    seen_titles: set[str] = set()
    deduped: list[dict] = []
    for item in all_items:
        key = _normalize_title(item["title"])
        if key in seen_titles:
            continue
        seen_titles.add(key)
        deduped.append(item)
    all_items = deduped

    # Find next issue number
    existing = sorted(issues_dir.glob("*.yml"))
    existing = [f for f in existing if not f.name.startswith("_")]
    max_number = 0
    for f in existing:
        try:
            data = yaml.safe_load(f.read_text())
            if data and isinstance(data.get("number"), int):
                max_number = max(max_number, data["number"])
        except Exception:
            continue

    issue_number = max_number + 1

    issue = {
        "number": issue_number,
        "title": f"Core Dispatch #{issue_number}",
        "slug": slug,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "editorial_notes": "<!-- Write your editorial notes here -->\n",
        "quote": {
            "text": "<!-- Add a quote here -->",
            "author": "",
            "url": "",
        },
        "credits": [],
        "items": all_items,
    }

    output_path = issues_dir / f"{slug}.yml"
    output_path.write_text(
        yaml.dump(issue, default_flow_style=False, sort_keys=False, allow_unicode=True)
    )
    print(f"Wrote {output_path} with {len(all_items)} items")
    return output_path


def main():
    repo_root = Path(__file__).resolve().parents[3]  # backend/app/pipeline -> repo root
    issues_dir = repo_root / "issues"
    issues_dir.mkdir(exist_ok=True)
    asyncio.run(run_pipeline(issues_dir))


if __name__ == "__main__":
    main()
