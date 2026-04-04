"""Fetch recently accepted/rejected PEPs from the python/peps repo."""

import re
from datetime import date, timedelta

import httpx

from app.config import settings

GITHUB_API = "https://api.github.com"
PEPS_REPO = "python/peps"

# Only match PRs that explicitly mark a PEP with a new status.
# e.g. "PEP 803: Mark as Accepted", "Mark PEP 747 as Final"
# NOT "PEP 822: add a Rejected Idea" (that's adding a section, not changing status)
STATUS_CHANGE_PATTERNS = [
    # "PEP 803: Mark as Accepted"
    re.compile(
        r"PEP\s+(\d+):\s*(?:Mark|Set)\s+(?:as\s+)?(Accepted|Final|Rejected|Withdrawn|Superseded)",
        re.IGNORECASE,
    ),
    # "Mark PEP 747 as Final"
    re.compile(
        r"(?:Mark|Set)\s+PEP\s+(\d+)\s+(?:as\s+)?(Accepted|Final|Rejected|Withdrawn|Superseded)",
        re.IGNORECASE,
    ),
]


async def fetch_pep_updates(since: date | None = None) -> list[dict]:
    """Find recently accepted/rejected PEPs by checking merged PRs in python/peps."""
    if since is None:
        since = date.today() - timedelta(days=30)

    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    items: list[dict] = []
    seen: set[int] = set()

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        # Fetch PEP index for real titles
        pep_titles: dict[int, str] = {}
        try:
            resp = await client.get("https://peps.python.org/api/peps.json")
            resp.raise_for_status()
            for num, data in resp.json().items():
                pep_titles[int(num)] = data.get("title", "")
        except Exception:
            pass
        for query_term in ["Accepted", "Final", "Rejected", "Withdrawn"]:
            resp = await client.get(
                f"{GITHUB_API}/search/issues",
                params={
                    "q": f"repo:{PEPS_REPO} is:pr is:merged merged:>={since.isoformat()} Mark {query_term} PEP in:title",
                    "per_page": 30,
                    "sort": "updated",
                    "order": "desc",
                },
            )
            resp.raise_for_status()
            data = resp.json()

            for pr in data.get("items", []):
                title = pr.get("title", "")

                # Match against strict patterns only
                pep_number = None
                status = None
                for pattern in STATUS_CHANGE_PATTERNS:
                    match = pattern.search(title)
                    if match:
                        pep_number = int(match.group(1))
                        status = match.group(2).capitalize()
                        break

                if pep_number is None or pep_number in seen:
                    continue
                seen.add(pep_number)

                pep_title = pep_titles.get(pep_number, "")
                display_title = (
                    f"PEP {pep_number}: {pep_title}"
                    if pep_title
                    else f"PEP {pep_number}"
                )

                items.append(
                    {
                        "section": "pep_updates",
                        "title": display_title,
                        "url": f"https://peps.python.org/pep-{pep_number:04d}/",
                        "summary": "",
                        "source": "peps",
                        "metadata": {
                            "pep_number": pep_number,
                            "status": status,
                            "pr_url": pr["html_url"],
                        },
                    }
                )

    return items
