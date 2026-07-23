"""AI products/tools handler — Product Hunt RSS + GitHub new AI repos.

Replaces: scripts/fetch-products.sh
"""

import json
import logging
import re
import html
from datetime import datetime, timezone, timedelta

from ..base import fetch_json, fetch_text, write_output, logger
from . import register


@register('products')
def fetch_products(output_path: str, **kwargs) -> list[dict]:
    """Fetch new AI products from Product Hunt and GitHub."""
    results = []
    results.extend(_fetch_ph_ai())
    results.extend(_fetch_gh_new())
    results = _dedupe(results)

    write_output(output_path, results[:6])
    logger.info("products: %d items → %s", min(len(results), 6), output_path)
    return results[:6]


def _fetch_ph_ai(max_items: int = 5) -> list[dict]:
    """Fetch AI-related products from Product Hunt RSS."""
    logger.info("  Product Hunt AI...")
    text = fetch_text("https://www.producthunt.com/feed?category=ai")
    if not text:
        return []

    results = []
    items = re.findall(r'<item>(.*?)</item>', text, re.DOTALL)
    for item in items[:10]:
        title_match = re.search(r'<title>(.*?)</title>', item)
        link_match = re.search(r'<link>(.*?)</link>', item)
        desc_match = re.search(r'<description>(.*?)</description>', item)

        title = html.unescape(title_match.group(1)) if title_match else ''
        link = link_match.group(1).strip() if link_match else ''
        desc_text = html.unescape(desc_match.group(1)) if desc_match else ''

        d_clean = re.sub(r'<[^>]+>', '', desc_text)[:200]

        if title and ('AI' in (title + d_clean).upper()[:200]):
            results.append({
                'title': title,
                'link': link,
                'source': 'Product Hunt',
                'score': 0,
                'summary': d_clean,
            })

    return results[:max_items]


def _fetch_gh_new(max_items: int = 3) -> list[dict]:
    """Fetch newly created AI-related GitHub repos (last 2 days)."""
    logger.info("  GitHub new AI repos...")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=2)).strftime('%Y-%m-%d')
    url = (f"https://api.github.com/search/repositories"
           f"?q=AI+agent+tools+created:>{cutoff}"
           f"&sort=stars&order=desc&per_page=10")

    data = fetch_json(url, headers={
        'Accept': 'application/vnd.github.v3+json',
    })
    if not data:
        return []

    results = []
    for repo in data.get('items', [])[:5]:
        results.append({
            'title': (f'{repo["full_name"]}: '
                      f'{repo.get("description", "") or ""}'),
            'link': repo['html_url'],
            'source': 'GitHub New',
            'score': repo.get('stargazers_count', 0),
            'summary': (f'⭐ {repo["stargazers_count"]} · '
                        f'Language: {repo.get("language", "?")}'),
        })

    return results[:max_items]


def _dedupe(items: list[dict]) -> list[dict]:
    """Deduplicate by title prefix similarity."""
    seen: set[str] = set()
    unique = []
    for item in items:
        key = item['title'][:50].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique
