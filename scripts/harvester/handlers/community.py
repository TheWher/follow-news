"""Community discussion handler — Hacker News + V2EX + LinuxDo.

Replaces: scripts/fetch-community.sh
Sources:
  - Hacker News Firebase API (top stories, filtered by score >= 30)
  - V2EX Hot Topics API (top 3)
  - LinuxDo Top Daily API (top 3)
"""

import json
import logging

from ..base import fetch_json, fetch_text, write_output, logger
from . import register


@register('community')
def fetch_community(output_path: str, **kwargs) -> list[dict]:
    """Fetch community discussions from all sources."""
    results = []

    results.extend(_fetch_hn())
    results.extend(_fetch_v2ex())
    results.extend(_fetch_linuxdo())

    write_output(output_path, results)
    logger.info("community: %d items → %s", len(results), output_path)
    return results


def _fetch_hn(max_items: int = 5) -> list[dict]:
    """Fetch top stories from Hacker News API."""
    logger.info("  HN top stories...")
    items = []

    ids = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not ids:
        return items

    count = 0
    for item_id in ids[:30]:
        if count >= max_items:
            break
        story = fetch_json(
            f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
            timeout=5
        )
        if not story or not isinstance(story, dict):
            continue

        score = story.get('score', 0)
        title = story.get('title', '')
        if score >= 30 and title:
            items.append({
                'title': title,
                'link': story.get('url',
                                  f"https://news.ycombinator.com/item?id={item_id}"),
                'source': 'Hacker News',
                'score': score,
                'comments': story.get('descendants', 0),
            })
            count += 1

    logger.info("    HN: %d items", count)
    return items


def _fetch_v2ex(max_items: int = 3) -> list[dict]:
    """Fetch hot topics from V2EX API."""
    logger.info("  V2EX hot topics...")
    items = []

    data = fetch_json("https://www.v2ex.com/api/topics/hot.json")
    if not data:
        return items

    count = 0
    for t in data[:10]:
        if count >= max_items:
            break
        title = t.get('title', '')
        if not title:
            continue
        items.append({
            'title': title,
            'link': t.get('url', f"https://www.v2ex.com/t/{t.get('id', '')}"),
            'source': f"V2EX {t.get('node', {}).get('title', '')}",
            'score': t.get('replies', 0),
            'comments': t.get('replies', 0),
        })
        count += 1

    logger.info("    V2EX: %d items", count)
    return items


def _fetch_linuxdo(max_items: int = 3) -> list[dict]:
    """Fetch daily top topics from LinuxDo."""
    logger.info("  LinuxDo daily top...")
    items = []

    data = fetch_json("https://linux.do/top/daily.json")
    if not data:
        return items

    topics = data.get('topic_list', {}).get('topics', [])
    count = 0
    for t in topics[:5]:
        if count >= max_items:
            break
        title = t.get('title', '')
        if not title:
            continue
        slug = t.get('slug', '')
        tid = t.get('id', '')
        items.append({
            'title': title,
            'link': (f"https://linux.do/t/{slug}/{tid}"
                     if slug else f"https://linux.do/t/topic/{tid}"),
            'source': 'LinuxDo',
            'score': t.get('like_count', 0),
            'comments': t.get('posts_count', 0),
        })
        count += 1

    logger.info("    LinuxDo: %d items", count)
    return items
