# Core Dispatch

A regular digest of what's happening in CPython, from merged PRs and PEP decisions to community discussions and upcoming events.

**Live at [coredispatch.xyz](https://coredispatch.xyz)**

## Local Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python)
- [bun](https://bun.sh/) (JavaScript)
- A GitHub token with public repo read access (for the generating the edition draft)

### Setup

```bash
# Install dependencies
cd backend && uv sync && cd ..
cd frontend && bun install && cd ..

# Add your GitHub token
echo 'GITHUB_TOKEN=ghp_...' > backend/.env
```

### Run

```bash
./scripts/dev.sh
```

This starts the FastAPI backend on `:8000` and the Astro frontend on `:3000`. The frontend proxies `/api` requests to the backend.

### Generate a draft edition

```bash
cd backend && uv run python -m app.pipeline.run
```

This fetches data from all sources and writes a YAML file to `drafts/`. Preview it at `http://localhost:3000/staging`.

## Publishing Workflow

### Automated (weekly)

1. **Friday 6 AM UTC** — GitHub Actions runs the pipeline, writes a draft to `drafts/`, and opens a draft PR
2. **Review** — edit the YAML in the PR: write editorial notes, remove uninteresting items, add community picks and a quote
3. **Preview** — merge the PR to main, preview at `/staging`
4. **Publish** — move the file from `drafts/` to `editions/` via another PR. Merge to publish.
5. **Email** — Buttondown sends the edition to subscribers via RSS-to-email

### Manual

1. Run `cd backend && uv run python -m app.pipeline.run` to generate a draft
2. Edit `drafts/<slug>.yml` — add editorial notes, curate items, add picks
3. Preview at `http://localhost:3000/staging`
4. Move the file to `editions/` when ready to publish
5. Push to main — GHA deploys to FastAPI Cloud


## Content

Each edition is a YAML file with auto-generated and hand-curated sections.

### Auto-generated sections

These are populated by the pipeline every Friday:

| Section | Source |
|---------|--------|
| **Upcoming Releases** | [peps.python.org](https://peps.python.org) release schedule iCal |
| **Official News** | Python Blog + PyPI Blog (configured in `official.yml`) |
| **PEP Updates** | Merged PRs in [python/peps](https://github.com/python/peps) that change a PEP's status |
| **Steering Council Updates** | PSC meeting summaries from [discuss.python.org/c/committers](https://discuss.python.org/c/committers) |
| **Merged PRs** | Top 10 CPython PRs by engagement — features, security fixes, performance |
| **Discussion** | Most active PEP discussions on Discourse, ranked by new replies |
| **Core Dev Musings** | Personal blogs and podcasts (configured in `core-blogs.yml`) |
| **Upcoming CFPs & Conferences** | [pythondeadlin.es](https://pythondeadlin.es) + PyCon event calendar |

### Hand-curated sections

These are added during editorial review:

| Section | Description |
|---------|-------------|
| **Community** | Links, talks, and tools submitted by the community |
| **One More Thing** | A quote or fun post — top-level `quote` field in the YAML |
| **Editorial Notes** | The intro paragraph — top-level `editorial_notes` field |
| **Credits** | Who put this edition together — top-level `credits` field |

## Contributing

### Submit a link

Found something the Python community should know about? [Open a GitHub issue](https://github.com/savannahostrowski/coredispatch.xyz/issues/new?template=submit-link.yml) with the link, a title, and which section it belongs in. Accepted submissions appear in the **Community** section.

### Submit a quote

Have a great quote for **One More Thing**? [Submit it as an issue](https://github.com/savannahostrowski/coredispatch.xyz/issues/new?template=submit-link.yml&title=%5BQuote%5D+) with the text, author, and a link to the source.

### Add a blog feed

Core developer or regular Python contributor with a blog? Open a PR to add your feed to `core-blogs.yml`:

```yaml
- name: Your Name
  url: https://yourblog.com/tags/python/feed.xml
```

Use a tag-filtered feed URL when possible to avoid off-topic posts.

### Add an official feed

If an official Python project has a blog (like the PSF or a working group), open a PR to add it to `official.yml`.

## Editing an Edition

Want to help curate? Here's what editors do during the review phase:

1. **Write editorial notes** — a 2-3 sentence intro that ties the highlights together. What's the big story this week?
2. **Remove noise** — delete items that aren't interesting or relevant. Less is more.
3. **Add community picks** — add items with `section: picks` from submitted issues or things you've found
4. **Add a quote** — fill in the `quote` field with something fun, insightful, or mass-reply-inducing
5. **Add credits** — list everyone who contributed to this edition in the `credits` field
6. **Review PR titles** — the auto-generated PR titles are raw GitHub titles. Rewrite to be human-readable when needed.

To add a manual item:

```yaml
- section: picks
  title: "Something cool"
  url: https://example.com
  summary: "Why this is worth reading."
  source: manual
  metadata:
    submitted_by: "githubhandle"
```
