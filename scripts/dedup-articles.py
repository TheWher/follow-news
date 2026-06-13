#!/usr/bin/env python3
"""Deduplicate news articles across sources (inspired by Horizon).
Strategy:
1. URL exact match — same link → merge, keep highest-score metadata
2. Title similarity — Levenshtein > 0.7 → likely same story, merge
3. Domain overlap — same base domain + overlapping keywords → merge
"""

import json, sys, re
from collections import defaultdict
from urllib.parse import urlparse

def normalize_url(url):
    """Strip protocol, www, trailing slash, utm params."""
    url = re.sub(r'^https?://(www\.)?', '', url)
    url = re.sub(r'[?#].*$', '', url)
    url = url.rstrip('/')
    return url.lower()

def extract_domain(url):
    try:
        return urlparse(url).netloc.replace('www.', '').lower()
    except:
        return url.lower()[:50]

def title_words(title):
    """Extract meaningful words from title for comparison."""
    # Remove common stop words, punctuation
    words = re.findall(r'[a-zA-Z0-9一-鿿]+', title.lower())
    stopwords = {'the','a','an','is','are','was','were','in','on','at','to','for','of','and','or','it','its','this','that','with','from','by','as','be','has','have','had','not','no','but','if','so','we','he','she','they'}
    return [w for w in words if w not in stopwords]

def word_overlap(words1, words2):
    if not words1 or not words2:
        return 0
    set1, set2 = set(words1), set(words2)
    intersection = set1 & set2
    return len(intersection) / min(len(set1), len(set2))

def deduplicate(articles, threshold=0.55):
    """
    Deduplicate articles using multi-strategy approach.
    Returns list of (merged_article, [duplicate_indices]).
    """
    if not articles:
        return []

    n = len(articles)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[py] = px

    # Precompute
    urls = [normalize_url(a.get('link','')) for a in articles]
    domains = [extract_domain(a.get('link','')) for a in articles]
    titles = [a.get('title','') for a in articles]
    title_word_sets = [title_words(t) for t in titles]

    for i in range(n):
        for j in range(i+1, n):
            if find(i) == find(j):
                continue

            # Strategy 1: URL exact match
            if urls[i] and urls[j] and urls[i] == urls[j]:
                union(i, j)
                continue

            # Strategy 2: Same domain + high title word overlap
            if domains[i] == domains[j]:
                overlap = word_overlap(title_word_sets[i], title_word_sets[j])
                if overlap > threshold:
                    union(i, j)
                    continue

            # Strategy 3: High title overlap across any domains (cross-source same story)
            overlap = word_overlap(title_word_sets[i], title_word_sets[j])
            if overlap > 0.75:
                union(i, j)
                continue

    # Group by root
    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)

    # Merge each group — keep highest-score item as primary
    merged = []
    for root, indices in groups.items():
        # Sort by score desc (higher = better), then by title length (longer = more info)
        indices.sort(key=lambda x: (
            articles[x].get('score', 0) or articles[x].get('stars', 0) or 0,
            len(articles[x].get('title',''))
        ), reverse=True)

        primary = articles[indices[0]].copy()
        primary['_dedup_count'] = len(indices)
        if len(indices) > 1:
            sources = list(set(articles[i].get('source','?') for i in indices))
            primary['source'] = ' + '.join(sources)
            primary['_duplicates'] = [articles[i].get('title','')[:80] for i in indices[1:3]]
        merged.append(primary)

    return merged

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/td-articles.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else '/tmp/td-articles-deduped.json'

    with open(input_file, 'r') as f:
        articles = json.load(f)

    before = len(articles)
    merged = deduplicate(articles)
    after = len(merged)
    dup_count = sum(1 for m in merged if m.get('_dedup_count', 1) > 1)

    print(f"Dedup: {before} → {after} articles ({before - after} removed, {dup_count} groups merged)")

    with open(output_file, 'w') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
