"""Fetch merged CPython PRs from GitHub.

Uses GitHub Search API with targeted queries to find significant PRs
without needing per-PR file requests.
"""

from datetime import date, timedelta

import httpx

from app.config import settings

CPYTHON_REPO = "python/cpython"
GITHUB_API = "https://api.github.com"

BOT_AUTHORS = {"miss-islington", "bedevere-bot"}

# Labels that mean "skip this"
SKIP_LABELS = {"docs", "skip news", "infrastructure"}

# Title patterns that indicate docs/CI noise
SKIP_TITLE_PATTERNS = [
    "document ",
    "documentation",
    "docstring",
    "whatsnew",
    "what's new",
    "run ",
    "ci:",
    "[ci]",
    "check-html",
    "blurb",
]

# Separate search queries to find signal PRs
SEARCH_QUERIES = [
    'label:"type-feature"',
    'label:"type-security"',
    'label:"type-performance"',
    "comments:>=15",
]


async def _search_prs(client: httpx.AsyncClient, query: str, since: date) -> list[dict]:
    """Run a single search query and return matching PRs."""
    full_query = (
        f"repo:{CPYTHON_REPO} is:pr is:merged merged:>={since.isoformat()} {query}"
    )
    results: list[dict] = []
    page = 1

    while True:
        resp = await client.get(
            f"{GITHUB_API}/search/issues",
            params={
                "q": full_query,
                "per_page": 100,
                "page": page,
                "sort": "updated",
                "order": "desc",
            },
        )
        resp.raise_for_status()
        data = resp.json()

        items = data.get("items", [])
        results.extend(items)

        if len(items) < 100:
            break
        page += 1

    return results


async def fetch_github_prs(since: date | None = None) -> list[dict]:
    """Fetch significant merged CPython PRs from the past month."""
    if since is None:
        since = date.today() - timedelta(days=14)

    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    seen: set[int] = set()
    items: list[dict] = []

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        for query in SEARCH_QUERIES:
            try:
                prs = await _search_prs(client, query, since)
            except Exception as e:
                print(f"  Warning: search query failed ({query}): {e}")
                continue

            for pr in prs:
                pr_number = pr["number"]
                if pr_number in seen:
                    continue
                seen.add(pr_number)

                author = pr.get("user", {}).get("login", "")
                if author in BOT_AUTHORS:
                    continue

                title = pr.get("title", "")
                title_lower = title.lower()
                if "backport" in title_lower:
                    continue
                # Cherry-picks like "[3.10] ..." or "[3.11] ..."
                if title.startswith("[3."):
                    continue

                labels = [label["name"] for label in pr.get("labels", [])]
                label_set = {lbl.lower() for lbl in labels}

                # Skip docs, CI, infrastructure PRs
                if label_set & SKIP_LABELS:
                    continue
                if any(pat in title_lower for pat in SKIP_TITLE_PATTERNS):
                    continue
                items.append(
                    {
                        "section": "merged_prs",
                        "title": title,
                        "url": pr["html_url"],
                        "summary": "",
                        "source": "github",
                        "metadata": {
                            "pr_number": pr_number,
                            "author": author,
                            "labels": labels,
                            "comments": pr.get("comments", 0),
                        },
                    }
                )

    # Rank and take top 10
    def _score(item: dict) -> int:
        meta = item["metadata"]
        label_set = {lbl.lower() for lbl in meta.get("labels", [])}
        score = meta.get("comments", 0)
        if "type-feature" in label_set:
            score += 50
        if "type-security" in label_set:
            score += 40
        if "type-performance" in label_set or "performance" in label_set:
            score += 30
        # New additions to stdlib are interesting
        title_lower = item["title"].lower()
        if title_lower.startswith(("add ", "gh-")) and "add " in title_lower:
            score += 10
        return score

    items.sort(key=_score, reverse=True)
    return items[:10]
