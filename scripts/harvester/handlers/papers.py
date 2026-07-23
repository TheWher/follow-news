"""AI papers handler — HuggingFace Daily Papers + PapersWithCode fallback.

Replaces: scripts/fetch-papers.sh
"""

import logging

from ..base import fetch_json, write_output, logger
from . import register


@register('papers')
def fetch_papers(output_path: str, **kwargs) -> list[dict]:
    """Fetch trending AI papers from HuggingFace (primary) and PapersWithCode."""
    results = _fetch_hf_papers()
    if not results:
        logger.info("  HF API failed, trying PapersWithCode...")
        results = _fetch_pwc_papers()

    write_output(output_path, results)
    logger.info("papers: %d items → %s", len(results), output_path)
    return results


def _fetch_hf_papers() -> list[dict]:
    """Fetch daily papers from HuggingFace."""
    logger.info("  HuggingFace daily papers...")
    data = fetch_json("https://huggingface.co/api/daily_papers")
    if not data:
        return []

    results = []
    for paper in data[:20]:
        title = (paper.get('title') or
                 paper.get('paper', {}).get('title', ''))
        if not title:
            continue

        paper_id = (paper.get('paper', {}).get('id', '') or
                    paper.get('id', ''))
        upvotes = paper.get('upvotes', 0) or paper.get('votes', 0)
        url = f"https://huggingface.co/papers/{paper_id}" if paper_id else ''
        summary = (paper.get('paper', {}).get('summary', '') or
                   paper.get('summary', '') or '')[:300]

        results.append({
            'title': title,
            'link': url,
            'source': 'HuggingFace Papers',
            'score': upvotes,
            'summary': summary,
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:10]


def _fetch_pwc_papers() -> list[dict]:
    """Fallback: fetch from PapersWithCode trending."""
    data = fetch_json(
        "https://paperswithcode.com/api/v1/papers/?ordering=-github_stars"
    )
    if not data or 'results' not in data:
        return []

    results = []
    for paper in data['results'][:20]:
        title = paper.get('title', '')
        if not title:
            continue
        results.append({
            'title': title,
            'link': (paper.get('url_abs', '') or
                     paper.get('url_pdf', '') or ''),
            'source': 'PapersWithCode',
            'score': paper.get('github_stars', 0) or 0,
            'summary': (paper.get('abstract', '') or '')[:300],
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:10]
