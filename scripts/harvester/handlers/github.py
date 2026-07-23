"""GitHub trending handler — multi-query GitHub search.

Replaces: scripts/fetch-github-trending.sh
Strategy: 5-dimensional search with different time windows
  - New projects (last 7 days) in AI, devtools, open-source alternative
  - Active projects (last 3 days) in ML, MCP tools
  - One query per monitored repo (daily star growth)
"""

import json
import logging
from datetime import datetime, timezone

from ..base import fetch_json, write_output, logger
from . import register


# ── Search queries ────────────────────────────────────────
# (label, query_template) — created / pushed cutoffs are filled in
QUERIES = [
    ("AI-Agent-新项目",
     "ai-agent+OR+llm+OR+agentic+created:>{created}+stars:>20&sort=stars&order=desc&per_page=6"),
    ("开发者工具-新项目",
     "developer-tools+OR+cli+OR+devtools+created:>{created}+stars:>20&sort=stars&order=desc&per_page=6"),
    ("开源替代-新项目",
     "open-source+alternative+OR+self-hosted+created:>{created}+stars:>20&sort=stars&order=desc&per_page=6"),
    ("AI-ML-近期活跃",
     "machine-learning+OR+deep-learning+OR+llm+pushed:>{pushed}+stars:>50&sort=stars&order=desc&per_page=6"),
    ("MCP-工具-近期活跃",
     "mcp+OR+model-context-protocol+OR+ai-tools+pushed:>{pushed}+stars:>10&sort=stars&order=desc&per_page=6"),
]


@register('github')
def fetch_github(output_path: str, **kwargs) -> list[dict]:
    """Fetch GitHub trending repos from all search queries."""
    all_repos: list[dict] = []
    seen: set[str] = set()

    created_cutoff = _days_ago_iso(7)
    pushed_cutoff = _days_ago_iso(3)

    for label, q_template in QUERIES:
        q = q_template.format(created=created_cutoff, pushed=pushed_cutoff)
        url = f"https://api.github.com/search/repositories?q={q}"
        logger.info("  GitHub query: %s", label)

        data = fetch_json(url, headers={
            'Accept': 'application/vnd.github.v3+json',
        })
        if not data or 'items' not in data:
            logger.warning("    GitHub API returned no data for %s", label)
            continue

        for item in data.get('items', [])[:5]:
            repo = _parse_repo(item)
            if repo and repo['link'] not in seen:
                seen.add(repo['link'])
                all_repos.append(repo)

    # Sort by daily growth desc, keep top 20
    all_repos.sort(key=lambda r: r.get('daily_growth', 0), reverse=True)
    top = all_repos[:20]

    write_output(output_path, top)
    logger.info("github: %d repos → %s", len(top), output_path)
    return top


def _days_ago_iso(days: int) -> str:
    """Return ISO date string for N days ago (UTC)."""
    from datetime import timedelta
    return (datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')


def _parse_repo(item: dict) -> dict | None:
    """Parse a single GitHub API item into our format."""
    name = item.get('full_name', '')
    desc = (item.get('description') or 'No description')[:120]
    stars = item.get('stargazers_count', 0)
    created = item.get('created_at', '')

    days = 1
    if created:
        try:
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            days = max(1, (datetime.now(timezone.utc) - dt).days)
        except ValueError:
            pass

    daily = round(stars / days, 1)
    topics = ','.join(item.get('topics', [])[:5])

    return {
        'title': f"⭐{stars} (+{daily:.0f}/d) | {name}: {desc}",
        'snippet': (f"{name} — {desc} [Stars: {stars}, +{daily:.0f}/d, "
                    f"Created: {created[:10]}, Topics: {topics}]"),
        'summary': (f"GitHub: {name} — {desc} "
                    f"[⭐{stars}, 日均+{daily:.0f}, 语言: {item.get('language', '?')}]"),
        'link': item['html_url'],
        'source': 'github-trending',
        'stars': stars,
        'daily_growth': daily,
    }
